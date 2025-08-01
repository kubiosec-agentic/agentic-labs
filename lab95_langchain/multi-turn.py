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
