"""
Security trace analysis with the Responses API.

Uses the OpenAI Responses API directly (not the Agent SDK) to analyze
a sysdig system call trace. This is the "raw client" approach for
comparison with the Agent SDK version in agent_07.

Input: data/docker-curl-https.txt (sysdig capture of curl inside Docker).
"""

from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env

with open("data/docker-curl-https.txt", "r", encoding="utf-8") as f:
    text = f.read()

instructions = """You are a security and malware analyst.
- First provide a concise summary of the process being traced.
- Then list the key points and phases in the trace (5-10 bullets).
- Avoid opinions or speculation; stick to the facts.
"""

response = client.responses.create(
    model="gpt-4o-mini",
    instructions=instructions,
    input=f'Text:\n"""\n{text}\n"""',
)

summary = response.output_text or "".join(
    msg.content[0].text
    for msg in response.output
    if msg.role == "assistant"
)
print(summary)
