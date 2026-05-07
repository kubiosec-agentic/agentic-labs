"""
Exercise 4: Workflow with Worker/Reviewer reflection pattern.
"""

import asyncio
import os
import sys
from dataclasses import dataclass
from uuid import uuid4

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: OPENAI_API_KEY is not set. Run: export OPENAI_API_KEY=\"sk-...\"")
if not os.environ.get("OPENAI_CHAT_MODEL"):
    sys.exit("Error: OPENAI_CHAT_MODEL is not set. Run: export OPENAI_CHAT_MODEL=\"gpt-4o-mini\"")

from agent_framework import (
    AgentResponse,
    Executor,
    Message,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.openai import OpenAIChatClient
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Messages passed between Worker and Reviewer
# ---------------------------------------------------------------------------
@dataclass
class ReviewRequest:
    request_id: str
    user_messages: list[Message]
    agent_messages: list[Message]


@dataclass
class ReviewResponse:
    request_id: str
    feedback: str
    approved: bool


# ---------------------------------------------------------------------------
# Reviewer: evaluates agent output
# ---------------------------------------------------------------------------
class Reviewer(Executor):
    def __init__(self, id: str, chat_client) -> None:
        super().__init__(id=id)
        self._chat_client = chat_client

    @handler
    async def review(self, request: ReviewRequest, ctx: WorkflowContext[ReviewResponse]) -> None:
        class _Verdict(BaseModel):
            feedback: str
            approved: bool

        messages = [
            Message(
                role="system",
                contents=[
                    "You review AI agent responses. Approve only if the "
                    "answer is relevant, accurate, clear, and complete."
                ],
            ),
            *request.user_messages,
            *request.agent_messages,
            Message(role="user", contents=["Please review the agent's response."]),
        ]

        response = await self._chat_client.get_response(
            messages=messages, options={"response_format": _Verdict},
        )
        verdict = _Verdict.model_validate_json(response.messages[-1].text)

        status = "APPROVED" if verdict.approved else "REJECTED"
        print(f"  Reviewer: {status} - {verdict.feedback}")

        await ctx.send_message(
            ReviewResponse(
                request_id=request.request_id,
                feedback=verdict.feedback,
                approved=verdict.approved,
            )
        )


# ---------------------------------------------------------------------------
# Worker: generates responses, retries on rejection
# ---------------------------------------------------------------------------
class Worker(Executor):
    def __init__(self, id: str, chat_client) -> None:
        super().__init__(id=id)
        self._chat_client = chat_client
        self._pending: dict[str, tuple[ReviewRequest, list[Message]]] = {}

    @handler
    async def handle_user(self, user_messages: list[Message], ctx: WorkflowContext[ReviewRequest]) -> None:
        messages = [
            Message(role="system", contents=["You are a helpful assistant."]),
            *user_messages,
        ]
        response = await self._chat_client.get_response(messages=messages)
        print(f"  Worker: generated response")

        request = ReviewRequest(
            request_id=str(uuid4()),
            user_messages=user_messages,
            agent_messages=response.messages,
        )
        self._pending[request.request_id] = (request, messages + list(response.messages))
        await ctx.send_message(request)

    @handler
    async def handle_review(self, review: ReviewResponse, ctx: WorkflowContext[ReviewRequest]) -> None:
        request, messages = self._pending.pop(review.request_id)

        if review.approved:
            # FIX: emit AgentResponse (final), not AgentResponseUpdate (delta).
            # Non-streaming workflows expect the completed response object.
            await ctx.yield_output(
                AgentResponse(messages=list(request.agent_messages))
            )
            return

        print(f"  Worker: retrying with feedback")
        messages.append(Message(role="system", contents=[review.feedback]))
        messages.append(Message(role="system", contents=["Regenerate the response."]))
        messages.extend(request.user_messages)

        response = await self._chat_client.get_response(messages=messages)
        new_request = ReviewRequest(
            request_id=review.request_id,
            user_messages=request.user_messages,
            agent_messages=response.messages,
        )
        self._pending[new_request.request_id] = (new_request, messages + list(response.messages))
        await ctx.send_message(new_request)


# ---------------------------------------------------------------------------
# Build and run
# ---------------------------------------------------------------------------
async def main() -> None:
    print("=== Workflow: Worker / Reviewer reflection ===\n")

    worker_client = OpenAIChatClient()
    reviewer_client = OpenAIChatClient()

    worker = Worker(id="worker", chat_client=worker_client)
    reviewer = Reviewer(id="reviewer", chat_client=reviewer_client)

    agent = (
        WorkflowBuilder(start_executor=worker)
        .add_edge(worker, reviewer)
        .add_edge(reviewer, worker)
        .build()
        .as_agent()
    )

    query = "Explain in three sentences why containers are useful for AI agent sandboxing."
    print(f"User: {query}\n")

    result = await agent.run(query)
    print(f"\nApproved response:\n{result}")

    print("\n=== Done ===")


if __name__ == "__main__":
    asyncio.run(main())
