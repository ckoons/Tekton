#!/bin/bash
# Test the updated CI wrapper to verify fixes

echo "=== Testing CI Wrapper Fixes ==="
echo "This test will:"
echo "1. Launch a simple test program that accepts input"
echo "2. Test @ command suppression"
echo "3. Test # substitution in injected text"
echo "4. Test message queue injection timing"
echo ""

# Create a simple interactive test program
cat > /tmp/test_interactive.sh << 'EOF'
#!/bin/bash
echo "Test program started. Type commands or 'quit' to exit."
while true; do
    read -p "> " input
    if [ "$input" = "quit" ]; then
        break
    fi
    echo "You typed: $input"
    sleep 0.1  # Simulate processing time
done
echo "Test program ended."
EOF

chmod +x /tmp/test_interactive.sh

# Create a test input script
cat > /tmp/test_input.sh << 'EOF'
#!/bin/bash
# This simulates user input to the wrapped program

sleep 1
echo "Testing @ command suppression"
echo "@status"  # This should be suppressed from output
sleep 2
echo "Testing normal input"
echo "hello world"  # This should appear normally
sleep 2
echo "quit"
EOF

chmod +x /tmp/test_input.sh

echo "Starting wrapped test program..."
echo "Watch for:"
echo "- @status command should NOT appear in output"
echo "- Status message should appear with # instead of @"
echo "- Messages should inject when input is idle"
echo ""

# Run the test
cd /Users/cskoons/projects/github/Coder-C
/tmp/test_input.sh | ./shared/ci_tools/ci-tool --name TestWrapper --ci test-model -- /tmp/test_interactive.sh

echo ""
echo "Test completed."