import os
import json
from flask import Flask, request, jsonify
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_experimental.tools import PythonREPLTool
from logging.handlers import RotatingFileHandler
from langchain_core.prompts import PromptTemplate
from datetime import datetime
import logging


# Initialize Flask application
app = Flask(__name__)


# Set up logging
def setup_logging(app):
    # Set up a specific logger with our desired output level
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug("Logging setup complete")

setup_logging(app)

# Prompting
template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

prompt = PromptTemplate.from_template(template)

@app.route("/chat/completions", methods=["POST"])
def openai_proxy():
    data = request.get_json()
    messages = data.get("messages", [])
    response_content = ""

    # Langchain agent to calculate results
    tools = [PythonREPLTool()]
#   llm = ChatOpenAI()
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    # Run the agent
    response = agent_executor.invoke({"input": messages, "chat_history": ""})
    response_content = response["output"]

    # Prepare log data for ES
    log_data = {
       "request": messages[-1] if messages else "",
       "response": response_content,
       "@timestamp": datetime.now().isoformat()
    }

    # Log processing request
    app.logger.info(log_data)

    # Calculate token usage
    prompt_tokens = sum(len(message) for message in messages)
    completion_tokens = len(response_content)
    total_tokens = prompt_tokens + completion_tokens

    # Based on the results, create an OpenAI client.chat.completions response
    return jsonify({
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content": response_content,
                    "role": "assistant"
                }
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }
    })

# Start the development server
if __name__ == "__main__":
    app.run(port=5000)
