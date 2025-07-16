# Projects Chat Implementation Plan

## Overview

This document provides a detailed step-by-step implementation plan for the Projects Chat feature, based on the comprehensive documentation created in the previous phase.

## Implementation Phases

### Phase 1: Core Frontend Implementation (2-3 hours)

#### Step 1.1: HTML Structure Addition
**File**: `/Hephaestus/ui/components/tekton/tekton-component.html`
**Location**: Lines 11-12 (after existing radio buttons)

**Add Radio Button Control**:
```html
<input type="radio" name="tekton-tab" id="tekton-tab-projectschat" style="display: none;">
```

**Location**: Lines 59-65 (after conflicts tab)
**Add Menu Tab**:
```html
<label for="tekton-tab-projectschat" class="tekton__tab" data-tab="projectschat"
       data-tekton-menu-item="Projects Chat"
       data-tekton-menu-component="tekton"
       data-tekton-menu-panel="projectschat-panel">
    <span class="tekton__tab-label">Projects Chat</span>
</label>
```

**Location**: Line 83 (after menu-bar, before content)
**Add Submenu Bar**:
```html
<div class="tekton__submenu-bar" data-tekton-zone="submenu" data-tekton-section="submenu">
    <div class="tekton__project-selector">
        <label for="project-ci-selector" class="tekton__selector-label">Tekton Project:</label>
        <select id="project-ci-selector" class="tekton__project-select">
            <option value="tekton">Tekton</option>
        </select>
    </div>
</div>
```

**Location**: Line 256 (after teamchat panel)
**Add Chat Panel**:
```html
<div id="projectschat-panel" class="tekton__panel"
     data-tekton-panel="projectschat"
     data-tekton-panel-for="Projects Chat"
     data-tekton-panel-component="tekton"
     data-tekton-tab-content="projectschat">
    <div id="projectschat-messages" class="tekton__chat-messages"
         data-tekton-element="chat-messages"
         data-tekton-chat="projects-chat">
        <div class="tekton__message tekton__message--system">
            <div class="tekton__message-content">
                <div class="tekton__message-text">
                    <h3 class="tekton__message-title">Project CI Assistant</h3>
                    <p id="projects-chat-instructions">Select a project to chat with its Companion Intelligence.</p>
                </div>
            </div>
        </div>
    </div>
</div>
```

#### Step 1.2: CSS Implementation
**File**: `/Hephaestus/ui/components/tekton/tekton-component.html`
**Location**: Style section (around line 1117)

**Add CSS Styles**:
```css
/* Submenu Bar Styles */
.tekton__submenu-bar {
    display: none;
    flex-direction: row;
    align-items: center;
    padding: 8px 16px;
    background-color: var(--bg-tertiary, #2a2a3a);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 40px;
    gap: 12px;
}

.tekton__project-selector {
    display: flex;
    align-items: center;
    gap: 12px;
}

.tekton__selector-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary, #f0f0f0);
}

.tekton__project-select {
    padding: 6px 12px;
    background-color: var(--bg-primary, #1e1e2e);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    color: var(--text-primary, #f0f0f0);
    font-size: 14px;
    min-width: 180px;
}

.tekton__project-select:focus {
    outline: none;
    border-color: #FFA500;
    box-shadow: 0 0 0 2px rgba(255, 165, 0, 0.2);
}

/* Show submenu when Projects Chat tab is active */
#tekton-tab-projectschat:checked ~ .tekton .tekton__submenu-bar {
    display: flex !important;
}

/* Show panel when Projects Chat tab is active */
#tekton-tab-projectschat:checked ~ .tekton #projectschat-panel {
    display: flex;
    flex-direction: column;
}

/* Active tab styling */
#tekton-tab-projectschat:checked ~ .tekton .tekton__tab[data-tab="projectschat"] {
    background-color: var(--bg-tertiary, #2a2a3a);
    border-bottom: 2px solid #FFA500;
}

/* Clear button visibility for Projects Chat */
#tekton-tab-projectschat:checked ~ .tekton #clear-chat-btn {
    display: block !important;
}
```

#### Step 1.3: JavaScript Functions
**File**: `/Hephaestus/ui/components/tekton/tekton-component.html`
**Location**: Script section (around line 1120)

**Add Global Variables**:
```javascript
// Project CI data structure
let projectCIs = [
    {
        project_name: "Tekton",
        ci_socket: "numa-ai",
        socket_port: 42016
    }
];
```

**Add Load Projects Function**:
```javascript
async function loadProjectCIs() {
    console.log('[TEKTON] Loading project CIs');
    
    try {
        const response = await fetch(tektonCoreUrl('/api/projects'));
        const data = await response.json();
        
        // Reset with Tekton first
        projectCIs = [
            {
                project_name: "Tekton",
                ci_socket: "numa-ai",
                socket_port: 42016
            }
        ];
        
        // Add other projects alphabetically
        data.projects
            .filter(p => !p.is_tekton_self)
            .sort((a, b) => a.name.localeCompare(b.name))
            .forEach((project, index) => {
                projectCIs.push({
                    project_name: project.name,
                    ci_socket: `project-${project.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}-ai`,
                    socket_port: 42100 + index
                });
            });
        
        // Update dropdown
        const selector = document.getElementById('project-ci-selector');
        if (selector) {
            selector.innerHTML = '';
            projectCIs.forEach(ci => {
                const option = document.createElement('option');
                option.value = ci.project_name;
                option.textContent = ci.project_name;
                selector.appendChild(option);
            });
        }
        
    } catch (error) {
        console.error('[TEKTON] Failed to load project CIs:', error);
    }
}
```

**Add Send Projects Chat Function**:
```javascript
function sendProjectsChat() {
    console.log('[TEKTON] Sending projects chat message');
    
    const chatInput = document.getElementById('tekton-chat-input');
    const projectSelector = document.getElementById('project-ci-selector');
    
    if (!chatInput || !projectSelector) {
        console.error('[TEKTON] Missing required elements');
        return;
    }
    
    const message = chatInput.value.trim();
    const selectedProject = projectSelector.value;
    
    if (!message || !selectedProject) {
        console.log('[TEKTON] Empty message or no project selected');
        return;
    }
    
    // Find project CI info
    const projectCI = projectCIs.find(ci => ci.project_name === selectedProject);
    if (!projectCI) {
        console.error('[TEKTON] Project CI not found:', selectedProject);
        return;
    }
    
    // Add user message to chat
    const chatContainer = document.getElementById('projectschat-messages');
    const userMessage = document.createElement('div');
    userMessage.className = 'tekton__message tekton__message--user';
    userMessage.innerHTML = `
        <div class="tekton__message-content">
            <div class="tekton__message-text">${message}</div>
        </div>
    `;
    chatContainer.appendChild(userMessage);
    
    // Clear input and scroll
    chatInput.value = '';
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Send to backend
    sendToProjectCI(selectedProject, message, projectCI);
}
```

**Add Backend Communication Function**:
```javascript
async function sendToProjectCI(projectName, message, projectCI) {
    try {
        const response = await fetch(tektonCoreUrl('/api/projects/chat'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                project_name: projectName,
                message: message,
                ci_socket: projectCI.ci_socket
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Add AI response to chat
        const chatContainer = document.getElementById('projectschat-messages');
        const aiMessage = document.createElement('div');
        aiMessage.className = 'tekton__message tekton__message--ai';
        aiMessage.innerHTML = `
            <div class="tekton__message-content">
                <div class="tekton__message-text"><strong>${projectName} CI:</strong> ${data.response}</div>
            </div>
        `;
        chatContainer.appendChild(aiMessage);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
    } catch (error) {
        console.error('[TEKTON] Projects chat error:', error);
        
        // Add error message
        const chatContainer = document.getElementById('projectschat-messages');
        const errorMessage = document.createElement('div');
        errorMessage.className = 'tekton__message tekton__message--system';
        errorMessage.innerHTML = `
            <div class="tekton__message-content">
                <div class="tekton__message-text">Error: ${error.message}</div>
            </div>
        `;
        chatContainer.appendChild(errorMessage);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}
```

**Update Existing tekton_sendChat Function**:
```javascript
// Find the existing tekton_sendChat function (around line 1213)
// Add this check at the beginning, after determining chatType:

if (chatType === 'projectschat') {
    // Route to projects chat
    sendProjectsChat();
    return false;
}
```

**Add Project Loading to DOM Ready**:
```javascript
// Find the existing DOM ready handler (around line 1962)
// Add this call:

loadProjectCIs();
```

### Phase 2: Backend Implementation (1-2 hours)

#### Step 2.1: API Endpoint Implementation
**File**: `/tekton-core/tekton/api/projects.py`
**Location**: End of file

**Add Required Imports**:
```python
import socket
import json
import asyncio
from typing import Dict, Any
```

**Add Socket Communication Helper**:
```python
async def send_to_project_ci_socket(port: int, message: str) -> str:
    """Send message to project CI via socket"""
    try:
        # Use same pattern as aish MessageHandler
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(20)  # 20 second timeout
        
        # Connect to CI socket
        await asyncio.get_event_loop().run_in_executor(
            None, sock.connect, ('localhost', port)
        )
        
        # Send message
        message_data = json.dumps({'content': message}) + '\n'
        await asyncio.get_event_loop().run_in_executor(
            None, sock.send, message_data.encode()
        )
        
        # Receive response
        response_data = await asyncio.get_event_loop().run_in_executor(
            None, sock.recv, 4096
        )
        
        sock.close()
        
        # Parse response
        response = json.loads(response_data.decode())
        return response.get('content', '')
        
    except Exception as e:
        logger.error(f"Socket communication failed: {e}")
        return f"Error: Unable to reach CI on port {port}"
```

**Add Port Helper Function**:
```python
def get_project_ci_port(project_name: str) -> int:
    """Get socket port for project CI"""
    if project_name.lower() == "tekton":
        return 42016  # numa-ai port
    
    # For other projects, use base port + hash
    # This is simplified - real implementation would use project registry
    project_hash = abs(hash(project_name)) % 1000
    return 42100 + project_hash
```

**Add API Endpoint**:
```python
@router.post("/api/projects/chat")
async def projects_chat(request: dict):
    """Send message to project CI"""
    project_name = request.get("project_name")
    message = request.get("message")
    ci_socket = request.get("ci_socket")
    
    if not all([project_name, message]):
        raise HTTPException(400, "Missing required fields: project_name, message")
    
    logger.info(f"Projects chat: {project_name} -> {message[:50]}...")
    
    # Get project CI port
    project_ci_port = get_project_ci_port(project_name)
    
    # Send to CI using socket pattern
    try:
        response = await send_to_project_ci_socket(
            project_ci_port, 
            f"[Project: {project_name}] {message}"
        )
        
        logger.info(f"Projects chat response: {response[:100]}...")
        
        return {
            "response": response,
            "project_name": project_name,
            "ci_socket": ci_socket or f"project-{project_name.lower()}-ai"
        }
        
    except Exception as e:
        logger.error(f"Projects chat failed: {e}")
        raise HTTPException(500, f"CI communication failed: {str(e)}")
```

#### Step 2.2: Environment Configuration
**File**: `.env.local.coder-c` (or similar)
**Add Configuration**:
```bash
# Project CI Configuration
TEKTON_PROJECT_CI_PORT_BASE=42100
TEKTON_PROJECT_CI_ENABLED=true
```

### Phase 3: Testing and Validation (1 hour)

#### Step 3.1: Frontend Testing
**Test Checklist**:
- [ ] Projects Chat tab appears in menu
- [ ] Submenu bar shows/hides correctly
- [ ] Project dropdown populates with projects
- [ ] Chat input works with Projects Chat selected
- [ ] Messages appear in chat panel
- [ ] Clear button works for Projects Chat

**Manual Testing Steps**:
1. Open Hephaestus UI
2. Navigate to Tekton component
3. Click "Projects Chat" tab
4. Verify submenu appears with project selector
5. Select "Tekton" project
6. Send test message: "Hello, what's your status?"
7. Verify response appears in chat

#### Step 3.2: Backend Testing
**Test Socket Communication**:
```bash
# Test numa-ai connection (Tekton project)
echo '{"content": "[Project: Tekton] test message"}' | nc localhost 42016

# Test API endpoint
curl -X POST http://localhost:8010/api/projects/chat \
  -H "Content-Type: application/json" \
  -d '{"project_name": "Tekton", "message": "test message"}'
```

#### Step 3.3: Integration Testing
**Test Full Flow**:
1. Create new project in Dashboard
2. Verify project appears in Projects Chat dropdown
3. Send message to new project CI
4. Verify message routing and response

### Phase 4: Documentation Updates (30 minutes)

#### Step 4.1: Update Component Documentation
**File**: `/MetaData/ComponentDocumentation/Hephaestus/README.md`
**Add**: Reference to Projects Chat feature

#### Step 4.2: Update API Documentation
**File**: `/MetaData/ComponentDocumentation/Tekton/API_REFERENCE.md`
**Add**: Document new `/api/projects/chat` endpoint

### Phase 5: Deployment and Monitoring (30 minutes)

#### Step 5.1: Deployment Checklist
- [ ] All files updated and saved
- [ ] Backend services restarted
- [ ] Frontend cache cleared
- [ ] Environment variables updated
- [ ] Basic smoke tests passed

#### Step 5.2: Monitoring Setup
**Monitor**:
- Socket connection health on ports 42100+
- API endpoint response times
- Error rates in projects chat
- User adoption metrics

## Risk Mitigation

### High Risk Items
1. **Socket Communication**: Test thoroughly with multiple project CIs
2. **Port Conflicts**: Ensure port range 42100+ is available
3. **UI Integration**: Verify no conflicts with existing chat systems
4. **Performance**: Monitor response times with multiple projects

### Rollback Plan
1. **Frontend**: Remove HTML changes, hide tab with CSS
2. **Backend**: Disable endpoint with feature flag
3. **Configuration**: Revert environment variables
4. **Database**: No database changes required

## Success Metrics

### Immediate Success (Day 1)
- [ ] Feature accessible in UI
- [ ] Basic messaging works with Tekton project
- [ ] No errors in browser console or server logs
- [ ] Users can complete basic workflows

### Short-term Success (Week 1)
- [ ] Multiple projects working correctly
- [ ] Positive user feedback
- [ ] Stable performance metrics
- [ ] Documentation complete and accessible

### Long-term Success (Month 1)
- [ ] Regular usage by development team
- [ ] Integration with development workflows
- [ ] Foundation for Phase 2 aish commands
- [ ] Preparation for CI-to-CI development

## Next Steps After Implementation

### Phase 2 Planning
1. **aish project commands**: Design CLI integration
2. **Forwarding system**: Enable CI forwarding to terminals
3. **Project CI lifecycle**: Improve creation/termination
4. **Multi-stack coordination**: Cross-stack communication

### Phase 3 Vision
1. **CI-to-CI development**: CIs writing code for each other
2. **Repository management**: CIs managing their own repos
3. **Mentoring relationships**: Human-CI and CI-CI mentoring
4. **Autonomous workflows**: Reduced human intervention

---

*This implementation plan provides a clear path from documentation to working feature, following the "simple, works, hard to screw up" philosophy while building toward the vision of CIs as their own developers.*