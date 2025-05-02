from langchain.agents import AgentExecutor, create_react_agent
from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI
from langchain import hub

import warnings
warnings.filterwarnings("ignore")

# Initialize the Python REPL tool
tools = []

# Define instructions for the agent
instructions = """You are an agent designed to answer mathematical questions."""

# Load a prompt template from LangChain Hub
base_prompt = hub.pull("langchain-ai/react-agent-template")
prompt = base_prompt.partial(instructions=instructions)

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

# Create the agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# Set up the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Example usage
response = agent_executor.invoke({"input": "Can you multiply 5 and 6 and 8 and take sqrt of the result?"})
print(response)
