from pathlib import Path
import asyncio

from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

work_dir = Path("coding")
work_dir.mkdir(exist_ok=True)

def main():
    async def run():
        async with DockerCommandLineCodeExecutor(work_dir=work_dir, image="python:3.11") as executor:  # type: ignore
            print(
                await executor.execute_code_blocks(
                    code_blocks=[
                        CodeBlock(language="python", code="print('Hello, World!')"),
                    ],
                    cancellation_token=CancellationToken(),
                )
            )
    asyncio.run(run())

if __name__ == "__main__":
    main()
