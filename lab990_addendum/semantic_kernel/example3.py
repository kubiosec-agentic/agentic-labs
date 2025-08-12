import os
import asyncio
from duckduckgo_search import DDGS  # <== New simplified search
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments
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

    def _get_fallback_info(self, topic: str) -> str:
        """Provide fallback information for common topics."""
        fallback_info = {
            "quantum physics": "Quantum physics is a fundamental theory in physics that describes the physical properties of nature at the scale of atoms and subatomic particles. It introduces concepts like superposition, entanglement, and wave-particle duality.",
            "artificial intelligence": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. It includes machine learning, natural language processing, and computer vision.",
            "machine learning": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
            "data science": "Data science is an interdisciplinary field that uses scientific methods, processes, algorithms and systems to extract knowledge and insights from structured and unstructured data.",
            "blockchain": "Blockchain is a distributed ledger technology that maintains a continuously growing list of records linked and secured using cryptography.",
            "python programming": "Python is a high-level, interpreted programming language known for its simple syntax and versatility in web development, data science, and automation.",
            "climate change": "Climate change refers to long-term shifts in global temperatures and weather patterns, primarily caused by human activities since the mid-20th century.",
        }

        topic_lower = topic.lower()
        for key, info in fallback_info.items():
            if key in topic_lower:
                return f"Information about '{topic}': {info}"

        return f"'{topic}' is an interesting and specialized topic that combines various concepts and principles from its field of study."

async def generate_funny_intro(kernel, topic: str) -> str:
    """Generate a funny introduction for a given topic with search results."""

    enhanced_prompt = """
    First, search for information about the topic: {{search.search_topic $topic}}

    Based on the search results above, write a funny introduction for a presentation about {{$topic}}.
    Make the introduction humorous while incorporating some of the factual information you found.
    Keep it engaging and light-hearted, suitable for a general audience.
    """

    print(f"🔍 Searching for information about '{topic}' and generating a funny introduction...")

    result = await kernel.invoke_prompt(
        prompt=enhanced_prompt,
        arguments=KernelArguments(topic=topic)
    )

    return str(result)

async def main():
    # 1. Load OpenAI key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")

    # 2. Create the kernel
    kernel = Kernel()

    # 3. Add OpenAI chat completion service
    service_id = "openai"
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            api_key=api_key,
            ai_model_id="gpt-3.5-turbo"
        )
    )

    # 4. Add the search plugin
    search_plugin = SearchPlugin()
    kernel.add_plugin(search_plugin, plugin_name="search")

    # 5. Demo with multiple topics
    topics = [
        "quantum physics",
        "artificial intelligence", 
        "climate change",
        "blockchain technology",
        "space exploration"
    ]

    print("🎭 Funny Introduction Generator with Search")
    print("=" * 50)

    for topic in topics:
        result = await generate_funny_intro(kernel, topic)

        print(f"\n{'='*60}")
        print(f"TOPIC: {topic.upper()}")
        print('='*60)
        print(result)
        print()

        await asyncio.sleep(1)

    # 6. Interactive mode
    print("\n🎯 Interactive Mode - Enter your own topics!")
    print("Type 'quit' to exit")

    while True:
        try:
            custom_topic = input("\nEnter a topic for a funny introduction: ").strip()
            if custom_topic.lower() in ['quit', 'exit', 'q']:
                break

            if custom_topic:
                result = await generate_funny_intro(kernel, custom_topic)
                print(f"\n{'='*60}")
                print(f"TOPIC: {custom_topic.upper()}")
                print('='*60)
                print(result)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\n👋 Thanks for using the Funny Introduction Generator!")

if __name__ == "__main__":
    asyncio.run(main())
