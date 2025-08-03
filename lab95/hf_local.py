from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
import torch
import platform
import os
import warnings
from transformers import logging

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
logging.set_verbosity_error()  # Only show errors from transformers

# Auto-detect system and optimize accordingly
def get_system_config():
    system = platform.system()
    machine = platform.machine()
    
    print(f"Detected system: {system} {machine}")
    
    # Auto-detect device and set optimal configuration
    if torch.cuda.is_available():
        device = "cuda"
        torch_dtype = torch.float16  # Use float16 for GPU
        threads = None  # Let CUDA handle threading
        max_tokens = 256  # Can handle more tokens on GPU
        print("🚀 Using GPU acceleration!")
    elif (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() 
          and "arm64" in machine.lower()):  # Only use MPS on Apple Silicon
        device = "mps"  # Apple Silicon GPU
        torch_dtype = torch.float16
        threads = None
        max_tokens = 128
        print("🍎 Using Apple Silicon MPS acceleration!")
    else:
        device = "cpu"
        torch_dtype = torch.float32  # Better for CPU
        # Optimize threads based on CPU
        cpu_count = os.cpu_count() or 4  # Default to 4 if None
        if "arm" in machine.lower() or "aarch64" in machine.lower():
            threads = min(8, cpu_count)  # Apple Silicon or ARM
            max_tokens = 128
            print("🍎 Optimizing for Apple Silicon CPU")
        else:
            threads = min(4, cpu_count // 2)  # Intel or other x86
            max_tokens = 64
            print("⚡ Optimizing for Intel/x86 CPU")
    
    return device, torch_dtype, threads, max_tokens

print("Setting up model with auto-detection...")
print("This may take a few minutes on first run to download the model...")

# Get optimal configuration for this system
device, torch_dtype, threads, max_tokens = get_system_config()

# Set threads if using CPU
if threads:
    torch.set_num_threads(threads)
    print(f"Set torch threads to: {threads}")

# Create a pipeline optimized for the detected system:
model_kwargs = {
    "torch_dtype": torch_dtype,
    "low_cpu_mem_usage": True,
}

# Add device mapping based on detected device
if device == "cpu":
    model_kwargs["device_map"] = "cpu"
elif device == "mps":
    model_kwargs["device_map"] = "mps"
# For CUDA, let it auto-detect

llm = HuggingFacePipeline.from_model_id(
    model_id="Qwen/Qwen2-0.5B-Instruct",  # Small, fast, and reliable Qwen2 model
    task="text-generation",
    model_kwargs=model_kwargs,
    pipeline_kwargs=dict(
        max_new_tokens=max_tokens,
        do_sample=True,  # Enable sampling for better responses
        temperature=0.7,  # Add some creativity
        top_p=0.9,
        repetition_penalty=1.1,
        return_full_text=False,
        clean_up_tokenization_spaces=True,
    ),
)

print("Model loaded successfully!")

print("Creating chat model...")
chat_model = ChatHuggingFace(llm=llm)

# Use it like any other LangChain LLM
print("Preparing messages...")
messages = [
    SystemMessage(content="You're a helpful assistant"),
    HumanMessage(
        content="Explain the concept of machine learning in simple terms"
    ),
]

print("Generating response... (this may take some time depending on your system)")
ai_msg = chat_model.invoke(messages)
print("\n" + "="*50)
print("AI Response:")
print("="*50)
print(ai_msg.content)
print("="*50)
