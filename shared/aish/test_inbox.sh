#!/bin/bash
# Test inbox functionality

echo "Testing aish inbox operations..."
echo "================================"

# Start a new terminal in background to ensure we have latest code
echo "Starting test terminal..."
TEKTON_ROOT="/Users/cskoons/projects/github/Tekton"
cd "$TEKTON_ROOT/Terma"

# Launch a test terminal that will process commands
export TEKTON_NAME="InboxTest"
export TERMA_SESSION_ID="test-$$"
export TERMA_ENDPOINT="http://localhost:8004"

# Run aish-proxy in background
"$TEKTON_ROOT/shared/aish/aish-proxy" &
PROXY_PID=$!
sleep 2

# Function to run aish commands
run_aish() {
    "$TEKTON_ROOT/shared/aish/aish" "$@"
}

# Test 1: Send a message to self
echo -e "\nTest 1: Send message to self"
run_aish terma InboxTest "Test message 1"

# Test 2: Check inbox
echo -e "\nTest 2: Check inbox (should show message)"
run_aish terma inbox

# Test 3: Pop message
echo -e "\nTest 3: Pop message"
run_aish terma inbox new pop

# Test 4: Check inbox again (should be empty)
echo -e "\nTest 4: Check inbox after pop"
run_aish terma inbox

# Test 5: Keep push
echo -e "\nTest 5: Push to keep inbox"
run_aish terma inbox keep push "Important note"

# Test 6: Check keep inbox
echo -e "\nTest 6: Check keep inbox"
run_aish terma inbox keep

# Test 7: Keep write
echo -e "\nTest 7: Write to keep inbox"
run_aish terma inbox keep write "Another note"

# Test 8: Check both inboxes
echo -e "\nTest 8: Check both inboxes"
run_aish terma inbox

# Clean up
echo -e "\nCleaning up..."
kill $PROXY_PID 2>/dev/null
wait $PROXY_PID 2>/dev/null

echo -e "\nTest complete!"