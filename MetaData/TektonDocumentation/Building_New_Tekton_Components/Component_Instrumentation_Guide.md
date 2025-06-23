# Component Instrumentation Guide

## Overview

This guide explains how to instrument Tekton components with metadata annotations that enable knowledge graph construction and improved AI understanding. All new components and updates to existing components MUST include proper instrumentation.

## Core Principles

1. **Instrument as You Build** - Add metadata when creating new code, not as an afterthought
2. **Update During Modifications** - When changing code, update its metadata
3. **Grep-Friendly Format** - Use patterns that are easily searchable
4. **Knowledge Graph Ready** - Structure metadata for future graph extraction
5. **Consistent Patterns** - Follow established conventions across all file types

## Instrumentation Types

### 1. UI Semantic Tags (data-tekton-*)

Used in HTML files to create navigable, self-documenting UI infrastructure.

#### Required Tags for New Components

```html
<!-- Component root - ALWAYS required -->
<div class="mycomponent"
     data-tekton-area="mycomponent"
     data-tekton-component="mycomponent"
     data-tekton-type="component-workspace"
     data-tekton-description="Brief component description">

<!-- Sections within component -->
<div class="mycomponent__header" 
     data-tekton-zone="header"
     data-tekton-section="header">

<!-- Interactive elements -->
<button data-tekton-action="refresh"
        data-tekton-action-type="primary"
        onclick="mycomponent_refresh()">

<!-- Forms and inputs -->
<input data-tekton-input="search"
       data-tekton-input-type="text"
       data-tekton-validation="optional">

<!-- Navigation -->
<div class="mycomponent__tab"
     data-tekton-menu-item="Overview"
     data-tekton-menu-component="mycomponent"
     data-tekton-menu-active="true"
     data-tekton-nav-target="overview">
```

#### Knowledge Graph Preparation Tags

```html
<!-- Relationships between components -->
<div data-tekton-component="mycomponent"
     data-tekton-depends-on="hermes,athena"
     data-tekton-provides="data-processing"
     data-tekton-consumes="messages,queries">

<!-- State and status -->
<span data-tekton-status="connection"
      data-tekton-status-type="health"
      data-tekton-status-source="backend">

<!-- Data flow indicators -->
<div data-tekton-data-sink="true"
     data-tekton-data-type="json"
     data-tekton-data-source="api">
```

### 2. Backend Code Metadata (@tekton-*)

Used in Python, JavaScript, and other code files to document functionality, relationships, and behavior.

#### Python Instrumentation

```python
# @tekton-module: Core API endpoints for MyComponent
# @tekton-depends: hermes.client, athena.query
# @tekton-provides: rest-api, websocket-events
# @tekton-version: 1.0.0

"""
MyComponent API Module

This module provides REST API endpoints for MyComponent functionality.
"""

# @tekton-function: Initialize database connection
# @tekton-critical: true
# @tekton-error-handling: retry-with-backoff
# @tekton-modifies: database-connection-pool
async def initialize_database():
    """Initialize database connections with retry logic."""
    # Implementation...

# @tekton-endpoint: GET /api/status
# @tekton-returns: SystemStatus
# @tekton-auth: optional
# @tekton-cache: 30s
@router.get("/status")
async def get_status():
    """Get current system status."""
    # Implementation...

# @tekton-class: Main service handler
# @tekton-singleton: true
# @tekton-lifecycle: application
class MyComponentService:
    """Main service class for MyComponent operations."""
    
    # @tekton-method: Process incoming messages
    # @tekton-async: true
    # @tekton-rate-limit: 100/minute
    async def process_message(self, message: dict):
        """Process messages from message queue."""
        # Implementation...
```

#### JavaScript Instrumentation

```javascript
// @tekton-module: UI state management
// @tekton-depends: websocket-client
// @tekton-provides: ui-updates, state-sync
// @tekton-browser-only: true

/**
 * MyComponent UI Controller
 * @tekton-class: UI controller for MyComponent
 * @tekton-singleton: true
 */

// @tekton-function: Initialize component UI
// @tekton-dom-requires: data-tekton-component="mycomponent"
// @tekton-calls: /api/status, /api/config
function initializeMyComponent() {
    // Implementation...
}

// @tekton-function: Handle WebSocket messages
// @tekton-event-handler: websocket-message
// @tekton-updates-dom: data-tekton-status, data-tekton-messages
function handleWebSocketMessage(event) {
    // Implementation...
}

// @tekton-function: Update UI status
// @tekton-dom-modifies: #mycomponent-status
// @tekton-triggered-by: websocket, api-poll
function updateStatus(status) {
    // Implementation...
}
```

## Instrumentation During Development

### When Creating New Code

1. **Before Writing Code**: Plan the metadata structure
2. **During Implementation**: Add metadata inline with code
3. **After Completion**: Verify all public interfaces are documented

### When Modifying Existing Code

1. **Before Changes**: Review existing metadata
2. **During Changes**: Update metadata to reflect new behavior
3. **After Changes**: Add note about what changed

Example of modification tracking:

```python
# @tekton-function: Process user requests
# @tekton-modified: 2024-01-20 - Added rate limiting
# @tekton-modified: 2024-01-22 - Added caching support
# @tekton-breaking-change: 2024-01-22 - Changed return format
async def process_request(request: dict):
    """Process incoming user requests with rate limiting."""
    # Implementation...
```

### Component Relationships

Document how components interact:

```python
# @tekton-integration: Hermes
# @tekton-message-types: status-update, data-request
# @tekton-connection-type: websocket
# @tekton-fallback: http-polling
class HermesIntegration:
    """Handles communication with Hermes message broker."""
    
    # @tekton-sends: {"type": "status-update", "frequency": "30s"}
    async def send_status_update(self):
        # Implementation...
    
    # @tekton-receives: {"type": "data-request", "handler": "process_data_request"}
    async def setup_listeners(self):
        # Implementation...
```

## Knowledge Graph Preparation

### Entity Extraction Patterns

Structure metadata for easy extraction into knowledge graph entities:

```python
# @tekton-entity-type: service
# @tekton-entity-name: MyComponentService
# @tekton-entity-properties: {
#   "port": 8015,
#   "protocol": "http",
#   "startup-time": "2-3s"
# }
```

### Relationship Extraction Patterns

Define relationships that can become graph edges:

```python
# @tekton-relationship: depends-on
# @tekton-relationship-target: HermesClient
# @tekton-relationship-properties: {
#   "connection-type": "websocket",
#   "required": true,
#   "fallback": "http"
# }
```

### Event Flow Documentation

Track data and event flows:

```python
# @tekton-event-source: true
# @tekton-emits: ["status-changed", "data-processed", "error-occurred"]
# @tekton-event-format: json
# @tekton-event-schema: ./schemas/events.json
```

## Validation and Maintenance

### Self-Validation Patterns

Include validation hints for automated checking:

```python
# @tekton-validates: input-schema.json
# @tekton-validation-level: strict
# @tekton-test-coverage-required: 80%
```

### Deprecation Tracking

```python
# @tekton-deprecated: 2024-02-01
# @tekton-removal-date: 2024-05-01
# @tekton-replacement: use process_request_v2 instead
# @tekton-migration-guide: docs/migration/v2.md
```

## Quick Reference Checklist

When building or modifying components, ensure:

- [ ] Component root has all required data-tekton-* attributes
- [ ] All public functions have @tekton-function metadata
- [ ] All classes have @tekton-class metadata
- [ ] All API endpoints have @tekton-endpoint metadata
- [ ] Dependencies are documented with @tekton-depends
- [ ] Provided capabilities use @tekton-provides
- [ ] Modifications are tracked with @tekton-modified
- [ ] Breaking changes use @tekton-breaking-change
- [ ] Relationships to other components are documented
- [ ] Event flows are specified with @tekton-emits/receives
- [ ] Knowledge graph entities and relationships are defined

## Integration with Development Workflow

### Before Committing Code

1. Run instrumentation check: `grep -r "@tekton-\|data-tekton-" . | grep -v ".git"`
2. Verify all new code has metadata
3. Ensure modified code has updated metadata
4. Check that relationships are bidirectional (both sides documented)

### During Code Review

- Reviewers should check for missing instrumentation
- Verify metadata accuracy against implementation
- Ensure breaking changes are properly marked
- Confirm relationship documentation is complete

### Automated Tooling Support

Future tools will:
- Extract metadata into knowledge graphs
- Generate documentation from metadata
- Validate relationship consistency
- Track API evolution through metadata changes

## Next Steps

1. Always instrument new code as you write it
2. Update metadata when modifying existing code
3. Use consistent patterns across all components
4. Think about knowledge graph extraction while instrumenting
5. Document both what the code does AND how it relates to other components