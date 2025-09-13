from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
import openai
import os
from datetime import datetime


# --- Set OpenAI API key ---
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()


# --- Define datetime tool ---
def get_current_datetime():
    """Returns the current date and time."""
    now = datetime.now()
    return now.strftime("Current date and time: %Y-%m-%d %H:%M:%S")


# --- Tool definitions for OpenAI function calling ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# --- Prompt Template ---
prompt = ChatPromptTemplate.from_template("Answer this question: {text}")


# --- OpenAI call as a Runnable with tool support ---
def call_openai_with_tools(prompt_value):
    messages = prompt_value.to_messages()
    openai_messages = [
        {"role": "user" if msg.type == "human" else msg.type, "content": msg.content}
        for msg in messages
    ]
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=openai_messages,
        tools=tools,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    # Check if tool was called
    if message.tool_calls:
        # Execute the tool
        for tool_call in message.tool_calls:
            if tool_call.function.name == "get_current_datetime":
                tool_result = get_current_datetime()
                
                # Add tool result back to conversation
                openai_messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call.model_dump()]
                })
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
                
                # Get final response
                final_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=openai_messages
                )
                return final_response.choices[0].message.content
    
    return message.content


llm = RunnableLambda(call_openai_with_tools)
parser = StrOutputParser()


# --- Chain: Prompt → LLM → Output ---
chain = prompt | llm | parser 


# --- Run inference ---
result = chain.invoke({"text": "What is the current date and time?"})
print(result)
