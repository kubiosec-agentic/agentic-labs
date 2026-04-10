"""
Exercise: Traceloop observability for OpenAI calls.

Wraps a simple GPT-4o call in a Traceloop workflow decorator so that
every invocation is traced end-to-end (latency, tokens, errors).

Prerequisites:
    export TRACELOOP_API_KEY="tl_..."
    export OPENAI_API_KEY="sk-..."

Run:
    python3 traceloop_01.py
"""

from openai import OpenAI
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow

Traceloop.init(
    app_name="joke_generation_service",
    disable_batch=True,
)


@workflow(name="joke_creation")
def create_joke():
  client = OpenAI()
  completion = client.chat.completions.create(
      model="gpt-4o",
      messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
  )
  return completion.choices[0].message.content


if __name__ == "__main__":
  print(create_joke())
