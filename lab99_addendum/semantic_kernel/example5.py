import os
import asyncio
import aiohttp
import ssl
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# Example plugin(s)
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class SearchPlugin:
    @kernel_function(name="search_topic", description="Search for real information about a topic using DuckDuckGo")
    async def search_topic(self, topic: str) -> str:
        """Search for real information about a topic using DuckDuckGo API."""
        try:
            # DuckDuckGo instant answer API
            url = f"https://api.duckduckgo.com/?q={topic}&format=json&no_html=1&skip_disambig=1"
            
            # Create SSL context that's more permissive
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract useful information
                        abstract = data.get('Abstract', '')
                        definition = data.get('Definition', '')
                        answer = data.get('Answer', '')
                        
                        if abstract:
                            return f"Search results for '{topic}': {abstract[:500]}..."
                        elif definition:
                            return f"Definition of '{topic}': {definition[:500]}..."
                        elif answer:
                            return f"Information about '{topic}': {answer[:500]}..."
                        else:
                            return f"No detailed information found for '{topic}' from search API."
                    else:
                        return f"Search API returned status {response.status} for '{topic}'."
        except Exception as e:
            print(f"Search error: {e}")
            return f"Search failed for '{topic}' due to network or API error."

class SummarizerPlugin:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
    
    @kernel_function(name="summarize", description="Use AI to summarize text into key points")
    async def summarize(self, text: str) -> str:
        """Create an AI-powered summary of the provided text."""
        if len(text.strip()) < 50:
            return f"Summary: {text}"
        
        # Use AI to create a better summary
        summary_prompt = f"""
        Please create a concise summary of the following text in 3-4 bullet points:
        
        {text}
        
        Format your response as bullet points starting with •
        Focus on the most important information and key concepts.
        """
        
        try:
            summary_response = await self.kernel.invoke_prompt(
                prompt=summary_prompt,
                arguments=KernelArguments()
            )
            return str(summary_response)
        except Exception as e:
            print(f"AI summarization error: {e}")
            return f"Summary: {text[:200]}..." if len(text) > 200 else f"Summary: {text}"

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
    kernel.add_plugin(SummarizerPlugin(kernel), "summary")

    # Allow searching for different topics
    topic = "quantum computing"  # Default topic, can be changed
    
    print(f"🔍 Searching for information about: {topic}")
    print("=" * 50)

    # Create a prompt that uses both plugins effectively
    prompt = f"""
    Search for information about {topic}: {{{{search.search_topic "{topic}"}}}}
    
    Now create a summary of the search results: {{{{summary.summarize $search_results}}}}
    
    Based on the search results and summary above, provide a comprehensive and informative response about {topic} that includes:
    1. A clear explanation of what {topic} is
    2. Key principles and concepts
    3. Current applications and potential future uses
    
    Please make your response engaging and accessible to a general audience.
    """

    response = await kernel.invoke_prompt(
        prompt=prompt,
        arguments=KernelArguments(search_results=f"{topic} research data")
    )

    print("🤖 Assistant Response:")
    print("=" * 50)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
