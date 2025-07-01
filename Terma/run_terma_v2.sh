#!/bin/bash
# Run the new Terma v2 - Native Terminal Orchestrator

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Terma v2 - Native Terminal Orchestrator"
echo "   This is the NEW Terma - no web terminals, just native!"
echo ""

# Set Python path
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Set default Tekton environment if not already set
export TERMA_PORT="${TERMA_PORT:-8004}"
export HERMES_URL="${HERMES_URL:-http://localhost:8001}"
export REGISTER_WITH_HERMES="${REGISTER_WITH_HERMES:-true}"

# Show configuration
echo "Configuration:"
echo "  Port: ${TERMA_PORT}"
echo "  Hermes URL: ${HERMES_URL}"
echo "  Register with Hermes: ${REGISTER_WITH_HERMES}"
echo ""

# Check if aish-proxy exists
AISH_PROXY="${HOME}/projects/github/aish/aish-proxy"
if [ ! -f "$AISH_PROXY" ]; then
    echo "⚠️  Warning: aish-proxy not found at $AISH_PROXY"
    echo "   Terminals will launch but without AI enhancement"
    echo "   Install aish to enable AI features"
else
    echo "✅ Found aish-proxy at $AISH_PROXY"
fi

echo ""

# Run the service
python3 -m terma.api.main