"""
LangChain agent loop with a local Python REPL tool.

Where LC_02 shows a single tool call executed once, this script shows a real
multi-step agent loop over a LOCAL, executable tool: a Python REPL. The model
writes code, the code runs on THIS machine, the output is fed back, and the
model decides whether to run more code or answer. The loop continues until the
model stops emitting tool calls.

  1. Define a python_repl tool with the @tool decorator (Pydantic schema)
  2. Bind it to gpt-4o with bind_tools
  3. Loop: invoke -> if tool_calls, execute locally, append ToolMessage, repeat
  4. Stop when the model returns a final answer with no tool calls

Contrast with the hosted code_interpreter in LC_04: there the code runs on
OpenAI's servers inside a sandbox. Here it runs in YOUR process, unsandboxed.

  !!!  SECURITY WARNING  !!!
  This tool runs model-generated Python in the current process with no
  sandbox. A prompt-injected or adversarial model can read files, exfiltrate
  environment variables (including OPENAI_API_KEY), open sockets, or delete
  data. Never point this at untrusted input, and only run it inside a
  disposable, isolated environment (throwaway container/VM, no secrets, no
  network). It is a teaching example of tool risk, not a production pattern.
"""

import io
import contextlib

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field


# ---- Tool definition: a local Python REPL -------------------------------

# Persistent namespace so variables defined in one call survive into the next,
# which lets the model build up state across loop iterations.
_REPL_NS: dict = {}


class PythonREPLInput(BaseModel):
    code: str = Field(description="Python source to execute. Use print() to return values.")


@tool("python_repl", args_schema=PythonREPLInput)
def python_repl(code: str) -> str:
    """Execute Python code and return whatever it prints to stdout.
    State persists between calls. Always print() the result you want back."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, _REPL_NS)          # UNSANDBOXED, see security warning
    except Exception as e:                 # feed the error back so the model can fix it
        return f"{type(e).__name__}: {e}"
    out = buf.getvalue().strip()
    return out if out else "(no output; remember to print() your result)"


# ---- LLM with the tool bound --------------------------------------------

llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools([python_repl])
TOOLS = {"python_repl": python_repl}

MAX_STEPS = 6   # cap the loop so a confused model cannot spin forever


def run_agent(question: str) -> str:
    messages = [
        SystemMessage(content=(
            "You are a precise assistant. When a question needs computation, "
            "use the python_repl tool and print the result. Do not compute in "
            "your head. When you have the answer, state it clearly."
        )),
        HumanMessage(content=question),
    ]

    for step in range(1, MAX_STEPS + 1):
        ai = llm_with_tools.invoke(messages)
        messages.append(ai)

        if not ai.tool_calls:
            return ai.content   # no tool call means the model is done

        for call in ai.tool_calls:
            print(f"\n[step {step}] tool={call['name']} args={call['args']}")
            result = TOOLS[call["name"]].invoke(call["args"])
            print(f"[step {step}] result={result!r}")
            messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    return "(stopped: reached MAX_STEPS without a final answer)"


if __name__ == "__main__":
    question = (
        "Compute the 25th Fibonacci number, then give the sum of all prime "
        "numbers below 100. Show each result."
    )
    print(f"Question: {question}")
    answer = run_agent(question)
    print(f"\nFinal answer:\n{answer}")
