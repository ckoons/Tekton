#!/bin/bash
# Quick test suite for aish functionality

echo "Testing aish command syntax..."
echo "=============================="

# Test 1: Direct message
echo -n "Test 1 - Direct message: "
if ./aish numa "test message" 2>&1 | grep -q "Specialist Orchestrator"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

# Test 2: Piped input
echo -n "Test 2 - Piped input: "
if echo "test message" | ./aish numa 2>&1 | grep -q "Specialist Orchestrator"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

# Test 3: Multi-word message (checking syntax, not response)
echo -n "Test 3 - Multi-word message syntax: "
if ! ./aish apollo "what is static analysis" 2>&1 | grep -q "No message provided"; then
    echo "✓ PASS (syntax accepted)"
else
    echo "✗ FAIL"
fi

# Test 4: Team chat (checking syntax, not response)
echo -n "Test 4 - Team chat syntax: "
if ! ./aish team-chat "hello team" 2>&1 | grep -q "No message provided"; then
    echo "✓ PASS (syntax accepted)"
else
    echo "✗ FAIL"
fi

# Test 5: Terma messaging
echo -n "Test 5 - Terma list: "
if ./aish terma list 2>&1 | grep -q "Active Terminals"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

# Test 6: Help command
echo -n "Test 6 - Help command: "
if ./aish help 2>&1 | grep -q "AI Training"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

echo "=============================="
echo "Testing complete!"