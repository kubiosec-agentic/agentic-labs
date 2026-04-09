"""
Interactive variant of mcp_01_stdio.py.

Same wiring (openai-agents + @modelcontextprotocol/server-filesystem over
stdio), but instead of running a fixed list of questions and exiting, it
opens a REPL so students can keep probing the filesystem server with
follow-up questions. The agent keeps conversation history in a
SQLiteSession so multi-turn references like "and now list the .py files
inside it" work the way you would expect.

Run:
    python3 mcp_01_stdio_interactive.py

Commands at the prompt:
    /quit, /exit, /q       leave the REPL
    /reset                 wipe the session history and start fresh
    /tools                 reprint the tool list from the server
    anything else          sent to the agent as a user turn
"""
import asyncio
import shutil

from agents import Agent, Runner
from agents.run_context import RunContextWrapper
from agents.mcp import MCPServerStdio
from agents.memory import SQLiteSession


BANNER = """\
Filesystem agent ready. Ask anything about the directory you picked.
Examples:
  - list the files in the directory
  - what file types are in here
  - show me the first 20 lines of README.md
  - find every python file and tell me which one is largest
Type /quit to exit, /reset to clear history, /tools to reprint tools.
"""


async def interactive_loop(agent: Agent, session: SQLiteSession, server: MCPServerStdio, run_context):
    print(BANNER)
    loop = asyncio.get_running_loop()
    while True:
        try:
            user_input = await loop.run_in_executor(None, input, "you> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input in ("/quit", "/exit", "/q"):
            return
        if user_input == "/reset":
            await session.clear_session()
            print("[session cleared]")
            continue
        if user_input == "/tools":
            tools = await server.list_tools(run_context, agent)
            print("Available tools:", [t.name for t in tools])
            continue

        try:
            result = await Runner.run(
                starting_agent=agent,
                input=user_input,
                session=session,
            )
            print(f"agent> {result.final_output}\n")
        except Exception as exc:
            print(f"[error] {exc}\n")


async def main():
    directory_path = input("Please enter the path: ").strip()
    if not directory_path:
        print("No path given, exiting.")
        return

    async with MCPServerStdio(
        name="filesystem",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", directory_path],
        },
    ) as server:
        run_context = RunContextWrapper(context=None)
        agent = Agent(
            name="FilesystemAssistant",
            instructions=(
                f"You help the user explore the directory at {directory_path}. "
                "Use the filesystem MCP tools to answer questions. When the "
                "user asks a follow-up, assume it refers to the same "
                "directory unless they say otherwise. Keep answers short and "
                "factual; if a tool call is needed, make it."
            ),
            mcp_servers=[server],
        )

        tools = await server.list_tools(run_context, agent)
        print("Available tools:", [t.name for t in tools])

        session = SQLiteSession("mcp_stdio_interactive")
        await interactive_loop(agent, session, server, run_context)


if __name__ == "__main__":
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed.")
    asyncio.run(main())
