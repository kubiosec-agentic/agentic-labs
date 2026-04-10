"""
Enterprise-ready OpenAI agent exposed as a FastAPI service.

Demonstrates:
- Structured logging (JSON) for observability
- Health check endpoint for container orchestration
- Graceful shutdown
- Environment-based configuration (no hardcoded secrets)
- Request/response tracing with correlation IDs
- Error handling with proper HTTP status codes
"""

import asyncio
import logging
import json
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agents import Agent, Runner, function_tool


# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("agent_service")


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------
@function_tool
def get_weather(city: str) -> str:
    """Return the current weather for a city (stub)."""
    # In production this would call a real weather API
    return f"The weather in {city} is 18C and sunny."


@function_tool
def get_time(timezone: str) -> str:
    """Return the current time in a timezone (stub)."""
    return f"The current time in {timezone} is 14:30 UTC."


agent = Agent(
    name="Enterprise Assistant",
    instructions=(
        "You are a helpful assistant with access to weather and time tools. "
        "Always use the tools when the user asks about weather or time. "
        "Be concise."
    ),
    tools=[get_weather, get_time],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"


class ChatResponse(BaseModel):
    response: str
    correlation_id: str
    duration_ms: float


# ---------------------------------------------------------------------------
# App lifecycle (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Agent service starting up")

    # Validate required configuration
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY is not set, exiting")
        sys.exit(1)

    yield

    logger.info("Agent service shutting down gracefully")


app = FastAPI(
    title="Agent Service",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Middleware: correlation ID
# ---------------------------------------------------------------------------
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    """Health check for container orchestration (K8s, ECS, etc.)."""
    return {
        "status": "healthy",
        "service": "agent-service",
        "checks": {
            "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        },
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    """Send a message to the agent and get a response."""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    start = time.monotonic()

    logger.info(
        "Incoming request",
        extra={"correlation_id": correlation_id},
    )

    try:
        result = await Runner.run(agent, req.message)
        duration_ms = (time.monotonic() - start) * 1000

        logger.info(
            f"Request completed in {duration_ms:.0f}ms",
            extra={"correlation_id": correlation_id},
        )

        return ChatResponse(
            response=result.final_output,
            correlation_id=correlation_id,
            duration_ms=round(duration_ms, 1),
        )

    except Exception as e:
        duration_ms = (time.monotonic() - start) * 1000
        logger.exception(
            f"Agent error after {duration_ms:.0f}ms",
            extra={"correlation_id": correlation_id},
        )
        raise HTTPException(status_code=500, detail="Agent processing failed")


# ---------------------------------------------------------------------------
# Local dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agent_service:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=True,
    )
