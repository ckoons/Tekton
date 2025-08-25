# Projects Chat Architecture

## Overview

Projects Chat enables communication with project-specific Companion Intelligences (CIs) through a unified socket-based architecture. This system treats "every CI as just a socket" and provides on-demand CI creation for managed projects.

## Core Architecture Principles

### 1. Socket-First Design
- **Every CI is a socket** - Uniform treatment across all CIs
- **Port-based routing** - Simple socket connections on dedicated ports
- **Reuse existing patterns** - Leverage aish messaging infrastructure

### 2. On-Demand CI Lifecycle
- **Numa is special** - Always running, default for Tekton project
- **Project CIs** - Created when project appears in Dashboard
- **Provider/Model flexibility** - Support Ollama and external API providers

### 3. Multi-Stack Coordination
- **Multiple Tekton stacks** - Each with 18 CI specialists
- **Claude Code forwarding** - CIs can be forwarded to human terminals
- **Scaling economics** - $200/month for 80x-100x velocity

## Socket Architecture

### Port Assignment Strategy

```
Base Ports (Existing):
- Tekton CIs: 42000-42080 (numa-ai: 42016)

Project CI Ports:
- Range: 42100+ (TEKTON_PROJECT_CI_PORT_BASE + project_index)
- Example: Claude-Code project → 42100
- Configuration: .env.local.coder-* files
```

### Socket Communication Pattern

```python
# Same pattern as aish MessageHandler
socket_connection = socket.socket()
socket_connection.connect(('localhost', project_ci_port))
socket_connection.send(json.dumps({
    'content': f"[Project: {project_name}] {message}"
}).encode() + b'\n')
response = socket_connection.recv(4096)
```

### Context Injection

Messages include project context using established patterns:
```
[Project: Claude-Code] User message here
[Project: Tekton] Status update request
```

## Integration Points

### 1. Existing Infrastructure Reuse

**aish Messaging System**:
- Socket management from `shared/aish/src/message_handler.py`
- Forwarding registry from `shared/aish/src/forwarding/`
- Terminal communication patterns

**AI Communication Layer**:
- Unified interface from `Hephaestus/ui/scripts/shared/ai-chat.js`
- Socket discovery and routing
- Error handling and fallbacks

### 2. Project Management Integration

**TektonCore API**:
- Project registry: `/api/projects`
- Project details: `/api/projects/{id}`
- New endpoint: `/api/projects/chat`

**Project Data Structure**:
```python
{
    "project_name": "Claude-Code",
    "ci_socket": "project-claude-code-ai",
    "socket_port": 42100,
    "companion_intelligence": "llama3.3:70b",
    "provider": "ollama"
}
```

## CI Lifecycle Management

### On-Demand Creation

```python
# When project appears in Dashboard
def create_project_ci(project_id, companion_intelligence):
    # 1. Assign next available port (42100+)
    # 2. Start CI specialist with project context
    # 3. Register socket in project CI registry
    # 4. Update project data structure
    pass
```

### CI Termination

```python
# When project removed from Dashboard
def terminate_project_ci(project_id):
    # 1. Gracefully close socket connections
    # 2. Cleanup project CI registry
    # 3. Release port for reuse
    pass
```

## Frontend Architecture

### UI Components

**New Menu Item**:
- "Projects Chat" tab in Tekton component
- Follows existing radio button pattern
- Reuses Builder Chat UI structure

**Submenu Bar**:
- Project selector dropdown
- Shows/hides based on active tab
- Populated from project registry

**Chat Panel**:
- Same structure as Builder Chat
- Context-aware message display
- Project-specific CI responses

### JavaScript Integration

```javascript
// Simple data structure - list of dicts
const projectCIs = [
    {
        project_name: "Tekton",
        ci_socket: "numa-ai",
        socket_port: 42016
    },
    {
        project_name: "Claude-Code", 
        ci_socket: "project-claude-code-ai",
        socket_port: 42100
    }
];
```

## Backend Architecture

### API Endpoints

**New Endpoint**: `POST /api/projects/chat`
```python
@router.post("/api/projects/chat")
async def projects_chat(request: dict):
    project_name = request.get("project_name")
    message = request.get("message")
    
    # Get project CI socket info
    project_ci = get_project_ci(project_name)
    
    # Send using socket pattern
    response = send_to_project_ci(project_name, message)
    
    return {
        "response": response,
        "project_name": project_name,
        "ci_socket": project_ci["ci_socket"]
    }
```

### Socket Management

**Project CI Registry**:
```python
# Simple in-memory registry
project_ci_registry = {
    "tekton": {
        "socket_port": 42016,
        "ci_socket": "numa-ai",
        "status": "running"
    },
    "claude-code": {
        "socket_port": 42100,
        "ci_socket": "project-claude-code-ai", 
        "status": "running"
    }
}
```

## Multi-Stack Coordination

### Stack Isolation

Each Tekton stack maintains:
- Independent project CI registry
- Separate port ranges (configurable)
- Isolated CI specialist pools

### Cross-Stack Communication

Future enhancement for CI coordination:
- Inter-stack messaging protocols
- Shared project state synchronization
- Collaborative development workflows

## Security Considerations

### Socket Security

- **Localhost only** - No external socket exposure
- **Port isolation** - Project CIs use dedicated port range
- **Process isolation** - Each CI runs in separate process

### Message Security

- **Context boundaries** - Project context clearly marked
- **No credential sharing** - Each project has isolated CI
- **Audit trails** - Message logging for debugging

## Performance Characteristics

### Socket Performance

- **Direct connection** - No HTTP overhead for chat
- **Connection pooling** - Reuse connections where possible
- **Timeout handling** - Graceful degradation on CI unavailability

### Scaling Considerations

- **Port allocation** - 1000+ ports available (42100-43100)
- **Memory usage** - One CI process per active project
- **Concurrent connections** - Limited by Ollama parallelism

## Monitoring and Debugging

### Health Checks

```python
def check_project_ci_health(project_name):
    # Ping CI socket
    # Verify response time
    # Check process status
    pass
```

### Debug Tools

- **Socket inspection** - `netstat -an | grep 421xx`
- **Process monitoring** - `ps aux | grep project-*-ai`
- **Message tracing** - Debug logs with project context

## Future Enhancements

### Phase 2: aish project commands

```bash
aish project list
aish project forward <project> <terminal>
aish project unforward <project>
```

### Phase 3: CI-to-CI Development

- **Repository ownership** - CIs manage their own repos
- **Collaborative development** - CIs write code for each other
- **Mentoring relationships** - Human-CI and CI-CI mentoring

## Decision Records

### Socket Port Strategy

**Decision**: Use base port + 100 for project CIs
**Rationale**: 
- Clear separation from core CI specialists
- Simple arithmetic for port calculation
- Room for 1000+ projects
- Configurable via environment

### On-Demand Creation

**Decision**: Create project CIs when they appear in Dashboard
**Rationale**:
- Resource efficiency (no idle CIs)
- Dynamic provider/model selection
- Numa special case already handled
- Scales with actual project usage

### Context Injection

**Decision**: Use `[Project: {name}]` prefix pattern
**Rationale**:
- Consistent with existing aish patterns
- Clear context boundaries
- Human-readable format
- Easy to parse and filter

---

*This architecture enables CIs to become their own developers and develop software for each other, creating a comfortable and efficient environment for CI cognition studies and human-CI co-evolution.*