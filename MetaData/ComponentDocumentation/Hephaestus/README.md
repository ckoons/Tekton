# Hephaestus

![Hephaestus](../../../images/icon.jpg)

Hephaestus is the unified user interface component for the Tekton ecosystem, providing a seamless web-based dashboard for interacting with all Tekton components.

## Overview

Hephaestus serves as the central user interface for the Tekton ecosystem, offering a modern web-based dashboard that integrates all Tekton components into a cohesive user experience. Built with simplicity and maintainability in mind, Hephaestus uses vanilla web technologies (HTML, CSS, JavaScript) to create a responsive, intuitive interface without the complexity of modern frontend frameworks.

## Key Features

- **Unified Dashboard**: Centralized interface for all Tekton components
- **Component Integration**: Standardized pattern for component UI integration
- **Multi-Mode Interface**: Support for both terminal and graphical interfaces
- **Real-Time Communication**: WebSocket-based communication with backend services
- **Theme Support**: Light and dark theme options
- **State Management**: Client-side state management for user preferences and context
- **Shadow DOM Isolation**: Component isolation using Shadow DOM
- **Single Port Architecture**: Follows the Tekton Single Port Architecture pattern

## Architecture

Hephaestus implements a component-based architecture with these key elements:

1. **Core UI Framework**:
   - Vanilla JavaScript without external dependencies
   - Component loading and management system
   - Event-based communication between components
   - Shared utilities for common UI operations

2. **Component Integration System**:
   - Standard pattern for integrating component UIs
   - Shadow DOM for style and script isolation
   - Component registration and discovery
   - Component lifecycle management

3. **Communication Layer**:
   - WebSocket-based real-time communication
   - HTTP REST API integration
   - Standardized message formats
   - Connection management and recovery

4. **State Management**:
   - Client-side state persistence
   - Component-specific state isolation
   - Shared global state for cross-component coordination
   - State synchronization between components

5. **UI Subsystems**:
   - Terminal integration with Terma
   - Theme management
   - Navigation system
   - Notification system
   - Modal and dialog system

## Component Integration

Hephaestus provides a standardized pattern for integrating component UIs:

1. **HTML Templates**: Component markup in isolated templates
2. **Shadow DOM**: Style and script isolation using Shadow DOM
3. **Component Registration**: Declarative component registration
4. **State Binding**: Two-way binding between UI and component state
5. **Event System**: Event-based communication between components
6. **WebSocket Integration**: Standard WebSocket connection management

Component UIs are structured as:
```
ui/
  components/
    component-name.html    # Component template
  styles/
    component-name.css     # Component styles
  scripts/
    component-name.js      # Component functionality
    component-name-state.js # Component state management
```

## Installation

Hephaestus is installed as part of the Tekton ecosystem:

```bash
# Clone the repository (if not already done)
git clone https://github.com/yourusername/Tekton.git
cd Tekton

# Run the setup script
cd Hephaestus
./setup.sh

# Start Hephaestus using the unified launcher
cd ..
./scripts/tekton-launch --components hephaestus
```

## Quick Start

```bash
# Start Hephaestus on port 8080
HEPHAESTUS_PORT=8080 ./scripts/tekton-launch --components hephaestus

# Access the UI in your browser
# http://localhost:8080
```

## Integration with Tekton Components

Hephaestus integrates with all Tekton components:

- **Ergon**: Task and agent management UI
- **Athena**: Knowledge graph visualization and interaction
- **Terma**: Terminal integration and command execution
- **Engram**: Memory visualization and management
- **Synthesis**: Workflow execution and monitoring
- **Prometheus**: Planning and project management
- **Sophia**: Intelligence measurement and visualization
- **Telos**: Requirements management and tracing
- **Rhetor**: Prompt engineering and template management

## Adding New Component UIs

To add a new component UI to Hephaestus:

1. Create a component template in `ui/components/your-component.html`
2. Add component-specific styles in `ui/styles/your-component.css`
3. Implement component functionality in `ui/scripts/your-component.js`
4. Add component state management in `ui/scripts/your-component-state.js`
5. Register the component in `server/component_registry.json`

Example component template:
```html
<div class="your-component">
  <div class="your-component__header">
    <h2>Your Component</h2>
  </div>
  <div class="your-component__content">
    <!-- Component content here -->
  </div>
</div>
```

## CSS Naming Convention

Hephaestus uses the BEM (Block, Element, Modifier) naming convention for CSS:

```css
/* Block */
.your-component { }

/* Element */
.your-component__header { }
.your-component__content { }

/* Modifier */
.your-component--active { }
.your-component__header--collapsed { }
```

## WebSocket Communication

Hephaestus uses WebSockets for real-time communication with backend services:

```javascript
// Connect to WebSocket service
const wsUrl = `ws://${window.location.hostname}:8006/ws`;
const socket = new WebSocket(wsUrl);

// Send message
socket.send(JSON.stringify({
  type: 'request',
  action: 'fetch_data',
  payload: { /* request data */ }
}));

// Receive message
socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  // Handle message
};
```

## Documentation

For more detailed documentation, see:
- [UI_STYLING_GUIDE.md](./UI_STYLING_GUIDE.md) - Styling guidelines and best practices
- [COMPONENT_PATTERNS.md](./COMPONENT_PATTERNS.md) - Component implementation patterns
- [STATE_MANAGEMENT_PATTERNS.md](./STATE_MANAGEMENT_PATTERNS.md) - State management guidelines
- [DEVELOPMENT_STATUS.md](./DEVELOPMENT_STATUS.md) - Current implementation status
- [COMPONENT_ISOLATION_STRATEGY.md](./COMPONENT_ISOLATION_STRATEGY.md) - Component isolation using Shadow DOM