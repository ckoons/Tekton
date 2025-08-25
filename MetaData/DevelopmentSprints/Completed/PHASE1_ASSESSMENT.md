# Apollo Phase 1: Assessment Report

## Component Location
- Frontend: `/Hephaestus/ui/components/apollo/apollo-component.html`
- Backend: `/Apollo/apollo/`
- Component runs on port: 8112

## Current State (2025-07-20)

### Backend Status
- Health endpoint working: `http://localhost:8112/health`
- Component status: Healthy
- Registered with Hermes: Yes
- Version: 0.1.0

### Frontend Analysis

#### Tab Navigation
All 8 tabs use onclick handlers that need CSS-first conversion:
1. Dashboard - `onclick="apollo_switchTab('dashboard')"`
2. Sessions - `onclick="apollo_switchTab('sessions')"`
3. Token Budgets - `onclick="apollo_switchTab('tokens')"`
4. Protocols - `onclick="apollo_switchTab('protocols')"`
5. Forecasting - `onclick="apollo_switchTab('forecasting')"`
6. Actions - `onclick="apollo_switchTab('actions')"`
7. Attention Chat - `onclick="apollo_switchTab('attention')"`
8. Team Chat - `onclick="apollo_switchTab('teamchat')"`

Additional onclick handlers:
- Clear button: `onclick="apollo_clearChat()"`
- Send button: `onclick="apollo_sendChat()"`

#### Mock Data Found

##### Dashboard Tab
- **Active Sessions Count**: Hardcoded as "4"
- **Total Tokens**: Hardcoded as "102,536"
- **Token Usage**: Hardcoded percentages (38.4%)
- **System Status**: Static "All LLM systems operational"
- **Session List**: Hardcoded sessions (Codex, Athena, Rhetor, Engram) with fake health states

##### Sessions Tab
- Hardcoded session cards with mock data:
  - Model names (claude-3-opus)
  - Token usage (12,420 / 30,000)
  - Health scores (98%)
  - Last active times

### API Issues Found

1. **Double API Prefix**: Routes are mounted incorrectly resulting in `/api/v1/api/...` instead of `/api/v1/...`
   - Found in: `/Apollo/apollo/api/app.py` line 204
   - Routes include: `app.include_router(api_router, prefix="/api/v1")`
   - But api_router already has prefix="/api" causing double prefix

2. **Hardcoded URLs**: Frontend likely uses hardcoded localhost URLs instead of `tekton_url()`

### Code Quality Issues

#### Frontend
- Large monolithic HTML file (4000+ lines)
- Inline JavaScript at bottom of HTML
- No proper separation of concerns
- Mock data embedded directly in HTML

#### Backend  
- Need to verify if using TektonEnviron vs os.environ
- Check for hardcoded ports/URLs
- API route structure needs fixing

### Test Coverage
- Tests exist in `/Apollo/tests/` but coverage unknown
- Need to run: `pytest tests/apollo/ -v`

## Identified Tasks for Renovation

### Phase 1 Priority (Assessment)
- [x] Document all mock data locations
- [x] Identify all onclick handlers
- [x] Find API routing issues
- [ ] Run existing tests to check coverage
- [ ] Test each API endpoint

### Phase 2 Priority (Code Standards)
- [ ] Fix API double prefix issue
- [ ] Replace hardcoded values with TektonEnviron
- [ ] Remove unused imports/functions
- [ ] Fix linting issues

### Phase 3 Priority (Backend)
- [ ] Fix API routes structure
- [ ] Connect real data endpoints
- [ ] Remove mock endpoints
- [ ] Integrate with aish MCP

### Phase 4 Priority (Frontend)
- [ ] Convert Dashboard tab to CSS-first (proof of concept)
- [ ] Remove all mock data from HTML
- [ ] Connect to real API endpoints
- [ ] Add proper loading/error states
- [ ] Convert remaining 7 tabs to CSS-first

### Phase 5 Priority (Testing)
- [ ] Write missing tests
- [ ] Update documentation
- [ ] Full integration testing

## Next Steps
1. Fix the API routing issue first (quick win)
2. Convert Dashboard tab to CSS-first pattern as proof of concept
3. Connect Dashboard to real backend data
4. Apply pattern to remaining tabs

## Questions for Casey/Team
1. Should Apollo actually track other Tekton components' sessions or its own internal sessions?
2. What real data should the Token Budget display - actual CI API usage?
3. For Team Chat - should this connect to aish MCP at port 8118?