"""
SQL simulation with OpenAI function calling.

The LLM generates a SQL query based on a natural-language request, then
calls a local tool to "execute" it. The tool returns mock results, and
the LLM summarizes the outcome.

Supports OPENAI_BASE_URL override (useful with mitmproxy in Example 5).
"""

import json
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY and OPENAI_BASE_URL from env

# --- Local tool: simulates a SQL handler ---
def find_product(sql_query):
    print(f"[tool] Executing SQL: {sql_query}")
    return [
        {"name": "pen", "color": "blue", "price": 1.99},
        {"name": "pen", "color": "red", "price": 1.78},
    ]

# --- Tool schema ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "find_product",
            "description": "Create a SQL query to find or update product data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "A SQL query string to retrieve or modify product info",
                    }
                },
                "required": ["sql_query"],
            },
        },
    }
]

def llm(user_question, model="gpt-4o"):
    messages = [{"role": "user", "content": user_question}]

    # Step 1: LLM decides to call the tool
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    messages.append(response_message)

    tool_calls = response_message.tool_calls
    if not tool_calls:
        print("Warning: No tool call was returned.")
        return None, None

    # Step 2: Execute the tool locally
    tool_call = tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    if function_name == "find_product":
        tool_output = find_product(function_args["sql_query"])
    else:
        tool_output = []

    # Step 3: Feed tool result back; LLM produces final answer
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": function_name,
        "content": json.dumps(tool_output),
    })

    second_response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return function_args, second_response


if __name__ == "__main__":
    functionarg, answer = llm("Create an SQL query to update the price of the blue pen to 5 dollars")

    if functionarg and answer:
        print(f"SQL Statement: {functionarg['sql_query']}")
        print(f"GPT Response:  {answer.choices[0].message.content}")
    else:
        print("Could not retrieve a valid function call or LLM response.")
