# Athena Renovation Sprint - Initial Context

## Component Overview
Athena is the Knowledge Graph component in Tekton, responsible for:
- Knowledge graph visualization and management
- Entity tracking and relationships
- Query building for graph exploration
- Knowledge chat for AI-powered insights
- Team coordination through chat

## Current State (as of 2025-01-20)
- **UI Pattern**: Uses old JavaScript onclick handlers for tabs (lines 17-31)
- **Location**: `/Hephaestus/ui/components/athena/athena-component.html`
- **Backend Port**: 8105 (from env.js)
- **Health Check**: Should be working (glowing nav dots indicate healthy backend)

## Key Migration Points

### 1. CSS-First Tab Navigation
Athena currently has 5 tabs using onclick handlers:
- Knowledge Graph (line 17: `onclick="athena_switchTab('graph');"`)
- Entities (line 20: `onclick="athena_switchTab('entities');"`)
- Query Builder (line 23: `onclick="athena_switchTab('query');"`)
- Knowledge Chat (line 26: `onclick="athena_switchTab('chat');"`)
- Team Chat (line 29: `onclick="athena_switchTab('teamchat');"`)

These need conversion to radio button pattern like Apollo.

### 2. JavaScript Functions to Replace
- `athena_switchTab()` (lines 790-860) - Replace with CSS
- `athena_clearChat()` (lines 862-898, 1067-1083) - Keep but simplify
- `athena_sendChat()` (lines 998-1065) - Keep for chat functionality

### 3. Known Integration Points
- Uses aish MCP for AI communication (window.AIChat calls)
- Should connect to `http://localhost:8105/api/*` endpoints
- Team Chat functionality uses aish MCP `/tools/team-chat`
- Knowledge chat sends direct messages to 'athena' AI

### 4. Mock Data to Remove
Need to identify and catalog during Phase 1 assessment:
- Sample entities (lines 94-119) - hardcoded UI test data
- Graph placeholder (lines 63-68) - needs real graph visualization
- Entity type filters - verify if backend supports these

### 5. CSS Classes Already Present
- Component follows BEM naming convention (athena__)
- Has comprehensive styling (lines 246-776)
- Includes chat message styling patterns from Numa

## Success Metrics for Athena
1. All tabs use CSS-first navigation (no JavaScript onclick)
2. All data comes from real Athena backend at port 8105
3. Knowledge Graph shows real entity relationships
4. Team Chat uses aish MCP server
5. Entity management connected to real backend
6. Query builder generates and executes real queries

## First Steps
1. Run Athena and document current functionality
2. Test backend endpoints at port 8105
3. Catalog all mock data instances
4. Document current tab switching behavior
5. Check if graph visualization library is loaded

## Reference Patterns
- **CSS-First Tabs**: Use Apollo's radio button pattern
- **Port Configuration**: Use `window.ATHENA_PORT` from env.js
- **URL Building**: Use `tekton_url('athena', '/api/endpoint')`
- **MCP Integration**: Use aish MCP at port 8118
- **Chat Pattern**: Follow Numa's message styling

## Special Considerations
1. **Graph Visualization**: May need to verify/install graph library
2. **Query Builder**: Complex form that needs backend API design
3. **Entity Management**: CRUD operations need proper error handling
4. **Protected HTML Panel**: Lines 933-979 have complex protection logic

Remember Casey's philosophy: "Simple, works, hard to screw up"