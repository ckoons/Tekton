# Hermes Component Preliminary Analysis

## Component Overview
Hermes is the inter-component messaging and data routing hub for Tekton. It provides service registry, message monitoring, connection visualization, and chat interfaces.

## Current State Assessment

### UI Structure
- **6 Main Tabs**: Service Registry, Message Monitor, Connections, Message History, Message/Data Chat, Team Chat
- **Complex Layout**: Sidebar filters, grid/list views, modal dialogs
- **Chat Integration**: Two separate chat interfaces (component-specific and team-wide)

### JavaScript Dependencies
1. **Tab Switching**: `hermes_switchTab()` function with onclick handlers
2. **Chat Functions**: `hermes_sendChat()` and `hermes_clearChat()`
3. **View Toggle**: Grid/List view switching in registry
4. **Modal Handling**: Component detail modals
5. **Filter Management**: Message type and component filters

### Onclick Handlers Found
1. Registry tab - line 27: `onclick="hermes_switchTab('registry'); return false;"`
2. Messaging tab - line 36: `onclick="hermes_switchTab('messaging'); return false;"`
3. Connections tab - line 45: `onclick="hermes_switchTab('connections'); return false;"`
4. History tab - line 54: `onclick="hermes_switchTab('history'); return false;"`
5. Chat tab - line 63: `onclick="hermes_switchTab('chat'); return false;"`
6. Team Chat tab - line 72: `onclick="hermes_switchTab('teamchat'); return false;"`
7. Clear button - line 80: `onclick="hermes_clearChat(); return false;"`
8. Chat input - line 402: `onkeydown="if(event.key === 'Enter'..."`
9. Send button - line 403: `onclick="hermes_sendChat(); return false;"`

### Mock Data Locations
1. Service Registry - line 133-135: "Loading services..." placeholder
2. Message Monitor - line 224-226: Placeholder message
3. Component filters - line 214-216: "Loading components..."
4. Connection graph - line 261: "Loading connection graph..."
5. Connection details - line 267: "Select a connection to view details"
6. History table - line 342: Empty tbody for dynamic content

### CSS-First Conversion Strategy
1. **Radio Input Pattern**: Add 6 hidden radio inputs for tab state
2. **Label Triggers**: Convert tab divs to labels
3. **CSS State Management**: Use `:checked` pseudo-class
4. **Panel Visibility**: Control with CSS sibling selectors
5. **Active Styling**: CSS-based active states
6. **Preserve Functionality**: Keep chat and data features intact

### Backend Integration Points
1. `/api/hermes/registry` - Service registry data
2. `/api/hermes/messages` - Real-time message stream
3. `/api/hermes/connections` - Connection graph data
4. `/api/hermes/history` - Message history queries
5. `/api/hermes/chat` - AI chat endpoint (to be routed through aish MCP)

### Unique Challenges
1. **Real-time Updates**: Message monitoring needs WebSocket or SSE
2. **Graph Visualization**: Connection graph requires D3.js or similar
3. **Multi-view Support**: Grid/List toggle in registry
4. **Complex Filters**: Multiple filter types across different tabs
5. **Dual Chat System**: Component chat vs team chat
6. **Service Discovery**: Must show real Tekton services

### Priority Items
1. Remove all onclick handlers (9 total)
2. Implement CSS-first tab system
3. Connect to real Hermes backend API
4. Remove mock data placeholders
5. Integrate with aish MCP for AI features
6. Ensure message bus is actually working
7. Test service registry with live components

### Dependencies
- Hermes backend must be running
- Service registry API must be functional
- Message bus must be active
- Other Tekton components for testing
- aish MCP for AI integration

## Recommendations
1. Start with tab conversion (most visible change)
2. Test incrementally - each tab separately
3. Preserve existing chat functionality during conversion
4. Add real-time message updates last (most complex)
5. Consider using CSS Grid for registry layout
6. Keep modal functionality but convert triggers