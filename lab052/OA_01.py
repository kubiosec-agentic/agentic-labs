import os
import json
from collections import Counter
from openai import OpenAI

client = OpenAI()

# --- Tool function ---
def summarize_directory(path: str) -> str:
    """Summarize file types in the given directory."""
    if not os.path.isdir(path):
        return f"Directory not found: {path}"

    extensions = []
    try:
        for entry in os.listdir(path):
            full = os.path.join(path, entry)
            if os.path.isfile(full):
                _, ext = os.path.splitext(entry)
                extensions.append(ext.lower() if ext else "no extension")
    except Exception as e:
        return f"Error reading '{path}': {e}"

    counts = Counter(extensions)
    if not counts:
        return f"No files found in '{path}'."

    lines = [f"{ext}: {count}" for ext, count in sorted(counts.items())]
    return f"Summary of file types in '{path}':\n" + "\n".join(lines)

# --- Initial conversation ---
messages = [
    {"role": "system", "content": "You are a helpful assistant that can summarize directory contents."},
    {"role": "user", "content": "Summarize the types of files in the current directory."}
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "summarize_directory",
            "description": "Summarize file types in a directory path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the directory"}
                },
                "required": ["path"]
            }
        }
    }
]

# --- 1) Ask the model; let it decide to call the tool ---
resp1 = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

msg1 = resp1.choices[0].message

if msg1.tool_calls:
    # Append the assistant's tool call message
    messages.append({
        "role": "assistant",
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            } for tc in msg1.tool_calls
        ]
    })

    # Execute each tool call and append corresponding tool results
    for tc in msg1.tool_calls:
        fn_name = tc.function.name
        raw_args = tc.function.arguments
        # <-- IMPORTANT: arguments is a JSON string; parse it safely
        try:
            args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
        except json.JSONDecodeError:
            args = {}

        if fn_name == "summarize_directory":
            dir_path = args.get("path", ".")
            result = summarize_directory(dir_path)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # --- 2) Ask the model to produce a final answer using the tool output ---
    resp2 = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    print(resp2.choices[0].message.content)

else:
    # No tool call; just print the model text
    print(msg1.content or "(no content)")
