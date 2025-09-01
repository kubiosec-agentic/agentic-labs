# Import the required libraries
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Pick a small Qwen model (CPU friendly)
model_id = "Qwen/Qwen2.5-0.5B"  # or "Qwen/Qwen2.5-1.5B"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)

# Ensure CPU usage
device = torch.device("cpu")
model.to(device)

# Example prompt
prompt = """Explain me what the Log4j exploit issue is."""

# Tokenize the input
inputs = tokenizer(prompt, return_tensors="pt").to(device)
attention_mask = inputs.get("attention_mask", None)

# Generate response
outputs = model.generate(
    inputs["input_ids"],
    attention_mask=attention_mask,
    max_new_tokens=1500,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    pad_token_id=tokenizer.eos_token_id
)

# Decode the output
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("=== Model Output ===")
print(response)
