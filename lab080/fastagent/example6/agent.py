import asyncio
from mcp_agent.core.fastagent import FastAgent

fast = FastAgent("Memory & State Transfer Demo")

@fast.agent(
    name="primary",
    instruction="You are a primary assistant that helps with various tasks and can remember our conversation history.",
    use_history=True
)
@fast.agent(
    name="analyst", 
    instruction="You are a data analyst specializing in analyzing conversation patterns and providing insights.",
    model="haiku",
    use_history=True
)
@fast.agent(
    name="summarizer",
    instruction="You are a summarizer that creates concise summaries of conversation history.",
    model="gpt-4o-mini", 
    use_history=True
)

async def main():
    async with fast.run() as agent:
        print("=== Memory & State Transfer Demo ===")
        print("This demo shows how FastAgent handles conversation memory and state transfer between agents.")
        
        # Start with primary agent
        print("\n1. Building conversation history with primary agent...")
        await agent.primary.send("Hi! I'm working on a project about sustainable energy. Can you help me understand the key types of renewable energy sources?")
        
        print("\n2. Continuing conversation to build context...")
        await agent.primary.send("What are the main challenges with solar energy implementation?")
        
        print("\n3. Adding more context...")
        await agent.primary.send("How does wind energy compare to solar in terms of efficiency and cost?")
        
        print("\n=== State Transfer Demo ===")
        print("\n4. Transferring conversation context to analyst agent...")
        
        # Transfer the conversation history to the analyst
        analyst_response = await agent.analyst.send([
            "Please analyze the conversation history I'm sharing with you and identify the main topics discussed and any patterns you notice.",
            *agent.primary.message_history
        ])
        print(f"Analyst insights: {analyst_response}")
        
        print("\n5. Transferring to summarizer agent...")
        # Transfer to summarizer
        summary_response = await agent.summarizer.send([
            "Please create a concise summary of this conversation about renewable energy:",
            *agent.primary.message_history
        ])
        print(f"Summary: {summary_response}")
        
        print("\n=== Saving Conversation State ===")
        print("To save conversation history, use: ***SAVE_HISTORY session_memory.json")
        print("This will preserve the conversation state for future sessions.")
        
        print("\n=== Memory Management Features ===")
        print("- Conversation history is maintained by default (use_history=True)")
        print("- History can be transferred between different agents/models")
        print("- Conversations can be saved and reloaded using the prompt server")
        print("- Different agents can have different memory configurations")
        
        print("\nStarting interactive mode to explore memory features:")
        await agent.primary.interactive()

if __name__ == "__main__":
    asyncio.run(main())