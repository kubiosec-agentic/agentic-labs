"""Target sub-agent: the banking chatbot being tested.

Low temperature (0.1) for consistent, predictable behavior. The target
follows strict safety rules defined in safety_rules.py. The red team
agent tries to make it violate these rules.

Based on google/adk-samples/ai-security-agent (Apache 2.0).
"""

from google.adk.agents import Agent
from google.genai import types

from ..config import config, permissive_safety_settings, resolve_model
from ..safety_rules import BANKING_AGENT_IDENTITY, BANKING_SAFETY_CONSTITUTION


def create() -> Agent:
    model = resolve_model(config.target_model)
    return Agent(
        name="target",
        model=model,
        instruction=(
            f"{BANKING_AGENT_IDENTITY}\n{BANKING_SAFETY_CONSTITUTION}\n"
            "When answering the user, adhere strictly to these protocols."
        ),
        # Disable the platform filter (Gemini only) so ONLY the constitution
        # above governs the target's behavior. That is what the evaluator grades.
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            safety_settings=(
                permissive_safety_settings() if isinstance(model, str) else None
            ),
        ),
    )
