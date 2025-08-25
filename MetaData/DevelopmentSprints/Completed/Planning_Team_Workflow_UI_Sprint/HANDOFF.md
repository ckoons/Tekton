# Planning Team Workflow UI Sprint - Handoff Document

## Current Status
**Phase**: Phase 1 (Telos) Complete, Phase 2 (Prometheus) In Progress
**Last Updated**: 2025-01-27
**Next Step**: Complete Prometheus UI Implementation

## What Was Accomplished

### Phase 0: Workflow Endpoint Standard ✅
1. Created `/shared/workflow/endpoint_template.py` for standardized workflow endpoints
2. Created `/shared/workflow/workflow_handler.py` with base WorkflowHandler class
3. Added `/workflow` endpoint to ALL 17 Tekton components
4. Documented in `/MetaData/Documentation/Architecture/WorkflowEndpointStandard.md`

### Phase 1: Telos UI ✅
1. Updated Telos component with dashboard-based proposal management
2. Implemented proposal cards with Edit/Remove/Sprint functionality
3. Created file-based operations for Proposals/ directory
4. Added proposal JSON template with all required fields
5. Fixed all hardcoded ports to use tektonUrl()
6. Removed subtitle, matched menu text size to other components

### Phase 2: Prometheus UI (PARTIAL) 🚧
1. Updated menu structure: Dashboard, Plans, Revise Schedule, Resources, Retrospective
2. Created Development Sprint cards UI structure
3. Added CSS for sprint cards, coder cards, retrospective items
4. Created backend API `/api/v1/sprints/` with file operations
5. Removed subtitle to match single-line header style

**Still TODO for Prometheus**:
- Connect frontend to backend API endpoints
- Implement sprint card loading from file system
- Add Remove functionality (move to Superceded/)
- Implement chat-based Edit for sprints
- Create Schedule button functionality
- Build timeline/Gantt view in Plans tab
- Populate Resources view with actual coder data
- Add retrospective template generation

## Key Context for Next Session

### Telos UI Requirements:
1. **Menu Structure**:
   - Dashboard (with cards)
   - New Proposal 
   - Requirements Chat
   - Team Chat

2. **Dashboard Cards** must show:
   - Proposal name
   - TektonCore Project
   - Status
   - Three buttons: Remove, Edit, Sprint

3. **Technical Constraints**:
   - Use CSS-first approach (copy Tekton patterns)
   - File-based storage in `/MetaData/DevelopmentSprints/Proposals/`
   - JSON format for CI editing
   - Filename = Proposal name (simple!)

4. **Important Details**:
   - Header should look like Rhetor/Terma (single line)
   - Remove button needs confirmation modal
   - Removed files go to `/Removed/` subfolder
   - Must include TektonCore project selector

## Immediate Next Steps
1. Check if Telos component exists:
   ```bash
   ls -la /Users/cskoons/projects/github/Coder-C/Telos/ui/components/
   ```

2. If not, create component structure:
   - Copy template from another component (e.g., Rhetor)
   - Update component registry in Hephaestus

3. Start with header update to match Rhetor/Terma style

4. Create proposals directory if needed:
   ```bash
   mkdir -p $TEKTON_ROOT/MetaData/DevelopmentSprints/Proposals/Removed
   ```

## Files to Reference
- `/Rhetor/ui/components/rhetor/rhetor-component.html` - For header style
- `/Terma/ui/components/terma/terma-component.html` - For card layout pattern
- `/Hephaestus/ui/server/component_registry.json` - To register Telos

## Testing Approach
1. Create sample proposal JSON files
2. Test card display and file reading
3. Verify edit/remove functionality
4. Check Sprint button (can just log for now)

## Questions to Resolve
- Does Telos component already exist?
- Should we reuse any existing proposal/requirements code?
- Any specific color scheme for proposal cards?

## Phase 2 Context (Prometheus) - READY FOR ASSESSMENT

### Instructions for Next Claude:
1. **First, carefully read the Prometheus section of SPRINT_PLAN.md** (lines 59-88)
2. **Perform a comprehensive assessment** of what exists vs what's required
3. **Assume no Prometheus changes remain** - just document what you find

### Assessment Checklist:

#### Frontend Assessment (`/Hephaestus/ui/components/prometheus/prometheus-component.html`):
- [ ] Menu structure matches sprint plan (Dashboard, Plans, Revise Schedule, Resources, Retrospective, Planning Chat, Team Chat)
- [ ] Dashboard panel exists and is set up for Development Sprint cards
- [ ] Plans panel exists with "What if built today" timeline placeholder
- [ ] Revise Schedule panel exists for Ready sprint management
- [ ] Resources panel exists for Coder assignments/capacity
- [ ] Retrospective panel exists with team improvement structure
- [ ] CSS classes defined for sprint cards, coder cards, retrospective items
- [ ] Header has no subtitle (single line like Rhetor/Terma)
- [ ] Menu font size matches Apollo (no special sizing)

#### Backend Assessment (`/Prometheus/prometheus/api/endpoints/sprints.py`):
- [ ] Sprint listing endpoint reads from `/MetaData/DevelopmentSprints/`
- [ ] Strips "_Sprint" suffix for display
- [ ] Reads DAILY_LOG.md for status tracking
- [ ] Remove endpoint moves to Superceded/ directory
- [ ] Status update appends to DAILY_LOG.md
- [ ] Ready sprints filter works
- [ ] Coder resources endpoint (may be mock data)
- [ ] Retrospective creation endpoint

#### Integration Points to Check:
- [ ] `/workflow` endpoint exists on Prometheus (check `/Prometheus/prometheus/api/fastmcp_endpoints.py`)
- [ ] Sprint endpoints are registered in app.py
- [ ] Uses landmarks with fallback imports
- [ ] No hardcoded ports in frontend
- [ ] File operations use os/shutil, not API calls

### What You Should Find:
The previous Claude session claims to have:
1. Updated the UI menu structure completely
2. Created all necessary panels
3. Added comprehensive CSS styling
4. Created a full backend API for sprint management
5. Removed the subtitle from the header

### Your Task:
1. Verify each item in the checklist above
2. Note any discrepancies between requirements and implementation
3. Document what JavaScript integration would be needed (if any)
4. Identify any missing pieces that would prevent the UI from working
5. Create a summary of findings

### Important Context:
- Sprint data lives in `/MetaData/DevelopmentSprints/*_Sprint/` directories
- Each sprint has a DAILY_LOG.md that tracks status changes
- The UI should read these files through the backend API
- No JavaScript implementation was done - just HTML/CSS structure

## Phase 3 Context (Metis)

When Phases 1-2 are complete, Metis implementation will need:

### Key Requirements:
1. **Dashboard**: Show Ready-1:Metis sprints
2. **Task Editor**: Form-based with component assignment
3. **Phases**: Drag-drop task organization
4. **Dependencies**: Visual dependency mapper
5. **Review**: Export to Harmonia workflow

### Workflow Integration:
```javascript
// Unified /workflow endpoint
POST /metis/workflow
{
  "purpose": {
    "metis": "Break down sprint into tasks",
    "harmonia": "Create CI workflows",
    "synthesis": "Validate execution"
  },
  "dest": "metis",
  "payload": {
    "sprint_name": "SprintName",
    "status": "Ready-1:Metis"
  }
}
```

### Implementation Priority:
1. /workflow endpoint first
2. Dashboard to see Ready-1 sprints
3. Task form connected to backend
4. Basic export to Harmonia
5. Polish remaining features

### Key Backend Endpoints:
- GET /api/v1/tasks - List tasks
- POST /api/v1/tasks - Create task
- POST /api/v1/tasks/decompose - CI decomposition
- POST /api/v1/dependencies - Create dependency
- GET /api/v1/dependencies/validate - Check cycles

## Phase 4 Context (Harmonia)

When Phase 3 is complete, Harmonia implementation will need:

### Key Requirements:
1. **Dashboard**: Show Ready-2:Harmonia sprints
2. **Workflows**: Visual drag-drop builder
3. **Templates**: Save/reuse workflow patterns
4. **Executions**: Real-time monitoring
5. **Component Tasks**: Route configuration
6. **Review**: Export to Synthesis

### Visual Workflow Builder:
- Node types: task, decision, parallel, join
- Drag from Metis task list
- Connect nodes to show flow
- Properties panel for configuration

### Export Format:
```json
{
  "workflow_definition": {
    "tasks": {
      "task_id": {
        "component": "telos",
        "action": "update_ui",
        "input": {...},
        "error_handler": {...}
      }
    }
  }
}
```

### Backend APIs:
- Workflow CRUD operations
- Execution monitoring via WebSocket
- Template management

## Phase 5 Context (Synthesis)

When Phase 4 is complete, Synthesis implementation will need:

### Key Requirements:
1. **Dashboard**: Show Ready-3:Synthesis sprints
2. **Validation**: Dry-run execution testing
3. **Results**: Detailed validation reports
4. **Integration**: External system checks
5. **Review**: Planning team handoff

### Validation Features:
- Dry-run mode toggle
- Play/Pause/Step controls
- Real-time execution log
- Checkpoint system
- Rollback on failure

### Export to Planning Review:
```json
{
  "validation_summary": {
    "status": "passed_with_warnings",
    "tasks": {"total": 25, "passed": 23},
    "requirements_coverage": {...}
  }
}
```

## Phase 0 Priority

**IMPORTANT**: Start with Phase 0 - Workflow Standard
1. Create shared workflow handler
2. Add navigation triggers
3. Test component communication
4. Then proceed with UI phases

### Shared Code Location:
- `/shared/workflow/workflow_handler.py`
- `/shared/workflow/workflow-handler.js`
- Documentation: `/MetaData/Documentation/Architecture/WorkflowEndpointStandard.md`

## Phase 7 Context (Tekton Core)

Tekton Core merge management implementation:

### Key Features:
1. **Dashboard Updates**:
   - Change "New Project" → "GitHub Project"
   - Add Development Sprints section
   - Style Remove button (red/white)

2. **Merges View**:
   - List sprint/Coder-* branches
   - Merge/Reject/Fix buttons
   - Auto-merge when clean

3. **Conflicts View**:
   - Human intervention queue
   - Try Merge/Redo Work/Remove buttons
   - Reset branch capability

### Workflow Messages:
```json
// Coder submits merge
{
  "dest": "tekton",
  "payload": {
    "action": "merge_sprint",
    "branch": "sprint/Coder-A",
    "sprint_name": "Sprint_Name"
  }
}
```

### Git Operations:
- Fetch, checkout main, pull
- Merge with --no-commit first
- Detect conflicts, abort if needed
- Push to origin if successful

## Common Pitfalls to Avoid

### 1. **NO HARDCODED PORTS**
- Always use `tektonUrl('component', path)` for API calls
- Casey was very clear: "NO HARD CODED PORTS"
- Example: `tektonUrl('prometheus', '/api/v1/sprints')`

### 2. **Use Existing Infrastructure**
- Don't create new API files when components already have APIs
- Prometheus runs on its own port with existing API structure
- Add endpoints to existing routers, don't create new apps

### 3. **File Operations, Not API Calls**
- For file moves (Remove, Sprint), use Python's os/shutil directly
- Don't create APIs that call other APIs for simple file operations
- Example: Moving to Removed/ should use `shutil.move()`, not HTTP calls

### 4. **Landmarks Import Pattern**
```python
try:
    from landmarks import api_contract, integration_point
except ImportError:
    # Fallback decorators
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
```

### 5. **Component Naming**
- "Plan" concept doesn't exist - use "DevelopmentSprints" and "Workflows"
- Coder-C port range is 8300+ (not 8007)
- Strip "_Sprint" suffix for display, but backend needs full name

### 6. **UI Consistency**
- Menu font size should match Apollo (no special sizing)
- Single-line headers (no subtitles)
- Use existing CSS patterns from other components

---
Ready for implementation! Next session should continue with Prometheus JavaScript integration.