# Hermes Renovation Quick Reference

## Component Stats
- **Location**: `/Hephaestus/ui/components/hermes/hermes-component.html`
- **Tabs**: 6 (Registry, Messaging, Connections, History, Chat, Team Chat)
- **Onclick Handlers**: 9 total
- **Lines of Code**: ~1512
- **Primary Color**: Blue (#4285F4)

## Priority Tasks

### 1. Remove Onclick Handlers
- [ ] Line 27: Registry tab
- [ ] Line 36: Messaging tab  
- [ ] Line 45: Connections tab
- [ ] Line 54: History tab
- [ ] Line 63: Chat tab
- [ ] Line 72: Team Chat tab
- [ ] Line 80: Clear button
- [ ] Line 402: Chat input keydown
- [ ] Line 403: Send button

### 2. Mock Data to Replace
- [ ] Service registry loading placeholder
- [ ] Message monitor placeholder
- [ ] Component filters loading
- [ ] Connection graph loading
- [ ] History table (empty)

### 3. Backend Endpoints Needed
- `/api/hermes/registry` - Service list
- `/api/hermes/messages` - Message stream
- `/api/hermes/connections` - Connection data
- `/api/hermes/history` - Message history
- `/api/hermes/chat` - CI chat (via aish MCP)

## CSS-First Pattern
```html
<!-- Radio inputs at top -->
<input type="radio" name="hermes-tabs" id="hermes-tab-[name]" class="hermes__tab-input">

<!-- Labels as tabs -->
<label for="hermes-tab-[name]" class="hermes__tab">

<!-- CSS controls visibility -->
#hermes-tab-[name]:checked ~ .hermes__content #[name]-panel { display: block; }
```

## Key Functions to Preserve
- `hermes_sendChat()` - Keep but remove inline
- `hermes_clearChat()` - Keep but remove inline
- Message real-time updates
- Service registry refresh
- Filter functionality

## Testing Priority
1. Tab switching works
2. Service registry shows real components
3. Chat sends/receives messages
4. Message monitor updates
5. Filters work correctly

## Dependencies
- Hermes backend running on port 8020
- aish MCP for CI features
- Other Tekton components for registry
- WebSocket for real-time messages

## Common Issues to Watch
1. HTML panel protection code
2. Complex tab switching logic
3. Real-time update mechanisms
4. Modal dialog handling
5. Multiple view states (grid/list)