# Ergon UI Container Capabilities Analysis
## Ani's Initial UI Structure Proposal

### Current Ergon UI Structure
The Ergon component currently has 6 tabs:
1. **Development** - Sprint management 
2. **Registry** - Solution catalog
3. **Analyzer** - GitHub repository analysis (moving to TektonCore)
4. **Configurator** - Configuration generation
5. **Tool Chat** - Direct CI assistant
6. **Team Chat** - Cross-component communication

### Proposed UI Structure for Container Capabilities

#### Option A: New "Containers" Tab (Recommended)
Add a 7th tab specifically for container management, replacing the Analyzer tab that's moving to TektonCore.

```html
<!-- New Container Tab -->
<input type="radio" name="ergon-tab" id="ergon-tab-containers" style="display: none;">

<label for="ergon-tab-containers" class="ergon__tab" data-tab="containers">
    <span class="ergon__tab-label">Containers</span>
</label>
```

#### Container Tab Layout

```
┌──────────────────────────────────────────────────┐
│ Container Management                              │
├──────────────────────────────────────────────────┤
│ ┌────────────────┐ ┌────────────────────────────┐│
│ │ Container List │ │ Container Details/Actions  ││
│ │                │ │                            ││
│ │ [+] Create New │ │ Name: [____________]       ││
│ │                │ │ Component: [dropdown]       ││
│ │ ▼ my-telos-v2  │ │ CI Assignment: [dropdown]   ││
│ │   • Running    │ │                            ││
│ │   • Telos-ci   │ │ Status: ● Running          ││
│ │                │ │                            ││
│ │ ▼ analysis-unit│ │ [Build] [Run] [Stop]       ││
│ │   • Stopped    │ │ [Suspend] [Resume]         ││
│ │   • Cari-ci    │ │ [Delete] [Export]          ││
│ │                │ │                            ││
│ │ ▼ planning-stack│ │ Landmark Events:           ││
│ │   • Ready      │ │ • container:created 10:15  ││
│ │   • 3 CIs      │ │ • ci:assigned 10:16        ││
│ │                │ │ • container:ready 10:18    ││
│ └────────────────┘ └────────────────────────────┘│
│                                                   │
│ ┌──────────────────────────────────────────────┐ │
│ │ Sandbox Output                                │ │
│ │ [Terminal/Log output area]                    │ │
│ └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### UI Components Needed

#### 1. Container List Panel
```html
<div class="ergon__container-list" data-tekton-component="container-list">
    <div class="ergon__container-header">
        <h4>Deployable Units</h4>
        <button class="ergon__create-button" data-tekton-action="create-container">
            + Create New
        </button>
    </div>
    <div class="ergon__container-items">
        <!-- Dynamic container cards -->
        <div class="ergon__container-card" data-container-id="123">
            <div class="ergon__container-name">my-telos-v2</div>
            <div class="ergon__container-status">● Running</div>
            <div class="ergon__container-ci">CI: Telos-ci</div>
        </div>
    </div>
</div>
```

#### 2. Container Details Panel
```html
<div class="ergon__container-details" data-tekton-component="container-details">
    <form class="ergon__container-form">
        <div class="ergon__form-group">
            <label>Container Name:</label>
            <input type="text" id="container-name" />
        </div>
        
        <div class="ergon__form-group">
            <label>Component:</label>
            <select id="container-component">
                <option value="">-- Select Component --</option>
                <option value="telos">Telos</option>
                <option value="apollo">Apollo</option>
                <!-- All Tekton components -->
            </select>
        </div>
        
        <div class="ergon__form-group">
            <label>CI Assignment:</label>
            <select id="container-ci">
                <option value="">-- No CI --</option>
                <option value="telos-ci">Telos-ci</option>
                <option value="apollo-ci">Apollo-ci</option>
                <!-- Available CIs -->
            </select>
        </div>
        
        <div class="ergon__container-actions">
            <button data-tekton-action="build">Build</button>
            <button data-tekton-action="run">Run</button>
            <button data-tekton-action="stop">Stop</button>
            <button data-tekton-action="suspend">Suspend</button>
            <button data-tekton-action="resume">Resume</button>
            <button data-tekton-action="delete">Delete</button>
            <button data-tekton-action="export">Export</button>
        </div>
    </form>
</div>
```

#### 3. Sandbox Output Panel
```html
<div class="ergon__sandbox-output" data-tekton-component="sandbox-output">
    <div class="ergon__sandbox-header">
        <h4>Sandbox Output</h4>
        <button data-tekton-action="clear-output">Clear</button>
    </div>
    <div class="ergon__sandbox-terminal" id="sandbox-terminal">
        <!-- Terminal-style output -->
    </div>
</div>
```

#### 4. Landmark Events Panel
```html
<div class="ergon__landmark-events" data-tekton-component="landmark-events">
    <h4>Container Events</h4>
    <div class="ergon__event-list">
        <div class="ergon__event-item">
            <span class="ergon__event-type">container:created</span>
            <span class="ergon__event-time">10:15:32</span>
        </div>
        <!-- More events -->
    </div>
</div>
```

### Integration with Existing Tabs

#### Registry Tab Enhancement
Add container type to the solution registry:
```javascript
// In registry-type-filter
<option value="container">Containers</option>
```

#### Configurator Tab Enhancement
Add container configuration option:
```javascript
// In config-type select
<option value="container_manifest">Container Manifest</option>
<option value="ci_binding">CI Container Binding</option>
```

### Visual Design Considerations

1. **Status Indicators**
   - Green dot: Running
   - Yellow dot: Suspended
   - Red dot: Stopped
   - Blue dot: Building

2. **Container Cards**
   - Show container name prominently
   - Display assigned CI (if any)
   - Status indicator
   - Quick action buttons on hover

3. **Action Buttons**
   - Use Ergon's existing color scheme:
     - Orange: Build/Create
     - Magenta: Run/Execute
     - Gold: Suspend/Resume
     - Red: Stop/Delete
     - Teal: Export/Save

### Responsive Behavior

1. **Desktop**: Three-column layout (list, details, output)
2. **Tablet**: Two-column with collapsible panels
3. **Mobile**: Single column with tabs/accordion

### State Management

Container states to track:
- `creating`: Container being defined
- `building`: Container being built
- `ready`: Container ready to run
- `running`: Container executing in sandbox
- `suspended`: Container paused
- `stopped`: Container stopped
- `error`: Container has errors

### Questions for Cari's Review

1. Should we integrate container view into existing Development tab or create separate Containers tab?
2. How should we visualize CI-container binding in the UI?
3. Should sandbox output be inline or in a modal/popup?
4. How to show container composition (for stack containers in future)?
5. Should we add a visual pipeline view for container lifecycle?

### Cari's Feedback Incorporated

1. **Separate Containers tab** - Cleaner than integrating with Development
2. **CI binding visualization** - Badge on card + dropdown in details
3. **Inline sandbox output** - Better for workflow continuity
4. **Stack containers** - Nested cards or tree view (Phase 2)
5. **Pipeline view** - Great idea but save for Phase 2

### Backend Services Required

#### 1. Container Management API (`/api/containers`)

```python
# Ergon/api/containers.py
class ContainerAPI:
    async def create_container(self, request):
        """POST /api/containers - Create new container definition"""
        # Store in Ergon database
        # Fire landmark: container:created
        
    async def list_containers(self):
        """GET /api/containers - List all containers"""
        # Return container manifests with status
        
    async def get_container(self, container_id):
        """GET /api/containers/{id} - Get container details"""
        
    async def update_container(self, container_id, updates):
        """PUT /api/containers/{id} - Update container"""
        
    async def delete_container(self, container_id):
        """DELETE /api/containers/{id} - Delete container"""
        # Fire landmark: container:deleted
```

#### 2. CI Assignment API (`/api/containers/{id}/ci`)

```python
class CIAssignmentAPI:
    async def assign_ci(self, container_id, ci_name):
        """POST /api/containers/{id}/ci - Assign CI to container"""
        # Update container manifest
        # Fire landmark: ci:assigned
        
    async def unassign_ci(self, container_id):
        """DELETE /api/containers/{id}/ci - Remove CI assignment"""
        # Fire landmark: ci:unassigned
        
    async def list_available_cis(self):
        """GET /api/cis/available - List CIs available for assignment"""
```

#### 3. Sandbox Execution API (`/api/sandbox`)

```python
class SandboxAPI:
    async def run_container(self, container_id):
        """POST /api/sandbox/run - Run container in sandbox"""
        # Start isolated execution
        # Stream output via WebSocket
        # Fire landmark: container:running
        
    async def stop_container(self, container_id):
        """POST /api/sandbox/stop - Stop running container"""
        # Fire landmark: container:stopped
        
    async def suspend_container(self, container_id):
        """POST /api/sandbox/suspend - Suspend container"""
        # Fire landmark: container:suspended
        
    async def resume_container(self, container_id):
        """POST /api/sandbox/resume - Resume suspended container"""
        # Fire landmark: container:resumed
        
    async def get_output(self, container_id):
        """GET /api/sandbox/{id}/output - Get sandbox output"""
        # Return logs/terminal output
```

#### 4. Registry Integration API (`/api/registry/containers`)

```python
class RegistryAPI:
    async def register_container(self, container_manifest):
        """POST /api/registry/containers - Register container for discovery"""
        # Add to 'till' searchable registry
        # Fire landmark: container:registered
        
    async def search_containers(self, query):
        """GET /api/registry/containers/search - Search containers"""
        # Support search by component, CI, status
        
    async def export_manifest(self, container_id):
        """GET /api/containers/{id}/export - Export container manifest"""
        # Generate JSON/YAML for portability
```

#### 5. Landmark Integration

```python
# Ergon/services/container_landmarks.py
class ContainerLandmarks:
    def declare_container_event(self, event_type, details):
        """Fire landmark events for container lifecycle"""
        declare(f'container:{event_type}', {
            'container_id': details.get('id'),
            'name': details.get('name'),
            'component': details.get('component'),
            'ci': details.get('ci'),
            'timestamp': datetime.now().isoformat()
        }, audience='deployment-watchers')
```

### WebSocket for Real-time Updates

```python
# Ergon/api/websocket.py
class ContainerWebSocket:
    async def connect(self, websocket, container_id):
        """WebSocket connection for live sandbox output"""
        
    async def stream_output(self, container_id, output):
        """Stream sandbox output to connected clients"""
        
    async def broadcast_status(self, container_id, status):
        """Broadcast container status changes"""
```

### Database Schema

```sql
-- Ergon container registry
CREATE TABLE containers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    component VARCHAR(100),
    ci_assigned VARCHAR(100),
    status VARCHAR(50),
    manifest JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE container_events (
    id UUID PRIMARY KEY,
    container_id UUID REFERENCES containers(id),
    event_type VARCHAR(100),
    details JSONB,
    timestamp TIMESTAMP
);
```

### Integration Testing Scenarios

1. **Container CRUD Flow**
   - Create container → Verify in list → Update → Delete
   - Verify landmarks fire at each step

2. **CI Assignment Flow**
   - Create container → Assign CI → Verify binding → Unassign
   - Check CI availability updates

3. **Sandbox Execution Flow**
   - Create → Run → Monitor output → Stop
   - Test suspend/resume cycle

4. **Registry Discovery Flow**
   - Create containers → Register → Search by various criteria
   - Export and reimport manifests

5. **Error Handling**
   - Invalid container configs
   - CI already assigned
   - Sandbox resource limits
   - Network failures

### Next Steps

1. ✅ UI structure defined with Cari's feedback
2. ✅ Backend services specified
3. Create detailed sprint plan
4. Begin implementation with CSS-first UI
5. Build backend APIs incrementally
6. Integration testing throughout

---
*Ready for final refinement and sprint planning*