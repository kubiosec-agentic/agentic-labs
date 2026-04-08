"""Utility for running sub-agents in isolated sessions.

Each sub-agent runs in a fresh Runner with its own InMemorySessionService,
in a separate thread. This guarantees zero context leakage between the
attacker (red team) and the target (banking assistant), mimicking a
real-world stateless API request.

Includes retry logic for 429 rate-limit errors (common with free-tier keys).

Based on google/adk-samples/ai-security-agent (Apache 2.0).
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.errors import ClientError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


@retry(
    retry=retry_if_exception_type(ClientError),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    stop=stop_after_attempt(3),
)
def execute_sub_agent(agent: Agent, prompt_text: str) -> str:
    """Run a sub-agent in an isolated thread with a fresh session.

    The ThreadPoolExecutor pattern ensures:
    1. A clean-room environment for the target, preventing context leakage.
    2. The target's safety protocols are tested in a vacuum, mimicking a
       real-world stateless API request.
    """

    async def _run_internal():
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="app",
            user_id="internal_bot",
            session_id="temp_task_session",
        )
        runner = Runner(
            agent=agent,
            app_name="app",
            session_service=session_service,
        )
        content = types.Content(
            role="user",
            parts=[types.Part(text=prompt_text)],
        )
        result_text = ""
        async for event in runner.run_async(
            new_message=content,
            user_id="internal_bot",
            session_id=session.id,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        result_text += part.text
        return result_text

    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _run_internal())
            return future.result()
    except (RuntimeError, ValueError, TypeError) as e:
        return f"Error running sub-agent: {e!s}"
