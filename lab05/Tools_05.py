from openai import OpenAI
import json

client = OpenAI()

# Your local function (simulated SQL handler)
def find_product(sql_query):
    print(f"🛠️ Executing SQL: {sql_query}")
    return [
        {"name": "pen", "color": "blue", "price": 1.99},
        {"name": "pen", "color": "red", "price": 1.78},
    ]

# Tools spec (replaces deprecated "functions")
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

# Core LLM function
def llm(user_question):
    messages = [{"role": "user", "content": user_question}]

    try:
        # First request to get tool call
        response = client.chat.completions.create(
            model="gpt-4o",  # Or use "gpt-4-turbo"
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

        # Get first tool call (you could support multiple if needed)
        tool_call = tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        if function_name == "find_product":
            tool_output = find_product(function_args["sql_query"])
        else:
            tool_output = []

        # Send tool output back to LLM for final natural language reply
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(tool_output),
        })

        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        return function_args, second_response

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return None, None


# Run test prompt
functionarg, answer = llm("Create an SQL query to update the price of the blue pen")

# Output
if functionarg and answer:
    print("✅ SQL Statement:", functionarg['sql_query'])
    print("💬 GPT Response:", answer.choices[0].message.content)
else:
    print("❌ Could not retrieve a valid function call or LLM response.")
