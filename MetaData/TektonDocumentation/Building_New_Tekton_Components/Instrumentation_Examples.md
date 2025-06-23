# Instrumentation Examples

## Overview

This document provides concrete examples of instrumentation for all major file types in Tekton components. Use these as templates when adding instrumentation to your code.

## HTML Files

### Complete Component Example

```html
<!-- Athena Component - Knowledge Graph Management -->
<div class="athena"
     data-tekton-area="athena"
     data-tekton-component="athena"
     data-tekton-type="component-workspace"
     data-tekton-description="Knowledge graph and entity management system"
     data-tekton-depends-on="hermes"
     data-tekton-provides="knowledge-graph,entity-search,relationship-mapping"
     data-tekton-version="1.0.0">
    
    <!-- Component Header -->
    <div class="athena__header" 
         data-tekton-zone="header" 
         data-tekton-section="header">
        <div class="athena__title-container">
            <img src="/images/athena-icon.jpg" alt="Athena" class="athena__icon">
            <h2 class="athena__title"
                data-tekton-text="component-title"
                data-tekton-text-content="Athena - Knowledge">
                <span class="athena__title-main">Athena</span>
                <span class="athena__title-sub">Knowledge</span>
            </h2>
        </div>
        
        <!-- Status Indicators -->
        <div class="athena__status"
             data-tekton-status-group="health"
             data-tekton-updates="websocket,30s">
            <span data-tekton-status="graph-connection"
                  data-tekton-status-type="database"
                  data-tekton-status-values="connected,disconnected,error">
                Graph: <span id="graph-status">Checking...</span>
            </span>
        </div>
    </div>
    
    <!-- Navigation Menu -->
    <div class="athena__menu-bar" 
         data-tekton-zone="menu" 
         data-tekton-nav="component-menu">
        <div class="athena__tabs">
            <div class="athena__tab athena__tab--active" 
                 data-tab="entities"
                 data-tekton-menu-item="Entities"
                 data-tekton-menu-component="athena"
                 data-tekton-menu-active="true"
                 data-tekton-menu-panel="entities-panel"
                 data-tekton-nav-target="entities"
                 data-tekton-nav-action="switchTab"
                 onclick="athena_switchTab('entities')">
                <span class="athena__tab-label">Entities</span>
            </div>
        </div>
    </div>
    
    <!-- Content Panels -->
    <div class="athena__content" 
         data-tekton-zone="content" 
         data-tekton-scrollable="true">
        
        <!-- Entity Search Panel -->
        <div id="entities-panel" 
             class="athena__panel athena__panel--active"
             data-tekton-panel="entities"
             data-tekton-panel-for="Entities"
             data-tekton-panel-component="athena"
             data-tekton-panel-active="true">
            
            <!-- Search Form -->
            <form class="athena__search-form"
                  data-tekton-form="entity-search"
                  data-tekton-form-method="GET"
                  data-tekton-form-endpoint="/api/knowledge/entities"
                  data-tekton-form-result-target="entity-results">
                
                <input type="text" 
                       id="entity-search"
                       data-tekton-input="search-query"
                       data-tekton-input-type="search"
                       data-tekton-validation="min-length:2"
                       data-tekton-autocomplete="entity-names"
                       placeholder="Search entities...">
                
                <button type="submit"
                        data-tekton-action="search"
                        data-tekton-action-type="primary"
                        data-tekton-triggers="form-submit">
                    Search
                </button>
            </form>
            
            <!-- Results Display -->
            <div id="entity-results"
                 data-tekton-results="entity-search"
                 data-tekton-result-type="entity-list"
                 data-tekton-empty-message="No entities found"
                 data-tekton-loading-indicator="true">
                <!-- Results injected here -->
            </div>
        </div>
        
        <!-- Chat Interface -->
        <div class="athena__chat"
             data-tekton-chat="athena-assistant"
             data-tekton-chat-type="component"
             data-tekton-ai="athena-assistant"
             data-tekton-ai-context="knowledge-graph">
            
            <div class="athena__messages"
                 data-tekton-chat-messages="true"
                 data-tekton-message-format="markdown"
                 data-tekton-scroll-behavior="bottom">
                <!-- Messages appear here -->
            </div>
            
            <div class="athena__chat-input-container">
                <textarea data-tekton-chat-input="true"
                          data-tekton-input-multiline="true"
                          data-tekton-max-length="4000"
                          placeholder="Ask about entities, relationships..."></textarea>
                
                <button data-tekton-chat-send="true"
                        data-tekton-action="send-message"
                        data-tekton-requires="chat-input">
                    Send
                </button>
            </div>
        </div>
    </div>
</div>
```

## Python Files

### API Module Example

```python
# @tekton-module: Athena Knowledge Graph API
# @tekton-type: rest-api
# @tekton-depends: neo4j-driver, hermes.client
# @tekton-provides: knowledge-graph-api, entity-management, relationship-queries
# @tekton-version: 1.0.0
# @tekton-stability: stable

"""
Athena Knowledge Graph API

This module provides REST endpoints for managing entities and relationships
in the Tekton knowledge graph.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any

# @tekton-imports: External dependencies
# @tekton-import-purpose: neo4j for graph database, pydantic for validation
from neo4j import AsyncSession
from pydantic import BaseModel, Field

# @tekton-imports: Internal dependencies  
# @tekton-import-from: athena.core
from ..core.entity import Entity
from ..core.relationship import Relationship
from ..core.graph_db import get_session

# @tekton-router: Main API router for knowledge graph
# @tekton-path-prefix: /api/knowledge
# @tekton-tags: ["knowledge", "graph"]
router = APIRouter(
    prefix="/api/knowledge",
    tags=["knowledge"],
    responses={404: {"description": "Not found"}},
)

# @tekton-model: Entity creation request
# @tekton-validates: entity-schema.json
class CreateEntityRequest(BaseModel):
    """Request model for creating new entities."""
    
    # @tekton-field: Entity type classification
    # @tekton-allowed-values: ["person", "concept", "organization", "document", "system"]
    entity_type: str = Field(..., description="Type of entity")
    
    # @tekton-field: Human-readable entity name
    # @tekton-validation: min-length:1, max-length:255
    name: str = Field(..., description="Entity name")
    
    # @tekton-field: Additional entity properties
    # @tekton-format: json-object
    properties: Dict[str, Any] = Field(default_factory=dict)

# @tekton-endpoint: POST /api/knowledge/entities
# @tekton-operation: create-entity
# @tekton-auth: required
# @tekton-rate-limit: 100/minute
# @tekton-emits: entity-created
# @tekton-modifies: knowledge-graph
@router.post("/entities", response_model=Dict[str, str])
async def create_entity(
    request: CreateEntityRequest,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """
    Create a new entity in the knowledge graph.
    
    @tekton-function: Create knowledge graph entity
    @tekton-critical: false
    @tekton-retry: 3
    @tekton-timeout: 5s
    """
    try:
        # @tekton-step: Validate entity type
        # @tekton-validation: entity-type-enum
        if request.entity_type not in ["person", "concept", "organization", "document", "system"]:
            raise HTTPException(status_code=400, detail="Invalid entity type")
        
        # @tekton-step: Create entity object
        # @tekton-creates: Entity
        entity = Entity(
            entity_type=request.entity_type,
            name=request.name,
            properties=request.properties
        )
        
        # @tekton-step: Persist to graph database
        # @tekton-database-write: neo4j
        # @tekton-transaction: required
        entity_id = await entity.save(session)
        
        # @tekton-step: Emit creation event
        # @tekton-event: entity-created
        # @tekton-event-data: {"entity_id": entity_id, "type": request.entity_type}
        await emit_event("entity-created", {
            "entity_id": entity_id,
            "entity_type": request.entity_type,
            "name": request.name
        })
        
        return {"entity_id": entity_id, "status": "created"}
        
    except Exception as e:
        # @tekton-error-handling: Log and re-raise
        # @tekton-logs: error
        logger.error(f"Failed to create entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @tekton-endpoint: GET /api/knowledge/entities/search
# @tekton-operation: search-entities  
# @tekton-auth: optional
# @tekton-cache: 60s
# @tekton-returns: List[Entity]
@router.get("/entities/search", response_model=List[Dict[str, Any]])
async def search_entities(
    query: str,
    entity_type: Optional[str] = None,
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
) -> List[Dict[str, Any]]:
    """
    Search for entities matching query criteria.
    
    @tekton-function: Full-text entity search
    @tekton-index-used: entity-name-fulltext
    @tekton-performance: <100ms for 1M entities
    """
    # @tekton-query: Cypher query for entity search
    # @tekton-query-type: fulltext-search
    # @tekton-query-optimization: uses-index
    cypher = """
    MATCH (e:Entity)
    WHERE e.name CONTAINS $query
    AND ($entity_type IS NULL OR e.entity_type = $entity_type)
    RETURN e
    LIMIT $limit
    """
    
    result = await session.run(
        cypher,
        query=query,
        entity_type=entity_type,
        limit=limit
    )
    
    # @tekton-transform: Convert graph nodes to API response
    # @tekton-serialization: entity-to-dict
    entities = []
    async for record in result:
        entity = Entity.from_node(record["e"])
        entities.append(entity.to_dict())
    
    return entities

# @tekton-class: Entity relationship manager
# @tekton-singleton: false
# @tekton-lifecycle: request-scoped
class RelationshipManager:
    """
    Manages entity relationships in the knowledge graph.
    
    @tekton-responsibility: CRUD operations for relationships
    @tekton-collaborates-with: Entity, GraphDatabase
    """
    
    def __init__(self, session: AsyncSession):
        # @tekton-dependency-injection: Graph database session
        self.session = session
    
    # @tekton-method: Create bidirectional relationship
    # @tekton-modifies: knowledge-graph
    # @tekton-transaction: required
    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Dict[str, Any] = None
    ) -> str:
        """
        Create a relationship between two entities.
        
        @tekton-precondition: Both entities must exist
        @tekton-postcondition: Relationship created with unique ID
        @tekton-invariant: No duplicate relationships of same type
        """
        # Implementation...
        pass

# @tekton-websocket: /ws/knowledge/updates
# @tekton-event-stream: knowledge-graph-changes
# @tekton-auth: required
# @tekton-reconnect: auto
@router.websocket("/ws/updates")
async def knowledge_updates(websocket: WebSocket):
    """
    WebSocket endpoint for real-time knowledge graph updates.
    
    @tekton-broadcasts: entity-created, entity-updated, relationship-created
    @tekton-client-events: subscribe, unsubscribe
    @tekton-heartbeat: 30s
    """
    await websocket.accept()
    # Implementation...
```

### Service Class Example

```python
# @tekton-module: Athena Core Service
# @tekton-type: business-logic
# @tekton-pattern: service-layer
# @tekton-thread-safety: async-safe

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

# @tekton-service: Main Athena knowledge service
# @tekton-responsibilities: entity-lifecycle, relationship-management, graph-queries
# @tekton-state-management: stateless
# @tekton-initialization: lazy
class AthenaService:
    """
    Core service for Athena knowledge graph operations.
    
    @tekton-design-pattern: Repository pattern with async support
    @tekton-error-strategy: fail-fast with detailed logging
    """
    
    # @tekton-singleton-instance: Shared service instance
    # @tekton-thread-safe: yes
    _instance = None
    
    def __init__(self):
        # @tekton-initialization: Service dependencies
        # @tekton-lazy-load: database connections
        self._db = None
        self._cache = None
        self._initialized = False
    
    # @tekton-factory-method: Get or create service instance
    # @tekton-thread-safe: yes
    # @tekton-returns: AthenaService singleton
    @classmethod
    async def get_instance(cls) -> 'AthenaService':
        """Get or create the Athena service instance."""
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance._initialize()
        return cls._instance
    
    # @tekton-initialization-method: Setup service dependencies
    # @tekton-idempotent: yes
    # @tekton-startup-time: 1-2s
    async def _initialize(self):
        """Initialize service dependencies."""
        if self._initialized:
            return
            
        # @tekton-step: Connect to graph database
        # @tekton-retry: exponential-backoff
        # @tekton-timeout: 10s
        self._db = await self._connect_database()
        
        # @tekton-step: Initialize cache
        # @tekton-cache-type: redis
        # @tekton-cache-ttl: 300s
        self._cache = await self._setup_cache()
        
        self._initialized = True

    # @tekton-query-method: Find entities by pattern
    # @tekton-cache: true
    # @tekton-cache-key: pattern-{pattern}-type-{entity_type}
    # @tekton-performance-target: <50ms
    async def find_entities_by_pattern(
        self,
        pattern: str,
        entity_type: Optional[str] = None
    ) -> List[Entity]:
        """
        Find entities matching a pattern.
        
        @tekton-algorithm: Full-text search with relevance ranking
        @tekton-index: entity-name-fulltext
        @tekton-result-limit: 100
        """
        # @tekton-cache-check: Try cache first
        cache_key = f"pattern-{pattern}-type-{entity_type}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached
        
        # @tekton-database-query: Optimized Cypher query
        # @tekton-query-plan: IndexSeek -> Filter -> Sort
        results = await self._db.query(
            """
            MATCH (e:Entity)
            WHERE e.name =~ $pattern
            AND ($type IS NULL OR e.entity_type = $type)
            RETURN e
            ORDER BY e.relevance DESC
            LIMIT 100
            """,
            pattern=f".*{pattern}.*",
            type=entity_type
        )
        
        # @tekton-cache-store: Cache results
        await self._cache.set(cache_key, results, ttl=300)
        
        return results

    # @tekton-command-method: Merge duplicate entities
    # @tekton-modifies: knowledge-graph
    # @tekton-transaction: required
    # @tekton-compensating-action: unmerge_entities
    async def merge_entities(
        self,
        primary_id: str,
        duplicate_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Merge duplicate entities into a primary entity.
        
        @tekton-preconditions: All entities exist, no circular relationships
        @tekton-postconditions: Duplicates removed, relationships transferred
        @tekton-side-effects: Emits entity-merged events
        """
        # Implementation with detailed instrumentation...
        pass
```

## JavaScript Files

### UI Controller Example

```javascript
// @tekton-module: Athena UI Controller
// @tekton-type: browser-javascript
// @tekton-depends: websocket-client, dom-ready
// @tekton-provides: ui-state-management, event-handling
// @tekton-compatibility: es6+

/**
 * Athena UI Controller
 * 
 * @tekton-responsibility: UI state management and event handling
 * @tekton-pattern: Module pattern with event delegation
 * @tekton-initialization: DOMContentLoaded
 */

// @tekton-namespace: Global Athena namespace
// @tekton-singleton: true
window.AthenaUI = (function() {
    'use strict';
    
    // @tekton-state: Component state management
    // @tekton-mutable: internal only
    // @tekton-persistence: session
    const state = {
        connected: false,
        entities: [],
        selectedEntity: null,
        searchQuery: '',
        activePanel: 'entities'
    };
    
    // @tekton-config: UI configuration
    // @tekton-source: data-attributes, environment
    const config = {
        wsUrl: null,
        apiBaseUrl: '/api/knowledge',
        updateInterval: 30000,
        maxRetries: 3
    };
    
    // @tekton-function: Initialize UI controller
    // @tekton-lifecycle: startup
    // @tekton-dom-ready: required
    // @tekton-calls: connectWebSocket, setupEventHandlers, loadInitialData
    function initialize() {
        console.log('Initializing Athena UI');
        
        // @tekton-step: Extract configuration from DOM
        // @tekton-dom-query: [data-tekton-component="athena"]
        const component = document.querySelector('[data-tekton-component="athena"]');
        if (!component) {
            console.error('Athena component not found in DOM');
            return;
        }
        
        // @tekton-step: Setup WebSocket connection
        // @tekton-async: true
        // @tekton-retry: exponential-backoff
        connectWebSocket();
        
        // @tekton-step: Bind event handlers
        // @tekton-event-delegation: true
        setupEventHandlers();
        
        // @tekton-step: Load initial data
        // @tekton-parallel: true
        loadInitialData();
    }
    
    // @tekton-function: Setup WebSocket connection
    // @tekton-creates: WebSocket
    // @tekton-error-handling: reconnect-with-backoff
    // @tekton-emits: connection-state-changed
    function connectWebSocket() {
        // @tekton-websocket-config: Auto-reconnect, heartbeat
        const wsUrl = `ws://${window.location.host}/api/knowledge/ws/updates`;
        
        // @tekton-step: Create WebSocket connection
        // @tekton-protocol: ws
        // @tekton-heartbeat: 30s
        const ws = new WebSocket(wsUrl);
        
        // @tekton-event-handler: Connection opened
        // @tekton-updates: connection-status
        // @tekton-dom-modifies: [data-tekton-status="connection"]
        ws.onopen = function(event) {
            state.connected = true;
            updateConnectionStatus('connected');
            
            // @tekton-message: Subscribe to updates
            // @tekton-message-type: subscribe
            ws.send(JSON.stringify({
                type: 'subscribe',
                channels: ['entity-updates', 'relationship-updates']
            }));
        };
        
        // @tekton-event-handler: Message received
        // @tekton-message-types: entity-created, entity-updated, entity-deleted
        // @tekton-updates: entity-list, entity-details
        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            
            // @tekton-message-routing: Route by message type
            switch(message.type) {
                case 'entity-created':
                    handleEntityCreated(message.data);
                    break;
                case 'entity-updated':
                    handleEntityUpdated(message.data);
                    break;
                case 'entity-deleted':
                    handleEntityDeleted(message.data);
                    break;
            }
        };
        
        // @tekton-event-handler: Connection error
        // @tekton-error-recovery: exponential-backoff-reconnect
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
            state.connected = false;
            updateConnectionStatus('error');
            
            // @tekton-retry: Exponential backoff
            setTimeout(connectWebSocket, Math.min(state.retryCount * 1000, 30000));
            state.retryCount++;
        };
        
        return ws;
    }
    
    // @tekton-function: Setup DOM event handlers
    // @tekton-pattern: Event delegation
    // @tekton-events: click, submit, input
    function setupEventHandlers() {
        // @tekton-event-delegation: Component root
        const component = document.querySelector('[data-tekton-component="athena"]');
        
        // @tekton-event: Click handler for actions
        // @tekton-delegates-to: data-tekton-action
        component.addEventListener('click', function(event) {
            const action = event.target.closest('[data-tekton-action]');
            if (action) {
                const actionName = action.getAttribute('data-tekton-action');
                handleAction(actionName, action, event);
            }
        });
        
        // @tekton-event: Form submission
        // @tekton-prevents-default: true
        // @tekton-validates: true
        component.addEventListener('submit', function(event) {
            const form = event.target.closest('[data-tekton-form]');
            if (form) {
                event.preventDefault();
                handleFormSubmit(form);
            }
        });
        
        // @tekton-event: Input changes
        // @tekton-debounce: 300ms
        // @tekton-updates: search-results
        let debounceTimer;
        component.addEventListener('input', function(event) {
            const input = event.target.closest('[data-tekton-input]');
            if (input) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    handleInputChange(input);
                }, 300);
            }
        });
    }
    
    // @tekton-function: Handle entity search
    // @tekton-api-call: GET /api/knowledge/entities/search
    // @tekton-updates: entity-results
    // @tekton-error-display: inline
    async function searchEntities(query) {
        // @tekton-validation: Minimum query length
        if (query.length < 2) {
            clearSearchResults();
            return;
        }
        
        // @tekton-loading-state: Show loading indicator
        showLoadingIndicator('entity-results');
        
        try {
            // @tekton-api-request: Search entities
            // @tekton-timeout: 5s
            // @tekton-retry: 1
            const response = await fetch(
                `${config.apiBaseUrl}/entities/search?query=${encodeURIComponent(query)}`,
                {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error(`Search failed: ${response.statusText}`);
            }
            
            const entities = await response.json();
            
            // @tekton-dom-update: Render search results
            // @tekton-template: entity-result-template
            renderSearchResults(entities);
            
        } catch (error) {
            // @tekton-error-handling: Display user-friendly error
            // @tekton-dom-target: [data-tekton-results="entity-search"]
            displayError('entity-results', 'Search failed. Please try again.');
            console.error('Entity search error:', error);
        } finally {
            // @tekton-cleanup: Hide loading indicator
            hideLoadingIndicator('entity-results');
        }
    }
    
    // @tekton-function: Update entity display
    // @tekton-dom-modifies: [data-tekton-entity-display]
    // @tekton-animation: fade-in
    function updateEntityDisplay(entity) {
        // @tekton-dom-query: Entity display container
        const display = document.querySelector('[data-tekton-entity-display]');
        if (!display) return;
        
        // @tekton-template: Entity details template
        // @tekton-sanitization: html-escape
        const html = `
            <div class="athena__entity-details">
                <h3>${escapeHtml(entity.name)}</h3>
                <div class="athena__entity-type">${entity.entity_type}</div>
                <div class="athena__entity-properties">
                    ${Object.entries(entity.properties).map(([key, value]) => `
                        <div class="athena__property">
                            <span class="athena__property-key">${escapeHtml(key)}:</span>
                            <span class="athena__property-value">${escapeHtml(String(value))}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // @tekton-dom-update: With animation
        display.style.opacity = '0';
        display.innerHTML = html;
        
        // @tekton-animation: Fade in
        requestAnimationFrame(() => {
            display.style.transition = 'opacity 0.3s';
            display.style.opacity = '1';
        });
    }
    
    // @tekton-public-api: Exposed methods
    // @tekton-returns: Public interface object
    return {
        initialize: initialize,
        searchEntities: searchEntities,
        getState: () => Object.freeze({...state}),
        refresh: loadInitialData
    };
    
})();

// @tekton-initialization: Auto-initialize on DOM ready
// @tekton-timing: DOMContentLoaded
// @tekton-condition: Component exists in DOM
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('[data-tekton-component="athena"]')) {
        AthenaUI.initialize();
    }
});
```

## Configuration Files

### Environment Configuration

```bash
# @tekton-config: Athena component configuration
# @tekton-environment: development
# @tekton-overrides: ~/.env.tekton, system environment
# @tekton-validation: required-fields

# @tekton-section: Service configuration
# @tekton-var: Service port
# @tekton-type: integer
# @tekton-range: 8000-9000
# @tekton-default: 8010
ATHENA_PORT=8010

# @tekton-var: Service host binding
# @tekton-type: hostname
# @tekton-default: 0.0.0.0
ATHENA_HOST=0.0.0.0

# @tekton-section: Database configuration
# @tekton-var: Neo4j connection URI
# @tekton-type: uri
# @tekton-required: true
# @tekton-format: bolt://host:port
NEO4J_URI=bolt://localhost:7687

# @tekton-var: Neo4j username
# @tekton-type: string
# @tekton-secret: true
NEO4J_USER=neo4j

# @tekton-var: Neo4j password
# @tekton-type: string
# @tekton-secret: true
# @tekton-validation: min-length:8
NEO4J_PASSWORD=your-secure-password

# @tekton-section: Integration endpoints
# @tekton-var: Hermes WebSocket URL
# @tekton-type: url
# @tekton-protocol: ws
# @tekton-health-check: true
HERMES_WS_URL=ws://localhost:8001/ws

# @tekton-section: Performance tuning
# @tekton-var: Cache TTL in seconds
# @tekton-type: integer
# @tekton-unit: seconds
# @tekton-default: 300
CACHE_TTL=300

# @tekton-var: Maximum concurrent connections
# @tekton-type: integer
# @tekton-range: 1-1000
# @tekton-affects: connection-pool
MAX_CONNECTIONS=100
```

### Docker Configuration

```dockerfile
# @tekton-dockerfile: Athena component container
# @tekton-base-image: python:3.11-slim
# @tekton-size-estimate: 150MB
# @tekton-build-time: 2-3 minutes

FROM python:3.11-slim

# @tekton-metadata: Container labels
# @tekton-maintainer: Tekton Team
LABEL component="athena" \
      version="1.0.0" \
      description="Knowledge graph component"

# @tekton-stage: Install system dependencies
# @tekton-packages: Required for neo4j driver
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# @tekton-stage: Setup application directory
# @tekton-directory: Application root
WORKDIR /app

# @tekton-stage: Install Python dependencies
# @tekton-cache-mount: pip cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# @tekton-stage: Copy application code
# @tekton-excludes: __pycache__, .env, tests
COPY athena/ ./athena/
COPY ui/ ./ui/

# @tekton-configuration: Runtime settings
# @tekton-env-requires: ATHENA_PORT, NEO4J_URI
ENV PYTHONUNBUFFERED=1 \
    ATHENA_HOST=0.0.0.0

# @tekton-networking: Exposed ports
# @tekton-port-purpose: HTTP API
EXPOSE 8010

# @tekton-health-check: Container health monitoring
# @tekton-interval: 30s
# @tekton-timeout: 3s
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import httpx; httpx.get('http://localhost:8010/health')"

# @tekton-entrypoint: Start application
# @tekton-signal-handling: SIGTERM, SIGINT
CMD ["python", "-m", "athena"]
```

## Testing Files

### Test Module Example

```python
# @tekton-test-module: Athena entity tests
# @tekton-test-type: unit
# @tekton-coverage-target: 80%
# @tekton-depends: pytest, pytest-asyncio, pytest-mock

"""
Unit tests for Athena entity management.

@tekton-test-categories: entity-crud, validation, error-handling
@tekton-fixtures: mock-database, test-entities
"""

import pytest
from unittest.mock import Mock, AsyncMock

# @tekton-import-under-test: Entity model and service
from athena.core.entity import Entity
from athena.services.entity_service import EntityService

# @tekton-fixture: Mock database session
# @tekton-scope: function
# @tekton-provides: Mocked Neo4j session
@pytest.fixture
async def mock_session():
    """Provide mocked database session."""
    session = AsyncMock()
    session.run = AsyncMock()
    return session

# @tekton-fixture: Test entities
# @tekton-scope: module
# @tekton-data-set: Standard test entities
@pytest.fixture
def test_entities():
    """Standard test entity dataset."""
    return [
        Entity(entity_type="person", name="John Doe"),
        Entity(entity_type="concept", name="Machine Learning"),
        Entity(entity_type="organization", name="Tekton Corp")
    ]

# @tekton-test-class: Entity CRUD operations
# @tekton-test-focus: Happy path and edge cases
class TestEntityOperations:
    """Test entity CRUD operations."""
    
    # @tekton-test: Create entity successfully
    # @tekton-validates: Entity creation with all fields
    # @tekton-expected-behavior: Returns entity ID
    @pytest.mark.asyncio
    async def test_create_entity_success(self, mock_session):
        """Test successful entity creation."""
        # @tekton-arrange: Setup service and entity
        service = EntityService(mock_session)
        entity = Entity(
            entity_type="person",
            name="Test Person",
            properties={"role": "developer"}
        )
        
        # @tekton-mock-setup: Configure expected behavior
        mock_session.run.return_value = AsyncMock(
            single=AsyncMock(return_value={"id": "12345"})
        )
        
        # @tekton-act: Create entity
        entity_id = await service.create_entity(entity)
        
        # @tekton-assert: Verify creation
        assert entity_id == "12345"
        mock_session.run.assert_called_once()
        
        # @tekton-assert: Verify query parameters
        call_args = mock_session.run.call_args[0]
        assert "CREATE" in call_args[0]
        assert entity.name in str(call_args[1])
    
    # @tekton-test: Handle duplicate entity
    # @tekton-validates: Duplicate detection
    # @tekton-expected-behavior: Raises DuplicateEntityError
    @pytest.mark.asyncio
    async def test_create_duplicate_entity(self, mock_session):
        """Test duplicate entity handling."""
        # @tekton-arrange: Setup duplicate scenario
        service = EntityService(mock_session)
        entity = Entity(entity_type="person", name="Existing Person")
        
        # @tekton-mock-setup: Simulate constraint violation
        mock_session.run.side_effect = ConstraintError("already exists")
        
        # @tekton-act-assert: Expect specific exception
        with pytest.raises(DuplicateEntityError) as exc_info:
            await service.create_entity(entity)
        
        # @tekton-assert: Verify error details
        assert "already exists" in str(exc_info.value)
        assert exc_info.value.entity_name == "Existing Person"

# @tekton-test-class: Entity search functionality
# @tekton-performance-tests: included
class TestEntitySearch:
    """Test entity search operations."""
    
    # @tekton-test: Search performance
    # @tekton-performance-requirement: <100ms for 1000 entities
    # @tekton-test-data-size: 1000 entities
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_search_performance(self, mock_session, benchmark):
        """Test search performance with large dataset."""
        # @tekton-arrange: Large dataset
        service = EntityService(mock_session)
        
        # @tekton-mock-setup: Return 1000 entities
        mock_results = [
            {"e": {"name": f"Entity {i}", "entity_type": "test"}}
            for i in range(1000)
        ]
        mock_session.run.return_value = AsyncMock(
            __aiter__=lambda self: iter(mock_results)
        )
        
        # @tekton-act: Benchmark search
        result = await benchmark(
            service.search_entities,
            query="Entity",
            limit=1000
        )
        
        # @tekton-assert: Performance and correctness
        assert len(result) == 1000
        assert benchmark.stats["mean"] < 0.1  # 100ms
```

## Knowledge Graph Metadata Examples

### Graph-Ready Python Module

```python
# @tekton-module: Recommendation Engine
# @tekton-graph-entity: Service
# @tekton-graph-properties: {
#   "name": "RecommendationEngine",
#   "type": "ml-service",
#   "version": "2.0.0",
#   "status": "production"
# }
# @tekton-graph-relationships: [
#   {"type": "DEPENDS_ON", "target": "AthenaService", "properties": {"api": "entity-search"}},
#   {"type": "DEPENDS_ON", "target": "UserProfileService", "properties": {"api": "get-preferences"}},
#   {"type": "PROVIDES", "target": "API", "properties": {"endpoint": "/recommendations"}}
# ]

class RecommendationEngine:
    """
    ML-powered recommendation engine.
    
    @tekton-ml-model: collaborative-filtering
    @tekton-training-frequency: daily
    @tekton-inference-latency: <50ms
    """
    
    # @tekton-graph-method: Core recommendation algorithm
    # @tekton-graph-properties: {
    #   "algorithm": "matrix-factorization",
    #   "complexity": "O(n*m*k)",
    #   "accuracy": "0.92"
    # }
    async def get_recommendations(self, user_id: str, limit: int = 10):
        """Generate personalized recommendations."""
        pass
```

### Graph-Ready HTML Component

```html
<!-- @tekton-graph-entity: UIComponent -->
<!-- @tekton-graph-properties: {
  "name": "RecommendationPanel",
  "type": "ui-widget",
  "framework": "vanilla-js",
  "responsive": true
} -->
<!-- @tekton-graph-relationships: [
  {"type": "DISPLAYS_DATA_FROM", "target": "RecommendationEngine"},
  {"type": "SENDS_EVENTS_TO", "target": "AnalyticsService"},
  {"type": "PART_OF", "target": "AthenaUI"}
] -->
<div class="recommendations-panel"
     data-tekton-component="recommendations"
     data-tekton-graph-node="true"
     data-tekton-consumes="recommendation-api"
     data-tekton-emits="recommendation-clicked,recommendation-dismissed">
    <!-- Component content -->
</div>
```

## Best Practices Summary

1. **Always instrument as you code** - Don't wait until later
2. **Use consistent prefixes** - `@tekton-` for code, `data-tekton-` for HTML
3. **Include relationships** - Document what depends on what
4. **Add semantic meaning** - Not just what, but why and how
5. **Think graph structure** - How will this be queried later?
6. **Update on changes** - Keep metadata in sync with code
7. **Version important changes** - Track evolution over time
8. **Document side effects** - What else does this code affect?
9. **Include performance hints** - Expected latency, complexity
10. **Mark critical paths** - What's essential vs optional?