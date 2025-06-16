#!/bin/bash
#
# Hephaestus UI Launcher Script
# 
# This script launches the Hephaestus UI server with the correct configuration
# for the Tekton orchestration system.
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set default port from environment variable or use 8080
PORT="${HEPHAESTUS_PORT:-8080}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Launch the Hephaestus UI server"
      echo ""
      echo "Options:"
      echo "  --port PORT      Server port (default: ${PORT})"
      echo "  --help, -h       Show this help message"
      echo ""
      echo "Environment variables:"
      echo "  HEPHAESTUS_PORT  Default server port"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Change to the Hephaestus directory
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is not available"
    exit 1
fi

# Check if the server script exists
if [ ! -f "ui/server/server.py" ]; then
    echo "Error: Hephaestus server script not found at ui/server/server.py"
    exit 1
fi

# Launch the server
echo "Starting Hephaestus UI on port $PORT..."
echo "Access the UI at: http://localhost:$PORT"
echo "Press Ctrl+C to stop the server"
echo ""

# Execute the server with the specified port
exec python3 ui/server/server.py --port "$PORT"