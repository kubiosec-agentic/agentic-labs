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

# Microsoft Agent Framework + A2A integration.
# a2a-sdk shipped 1.0 GA and agent-framework-a2a now REQUIRES
# "a2a-sdk>=1.0,<2" and "agent-framework-core>=1.15.0". The old
# "a2a-sdk>=0.3.26,<1.0" pin makes pip fail with ResolutionImpossible.
# agent-framework-a2a is still published as a beta (1.0.0bYYMMDD).
pip install --quiet \
  "agent-framework-core>=1.15.0" \
  "agent-framework-openai>=1.14.0" \
  "agent-framework-a2a>=1.0.0b260821" \
  "a2a-sdk>=1.0,<2"

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
