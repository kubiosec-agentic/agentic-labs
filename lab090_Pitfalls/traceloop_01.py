from openai import OpenAI
import os
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow

Traceloop.init()

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
