# Athena Component Renovation Plan

## Overview
Renovate the Athena (Knowledge Weaver) component following the successful Apollo pattern, adapting for Athena's knowledge graph functionality.

## Current State Assessment

### UI Structure
- **5 Tabs**: Knowledge Graph, Entities, Query Builder, Knowledge Chat, Team Chat
- **BEM Naming**: Uses `.athena__*` convention throughout
- **onclick handlers**: Need conversion to event listeners
- **Mock Data**: Sample entities shown in UI
- **Dual Chat**: Knowledge Chat + Team Chat functionality

### Backend
- **Port**: Configured via GlobalConfig (typically 8007)
- **API**: Full REST API at `/api/v1/`
- **Endpoints**: entities, knowledge, query, visualization
- **Status**: Backend appears properly implemented

## Renovation Tasks

### Phase 1: UI Modernization

#### 1. CSS-First Navigation
- [ ] Add hidden radio inputs for tab control
- [ ] Convert tab divs to labels
- [ ] Update CSS for :checked state handling
- [ ] Remove onclick="athena_switchTab()"

#### 2. Real Data Integration
- [ ] Create athena-service.js for API calls
- [ ] Replace mock entities with API data
- [ ] Connect Knowledge Graph to visualization API
- [ ] Implement Query Builder with real search
- [ ] Add loading states and error handling

#### 3. Chat Implementation
- [ ] Fix chat input lookup (same bug as Apollo)
- [ ] Add window.AIChat integration
- [ ] Update chat styling to match Athena's purple theme
- [ ] Implement immediate event handler setup

#### 4. Visual Enhancements
- [ ] Ensure purple color scheme consistency
- [ ] Add component-specific styling
- [ ] Update entity type icons
- [ ] Polish graph visualization

### Phase 2: Backend Verification
- [ ] Check for os.getenv usage
- [ ] Verify GlobalConfig usage
- [ ] Ensure proper error handling
- [ ] Test all API endpoints

## Key Differences from Apollo

1. **More Complex Data**: Entities with types, properties, relationships
2. **Graph Visualization**: Need to handle D3.js or similar
3. **Query Builder**: Complex search interface
4. **Knowledge vs Team Chat**: Two distinct chat modes
5. **BEM Naming**: More structured CSS classes

## API Endpoints to Implement

```javascript
// athena-service.js structure
const ATHENA_API = {
    // Entity management
    getEntities: () => GET `/api/v1/entities`,
    createEntity: (data) => POST `/api/v1/entities`,
    updateEntity: (id, data) => PUT `/api/v1/entities/${id}`,
    deleteEntity: (id) => DELETE `/api/v1/entities/${id}`,
    
    // Knowledge operations
    getKnowledge: () => GET `/api/v1/knowledge`,
    searchEntities: (query) => POST `/api/v1/query/search`,
    getGraphData: () => GET `/api/v1/visualization/graph`,
    
    // Chat/LLM
    askQuestion: (question) => POST `/api/v1/llm/ask`
};
```

## Success Criteria

1. All tabs load real data from Athena backend
2. No onclick handlers remain
3. Chat works with window.AIChat
4. Maintains Athena's purple theme identity
5. Knowledge graph visualization works
6. Query builder returns real results

## Notes

- Athena is more data-heavy than Apollo
- Graph visualization may need special handling
- Entity management is core functionality
- Keep the elegant BEM structure while modernizing

Ready to begin renovation following the proven Apollo pattern!