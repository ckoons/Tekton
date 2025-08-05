#!/bin/bash
# Test CI messaging with a simple echo script

cat > /tmp/test_ci.sh << 'EOF'
#!/bin/bash
# Simulate a CI that uses @ commands

echo "Hello, I'm a test CI!"
echo ""
echo "Let me send a message to another CI:"
echo '@send numa@Casey "Hi from the test CI! Can you help with a task?"'
echo ""
echo "Now let me ask a question:"
echo '@ask claude@Beth "What do you think about the new messaging system?"'
echo ""
echo "Let me check my status:"
echo "@status"
echo ""
echo "Here's some code that shouldn't trigger parsing:"
echo '```python'
echo '# This @send command is in a code block'
echo 'def send_message():'
echo '    return "@send target message"'
echo '```'
echo ""
echo "Back to normal text. Waiting for input..."
read -p "Type something: " input
echo "You typed: $input"
EOF

chmod +x /tmp/test_ci.sh

# Launch the test CI with messaging
./shared/ci_tools/ci-tool --name TestUser --ci test-script /tmp/test_ci.sh