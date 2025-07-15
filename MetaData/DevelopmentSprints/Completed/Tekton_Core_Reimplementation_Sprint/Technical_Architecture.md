# Technical Architecture: tekton-core Reimplementation

## System Overview

tekton-core becomes a visual project management hub with integrated chat and GitHub workflow management, designed for both human visual interaction and AI programmatic access.

## Architecture Principles

1. **Dashboard-First**: Visual interface is primary, API supports it
2. **Chat-Integrated**: Communication happens where work happens  
3. **Project-Centric**: Everything revolves around project contexts
4. **AI-Friendly**: Every UI action has an API/MCP equivalent
5. **Simple Storage**: Start with JSON, upgrade only when needed

## Component Architecture

```
tekton-core/
├── backend/
│   ├── api/                    # FastAPI application
│   │   ├── app.py             # Main application
│   │   ├── projects.py        # Project management
│   │   ├── chat.py            # Chat endpoints
│   │   ├── github.py          # GitHub integration
│   │   └── websocket.py       # Real-time updates
│   ├── core/
│   │   ├── project_manager.py # Project lifecycle
│   │   ├── chat_manager.py    # Chat orchestration
│   │   ├── github_client.py   # GitHub API wrapper
│   │   └── models.py          # Data models
│   └── storage/
│       └── json_store.py      # Simple JSON persistence
├── ui/
│   ├── index.html             # Single-page application
│   ├── css/
│   │   └── dashboard.css      # Bubble visualization
│   ├── js/
│   │   ├── dashboard.js       # Main controller
│   │   ├── projects.js        # Project management
│   │   ├── chat.js            # Chat interfaces
│   │   └── api.js             # Backend communication
│   └── components/            # Reusable UI components
└── scripts/                   # GitFlow helpers (Phase 3)
```

## Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  Dashboard  │────▶│   Backend   │
│    (UI)     │◀────│    (SPA)    │◀────│   (API)     │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                         │
       │                                         │
       ▼                                         ▼
┌─────────────┐                         ┌─────────────┐
│  WebSocket  │                         │   Storage   │
│ (Real-time) │                         │   (JSON)    │
└─────────────┘                         └─────────────┘
```

## Core Components

### 1. Project Manager
```python
class ProjectManager:
    """Manages project lifecycle and state"""
    
    def create_project(self, name, repo_url, companion_ai):
        # Clone repository
        # Create fork if external
        # Initialize project structure
        # Assign AI companion
        # Register in storage
    
    def clone_project(self, source_project_id, new_config):
        # Copy working directory
        # Create new repo
        # Preserve structure
        # Assign new AI
    
    def update_project(self, project_id, updates):
        # Update metadata
        # Sync with GitHub
        # Notify participants
```

### 2. Chat Manager
```python
class ChatManager:
    """Orchestrates all communication"""
    
    def __init__(self):
        self.project_chats = {}  # project_id -> ChatRoom
        self.team_chat = TeamChat()
    
    def send_project_message(self, project_id, sender, content):
        # Add to project chat
        # Notify participants
        # Store in history
        # Broadcast via WebSocket
    
    def send_team_message(self, sender, content, target="all"):
        # Route based on target
        # Notify recipients
        # Update UI
```

### 3. GitHub Integration
```python
class GitHubClient:
    """Handles all GitHub operations"""
    
    async def clone_repository(self, repo_url, target_dir):
        # Clone via git
        # Return success/failure
    
    async def create_fork(self, original_repo, fork_name):
        # Use GitHub API
        # Create fork
        # Return fork URL
    
    async def get_pull_requests(self, repo):
        # Fetch open PRs
        # Include status checks
        # Return PR list
    
    async def merge_pull_request(self, pr_id, method="squash"):
        # Approve and merge
        # Delete branch
        # Update status
```

## Storage Design

### Project Registry (`~/.tekton/projects/registry.json`)
```json
{
  "version": "1.0",
  "projects": {
    "tekton-main": {
      "id": "tekton-main",
      "name": "Tekton",
      "repo": "https://github.com/casey/Tekton",
      "upstream": null,
      "working_dir": "/Users/casey/projects/github/Tekton",
      "companion_ai": "numa",
      "created_at": "2025-01-05T10:00:00Z",
      "last_activity": "2025-01-05T15:30:00Z",
      "status": {
        "branch": "main",
        "clean": true,
        "health": "good"
      }
    }
  }
}
```

### Chat History (`~/.tekton/projects/chats/`)
```json
{
  "project_id": "tekton-main",
  "messages": [
    {
      "id": "msg-001",
      "timestamp": "2025-01-05T10:30:00Z",
      "sender": "alice",
      "content": "Starting work on auth module",
      "type": "chat"
    }
  ]
}
```

## API Design

### RESTful Endpoints
```
# Projects
GET    /api/v1/projects              # List all projects
POST   /api/v1/projects              # Create new project
GET    /api/v1/projects/{id}         # Get project details
PUT    /api/v1/projects/{id}         # Update project
DELETE /api/v1/projects/{id}         # Delete project
POST   /api/v1/projects/{id}/clone   # Clone project

# GitHub Operations  
POST   /api/v1/github/clone          # Clone repository
POST   /api/v1/github/fork           # Create fork
GET    /api/v1/github/prs/{repo}     # List PRs
POST   /api/v1/github/merge/{pr}     # Merge PR

# Chat
GET    /api/v1/chat/project/{id}     # Get project chat history
POST   /api/v1/chat/project/{id}     # Send project message
GET    /api/v1/chat/team             # Get team chat history
POST   /api/v1/chat/team             # Send team message

# WebSocket
WS     /ws/dashboard                 # Dashboard updates
WS     /ws/chat/project/{id}         # Project chat
WS     /ws/chat/team                 # Team chat
```

### MCP Tools (Future)
```python
mcp_tools = [
    # Project Management
    "list_projects",
    "get_project",
    "create_project", 
    "update_project",
    "clone_project",
    
    # Communication
    "send_project_chat",
    "send_team_chat",
    "get_chat_history",
    
    # GitHub
    "get_prs",
    "create_pr",
    "merge_pr",
    "get_pr_status",
    
    # Workflow
    "get_my_tasks",
    "update_task_status",
    "request_review"
]
```

## Security Considerations

1. **GitHub Authentication**: OAuth tokens stored securely
2. **Project Isolation**: Each project has separate working directory
3. **Chat Privacy**: Project chats visible only to participants
4. **API Security**: Authentication for all endpoints
5. **File System**: Careful path validation

## Performance Optimization

1. **Lazy Loading**: Load project details on demand
2. **Chat Pagination**: Don't load entire history
3. **WebSocket Efficiency**: Only send relevant updates
4. **Caching**: Cache GitHub API responses
5. **Async Operations**: All I/O operations async

## Deployment

### Development
```bash
cd tekton-core
./run_tekton_core.sh --dev
# Backend on http://localhost:8017
# UI on http://localhost:8017/dashboard
```

### Production
```bash
# With proper config
./run_tekton_core.sh --prod
```

### Configuration
```yaml
# config/tekton-core.yaml
service:
  port: 8017
  host: "0.0.0.0"
  
github:
  token: ${GITHUB_TOKEN}
  
storage:
  path: "~/.tekton/projects"
  
chat:
  history_limit: 1000
  
ui:
  bubble_animation: true
  theme: "dark"
```

## Integration Points

### With Terma
- Terminals can join project chats
- Terminal status shown in dashboard
- Direct messaging between terminals and projects

### With aish
- `aish tekton-core` commands for CLI access
- Project chat via aish
- Task management via aish

### With Other Components
- Register with Hermes for discovery
- Use Engram for long-term chat storage
- Prometheus for project planning

## Future Enhancements

1. **Project Templates**: Pre-configured project types
2. **Advanced Search**: Search across all projects
3. **Analytics Dashboard**: Project metrics and insights
4. **Mobile UI**: Responsive design for tablets
5. **Backup/Restore**: Project state backup

---
*"Architecture should be as simple as possible, but no simpler"*