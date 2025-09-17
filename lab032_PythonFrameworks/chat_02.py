from openai import OpenAI

# Initialize client
client = OpenAI()

print("🤖 AI Chatbot (type 'exit' to quit)\n")

# Store conversation history
messages = []

# Loop until we exit
while True:
    # Ask the user for input
    user_input = input("You: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Goodbye!")
        break

    # Append user message to history
    messages.append({"role": "user", "content": [{"type": "text", "text": user_input}]})

    # Create response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "text"},
        temperature=1,
        max_completion_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        store=False
    )

    ai_reply = response.choices[0].message.content
    print(f"AI: {ai_reply}\n")

    # Append assistant response to history
    messages.append({"role": "assistant", "content": [{"type": "text", "text": ai_reply}]})
