# CI Platform Integration Sprint Plan

## Sprint Overview

**Sprint Name**: CI Platform Integration Sprint  
**Sprint Goal**: Integrate CI specialists throughout Tekton, creating a platform-wide CI ecosystem with Numa as the platform mentor and individual CI specialists for each component.  
**Duration**: 2-3 weeks  
**Priority**: High  

## Sprint Objectives

1. Create shared CI management utilities (launcher, killer, status)
2. Implement CI lifecycle management with TEKTON_REGISTER_AI flag
3. Create Numa (Platform AI) and Noesis (Discovery) components
4. Integrate CI socket registry with component lifecycle
5. Implement CI health monitoring and auto-recovery
6. Update Rhetor UI to include Numa as the first tab
7. Enable Team Chat across all component CIs

## Key Design Decisions

### 1. CI Process Model
- **Independent Processes**: Each CI runs as a separate process
- **Benefits**: Isolation, fault tolerance, resource management
- **Communication**: Via socket registry (Unix philosophy)

### 2. Environment Control
```bash
# Enable/disable CI registration
export TEKTON_REGISTER_AI=true   # Production mode
export TEKTON_REGISTER_AI=false  # Development mode
```

### 3. CI Monitoring Strategy
- Track "last spoke" timestamp
- 5-minute timeout before health check
- Send ESC character to check responsiveness
- Auto-restart if unresponsive
- Use debug logs to track activity

### 4. Component Updates
- **Numa (8016)**: Platform mentor AI, first UI tab
- **Noesis (8015)**: Discovery AI, placeholder for future sprint
- Both have Chat and Team Chat interfaces

## Implementation Tasks

### Phase 1: Foundation (Days 1-3)

1. **Create CI Utilities**
   - `tekton_ai_launcher.py` - Launch CI processes
   - `tekton_ai_killer.py` - Terminate CI processes
   - `tekton_ai_status.py` - Check CI health
   - `AIRegistryClient` - Shared registry access

2. **Update Port Assignments**
   - Add Numa (8016) to `port_assignments.md`
   - Add Noesis (8015) to `port_assignments.md`
   - Create `.tekton/.env.tekton` with TEKTON_REGISTER_AI

3. **Create Numa Component**
   - Basic FastAPI structure
   - Health check endpoint
   - Hermes registration
   - Companion Chat interface
   - Team Chat interface

4. **Create Noesis Component**
   - Basic FastAPI structure
   - Health check endpoint
   - Hermes registration
   - Discovery Chat interface
   - Team Chat interface

### Phase 2: Integration (Days 4-6)

1. **Update Enhanced Tekton Tools**
   - Modify `enhanced_tekton_launcher.py`
     - Add Numa and Noesis to component list
     - Call `tekton_ai_launcher.py` after health check
     - Launch Numa after all components
   - Modify `enhanced_tekton_killer.py`
     - Call `tekton_ai_killer.py` before component shutdown
     - Kill Numa before other components
   - Modify `enhanced_tekton_status.py`
     - Include CI status from registry

2. **Implement CI Health Monitoring**
   - Last spoke timestamp tracking
   - ESC character health check
   - Auto-restart logic
   - Debug log parsing

### Phase 3: CI Implementation (Days 7-10)

1. **Base CI Worker Class**
   ```python
   class AISpecialistWorker:
       - Socket polling loop
       - LLM integration
       - Response handling
       - Health reporting
   ```

2. **Rhetor CI Specialist**
   - Orchestrator role
   - Team chat moderation
   - Claude 4 Sonnet integration

3. **Apollo CI Specialist**
   - Executive coordinator role
   - Strategic analysis
   - Claude 4 Sonnet integration

4. **Numa Platform AI**
   - Platform mentor role
   - Access to all component sockets
   - Coaching/guidance prompts

### Phase 4: UI Integration (Days 11-12)

1. **Update Hephaestus UI**
   - Add Numa as first navigation tab
   - Add Noesis to navigation (after Sophia)
   - Update component ordering

2. **Rhetor UI Updates**
   - Add Numa to all relevant screens
   - Add Noesis placeholder
   - Update team chat to show all CIs

### Phase 5: Testing & Documentation (Days 13-14)

1. **Testing**
   - Unit tests for CI utilities
   - Integration tests for lifecycle
   - End-to-end team chat test
   - Performance and timeout tests

2. **Documentation**
   - Update CI Socket Registry docs
   - Create CI Lifecycle Guide
   - Update component documentation
   - Create troubleshooting guide

## Success Criteria

1. ✓ TEKTON_REGISTER_AI flag controls CI lifecycle
2. ✓ CI processes start/stop with components
3. ✓ Numa launches after full stack, terminates first
4. ✓ Health monitoring detects and recovers unresponsive CIs
5. ✓ Team Chat works with multiple CIs
6. ✓ Numa appears as first UI tab
7. ✓ All utilities have proper error handling

## Risk Mitigation

1. **API Cost Overrun**
   - Use Ollama for local models
   - Anthropic Max account for unlimited
   - Budget tracking via Penia

2. **Process Management Complexity**
   - Start with 2-3 CIs (Rhetor, Apollo, Numa)
   - Gradual rollout to all components
   - Clear logging and monitoring

3. **Performance Impact**
   - Independent processes minimize impact
   - 5-minute health check timeout
   - Async socket operations

## Future Enhancements

1. Advanced Numa coaching behaviors
2. Inter-AI collaboration patterns
3. Context sharing between CIs
4. CI performance analytics
5. Dynamic CI scaling

## Dependencies

- Existing socket registry implementation
- LLM client infrastructure
- Hermes message bus
- Enhanced Tekton tools

## Team

- **Sprint Lead**: Casey
- **Architecture**: Claude (Architect)
- **Implementation**: Claude (Developer)
- **Testing**: Automated + Manual verification