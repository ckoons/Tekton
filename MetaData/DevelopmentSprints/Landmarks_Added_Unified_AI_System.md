# Landmarks Added to Unified AI System

## Summary
Added landmarks to the new unified AI system components to document architectural decisions, performance boundaries, and integration points.

## Files Instrumented

### 1. `/shared/ai/socket_client.py`

#### Class: `AISocketClient`
- **@architecture_decision**: "Unified AI Socket Client Architecture"
  - Centralize all AI socket communication for consistent protocol handling
  - Alternatives: Individual implementations, REST API only, gRPC
  
- **@integration_point**: "Greek Chorus AI Integration"
  - Target: Greek Chorus AIs (ports 45000-50000)
  - Protocol: Socket/NDJSON
  - Bidirectional message exchange with streaming

#### Method: `send_message()`
- **@performance_boundary**: "AI Socket Message Exchange"
  - SLA: <30s timeout per message
  - Uses connection pooling and exponential backoff retry

#### Method: `send_message_stream()`
- **@architecture_decision**: "Native Streaming Support"
  - Real-time streaming for better UX and reduced latency
  - Alternatives: Polling, Long polling, WebSockets
  
- **@performance_boundary**: "Streaming Response Handler"
  - SLA: <100ms first token latency
  - Yields chunks immediately without buffering

### 2. `/shared/ai/unified_registry.py`

#### Class: `UnifiedAIRegistry`
- **@architecture_decision**: "Unified AI Registry Architecture"
  - Single source of truth for all AI specialists
  - Event-driven updates and health monitoring
  - Alternatives: Distributed registries, Static config, Service mesh
  
- **@state_checkpoint**: "Central AI Registry State"
  - Type: Singleton with persistence
  - Consistency: Eventually consistent with file locking
  - Recovery: Reload from persistent storage on restart

#### Method: `discover()`
- **@performance_boundary**: "AI Discovery with Caching"
  - SLA: <10ms for cached queries, <100ms for fresh queries
  - In-memory cache with 60s TTL

### 3. `/shared/ai/routing_engine.py`

#### Class: `RoutingEngine`
- **@architecture_decision**: "Rule-Based AI Routing Engine"
  - Intelligent routing based on context, capabilities, and performance
  - Alternatives: Random selection, Round-robin, Static mapping
  
- **@state_checkpoint**: "Routing State and Metrics"
  - Type: In-memory cache
  - Resets on restart, rebuilds from registry

#### Method: `route_message()`
- **@performance_boundary**: "Message Routing Decision"
  - SLA: <50ms routing decision time
  - Uses cached registry data
  
- **@danger_zone**: "Complex Routing Logic"
  - Risks: Routing loops, Availability cascades, Load imbalance
  - Mitigation: Fallback limits, exclude lists, load balancing

### 4. `/Rhetor/rhetor/core/llm_client.py`

#### Class: `LLMClient`
- **@architecture_decision**: "Rhetor LLM Client Migration to Unified System"
  - Eliminate duplicate implementations using shared AI infrastructure
  - Decided by: Casey
  - Impacts: Code reduction, consistency, maintenance

## Benefits

1. **Architectural Memory**: Future maintainers (human or AI) can understand why decisions were made
2. **Performance Contracts**: Clear SLAs and optimization notes for critical paths
3. **Risk Awareness**: Danger zones are clearly marked with mitigation strategies
4. **Integration Documentation**: Clear data flow and protocol documentation
5. **State Management**: Explicit documentation of stateful components

## Next Steps

- Monitor landmark usage in development
- Add more landmarks as new features are added
- Use landmarks in code reviews to ensure architectural consistency