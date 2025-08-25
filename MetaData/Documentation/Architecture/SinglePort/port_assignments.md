# Tekton Port Assignment Documentation

## Single Port Architecture

As of April 26, 2025, Tekton has moved to a consolidated, single-port-per-component architecture. Each component now uses a single port for all its operations (HTTP, WebSocket, and Events) via path-based routing.

## Port Allocation Scheme

| Component Name | Port | Environment Variable | Description |
|----------------|------|----------------------|-------------|
| Hephaestus UI | 8080 | HEPHAESTUS_PORT | HTTP, WebSocket, Events via path routing (standard web UI port) |
| Engram | 8000 | ENGRAM_PORT | Memory system - HTTP, WebSocket, Events |
| Hermes | 8001 | HERMES_PORT | Service registry, Database, Events |
| Ergon | 8002 | ERGON_PORT | Agent system - HTTP, WebSocket, Events |
| Rhetor | 8003 | RHETOR_PORT | LLM management - HTTP, WebSocket, Events |
| Terma | 8004 | TERMA_PORT | Terminal - HTTP, WebSocket, Events |
| Athena | 8005 | ATHENA_PORT | Knowledge graph - HTTP, Events |
| Prometheus | 8006 | PROMETHEUS_PORT | Planning system - HTTP, Events |
| Harmonia | 8007 | HARMONIA_PORT | Workflow system - HTTP, Events |
| Telos | 8008 | TELOS_PORT | Requirements system - HTTP, Events |
| Synthesis | 8009 | SYNTHESIS_PORT | Execution engine - HTTP, WebSocket, Events |
| Tekton Core | 8010 | TEKTON_CORE_PORT | Core orchestration - HTTP, Events |
| Metis | 8011 | METIS_PORT | Task Architecture & Management - HTTP, WebSocket, Events |
| Apollo | 8012 | APOLLO_PORT | Local Attention/Prediction layer - HTTP, Events |
| Budget | 8013 | BUDGET_PORT | Token/cost management system - HTTP, Events |
| Sophia | 8014 | SOPHIA_PORT | Machine learning system - HTTP, Events |
| Noesis | 8015 | NOESIS_PORT | Discovery system - HTTP, Events |
| Numa | 8016 | NUMA_PORT | Platform CI mentor - HTTP, Events |

## Design Rationale

1. **Simplified Port Management**: Sequential port numbering (8000-8010) makes it easy to remember and track port assignments
2. **Consistent Convention**: Only Hephaestus UI retains its conventional 8080 port for web access
3. **Environment Variables**: All port references should use the standardized environment variables, not hardcoded port numbers
4. **Path-Based Routing**: Each component uses a single port for all communication methods (HTTP, WebSocket, Events)

## Implementation Guidelines

When updating component code to use the new port assignments:

1. **Environment Variables**: Always use the environment variables defined in the table above
2. **Fallback Values**: If providing fallback values, use the standardized port number
3. **Configuration Files**: Update any configuration files to use these environment variables
4. **Service Discovery**: Ensure service discovery mechanisms use these environment variables

```python
# Example Python code
import os

# Correct way to reference ports
port = int(os.environ.get("COMPONENT_PORT", 8xxx))  # Use standard fallback

# Example service URL construction
service_url = f"http://localhost:{os.environ.get('HERMES_PORT', 8001)}/api/service"
```

```javascript
// Example JavaScript code
const componentPort = process.env.COMPONENT_PORT || 8xxx;  // Use standard fallback
const wsUrl = `ws://localhost:${process.env.COMPONENT_PORT || 8xxx}/ws`;
```

## Migration Plan

1. Update all scripts to use the new port assignments (completed)
2. Update component code to use environment variables for port references
3. Update documentation and configuration files
4. Test connectivity between components
5. Deploy the updated system

## External Services

External services (like Ollama) retain their conventional ports:
- Ollama API: 11434
- External databases: Use their standard ports

## Notes

- This port assignment scheme is part of Tekton's Single Port Architecture initiative
- Previous multi-port setups have been consolidated
- All Tekton tools (launch, status, kill) have been updated to support this architecture
