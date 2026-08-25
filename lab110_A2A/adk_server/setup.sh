#!/usr/bin/env bash
set -e

echo "=== A2A Demo: ADK Server Setup ==="

VENV=".venv"

if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment in $VENV ..."
    python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

echo "Installing dependencies ..."
pip install --quiet --upgrade pip
# google-adk[a2a] pulls in bare a2a-sdk, which does NOT include the
# server-side HTTP deps (sse-starlette, starlette). Without them ADK logs
# "Failed to setup A2A agent ...: No module named 'sse_starlette'" at
# startup, mounts no A2A routes, and every agent-card URL returns 404.
# The [http-server] extra fixes that. a2a-sdk 1.x is GA and is what
# agent-framework-a2a requires on the client side.
pip install --quiet "google-adk[a2a]" "a2a-sdk[http-server]>=1.0,<2"

echo ""
echo "Setup complete."
echo "  source $VENV/bin/activate"
echo ""
echo "Authentication (choose one):"
echo "  Option A - Gemini API (simplest):"
echo "    export GOOGLE_API_KEY=\"your-gemini-api-key\""
echo ""
echo "  Option B - Vertex AI:"
echo "    export GOOGLE_GENAI_USE_VERTEXAI=true"
echo "    export GOOGLE_CLOUD_PROJECT=\"your-project-id\""
echo "    export GOOGLE_CLOUD_LOCATION=\"europe-west1\""
echo "    gcloud auth application-default login"
echo ""
echo "Start the A2A server:"
echo "  adk api_server --a2a --port 8001 remote_a2a"
echo ""
echo "Verify with:"
echo "  curl http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json"
