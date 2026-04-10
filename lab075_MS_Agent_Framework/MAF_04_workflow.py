"""
Exercise 4: Workflow with Worker/Reviewer reflection pattern.

This demonstrates the WorkflowBuilder, which lets you wire executors
into a cyclic graph. Here a Worker generates a response and a Reviewer
evaluates it. If the Reviewer rejects, the Worker retries with
feedback. Only approved responses are emitted.

This is a simplified version of the openai_workflow.py reference file
in this directory (which has the full implementation). Read that file
for the complete pattern including structured output and state
management.

Prerequisites:
    export OPENAI_API_KEY="sk-..."

Run:
    python3 MAF_04_workflow.py
"""

import asyncio
from dataclasses import dataclass
from uuid import uuid4

from agent_framework import (
    AgentRunResponseUpdate,
    AgentRunUpdateEvent,
    ChatMessage,
    Contents,
    Executor,
    Role,
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
    user_messages: list[ChatMessage]
    agent_messages: list[ChatMessage]


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
            ChatMessage(
                role=Role.SYSTEM,
                text=(
                    "You review AI agent responses. Approve only if the "
                    "answer is relevant, accurate, clear, and complete."
                ),
            ),
            *request.user_messages,
            *request.agent_messages,
            ChatMessage(role=Role.USER, text="Please review the agent's response."),
        ]

        response = await self._chat_client.get_response(
            messages=messages, response_format=_Verdict,
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
        self._pending: dict[str, tuple[ReviewRequest, list[ChatMessage]]] = {}

    @handler
    async def handle_user(self, user_messages: list[ChatMessage], ctx: WorkflowContext[ReviewRequest]) -> None:
        messages = [
            ChatMessage(role=Role.SYSTEM, text="You are a helpful assistant."),
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
            contents: list[Contents] = []
            for msg in request.agent_messages:
                contents.extend(msg.contents)
            await ctx.add_event(
                AgentRunUpdateEvent(
                    self.id,
                    data=AgentRunResponseUpdate(contents=contents, role=Role.ASSISTANT),
                )
            )
            return

        print(f"  Worker: retrying with feedback")
        messages.append(ChatMessage(role=Role.SYSTEM, text=review.feedback))
        messages.append(ChatMessage(role=Role.SYSTEM, text="Regenerate the response."))
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

    worker_client = OpenAIChatClient(model_id="gpt-4o-mini")
    reviewer_client = OpenAIChatClient(model_id="gpt-4o-mini")

    worker = Worker(id="worker", chat_client=worker_client)
    reviewer = Reviewer(id="reviewer", chat_client=reviewer_client)

    agent = (
        WorkflowBuilder()
        .add_edge(worker, reviewer)
        .add_edge(reviewer, worker)
        .set_start_executor(worker)
        .build()
        .as_agent()
    )

    query = "Explain in three sentences why containers are useful for AI agent sandboxing."
    print(f"User: {query}\n")

    async for event in agent.run_stream(query):
        print(f"\nApproved response:\n{event}")

    print("\n=== Done ===")


if __name__ == "__main__":
    asyncio.run(main())
