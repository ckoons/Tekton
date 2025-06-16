#!/bin/bash
# Test script for Budget component integration

# Check if required files exist
echo "Checking Budget component files..."

FILES=(
    "budget-component.html"
    "scripts/budget-api-client.js"
    "scripts/budget-chart-utils.js"
    "scripts/budget-cli-handler.js"
    "scripts/budget-component.js"
    "scripts/budget-models.js"
    "scripts/budget-state-manager.js"
    "scripts/budget-ws-handler.js"
)

for file in "${FILES[@]}"; do
    if [[ -f $(dirname "$0")/$file ]]; then
        echo "✓ Found: $file"
    else
        echo "✗ Missing: $file"
    fi
done

# Check for Chart.js dependency
echo ""
echo "Checking for Chart.js dependency..."
if [[ -f $(dirname "$0")/../../scripts/chart.js ]]; then
    echo "✓ Found: Chart.js"
else
    echo "✗ Missing: Chart.js (You'll need to include Chart.js in the Hephaestus UI)"
    echo "  Consider adding: <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script> to the main index.html"
fi

# Check Budget component HTML integration
echo ""
echo "Checking component integration..."
COMPONENT_LOADER=$(grep -l "budget-component.html" $(dirname "$0")/../../index.html || echo "")
if [[ -n "$COMPONENT_LOADER" ]]; then
    echo "✓ Budget component referenced in index.html"
else
    echo "✗ Budget component not referenced in index.html"
    echo "  To integrate, add this line to index.html in the components section:"
    echo "  <div id=\"budget-panel\" class=\"component-panel\"></div>"
    echo "  And load the component with:"
    echo "  document.getElementById('budget-panel').innerHTML = await fetch('components/budget/budget-component.html').then(r => r.text());"
fi

# Check for port configuration
echo ""
echo "Checking environment configuration..."
ENV_CONFIG=$(grep -l "BUDGET_PORT" $(dirname "$0")/../../scripts/env.js || echo "")
if [[ -n "$ENV_CONFIG" ]]; then
    echo "✓ BUDGET_PORT found in env.js"
else
    echo "✗ BUDGET_PORT not found in env.js"
    echo "  Add this line to env.js:"
    echo "  window.BUDGET_PORT = 8013;  // Default Budget port"
fi

echo ""
echo "Test complete. Address any issues before deploying."