from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel

from autogen_core import CancellationToken
from autogen_core.models import SystemMessage, UserMessage
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient

# ---------- Structured output schema returned by the LLM ----------
class Block(BaseModel):
    language: Literal["python", "bash", "sh"]
    code: str
    filename: Optional[str] = None  # optional hint; executor runs from temp files anyway

class CodePlan(BaseModel):
    blocks: List[Block]
    notes: Optional[str] = None

# ---------- Planner: ask the model for executable code blocks ----------
async def plan_code(user_instruction: str) -> CodePlan:
    model = OpenAIChatCompletionClient(
        model="gpt-4o",  # supports structured output
        temperature=0
    )
    sys = SystemMessage(
        content=(
            "You are a coding agent. Return a compact plan of code blocks that can run "
            "inside a Debian-based container with Python 3.11. Allowed languages: python, bash. "
            "If multiple steps are needed, create multiple blocks in order. Avoid network access "
            "unless explicitly requested. Prefer self-contained examples."
        )
    )
    usr = UserMessage(
        content=(
            "Instruction:\n"
            f"{user_instruction}\n\n"
            "Respond ONLY as JSON matching the CodePlan schema I provided. "
            "Do not include explanations outside JSON."
        ),
        source="user",
    )

    # Ask for structured output directly as our Pydantic model
    resp = await model.create(
        messages=[sys, usr],
        extra_create_args={"response_format": CodePlan},  # structured output
    )

    # Parse the JSON string into our model
    plan = CodePlan.model_validate_json(resp.content)  # type: ignore[arg-type]
    await model.close()
    return plan

# ---------- Executor: run blocks in Docker ----------
async def execute_blocks(plan: CodePlan, work_dir: Path) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    # Use Python 3.11 image (has sh + python as required by the executor)
    async with DockerCommandLineCodeExecutor(work_dir=work_dir, image="python:3.11") as ex:  # type: ignore
        # Map our blocks to AutoGen CodeBlock objects
        code_blocks = [
            CodeBlock(language=("bash" if b.language in ("bash", "sh") else "python"), code=b.code)
            for b in plan.blocks
        ]
        result = await ex.execute_code_blocks(
            code_blocks=code_blocks,
            cancellation_token=CancellationToken(),
        )
        print("Exit code:", result.exit_code)
        print("Output:\n", result.output)
        print("Executed file:", result.code_file)

# ---------- Demo ----------
async def main() -> None:
    work_dir = Path("coding")
    # Example prompt: the model decides what code to write
    user_instruction = (
        "Create a small Python script that writes numbers 1..5 to numbers.txt, "
        "then a Bash step that prints the file to stdout."
    )

    plan = await plan_code(user_instruction)
    await execute_blocks(plan, work_dir)

if __name__ == "__main__":
    asyncio.run(main())
