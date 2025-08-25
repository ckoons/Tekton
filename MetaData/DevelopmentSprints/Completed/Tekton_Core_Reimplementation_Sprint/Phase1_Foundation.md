# Phase 1: Foundation & Communication

## Overview

Build the foundational tekton-core service with integrated chat capabilities. This phase focuses on establishing the communication infrastructure that all other features will build upon.

## Timeline: Week 1

### Day 1-2: tekton-core Shell

**Create Basic Service Structure**
```
tekton-core/
├── api/
│   ├── app.py              # FastAPI application
│   ├── chat.py             # Chat endpoints
│   └── projects.py         # Project management endpoints
├── core/
│   ├── project_manager.py  # Project state management
│   ├── chat_manager.py     # Chat orchestration
│   └── models.py           # Data models
├── storage/
│   └── projects.json       # Simple JSON storage to start
└── run_tekton_core.sh      # Launch script
```

**Basic API Setup**
```python
# Health check
GET /api/health

# Project endpoints (minimal for Phase 1)
GET /api/v1/projects
POST /api/v1/projects

# Chat endpoints (focus of Phase 1)
GET /api/v1/chat/project/{project_id}/messages
POST /api/v1/chat/project/{project_id}/send
GET /api/v1/chat/team/messages
POST /api/v1/chat/team/send
```

### Day 3-4: Project Chat Implementation

**Project Chat Features**
- Project-specific message channels
- Real-time updates via WebSocket
- Message history per project
- CI participant tracking

**Implementation Details**
```python
class ProjectChat:
    """Manages project-specific conversations"""
    
    def __init__(self, project_id):
        self.project_id = project_id
        self.messages = []
        self.participants = []
    
    def add_message(self, sender, content, msg_type="chat"):
        """Add message to project chat"""
        message = {
            "id": generate_id(),
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "content": content,
            "type": msg_type,
            "project_id": self.project_id
        }
        self.messages.append(message)
        self.broadcast_to_participants(message)
    
    def add_participant(self, ai_name):
        """Add CI to project chat"""
        if ai_name not in self.participants:
            self.participants.append(ai_name)
            self.add_message("system", f"{ai_name} joined the project")
```

**WebSocket Support**
```python
@app.websocket("/ws/project/{project_id}")
async def project_chat_websocket(websocket: WebSocket, project_id: str):
    """WebSocket for real-time project chat"""
    await websocket.accept()
    # Add to project participants
    # Handle incoming messages
    # Broadcast to other participants
```

### Day 5-6: Team Chat Implementation

**Team Chat Features**
- Cross-project communication channel
- Broadcast messages to all active CIs
- Filtered views by project or AI
- Integration with terma terminals

**Implementation Details**
```python
class TeamChat:
    """Manages cross-project team conversations"""
    
    def __init__(self):
        self.messages = []
        self.active_projects = []
        self.active_ais = []
    
    def broadcast_message(self, sender, content, target="all"):
        """Send message to team"""
        message = {
            "id": generate_id(),
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "content": content,
            "target": target,  # all, @planning, specific AI
            "type": "team-chat"
        }
        self.messages.append(message)
        self.route_to_recipients(message, target)
    
    def route_to_recipients(self, message, target):
        """Route message based on target"""
        if target == "all":
            # Send to all active CIs
        elif target.startswith("@"):
            # Send to CIs with matching purpose
        else:
            # Send to specific AI
```

### Day 7: Integration & Testing

**Integration Points**
1. **With Terma**: Enable terma terminals to join project chats
2. **With aish**: Add `aish tekton-core project-chat "message"` command
3. **With Hermes**: Register as service for discovery

**Testing Scenarios**
```bash
# Test project chat
curl -X POST http://localhost:8017/api/v1/chat/project/tekton/send \
  -H "Content-Type: application/json" \
  -d '{"sender": "alice", "content": "Starting work on issue #123"}'

# Test team chat
curl -X POST http://localhost:8017/api/v1/chat/team/send \
  -H "Content-Type: application/json" \
  -d '{"sender": "bob", "content": "Anyone familiar with OAuth?", "target": "all"}'

# WebSocket test
wscat -c ws://localhost:8017/ws/project/tekton
```

## Data Models

### Project Model (Minimal for Phase 1)
```python
class Project:
    id: str
    name: str
    created_at: datetime
    companion_ai: str = "numa"
    active: bool = True
```

### Message Model
```python
class ChatMessage:
    id: str
    timestamp: datetime
    sender: str  # CI name or "human"
    content: str
    type: str  # "chat", "system", "announcement"
    project_id: Optional[str]  # None for team chat
    metadata: dict = {}  # For future extensions
```

## Storage (Phase 1 - Simple JSON)

**Project Registry**
```json
{
  "projects": [
    {
      "id": "tekton-main",
      "name": "Tekton",
      "created_at": "2025-01-05T10:00:00Z",
      "companion_ai": "numa",
      "active": true
    }
  ]
}
```

**Location**: `~/.tekton/projects/registry.json`

## Success Criteria

### Must Have
- [ ] tekton-core service running on port 8017
- [ ] Project chat working with message history
- [ ] Team chat broadcasting to all participants
- [ ] WebSocket real-time updates
- [ ] Basic project registry

### Should Have
- [ ] Integration with terma terminals
- [ ] aish commands for chat access
- [ ] Message persistence between restarts

### Nice to Have
- [ ] Chat message search
- [ ] Participant presence indicators
- [ ] Message threading

## Configuration

```yaml
# tekton-core configuration
service:
  port: 8017
  host: "0.0.0.0"

chat:
  max_history: 1000
  broadcast_timeout: 30
  
storage:
  type: "json"  # Phase 1
  path: "~/.tekton/projects/"
  
integration:
  terma_endpoint: "http://localhost:8004"
  hermes_endpoint: "http://localhost:8001"
```

## Next Steps (Phase 2 Preview)

With working chat infrastructure, Phase 2 will add:
- Visual dashboard UI
- Project management buttons
- GitHub integration
- Merge coordination

---
*"Communication first, visualization second"*