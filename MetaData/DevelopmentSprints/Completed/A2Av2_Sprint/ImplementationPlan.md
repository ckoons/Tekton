# A2A v2 Protocol Update - Implementation Plan

## Overview

This document provides a detailed implementation plan for implementing Tekton's A2A communication framework from scratch to fully comply with the A2A Protocol v0.2.1 specification. Since we have no legacy constraints, we can build a clean, specification-compliant implementation.

## Implementation Phases

### Phase 1: Protocol Foundation (Days 1-3)

#### 1.1 JSON-RPC 2.0 Core Implementation

**Location**: `tekton-core/tekton/a2a/protocol/`

**New Files**:
```
tekton/a2a/protocol/
├── __init__.py
├── jsonrpc.py          # JSON-RPC request/response handling
├── errors.py           # A2A-specific error codes
└── types.py            # Protocol type definitions
```

**Key Classes**:
- `JSONRPCRequest`: Handle JSON-RPC 2.0 requests
- `JSONRPCResponse`: Format JSON-RPC 2.0 responses
- `A2AError`: Error handling with proper codes
- Protocol type definitions matching A2A spec

**Implementation Details**:
```python
# jsonrpc.py
class JSONRPCRequest:
    def __init__(self, method: str, params: Dict[str, Any], id: Union[str, int]):
        self.jsonrpc = "2.0"
        self.method = method
        self.params = params
        self.id = id
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JSONRPCRequest":
        # Validation and parsing
        pass

# errors.py
class A2AError(Exception):
    # Standard JSON-RPC errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # A2A-specific errors
    TASK_NOT_FOUND = -32001
    TASK_NOT_CANCELABLE = -32002
    PUSH_NOTIFICATION_NOT_SUPPORTED = -32003
```

#### 1.2 HTTP Transport Layer

**Location**: `tekton-core/tekton/a2a/transport/`

**New Files**:
```
tekton/a2a/transport/
├── __init__.py
├── http_server.py      # FastAPI-based A2A server
├── http_client.py      # A2A client implementation
└── middleware.py       # Authentication middleware
```

**Key Components**:
- FastAPI router for A2A endpoints
- HTTP client with connection pooling
- Request/response logging middleware

**Implementation Details**:
```python
# http_server.py
from fastapi import APIRouter, Request, HTTPException
from ..protocol import JSONRPCRequest, JSONRPCResponse

router = APIRouter(prefix="/a2a/v1")

@router.post("/")
async def handle_jsonrpc(request: Request):
    """Main JSON-RPC endpoint"""
    body = await request.json()
    rpc_request = JSONRPCRequest.from_dict(body)
    
    # Route to appropriate method handler
    result = await route_method(rpc_request)
    return JSONRPCResponse(result=result, id=rpc_request.id)
```

#### 1.3 Method Handlers

**Location**: `tekton-core/tekton/a2a/methods/`

**New Files**:
```
tekton/a2a/methods/
├── __init__.py
├── message.py          # message/send, message/stream
├── tasks.py            # tasks/get, tasks/cancel, etc.
└── agent.py            # agent/authenticatedExtendedCard
```

**Implementation for Core Methods**:
- `message/send`: Synchronous message handling
- `tasks/get`: Retrieve task status
- `tasks/cancel`: Cancel running tasks

### Phase 2: Streaming and Tasks (Days 4-6)

#### 2.1 Server-Sent Events Implementation

**Location**: `tekton-core/tekton/a2a/streaming/`

**New Files**:
```
tekton/a2a/streaming/
├── __init__.py
├── sse.py              # SSE manager and formatting
├── events.py           # Event types and serialization
└── subscription.py     # Subscription management
```

**Key Classes**:
- `SSEManager`: Manage SSE connections
- `StreamingResponse`: FastAPI SSE response
- `EventFormatter`: Format events for SSE

**Implementation Details**:
```python
# sse.py
from fastapi import Response
from typing import AsyncGenerator
import json

class SSEManager:
    def __init__(self):
        self.connections: Dict[str, Set[AsyncGenerator]] = {}
    
    async def stream(self, task_id: str) -> AsyncGenerator[str, None]:
        """Generate SSE stream for a task"""
        async for event in self.get_events(task_id):
            yield f"data: {json.dumps(event)}\n\n"

# In http_server.py
@router.post("/message/stream")
async def message_stream(request: JSONRPCRequest):
    """Streaming message endpoint"""
    return StreamingResponse(
        sse_manager.stream(task_id),
        media_type="text/event-stream"
    )
```

#### 2.2 Task State Machine

**Location**: `tekton-core/tekton/a2a/tasks/`

**New Files**:
```
tekton/a2a/tasks/
├── __init__.py
├── state_machine.py    # Task state machine
├── models.py           # Task and TaskStatus models
└── manager.py          # Task lifecycle management
```

**State Implementation**:
```python
# state_machine.py
from enum import Enum
from typing import Dict, Set, Optional

class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    REJECTED = "rejected"
    AUTH_REQUIRED = "auth-required"
    UNKNOWN = "unknown"

class TaskStateMachine:
    TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
        TaskState.SUBMITTED: {TaskState.WORKING, TaskState.REJECTED},
        TaskState.WORKING: {
            TaskState.INPUT_REQUIRED, 
            TaskState.AUTH_REQUIRED,
            TaskState.COMPLETED, 
            TaskState.FAILED,
            TaskState.CANCELED
        },
        # ... more transitions
    }
    
    def transition(self, from_state: TaskState, to_state: TaskState) -> bool:
        """Validate and perform state transition"""
        if to_state in self.TRANSITIONS.get(from_state, set()):
            # Emit state change event
            return True
        return False
```

#### 2.3 Message and Part Types

**Location**: `tekton-core/tekton/a2a/types/`

**Updates to Existing Files**:
- Update `message.py` to support Part types
- Add TextPart, FilePart, DataPart classes
- Update serialization for JSON-RPC

### Phase 3: Security and Agent Cards (Days 7-9)

#### 3.1 Authentication Middleware

**Location**: `tekton-core/tekton/a2a/auth/`

**New Files**:
```
tekton/a2a/auth/
├── __init__.py
├── middleware.py       # Authentication middleware
├── schemes.py          # Auth scheme implementations
└── validators.py       # Token validation
```

**Supported Schemes**:
- Bearer token (JWT)
- Basic authentication
- API Key authentication

**Implementation**:
```python
# middleware.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPBasic, APIKeyHeader

class A2AAuthMiddleware:
    def __init__(self, schemes: List[str]):
        self.schemes = schemes
        self.validators = {
            "Bearer": BearerValidator(),
            "Basic": BasicValidator(),
            "ApiKey": APIKeyValidator()
        }
    
    async def authenticate(self, request: Request) -> Optional[Dict]:
        """Authenticate request using configured schemes"""
        for scheme in self.schemes:
            validator = self.validators.get(scheme)
            if validator:
                result = await validator.validate(request)
                if result:
                    return result
        
        raise HTTPException(401, detail="Authentication required")
```

#### 3.2 Updated Agent Card

**Location**: `tekton-core/tekton/a2a/discovery/`

**Updates**:
- Enhance `AgentCard` class with new fields
- Add security schemes and requirements
- Implement skills and capabilities structure

**New Agent Card Structure**:
```python
# discovery/agent_card.py
from pydantic import BaseModel
from typing import Dict, List, Optional

class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]
    examples: Optional[List[str]] = []
    inputModes: Optional[List[str]] = None
    outputModes: Optional[List[str]] = None

class AgentCapabilities(BaseModel):
    streaming: bool = False
    pushNotifications: bool = False
    stateTransitionHistory: bool = False
    extensions: List[Dict[str, Any]] = []

class SecurityScheme(BaseModel):
    type: str
    description: Optional[str] = None
    # Additional fields based on type

class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    version: str
    capabilities: AgentCapabilities
    skills: List[AgentSkill]
    securitySchemes: Optional[Dict[str, SecurityScheme]] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    # ... other fields
```

#### 3.3 Well-Known URI Endpoint

**Implementation**:
```python
# In http_server.py
@router.get("/.well-known/agent.json")
async def get_agent_card():
    """Return agent card at well-known URI"""
    return current_agent.get_card().dict()

@router.get("/agent/authenticatedExtendedCard")
async def get_extended_card(auth: Dict = Depends(authenticate)):
    """Return extended agent card for authenticated users"""
    return current_agent.get_extended_card(auth).dict()
```

## Integration Points

### Hermes Integration

**File**: `Hermes/hermes/core/a2a_service.py`

**Updates**:
1. Add JSON-RPC method routing
2. Implement SSE connection management
3. Update message bus integration for events

### Ergon Integration

**File**: `Ergon/ergon/api/a2a_endpoints.py`

**Updates**:
1. Replace existing endpoints with JSON-RPC handler
2. Add streaming endpoints
3. Update client to use new protocol

### Component Registration

**All Components**:
1. Update agent registration to use new Agent Card format
2. Add A2A endpoint to component startup
3. Implement well-known URI endpoint

## Testing Strategy

### Unit Tests

**Location**: `tekton-core/tests/a2a/`

- Protocol parsing and serialization
- State machine transitions
- Authentication schemes
- Error handling

### Integration Tests

**Location**: `tests/integration/a2a/`

- Agent-to-agent communication
- Streaming functionality
- Task lifecycle
- Authentication flow

### Performance Tests

**Location**: `tests/performance/a2a/`

- Connection pooling efficiency
- SSE connection limits
- Message throughput
- State transition speed

## Implementation Guide

### For Component Developers

1. Register your agent with proper Agent Card:
```python
from tekton.a2a.discovery import AgentCard, AgentCapabilities, AgentSkill

agent_card = AgentCard(
    name="My Agent",
    description="Agent description",
    url="http://localhost:8001/a2a/v1",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        pushNotifications=True
    ),
    skills=[
        AgentSkill(
            id="task1",
            name="Task 1",
            description="Performs task 1",
            tags=["processing"],
            examples=["Process this data", "Analyze this file"]
        )
    ],
    defaultInputModes=["application/json", "text/plain"],
    defaultOutputModes=["application/json"],
    securitySchemes={
        "bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    },
    security=[{"bearer": []}]
)
```

2. Handle A2A requests using JSON-RPC:
```python
# Sending a message
request = {
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
        "message": {
            "role": "user",
            "parts": [
                {"kind": "text", "text": "Process this data"},
                {"kind": "data", "data": {"key": "value"}}
            ],
            "messageId": str(uuid.uuid4()),
            "kind": "message"
        }
    },
    "id": str(uuid.uuid4())
}

# Receiving a response
response = {
    "jsonrpc": "2.0",
    "result": {
        "id": "task-123",
        "contextId": "ctx-456",
        "status": {
            "state": "completed",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        "artifacts": [
            {
                "artifactId": "artifact-789",
                "name": "result.json",
                "parts": [
                    {"kind": "data", "data": {"result": "processed"}}
                ]
            }
        ]
    },
    "id": request["id"]
}
```

## Deployment Plan

Since this is a fresh implementation:

1. **Phase 1 Deployment**: Deploy core protocol to development environment
2. **Phase 2 Deployment**: Add streaming capabilities 
3. **Phase 3 Deployment**: Enable full authentication and security
4. **Production Deployment**: Full deployment with all features enabled

## Success Metrics

- All unit tests passing (100%)
- Integration tests passing (95%+)
- Successful agent communication using new protocol
- SSE streaming functional with 10+ concurrent connections
- Authentication working with at least 2 schemes
- Performance within 10% of current implementation