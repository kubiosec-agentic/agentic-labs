# Import the required libraries
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("fdtn-ai/Foundation-Sec-8B")
model = AutoModelForCausalLM.from_pretrained("fdtn-ai/Foundation-Sec-8B")

# Example: Matching CWE to CVE IDs
prompt="""CVE-2021-44228 is a remote code execution flaw in Apache Log4j2 via unsafe JNDI lookups (“Log4Shell”). The CWE is CWE-502.

CVE-2017-0144 is a remote code execution vulnerability in Microsoft’s SMBv1 server (“EternalBlue”) due to a buffer overflow. The CWE is CWE-119.

CVE-2014-0160 is an information-disclosure bug in OpenSSL’s heartbeat extension (“Heartbleed”) causing out-of-bounds reads. The CWE is CWE-125.

CVE-2017-5638 is a remote code execution issue in Apache Struts 2’s Jakarta Multipart parser stemming from improper input validation of the Content-Type header. The CWE is CWE-20.

CVE-2019-0708 is a remote code execution vulnerability in Microsoft’s Remote Desktop Services (“BlueKeep”) triggered by a use-after-free. The CWE is CWE-416.

CVE-2015-10011 is a vulnerability about OpenDNS OpenResolve improper log output neutralization. The CWE is"""

# Tokenize the input
inputs = tokenizer(prompt, return_tensors="pt")

# Generate the response
outputs = model.generate(
    inputs["input_ids"],
    max_new_tokens=3,
    do_sample=True,
    temperature=0.1,
    top_p=0.9,
)

# Decode and print the response
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
response = response.replace(prompt, "").strip()
print(response)
