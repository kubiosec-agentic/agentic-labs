import os
import asyncio
from semantic_kernel import Kernel
from ddgs import DDGS
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# Example plugin(s)
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class SearchPlugin:
    """A plugin that provides search functionality for topics."""

    @kernel_function(
        description="Search for information about a topic using DuckDuckGo",
        name="search_topic"
    )
    async def search_topic(self, topic: str) -> str:
        """Simplified DuckDuckGo search using duckduckgo-search package."""
        try:
            with DDGS() as ddgs:
                results = ddgs.text(topic, max_results=1)
                for r in results:
                    snippet = r.get("body", "")[:300]
                    if snippet:
                        return f"Search result for '{topic}': {snippet}..."
            return self._get_fallback_info(topic)
        except Exception:
            return self._get_fallback_info(topic)

class SummarizerPlugin:
    @kernel_function(name="summarize", description="Summarize text")
    async def summarize(self, text: str) -> str:
        return "- Point one\n- Point two\n- Point three"

async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY")

    kernel = Kernel()
    service_id = "openai"
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            api_key=api_key,
            ai_model_id="gpt-4"
        )
    )
    kernel.add_plugin(SearchPlugin(), "search")
    kernel.add_plugin(SummarizerPlugin(), "summary")

    # Create a prompt that uses both plugins
    prompt = """
    First, search for information about quantum computing: {{search.search_topic "quantum computing"}}
    
    Now summarize the search results: {{summary.summarize $search_result}}
    
    Based on this information, provide a comprehensive response about quantum computing.
    """

    response = await kernel.invoke_prompt(
        prompt=prompt,
        arguments=KernelArguments(search_result="quantum computing information")
    )

    print("Assistant:", response)

if __name__ == "__main__":
    asyncio.run(main())
