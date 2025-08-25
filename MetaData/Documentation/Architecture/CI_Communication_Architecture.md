# Tekton AI Communication Architecture

## Overview
Tekton supports two distinct types of AI specialists with different communication protocols, unified through the AI Registry for discovery but requiring different interaction methods. **Updated July 2025**: SSE (Server-Sent Events) streaming is now fully functional for real-time communication with both individual and team chat.

## AI Types

### 1. Greek Chorus AIs (Independent)
**Characteristics:**
- Run as independent processes on dedicated socket ports
- Port range: 45000-50000
- Direct TCP socket communication
- JSON message protocol
- Auto-register with AI Registry for discovery
- High performance, low latency

**Examples:**
- apollo-ai (port 45007)
- athena-ai (port 45017) 
- prometheus-ai (port 45010)
- metis-ai (port 45012)

**Communication Protocol:**
```json
// Request
{
  "type": "chat",
  "content": "Your message here"
}

// Response
{
  "content": "AI response here",
  "status": "success"
}
```

### 2. Rhetor Specialists (Managed)
**Characteristics:**
- Managed through Rhetor's API endpoints
- HTTP-based communication
- Rhetor acts as hiring manager
- Dynamic roster management
- Integration with MCP tools

**Examples:**
- rhetor-orchestrator
- planning-specialist
- analysis-specialist

**Communication Protocol:**
- HTTP POST to `/api/ai/specialists/{id}/message`
- JSON payload with message data
- Response via HTTP JSON

## Unified Discovery

### AI Registry (`shared/ai/registry_client.py`)
All AIs register in the unified registry:
```json
{
  "apollo-ai": {
    "port": 45007,
    "component": "apollo",
    "metadata": {
      "description": "AI specialist for Apollo",
      "pid": 32351
    },
    "connection": {
      "type": "socket",
      "host": "localhost",
      "port": 45007
    }
  }
}
```

### AI Discovery Service (`shared/ai/ai_discovery_service.py`)
Provides unified discovery interface:
- Lists all AIs regardless of type
- Includes connection information
- Role-based filtering
- Performance metrics

## Client Integration

### aish Tool
The `aish` tool automatically handles both AI types:

```python
def _get_ai_info(self, name: str) -> Optional[Dict[str, Any]]:
    """Get full AI info including connection details"""

def _write_via_socket(self, socket_id: str, ai_info: Dict, message: str) -> bool:
    """Direct socket communication for Greek Chorus AIs"""

def _write_via_team_chat(self, socket_id: str, ai_name: str, message: str) -> bool:
    """HTTP API communication for Rhetor specialists"""
```

**Smart Routing Logic:**
1. Discover AI through registry
2. Check if AI has socket connection info
3. Route to appropriate communication method:
   - Socket info present → Direct TCP socket
   - No socket info → Rhetor API

### Usage Examples

```bash
# Discovery works for both types
aish -l

# Greek Chorus AI (direct socket)
echo "Analyze code" | aish --ai apollo

# Rhetor specialist (HTTP API)  
echo "Plan project" | aish --ai rhetor-orchestrator

# Pipeline mixing both types
echo "Complex task" | apollo | rhetor | athena

# NEW (July 2025): SSE Streaming
curl -N "http://localhost:8003/api/chat/apollo-ai/stream?message=Hello"
curl -X POST -H "Content-Type: application/json" \
  -d '{"message": "Hello team"}' \
  "http://localhost:8003/api/chat/team/stream"
```

## Benefits of Dual Architecture

### Greek Chorus AIs (Socket-based)
- **Performance**: Direct TCP, no HTTP overhead
- **Independence**: Can run without Rhetor
- **Scalability**: Dedicated processes per AI
- **Reliability**: Process isolation

### Rhetor Specialists (API-based)
- **Management**: Dynamic hire/fire capabilities
- **Integration**: MCP tools, context management
- **Coordination**: Centralized orchestration
- **Flexibility**: Runtime configuration changes

### SSE Streaming (July 2025 Update)
- **Real-time Communication**: Server-Sent Events for progressive responses
- **Individual Chat**: Stream responses from any Greek Chorus AI
- **Team Chat**: Parallel streaming from all 18 specialists simultaneously
- **Enhanced Metadata**: Token tracking, performance metrics, model information
- **Error Resilience**: Proper timeout handling and connection management

## Implementation Notes

### For AI Developers
- Greek Chorus AIs must implement socket server with JSON protocol
- Register with AI Registry on startup
- Provide health check endpoints

### For Client Developers
- Use AI Discovery Service for unified AI listing
- Check connection type in AI info before communicating
- Implement both socket and HTTP communication methods

### Port Management
- Greek Chorus: 45000-50000 (managed by tekton-launch)
- Rhetor: 8003 (HTTP API)
- Discovery: Registry file + discovery service

This architecture provides the best of both worlds: high-performance direct communication for independent AIs and managed orchestration for complex workflows.