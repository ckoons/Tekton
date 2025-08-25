# Claude Code Implementation Prompt - CI Platform Integration Sprint

## Initial Context for Claude

Hello Claude! You'll be implementing the CI Platform Integration Sprint for Tekton. This sprint adds CI specialists to each component and introduces Numa as the platform-wide CI mentor.

## Project Background

Tekton is a Multi-AI Engineering Platform with these goals:
- AI-enabled software engineering
- CI cognition research with computational spectral analysis
- Structured memory and latent-space exploration
- CI behavior and personality development within a community

The platform consists of multiple components (Rhetor, Apollo, Athena, etc.) that communicate via a socket registry. We're now adding CI specialists to create a collaborative CI ecosystem.

## Sprint Objectives

You'll be implementing:

1. **AI Management Utilities** - Tools to launch, monitor, and terminate CI processes
2. **Numa Component** - Platform-wide CI mentor with access to all components
3. **Noesis Component** - Discovery CI (placeholder for future sprint)
4. **Integration Updates** - Modify existing tools to manage CI lifecycle
5. **Health Monitoring** - Detect and recover unresponsive CIs

## Key Architectural Decisions

### Process Model
- Each CI runs as an **independent process** (not threads)
- Communication via the existing **socket registry**
- CIs are peers, not supervisors

### Environment Control
```bash
export TEKTON_REGISTER_AI=true   # Enable CI lifecycle
export TEKTON_REGISTER_AI=false  # Disable for development
```

### Numa's Special Role
- Launches **after** all components are healthy
- Terminates **before** any component shuts down
- Has read access to all component sockets
- Serves as a mentor/coach, not a boss

### Health Monitoring
- Track "last spoke" timestamps
- After 5 minutes of silence, send ESC character
- Auto-restart if unresponsive

## Implementation Guidelines

### Phase 1: Start with Foundations
1. Read the existing sprint documentation in `/MetaData/DevelopmentSprints/AI_Platform_Integration_Sprint/`
2. Create the CI registry client first (shared infrastructure)
3. Build management utilities (launcher, killer, status)
4. Test thoroughly before moving to next phase

### Phase 2: Component Creation
1. Build Numa with basic FastAPI structure
2. Include health endpoints and Hermes registration
3. Create placeholder Noesis component
4. Ensure both register with socket registry

### Phase 3: Integration
1. Update Enhanced Tekton tools carefully
2. Maintain backward compatibility
3. Test with TEKTON_REGISTER_AI=false first
4. Gradually enable CI features

### Phase 4: CI Implementation
1. Create base AISpecialistWorker class
2. Implement socket polling loop
3. Integrate with Claude API (use claude-3-5-sonnet-20241022)
4. Add personality prompts for each AI

## Code Style Guidelines

### Python Standards
- Use async/await for all I/O operations
- Type hints for all function parameters
- Comprehensive error handling
- Clear logging at each step

### File Organization
```
EnhancedTools/
  tekton_ai_launcher.py
  tekton_ai_killer.py
  tekton_ai_status.py
  
shared_lib/
  AIRegistryClient.py
  AISpecialistWorker.py
  
Numa/
  main.py
  numa_ai.py
  static/
    numa_chat.html
```

### Error Handling
- Never let an CI crash take down a component
- Always deregister CIs on shutdown
- Log all errors with context
- Graceful degradation when CI unavailable

## Testing Requirements

### Unit Tests
- Test each utility independently
- Mock socket registry calls
- Verify error handling

### Integration Tests
- Full startup/shutdown cycles
- Component restart scenarios
- CI crash recovery
- Team chat functionality

## Important Warnings

### DO NOT:
- Create CIs as threads within components
- Give CIs write access to component code
- Allow CIs to restart components directly
- Skip the health monitoring implementation
- Forget to handle the shutdown sequence

### DO:
- Keep CI processes completely independent
- Use the socket registry for all communication
- Implement comprehensive logging
- Test with TEKTON_REGISTER_AI=false first
- Document any deviations from the plan

## Success Criteria

Your implementation is complete when:

1. ✓ `tekton_ai_launcher.py` starts all registered CIs
2. ✓ `tekton_ai_killer.py` cleanly terminates all CIs
3. ✓ `tekton_ai_status.py` shows health of all CIs
4. ✓ Numa launches after components, terminates first
5. ✓ Health monitoring detects unresponsive CIs
6. ✓ Team chat works with multiple CI participants
7. ✓ All changes respect TEKTON_REGISTER_AI flag

## Getting Started

1. First, check the current state of Tekton:
   ```bash
   cd /Users/cskoons/projects/github/Tekton
   ./EnhancedTools/enhanced_tekton_status.py
   ```

2. Review the sprint documentation:
   - `SprintPlan.md` - Overall plan
   - `ArchitecturalDecisions.md` - Design rationale
   - `ImplementationPlan.md` - Step-by-step guide

3. Start with Phase 1 tasks:
   - Create `.tekton/.env.tekton` entries
   - Build `AIRegistryClient.py`
   - Implement `tekton_ai_launcher.py`

4. Test each component thoroughly before proceeding

## Questions to Consider

As you implement:
- How should CIs handle component restarts?
- What's the best way to visualize CI health in the UI?
- Should we implement rate limiting for API calls?
- How can we make debugging CI issues easier?

## Final Notes

Remember:
- Casey prefers to see multiple approaches before implementation
- Don't commit or push to GitHub - Casey handles version control
- Use TODO lists to track progress
- Ask questions if anything is unclear

The goal is to create a robust, maintainable CI ecosystem that enhances Tekton without adding complexity. Focus on reliability and clean integration over advanced features.

Good luck with the implementation! The existing Tekton codebase provides excellent patterns to follow.