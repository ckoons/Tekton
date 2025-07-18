# Tekton Shared Component Utilities

This document describes the shared utilities available for Tekton components, using our new simplified UI approach with direct HTML injection and BEM naming conventions.

## Overview

Tekton provides a set of shared utilities to standardize common functionality across components. These utilities help ensure consistent behavior, reduce code duplication, and simplify component development.

## UI Component Utilities

### Direct HTML Injection

The new UI approach uses direct HTML injection instead of Shadow DOM:

```javascript
class ComponentUtilities {
  /**
   * Inject HTML into a container element
   * @param {string} html - HTML content to inject
   * @param {HTMLElement} container - Container element to inject into
   * @returns {HTMLElement} - The container with injected content
   */
  static injectHTML(html, container) {
    container.innerHTML = html;
    return container;
  }
  
  /**
   * Load component HTML from a URL and inject it into a container
   * @param {string} url - URL to load HTML from
   * @param {HTMLElement} container - Container element to inject into
   * @returns {Promise<HTMLElement>} - The container with injected content
   */
  static async loadAndInjectHTML(url, container) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to load HTML from ${url}: ${response.status}`);
      }
      const html = await response.text();
      return this.injectHTML(html, container);
    } catch (error) {
      console.error('Error loading component HTML:', error);
      container.innerHTML = `<div class="component-error">
        <h3>Error Loading Component</h3>
        <p>${error.message}</p>
      </div>`;
      throw error;
    }
  }
}
```

### Component Class Pattern

Each component follows a standard class-based pattern:

```javascript
/**
 * Base component class for Tekton UI components
 */
class BaseComponent {
  /**
   * Create a new component
   * @param {string} id - Component ID
   * @param {HTMLElement} container - Container element to render into
   */
  constructor(id, container) {
    this.id = id;
    this.container = container;
    this.state = {};
    this.eventHandlers = [];
    this.styleElement = null;
    this.initialized = false;
  }
  
  /**
   * Initialize the component
   * @returns {Promise<BaseComponent>} - The component instance
   */
  async init() {
    if (this.initialized) return this;
    
    try {
      // Load HTML
      await ComponentUtilities.loadAndInjectHTML(
        `/components/${this.id}/${this.id}-component.html`, 
        this.container
      );
      
      // Load and inject styles
      await this.loadStyles();
      
      // Initialize event handlers
      this.initEventHandlers();
      
      this.initialized = true;
      
      return this;
    } catch (error) {
      console.error(`Error initializing component ${this.id}:`, error);
      throw error;
    }
  }
  
  /**
   * Load component styles
   * @returns {Promise<HTMLStyleElement>} - The created style element
   */
  async loadStyles() {
    try {
      const response = await fetch(`/styles/${this.id}/${this.id}-component.css`);
      if (!response.ok) {
        throw new Error(`Failed to load styles: ${response.status}`);
      }
      
      const css = await response.text();
      
      // Create or update style element
      if (!this.styleElement) {
        this.styleElement = document.createElement('style');
        document.head.appendChild(this.styleElement);
      }
      
      this.styleElement.textContent = css;
      return this.styleElement;
    } catch (error) {
      console.error(`Error loading styles for ${this.id}:`, error);
      throw error;
    }
  }
  
  /**
   * Initialize event handlers
   * Must be implemented by subclasses
   */
  initEventHandlers() {
    // To be implemented by subclasses
  }
  
  /**
   * Add an event handler
   * @param {HTMLElement} element - Element to attach handler to
   * @param {string} eventType - Event type (e.g., 'click')
   * @param {Function} handler - Event handler function
   */
  addEventHandler(element, eventType, handler) {
    element.addEventListener(eventType, handler);
    
    // Store for cleanup
    this.eventHandlers.push({
      element,
      eventType,
      handler
    });
  }
  
  /**
   * Clean up the component
   */
  cleanup() {
    // Remove event handlers
    this.eventHandlers.forEach(({element, eventType, handler}) => {
      element.removeEventListener(eventType, handler);
    });
    this.eventHandlers = [];
    
    // Remove style element
    if (this.styleElement && this.styleElement.parentNode) {
      this.styleElement.parentNode.removeChild(this.styleElement);
      this.styleElement = null;
    }
    
    // Clear container
    this.container.innerHTML = '';
    
    this.initialized = false;
  }
  
  /**
   * Find an element within the component
   * @param {string} selector - CSS selector
   * @returns {HTMLElement} - The found element
   */
  $(selector) {
    return this.container.querySelector(selector);
  }
  
  /**
   * Find all elements within the component
   * @param {string} selector - CSS selector
   * @returns {HTMLElement[]} - The found elements
   */
  $$(selector) {
    return [...this.container.querySelectorAll(selector)];
  }
  
  /**
   * Update the component's state
   * @param {Object} newState - New state to merge with current state
   */
  updateState(newState) {
    this.state = {...this.state, ...newState};
    this.render();
  }
  
  /**
   * Render the component based on current state
   * Must be implemented by subclasses
   */
  render() {
    // To be implemented by subclasses
  }
}
```

### BEM Utility Functions

Helpers for working with BEM-style class names:

```javascript
/**
 * Utilities for working with BEM-style class names
 */
class BEMUtilities {
  /**
   * Create a block class name
   * @param {string} block - Block name
   * @returns {string} - The block class name
   */
  static block(block) {
    return block;
  }
  
  /**
   * Create an element class name
   * @param {string} block - Block name
   * @param {string} element - Element name
   * @returns {string} - The element class name
   */
  static element(block, element) {
    return `${block}__${element}`;
  }
  
  /**
   * Create a modifier class name
   * @param {string} blockOrElement - Block or element class name
   * @param {string} modifier - Modifier name
   * @returns {string} - The modifier class name
   */
  static modifier(blockOrElement, modifier) {
    return `${blockOrElement}--${modifier}`;
  }
  
  /**
   * Get class names for an element with optional modifiers
   * @param {string} block - Block name
   * @param {string} element - Element name
   * @param {Object} modifiers - Object where keys are modifier names and values are booleans
   * @returns {string} - Space-separated class names
   */
  static elementWithModifiers(block, element, modifiers = {}) {
    const elementClass = this.element(block, element);
    
    return Object.entries(modifiers)
      .filter(([_, active]) => active)
      .reduce((classes, [modifier]) => {
        return `${classes} ${this.modifier(elementClass, modifier)}`;
      }, elementClass);
  }
}
```

## Shell Utilities

### Core Utilities (tekton-utils.sh)

The core utilities provide common functions for logging, directory detection, command execution, and cross-platform compatibility.

```bash
#!/bin/bash

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/tekton-utils.sh"

# Use logging functions
tekton_info "Starting component..."
tekton_success "Component started"
tekton_warn "Warning message"
tekton_error_exit "Error message" 1

# Directory functions
TEKTON_ROOT=$(tekton_find_root)
tekton_is_in_tekton_dir "/some/path"

# Command utilities
if tekton_command_exists "python3"; then
    # Do something
fi

# Prompt user for input
VALUE=$(tekton_prompt_with_default "Enter value" "default")
if tekton_prompt_yes_no "Continue?" "y"; then
    # User chose yes
fi
```

### Port Management (tekton-ports.sh)

Utilities for managing ports according to Tekton's Single Port Architecture.

```bash
#!/bin/bash

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/tekton-utils.sh"
source "${SCRIPT_DIR}/../lib/tekton-ports.sh"

# Check if a port is in use
if tekton_is_port_used 8080; then
    # Port is in use
fi

# Get process using a port
PROCESS_INFO=$(tekton_get_port_process 8080)

# Release a port
tekton_release_port 8080 "Hephaestus UI"

# Get a component's standard port
PORT=$(tekton_get_component_port "hermes")

# Ensure all ports are available
tekton_ensure_ports_available

# Check if a port is responding
if tekton_is_port_responding 8080 "localhost" "/health"; then
    # Service is healthy
fi

# Wait for a port to be available
tekton_wait_for_port_available 8080 30 "Hephaestus UI"

# Wait for a port to start responding
tekton_wait_for_port_responding 8080 30 "Hephaestus UI"
```

## Python Utilities

### LLM Client

The `tekton_llm_client` package provides a standardized client for interacting with LLMs through Rhetor.

```python
import asyncio
from tekton_llm_client import (
    TektonLLMClient, 
    PromptTemplateRegistry, 
    parse_json,
    StructuredOutputParser, 
    OutputFormat
)

async def main():
    # Create an LLM client
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Use prompt templates
    registry = PromptTemplateRegistry()
    prompt = registry.render(
        "code_review",
        language="python",
        code="def hello(): return 'Hello, world!'",
        focus_area="best practices"
    )
    
    # Generate text
    response = await client.generate_text(prompt=prompt)
    
    # Parse structured output
    data = parse_json(response.content)
    
    # Parse specific output formats
    parser = StructuredOutputParser(format=OutputFormat.LIST)
    items = parser.parse(response.content)
    
    # Clean up
    await client.shutdown()

asyncio.run(main())
```

### Component Registration

The `tekton.utils.registration` module provides utilities for registering components with the Hermes service registry.

```python
from tekton.utils.registration import (
    load_component_config,
    register_component,
    unregister_component,
    get_registration_status
)

async def main():
    # Load component configuration
    config = load_component_config("my-component")
    
    # Register component
    success, client = await register_component("my-component", config)
    
    if success:
        print("Component registered successfully")
        
        # Use the client for other operations
        await client.heartbeat()
        
        # When done, unregister and close the client
        await client.unregister()
        await client.close()
    else:
        print("Failed to register component")
```

## Best Practices for Simplified UI Components

1. **HTML Structure**: Follow the standard RIGHT PANEL structure with HEADER, MENU BAR, WORKSPACE, and optional CHAT-INPUT-AREA.

2. **BEM Naming Convention**: Use Block-Element-Modifier pattern for CSS class names.
   ```css
   /* Block */
   .component-name {}
   
   /* Element */
   .component-name__header {}
   .component-name__menu {}
   
   /* Modifier */
   .component-name__button--primary {}
   .component-name__menu--collapsed {}
   ```

3. **Component Size**: Keep component files under 500 lines. Split files at 600+ lines with a hard limit of 1000 lines.

4. **Direct HTML Injection**: Use direct HTML injection instead of Shadow DOM for simpler debugging and integration.

5. **File Organization**: Follow the standard file organization:
   ```
   components/
   ├── [component-name]/
   │   └── [component-name]-component.html
   ├── styles/
   │   └── [component-name]/
   │       └── [component-name]-component.css
   └── scripts/
       └── [component-name]/
           ├── [component-name]-service.js (optional)
           └── [component-name]-component.js
   ```

6. **Cleanup**: Always implement proper cleanup to prevent memory leaks:
   ```javascript
   // In your component class
   cleanup() {
     // Remove event listeners
     this.eventHandlers.forEach(({element, eventType, handler}) => {
       element.removeEventListener(eventType, handler);
     });
     
     // Clear references
     this.container.innerHTML = '';
     this.eventHandlers = [];
   }
   ```

7. **Event Delegation**: Use event delegation for efficient event handling:
   ```javascript
   // Instead of adding handlers to each button
   this.$$('.my-component__button').forEach(button => {
     button.addEventListener('click', this.handleClick.bind(this));
   });
   
   // Use delegation on the container
   this.container.addEventListener('click', event => {
     const button = event.target.closest('.my-component__button');
     if (button) {
       this.handleClick(event);
     }
   });
   ```

8. **Component Communication**: Use custom events for component communication:
   ```javascript
   // Dispatch an event
   const event = new CustomEvent('componentStateChanged', {
     bubbles: true,
     detail: { 
       componentId: this.id,
       state: this.state
     }
   });
   this.container.dispatchEvent(event);
   
   // Listen for events from other components
   document.addEventListener('componentStateChanged', event => {
     if (event.detail.componentId !== this.id) {
       this.handleExternalStateChange(event.detail);
     }
   });
   ```

## Migration Guide

To migrate existing components to use the new simplified approach:

1. **Convert Shadow DOM components** to use direct HTML injection with the BaseComponent class.

2. **Apply BEM naming conventions** to CSS classes for better organization and isolation.

3. **Restructure the component** to follow the standard RIGHT PANEL layout.

4. **Move event handlers** from Shadow DOM delegation to standard delegation.

5. **Replace Shadow DOM event dispatch** with standard CustomEvents.

6. **Update component loading** to use the new class-based pattern.

7. **Clean up any Shadow DOM-specific code** that's no longer needed.

8. **Verify component styling** works properly without Shadow DOM encapsulation.

## Examples

See the `examples` directory for complete examples of using the shared utilities with the new direct HTML injection approach and BEM naming conventions.