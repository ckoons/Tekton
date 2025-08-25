# Apollo Renovation Sprint - Initial Context

## Component Overview
Apollo is the Attention/Prediction component in Tekton, responsible for:
- Session management and attention tracking
- Token budget monitoring
- Protocol management
- Forecasting capabilities
- Team coordination through chat

## Current State (as of 2025-01-20)
- **UI Pattern**: Uses old JavaScript onclick handlers for tabs
- **Location**: `/Hephaestus/ui/components/apollo/apollo-component.html`
- **Backend Port**: 8112 (from env.js)
- **Health Check**: Working (verified with glowing nav dots)

## Key Migration Points

### 1. CSS-First Tab Navigation
Apollo currently has 8 tabs using onclick handlers:
- Dashboard
- Sessions  
- Token Budgets
- Protocols
- Forecasting
- Actions
- Attention Chat
- Team Chat

These need conversion to radio button pattern like Settings component.

### 2. Known Integration Points
- Uses aish MCP for CI communication (needs verification)
- Should connect to `http://localhost:8112/api/*` endpoints
- Team Chat functionality should use aish MCP `/tools/team-chat`

### 3. Mock Data to Remove
Need to identify and catalog during Phase 1 assessment:
- Session data (likely mocked)
- Token budget displays
- Protocol listings
- Forecasting charts

## Success Metrics for Apollo
1. All tabs use CSS-first navigation (no JavaScript switching)
2. All data comes from real Apollo backend at port 8112
3. Team Chat uses aish MCP server
4. Maintains current functionality while following new patterns

## First Steps
1. Copy the template sprint directory
2. Run Apollo and document current functionality
3. Catalog all mock data instances
4. Create inventory of onclick handlers to replace
5. Test existing Apollo backend endpoints

## Reference Patterns
- **CSS-First Tabs**: See `/components/settings/settings-component.html`
- **Port Configuration**: Use `window.APOLLO_PORT` from env.js
- **URL Building**: Use `tekton_url('apollo', '/api/endpoint')`
- **MCP Integration**: Use aish MCP at port 8118

Remember Casey's philosophy: "Simple, works, hard to screw up"