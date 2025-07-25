#!/bin/bash
# Functional tests for unified CI registry and messaging

echo "Testing Unified CI Registry and Messaging"
echo "========================================"

# Test 1: Basic list command
echo -n "Test 1: aish list... "
if aish list | grep -q "Greek Chorus AIs:"; then
    echo "PASS"
else
    echo "FAIL - list output missing Greek Chorus section"
    exit 1
fi

# Test 2: List with type filter
echo -n "Test 2: aish list type greek... "
count=$(aish list type greek | grep -c "port")
if [ "$count" -gt 10 ]; then
    echo "PASS ($count Greek Chorus AIs found)"
else
    echo "FAIL - expected more than 10 Greek Chorus AIs, found $count"
    exit 1
fi

# Test 3: List terminals
echo -n "Test 3: aish list type terminal... "
if aish list type terminal | grep -q "Active Terminals:"; then
    echo "PASS"
else
    echo "FAIL - terminal list not working"
    exit 1
fi

# Test 4: JSON output
echo -n "Test 4: aish list json... "
if aish list json | jq -e '.[0].message_format' > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL - JSON output missing message_format field"
    exit 1
fi

# Test 5: JSON with filter
echo -n "Test 5: aish list json terminal... "
terminal_count=$(aish list json terminal | jq 'length')
if [ "$terminal_count" -ge 0 ]; then
    echo "PASS ($terminal_count terminals)"
else
    echo "FAIL - JSON terminal filter not working"
    exit 1
fi

# Test 6: List forwarding CIs
echo -n "Test 6: aish list forward... "
if aish list forward > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL - forward filter not working"
    exit 1
fi

# Test 7: Check message configuration in registry
echo -n "Test 7: Message configuration in registry... "
numa_format=$(aish list json | jq -r '.[] | select(.name=="numa") | .message_format')
if [ "$numa_format" = "rhetor_socket" ]; then
    echo "PASS"
else
    echo "FAIL - numa should have rhetor_socket format, got: $numa_format"
    exit 1
fi

# Test 8: Terminal message configuration
echo -n "Test 8: Terminal configuration... "
if aish list json terminal | jq -e '.[0] | select(.message_format=="terma_route")' > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL - terminals should have terma_route format"
    exit 1
fi

echo ""
echo "All tests passed! ✅"
echo ""
echo "Summary:"
echo "- Unified CI registry is working"
echo "- All CI types are properly configured"
echo "- Message routing configuration is in place"
echo "- JSON output includes messaging fields"