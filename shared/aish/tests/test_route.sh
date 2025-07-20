#!/bin/bash
# Test suite for aish route command
# Tests route creation, listing, deletion, and message routing

# Don't exit on error - we want to test error cases

# Setup
export TEKTON_ROOT="/Users/cskoons/projects/github/Coder-C"
AISH="$TEKTON_ROOT/shared/aish/aish"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Clean session marker to start fresh
rm -f "$TEKTON_ROOT/.tekton/aish/.session_active"

# Test function
test_case() {
    local test_name="$1"
    local command="$2"
    local expected="$3"
    local check_type="${4:-contains}"  # contains, exact, json_field
    
    echo -n "Testing: $test_name ... "
    
    # Run command and capture output
    if output=$($command 2>&1); then
        case "$check_type" in
            "contains")
                if [[ "$output" == *"$expected"* ]]; then
                    echo -e "${GREEN}PASS${NC}"
                    ((PASSED++))
                else
                    echo -e "${RED}FAIL${NC}"
                    echo "  Expected to contain: $expected"
                    echo "  Got: $output"
                    ((FAILED++))
                fi
                ;;
            "exact")
                if [[ "$output" == "$expected" ]]; then
                    echo -e "${GREEN}PASS${NC}"
                    ((PASSED++))
                else
                    echo -e "${RED}FAIL${NC}"
                    echo "  Expected: $expected"
                    echo "  Got: $output"
                    ((FAILED++))
                fi
                ;;
            "json_field")
                # Extract JSON field using grep/sed
                field_name="${expected%%:*}"
                field_value="${expected#*:}"
                if echo "$output" | grep -q "\"$field_name\": \"$field_value\""; then
                    echo -e "${GREEN}PASS${NC}"
                    ((PASSED++))
                else
                    echo -e "${RED}FAIL${NC}"
                    echo "  Expected field: $field_name = $field_value"
                    echo "  Got: $output"
                    ((FAILED++))
                fi
                ;;
        esac
    else
        echo -e "${RED}FAIL${NC} (command failed)"
        echo "  Error: $output"
        ((FAILED++))
    fi
}

# Test error on failure
test_error() {
    local test_name="$1"
    local command="$2"
    
    echo -n "Testing: $test_name ... "
    
    if $command 2>&1 >/dev/null; then
        echo -e "${RED}FAIL${NC} (expected error but succeeded)"
        ((FAILED++))
    else
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
    fi
}

echo "=== AISH ROUTE TEST SUITE ==="
echo

# Test 1: Empty route list
test_case "Empty route list" \
    "$AISH route list" \
    "No routes defined"

# Test 2: Create simple route
test_case "Create simple route" \
    "$AISH route name test numa tekton-core" \
    "Route 'test' created: numa → tekton-core"

# Test 3: List routes after creation
test_case "List shows created route" \
    "$AISH route list" \
    "test: numa → tekton-core"

# Test 4: Create route with purposes
test_case "Create route with purposes" \
    "$AISH route name analysis numa purpose \"code review\" apollo purpose \"risk assessment\" tekton-core" \
    "Route 'analysis' created: numa → apollo → tekton-core"

# Test 5: Show route details
test_case "Show route with purposes" \
    "$AISH route show analysis" \
    "Purpose: \"code review\""

# Test 6: Route default message
output=$($AISH route tekton-core "Test message" 2>&1)
test_case "Route message outputs JSON" \
    "echo '$output' | grep -o '\"message\": \"Test message\"'" \
    "\"message\": \"Test message\""

# Test 7: Route through named route
output=$($AISH route name test tekton-core "Test via route" 2>&1)
test_case "Named route adds metadata" \
    "echo '$output' | grep -o '\"route_name\": \"test\"'" \
    "\"route_name\": \"test\""

# Test 8: Test route progression with annotations
json_with_annotation='{
  "message": "Test progression",
  "annotations": [{"author": "numa", "content": "Initial analysis"}]
}'
output=$($AISH route name analysis tekton-core "$json_with_annotation" 2>&1)
test_case "Route progression moves to next hop" \
    "echo '$output' | grep -o '\"next_hop\": \"apollo\"'" \
    "\"next_hop\": \"apollo\""

# Test 9: Remove specific route
test_case "Remove route by name" \
    "$AISH route remove test" \
    "Route 'test' removed"

# Test 10: Verify route was removed
test_case "Removed route not in list" \
    "$AISH route list" \
    "analysis: numa"

# Test 11: Create project route
test_case "Create route with project hop" \
    "$AISH route name deploy prometheus project servers terma" \
    "Route 'deploy' created: prometheus → project:servers → terma"

# Test 12: Invalid JSON handling
test_error "Invalid JSON rejected" \
    "$AISH route tekton-core '{bad json'"

# Test 13: Route to non-existent named route
output=$($AISH route name nonexistent tekton-core "message" 2>&1)
test_case "Non-existent route error" \
    "echo '$output'" \
    "No route named 'nonexistent' to tekton-core"

# Test 14: List routes to specific destination
test_case "List routes filtered by destination" \
    "$AISH route list tekton-core" \
    "analysis:"

# Test 15: Remove all routes with name
$AISH route name dup1 numa dest1 >/dev/null 2>&1
$AISH route name dup1 apollo dest2 >/dev/null 2>&1
test_case "Remove all routes with same name" \
    "$AISH route remove dup1" \
    "Route 'dup1' removed"

# Summary
echo
echo "=== TEST SUMMARY ==="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi