#!/bin/bash
# Start Tekton Shared Services

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEKTON_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source environment
source "$TEKTON_ROOT/shared/utils/setup_env.sh"
setup_tekton_env "$SCRIPT_DIR" "$TEKTON_ROOT"

# Default values
ORPHAN_INTERVAL=${ORPHAN_INTERVAL:-6.0}  # hours
ORPHAN_MIN_AGE=${ORPHAN_MIN_AGE:-2.0}   # hours
DRY_RUN=${DRY_RUN:-false}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --orphan-interval)
            ORPHAN_INTERVAL="$2"
            shift 2
            ;;
        --orphan-min-age)
            ORPHAN_MIN_AGE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --orphan-interval HOURS  Hours between orphan cleanup (default: 6.0)"
            echo "  --orphan-min-age HOURS   Min age for orphan detection (default: 2.0)"
            echo "  --dry-run               Run in dry-run mode"
            echo "  --help                  Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Starting Tekton Shared Services..."
echo "Orphan cleanup interval: ${ORPHAN_INTERVAL} hours"
echo "Orphan minimum age: ${ORPHAN_MIN_AGE} hours"
echo "Dry run: ${DRY_RUN}"

# Build command
CMD="python3 $SCRIPT_DIR/run_shared_services.py"
CMD="$CMD --orphan-interval $ORPHAN_INTERVAL"
CMD="$CMD --orphan-min-age $ORPHAN_MIN_AGE"

if [ "$DRY_RUN" = true ]; then
    CMD="$CMD --dry-run"
fi

# Run the service
exec $CMD