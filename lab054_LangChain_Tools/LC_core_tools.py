"""
LangChain runnables with OpenAI function calling.

Extends the LC_core.py pattern by adding a tool (get_current_datetime).
The RunnableLambda handles the three-phase tool-call cycle internally:

  1. Model requests the tool via tool_calls
  2. Code executes get_current_datetime() and appends the result
  3. Model produces a final answer that includes the live timestamp

This is a minimal example of combining LangChain's chain abstraction
with OpenAI's function-calling mechanism.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from openai import OpenAI
from datetime import datetime

client = OpenAI()  # reads OPENAI_API_KEY from env


# ---- Tool: current date and time ----

def get_current_datetime():
    """Returns the current date and time as a formatted string."""
    now = datetime.now()
    return now.strftime("Current date and time: %Y-%m-%d %H:%M:%S")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ---- Prompt template ----
prompt = ChatPromptTemplate.from_template("Answer this question: {text}")


# ---- OpenAI call with tool support, wrapped as a Runnable ----

def call_openai_with_tools(prompt_value):
    messages = prompt_value.to_messages()
    openai_messages = [
        {
            "role": "user" if msg.type == "human" else msg.type,
            "content": msg.content,
        }
        for msg in messages
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=openai_messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    message = response.choices[0].message

    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "get_current_datetime":
                tool_result = get_current_datetime()

                openai_messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call.model_dump()],
                })
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

                final = client.chat.completions.create(
                    model="gpt-4o",
                    messages=openai_messages,
                )
                return final.choices[0].message.content

    return message.content


llm = RunnableLambda(call_openai_with_tools)
parser = StrOutputParser()

# ---- Chain: Prompt -> LLM (with tools) -> Output ----
chain = prompt | llm | parser

result = chain.invoke({"text": "What is the current date and time?"})
print(result)
