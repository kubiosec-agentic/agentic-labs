
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain.agents import create_react_agent, AgentExecutor, Tool
from langchain_experimental.tools import PythonREPLTool
from langchain import hub
import warnings

# Suppress LangSmith warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langsmith")


# your weather tool
def get_weather(location: str) -> str:
    """Get weather at a location."""
    return "It's sunny in " + location

class OutputSchema(BaseModel):
    """Schema for response."""
    answer: str
    justification: str

llm = ChatOpenAI(model="gpt-4o")


# your structured + tool-bound LLM
structured_llm = llm.bind_tools(
    [get_weather],
    response_format=OutputSchema,
    strict=True,
)

# import Python REPL tool
repl_tool = PythonREPLTool()

# Create agent that can call both tools
agent_tools = [
    Tool(
      name="get_weather",
      func=get_weather,
      description="Get the weather at a location"
    ),
    repl_tool  # Python code executor
]

# Get the react prompt
prompt = hub.pull("hwchase17/react")

# Create the react agent
agent = create_react_agent(llm, agent_tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)

# Now queries can go through the agent
tool_call_resp = structured_llm.invoke("What is the weather in SF?")

# And agent can dynamically run Python when needed:
agent_response = agent_executor.invoke({"input": "Obtain obtain using code the environment variables and format them in a makup table in your response"})


#printing the responses
print(agent_response)
