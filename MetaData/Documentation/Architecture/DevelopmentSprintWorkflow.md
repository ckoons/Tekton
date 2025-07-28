# Development Sprint Workflow Architecture

## Overview

The Development Sprint Workflow is Tekton's unified pipeline for transforming ideas into implemented code. Every change, from simple bug fixes to complex features, flows through this consistent process, with intelligent routing based on sprint type and complexity.

## Core Philosophy

**"Everything is a Development Sprint"**

Whether it's a hotfix, a new feature, documentation update, or retrospective action item - all work flows through the same pipeline. The system adapts its complexity based on the sprint's requirements, skipping unnecessary phases while maintaining quality gates where needed.

## Workflow Components

### Planning Team CIs

1. **Telos** - Requirements & Proposals
   - Captures ideas as proposals
   - Manages requirements
   - Converts proposals to Development Sprints

2. **Prometheus** - Planning & Scheduling  
   - Manages Development Sprint lifecycle
   - Resource allocation and scheduling
   - Retrospectives and continuous improvement

3. **Metis** - Task Architecture & Management
   - Decomposes sprints into manageable tasks with AI assistance
   - Comprehensive task lifecycle management (CRUD operations)
   - Manages task dependencies and relationships
   - Estimates complexity and effort hours
   - Organizes tasks into development phases
   - Provides task breakdown export to Harmonia
   - Integrates with Telos requirements system

4. **Harmonia** - Workflow Orchestration
   - Creates executable CI workflows
   - Routes tasks to components
   - Manages execution templates

5. **Synthesis** - Validation & Integration
   - Validates workflows
   - Tests integration points
   - Ensures requirements coverage

6. **Tekton Core** - Merge Management
   - Manages Coder branches
   - Handles merge conflicts
   - GitHub PR/merge operations

## Status Progression

```
Created → Planning → Ready → Ready-1:Metis → Ready-2:Harmonia → 
Ready-3:Synthesis → Ready-Review → Building → Complete → Superceded
```

### Status Definitions

- **Created**: Sprint created from proposal
- **Planning**: Initial planning phase
- **Ready**: Ready for task breakdown
- **Ready-1:Metis**: Awaiting task decomposition
- **Ready-2:Harmonia**: Awaiting workflow creation
- **Ready-3:Synthesis**: Awaiting validation
- **Ready-Review**: Planning team review
- **Building**: Active development by Coder
- **Complete**: Successfully merged
- **Superceded**: Cancelled or replaced

## Sprint Types & Templates

### Standard Templates

1. **Feature Development**
   - Full pipeline engagement
   - PRD required
   - Complete validation

2. **Break/Fix**
   - Simplified flow
   - Branch: `sprint/release-xyz`
   - Skip merge to main
   - Direct to validation

3. **Documentation Update**
   - Skip technical phases
   - Direct to TektonCore
   - Minimal validation

4. **Retrospective Follow-up**
   - Auto-generated from retrospectives
   - Pre-populated with action items
   - Assigned complexity based on scope

### Template Structure

```json
{
  "template": "break_fix",
  "requires": {
    "PRD": false,
    "task_breakdown": false,
    "workflow_design": false,
    "validation": true
  },
  "workflow_hints": {
    "branch_pattern": "sprint/release-{version}",
    "merge_target": "release",
    "skip_phases": ["metis", "harmonia"],
    "auto_advance": true
  }
}
```

## Intelligent Phase Skipping

Components check sprint requirements and auto-advance when not needed:

```python
# Component checks if it has work
if not sprint.requires.get(self.phase_requirement):
    await advance_to_next_phase(sprint)
    return {"status": "auto_advanced"}
```

This ensures:
- Simple changes move quickly
- Complex changes get full analysis
- No manual intervention for skipping
- Complete audit trail maintained

## Merge Workflow

### Coder Branch Management

1. **Assignment**: Coder-X assigned sprint, creates `sprint/Coder-X` branch
2. **Development**: Implements changes with human-in-the-loop
3. **Local Merge**: Merges with main locally, resolves conflicts
4. **Submit**: Sends merge request to TektonCore
5. **Final Merge**: TektonCore merges to origin/main

### Conflict Resolution

```
Coder submits → TektonCore attempts merge → 
  Success: Assign next sprint
  Conflict: Send fix request → Coder fixes → Resubmit
  Timeout: Human intervention via Conflicts UI
```

## Workflow Communication

All components implement the standard `/workflow` endpoint:

```json
{
  "purpose": {
    "component1": "What this component should do",
    "component2": "What that component should do"
  },
  "dest": "target_component",
  "payload": {
    "action": "process_sprint",
    "sprint_name": "Sprint_Name",
    "status": "Current_Status"
  }
}
```

## Efficiency Features

### 1. **Progressive Complexity**
- Starts simple, adds complexity only when needed
- Templates encode learned patterns
- Keyword detection for automatic template selection

### 2. **Parallel Processing**
- Multiple Coders on different sprints
- Phases can process multiple sprints simultaneously
- Non-blocking handoffs between components

### 3. **Automatic Next Sprint Assignment**
- After successful merge, Coder gets next sprint
- No idle time between tasks
- Load balancing across Coders

### 4. **Smart Routing**
- Sprint type determines path
- Requirements drive phase engagement
- Automatic status advancement

## File Organization

```
/MetaData/DevelopmentSprints/
├── Templates/              # Sprint templates
├── Proposals/              # Active proposals (pre-sprint)
│   └── Removed/           # Archived proposals
├── Active_Sprint_Name/     # Active sprints
│   ├── SPRINT_PLAN.md     # Sprint details
│   ├── DAILY_LOG.md       # Status tracking
│   └── HANDOFF.md         # Session handoffs
├── Completed/             # Finished sprints
│   └── RETROSPECTIVE.json # Team feedback
└── Superceded/           # Cancelled sprints
```

## Benefits

1. **Consistency**: One pipeline for all changes
2. **Flexibility**: Templates handle special cases
3. **Efficiency**: Phases skipped when not needed
4. **Traceability**: Complete history of decisions
5. **Quality**: Validation where it matters
6. **Automation**: Learns patterns, creates templates

## Future Enhancements

As the system matures, templates will capture more patterns:
- Security review requirements
- Performance testing needs
- Compliance checkpoints
- External dependency management

The workflow is designed to evolve through usage, becoming more efficient while maintaining quality and oversight where needed.