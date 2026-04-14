"""
Custom LiteLLM Proxy Logger
============================
Logs every LLM call flowing through the proxy: model, tokens, cost,
latency, and whether guardrails flagged anything.

Docs: https://docs.litellm.ai/docs/proxy/logging
"""

import json
import sys
import logging
import datetime as dt
from litellm.integrations.custom_logger import CustomLogger
import litellm

logger = logging.getLogger("proxy_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


class ProxyCallLogger(CustomLogger):
    """Structured JSON logger for all proxy LLM traffic."""

    # ── helpers ──────────────────────────────────────────────────
    @staticmethod
    def _ts() -> str:
        return dt.datetime.utcnow().isoformat() + "Z"

    @staticmethod
    def _safe_json(obj) -> str:
        try:
            return json.dumps(obj, default=str)
        except Exception:
            return str(obj)

    def _extract_meta(self, kwargs: dict) -> dict:
        """Pull useful metadata out of the kwargs dict."""
        litellm_params = kwargs.get("litellm_params", {})
        metadata = litellm_params.get("metadata", {})
        return {
            "model": kwargs.get("model"),
            "call_type": kwargs.get("call_type"),
            "user": kwargs.get("user"),
            "request_id": metadata.get("request_id"),
            "guardrails": metadata.get("guardrails"),
        }

    # ── lifecycle hooks ──────────────────────────────────────────
    def log_pre_api_call(self, model, messages, kwargs):
        meta = self._extract_meta(kwargs)
        record = {
            "ts": self._ts(),
            "event": "llm_pre_call",
            "model": model,
            "message_count": len(messages) if messages else 0,
            "metadata": meta,
        }
        logger.info(f"[PROXY-LOG] {self._safe_json(record)}")

    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        pass  # async version handles success logging

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        pass  # async version preferred

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        meta = self._extract_meta(kwargs)
        usage = {}
        cost = 0.0

        try:
            usage = dict(response_obj.get("usage", {}))
        except Exception:
            pass

        try:
            cost = litellm.completion_cost(completion_response=response_obj)
        except Exception:
            pass

        latency_ms = (
            (end_time - start_time).total_seconds() * 1000
            if start_time and end_time
            else None
        )

        record = {
            "ts": self._ts(),
            "event": "llm_success",
            "model": meta["model"],
            "call_type": meta["call_type"],
            "user": meta["user"],
            "request_id": meta["request_id"],
            "guardrails_applied": meta["guardrails"],
            "usage": usage,
            "cost_usd": round(cost, 6),
            "latency_ms": round(latency_ms, 1) if latency_ms else None,
        }
        logger.info(f"[PROXY-LOG] {self._safe_json(record)}")

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        meta = self._extract_meta(kwargs)
        exception = kwargs.get("exception", "unknown")
        latency_ms = (
            (end_time - start_time).total_seconds() * 1000
            if start_time and end_time
            else None
        )

        record = {
            "ts": self._ts(),
            "event": "llm_failure",
            "model": meta["model"],
            "call_type": meta["call_type"],
            "user": meta["user"],
            "request_id": meta["request_id"],
            "error": str(exception)[:500],
            "latency_ms": round(latency_ms, 1) if latency_ms else None,
        }
        logger.info(f"[PROXY-LOG] {self._safe_json(record)}")

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        pass  # async version preferred


# ── Singleton referenced by config.yaml ──────────────────────────
proxy_handler_instance = ProxyCallLogger()
