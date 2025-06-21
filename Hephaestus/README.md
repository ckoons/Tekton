# Hephaestus Documentation

## Overview

This documentation provides comprehensive information about the Hephaestus UI component of the Tekton AI orchestration system. Hephaestus serves as the unified user interface for interacting with all Tekton components through a combination of terminal and graphical interfaces.

## Documentation Structure

### Core Documentation

- **[UI Architecture Guide](./ui/README.md)** - Main UI architecture reference
- **[Technical Documentation](./technical_documentation.md)** - System design and components
- **[Developer Guide](./developer_guide.md)** - Creating and extending components
- **[Architecture Overview](./architecture.md)** - Visual diagrams and system flow

### Development Guides

- **[UI DevTools Comprehensive Guide](./docs/UI_DEVTOOLS_COMPREHENSIVE_GUIDE.md)** - Complete guide to UI DevTools
- **[Instrumentation Guide](./docs/INSTRUMENTATION_GUIDE.md)** - Semantic tagging system and patterns
- **[Loading State System](./docs/LOADING_STATE_INSTRUMENTATION.md)** - Component loading detection
- **[Debug Instrumentation](./ui/server/README_DEBUG.md)** - Python debug system

### Reference Documents

- **[Component Index](./docs/INSTRUMENTATION_INDEX.md)** - Quick component reference
- **[Testing Guide](./tests/README.md)** - Test suite documentation
- **[API Reference](./docs/api_reference.md)** - Component APIs

### Historical Documentation

Archived documentation from previous sprints and migrations can be found in `./docs/archive/`

## Key Features

1. **Shadow DOM Isolation**: Components are loaded in isolated Shadow DOM contexts to prevent style bleeding and DOM conflicts.

2. **Component-Based Design**: Each Tekton subsystem has a dedicated UI component with its own HTML, CSS, and JavaScript.

3. **Theme System**: Consistent theming across components using CSS variables propagated through Shadow DOM boundaries.

4. **Utilities Library**: Common UI patterns implemented as reusable utilities for notifications, dialogs, tabs, and more.

5. **Service Integration**: Standardized patterns for integrating with Tekton services like LLM Adapter, Hermes message bus, and Engram memory system.

6. **Loading State System**: Semantic HTML attributes track component loading lifecycle (pending → loading → loaded/error) with automatic timing and error reporting.

7. **100% Semantic Instrumentation**: All UI elements use `data-tekton-*` attributes for reliable AI/automation discovery and interaction.

8. **WebSocket Communication**: Real-time communication with backend services through a unified WebSocket client.

9. **Terminal Interface**: Terminal-based interaction alongside the graphical interface for command-line operations.

## Getting Started

To start working with Hephaestus:

1. **Setup**: Ensure you have the Tekton codebase cloned and set up locally
2. **Run**: Use the `/Hephaestus/run_ui.sh` script to start the UI server
3. **Access**: Open `http://localhost:8080` in your browser
4. **Develop**: Follow the [Developer Guide](./developer_guide.md) to create or modify components

## Contributing

When contributing to Hephaestus, please:

1. Follow the established CSS naming convention
2. Use Shadow DOM isolation for all components
3. Implement proper theme support
4. Add comprehensive error handling
5. Test your components thoroughly
6. Document any new features or changes

## See Also

- [DEVELOPMENT_STATUS.md](../DEVELOPMENT_STATUS.md) - Current development status and roadmap
- [UI_STYLING_GUIDE.md](../UI_STYLING_GUIDE.md) - Detailed styling guidelines
- [COMPONENT_ISOLATION_STRATEGY.md](../COMPONENT_ISOLATION_STRATEGY.md) - In-depth explanation of the isolation approach
- [CSS_NAMING_CONVENTION.md](../CSS_NAMING_CONVENTION.md) - CSS naming conventions and examples