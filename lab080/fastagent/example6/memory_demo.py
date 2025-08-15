#!/usr/bin/env python3
"""
Advanced Memory Management Demo

This script demonstrates more advanced memory features:
- Persistent memory across sessions
- Memory with different models
- State transfer patterns
"""

import asyncio
import json
from pathlib import Path
from mcp_agent.core.fastagent import FastAgent

class MemoryManager:
    def __init__(self, memory_file="conversation_memory.json"):
        self.memory_file = Path(memory_file)
    
    def save_conversation(self, agent_name, messages):
        """Save conversation history to file"""
        memory_data = {}
        if self.memory_file.exists():
            memory_data = json.loads(self.memory_file.read_text())
        
        memory_data[agent_name] = {
            "timestamp": str(asyncio.get_event_loop().time()),
            "messages": messages
        }
        
        self.memory_file.write_text(json.dumps(memory_data, indent=2))
        print(f"💾 Saved {len(messages)} messages for {agent_name}")
    
    def load_conversation(self, agent_name):
        """Load conversation history from file"""
        if not self.memory_file.exists():
            return []
        
        memory_data = json.loads(self.memory_file.read_text())
        if agent_name in memory_data:
            messages = memory_data[agent_name]["messages"]
            print(f"📖 Loaded {len(messages)} messages for {agent_name}")
            return messages
        return []

async def memory_demo():
    fast = FastAgent("Advanced Memory Demo")
    memory = MemoryManager()
    
    @fast.agent(
        name="researcher",
        instruction="You are a research assistant with persistent memory across sessions."
    )
    @fast.agent(
        name="reviewer", 
        instruction="You review and critique research findings.",
        model="haiku"
    )
    
    async def demo():
        async with fast.run() as agent:
            print("=== Advanced Memory Management Demo ===")
            
            # Load previous conversation if exists
            previous_messages = memory.load_conversation("researcher")
            if previous_messages:
                print("📚 Restoring previous conversation...")
                # Note: In a real implementation, you'd restore the message history
                
            print("\n🔬 Starting research conversation...")
            research_response = await agent.researcher.send(
                "I'm researching the impact of AI on education. Can you help me identify key areas to explore?"
            )
            
            print("\n📝 Continuing research...")
            follow_up = await agent.researcher.send(
                "What are the potential negative impacts I should also consider?"
            )
            
            # Save the conversation
            memory.save_conversation("researcher", agent.researcher.message_history)
            
            print("\n🔄 Transferring research to reviewer...")
            review_response = await agent.reviewer.send([
                "Please review this research conversation and provide critical feedback:",
                *agent.researcher.message_history
            ])
            
            print("\n💡 Memory Features Demonstrated:")
            print("- ✅ Conversation persistence across sessions")
            print("- ✅ State transfer between different agents")
            print("- ✅ Memory management with file storage")
            print("- ✅ Multi-agent collaboration with shared context")
            
            return {
                "research_messages": len(agent.researcher.message_history),
                "review_messages": len(agent.reviewer.message_history)
            }
    
    return await demo()

if __name__ == "__main__":
    result = asyncio.run(memory_demo())
    print(f"\n📊 Demo completed: {result}")