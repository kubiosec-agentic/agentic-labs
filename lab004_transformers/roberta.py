from transformers import pipeline

qa = pipeline(
    "question-answering",
    model="deepset/roberta-base-squad2",
    device="cpu"  # You can use mps or cuda if available
)

question = "Who wrote The Hobbit?"
context = "... The Hobbit is a fantasy novel by J. R. R. Tolkien ..."

print("Question:", question)
print("Context:", context)

out = qa(
    question=question,
    context=context
)
print(out)