#!/bin/bash
# Manual test for delimiter functionality

echo "Manual Delimiter Test"
echo "===================="
echo ""
echo "This script will test the delimiter functionality with your CI terminal."
echo ""

# Test 1: Launch a Python CI
echo "1. Launching Python interpreter as 'test-delim-py'..."
python shared/aish/aish ci-tool -n test-delim-py -d '\n' -- python -u -c "
import sys
print('Python ready')
sys.stdout.flush()
while True:
    try:
        line = input()
        if line.strip():
            try:
                exec(line)
                sys.stdout.flush()
            except Exception as e:
                print(f'Error: {e}')
                sys.stdout.flush()
    except EOFError:
        break
" &

PYTHON_PID=$!
sleep 2

# Test 2: Send commands with different delimiters
echo ""
echo "2. Testing different delimiters:"
echo ""

echo "  a) Testing newline delimiter (\\n):"
echo "     Command: aish test-delim-py \"print('Hello with newline')\" -x '\\n'"
python shared/aish/aish test-delim-py "print('Hello with newline')" -x '\n'
sleep 1

echo ""
echo "  b) Testing CRLF delimiter (\\r\\n):"
echo "     Command: aish test-delim-py \"print('Hello with CRLF')\" -x '\\r\\n'"
python shared/aish/aish test-delim-py "print('Hello with CRLF')" -x '\r\n'
sleep 1

echo ""
echo "  c) Testing tab delimiter (\\t):"
echo "     Command: aish test-delim-py \"print('Hello with tab')\" -x '\\t'"
python shared/aish/aish test-delim-py "print('Hello with tab')" -x '\t'
sleep 1

echo ""
echo "  d) Testing without execute flag (should show message format):"
echo "     Command: aish test-delim-py \"print('No execute')\""
python shared/aish/aish test-delim-py "print('No execute')"
sleep 1

# Cleanup
echo ""
echo "3. Cleanup..."
kill $PYTHON_PID 2>/dev/null
rm -f /tmp/ci_msg_test-delim-py.sock

echo "Test complete!"
echo ""
echo "You should have seen:"
echo "  - 'Hello with newline' printed when using -x '\\n'"
echo "  - 'Hello with CRLF' printed when using -x '\\r\\n'"  
echo "  - 'Hello with tab' NOT printed (tab doesn't trigger Python execution)"
echo "  - A formatted message for the last test without -x flag"