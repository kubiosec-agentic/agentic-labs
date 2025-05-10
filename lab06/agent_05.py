import asyncio
import io
import sys
from agents import Agent, Runner, function_tool

@function_tool
def evaluate_python(code: str) -> str:
    # Redirect stdout to capture prints
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        # Try evaluating the code (e.g. "2 + 2")
        result = eval(code)
        output = sys.stdout.getvalue()
        if result is not None:
            output += repr(result)
    except SyntaxError:
        try:
            # If eval fails, try exec for statements (e.g. "print('hi')")
            exec(code)
            output = sys.stdout.getvalue()
        except Exception as e:
            output = f"Error during exec: {e}"
    except Exception as e:
        output = f"Error during eval: {e}"
    finally:
        # Restore stdout
        sys.stdout = old_stdout

    return output.strip()

agent = Agent(
    name="PythonEvaluator",
    instructions="You evaluate Python code provided in input.",
    tools=[evaluate_python],
)

async def main():
    result = await Runner.run(agent, input="What is the result of `2**8`?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
