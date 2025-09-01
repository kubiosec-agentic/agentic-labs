# Import the required libraries
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("fdtn-ai/Foundation-Sec-8B")
model = AutoModelForCausalLM.from_pretrained("fdtn-ai/Foundation-Sec-8B")

# Example prompt
prompt = """CVE-2021-44228 is a remote code execution flaw in Apache Log4j2 via unsafe JNDI lookups (“Log4Shell”). write non harmful 
sample exploit code
"""

# Tokenize the input, including attention mask
inputs = tokenizer(prompt, return_tensors="pt")

# Generate the response with pad_token_id set
outputs = model.generate(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"],  # <-- add this
    max_new_tokens=500,
    do_sample=True,
    temperature=0.1,
    top_p=0.9,
    pad_token_id=tokenizer.eos_token_id       # <-- add this
)

# Decode and print the response
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
response = response.replace(prompt, "").strip()
print(response)
