"""Model and environment configuration for the red team security audit.

Uses Google AI Studio (not VertexAI) by default. Override with environment
variables if needed: RED_TEAM_MODEL, TARGET_MODEL, EVALUATOR_MODEL.

Based on google/adk-samples/ai-security-agent (Apache 2.0).
"""

import os
from dataclasses import dataclass

from google.genai import types


@dataclass
class SecurityAuditConfig:
    """Model assignments for each role in the red team pipeline.

    The red team agent uses high temperature for creative attacks.
    The target uses low temperature for consistent behavior.
    The evaluator uses zero temperature for deterministic verdicts.
    """

    # The attacker/orchestrator needs a model that will comply with AUTHORIZED
    # adversarial generation. Cheap safety-tuned models refuse this exercise
    # (gemini-3.8-flash and gpt-4o-mini both decline "Prompt Injection");
    # gpt-4o complies. Non-Gemini names are routed through LiteLLM (see
    # resolve_model), so the attacker runs on OpenAI while the target and
    # evaluator stay on cheap Gemini flash. Override any of these via env.
    red_team_model: str = os.getenv("RED_TEAM_MODEL", "openai/gpt-4o")
    target_model: str = os.getenv("TARGET_MODEL", "gemini-3.8-flash")
    evaluator_model: str = os.getenv("EVALUATOR_MODEL", "gemini-3.8-flash")


config = SecurityAuditConfig()


def resolve_model(name: str):
    """Return the model ADK should use for `name`.

    Gemini names ('gemini-...', 'models/gemini-...') are passed to ADK as
    plain strings. Any provider-prefixed name ('openai/gpt-4o',
    'anthropic/claude-...') is routed through LiteLLM, which lets the pipeline
    mix providers -- the attacker can run on OpenAI while the target and
    evaluator run on Gemini. LiteLLM reads the matching provider key from the
    environment (OPENAI_API_KEY for openai/*).
    """
    if "/" in name and not name.startswith("models/"):
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model=name)
    return name


def permissive_safety_settings() -> list:
    """Disable Gemini's platform content filters for this red-team pipeline.

    This is an AUTHORIZED, sandboxed AI-safety lab. The goal is to generate
    adversarial test prompts and check whether the TARGET violates its own
    safety constitution (see safety_rules.py), not to exercise Gemini's
    platform filter. Left at defaults, Gemini blocks the red-team agent's
    output; it arrives as an empty response (finish_reason=SAFETY) and
    stalls the pipeline. NEVER disable these filters in a production app.
    """
    categories = [
        types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    ]
    return [
        types.SafetySetting(category=c, threshold=types.HarmBlockThreshold.BLOCK_NONE)
        for c in categories
    ]
