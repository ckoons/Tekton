#!/bin/bash
# Launch any CI tool with messaging support

# Default values
CI_NAME=""
USER_NAME=""
WORKING_DIR="$PWD"
COMMAND=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ci)
            CI_NAME="$2"
            shift 2
            ;;
        --name)
            USER_NAME="$2"
            shift 2
            ;;
        --dir)
            WORKING_DIR="$2"
            shift 2
            ;;
        --)
            shift
            COMMAND="$@"
            break
            ;;
        *)
            echo "Usage: $0 --ci CI_NAME --name USER_NAME [--dir DIR] -- command [args...]"
            echo ""
            echo "Examples:"
            echo "  $0 --ci claude --name Casey -- claude"
            echo "  $0 --ci numa --name Beth --dir /path/to/project -- python -m numa"
            echo ""
            echo "This wrapper adds @ command messaging to any CI tool:"
            echo "  @send target \"message\" - Send a message"
            echo "  @ask target \"question\" - Ask a question"
            echo "  @reply target \"answer\" - Reply to a message"
            echo "  @status - Check message status"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$CI_NAME" ] || [ -z "$USER_NAME" ] || [ -z "$COMMAND" ]; then
    echo "Error: --ci, --name, and command are required"
    exit 1
fi

# Set up environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/..:$PYTHONPATH"

# Launch with wrapper
echo "Launching $CI_NAME for $USER_NAME with messaging support..."
python3 "${SCRIPT_DIR}/ci_message_wrapper.py" \
    --name "$USER_NAME" \
    --ci "$CI_NAME" \
    --dir "$WORKING_DIR" \
    $COMMAND