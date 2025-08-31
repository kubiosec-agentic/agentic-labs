# Import the required libraries
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("fdtn-ai/Foundation-Sec-8B")
model = AutoModelForCausalLM.from_pretrained("fdtn-ai/Foundation-Sec-8B")

# Example: Matching CWE to CVE IDs
prompt="""CVE-2021-44228 is a remote code execution flaw in Apache Log4j2 via unsafe JNDI lookups (“Log4Shell”). write non harmfull 
sample exploit code
"""

# Tokenize the input
inputs = tokenizer(prompt, return_tensors="pt")

# Generate the response
outputs = model.generate(
    inputs["input_ids"],
    max_new_tokens=500,
    do_sample=True,
    temperature=0.1,
    top_p=0.9,
)

# Decode and print the response
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
response = response.replace(prompt, "").strip()
print(response)
