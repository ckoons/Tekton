# Planning Team Developer Guide

## Introduction

The Planning Team is a collaborative system of specialized CIs that transform ideas into implemented code through the Development Sprint Workflow. This guide explains how to work with the Planning Team CIs and navigate the sprint process.

## Planning Team Members

### Telos - Requirements Specialist
**Purpose**: Capture ideas and transform them into actionable proposals

**Key Features**:
- Proposal templates with structured fields
- Requirements management
- Conversion to Development Sprints

**Usage**:
```bash
# Create a new proposal
1. Navigate to Telos → New Proposal
2. Fill in: Name, Purpose, Description, Requirements
3. Save to create proposal card
4. Click "Sprint" to create Development Sprint
```

### Prometheus - Strategic Planner
**Purpose**: Manage sprint lifecycle and resource allocation

**Key Features**:
- Sprint scheduling and status tracking (color-coded cards)
- Resource allocation (Coder assignment and capacity tracking)
- Timeline/Gantt visualization (CSS Grid-based)
- Retrospective management with completion workflow
- Button-driven interface following Terma pattern

**Menu Structure**:
- Dashboard - Sprint status cards with View/Edit/Update actions
- Plans - Timeline visualization showing sprint schedules
- Revise Schedule - Status update form for active sprints
- Resources - Coder workload and assignment management
- Retrospective - Create/view/edit retrospectives, complete sprints

**UI Features** (July 2025 Update):
- Color-coded buttons: View (yellow), Edit (green), Complete (purple)
- CSS-first architecture with BEM naming convention
- Footer visible on all tabs (proper positioning)
- No loading spinners - immediate responsiveness
- Comprehensive Landmarks and Semantic Tags for CI navigation
- Sprint completion moves to `/MetaData/DevelopmentSprints/Completed/`

### Metis - Task Architect
**Purpose**: Break down sprints into manageable tasks

**Key Features**:
- AI-powered task decomposition
- Dependency mapping
- Complexity estimation
- Phase organization

**When Engaged**:
- Complex features requiring breakdown
- Multi-component changes
- When PRD is required

### Harmonia - Workflow Orchestrator
**Purpose**: Create executable CI workflows

**Key Features**:
- Visual workflow designer
- Component routing
- Template management
- Execution monitoring

**When Engaged**:
- Multi-step workflows needed
- Cross-component coordination
- Complex execution patterns

### Synthesis - Validation Engineer
**Purpose**: Validate workflows before execution

**Key Features**:
- Dry-run execution
- Integration testing
- Requirements coverage
- Performance analysis

**Always Engaged For**:
- Production changes
- External integrations
- Critical path modifications

### Tekton Core - Merge Master
**Purpose**: Manage code integration and GitHub operations

**Key Features**:
- Branch merge automation
- Conflict resolution workflow
- GitHub PR/merge operations
- Coder work assignment

## Common Workflows

### 1. Simple Bug Fix

```
Telos (Proposal) → Prometheus (Schedule) → Skip to Synthesis → 
TektonCore (Merge) → Complete
```

**Template**: `break_fix`
- No PRD required
- Skip task breakdown
- Validation only
- Quick turnaround

### 2. Feature Development

```
Telos → Prometheus → Metis → Harmonia → Synthesis → 
Review → TektonCore → Complete
```

**Template**: `feature_development`
- Full pipeline engagement
- PRD and task breakdown
- Complete validation
- Planning team review

### 3. Documentation Update

```
Telos → Prometheus → Skip to TektonCore → Complete
```

**Template**: `documentation`
- Minimal validation
- No technical phases
- Direct to merge

### 4. Retrospective Action

```
Prometheus (Auto-create) → Appropriate phases based on action → Complete
```

**Template**: Based on action type
- Auto-generated from retrospective
- Pre-populated details
- Routed by complexity

## Working with Templates

### Using Existing Templates

```python
# In proposal creation
{
  "name": "Fix Login Bug",
  "template": "break_fix",
  "purpose": "Resolve authentication timeout",
  "description": "Users experiencing logout after 5 minutes"
}
```

### Creating New Templates

After identifying a pattern:

1. Document the workflow path
2. Identify required phases
3. Create template in `/MetaData/DevelopmentSprints/Templates/`
4. Test with sample sprint

### Template Structure

```json
{
  "name": "security_patch",
  "description": "Emergency security fixes",
  "requires": {
    "PRD": false,
    "task_breakdown": true,
    "workflow_design": false,
    "validation": true,
    "security_review": true
  },
  "workflow_hints": {
    "priority": "critical",
    "skip_phases": ["harmonia"],
    "branch_pattern": "sprint/security-{date}"
  },
  "default_fields": {
    "complexity": 8,
    "type": "security"
  }
}
```

## Status Management

### Checking Sprint Status

Status is tracked in `DAILY_LOG.md`:

```markdown
## Sprint Status: Ready-2:Harmonia
**Updated**: 2025-01-26T14:00:00Z
**Updated By**: Metis

Previous Status: Ready-1:Metis → Ready-2:Harmonia
```

### Manual Status Updates

When needed (rare):
```python
# Update status in DAILY_LOG.md
# Notify next component via /workflow
POST /harmonia/workflow
{
  "purpose": {"harmonia": "Process sprint"},
  "dest": "harmonia",
  "payload": {
    "action": "process_sprint",
    "sprint_name": "Sprint_Name",
    "status": "Ready-2:Harmonia"
  }
}
```

## Coder Integration

### How Coders Receive Work

1. TektonCore assigns sprint after successful merge
2. Creates branch `sprint/Coder-X`
3. Coder implements with human oversight
4. Submits merge request when complete

### Merge Flow

```
Coder-A: git merge main (local)
Coder-A: Resolve conflicts
Coder-A: POST /tekton/workflow {"action": "merge_sprint"}
TektonCore: Attempts merge
  Success → Assign next sprint
  Conflict → Request fix
  Timeout → Human intervention
```

## Best Practices

### 1. Choose the Right Template
- Start with closest matching template
- Modify as needed
- Create new template if pattern repeats

### 2. Let Phases Auto-Skip
- Don't manually advance status
- Components handle skipping intelligently
- Maintains audit trail

### 3. Use Keywords in Proposals
- "hotfix" → Urgent routing
- "docs" → Documentation template
- "retrospective" → Follow-up sprint

### 4. Monitor Phase Bottlenecks
- Check Dashboard for stuck sprints
- Use "Skip" buttons when appropriate
- Escalate to human if needed

### 5. Leverage Retrospectives
- Document what worked/didn't
- Create templates from learnings
- Continuously improve workflow

## Troubleshooting

### Sprint Stuck in Phase

1. Check component logs
2. Verify /workflow endpoint responding
3. Manual advance if needed
4. Document issue for template update

### Merge Conflicts

1. Check Conflicts UI in TektonCore
2. Try "Merge" again (may work)
3. "Redo Work" resets branch
4. "Remove" moves to Superceded

### Missing Requirements

1. Return to Telos
2. Edit proposal/sprint
3. Add requirements
4. Resume workflow

## Advanced Features

### Parallel Sprint Processing
- Multiple Coders on related sprints
- Coordinate through Harmonia
- Synthesis validates integration

### Custom Validation Rules
- Add to Synthesis configuration
- Template-specific validation
- Performance thresholds

### Workflow Monitoring
- Real-time execution in Harmonia
- WebSocket updates
- Checkpoint debugging

## Summary

The Planning Team Workflow provides a flexible, intelligent pipeline that adapts to your needs. Start with the full process, identify patterns, create templates, and watch the system optimize itself through usage. The key is consistency in the process with flexibility in the execution.