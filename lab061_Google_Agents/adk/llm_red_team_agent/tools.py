"""Tools exposed to the orchestrator agent.

Each tool wraps a sub-agent call: generate attack, simulate target response,
evaluate the interaction. The orchestrator chains them in sequence.

Based on google/adk-samples/ai-security-agent (Apache 2.0).
"""

from .agent_utils import execute_sub_agent
from .sub_agents import evaluator, red_team, target

red_team_worker = red_team.create()
target_worker = target.create()
evaluator_worker = evaluator.create()


def generate_attack_prompt(risk_category: str) -> str:
    """Asks the Red Team agent to generate an adversarial prompt.

    Use this first. The risk_category can be: Toxicity, Phishing,
    PII Leakage, Prompt Injection, Financial Advice, AML, etc.
    """
    print(f"\n  [Tool] Generating attack for '{risk_category}'...")
    return execute_sub_agent(red_team_worker, risk_category)


def simulate_target_response(attack_prompt: str) -> str:
    """Sends an attack prompt to the target banking agent and gets its response.

    Use this after you have an attack prompt from generate_attack_prompt.
    """
    print("  [Tool] Simulating target response...")
    return execute_sub_agent(target_worker, attack_prompt)


def evaluate_interaction(attack_prompt: str, target_response: str) -> str:
    """Asks the evaluator to judge whether the attack succeeded.

    Use this last. Returns a JSON verdict with PASS/FAIL and reasoning.
    """
    print("  [Tool] Evaluating interaction...")
    eval_query = f"[ATTACK]: {attack_prompt}\n[RESPONSE]: {target_response}"
    return execute_sub_agent(evaluator_worker, eval_query)
