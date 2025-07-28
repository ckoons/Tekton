# Workflow Endpoint Standard

## Overview

The Workflow Endpoint Standard defines a unified API for inter-component communication in the Tekton Planning Team workflow. All components implement a `/workflow` endpoint that accepts standardized JSON messages to coordinate the planning pipeline.

## Endpoint Specification

**URL**: `POST /{component}/workflow`

**Components**: All Tekton components (Telos, Prometheus, Metis, Harmonia, Synthesis, etc.)

## JSON Message Structure

```json
{
  "purpose": {
    "component1": "What component1 should do",
    "component2": "What component2 should do",
    "component3": "What component3 should do"
  },
  "dest": "component_name",
  "payload": {
    "action": "specific_action",
    "sprint_name": "Sprint_Name",
    "status": "Current_Status",
    "data": {}
  }
}
```

### Field Definitions

**purpose** (object, required):
- Contains instructions for each component that might receive this workflow
- Key: component name (lowercase)
- Value: Description of what that component should do
- Components check their own key to understand their task

**dest** (string, required):
- Target component for this message
- Must match a valid component name
- Component ignores message if dest doesn't match

**payload** (object, required):
- **action**: Specific action to perform
- **sprint_name**: Name of the sprint (if applicable)
- **status**: Current workflow status
- **data**: Additional data specific to the action

## Standard Actions

### look_for_work
Triggered when component is clicked in navigation. Component checks for pending work.

```json
{
  "purpose": {"metis": "check for Ready-1 sprints"},
  "dest": "metis",
  "payload": {"action": "look_for_work"}
}
```

### check_work
Standard action for all components to check their workflow directory for assigned work.

```json
{
  "purpose": "check_work",
  "dest": "telos",
  "payload": {
    "component": "telos",
    "action": "look_for_work"
  }
}
```

Response format:
```json
{
  "status": "success",
  "component": "telos",
  "work_available": true,
  "work_count": 2,
  "work_items": [
    {
      "workflow_id": "planning_team_ui_2025_01_27_143045",
      "workflow_file": "planning_team_ui_2025_01_27_143045.json",
      "status": "pending",
      "component_tasks": [...]
    }
  ]
}
```

### process_sprint
Component should process a sprint at their workflow stage.

```json
{
  "purpose": {
    "metis": "Break down sprint into tasks",
    "harmonia": "Create CI workflows",
    "synthesis": "Validate execution"
  },
  "dest": "metis",
  "payload": {
    "action": "process_sprint",
    "sprint_name": "Planning_Team_Workflow_UI_Sprint",
    "status": "Ready-1:Metis"
  }
}
```

### update_status
Update sprint status in DAILY_LOG.md.

```json
{
  "purpose": {"prometheus": "Update sprint status"},
  "dest": "prometheus",
  "payload": {
    "action": "update_status",
    "sprint_name": "Sprint_Name",
    "old_status": "Ready-1:Metis",
    "new_status": "Ready-2:Harmonia"
  }
}
```

## Workflow Status Progression

The planning workflow follows this status progression:

1. **Created** → Sprint created from proposal
2. **Planning** → Initial planning phase
3. **Ready** → Ready for breakdown
4. **Ready-1:Metis** → Metis task breakdown
5. **Ready-2:Harmonia** → Harmonia workflow creation
6. **Ready-3:Synthesis** → Synthesis validation
7. **Ready-Review** → Planning team review
8. **Building** → Active development
9. **Complete** → Sprint finished
10. **Superceded** → Cancelled/replaced

## Implementation Requirements

### Shared Endpoint Template (NEW)

All components now use a standardized template for creating their workflow endpoint:

```python
# /shared/workflow/endpoint_template.py
from shared.workflow.endpoint_template import create_workflow_endpoint

# In your component's API
workflow_router = create_workflow_endpoint("telos")
app.include_router(workflow_router)
```

This provides:
- Automatic message validation
- Standard response format
- Integration with WorkflowHandler
- Support for check_work action

### Python Implementation

```python
# /shared/workflow/workflow_handler.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

class WorkflowMessage(BaseModel):
    purpose: Dict[str, str]
    dest: str
    payload: Dict[str, Any]

class WorkflowHandler:
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.router = APIRouter()
        self.router.post("/workflow")(self.handle_workflow)
    
    async def handle_workflow(self, message: WorkflowMessage):
        # Ignore if not for this component
        if message.dest != self.component_name:
            return {"status": "ignored", "reason": "wrong destination"}
        
        # Get purpose for this component
        purpose = message.purpose.get(self.component_name)
        if not purpose:
            return {"status": "error", "reason": "no purpose defined"}
        
        # Route to appropriate handler
        action = message.payload.get("action")
        if action == "look_for_work":
            return await self.look_for_work()
        elif action == "process_sprint":
            return await self.process_sprint(message.payload)
        elif action == "update_status":
            return await self.update_status(message.payload)
        else:
            return {"status": "error", "reason": "unknown action"}
    
    async def look_for_work(self):
        # Override in component
        raise NotImplementedError
    
    async def process_sprint(self, payload: Dict[str, Any]):
        # Override in component
        raise NotImplementedError
    
    async def update_status(self, payload: Dict[str, Any]):
        # Override in component
        raise NotImplementedError
```

### JavaScript Implementation

```javascript
// /shared/workflow/workflow-handler.js
class WorkflowHandler {
  constructor(componentName) {
    this.componentName = componentName;
  }
  
  async handleWorkflow(message) {
    // Ignore if not for this component
    if (message.dest !== this.componentName) {
      return {status: 'ignored', reason: 'wrong destination'};
    }
    
    // Get purpose for this component
    const purpose = message.purpose[this.componentName];
    if (!purpose) {
      return {status: 'error', reason: 'no purpose defined'};
    }
    
    // Route to appropriate handler
    const action = message.payload.action;
    switch(action) {
      case 'look_for_work':
        return await this.lookForWork();
      case 'process_sprint':
        return await this.processSprint(message.payload);
      case 'update_status':
        return await this.updateStatus(message.payload);
      default:
        return {status: 'error', reason: 'unknown action'};
    }
  }
  
  async lookForWork() {
    // Override in component
    throw new Error('Not implemented');
  }
  
  async processSprint(payload) {
    // Override in component
    throw new Error('Not implemented');
  }
  
  async updateStatus(payload) {
    // Override in component
    throw new Error('Not implemented');
  }
}
```

## Navigation Integration

Add workflow triggers to Hephaestus navigation:

```javascript
// /Hephaestus/ui/scripts/navigation.js
document.addEventListener('DOMContentLoaded', () => {
  const navItems = document.querySelectorAll('[data-component]');
  
  navItems.forEach(item => {
    item.addEventListener('click', async (e) => {
      const component = e.target.dataset.component;
      if (!component) return;
      
      try {
        const response = await fetch(`/${component}/workflow`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            purpose: {[component]: "check for work"},
            dest: component,
            payload: {action: "look_for_work"}
          })
        });
        
        const result = await response.json();
        console.log(`[NAV] ${component} workflow response:`, result);
      } catch (error) {
        console.error(`[NAV] Error calling ${component} workflow:`, error);
      }
    });
  });
});
```

## Component Handoff Pattern

Components hand off work by calling the next component's workflow endpoint:

```python
# Example: Metis handing off to Harmonia
async def export_to_harmonia(self, sprint_data):
    message = {
        "purpose": {
            "harmonia": "Create CI workflows from task breakdown"
        },
        "dest": "harmonia",
        "payload": {
            "action": "process_sprint",
            "sprint_name": sprint_data["sprint_name"],
            "status": "Ready-2:Harmonia",
            "data": sprint_data
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{HARMONIA_PORT}/workflow",
            json=message
        )
        return response.json()
```

## Status Update Pattern

After processing, components update the sprint status:

```python
# Update DAILY_LOG.md with new status
def update_sprint_status(sprint_name, new_status):
    sprint_path = f"{TEKTON_ROOT}/MetaData/DevelopmentSprints/{sprint_name}/"
    daily_log = os.path.join(sprint_path, "DAILY_LOG.md")
    
    # Append status update
    with open(daily_log, 'a') as f:
        f.write(f"\n## Sprint Status: {new_status}\n")
        f.write(f"**Updated**: {datetime.now().isoformat()}Z\n")
        f.write(f"**Updated By**: {component_name}\n\n")
```

## Testing

Each component should have workflow endpoint tests:

```python
# test_workflow.py
async def test_workflow_endpoint():
    # Test wrong destination
    response = await client.post("/workflow", json={
        "purpose": {"other": "do something"},
        "dest": "other",
        "payload": {"action": "test"}
    })
    assert response.json()["status"] == "ignored"
    
    # Test look_for_work
    response = await client.post("/workflow", json={
        "purpose": {"metis": "check for work"},
        "dest": "metis",
        "payload": {"action": "look_for_work"}
    })
    assert response.json()["status"] == "success"
```

## Components with Workflow Endpoint

As of 2025-01-27, all 17 Tekton components have been updated with the standardized workflow endpoint:

### Core Components
1. **Apollo** - Attention/Prediction
2. **Athena** - Knowledge
3. **Engram** - Memory
4. **Ergon** - Agents/Tools/MCP
5. **Hermes** - Messages/Data
6. **Noesis** - Discovery
7. **Numa** - Companion
8. **Rhetor** - LLM/Prompt/Context
9. **Sophia** - Learning
10. **Terma** - Terminal
11. **Tekton-core** - Core services

### Planning Team Components
12. **Telos** - Requirements (with proposal management)
13. **Prometheus** - Planning
14. **Metis** - Task Architecture & Management
15. **Harmonia** - Orchestration
16. **Synthesis** - Integration

### Financial Component
17. **Budget/Penia** - LLM Cost management

All components use the shared `create_workflow_endpoint()` template for consistency.

## Benefits

1. **Unified Interface**: All components speak the same language
2. **Discoverable**: Purpose field documents what each component does
3. **Extensible**: Easy to add new actions and components
4. **Debuggable**: Clear message flow and purpose
5. **Decoupled**: Components don't need to know internal details of others
6. **Standardized**: 17 components with identical endpoint behavior

## Migration Guide

For existing components:

1. Add `/workflow` endpoint using shared handler
2. Implement component-specific actions
3. Update navigation to include data-component attribute
4. Test workflow integration
5. Document component-specific purposes and actions

---

This standard ensures consistent, maintainable workflow coordination across all Tekton components.