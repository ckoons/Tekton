# Projects Chat Implementation Guide

## Overview

This document provides the detailed implementation plan for the Projects Chat feature in the Hephaestus UI. The implementation follows the principle of "simple, works, hard to screw up" and reuses existing patterns from the Builder Chat system.

## Implementation Strategy

### 1. HTML Structure - Minimal Changes

**File**: `/Hephaestus/ui/components/tekton/tekton-component.html`

#### Add Radio Button Control
```html
<!-- Add after existing radio buttons (line 12) -->
<input type="radio" name="tekton-tab" id="tekton-tab-projectschat" style="display: none;">
```

#### Add Menu Tab
```html
<!-- Add after conflicts tab (line 59) -->
<label for="tekton-tab-projectschat" class="tekton__tab" data-tab="projectschat"
       data-tekton-menu-item="Projects Chat"
       data-tekton-menu-component="tekton"
       data-tekton-menu-panel="projectschat-panel">
    <span class="tekton__tab-label">Projects Chat</span>
</label>
```

#### Add Submenu Bar
```html
<!-- Add after menu-bar, before content (line 83) -->
<div class="tekton__submenu-bar" data-tekton-zone="submenu" data-tekton-section="submenu">
    <div class="tekton__project-selector">
        <label for="project-ci-selector" class="tekton__selector-label">Tekton Project:</label>
        <select id="project-ci-selector" class="tekton__project-select">
            <option value="tekton">Tekton</option>
            <!-- Populated dynamically -->
        </select>
    </div>
</div>
```

#### Add Chat Panel
```html
<!-- Add after teamchat panel (line 256) -->
<div id="projectschat-panel" class="tekton__panel"
     data-tekton-panel="projectschat"
     data-tekton-panel-for="Projects Chat"
     data-tekton-panel-component="tekton"
     data-tekton-tab-content="projectschat">
    <div id="projectschat-messages" class="tekton__chat-messages"
         data-tekton-element="chat-messages"
         data-tekton-chat="projects-chat">
        <!-- Welcome message -->
        <div class="tekton__message tekton__message--system"
             data-tekton-element="chat-message"
             data-tekton-message-type="system">
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

### 2. CSS Implementation - Reuse Existing Patterns

#### Submenu Bar Styling
```css
/* Add to existing styles in tekton-component.html */
.tekton__submenu-bar {
    display: none; /* Hidden by default */
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
```

#### Tab Control Logic
```css
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

### 3. JavaScript Implementation - Minimal and Simple

#### Project CI Data Structure
```javascript
// Simple list of dicts as requested
let projectCIs = [
    {
        project_name: "Tekton",
        ci_socket: "numa-ai",
        socket_port: 42016
    }
    // Populated dynamically from API
];
```

#### Load Projects Function
```javascript
async function loadProjectCIs() {
    console.log('[TEKTON] Loading project CIs');
    
    try {
        const response = await fetch(tektonCoreUrl('/api/projects'));
        const data = await response.json();
        
        // Build projectCIs array
        projectCIs = [
            // Tekton always first
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
                    ci_socket: `project-${project.name.toLowerCase()}-ai`,
                    socket_port: 42100 + index
                });
            });
        
        // Populate dropdown
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

#### Send Projects Chat Function
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
    
    // Clear input
    chatInput.value = '';
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Send to backend
    sendToProjectCI(selectedProject, message, projectCI);
}
```

#### Backend Communication
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
        
        // Add CI response to chat
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

#### Integration with Existing Chat System
```javascript
// Modify existing tekton_sendChat function
function tekton_sendChat() {
    // ... existing code ...
    
    // Determine active chat type
    const activeTab = tektonContainer.querySelector('.tekton__tab--active');
    const chatType = activeTab.getAttribute('data-tab');
    
    if (chatType === 'projectschat') {
        // Route to projects chat
        sendProjectsChat();
        return false;
    }
    
    // ... rest of existing code ...
}
```

### 4. Backend Implementation

#### New API Endpoint
```python
# Add to /tekton-core/tekton/api/projects.py

@router.post("/api/projects/chat")
async def projects_chat(request: dict):
    """Send message to project CI"""
    project_name = request.get("project_name")
    message = request.get("message")
    ci_socket = request.get("ci_socket")
    
    if not all([project_name, message, ci_socket]):
        raise HTTPException(400, "Missing required fields")
    
    # Get project CI port
    project_ci_port = get_project_ci_port(project_name)
    
    # Send to CI using socket pattern
    try:
        response = await send_to_project_ci_socket(
            project_ci_port, 
            f"[Project: {project_name}] {message}"
        )
        
        return {
            "response": response,
            "project_name": project_name,
            "ci_socket": ci_socket
        }
        
    except Exception as e:
        logger.error(f"Projects chat failed: {e}")
        raise HTTPException(500, f"CI communication failed: {str(e)}")
```

#### Socket Communication Helper
```python
# Add to projects.py

import socket
import json
import asyncio

async def send_to_project_ci_socket(port: int, message: str) -> str:
    """Send message to project CI via socket"""
    try:
        # Use same pattern as aish MessageHandler
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(20)  # 20 second timeout
        
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
        return f"Error: Unable to reach {port}"

def get_project_ci_port(project_name: str) -> int:
    """Get socket port for project CI"""
    if project_name.lower() == "tekton":
        return 42016  # numa-ai
    
    # Calculate port for other projects
    # This is simplified - real implementation would use project registry
    project_index = hash(project_name) % 1000
    return 42100 + project_index
```

### 5. Integration Points

#### With Existing Chat System
- **Reuse chat input**: Same `tekton-chat-input` element
- **Reuse clear button**: Same `clear-chat-btn` logic
- **Reuse message styling**: Same CSS classes for messages

#### With Project Management
- **Project loading**: Called when dashboard loads
- **Project updates**: Refresh when projects change
- **Project removal**: Handle CI cleanup

#### With CI Communication
- **Socket pattern**: Same as aish MessageHandler
- **Error handling**: Same patterns as existing chat
- **Context injection**: Follow terma message patterns

### 6. Testing Strategy

#### Unit Tests
```javascript
// Test project CI loading
function testLoadProjectCIs() {
    // Mock API response
    // Verify projectCIs array
    // Check dropdown population
}

// Test message sending
function testSendProjectsChat() {
    // Mock user input
    // Verify message formatting
    // Check UI updates
}
```

#### Integration Tests
```python
# Test socket communication
async def test_projects_chat_socket():
    # Start mock CI on test port
    # Send test message
    # Verify response format
    
# Test API endpoint
async def test_projects_chat_api():
    # Mock project registry
    # Test API call
    # Verify response
```

### 7. Error Handling

#### Frontend Error States
- **No projects**: Show "No projects available" message
- **CI unavailable**: Show "CI temporarily unavailable" 
- **Network error**: Show "Connection failed, please try again"
- **Invalid selection**: Auto-select first available project

#### Backend Error Handling
- **Socket timeout**: Return error message with retry suggestion
- **Port unavailable**: Log error and return fallback message
- **Invalid project**: Return clear error message
- **CI process down**: Attempt to restart or return status

### 8. Performance Considerations

#### Frontend Optimization
- **Lazy loading**: Only load projects when tab is active
- **Debounced input**: Prevent rapid-fire messages
- **Connection pooling**: Reuse backend connections
- **Message limits**: Cap message history length

#### Backend Optimization
- **Socket reuse**: Keep connections open where possible
- **Async handling**: Non-blocking socket operations
- **Error caching**: Cache error states to avoid repeated failures
- **Process monitoring**: Health checks for CI processes

### 9. Deployment Steps

#### Phase 1: Core Implementation
1. Add HTML structure to tekton-component.html
2. Add CSS styles for submenu and chat panel
3. Add JavaScript functions for project loading and messaging
4. Add backend API endpoint for projects chat
5. Test basic functionality

#### Phase 2: Integration
1. Integrate with existing project loading
2. Add error handling and edge cases
3. Implement socket communication helpers
4. Add performance optimizations
5. Test with multiple projects

#### Phase 3: Polish
1. Add loading states and better UX
2. Implement message persistence (optional)
3. Add keyboard shortcuts
4. Performance testing and optimization
5. Documentation and training

### 10. Maintenance

#### Regular Tasks
- **Monitor CI health**: Check socket connections
- **Update project registry**: Keep in sync with project changes
- **Port management**: Track and cleanup unused ports
- **Performance monitoring**: Track response times and errors

#### Troubleshooting
- **Check socket connectivity**: `netstat -an | grep 421xx`
- **Verify CI processes**: `ps aux | grep project-*-ai`
- **Test project loading**: Browser console logs
- **Debug message flow**: Enable debug logging

---

*This implementation provides a simple, working, and maintainable solution that integrates seamlessly with existing Tekton patterns while preparing for future CI-to-CI development workflows.*