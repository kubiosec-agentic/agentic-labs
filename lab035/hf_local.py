from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
import warnings
from transformers import logging

# Suppress warnings - this is the minimal needed
warnings.filterwarnings("ignore", category=UserWarning)
logging.set_verbosity_error()

# Create a pipeline with a small, reliable model (simple approach with minimal fixes):
llm = HuggingFacePipeline.from_model_id(
    model_id="Qwen/Qwen2-0.5B-Instruct",  # Small instruction-tuned model for general tasks
    task="text-generation",  # Use this pipeline for generating text completions
    model_kwargs={
        "device_map": "mps",  # Use "cpu" to run on CPU; use "mps" for Apple Silicon or "auto" for GPU (e.g., CUDA)
        "torch_dtype": "float16",  # Use half-precision to reduce memory usage (GPU only)
        "low_cpu_mem_usage": True,  # Optimizes model loading by reducing RAM usage
    },
    pipeline_kwargs=dict(
        max_new_tokens=512,  # Limit the length of the generated output
        do_sample=True,  # Enable sampling (instead of greedy decoding) for more diverse outputs
        temperature=0.7,  # Controls randomness: higher = more random, lower = more focused
        repetition_penalty=1.1,  # Penalizes repeated phrases to improve output quality
        return_full_text=False,  # Only return the generated portion, not the original prompt
        clean_up_tokenization_spaces=True,  # Remove extraneous spaces in output
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
