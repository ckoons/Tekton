# AI Platform Integration Sprint - Architectural Decisions

## Overview

This document captures the key architectural decisions for integrating AI specialists throughout the Tekton platform.

## Key Architectural Decisions

### 1. AI Process Model - Independent Processes

**Decision**: Each AI specialist runs as an independent process, not a thread within Rhetor.

**Rationale**:
- **Isolation**: Apollo's AI survives Rhetor restarts
- **Fault Tolerance**: One AI crash doesn't affect others
- **Resource Management**: OS handles process scheduling and memory
- **Scalability**: Can distribute AIs across machines in future

**Alternatives Considered**:
- Threading within Rhetor: Simpler but less robust
- Subprocess management: Middle ground but more complex

**Implications**:
- Need process management utilities
- Inter-process communication via sockets
- More complex deployment but better reliability

### 2. Environment-Based Feature Flag

**Decision**: Use `TEKTON_REGISTER_AI` environment variable to control AI lifecycle.

**Rationale**:
- **Development Flexibility**: Easy to disable during coding
- **Cost Control**: Avoid API charges during testing
- **Gradual Rollout**: Enable per-developer or per-environment
- **Standard Pattern**: Follows common feature flag practices

**Implementation**:
```bash
# In .tekton/.env.tekton or shell
export TEKTON_REGISTER_AI=true   # Enable AI
export TEKTON_REGISTER_AI=false  # Disable AI (default)
```

### 3. Socket-Based Communication

**Decision**: Use the existing socket registry for all AI communication.

**Rationale**:
- **Unix Philosophy**: Everything is a file/stream
- **Existing Infrastructure**: Socket registry already built
- **Simple Interface**: Read/write operations only
- **Language Agnostic**: Any process can participate

**Message Flow**:
```
Component → Write to Socket → AI Reads → Processes → Writes Response → Component Reads
```

### 4. AI Health Monitoring via Activity

**Decision**: Monitor AI health by tracking "last spoke" timestamps rather than active polling.

**Rationale**:
- **Non-Intrusive**: Doesn't interrupt AI operations
- **Natural Behavior**: AIs communicate when active
- **Resource Efficient**: No constant health checks
- **Debug Integration**: Can use debug logs as activity

**Health Check Logic**:
1. Track last communication timestamp
2. After 5 minutes of silence, send ESC character
3. If no response in 30 seconds, mark unresponsive
4. Auto-restart if configured

### 5. Numa as Platform Mentor

**Decision**: Numa is a peer AI with platform-wide visibility, not a privileged supervisor.

**Rationale**:
- **Collaborative Model**: Facilitator, not boss
- **User-Centric**: Serves the user, not other AIs
- **Simple Permissions**: Read access everywhere, write to sockets
- **Coaching Role**: Guides through knowledge, not authority

**Numa's Capabilities**:
- Access to all component sockets
- Can read any file in Tekton
- Provides platform-wide perspective
- Mentors through suggestions, not commands

### 6. Component Lifecycle Integration

**Decision**: AI lifecycle tied to component lifecycle with special handling for Numa.

**Rationale**:
- **Simplicity**: Components and their AIs live together
- **Resource Management**: Clean startup/shutdown
- **Special Cases**: Numa for full stack, component AIs for individuals
- **Predictable Behavior**: Clear when AIs start/stop

**Lifecycle Sequence**:
```
Start: Component → Health Check → Register AI → AI Process
Stop: Terminate AI → Deregister → Terminate Component
Numa: Starts after all components, stops before any component
```

### 7. Shared AI Registry Client

**Decision**: Create a shared registry client that works independently of Rhetor.

**Rationale**:
- **Shutdown Resilience**: Can deregister even if Rhetor is down
- **File-Based Fallback**: Persist registry state to disk
- **Universal Access**: Any component can register/query AIs
- **Decoupled Design**: Registry logic separate from Rhetor

**Registry Client Features**:
- HTTP API when Rhetor available
- File-based operations as fallback
- Async interface for non-blocking ops
- Automatic retry and error handling

### 8. Model Selection Strategy

**Decision**: Standardize on Claude 4 Sonnet with Claude 4 Opus for premium needs.

**Rationale**:
- **Latest Models**: Claude 3 sunset approaching
- **Cost Efficiency**: Sonnet for most tasks
- **Quality Option**: Opus for complex reasoning
- **Anthropic Max**: Unlimited usage for development

**Model Assignments**:
- Default: Claude 4 Sonnet (claude-3-5-sonnet-20241022)
- Premium: Claude 4 Opus (when available)
- Local: Ollama models for cost-free operation

### 9. Debug Mode Integration

**Decision**: Use debug logs to track AI activity and health.

**Rationale**:
- **Existing Infrastructure**: Debug system already in place
- **Rich Information**: Detailed activity tracking
- **Filterable**: Can extract AI-specific logs
- **Performance**: No overhead when disabled

**Debug Integration**:
- Parse debug logs for AI activity
- Update "last spoke" on any AI output
- Filter by component name for clarity
- Use for troubleshooting and monitoring

### 10. Gradual Component Rollout

**Decision**: Start with Rhetor, Apollo, and Numa, then expand to all components.

**Rationale**:
- **Risk Management**: Test with small set first
- **Learning Curve**: Refine patterns before scaling
- **Resource Control**: Monitor costs and performance
- **Iterative Improvement**: Apply lessons learned

**Rollout Plan**:
1. Phase 1: Rhetor (orchestrator), Apollo (executive), Numa (platform)
2. Phase 2: Athena, Hermes, Engram (core infrastructure)
3. Phase 3: Remaining components
4. Phase 4: Specialized AIs (if needed)

## Technical Standards

### AI Process Naming
- Pattern: `{component_name}_ai`
- Examples: `rhetor_ai`, `apollo_ai`, `numa_ai`

### Socket Naming
- Pattern: Component name directly
- Examples: `rhetor`, `apollo`, `numa`
- Special: `team-chat-all` for broadcasts

### Port Assignments
- Numa: 8016 (Platform AI)
- Noesis: 8015 (Discovery - placeholder)

### Environment Variables
- `TEKTON_REGISTER_AI`: Enable/disable AI lifecycle
- `TEKTON_AI_DEBUG`: Enable AI-specific debug logging
- `TEKTON_AI_AUTO_RESTART`: Enable automatic restart of failed AIs

## Security Considerations

1. **Process Isolation**: Each AI runs with component permissions
2. **Socket Access**: Controlled by registry permissions
3. **File Access**: AIs inherit component file access
4. **Network**: Localhost only, no external AI access

## Performance Considerations

1. **Startup Time**: AIs launch async, don't block components
2. **Memory**: Each AI process ~200-500MB
3. **CPU**: Minimal when idle, spikes during processing
4. **Monitoring**: 5-minute timeout minimizes overhead

## Future Considerations

1. **Distributed AIs**: Could run on separate machines
2. **AI Pooling**: Shared AIs for similar components
3. **Dynamic Scaling**: Spawn AIs based on load
4. **Specialized Models**: Task-specific AI variants

These architectural decisions provide a solid foundation for integrating AI throughout Tekton while maintaining simplicity, reliability, and flexibility.