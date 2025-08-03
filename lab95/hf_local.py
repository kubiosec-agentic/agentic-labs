from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
import warnings
from transformers import logging

# Suppress warnings - this is the minimal needed
warnings.filterwarnings("ignore", category=UserWarning)
logging.set_verbosity_error()

# Create a pipeline with a small, reliable model (simple approach with minimal fixes):
llm = HuggingFacePipeline.from_model_id(
    model_id="Qwen/Qwen2-0.5B-Instruct",  
    task="text-generation",
    model_kwargs={
        "device_map": "cpu", # Use mps for Mac M series or auto for CUDO
        "torch_dtype": "float16",  # Much more efficient on GPU
        "low_cpu_mem_usage": True,  # Memory optimization
    },
    pipeline_kwargs=dict(
        max_new_tokens=512,  # Can handle much longer responses with GPU power
        do_sample=True,
        temperature=0.7,
        repetition_penalty=1.1,
        return_full_text=False,
        clean_up_tokenization_spaces=True,
    ),
)


chat_model = ChatHuggingFace(llm=llm)

# Use it like any other LangChain LLM
messages = [
    SystemMessage(content="You're a helpful assistant"),
    HumanMessage(
        content="Explain the concept of machine learning in simple terms"
    ),
]

print("Generating response...")
ai_msg = chat_model.invoke(messages)
print(ai_msg.content)
