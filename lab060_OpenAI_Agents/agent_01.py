"""
Simple synchronous agent.

The most minimal example: a single agent with no tools, no handoffs,
executed via Runner.run_sync (the synchronous wrapper around Runner.run).
"""

from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
