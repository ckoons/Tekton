#!/bin/bash
# Test the CI message bus

echo "=== Testing CI Message Bus ==="

# Clean up any existing queues
rm -rf /tmp/ci_queues
mkdir -p /tmp/ci_queues

# Test 1: Create and list queues
echo -e "\nTest 1: Create and list queues"
./ci_message_bus create apollo
./ci_message_bus create rhetor
./ci_message_bus create claude-code
./ci_message_bus list

# Test 2: Send and receive messages in background
echo -e "\nTest 2: Send and receive messages"

# Start receiver in background
./ci_message_bus recv apollo 5000 > apollo_messages.txt &
RECEIVER_PID=$!
sleep 0.5

# Send messages
./ci_message_bus send apollo "Context update from rhetor" rhetor
./ci_message_bus send apollo "Code analysis complete" claude-code
./ci_message_bus send apollo "High priority alert" system

# Wait for receiver
wait $RECEIVER_PID

echo "Apollo received:"
cat apollo_messages.txt
rm apollo_messages.txt

# Test 3: Multiple receivers
echo -e "\nTest 3: Multiple CI communication"

# Start multiple receivers
./ci_message_bus recv rhetor 3000 > rhetor_messages.txt &
PID1=$!
./ci_message_bus recv claude-code 3000 > claude_messages.txt &
PID2=$!
sleep 0.5

# Send messages
./ci_message_bus send rhetor "Please synthesize context" apollo
./ci_message_bus send claude-code "New code request" user
./ci_message_bus send rhetor "Analysis complete" claude-code

# Wait
wait $PID1 $PID2

echo -e "\nRhetor received:"
cat rhetor_messages.txt
echo -e "\nClaude-code received:"
cat claude_messages.txt

# Cleanup
rm rhetor_messages.txt claude_messages.txt
./ci_message_bus destroy apollo
./ci_message_bus destroy rhetor
./ci_message_bus destroy claude-code

echo -e "\n=== Message bus tests completed ==="