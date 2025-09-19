"""Writing assistant.
pip instal gradio
"""
import os
import gradio as gr
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai.chat_models import ChatOpenAI


LLM = ChatOpenAI(
    model="gpt-3.5-turbo",  # Fixed deprecated model_name parameter
    temperature=0.0,
    api_key=os.getenv("OPENAI_API_KEY")
)
MISSION = (
    "You are a helpful assistant that can fix and improve writing in terms of"
    " style, punctuation, grammar, vocabulary, and orthography so that it looks like something"
    " that a native speaker would write."
)

PREFIX = (
    "Give feedback on incorrect spelling, grammar, and expressions of the text"
    " below. Check the tense consistency. Explain grammar rules and examples for"
    " grammar rules. Give hints so the text becomes more concise and engrossing.\n"
    "Text: {text}."
    ""
    "Feedback: "
)


def suggest_improvements(input_text: str, temperature: float) -> str:
    """Suggest improvements to the text."""
    # Create a new LLM instance with the specified temperature
    llm_with_temp = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    messages = [
        SystemMessage(content=MISSION),
        HumanMessage(content=PREFIX.format(text=input_text)),
    ]
    
    # Use the correct invoke method
    response = llm_with_temp.invoke(messages)
    return response.content


demo = gr.Interface(
    fn=suggest_improvements,
    inputs=[
        gr.Textbox(label="Text to improve", lines=5, placeholder="Enter the text you want to improve..."),
        gr.Slider(0.0, 1.0, value=0.0, label="Temperature", info="Higher values = more creative responses")
    ],
    outputs=[gr.Textbox(label="Suggestions", lines=10)],
    title="Writing Assistant",
    description="Get feedback on spelling, grammar, style, and suggestions to improve your writing.",
)
if __name__ == "__main__":
    with demo:
        gr.HTML(
            "<center>Powered by <a href='https://github.com/langchain_ai/langchain'>LangChain "
            "🦜️🔗</a></center>"
        )  # noqa: E501

    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)