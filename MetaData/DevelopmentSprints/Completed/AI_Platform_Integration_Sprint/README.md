# CI Platform Integration Sprint

## Quick Overview

**Sprint Goal**: Integrate CI specialists throughout Tekton, creating a platform-wide CI ecosystem with Numa as the platform mentor and individual CI specialists for each component.

**Duration**: 2-3 weeks | **Priority**: High | **Status**: Planning

## What We're Building

### Core Components
- **Numa (8016)**: Platform-wide CI mentor with access to all components
- **Noesis (8015)**: Discovery CI (placeholder for future sprint)
- **CI Management Utilities**: Launcher, killer, and status tools
- **CI Health Monitoring**: Auto-recovery for unresponsive CIs

### Key Features
- Environment-controlled CI lifecycle (`TEKTON_REGISTER_AI`)
- Independent CI processes for isolation and fault tolerance
- Socket-based communication via existing registry
- Team Chat integration across all CI specialists

## Quick Start Guide

### Enable CI Support
```bash
# In .tekton/.env.tekton
export TEKTON_REGISTER_AI=true   # Enable AI
export TEKTON_REGISTER_AI=false  # Disable CI (default)
```

### Check CI Status
```bash
# View all CI processes
./EnhancedTools/tekton_ai_status.py

# Launch CI manually (if needed)
./EnhancedTools/tekton_ai_launcher.py

# Terminate all CIs
./EnhancedTools/tekton_ai_killer.py
```

## Architecture at a Glance

### Process Model
- Each CI runs as an independent process
- Communication via socket registry
- Numa launches after all components, terminates first

### Health Monitoring
- Track "last spoke" timestamp
- 5-minute timeout before health check
- Send ESC character to check responsiveness
- Auto-restart if unresponsive

### Component Integration
```
Start: Component → Health Check → Register CI → CI Process
Stop: Terminate CI → Deregister → Terminate Component
```

## Sprint Phases

### Phase 1: Foundation (Days 1-3)
- Create CI management utilities
- Implement Numa and Noesis components
- Update port assignments

### Phase 2: Integration (Days 4-6)
- Update Enhanced Tekton Tools
- Implement health monitoring
- Add lifecycle hooks

### Phase 3: CI Implementation (Days 7-10)
- Build base CI worker class
- Implement component-specific CIs
- Integrate with LLM services

### Phase 4: UI Integration (Days 11-12)
- Add Numa as first navigation tab
- Update Rhetor UI for all CIs
- Enable Team Chat visualization

### Phase 5: Testing & Documentation (Days 13-14)
- Unit and integration tests
- Performance validation
- Documentation updates

## Success Metrics

- [ ] TEKTON_REGISTER_CI flag controls CI lifecycle
- [ ] CI processes start/stop with components
- [ ] Numa launches after full stack, terminates first
- [ ] Health monitoring detects and recovers unresponsive CIs
- [ ] Team Chat works with multiple CIs
- [ ] Numa appears as first UI tab
- [ ] All utilities have proper error handling

## Key Files

### Sprint Documentation
- `SprintPlan.md` - Detailed sprint plan
- `ArchitecturalDecisions.md` - Design rationale
- `ImplementationPlan.md` - Step-by-step guide
- `ClaudeCodePrompt.md` - CI implementation prompt

### Implementation
- `EnhancedTools/tekton_ai_launcher.py`
- `EnhancedTools/tekton_ai_killer.py`
- `EnhancedTools/tekton_ai_status.py`
- `shared_lib/AIRegistryClient.py`

### Components
- `Numa/` - Platform CI mentor
- `Noesis/` - Discovery CI (placeholder)

## Team

- **Sprint Lead**: Casey
- **Architecture**: Claude (Architect)
- **Implementation**: Claude (Developer)
- **Testing**: Automated + Manual verification

## Notes

- Start with Rhetor, Apollo, and Numa for initial rollout
- Use Claude 4 Sonnet as default model
- Monitor API costs via Penia
- Gradual expansion to all components after validation