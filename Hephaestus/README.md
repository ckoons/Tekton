# Hephaestus

## Overview

Hephaestus is the unified user interface for the Tekton ecosystem, providing both terminal and graphical interfaces for interacting with all Tekton components. It features a CSS-first architecture, Shadow DOM isolation, comprehensive semantic tagging, and advanced debugging tools for AI-assisted development.

## Quick Start

```bash
# Start the UI server
./run_ui.sh

# Or with MCP DevTools
./run_mcp.sh

# Access the UI
open http://localhost:8088
```

## CSS-First Architecture (June 2025)

Hephaestus now uses a **CSS-first architecture** with:
- Components loaded dynamically via minimal-loader.js when needed
- Navigation managed by JavaScript event handlers  
- Clean separation between navigation and content
- No build step required - edit components directly

**📖 MUST READ**: [CSS-First Architecture Documentation](/MetaData/TektonDocumentation/Architecture/CSSFirstArchitecture.md)

Key benefits:
- Edit component files directly in `ui/components/`
- Changes appear after browser refresh
- Navigation uses `#componentName` URL fragments
- Components are loaded on-demand when clicked

## Key Features

### 1. CSS-First Architecture
- Direct component editing without build steps
- Dynamic loading via minimal-loader.js
- URL fragment-based navigation (#componentName)
- Immediate updates on browser refresh

### 2. Shadow DOM Isolation
- Prevents style bleeding between components
- Isolated component contexts
- Clean DOM separation
- Theme propagation through boundaries

### 3. Semantic Tagging System
- **100% Coverage**: All UI elements use `data-tekton-*` attributes
- **Static Tags**: 75+ tags defined in source code
- **Dynamic Tags**: 71+ tags added by browser at runtime
- **Total Tags**: 146+ semantic tags in running components
- Enables reliable AI/automation interaction

### 4. UI DevTools V2
**Revolutionary debugging based on "Code is Truth, Browser is Result"**
- **code_reader**: Read source files (the TRUTH)
- **browser_verifier**: Check browser DOM (the RESULT)  
- **comparator**: Understand differences (dynamic tags)
- **navigator**: Navigate to components reliably
- **safe_tester**: Test changes with preview

Launch with: `./run_mcp.sh`

### 5. Component Features
- **Theme System**: Consistent theming with CSS variables
- **Loading States**: Lifecycle tracking (pending → loading → loaded/error)
- **Service Integration**: Standardized patterns for all Tekton services
- **WebSocket Support**: Real-time backend communication
- **Terminal Interface**: Command-line operations alongside GUI

### 6. Debug System
- File trace logging for loaded JavaScript
- Console filtering without code modification
- Performance monitoring with zero overhead when disabled
- Dead code identification

Enable with: `HephaestusDebug.enableAll()`

## Configuration

### Environment Variables

```bash
# Hephaestus-specific settings
HEPHAESTUS_PORT=8088                  # UI server port
HEPHAESTUS_AI_PORT=45088              # CI specialist port  
HEPHAESTUS_DEBUG=false                # Debug mode
HEPHAESTUS_THEME=dark                 # Default theme

# DevTools settings
MCP_SERVER_PORT=8088                  # MCP DevTools port
MCP_DEBUG=false                       # MCP debug logging
```

### UI DevTools V2 Usage

```python
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def devtools_request(tool_name, arguments):
    async with httpx.AsyncClient() as client:
        response = await client.post(MCP_URL, json={
            "tool_name": tool_name,
            "arguments": arguments
        })
        return response.json()

# Example: Check component source vs browser
result = await devtools_request("code_reader", {"component": "rhetor"})
print(f"Source has {result['result']['semantic_tags']['total_count']} tags")

result = await devtools_request("browser_verifier", {"component": "rhetor"})
print(f"Browser has {result['result']['semantic_tags']['count']} tags")
```

## Component Structure

```
ui/components/
├── <component-name>/
│   └── <component-name>-component.html    # Complete component
├── shared/
│   └── component-template.html            # Template for new components
└── terma/
    └── terma-component.html              # Terminal integration

ui/scripts/
├── minimal-loader.js                      # Dynamic component loader
├── debug-config.js                        # Debug system configuration
└── <component-name>/
    └── <component-name>-component.js      # Component JavaScript

ui/styles/
├── main.css                               # Global styles
├── components.css                         # Component registry
└── themes/                                # Theme files
```

## Development Workflow

### 1. Creating a New Component

```bash
# Copy template
cp ui/components/shared/component-template.html \
   ui/components/mycomponent/mycomponent-component.html

# Edit component
# Add semantic tags: data-tekton-component="mycomponent"
# Implement functionality

# Register in components.css
echo '.mycomponent-component { display: block; }' >> ui/styles/components.css
```

### 2. Testing with DevTools

```python
# Verify semantic tags
result = await devtools_request("code_reader", {"component": "mycomponent"})

# Test in browser
result = await devtools_request("navigator", {"target": "mycomponent"})

# Safe test changes
result = await devtools_request("safe_tester", {
    "area": "mycomponent",
    "changes": [{"type": "text", "selector": ".title", "content": "New Title"}],
    "preview": True
})
```

### 3. Debugging

```javascript
// Enable debug output
HephaestusDebug.enableAll()

// Check component loading
HephaestusDebug.enableFileTrace()

// Navigate to component
window.location.hash = '#mycomponent'
```

## API Reference

### MCP DevTools API

The Model Context Protocol server provides tools for UI development:

#### Available Tools

- `code_reader` - Read component source files
- `browser_verifier` - Verify browser DOM state  
- `comparator` - Compare source vs browser
- `navigator` - Navigate to components
- `safe_tester` - Test UI changes safely
- `ui_capture` - Capture UI state
- `ui_sandbox` - Sandbox for testing changes

#### Tool Usage

```python
# Basic tool invocation
result = await devtools_request("tool_name", {
    "param1": "value1",
    "param2": "value2"
})
```

### Component API

Each component exposes:

```javascript
class ComponentName {
    // Lifecycle methods
    connectedCallback()      // When attached to DOM
    disconnectedCallback()   // When removed from DOM
    
    // State management
    setState(newState)       // Update component state
    getState()              // Get current state
    
    // Event handling
    emit(eventName, data)    // Emit custom event
    on(eventName, handler)   // Listen for events
}
```

## Integration Points

Hephaestus integrates with all Tekton components:

- **Hermes**: Message bus for inter-component communication
- **Engram**: Memory system for UI state persistence
- **Rhetor**: LLM integration for chat interfaces
- **Terma**: Terminal emulation and command execution
- **All Components**: Unified UI representation

### Service Integration Pattern

```javascript
// Example: Integrating with a Tekton service
import { HermesConnector } from '/scripts/hermes-connector.js';

const hermes = new HermesConnector();
await hermes.connect();

// Subscribe to messages
hermes.subscribe('component.event', (data) => {
    updateUI(data);
});

// Send messages
hermes.send('component.action', { 
    action: 'refresh',
    component: 'rhetor' 
});
```

## Troubleshooting

### Common Issues

#### Component Not Loading
- Check browser console for errors
- Verify component is registered in components.css
- Enable debug: `HephaestusDebug.enableAll()`
- Check file path in minimal-loader.js

#### Semantic Tags Missing
- Use DevTools to compare source vs browser
- Remember: Browser ADDS tags, doesn't remove them
- Check for typos in data-tekton-* attributes

#### Theme Not Applied
- Verify CSS variables in Shadow DOM
- Check theme propagation in component
- Inspect computed styles

## Best Practices

1. **Always Use Semantic Tags**
   - Add `data-tekton-*` attributes to all interactive elements
   - Use descriptive values: `data-tekton-action="submit-query"`

2. **Follow CSS-First Principles**
   - Edit components directly, no build step
   - Use CSS for layout, JavaScript for behavior

3. **Test with DevTools V2**
   - Verify source truth with code_reader
   - Check browser result with browser_verifier
   - Always preview before applying changes

4. **Document Components**
   - Add comments explaining functionality
   - Document data attributes used
   - Include usage examples

## Related Documentation

- [CSS-First Architecture](/MetaData/TektonDocumentation/Architecture/CSSFirstArchitecture.md)
- [UI DevTools V2 Guide](/MetaData/TektonDocumentation/Guides/UIDevToolsV2/README.md)
- [Semantic Tagging Guide](/MetaData/TektonDocumentation/Guides/SemanticTagging.md)
- [Component Development](/MetaData/ComponentDocumentation/Hephaestus/COMPONENT_GUIDE.md)
- [Debug System](/Hephaestus/ui/DEBUGGING.md)