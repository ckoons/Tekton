#!/bin/bash
#
# Run script for Prometheus component in Tekton
#

# Determine the Tekton root directory (parent of this component)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEKTON_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Set environment variables
PROMETHEUS_PORT=8006
export PROMETHEUS_PORT

# Set up environment and Python path
source "$TEKTON_ROOT/shared/utils/setup_env.sh"
setup_tekton_env "$SCRIPT_DIR" "$TEKTON_ROOT"

# Create logs directory
LOG_DIR="${TEKTON_LOG_DIR:-$TEKTON_ROOT/.tekton/logs}"
mkdir -p "$LOG_DIR"

# Check if Prometheus is already running
if nc -z localhost $PROMETHEUS_PORT 2>/dev/null; then
    echo "Prometheus is already running on port $PROMETHEUS_PORT"
    exit 0
fi

echo "Starting Prometheus on port $PROMETHEUS_PORT..."

# Change to the component directory
cd "${SCRIPT_DIR}" || { echo "Failed to change to Prometheus directory"; exit 1; }

# Run the server
python -m prometheus > "$LOG_DIR/prometheus.log" 2>&1 &
PROMETHEUS_PID=$!
echo "Prometheus server started with PID: $PROMETHEUS_PID"

# Wait for the server to start (up to 10 seconds)
for i in {1..10}; do
    if nc -z localhost $PROMETHEUS_PORT 2>/dev/null; then
        echo "Prometheus is running at http://localhost:$PROMETHEUS_PORT"
        break
    fi
    echo -n "."
    sleep 1
done

# Check if server started successfully
if ! nc -z localhost $PROMETHEUS_PORT 2>/dev/null; then
    echo "Prometheus failed to start on port $PROMETHEUS_PORT"
    echo "Check logs at $LOG_DIR/prometheus.log for details"
    exit 1
fi

# Register with Hermes if available
if [[ -f "${TEKTON_ROOT}/scripts/tekton-register" ]]; then
    echo "Registering Prometheus with Hermes..."
    ${TEKTON_ROOT}/scripts/tekton-register register --component prometheus --config "${TEKTON_ROOT}/config/components/prometheus.yaml" &
    REGISTER_PID=$!
fi

# Set up trap for clean shutdown
trap "kill $PROMETHEUS_PID 2>/dev/null; exit" EXIT SIGINT SIGTERM

# Keep the script running
wait $PROMETHEUS_PID