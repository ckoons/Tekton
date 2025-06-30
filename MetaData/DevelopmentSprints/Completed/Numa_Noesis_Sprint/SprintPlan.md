# Numa and Noesis Sprint Plan

## Sprint Goal

Implement Numa (Platform AI Mentor) and Noesis (Discovery System) as fully integrated Tekton components with proper UI, registration, and configuration management.

## Sprint Scope

### In Scope
- Basic FastAPI applications for both components
- UI components following Rhetor's pattern
- Hermes registration and health checks
- Environment configuration (no hardcoded ports)
- Placeholder chat functionality
- Dark theme UI styling

### Out of Scope
- Actual AI specialist implementation (TEKTON_REGISTER_AI=false)
- Complex discovery algorithms for Noesis
- Full mentoring logic for Numa
- Database integration

## Success Criteria

1. Both components launch successfully from enhanced_tekton_launcher
2. Components register with Hermes and show green status
3. UI displays correctly with dark theme matching Rhetor
4. Numa appears as default component on UI load
5. Chat interfaces are functional (placeholder responses)
6. No hardcoded configuration values

## Technical Approach

1. **Backend**: FastAPI following Rhetor's pattern
2. **UI**: BEM CSS with radio button tab switching
3. **Configuration**: Using shared env_config.py
4. **Registration**: Hermes REST API integration
5. **Styling**: CSS variables matching Rhetor's theme

## Risk Mitigation

- **Risk**: UI component loading conflicts
  - **Mitigation**: Follow minimal-loader.js pattern exactly
  
- **Risk**: Port conflicts
  - **Mitigation**: Use env_config.py, no defaults

- **Risk**: Registration failures
  - **Mitigation**: Match Hermes API expectations precisely