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

# Install specific pre-release versions to avoid Redis dependency issues on Python 3.14
pip install --quiet --pre \
  "agent-framework-core==1.0.0b251216" \
  "agent-framework-a2a==1.0.0b251216"

pip install --quiet openai httpx

echo ""
echo "Setup complete."
echo "  source $VENV/bin/activate"
echo ""
echo "Required environment variables:"
echo "  export OPENAI_API_KEY=\"sk-...\""
echo "  export OPENAI_CHAT_MODEL_ID=\"gpt-4o-mini\""
echo ""
echo "Make sure the ADK server is running first, then:"
echo "  python demo.py"
