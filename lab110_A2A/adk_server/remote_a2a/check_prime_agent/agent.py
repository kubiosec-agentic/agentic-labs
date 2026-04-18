from google.adk.agents import Agent

def check_prime(nums: list[int]) -> dict:
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        d = 3
        while d * d <= n:
            if n % d == 0:
                return False
            d += 2
        return True

    return {str(n): is_prime(n) for n in nums}

root_agent = Agent(
    name="check_prime_agent",
    model="gemini-2.5-flash-lite",
    description="Checks whether numbers are prime.",
    instruction=(
        "You check if numbers are prime. "
        "When the user provides one or more integers, call the check_prime tool "
        "with a list of ints and return the result."
    ),
    tools=[check_prime],
)
