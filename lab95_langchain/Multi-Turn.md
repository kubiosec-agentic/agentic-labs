
# 🔁 Multi-Turn Conversation with LangChain

## Introduction

This example demonstrates how to handle **multi-turn conversations** using LangChain without agents.  
We simulate a dialogue between a user and a chat model across multiple turns while maintaining **context** using the `RunnableWithMessageHistory` utility.

---

## 🧠 Why Multi-Turn?

LLMs are more effective when they understand what was said before. Multi-turn allows the model to:
- Track the flow of conversation
- Refer to previous questions/answers
- Mimic real human-like dialogue

---

## 🔧 Code Example
```python
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

# 1. Set up model and prompt
llm = ChatOpenAI()

system = SystemMessagePromptTemplate.from_template("You are a helpful assistant.")
prompt = ChatPromptTemplate.from_messages([
    system,
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])
chain = prompt | llm | StrOutputParser()

# 2. Add message history wrapper
message_history = ChatMessageHistory()
chat_chain = RunnableWithMessageHistory(
    chain,
    lambda session_id: message_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 3. Run multiple turns
session_id = "my-convo"

print(chat_chain.invoke({"input": "Hi, who won the World Cup in 2018?"}, config={"configurable": {"session_id": session_id}}))
print(chat_chain.invoke({"input": "Where was it held?"}, config={"configurable": {"session_id": session_id}}))
print(chat_chain.invoke({"input": "Who was the top scorer?"}, config={"configurable": {"session_id": session_id}}))
```

---

## 💬 What’s Happening?

- The conversation is split across **multiple invocations**, but the model remembers context using `ChatMessageHistory`.
- The `RunnableWithMessageHistory` wraps the chain and feeds back prior messages on each turn.
- `session_id` keeps track of which conversation the history belongs to.

---

## ✅ Summary

| Concept | Description |
|--------|-------------|
| `ChatPromptTemplate` | Builds a structured chat input |
| `RunnableWithMessageHistory` | Maintains dialogue context between turns |
| `ChatMessageHistory` | Stores messages across the session |
| `session_id` | Identifies the specific conversation |
| `invoke()` | Executes one turn in the dialogue |

---

This setup is ideal for building chatbots or support systems with **context awareness** — no agents required!
