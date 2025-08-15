import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("Prompt Server Demo Agent")

@fast.agent(
    instruction="You are a helpful assistant that can access saved conversation prompts",
    servers=["prompts"]
)
async def main():
    async with fast.run() as agent:
        print("=== Prompt Server Demo ===")
        print("This agent can load saved conversation histories using the prompts server.")
        print("First, let's have a conversation that we can save...")
        
        # Initial conversation
        response1 = await agent.send("What are the key benefits of using AI agents?")
        print(f"Agent: {response1}")
        
        # Continue conversation
        response2 = await agent.send("Can you elaborate on the automation benefits?")
        print(f"Agent: {response2}")
        
        # Save the conversation history
        print("\n=== Saving Conversation ===")
        print("Use: ***SAVE_HISTORY conversation.json")
        print("This will save our current conversation to a file that can be loaded later.")
        
        # Demonstrate how to access prompt server resources
        print("\n=== Accessing Saved Prompts ===")
        print("The prompts server can load previously saved conversations.")
        print("Use /prompts to see available saved conversations.")
        
        # Interactive mode for further testing
        print("\nStarting interactive mode - try saving history and loading prompts:")
        await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())