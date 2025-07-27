# Telos Requirements Manager

## Overview

Telos is the Requirements Management component of the Tekton Planning Team. It provides comprehensive requirements tracking, validation, tracing, and proposal management capabilities.

## Key Features

### 1. Requirements Management
- Create, read, update, and delete requirements
- Track requirement dependencies and relationships
- Validate requirements against criteria
- Generate requirement traces

### 2. Project Management
- Organize requirements into projects
- Export projects in multiple formats (JSON, Markdown)
- Track project metadata and statistics

### 3. Proposal Management (NEW)
- Create development sprint proposals
- Edit proposals using JSON templates
- Remove proposals (moves to Proposals/Removed/)
- Convert proposals to Development Sprints

### 4. Workflow Integration
- Standard `/workflow` endpoint for inter-component communication
- Checks for assigned work in workflow directory
- Integrates with Planning Team workflow pipeline

## API Endpoints

### Standard Endpoints
- `GET /` - Component information
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /discovery` - Service discovery
- `POST /workflow` - Workflow message handler

### Requirements Endpoints
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{project_id}` - Get project details
- `PUT /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project
- `POST /api/v1/projects/{project_id}/export` - Export project

### Requirements CRUD
- `GET /api/v1/projects/{project_id}/requirements` - List requirements
- `POST /api/v1/projects/{project_id}/requirements` - Create requirement
- `GET /api/v1/projects/{project_id}/requirements/{requirement_id}` - Get requirement
- `PUT /api/v1/projects/{project_id}/requirements/{requirement_id}` - Update requirement
- `DELETE /api/v1/projects/{project_id}/requirements/{requirement_id}` - Delete requirement

### Proposal Endpoints (NEW)
- `POST /api/v1/proposals/save` - Save proposal to disk
- `GET /api/v1/proposals/load/{proposal_name}` - Load proposal from disk
- `POST /api/v1/proposals/remove` - Move proposal to Removed directory
- `POST /api/v1/proposals/sprint` - Create development sprint from proposal

## Proposal Workflow

### 1. Creating a Proposal
Users create proposals through the Telos UI with the following JSON structure:
```json
{
  "name": "ProposalName",
  "tektonCoreProject": "Tekton",
  "purpose": "Brief one-line statement of what this will achieve",
  "description": "Detailed description of the proposal",
  "requirements": [
    "Specific requirement 1",
    "Specific requirement 2"
  ],
  "successCriteria": [
    "Measurable outcome 1",
    "Measurable outcome 2"
  ],
  "template": "feature_development",
  "complexity": 5,
  "estimatedHours": 40,
  "notes": "Additional context",
  "status": "proposal",
  "created": "2025-01-27T12:00:00Z",
  "modified": "2025-01-27T12:00:00Z"
}
```

### 2. Managing Proposals
- **Edit**: Loads existing proposal data into JSON editor
- **Remove**: Moves proposal file to `MetaData/DevelopmentSprints/Proposals/Removed/`
- **Sprint**: Creates development sprint structure

### 3. Sprint Creation
When converting a proposal to a sprint, Telos:
1. Creates directory: `MetaData/DevelopmentSprints/{ProposalName}_Sprint/`
2. Generates three required files:
   - `DAILY_LOG.md` - Progress tracking
   - `HANDOFF.md` - Session handoff instructions
   - `SPRINT_PLAN.md` - Sprint overview and checklist
3. Moves proposal to `MetaData/DevelopmentSprints/Proposals/Sprints/`
4. Saves proposal data as `proposal.json` in sprint directory

## UI Integration

The Telos UI (served by Hephaestus) provides:
- Dashboard with proposal cards
- JSON editor for creating/editing proposals
- Color-coded proposal status indicators
- Action buttons for Edit/Remove/Sprint operations

### Semantic Tags
The UI implements comprehensive semantic tagging:
- `data-tekton-component="telos-proposal-editor"`
- `data-tekton-action="save-proposal"`
- `data-tekton-element="proposal-card"`
- `data-tekton-status="proposal|removed|sprint"`

## Workflow Endpoint

Telos implements the standard workflow endpoint pattern:

```python
@router.post("/workflow")
async def workflow_endpoint(message: Dict[str, Any]) -> Dict[str, Any]:
    # Handles check_work purpose
    if purpose == "check_work" and payload.get("action") == "look_for_work":
        work_items = workflow_handler.check_for_work("telos")
        return {
            "status": "success",
            "component": "telos",
            "work_available": len(work_items) > 0,
            "work_count": len(work_items),
            "work_items": work_items
        }
```

## Configuration

Telos uses the standard Tekton configuration:
- Port: Determined by `GlobalConfig.get_port('telos')` (typically 8308)
- Host: Configurable via `TELOS_HOST` environment variable
- Logging: Uses shared component logging

## Integration Points

### Prometheus Integration
- Telos can request plan creation from Prometheus
- Sends requirement data for analysis

### Hermes Integration
- Uses Hermes for AI-powered requirement refinement
- Validates requirements through LLM analysis

### Planning Team Workflow
- Participates in the Planning Team workflow pipeline
- Receives and processes workflow messages
- Exports data for downstream components

## File Structure

```
/Telos/
├── telos/
│   ├── api/
│   │   ├── app.py          # FastAPI application with proposal endpoints
│   │   └── __main__.py     # Entry point
│   ├── core/
│   │   ├── requirements_manager.py
│   │   ├── requirement.py
│   │   └── project.py
│   └── models/
│       ├── requirement.py
│       └── project.py
└── README.md

/MetaData/DevelopmentSprints/
├── Proposals/              # Active proposals
├── Proposals/Removed/      # Removed proposals
├── Proposals/Sprints/      # Proposals converted to sprints
└── {SprintName}_Sprint/    # Individual sprint directories
```

## Best Practices

1. **Proposal Naming**: Use underscores instead of spaces in proposal names
2. **JSON Validation**: Always validate proposal JSON before saving
3. **Sprint Creation**: Ensure proposal has required fields before converting
4. **File Management**: Use atomic operations for file moves
5. **Error Handling**: Provide clear user feedback for all operations

## Future Enhancements

1. **Proposal Templates**: Pre-defined templates for common proposal types
2. **Bulk Operations**: Process multiple proposals at once
3. **Search and Filter**: Find proposals by criteria
4. **Version Control**: Track proposal change history
5. **Collaboration**: Multi-user proposal editing
6. **Workflow Automation**: Auto-convert approved proposals to sprints

---

*Last Updated: 2025-01-27*
*Component Version: Part of Tekton Planning Team*