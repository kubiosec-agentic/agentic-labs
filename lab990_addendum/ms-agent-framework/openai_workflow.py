# Copyright (c) Microsoft. All rights reserved.
# Updated to Microsoft Agent Framework 1.0 GA API
#
# Key changes from pre-1.0:
#   - ChatMessage -> Message (with contents= instead of text=)
#   - ChatClientProtocol -> SupportsChatGetResponse
#   - model_id= -> model=
#   - set_start_executor() fluent method -> start_executor= constructor param
#   - agent.run_stream() -> agent.run(stream=True)
#   - Contents -> list[Content] (Content is the unified content class)

"""
Sample: Workflow as Agent with Reflection and Retry Pattern

Purpose:
This sample demonstrates how to wrap a workflow as an agent using .as_agent().
It uses a reflection pattern where a Worker executor generates responses and a
Reviewer executor evaluates them. If the response is not approved, the Worker
regenerates the output based on feedback until the Reviewer approves it. Only
approved responses are emitted to the external consumer.

Key Concepts Demonstrated:
- WorkflowBuilder with .as_agent() to wrap a workflow as a regular agent.
- Cyclic workflow design (Worker / Reviewer) for iterative improvement.
- AgentRunUpdateEvent: Mechanism for emitting approved responses externally.
- Structured output parsing for review feedback using Pydantic.
- State management for pending requests and retry logic.

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    export OPENAI_CHAT_MODEL="gpt-4o-mini"
"""

import asyncio
import os
import sys
from dataclasses import dataclass
from uuid import uuid4

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("Error: OPENAI_API_KEY is not set. Run: export OPENAI_API_KEY=\"sk-...\"")

from agent_framework import (
    AgentRunResponseUpdate,
    AgentRunUpdateEvent,
    Content,
    Executor,
    Message,
    Role,
    SupportsChatGetResponse,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.openai import OpenAIChatClient
from pydantic import BaseModel


@dataclass
class ReviewRequest:
    """Structured request passed from Worker to Reviewer for evaluation."""

    request_id: str
    user_messages: list[Message]
    agent_messages: list[Message]


@dataclass
class ReviewResponse:
    """Structured response from Reviewer back to Worker."""

    request_id: str
    feedback: str
    approved: bool


class Reviewer(Executor):
    """Executor that reviews agent responses and provides structured feedback."""

    def __init__(self, id: str, chat_client: SupportsChatGetResponse) -> None:
        super().__init__(id=id)
        self._chat_client = chat_client

    @handler
    async def review(self, request: ReviewRequest, ctx: WorkflowContext[ReviewResponse]) -> None:
        print(f"Reviewer: Evaluating response for request {request.request_id[:8]}...")

        # Define structured schema for the LLM to return.
        class _Response(BaseModel):
            feedback: str
            approved: bool

        # Construct review instructions and context.
        messages = [
            Message(
                role=Role.SYSTEM,
                contents=[
                    "You are a reviewer for an AI agent. Provide feedback on the "
                    "exchange between a user and the agent. Indicate approval only if:\n"
                    "- Relevance: response addresses the query\n"
                    "- Accuracy: information is correct\n"
                    "- Clarity: response is easy to understand\n"
                    "- Completeness: response covers all aspects\n"
                    "Do not approve until all criteria are satisfied."
                ],
            )
        ]
        # Add conversation history.
        messages.extend(request.user_messages)
        messages.extend(request.agent_messages)

        # Add explicit review instruction.
        messages.append(Message(role=Role.USER, contents=["Please review the agent's responses."]))

        print("Reviewer: Sending review request to LLM...")
        response = await self._chat_client.get_response(messages=messages, response_format=_Response)

        parsed = _Response.model_validate_json(response.messages[-1].text)

        print(f"Reviewer: Review complete - Approved: {parsed.approved}")
        print(f"Reviewer: Feedback: {parsed.feedback}")

        # Send structured review result to Worker.
        await ctx.send_message(
            ReviewResponse(request_id=request.request_id, feedback=parsed.feedback, approved=parsed.approved)
        )


class Worker(Executor):
    """Executor that generates responses and incorporates feedback when necessary."""

    def __init__(self, id: str, chat_client: SupportsChatGetResponse) -> None:
        super().__init__(id=id)
        self._chat_client = chat_client
        self._pending_requests: dict[str, tuple[ReviewRequest, list[Message]]] = {}

    @handler
    async def handle_user_messages(self, user_messages: list[Message], ctx: WorkflowContext[ReviewRequest]) -> None:
        print("Worker: Received user messages, generating response...")

        # Initialize chat with system prompt.
        messages = [Message(role=Role.SYSTEM, contents=["You are a helpful assistant."])]
        messages.extend(user_messages)

        print("Worker: Calling LLM to generate response...")
        response = await self._chat_client.get_response(messages=messages)
        print(f"Worker: Response generated: {response.messages[-1].text}")

        # Add agent messages to context.
        messages.extend(response.messages)

        # Create review request and send to Reviewer.
        request = ReviewRequest(request_id=str(uuid4()), user_messages=user_messages, agent_messages=response.messages)
        print(f"Worker: Sending response for review (ID: {request.request_id[:8]})")
        await ctx.send_message(request)

        # Track request for possible retry.
        self._pending_requests[request.request_id] = (request, messages)

    @handler
    async def handle_review_response(self, review: ReviewResponse, ctx: WorkflowContext[ReviewRequest]) -> None:
        print(f"Worker: Received review for request {review.request_id[:8]} - Approved: {review.approved}")

        if review.request_id not in self._pending_requests:
            raise ValueError(f"Unknown request ID in review: {review.request_id}")

        request, messages = self._pending_requests.pop(review.request_id)

        if review.approved:
            print("Worker: Response approved. Emitting to external consumer...")
            contents: list[Content] = []
            for message in request.agent_messages:
                contents.extend(message.contents)

            # Emit approved result to external consumer via AgentRunUpdateEvent.
            await ctx.add_event(
                AgentRunUpdateEvent(self.id, data=AgentRunResponseUpdate(contents=contents, role=Role.ASSISTANT))
            )
            return

        print(f"Worker: Response not approved. Feedback: {review.feedback}")
        print("Worker: Regenerating response with feedback...")

        # Incorporate review feedback.
        messages.append(Message(role=Role.SYSTEM, contents=[review.feedback]))
        messages.append(
            Message(role=Role.SYSTEM, contents=["Please incorporate the feedback and regenerate the response."])
        )
        messages.extend(request.user_messages)

        # Retry with updated prompt.
        response = await self._chat_client.get_response(messages=messages)
        print(f"Worker: New response generated: {response.messages[-1].text}")

        messages.extend(response.messages)

        # Send updated request for re-review.
        new_request = ReviewRequest(
            request_id=review.request_id, user_messages=request.user_messages, agent_messages=response.messages
        )
        await ctx.send_message(new_request)

        # Track new request for further evaluation.
        self._pending_requests[new_request.request_id] = (new_request, messages)


async def main() -> None:
    print("Starting Workflow Agent Demo")
    print("=" * 50)

    # Initialize chat clients and executors.
    print("Creating chat client and executors...")
    mini_chat_client = OpenAIChatClient(model="gpt-4.1-nano")
    chat_client = OpenAIChatClient(model="gpt-4.1")
    reviewer = Reviewer(id="reviewer", chat_client=chat_client)
    worker = Worker(id="worker", chat_client=mini_chat_client)

    print("Building workflow with Worker / Reviewer cycle...")
    agent = (
        WorkflowBuilder(start_executor=worker)
        .add_edge(worker, reviewer)  # Worker sends responses to Reviewer
        .add_edge(reviewer, worker)  # Reviewer provides feedback to Worker
        .build()
        .as_agent()  # Wrap workflow as an agent
    )

    query = "Write code for parallel reading 1 million files on disk and write to a sorted output file."
    print(f"Running workflow agent with user query...")
    print(f"Query: '{query}'")
    print("-" * 50)

    # Run agent in streaming mode to observe incremental updates.
    async for event in agent.run(query, stream=True):
        print(f"Agent Response: {event}")

    print("=" * 50)
    print("Workflow completed!")


if __name__ == "__main__":
    print("Initializing Workflow as Agent Sample...")
    asyncio.run(main())
