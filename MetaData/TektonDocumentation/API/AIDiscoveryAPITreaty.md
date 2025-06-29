# Tekton AI Discovery API Treaty

## Version 1.0.0

This document defines the stable API contract between the Tekton AI Platform and clients like aish. This treaty guarantees interface stability and discovery mechanisms for AI specialists.

## Core Principles

1. **Dynamic Discovery**: Clients MUST use discovery rather than hardcoded names
2. **No Assumptions**: Clients MUST NOT assume specific AI names or ports
3. **Graceful Degradation**: Clients SHOULD handle missing AIs gracefully
4. **Metadata Driven**: All routing decisions based on discovered metadata

## Discovery Endpoints

### 1. List All AI Specialists

**Command Line:**
```bash
ai-discover list [--role ROLE] [--capability CAPABILITY] [--json]
```

**Programmatic:**
```python
discovery = AIDiscoveryService()
result = await discovery.list_ais(role="planning")
```

**Response Schema:**
```json
{
  "ais": [
    {
      "id": "string",           // Unique identifier (e.g., "apollo-ai")
      "name": "string",         // Display name (e.g., "apollo")
      "component": "string",    // Component name (e.g., "apollo")
      "status": "string",       // "healthy" | "unhealthy" | "unknown"
      "roles": ["string"],      // List of roles this AI can fulfill
      "capabilities": ["string"], // List of capabilities
      "model": "string",        // Model being used
      "context_window": int,    // Max context size
      "max_tokens": int,        // Max output tokens
      "connection": {
        "host": "string",       // Usually "localhost"
        "port": int             // Socket port number
      },
      "performance": {
        "avg_response_time": float,
        "success_rate": float,
        "total_requests": int
      }
    }
  ]
}
```

### 2. Get Specific AI Information

**Command Line:**
```bash
ai-discover info AI_ID [--json]
```

**Response:** Same as individual AI object above

### 3. Find Best AI for Role

**Command Line:**
```bash
ai-discover best ROLE [--json]
```

**Response:** Single AI object with best match for role

### 4. Test AI Connection

**Command Line:**
```bash
ai-discover test [AI_ID] [--json]
```

**Response:**
```json
{
  "ai_id": "string",
  "reachable": boolean,
  "response_time": float,  // in seconds
  "socket": "host:port",
  "error": "string"        // if not reachable
}
```

### 5. Get AI Schema

**Command Line:**
```bash
ai-discover schema AI_ID [--json]
```

**Response:**
```json
{
  "ai_id": "string",
  "message_types": {
    "chat": {
      "description": "Standard chat/completion request",
      "required": ["content"],
      "optional": ["temperature", "max_tokens", "system_prompt"]
    },
    "info": {
      "description": "Get AI information",
      "required": [],
      "optional": []
    }
  },
  "response_format": {
    "chat": {
      "content": "string",
      "model": "string",
      "usage": {"prompt_tokens": "int", "completion_tokens": "int"}
    }
  }
}
```

## Name Resolution Rules

### 1. AI Identification
- **Primary ID**: Use the `id` field (e.g., "apollo-ai")
- **Short Name**: The `name` field can be used for user-friendly display
- **Component Name**: The `component` field indicates the Greek Chorus member

### 2. Matching Algorithm for User Input

When a user types `echo "test" | apollo`, clients SHOULD:

1. Try exact match against `id`
2. Try exact match against `name`
3. Try exact match against `component`
4. Try prefix match against `id` (e.g., "apollo" matches "apollo-ai")
5. Try fuzzy match and suggest alternatives
6. Fail with helpful error message

### 3. Special Names
- `rhetor`: The orchestrator (maps to role "orchestration")
- `team-chat`: Full team discussion (if available)
- `@role`: Role-based routing (e.g., `@planning`, `@code-analysis`)

## Role Definitions

Standard roles that AIs may advertise:

- `orchestration`: Coordinating multiple AIs and complex tasks
- `code-analysis`: Analyzing, reviewing, and understanding code  
- `planning`: Task planning and project management
- `knowledge-synthesis`: Information synthesis and reasoning
- `memory`: Memory and context management
- `messaging`: Communication and chat
- `learning`: Learning and adaptation
- `agent-coordination`: Multi-agent coordination
- `specialist-management`: Managing AI specialists
- `workflow-design`: Designing workflows and processes
- `general`: General-purpose AI

## Socket Communication Protocol

### Message Format
All messages are newline-delimited JSON over TCP:

```json
{"type": "chat", "content": "message", "temperature": 0.7, "max_tokens": 4000}
```

### Standard Message Types

#### Chat Request
```json
{
  "type": "chat",
  "content": "string",
  "temperature": 0.7,      // optional, 0.0-1.0
  "max_tokens": 4000,      // optional
  "system_prompt": "string" // optional
}
```

#### Info Request
```json
{
  "type": "info"
}
```

#### Ping Request
```json
{
  "type": "ping"
}
```

### Response Formats

#### Chat Response
```json
{
  "content": "string",
  "model": "string",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 200,
    "total_tokens": 300
  }
}
```

#### Info Response
```json
{
  "type": "info_response",
  "ai_id": "string",
  "component": "string",
  "model": "string",
  "capabilities": ["string"],
  "context_window": 100000
}
```

#### Error Response
```json
{
  "error": "string",
  "type": "error",
  "code": "string"  // optional error code
}
```

## Client Implementation Requirements

### 1. Discovery Strategy

Clients MUST implement one of these strategies:

**Option A: Cache with TTL**
```python
class AIDiscoveryCache:
    def __init__(self, ttl=300):  # 5 minute cache
        self.cache = {}
        self.cache_time = 0
        self.ttl = ttl
    
    async def get_ais(self):
        if time.time() - self.cache_time > self.ttl:
            self.cache = await discover_ais()
            self.cache_time = time.time()
        return self.cache
```

**Option B: On-Demand Discovery**
- Discover on first use
- Re-discover on any connection failure
- Provide manual refresh command

### 2. Fallback Behavior

When an AI is unavailable, clients SHOULD:

1. Try to discover updated list
2. Use `ai-discover best ROLE` to find alternative
3. Inform user of the substitution
4. Continue with alternative or fail gracefully

### 3. Error Messages

Provide helpful error messages:

```
Error: AI 'apollo' not found.
Available AIs: hermes, prometheus, athena
Try: ai-discover list
```

## Breaking Changes Policy

This API treaty guarantees:

1. **Stable Core Fields**: The core fields (id, name, roles, connection) will not change
2. **Additive Only**: New fields may be added but won't break existing clients
3. **Version Header**: Future versions will include version in responses
4. **Deprecation Notice**: 3-month notice before removing features
5. **Discovery First**: Changes to AI names/ports don't break clients using discovery

## Migration Guide for aish

### Current State (Hardcoded)
```python
specialist_map = {
    'apollo': 'apollo-coordinator',
    'hermes': 'hermes-messenger'
}
```

### New State (Dynamic)
```python
async def resolve_specialist(name: str) -> Optional[Dict]:
    """Resolve a specialist name using discovery."""
    # Try exact match first
    ais = await discover_ais()
    
    # Try various matching strategies
    for ai in ais:
        if name in [ai['id'], ai['name'], ai['component']]:
            return ai
        if ai['id'].startswith(f"{name}-"):
            return ai
    
    # Try role-based if starts with @
    if name.startswith('@'):
        role = name[1:]
        return await discover_best_for_role(role)
    
    return None
```

### Integration Example
```python
# In aish socket_registry.py
class SocketRegistry:
    async def get_specialist_socket(self, name: str) -> Optional[Tuple[str, int]]:
        """Get socket for specialist using discovery."""
        ai = await resolve_specialist(name)
        if ai and ai['status'] == 'healthy':
            return (ai['connection']['host'], ai['connection']['port'])
        return None
```

## Testing Compliance

Clients can test their implementation:

```bash
# Test discovery
ai-discover list --json | jq '.ais[0]'

# Test connection
ai-discover test apollo-ai

# Test role resolution
ai-discover best planning

# Test error handling
echo "test" | aish_client non_existent_ai
```

## Questions from aish Answered

Based on your analysis questions:

1. **Q1: Discovery Endpoint**: Use `ai-discover` tool or `AIDiscoveryService` class
2. **Q2: Name Resolution**: Match in order: id → name → component → prefix → fuzzy
3. **Q3: Capability Discovery**: Yes, use role-based routing with `@role` syntax
4. **Q4: Discovery Frequency**: Cache with 5-minute TTL recommended
5. **Q5: Performance**: Specialist list is stable, caching is safe
6. **Q6: Unknown Specialists**: Try discovery first, then error with suggestions
7. **Q7: Inactive Specialists**: Filter by status == "healthy"
8. **Q8: Specialist Metadata**: Rich metadata included in discovery response
9. **Q9: Special Specialists**: "rhetor" remains orchestrator, "@role" for role-based

## Version History

- **1.0.0** (2024-06-29): Initial API Treaty
  - Dynamic discovery protocol
  - Socket communication standard
  - Role-based routing
  - Breaking changes policy