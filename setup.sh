#!/bin/bash
set -euo pipefail

echo "=== AutoRed Setup ==="

# 1. Install Python dependencies
echo "Installing Python dependencies..."
pip install requests matplotlib numpy

# 2. Configure environment
if [ ! -f .env ]; then
    echo "Creating .env — add your OLLAMA_API_KEY"
    cat > .env <<'EOF'
OLLAMA_MODELS=/lambda/nfs/apart-main/ollama_models
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=2
# OLLAMA_API_KEY=your_key_here
EOF
    echo "WARNING: Set OLLAMA_API_KEY in .env for cloud API access"
else
    echo ".env already exists"
fi

# 3. Check cloud API
if grep -q "OLLAMA_API_KEY=" .env && ! grep -q "^#.*OLLAMA_API_KEY" .env; then
    echo "Testing cloud API..."
    source <(grep -v '^#' .env | sed 's/^/export /')
    python3 -c "from models import check_cloud_health; print('Cloud API:', 'OK' if check_cloud_health() else 'FAIL')"
fi

# 4. Install local Ollama as fallback (optional)
if command -v ollama &> /dev/null; then
    echo "Ollama CLI found. Pulling local fallback model..."
    ollama pull gemma3:12b
else
    echo "No local Ollama — cloud-only mode. Install ollama for local fallback."
fi

# 5. Run smoke test
echo ""
echo "Running smoke tests..."
python3 smoke_test.py

echo ""
echo "=== Setup Complete ==="
echo "Run: nohup python3 run.py > run_stdout.log 2>&1 &"
