"""
OpenAI Agents SDK PoC — Agent App
===================================
- Talks to LiteLLM proxy (OpenAI-compatible) for LLM calls
- Uses Microsoft Learn MCP server for documentation search
- OpenAI Moderation API as input guardrail (agent-side)
- Custom structured JSON logging via TracingProcessor
- Exposed as a FastAPI service on :8080

Docs:
  Agents SDK  — https://openai.github.io/openai-agents-python/
  LiteLLM     — https://docs.litellm.ai/docs/proxy/configs
  MS Learn MCP — https://learn.microsoft.com/training/support/mcp
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI

from agents import (
    Agent,
    Runner,
    RunConfig,
    OpenAIChatCompletionsModel,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail,
    trace,
    set_tracing_disabled,
    set_trace_processors,
    enable_verbose_stdout_logging,
)
from agents.mcp import MCPServerStreamableHttp

from custom_logger import AgentCallLogger

# ── Configuration ────────────────────────────────────────────────
LITELLM_PROXY_URL = os.environ.get("LITELLM_PROXY_URL", "http://localhost:4000/v1")
LITELLM_PROXY_KEY = os.environ.get("LITELLM_PROXY_KEY", "sk-master-1234")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
# MCP via LiteLLM proxy gateway: the proxy forwards tool calls to the
# upstream MCP server configured in its config.yaml (mcp_servers section).
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:4000/mcp")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_app")

# ── Disable default OpenAI tracing export (we use our own) ──────
set_tracing_disabled(disabled=True)

# ── Register custom trace processor ─────────────────────────────
agent_logger = AgentCallLogger()
set_trace_processors([agent_logger])
set_tracing_disabled(disabled=False)  # re-enable with our processor

# ── LiteLLM proxy client ────────────────────────────────────────
litellm_client = AsyncOpenAI(
    api_key=LITELLM_PROXY_KEY,
    base_url=LITELLM_PROXY_URL,
)

litellm_model = OpenAIChatCompletionsModel(
    model="gpt-4o",
    openai_client=litellm_client,
)

# ── Direct OpenAI client (for moderation guardrail) ─────────────
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# ═══════════════════════════════════════════════════════════════════
#  GUARDRAIL — OpenAI Moderation API
# ═══════════════════════════════════════════════════════════════════
@input_guardrail
async def openai_moderation_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    """
    Calls the OpenAI Moderation API to check user input
    before it reaches the LLM. Trips the guardrail wire if
    any moderation category is flagged.
    """
    # Extract text from input
    if isinstance(input, str):
        text = input
    else:
        text_parts = []
        for item in input:
            if isinstance(item, dict):
                content = item.get("content", "")
                if isinstance(content, str):
                    text_parts.append(content)
            elif isinstance(item, str):
                text_parts.append(item)
        text = " ".join(text_parts) if text_parts else str(input)

    if not text.strip():
        return GuardrailFunctionOutput(
            output_info={"flagged": False, "reason": "empty input"},
            tripwire_triggered=False,
        )

    try:
        moderation = await openai_client.moderations.create(
            model="omni-moderation-latest",
            input=text,
        )
        result = moderation.results[0]
        flagged = result.flagged
        categories = {
            cat: score
            for cat, score in result.category_scores.model_dump().items()
            if score > 0.3
        }

        logger.info(
            f"[MODERATION] flagged={flagged} categories={categories}"
        )

        return GuardrailFunctionOutput(
            output_info={
                "flagged": flagged,
                "categories": categories,
            },
            tripwire_triggered=flagged,
        )
    except Exception as e:
        logger.warning(f"[MODERATION] API error (allowing through): {e}")
        return GuardrailFunctionOutput(
            output_info={"error": str(e)},
            tripwire_triggered=False,
        )


# ═══════════════════════════════════════════════════════════════════
#  MCP SERVER — Microsoft Learn
# ═══════════════════════════════════════════════════════════════════
ms_learn_mcp = MCPServerStreamableHttp(
    name="Microsoft Learn",
    params={
        "url": MCP_SERVER_URL,
        "timeout": 30,
    },
    cache_tools_list=True,
)


# ═══════════════════════════════════════════════════════════════════
#  AGENT DEFINITIONS
# ═══════════════════════════════════════════════════════════════════
def create_learning_agent() -> Agent:
    """Agent that searches Microsoft Learn docs via MCP."""
    return Agent(
        name="MSLearnResearcher",
        instructions=(
            "You are a helpful technical research assistant. "
            "You have access to Microsoft Learn documentation via MCP tools. "
            "When asked a technical question, use the available MCP tools to "
            "search Microsoft's documentation and provide accurate, well-sourced answers. "
            "Always cite the documentation source when possible."
        ),
        model=litellm_model,
        mcp_servers=[ms_learn_mcp],
        input_guardrails=[openai_moderation_guardrail],
    )


def create_general_agent() -> Agent:
    """General-purpose agent (no MCP, just LLM via proxy)."""
    return Agent(
        name="GeneralAssistant",
        instructions=(
            "You are a helpful general-purpose assistant. "
            "Answer questions clearly and concisely."
        ),
        model=litellm_model,
        input_guardrails=[openai_moderation_guardrail],
    )


# ═══════════════════════════════════════════════════════════════════
#  FASTAPI APP
# ═══════════════════════════════════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect to MCP server on startup, disconnect on shutdown."""
    logger.info(f"Connecting to MCP server at {MCP_SERVER_URL} ...")
    await ms_learn_mcp.__aenter__()
    logger.info("MCP server connected.")
    yield
    await ms_learn_mcp.__aexit__(None, None, None)
    logger.info("MCP server disconnected.")


app = FastAPI(
    title="OpenAI Agents SDK PoC",
    description="Agent talking to LiteLLM proxy + Microsoft Learn MCP",
    version="0.1.0",
    lifespan=lifespan,
)


# ── Request / Response schemas ───────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    agent_type: str = "learning"  # "learning" or "general"


class ChatResponse(BaseModel):
    agent: str
    response: str
    guardrail_passed: bool = True


class HealthResponse(BaseModel):
    status: str
    litellm_proxy: str
    mcp_server: str


# ── Endpoints ────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        litellm_proxy=LITELLM_PROXY_URL,
        mcp_server=MCP_SERVER_URL,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Send a message to an agent.
    - agent_type=learning → uses Microsoft Learn MCP tools
    - agent_type=general  → plain LLM via LiteLLM proxy
    """
    if req.agent_type == "learning":
        agent = create_learning_agent()
    else:
        agent = create_general_agent()

    try:
        with trace(f"chat-{req.agent_type}"):
            result = await Runner.run(agent, req.message)

        return ChatResponse(
            agent=agent.name,
            response=result.final_output,
            guardrail_passed=True,
        )

    except InputGuardrailTripwireTriggered as e:
        logger.warning(f"[GUARDRAIL] Input blocked: {e}")
        return ChatResponse(
            agent=agent.name,
            response="Your message was blocked by content moderation.",
            guardrail_passed=False,
        )
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools from the Microsoft Learn server."""
    try:
        tools = await ms_learn_mcp.list_tools()
        return {
            "server": ms_learn_mcp.name,
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                }
                for t in tools
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
#  CLI MODE — for quick local testing
# ═══════════════════════════════════════════════════════════════════
async def cli_demo():
    """Interactive CLI demo — useful for local dev."""
    print("=" * 60)
    print("  OpenAI Agents SDK PoC — CLI Mode")
    print(f"  LiteLLM Proxy : {LITELLM_PROXY_URL}")
    print(f"  MCP Server    : {MCP_SERVER_URL}")
    print("=" * 60)

    async with ms_learn_mcp:
        agent = create_learning_agent()

        while True:
            user_input = input("\n[You] > ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                break

            try:
                with trace("cli-chat"):
                    result = await Runner.run(agent, user_input)
                print(f"\n[Agent] {result.final_output}")
            except InputGuardrailTripwireTriggered:
                print("\n[Agent] Message blocked by content moderation.")
            except Exception as e:
                print(f"\n[Error] {e}")


if __name__ == "__main__":
    import sys

    if "--cli" in sys.argv:
        asyncio.run(cli_demo())
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)
