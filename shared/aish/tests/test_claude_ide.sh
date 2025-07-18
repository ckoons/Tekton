#!/bin/bash
# Test script for Claude Code IDE functionality

echo "=== Claude Code IDE Test Suite ==="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track results
PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local command="$2"
    local expected="$3"
    
    echo -n "Testing $test_name... "
    
    output=$(eval "$command" 2>&1)
    
    if echo "$output" | grep -q "$expected"; then
        echo -e "${GREEN}PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}FAILED${NC}"
        echo "  Expected: $expected"
        echo "  Got: $output" | head -5
        ((FAILED++))
    fi
}

# Change to project root
cd "$(dirname "$0")/../../.." || exit 1

echo "1. Testing introspect command"
run_test "introspect AIShell" \
    "python shared/aish/aish introspect AIShell" \
    "broadcast_message"

run_test "introspect MessageHandler" \
    "python shared/aish/aish introspect MessageHandler" \
    "send(ai_name: str, message: str)"

run_test "introspect non-existent class" \
    "python shared/aish/aish introspect NonExistentClass" \
    "not found"

run_test "introspect help" \
    "python shared/aish/aish introspect --help" \
    "Usage: aish introspect"

echo
echo "2. Testing explain command"
run_test "explain AttributeError" \
    "python shared/aish/aish explain 'AttributeError: AIShell object has no attribute broadcast'" \
    "Did you mean"

run_test "explain with suggestions" \
    "python shared/aish/aish explain 'AttributeError: MessageHandler object has no attribute send_message'" \
    "aish introspect"

echo
echo "3. Testing context command"
# Create test file
cat > /tmp/test_context_ide.py << 'EOF'
from src.core.shell import AIShell
from src.message_handler import MessageHandler

class MyClass:
    def my_method(self):
        pass

def my_function():
    pass
EOF

run_test "context with file" \
    "python shared/aish/aish context /tmp/test_context_ide.py" \
    "AIShell"

run_test "context shows local classes" \
    "python shared/aish/aish context /tmp/test_context_ide.py" \
    "MyClass"

run_test "context shows functions" \
    "python shared/aish/aish context /tmp/test_context_ide.py" \
    "my_function"

# Cleanup
rm -f /tmp/test_context_ide.py

echo
echo "4. Testing list commands"
run_test "list commands shows IDE section" \
    "python shared/aish/aish list commands | grep -A3 'CLAUDE CODE IDE'" \
    "introspect"

echo
echo "5. Running Python unit tests"
python -m pytest shared/aish/tests/test_claude_ide.py -v

echo
echo "=== Test Summary ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi