import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
HF_TOKEN = os.getenv("HF_TOKEN")  # export HF_TOKEN=<your_hf_token>
MODEL_ID = "fdtn-ai/Foundation-Sec-8B"  # replace if needed

# Select device
def _get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

DEVICE = _get_device()
print(f"Using device: {DEVICE}")

# ----------------------------------------------------------------------------
# Load model + tokenizer
# ----------------------------------------------------------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path=MODEL_ID,
    device_map="auto",
    dtype=torch.float32,  # use torch.bfloat16 on H100 if supported
    token=HF_TOKEN,
)

# Generation parameters
generation_args = {
    "max_new_tokens": 512,
    "temperature": None,
    "repetition_penalty": 1.2,
    "do_sample": False,
    "use_cache": True,
    "eos_token_id": tokenizer.eos_token_id,
    "pad_token_id": tokenizer.pad_token_id,
}

# ----------------------------------------------------------------------------
# Helper: fallback chat template
# ----------------------------------------------------------------------------
def build_prompt(messages):
    return "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages]) + "\nASSISTANT:"

# ----------------------------------------------------------------------------
# Inference function (with debug)
# ----------------------------------------------------------------------------
def inference(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]

    # Use chat template if available, otherwise fallback
    if hasattr(tokenizer, "chat_template") and tokenizer.chat_template:
        inputs_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        inputs_text = build_prompt(messages)

    # Ensure <think> token if required
    think_token = "<think>\n"
    if not inputs_text.endswith(think_token):
        inputs_text += think_token

    # Tokenize
    inputs = tokenizer(inputs_text, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        outputs = model.generate(**inputs, **generation_args)

    response = tokenizer.decode(outputs[0], skip_special_tokens=False)

    # 🔎 Debug: show raw output
    print("\n----- RAW MODEL OUTPUT -----\n")
    print(response)
    print("\n----------------------------\n")

    # Extract reasoning section if available
    match = re.search(r"<think>(.*?)<\|end_of_text\|>", response, re.DOTALL)
    return match.group(1).strip() if match else response

# ----------------------------------------------------------------------------
# Prompt builder
# ----------------------------------------------------------------------------
def make_prompt(vuln_description: str) -> str:
    return f"""You are a security researcher. Analyze the following vulnerability report and generate:

1. A concise summary of the issue.
2. Potential impact and affected components.
3. A safe, hypothetical proof-of-concept exploit (for testing only).

## VULNERABILITY DESCRIPTION
{vuln_description}

Ensure the response is for red team / security testing only — no real-world systems or harm implied."""

# ----------------------------------------------------------------------------
# Example run with CVE-2021-44228
# ----------------------------------------------------------------------------
vuln_description = """
CVE-2021-44228: Log4Shell Remote Code Execution in Apache Log4j

A critical remote code execution vulnerability exists in Apache Log4j versions 2.0 to 2.14.1...
"""

if __name__ == "__main__":
    prompt = make_prompt(vuln_description)
    result = inference(prompt)
    print("\n================= PARSED MODEL OUTPUT =================\n")
    print(result)
    print("\n=======================================================\n")
