#!/bin/bash
# Debug test for route parsing

export TEKTON_ROOT="/Users/cskoons/projects/github/Coder-C"
AISH="$TEKTON_ROOT/shared/aish/aish"

# Clean session
rm -f "$TEKTON_ROOT/.tekton/aish/.session_active"
rm -f "$TEKTON_ROOT/.tekton/aish/routes.json"

echo "=== Testing route parsing ==="
echo

echo "Test 1: Simple route"
$AISH route name simple numa apollo
echo

echo "Test 2: Route with single word purposes" 
$AISH route name single numa purpose analyze apollo purpose review tekton-core
echo

echo "Test 3: Route with multi-word purposes (the problem case)"
echo 'Command: $AISH route name multi numa purpose "code review" apollo purpose "risk assessment" tekton-core'
$AISH route name multi numa purpose "code review" apollo purpose "risk assessment" tekton-core
echo

echo "Test 4: Show the problematic route"
$AISH route show multi
echo

echo "Test 5: Check raw routes.json"
cat "$TEKTON_ROOT/.tekton/aish/routes.json" | python3 -m json.tool