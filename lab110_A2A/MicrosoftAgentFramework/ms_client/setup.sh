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
# Note: a2a-sdk must be pinned to 0.3.x; the 1.0.0a alpha has breaking API changes
pip install --quiet \
  "agent-framework-core>=1.0.1" \
  "agent-framework-openai>=1.0.1" \
  "agent-framework-a2a>=1.0.0b260311" \
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
