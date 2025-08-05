#!/bin/bash
# Test the new aish-based CI messaging

echo "=== Testing aish CI Messaging ==="
echo ""
echo "This test will:"
echo "1. Launch a test CI wrapper"
echo "2. Test aish command interception"
echo "3. Verify messages are routed correctly"
echo "4. Confirm responses appear via stdin"
echo ""

# Create a simple test program that echoes input
cat > /tmp/test_echo_ci.sh << 'EOF'
#!/bin/bash
echo "Test CI started. Type 'quit' to exit."
echo "You can use: aish <ci-name> \"message\" to send messages"
echo ""

while true; do
    read -p "> " input
    if [ "$input" = "quit" ]; then
        break
    fi
    echo "Echo: $input"
done

echo "Test CI ended."
EOF

chmod +x /tmp/test_echo_ci.sh

# Create test input that includes aish commands
cat > /tmp/test_aish_input.sh << 'EOF'
#!/bin/bash
sleep 2
echo "Test 1: Regular command (should pass through)"
echo "hello world"
sleep 2

echo "Test 2: Regular aish command (should pass through)"
echo "aish list"
sleep 2

echo "Test 3: CI messaging (should be intercepted)"
echo 'aish TestEcho-ci "This is a test message"'
sleep 2

echo "Test 4: Unknown CI (should show error via stdin)"
echo 'aish UnknownCI "This should fail"'
sleep 2

echo "quit"
EOF

chmod +x /tmp/test_aish_input.sh

echo "Starting test CI wrapper..."
echo "Watch for:"
echo "- Regular commands pass through normally"
echo "- aish list passes through"
echo "- aish TestEcho-ci message is intercepted"
echo "- Error messages appear via stdin"
echo ""

# First, clean up any existing test CI
pkill -f "test_echo_ci.sh" 2>/dev/null
rm -f /tmp/ci_msg_TestEcho-ci.sock 2>/dev/null

# Launch the test CI
echo "Launching: aish ci-tool --name TestEcho-ci -- /tmp/test_echo_ci.sh"
/tmp/test_aish_input.sh | aish ci-tool --name TestEcho-ci -- /tmp/test_echo_ci.sh

echo ""
echo "Test completed."
echo ""
echo "To test real CI-to-CI messaging:"
echo "1. Terminal 1: aish ci-tool --name Casey-ci -- claude"
echo "2. Terminal 2: aish ci-tool --name Betty-ci -- claude"
echo "3. In Casey's terminal: aish Betty-ci \"Hi Betty!\""
echo "4. Betty should see: [timestamp] Message from Casey-ci: Hi Betty!"