from typing import Annotated
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
import os
import asyncio

def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temperature = 53
    return f"The weather in {location} is {conditions[0]} with a high of {temperature}°C."

# Create the agent
agent = ChatAgent(
    name="WeatherAgent",
    description="A helpful agent that provides weather information",
    instructions="You are a weather assistant. Provide current weather information for any location.",
    chat_client=AzureOpenAIChatClient(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        endpoint="https://phbo-openai-1.openai.azure.com/",
        deployment_name="gpt-4o-mini",  # Use gpt-4o-mini as shown in the example
    ),
    tools=[get_weather],
)

# Test the agent
if __name__ == "__main__":
    print(asyncio.run(agent.run("What's the weather like in Seattle?")))


