from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the document
with open("data/docker-curl-https.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Define prompt instructions
instructions = """You are a security and malware analyst.
- First provide a concise summary of the process being traced
- Then list the key points and phases in the trace (5–10 bullets).
- Avoid opinions or speculation, stick to the facts.
"""

# Send to Responses API
response = client.responses.create(
    model="gpt-4.1",
    instructions=instructions,
    input=f"""Text:
\"\"\"
{text}
\"\"\""""
)

# Extract and print summary
summary = response.output_text or "".join(
    msg.content[0].text for msg in response.output if msg.role == "assistant"
)
print(summary)
