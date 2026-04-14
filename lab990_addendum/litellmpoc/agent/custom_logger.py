"""
Custom Trace Processor for the OpenAI Agents SDK
==================================================
Captures every agent span (LLM calls, tool calls, MCP calls,
guardrail checks, handoffs) and emits structured JSON logs.

Docs: https://openai.github.io/openai-agents-python/tracing/
"""

import json
import datetime as dt
from typing import Any

from agents.tracing import TracingProcessor, Trace, Span


class AgentCallLogger(TracingProcessor):
    """Structured JSON logger for all agent-level events."""

    @staticmethod
    def _ts() -> str:
        return dt.datetime.utcnow().isoformat() + "Z"

    @staticmethod
    def _safe_json(obj: Any) -> str:
        try:
            return json.dumps(obj, default=str)
        except Exception:
            return str(obj)

    # ── trace-level events ───────────────────────────────────────
    def on_trace_start(self, trace: Trace) -> None:
        record = {
            "ts": self._ts(),
            "event": "trace_start",
            "trace_id": trace.trace_id,
            "name": trace.name,
        }
        print(f"[AGENT-LOG] {self._safe_json(record)}", flush=True)

    def on_trace_end(self, trace: Trace) -> None:
        record = {
            "ts": self._ts(),
            "event": "trace_end",
            "trace_id": trace.trace_id,
            "name": trace.name,
        }
        print(f"[AGENT-LOG] {self._safe_json(record)}", flush=True)

    # ── span-level events ────────────────────────────────────────
    def on_span_start(self, span: Span) -> None:
        span_data = {}
        try:
            if hasattr(span, "span_data") and span.span_data:
                span_data = {
                    "type": getattr(span.span_data, "type", "unknown"),
                }
        except Exception:
            pass

        record = {
            "ts": self._ts(),
            "event": "span_start",
            "span_id": span.span_id,
            "name": getattr(span, "name", None),
            "span_data": span_data,
        }
        print(f"[AGENT-LOG] {self._safe_json(record)}", flush=True)

    def on_span_end(self, span: Span) -> None:
        span_data = {}
        try:
            if hasattr(span, "span_data") and span.span_data:
                raw = span.span_data
                span_data = {
                    "type": getattr(raw, "type", "unknown"),
                }
                # Capture model + usage for generation spans
                if getattr(raw, "type", "") == "generation":
                    span_data["model"] = getattr(raw, "model", None)
                    usage = getattr(raw, "usage", None)
                    if usage:
                        span_data["usage"] = {
                            "input_tokens": getattr(usage, "input_tokens", None),
                            "output_tokens": getattr(usage, "output_tokens", None),
                        }
                # Capture tool name for function spans
                if getattr(raw, "type", "") == "function":
                    span_data["tool_name"] = getattr(raw, "name", None)
                    span_data["output"] = str(getattr(raw, "output", ""))[:200]
                # Capture MCP tool call details
                if getattr(raw, "type", "") == "mcp_tool":
                    span_data["tool_name"] = getattr(raw, "name", None)
                    span_data["server"] = getattr(raw, "server", None)
        except Exception:
            pass

        record = {
            "ts": self._ts(),
            "event": "span_end",
            "span_id": span.span_id,
            "name": getattr(span, "name", None),
            "span_data": span_data,
        }
        print(f"[AGENT-LOG] {self._safe_json(record)}", flush=True)

    def shutdown(self) -> None:
        print("[AGENT-LOG] Trace processor shutting down.", flush=True)

    def force_flush(self) -> None:
        pass  # stdout is already unbuffered
