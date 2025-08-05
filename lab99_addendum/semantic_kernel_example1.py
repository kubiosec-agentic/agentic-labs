import os
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments

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

    # 4. Define a simple prompt function
    prompt = """Write a funny introduction for a presentation about {{$topic}}."""

    # Create and invoke the function directly
    result = await kernel.invoke_prompt(
        prompt=prompt,
        arguments=KernelArguments(topic="quantum physics")
    )
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
