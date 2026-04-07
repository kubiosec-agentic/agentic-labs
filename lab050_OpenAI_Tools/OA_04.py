"""
Wikipedia research tool with OpenAI function calling.

The LLM searches Wikipedia for information about cybersecurity pioneers,
retrieves summaries, and synthesizes a response. Demonstrates tool use
with an external API (Wikipedia) rather than a local function.
"""

import json
import wikipedia
from openai import OpenAI

client = OpenAI()


def search_security_innovators(query: str) -> str:
    """Search Wikipedia for information about security innovators."""
    try:
        search_results = wikipedia.search(query, results=3)

        if not search_results:
            return json.dumps({
                "status": "no_results",
                "message": f"No Wikipedia pages found for '{query}'",
            })

        page_title = search_results[0]
        try:
            summary = wikipedia.summary(page_title, sentences=3)
            page = wikipedia.page(page_title)

            return json.dumps({
                "status": "success",
                "title": page_title,
                "summary": summary,
                "url": page.url,
                "related_pages": search_results[1:3] if len(search_results) > 1 else [],
            })

        except wikipedia.exceptions.DisambiguationError as e:
            try:
                summary = wikipedia.summary(e.options[0], sentences=3)
                page = wikipedia.page(e.options[0])
                return json.dumps({
                    "status": "success",
                    "title": e.options[0],
                    "summary": summary,
                    "url": page.url,
                    "note": "Disambiguated result",
                    "other_options": e.options[1:4],
                })
            except Exception:
                return json.dumps({
                    "status": "disambiguation_error",
                    "message": f"Multiple pages found for '{query}'",
                    "options": e.options[:5],
                })

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# --- Tool schema ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_security_innovators",
            "description": "Search Wikipedia for information about cybersecurity pioneers, security researchers, or innovators",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (e.g., person name, security concept, or 'cybersecurity pioneers')",
                    }
                },
                "required": ["query"],
            },
        },
    }
]


def security_research_llm(user_question, model="gpt-4o"):
    """LLM with Wikipedia search for cybersecurity research."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a cybersecurity historian. Help users learn about security "
                "innovators, pioneers, and researchers by searching Wikipedia. "
                "Provide informative summaries about their contributions."
            ),
        },
        {"role": "user", "content": user_question},
    ]

    # Step 1: LLM decides to call the tool
    response = client.chat.completions.create(
        model=model, messages=messages, tools=tools, tool_choice="auto",
    )

    response_message = response.choices[0].message
    messages.append(response_message)

    tool_calls = response_message.tool_calls
    if not tool_calls:
        return response_message.content

    # Step 2: Execute Wikipedia searches
    for tool_call in tool_calls:
        function_args = json.loads(tool_call.function.arguments)
        search_result = search_security_innovators(function_args["query"])

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": search_result,
        })

    # Step 3: LLM synthesizes
    final = client.chat.completions.create(model=model, messages=messages)
    return final.choices[0].message.content


if __name__ == "__main__":
    print("Security Innovators Research Tool")
    print("=" * 50)

    research = security_research_llm(
        "Tell me about famous cybersecurity pioneers and innovators. "
        "Search for people who made significant contributions to computer security."
    )

    print(research)
