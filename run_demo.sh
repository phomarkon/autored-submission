#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

BANNER='
  ┌─────────────────────────────────────────────────┐
  │  AutoRed: Measuring the Elicitation Gap         │
  │  AI Control Hackathon 2026                      │
  │                                                 │
  │  Opening http://localhost:8501                   │
  └─────────────────────────────────────────────────┘
'

# Try Docker first (most portable)
if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
    echo "$BANNER"
    echo "  Starting with Docker..."
    echo ""
    docker build -t autored-demo . -q
    exec docker run --rm -p 8501:8501 autored-demo

# Fall back to uv + venv
elif command -v uv &>/dev/null; then
    if [ ! -d ".venv" ]; then
        echo "  Setting up Python environment..."
        uv venv .venv
        source .venv/bin/activate
        uv pip install streamlit
    else
        source .venv/bin/activate
    fi
    echo "$BANNER"
    exec streamlit run demo.py --server.headless true --server.port 8501

# Last resort: pip
elif command -v python3 &>/dev/null; then
    echo "  Installing streamlit..."
    python3 -m pip install --quiet streamlit 2>/dev/null || \
        python3 -m pip install --quiet --break-system-packages streamlit
    echo "$BANNER"
    exec python3 -m streamlit run demo.py --server.headless true --server.port 8501

else
    echo "Error: Need docker, uv, or python3. Install one and retry."
    exit 1
fi
