# Fix GUI Sprint - Architectural Decisions

## Overview
This document records the architectural decisions made during the Fix GUI Sprint Development Sprint. It captures the context, considerations, alternatives considered, and rationale behind each significant decision. This serves as a reference for both current implementation and future development.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. The architectural decisions in this document focus on simplifying and standardizing the Hephaestus UI architecture to create a more reliable component integration system.

## Decision 1: Simplify Panel System Architecture

### Context
The current Hephaestus UI uses a complex panel system with HTML panels, terminal panels, and special case handling for different components. This has led to confusion in component rendering, with components appearing in unexpected locations or not appearing at all.

### Problem Statement
Components like Athena are being loaded in the HTML panel (side panel) instead of the main content area. The distinction between terminal mode and HTML mode is causing rendering issues.

### Decision
Simplify the panel system to use a clear two-panel layout:
1. **Left Panel:** Navigation tabs and component selection
2. **Right Panel:** Main content area for all component UIs

### Alternatives Considered
1. **Maintain current architecture with fixes:** Continue using the current panel system but fix specific issues
2. **Complete UI rewrite:** Start from scratch with a new UI framework
3. **Multiple panel types:** Create different panel types for different component needs

### Rationale
The simplified two-panel layout provides a clear separation of concerns, making it easier to predict where components will render. It aligns with the user's preference for keeping the LEFT PANEL for navigation and using the RIGHT PANEL for HTML component UIs.

### Implementation Details
- Modify `ui-manager.js` to consistently use the main content area for all components
- Eliminate the concept of "terminal mode" vs. "HTML mode" in component loading
- Create a standardized component loading process that works for all components

## Decision 2: Eliminate Shadow DOM Complexity

### Context
The current implementation uses Shadow DOM for component isolation, which adds complexity and causes issues with style inheritance and DOM manipulation.

### Problem Statement
Shadow DOM implementation is causing conflicts with the Hephaestus component loader and making it difficult to apply consistent styling across components.

### Decision
Move away from Shadow DOM for most components, using simpler HTML-based components with clearly scoped CSS instead.

### Alternatives Considered
1. **Improve Shadow DOM implementation:** Fix the current Shadow DOM implementation with better encapsulation
2. **Web Components without Shadow DOM:** Use Web Components API but without Shadow DOM
3. **iframes for isolation:** Use iframes for complete component isolation

### Rationale
Simple HTML-based components with scoped CSS provide sufficient isolation while being easier to debug and maintain. This aligns with the user's preference for simpler HTML/CSS with minimal DOM manipulation.

### Implementation Details
- Remove `usesShadowDom: true` from component registry for most components
- Implement BEM naming convention for CSS to avoid style conflicts
- Create a simple component template system that doesn't rely on Shadow DOM

## Decision 3: Standardize Component Templates

### Context
Components currently have inconsistent structures and loading patterns, making it difficult to predict how they will render.

### Problem Statement
Each component has its own unique structure and initialization process, leading to inconsistent behavior and difficult maintenance.

### Decision
Create standardized component templates for both HTML and JavaScript, with clear lifecycle methods and rendering patterns.

### Alternatives Considered
1. **Custom framework:** Develop a custom framework specific to Hephaestus
2. **Adopt existing framework:** Integrate a lightweight existing framework (like Lit or Preact)
3. **Component-specific approaches:** Allow each component to define its own approach

### Rationale
Standardized templates provide consistency and predictability across components while remaining lightweight. This makes it easier to create new components and maintain existing ones.

### Implementation Details
- Create a base component template with standard lifecycle methods (init, render, update, destroy)
- Implement a standard structure for HTML templates with clearly defined content areas
- Standardize how components register event handlers and update their state

## Decision 4: Dedicated Terminal Functionality

### Context
The terminal functionality is currently mixed with the HTML UI components, causing confusion and rendering issues.

### Problem Statement
Some components (like Athena) are being forced into "terminal mode" when they should be using HTML interfaces. The terminal functionality is useful but needs to be properly separated.

### Decision
Use Terma as a dedicated terminal for AI tools, separate from the main component rendering system.

### Alternatives Considered
1. **Remove terminal functionality:** Focus only on HTML interfaces
2. **Multiple terminal instances:** Allow multiple terminal instances for different components
3. **Embedded terminals:** Embed terminal functionality within HTML components

### Rationale
Using Terma as a dedicated terminal component provides the terminal functionality where needed while preventing it from interfering with HTML-based components. This aligns with the user's request to "disable the terminal" for HTML components like Athena.

### Implementation Details
- Configure Terma as the primary terminal provider
- Remove terminal mode from other components like Athena
- Create clear integration points between HTML components and terminal functionality when needed

## Decision 5: Chat Interface Integration

### Context
AI/LLM integration is a core feature of Tekton, but the chat interfaces are not consistently implemented across components.

### Problem Statement
There's no standardized way to add chat interfaces to component screens, leading to inconsistent user experiences and duplicate code.

### Decision
Create a standardized chat interface component that can be added to any component screen, with consistent styling and behavior.

### Alternatives Considered
1. **Component-specific chat:** Allow each component to implement its own chat interface
2. **Central chat window:** Use a single chat window for all components
3. **External chat application:** Use a separate application for chat functionality

### Rationale
A standardized chat interface that can be embedded in any component provides consistency while allowing component-specific behaviors when needed. This aligns with the user's request to add AI/LLM chat to every RIGHT PANEL screen.

### Implementation Details
- Create a reusable chat interface component in `scripts/shared/chat-interface.js`
- Implement consistent styling in `styles/shared/chat-interface.css`
- Add hooks for connecting to the Tekton LLM Adapter
- Create an easy way to add the chat interface to any component

## Decision 6: WebSocket Connection Handling

### Context
WebSocket connections are failing with "invalid Connection header: keep-alive" errors, indicating issues with the WebSocket server configuration.

### Problem Statement
The current WebSocket implementation doesn't properly separate HTTP and WebSocket protocols, leading to connection errors.

### Decision
Implement proper HTTP/WebSocket separation, potentially using separate ports for WebSocket connections.

### Alternatives Considered
1. **Fix current implementation:** Fix the current implementation without architectural changes
2. **External WebSocket service:** Move WebSocket handling to a separate service
3. **WebSocket library:** Use a dedicated WebSocket library with better protocol handling

### Rationale
Proper protocol separation ensures reliable WebSocket connections while maintaining compatibility with the Single Port Architecture patterns described in the CLAUDE.md file.

### Implementation Details
- Modify `server.py` to properly handle WebSocket protocol
- Update `websocket.js` to connect using the correct protocol and headers
- Implement proper error handling for WebSocket connections

## Decision 7: Component Registration System

### Context
Components are currently registered in `component_registry.json` with inconsistent configuration parameters.

### Problem Statement
The component registration system doesn't clearly define which parameters are required and what they do, leading to configuration errors.

### Decision
Standardize the component registration system with clear documentation and validation.

### Alternatives Considered
1. **Dynamic registration:** Implement dynamic component registration at runtime
2. **Code-based registration:** Move registration from JSON to code
3. **Registry service:** Create a dedicated registry service

### Rationale
A standardized JSON-based registration system with validation provides a good balance of flexibility and reliability, making it easier to add new components.

### Implementation Details
- Clearly document all registration parameters
- Implement validation in the component loader
- Create a standard template for new component registration