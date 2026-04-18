#!/usr/bin/env bash
set -e

echo "=== A2A Demo: Microsoft Agent Framework Client Setup ==="

VENV=".venv"

if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment in $VENV ..."
    python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

echo "Installing dependencies ..."
pip install --quiet --upgrade pip

# Microsoft Agent Framework 1.0 GA + A2A integration
# The A2A protocol is 1.0 GA (March 2026), but the Python SDK (a2a-sdk)
# only has 1.0 alpha releases. Pin to 0.3.x for stability until the SDK
# ships a proper 1.0 GA. agent-framework-a2a is still in beta.
pip install --quiet \
  "agent-framework-core>=1.0.1" \
  "agent-framework-openai>=1.0.1" \
  "agent-framework-a2a>=1.0.0b260409" \
  "a2a-sdk>=0.3.26,<1.0"

pip install --quiet openai httpx

echo ""
echo "Setup complete."
echo "  source $VENV/bin/activate"
echo ""
echo "Required environment variables:"
echo "  export OPENAI_API_KEY=\"sk-...\""
echo "  export OPENAI_CHAT_MODEL=\"gpt-4o-mini\""
echo ""
echo "Make sure the ADK server is running first, then:"
echo "  python demo.py"
