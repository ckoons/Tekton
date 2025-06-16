#!/bin/bash
# Fixed run script for Prometheus component in Tekton

# Determine the script directory and Tekton root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEKTON_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Set up port environment variable
PROMETHEUS_PORT=8006
export PROMETHEUS_PORT

# Make sure Python can find our modules
export PYTHONPATH="${SCRIPT_DIR}:${TEKTON_ROOT}:${PYTHONPATH}"

# Create log directory
LOG_DIR="${TEKTON_LOG_DIR:-$TEKTON_ROOT/.tekton/logs}"
mkdir -p "$LOG_DIR"

# Check if Prometheus is already running
if nc -z localhost $PROMETHEUS_PORT 2>/dev/null; then
    echo "Prometheus is already running on port $PROMETHEUS_PORT"
    exit 0
fi

echo "Starting Prometheus on port $PROMETHEUS_PORT..."

# Run the Prometheus API server
cd "${SCRIPT_DIR}" || { echo "Failed to change to Prometheus directory"; exit 1; }

# Run the fixed app
python -m prometheus.api.fixed_app &
PROMETHEUS_PID=$!
echo "Prometheus server started with PID: $PROMETHEUS_PID"

# Wait for the server to start
for i in {1..10}; do
    if nc -z localhost $PROMETHEUS_PORT 2>/dev/null; then
        echo "Prometheus is running at http://localhost:$PROMETHEUS_PORT"
        break
    fi
    echo -n "."
    sleep 1
done

if ! nc -z localhost $PROMETHEUS_PORT 2>/dev/null; then
    echo "Prometheus failed to start on port $PROMETHEUS_PORT"
    kill $PROMETHEUS_PID 2>/dev/null
    exit 1
fi

# Wait for process to finish
wait $PROMETHEUS_PID