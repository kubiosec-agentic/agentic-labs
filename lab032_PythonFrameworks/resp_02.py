from openai import OpenAI
client = OpenAI()

print("----First Response----")
response = client.responses.create(
    model="gpt-4o-mini",
    input="tell me a joke",
)
print(response.output_text)

print("----Second Response----")
second_response = client.responses.create(
    model="gpt-4o-mini",
    previous_response_id=response.id,
    input=[{"role": "user", "content": "explain why this is funny."}],
)
print(second_response.output_text)

print("----3rd Response----")
third_response = client.responses.create(
    model="gpt-4o-mini",
    previous_response_id=second_response.id,
    input=[{"role": "user", "content": "Summarise the actions of this thread."}],
)
print(third_response.output_text)
