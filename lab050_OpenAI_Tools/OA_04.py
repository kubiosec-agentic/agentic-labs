"""
Wikipedia research tool with OpenAI function calling.

A minimal, self-contained demonstration of tool use with the OpenAI Python SDK:
the model decides when to search Wikipedia, we run the search locally, hand the
result back, and the model synthesizes an answer from it.

    pip install openai            # httpx ships as an openai dependency
    export OPENAI_API_KEY=...
    python wikipedia_tool_demo.py
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from openai import OpenAI

# Model IDs move fast; override without editing the file.
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
MAX_TOOL_TURNS = 5

WIKI_API = "https://en.wikipedia.org/w/api.php"
# EDIT THIS. Wikimedia's robot policy requires a User-Agent that identifies the
# client and carries a contact URL or email; generic defaults ("python-httpx/..")
# get throttled or blocked. Note that Wikimedia also blocks many cloud/datacenter
# IP ranges outright, so this returns 403 from CI or a VPS even with a good UA --
# run it from a workstation, or arrange authenticated access with Wikimedia.
USER_AGENT = "SecurityInnovatorsDemo/1.0 (https://example.org; you@example.org)"

http = httpx.Client(
    headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, deflate"},
    timeout=15.0,
)

_client: OpenAI | None = None


def openai_client() -> OpenAI:
    """Lazy so the module imports (and the tool self-test runs) without a key."""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


# --- 1. The tool: plain Python, no LLM involved -----------------------------

def _wiki(**params: Any) -> dict:
    """One call against the MediaWiki action API."""
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    response = http.get(WIKI_API, params=params)
    response.raise_for_status()
    return response.json()


def _first_sentences(text: str, count: int = 3) -> str:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text.strip())
    return " ".join(parts[:count])


def search_security_innovators(query: str) -> dict:
    """Search Wikipedia and summarize the best-matching article.

    Tools should return data, not raise: any failure comes back as a status the
    model can read and react to (retry, rephrase, tell the user).
    """
    try:
        hits = _wiki(action="query", list="search", srsearch=query, srlimit=3)
        titles = [hit["title"] for hit in hits["query"]["search"]]
        if not titles:
            return {"status": "no_results", "query": query}

        # Titles come straight from search, so we resolve them exactly.
        # `redirects=1` follows real redirects; nothing guesses at a different
        # article the way the `wikipedia` package's auto_suggest does.
        page = _wiki(
            action="query",
            prop="extracts|info",
            inprop="url",
            exintro=1,
            explaintext=1,
            redirects=1,
            titles=titles[0],
        )["query"]["pages"][0]

        if page.get("missing"):
            return {"status": "not_found", "title": titles[0]}

        return {
            "status": "success",
            "title": page["title"],
            "summary": _first_sentences(page.get("extract", "")),
            "url": page["fullurl"],
            "related_pages": titles[1:],
        }
    except httpx.HTTPError as exc:
        return {"status": "error", "message": f"Wikipedia request failed: {exc}"}
    except (KeyError, ValueError) as exc:
        return {"status": "error", "message": f"Unexpected API response: {exc}"}


# --- 2. The schema the model sees -------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_security_innovators",
            "description": (
                "Search Wikipedia for cybersecurity pioneers, security researchers, "
                "or security concepts. Call once per person or topic to look up."
            ),
            # strict=True guarantees the arguments match the schema exactly.
            # It requires additionalProperties: false and every property listed
            # in `required`.
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A person's name or a security concept, e.g. 'Dan Kaminsky'.",
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    }
]

TOOL_REGISTRY = {"search_security_innovators": search_security_innovators}


def run_tool_call(tool_call) -> dict:
    """Dispatch one tool call, converting every failure into a readable result."""
    function = TOOL_REGISTRY.get(tool_call.function.name)
    if function is None:
        return {"status": "error", "message": f"Unknown tool: {tool_call.function.name}"}
    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as exc:
        return {"status": "error", "message": f"Malformed arguments: {exc}"}
    try:
        return function(**arguments)
    except TypeError as exc:
        return {"status": "error", "message": f"Bad arguments: {exc}"}


# --- 3. The agent loop ------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a cybersecurity historian. Help users learn about security innovators, "
    "pioneers, and researchers by searching Wikipedia. Search for each person "
    "individually rather than in one broad query, and cite the article URLs you used."
)


def security_research_llm(user_question: str, model: str = MODEL) -> str:
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_question},
    ]

    for _ in range(MAX_TOOL_TURNS):
        response = openai_client().chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message

        # Dump to a plain dict so `messages` stays homogeneous and serializable.
        # exclude_none drops null legacy fields the API rejects on the way back.
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return message.content or ""

        # One tool message per tool_call_id, in the same order.
        for tool_call in message.tool_calls:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(run_tool_call(tool_call)),
            })

    return "Stopped: reached the maximum number of tool-calling turns."


if __name__ == "__main__":
    import sys

    # `python wikipedia_tool_demo.py --selftest "Dan Kaminsky"` exercises the
    # tool on its own, no API key and no model involved.
    if "--selftest" in sys.argv:
        query = sys.argv[sys.argv.index("--selftest") + 1]
        print(json.dumps(search_security_innovators(query), indent=2))
        raise SystemExit

    print("Security Innovators Research Tool")
    print("=" * 50)
    print(security_research_llm(
        "Tell me about famous cybersecurity pioneers and innovators. "
        "Look up a few people who made significant contributions to computer security."
    ))