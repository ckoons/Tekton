#!/bin/bash
# Test script for CI tool launcher

echo "=== Testing CI Tool Launcher ==="

# Test 1: Basic launch with echo
echo -e "\nTest 1: Basic launch with echo"
echo "hello world" | ./ci_tool_launcher --tool test-echo --executable /bin/echo --args "CI Tool says:"
if [ $? -eq 0 ]; then
    echo "✓ Test 1 passed"
else
    echo "✗ Test 1 failed"
fi

# Test 2: Python script test
echo -e "\nTest 2: Python script that reads stdin"
cat > test_script.py << 'EOF'
#!/usr/bin/env python3
import sys
print("Python tool started")
for line in sys.stdin:
    print(f"Received: {line.strip()}")
    if line.strip() == "quit":
        break
print("Python tool exiting")
EOF
chmod +x test_script.py

echo -e "test\nquit" | ./ci_tool_launcher --tool test-python --executable /usr/bin/env --args python3 test_script.py
if [ $? -eq 0 ]; then
    echo "✓ Test 2 passed"
else
    echo "✗ Test 2 failed"
fi

# Test 3: Long-running process with signal handling
echo -e "\nTest 3: Signal handling test"
cat > test_signal.py << 'EOF'
#!/usr/bin/env python3
import signal
import time
import sys

def signal_handler(sig, frame):
    print("Received signal, exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
print("Signal test started")
sys.stdout.flush()

# Sleep for a bit
time.sleep(2)
print("Should not see this")
EOF
chmod +x test_signal.py

# Launch in background
./ci_tool_launcher --tool test-signal --executable /usr/bin/env --args python3 test_signal.py &
LAUNCHER_PID=$!
sleep 0.5

# Send signal to launcher
kill -TERM $LAUNCHER_PID
wait $LAUNCHER_PID
if [ $? -eq 0 ]; then
    echo "✓ Test 3 passed"
else
    echo "✗ Test 3 failed"
fi

# Cleanup
rm -f test_script.py test_signal.py

echo -e "\n=== All tests completed ==="