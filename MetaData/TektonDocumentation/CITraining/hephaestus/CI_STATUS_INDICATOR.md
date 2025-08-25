# CI Status Indicator - Companion Intelligence Connection Status

## Overview

The CI (Companion Intelligence) status indicator provides visual feedback about the connection status between UI components and their associated AI specialists. This follows Casey's preference for the term "CI" for companion intelligences.

## Visual Design

### Header Status Indicator

Located in the component header (top-right), the CI status indicator consists of:
- **Status Dot**: A circular indicator that changes color and effect based on connection state
- **Status Text**: "CI Connected" or "CI Disconnected"

### Connection States

1. **Connected** (Active)
   - Dot: Green (#28a745) with luminous glow effect
   - Glow: Pulsing animation with multiple shadow layers
   - Text: "CI Connected" in normal color
   - Used when: Health check to component backend succeeds

2. **Disconnected** (Error/Inactive)
   - Dot: Gray (#666) with reduced opacity (0.5)
   - Glow: None
   - Text: "CI Disconnected" in gray (#666) with reduced opacity
   - Used when: Health check fails or CI is not running

3. **Connecting** (Initial State)
   - Dot: Yellow/warning color (#ffc107)
   - Glow: None
   - Text: "CI Connecting..." 
   - Used when: Component first loads

## Implementation Details

### CSS Classes

```css
.noesis__status-indicator[data-status="active"] {
  background-color: #28a745;
  box-shadow: 0 0 8px #28a745, 
              0 0 12px #28a745,
              0 0 16px rgba(40, 167, 69, 0.6);
  animation: pulse-glow 2s infinite;
}

.noesis__status-indicator[data-status="inactive"],
.noesis__status-indicator[data-status="error"] {
  background-color: #666;
  opacity: 0.5;
}
```

### Health Check

The component checks CI availability on load:
```javascript
fetch('http://localhost:8015/health')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'healthy') {
            // Set to connected state
        }
    })
    .catch(error => {
        // Set to disconnected state
    });
```

## Consistency with Navigation

This header indicator matches the behavior of the left navigation panel dots:
- Both use luminous glow when connected
- Both dim when disconnected
- Provides consistent visual language across the UI

## Benefits

1. **Clear Status**: Users immediately know if the CI is available
2. **Visual Consistency**: Matches navigation panel indicators
3. **Accessibility**: Both color and text indicate status
4. **Smooth Transitions**: CSS transitions make state changes pleasant

## Usage in Other Components

To implement in other Tekton components:

1. Add the status indicator HTML:
```html
<div class="component__connection-status">
    <span class="component__status-indicator" data-status="inactive"></span>
    <span class="component__status-text">CI Connecting...</span>
</div>
```

2. Include the CSS styles (adjust colors as needed)

3. Add health check on component initialization

4. Update status based on backend availability

---

*Created by Jill on July 5, 2025 during the Noesis sprint with Casey*