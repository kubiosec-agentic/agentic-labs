import os
import json
from openai import OpenAI

# ✅ Optional: Set a custom base URL (e.g. for Azure/OpenRouter/local)
BASE_URL = os.getenv("OPENAI_BASE_URL")  # or set manually: "https://api.openai.com/v1"
API_KEY = os.getenv("OPENAI_API_KEY")    # Set this in your shell or .env

# ✅ Initialize OpenAI client once
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL if BASE_URL else "https://api.openai.com/v1"
)

# 🛠️ Local function simulating a SQL handler
def find_product(sql_query):
    print(f"🛠️ Executing SQL: {sql_query}")
    return [
        {"name": "pen", "color": "blue", "price": 1.99},
        {"name": "pen", "color": "red", "price": 1.78},
    ]

# 📦 Tool schema definition (replaces old functions=...)
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

# 🤖 Single LLM logic with tool use
def llm(user_question, model="gpt-4o"):
    messages = [{"role": "user", "content": user_question}]
    try:
        # 🔁 Step 1: Get tool call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        tool_calls = response_message.tool_calls
        if not tool_calls:
            print("⚠️ No tool call was returned.")
            return None, None

        # 🧠 Step 2: Execute tool locally
        tool_call = tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        if function_name == "find_product":
            tool_output = find_product(function_args["sql_query"])
        else:
            tool_output = []

        # 🗣️ Step 3: Let GPT respond using tool result
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(tool_output),
        })

        second_response = client.chat.completions.create(
            model=model,
            messages=messages
        )

        return function_args, second_response

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return None, None


# 🚀 Example usage
if __name__ == "__main__":
    functionarg, answer = llm("Create an SQL query to update the price of the blue pen to 5 dollars")

    if functionarg and answer:
        print("✅ SQL Statement:", functionarg['sql_query'])
        print("💬 GPT Response:", answer.choices[0].message.content)
    else:
        print("❌ Could not retrieve a valid function call or LLM response.")
