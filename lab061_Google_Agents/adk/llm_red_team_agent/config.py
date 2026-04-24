"""Model and environment configuration for the red team security audit.

Uses Google AI Studio (not VertexAI) by default. Override with environment
variables if needed: RED_TEAM_MODEL, TARGET_MODEL, EVALUATOR_MODEL.

Based on google/adk-samples/ai-security-agent (Apache 2.0).
"""

import os
from dataclasses import dataclass


@dataclass
class SecurityAuditConfig:
    """Model assignments for each role in the red team pipeline.

    The red team agent uses high temperature for creative attacks.
    The target uses low temperature for consistent behavior.
    The evaluator uses zero temperature for deterministic verdicts.
    """

    red_team_model: str = os.getenv("RED_TEAM_MODEL", "gemini-2.5-pro")
    target_model: str = os.getenv("TARGET_MODEL", "gemini-2.5-pro")
    evaluator_model: str = os.getenv("EVALUATOR_MODEL", "gemini-2.5-pro")


config = SecurityAuditConfig()
