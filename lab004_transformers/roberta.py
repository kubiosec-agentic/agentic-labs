# Import the required libraries
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

# Pick a small encoder model fine-tuned for extractive QA (CPU friendly)
model_id = "deepset/roberta-base-squad2"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForQuestionAnswering.from_pretrained(model_id)

question = "Who wrote The Hobbit?"
context = "... The Hobbit is a fantasy novel by J. R. R. Tolkien ..."

print("Question:", question)
print("Context:", context)

# Tokenize question and context together (the model reads both at once)
inputs = tokenizer(question, context, return_tensors="pt")

# Run the model: it scores every token as a possible answer start / end
with torch.no_grad():
    outputs = model(**inputs)

# Pick the most likely start and end token
start = outputs.start_logits.argmax()
end = outputs.end_logits.argmax()

# Decode the answer span back to text
# (if the model thinks there is no answer, it points at the first token "<s>")
answer_tokens = inputs["input_ids"][0][start : end + 1]
answer = tokenizer.decode(answer_tokens)

print("Answer:", answer.strip())
