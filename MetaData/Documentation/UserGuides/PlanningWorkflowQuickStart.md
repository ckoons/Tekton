# Planning Workflow Quick Start

Get started with Tekton's Planning Team Workflow in 5 minutes!

## Quick Overview

The Planning Team transforms your ideas into working code through Development Sprints. Everything follows the same pipeline, but simpler tasks automatically skip unnecessary steps.

```
Idea → Proposal → Sprint → Tasks → Workflows → Validation → Merge → Done!
```

## Your First Sprint (Bug Fix Example)

### 1. Create a Proposal in Telos

Navigate to **Telos** → **New Proposal**

```
Name: Fix Login Timeout
Purpose: Users getting logged out too quickly
Description: Sessions expire after 5 minutes instead of 30
Template: break_fix
Requirements: 
- Sessions should last 30 minutes
- Remember me option should extend to 7 days
```

Click **Save** - Your proposal appears as a card.

### 2. Convert to Sprint

Click **Sprint** button on your proposal card.

This creates a Development Sprint and sends it to Prometheus.

### 3. Watch It Flow

The sprint automatically flows through the pipeline:

- **Prometheus** schedules it (Status: Ready)
- **Metis** evaluates and skips (no complex task breakdown needed for simple fixes)
- **Harmonia** skips (no complex workflow orchestration needed)  
- **Synthesis** validates the fix
- **Planning Team** reviews (or auto-approves for simple fixes)
- **TektonCore** assigns to next available Coder

### 4. Coder Implementation

Coder-A receives the sprint:
```bash
# Automated by TektonCore
git checkout -b sprint/Coder-A
# Coder makes changes
# Tests locally
git add .
git commit -m "Fix session timeout configuration"
git merge main  # Resolve any conflicts locally
```

### 5. Submit for Merge

Coder-A sends merge request:
```json
POST /tekton/workflow
{
  "dest": "tekton",
  "payload": {
    "action": "merge_sprint",
    "branch": "sprint/Coder-A",
    "sprint_name": "Fix_Login_Timeout"
  }
}
```

### 6. Automatic Completion

- TektonCore merges to main
- Sprint marked Complete
- Coder-A gets next sprint
- You can push to fork or create PR

## Common Sprint Types

### Feature Development
```
Template: feature_development
Path: Full pipeline (all phases)
Time: 1-2 days
```

### Documentation Update  
```
Template: documentation
Path: Telos → Prometheus → TektonCore
Time: 1-2 hours
```

### Hotfix
```
Template: hotfix
Path: Telos → Synthesis → TektonCore  
Time: 2-4 hours
Branch: sprint/hotfix-{date}
```

### Retrospective Follow-up
```
Template: (auto-selected)
Path: Based on action complexity
Time: Varies
```

## Key Commands

### Check Sprint Status
Look in any sprint directory for `DAILY_LOG.md`:
```
/MetaData/DevelopmentSprints/Your_Sprint/DAILY_LOG.md
```

### Find Your Sprints
- **Proposed**: Telos Dashboard
- **Scheduled**: Prometheus Dashboard  
- **In Progress**: TektonCore Dashboard
- **Completed**: `/Completed/` directory

### Manual Phase Skip
If a sprint gets stuck, from any component dashboard:
- Click **Skip** to advance to next phase
- System maintains audit trail

## Tips for Success

### 1. Use Templates
Don't reinvent the wheel:
- `break_fix` - For bugs
- `feature_development` - For new features
- `documentation` - For docs only
- `hotfix` - For urgent fixes

### 2. Keep Proposals Simple
- Clear one-line purpose
- Bullet point requirements
- Link to issues/discussions

### 3. Let It Flow
- Don't micromanage phases
- Trust auto-skip logic
- Intervene only when stuck

### 4. Learn from Retrospectives
After each sprint:
- What went well?
- What was slow?
- Create template for next time

## Quick Troubleshooting

**Sprint stuck?**
1. Check component dashboard
2. Click "Skip" if appropriate
3. Check logs if error

**Merge conflict?**
1. Go to TektonCore → Conflicts
2. Click "Fix" to notify Coder
3. Or "Redo Work" to start over

**Wrong template?**
1. Edit in Prometheus before Ready
2. Or create new sprint with correct template

## Next Steps

1. **Create your first proposal** in Telos
2. **Watch it flow** through the pipeline
3. **Check the results** in TektonCore
4. **Create a custom template** after 3-4 similar sprints

Remember: The system learns from your usage. Start simple, identify patterns, create templates, and watch your development process optimize itself!

---

Need help? Check the [full Planning Team Guide](../DeveloperGuides/PlanningTeamGuide.md) or ask in Team Chat!