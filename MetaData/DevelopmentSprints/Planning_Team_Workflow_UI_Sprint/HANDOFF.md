# Planning Team Workflow UI Sprint - Handoff Document

## Current Status
**Phase**: Planning Complete
**Next Step**: Begin Phase 1 Implementation

## What Was Accomplished
1. Created comprehensive sprint plan for Planning Team Workflow UI
2. Defined Telos UI requirements with Casey
3. Established JSON structures for proposals and development sprints
4. Documented workflow: Idea → Proposal → Development Sprint

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

## Phase 2 Context (Prometheus)

When Phase 1 is complete, Prometheus implementation will need:

### Key Requirements:
1. **Dashboard**: Read all `*_Sprint/` directories
2. **Status tracking**: In DAILY_LOG.md
3. **Menu items**: Dashboard, Plans, Revise Schedule, Resources, Retrospective, Planning Chat, Team Chat
4. **Card display**: Strip "_Sprint" suffix from names
5. **Retrospective**: Structured JSON + team chat transcript

### Directory Structure:
```
/MetaData/DevelopmentSprints/
├── Active_Sprint_1/
├── Another_Sprint/
├── Superceded/        (for removed sprints)
└── Completed/         (with RETROSPECTIVE.json)
```

### Status Flow:
Planning → Ready → Building → Complete → Superceded

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
- POST /api/v1/tasks/decompose - AI decomposition
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

---
Ready for implementation! Next session should start with Phase 0 shared components.