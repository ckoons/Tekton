# TektonCore Automated GitHub Merge Process

## Overview

TektonCore's automated merge process is the final stage of the Development Sprint workflow, where completed work is integrated into the main branch. This system combines intelligent conflict detection, automated clean merges, and sophisticated conflict resolution workflows to maintain development velocity while ensuring code quality.

## Architecture Components

### Core Systems

1. **SprintCoordinator** - Central orchestrator
   - Monitors sprint status via DAILY_LOG.md files
   - Coordinates between all subsystems
   - Manages the overall merge workflow

2. **DevSprintMonitor** - Sprint status tracking
   - Watches MetaData/DevelopmentSprints directory
   - Detects "Ready for Merge" status changes
   - Maintains sprint state information

3. **BranchManager** - Git operations
   - Creates sprint branches: `sprint/coder-x/sprint-name`
   - Performs dry-run merges (`git merge --no-commit`)
   - Executes actual merges and branch cleanup
   - Manages Coder-A/B/C repository coordination

4. **SprintMergeCoordinator** - Merge workflow
   - Queues merges by priority
   - Handles conflict resolution workflow
   - Coordinates human decisions when needed

## Merge Workflow States

```
Sprint Complete → Ready for Merge → Merge Queue → Dry-Run Check
                                                         ↓
                                              Clean ←→ Conflicts
                                                ↓          ↓
                                          Auto-Merge   Resolution
                                                ↓          ↓
                                             Merged    Fix/Consult/Redo
```

### State Transitions

1. **Sprint Complete**: Coder marks sprint as complete in DAILY_LOG.md
2. **Ready for Merge**: Status updated, detected by DevSprintMonitor
3. **Merge Queue**: Sprint added to priority queue
4. **Dry-Run Check**: Automated conflict detection
5. **Clean/Conflicts**: Branching based on dry-run results
6. **Auto-Merge/Resolution**: Automated or manual conflict resolution
7. **Merged**: Successfully integrated into main branch

## UI Integration

### Projects Tab
- Shows all Tekton-managed projects
- Git action buttons (Status, Pull, Push/PR) based on repository configuration
- Fork repositories: Status (green), Pull (blue), Push (gold)
- Upstream repositories: Status (green), Pull (blue), Pull Request (purple)

### Sprints Tab
- Real-time view of all sprints across all projects
- Status indicators and Coder assignments
- Direct access to Daily Log, Plan, and Handoff documents
- 3-column grid layout for easy scanning

### Merges Tab
- Shows sprints in "Ready for Merge" status
- Dry-run workflow with Execute button
- Conflict resolution modal with options:
  - Fix: AI-powered conflict resolution
  - Consult: Send back to original Coder
  - Redo: Reassign sprint with priority 1

## API Endpoints

### Sprint Status
```
GET /api/v1/sprints/status
- Returns all sprints with current status
- Includes coder assignments and task counts
```

### Merge Operations
```
GET /api/v1/sprints/merges
- Returns sprints ready for merge

POST /api/v1/sprints/merge/dry-run
- Performs git merge --no-commit
- Returns conflict information

POST /api/v1/sprints/complete-merge/{merge_id}
- Completes clean merge to main
- Updates sprint status to "Merged"

POST /api/v1/sprints/merge/fix
- AI-powered conflict resolution (placeholder)

POST /api/v1/sprints/merge/consult
- Sends conflict back to original Coder

POST /api/v1/sprints/merge/redo
- Creates new sprint with priority 1
- Deletes conflicted branch
```

## Dry-Run Merge Process

### Implementation
```python
async def dry_run_merge(self, branch_name: str, target_branch: str = "main"):
    # Save current branch
    current_branch = await self._get_current_branch()
    
    # Checkout target and update
    await self._run_git_command(["checkout", target_branch])
    await self._run_git_command(["pull", "origin", target_branch])
    
    # Attempt merge without commit
    result = await self._run_git_command(["merge", "--no-commit", "--no-ff", branch_name])
    
    if result.returncode == 0:
        # Clean merge possible
        can_merge = True
        conflicts = []
    else:
        # Detect conflicts
        conflict_files = await self._get_conflict_files()
        conflicts = self._analyze_conflicts(conflict_files)
        can_merge = False
    
    # Always abort to keep repository clean
    await self._run_git_command(["merge", "--abort"])
    await self._run_git_command(["checkout", current_branch])
    
    return can_merge, conflicts
```

### Conflict Detection
- File-level conflicts (both branches modified same file)
- Line-level conflicts (overlapping changes)
- Semantic conflicts (future enhancement)
- API contract conflicts (future enhancement)

## Conflict Resolution Workflow

### 1. Fix (AI-Powered)
**Current**: Placeholder implementation
**Future**: 
- CI analyzes conflict patterns
- Suggests resolution based on code understanding
- Applies fixes automatically when confidence is high

### 2. Consult (Original Coder)
**Current**: Sends notification to original Coder
**Future**:
- Creates task in Coder's queue
- Provides conflict context and diff
- Tracks resolution time

### 3. Redo (New Sprint)
**Process**:
1. Delete conflicted branch
2. Create new sprint with same name + "_REDO"
3. Set priority to 1 (highest)
4. Assign to available Coder
5. Original sprint marked as "Superceded"

## Priority System

### Sprint Priority (1-5, default 3)
1. **Priority 1**: Critical fixes, redos
2. **Priority 2**: High-priority features
3. **Priority 3**: Standard development (default)
4. **Priority 4**: Nice-to-have features
5. **Priority 5**: Technical debt, refactoring

### Merge Queue Priority
- Sprints processed by priority first
- Within same priority, FIFO order
- Clean merges always processed before conflicts

## Landmarks and Semantic Tags

### Backend Landmarks
```python
@architecture_decision(
    title="Dry-Run Merge Strategy",
    rationale="Detect conflicts without repository corruption",
    decided_by="Casey"
)
async def dry_run_merge(self, branch_name: str):
    pass

@api_contract(
    title="Complete Merge API",
    endpoint="/sprints/complete-merge/{merge_id}",
    method="POST"
)
async def complete_merge(merge_id: str):
    pass

@danger_zone(
    title="Concurrent Merge Operations",
    risks=["repository corruption", "lost commits"],
    mitigation="Queue-based processing, atomic operations"
)
async def merge_branch(self, branch_name: str):
    pass
```

### Frontend Semantic Tags
```html
<!-- Merge card with full semantic tagging -->
<div class="tekton__merge-card"
     data-tekton-element="merge-card"
     data-tekton-merge-id="${merge.id}"
     data-tekton-status="${merge.status}"
     data-tekton-priority="${merge.priority}">
    
    <button data-tekton-action="execute-merge"
            data-tekton-merge-target="${merge.id}"
            data-tekton-trigger="dry-run">
        Execute
    </button>
</div>

<!-- Conflict resolution modal -->
<div data-tekton-modal="merge-conflict"
     data-tekton-conflict-type="content"
     data-tekton-ai-ready="true">
    
    <button data-tekton-action="fix-conflict"
            data-tekton-ai="conflict-resolver">Fix</button>
    <button data-tekton-action="consult-coder"
            data-tekton-target="original-coder">Consult</button>
    <button data-tekton-action="redo-sprint"
            data-tekton-priority="1">Redo</button>
</div>
```

## Monitoring and Metrics

### Key Metrics
- **Clean merge rate**: Target >80%
- **Average merge time**: Target <5 minutes
- **Conflict resolution time**: Target <10 minutes
- **Redo rate**: Target <5%

### Health Indicators
- Sprint queue length
- Merge success/failure rates
- Conflict patterns and frequency
- Coder workload distribution

## Future Enhancements

### Near Term
1. **Semantic Conflict Detection**
   - Analyze code semantics beyond text diffs
   - Detect logical conflicts
   - API compatibility checking

2. **AI-Powered Resolution**
   - Learn from past conflict resolutions
   - Apply patterns automatically
   - Confidence-based automation

3. **Predictive Conflict Detection**
   - Analyze sprints before completion
   - Warn about potential conflicts early
   - Suggest coordination strategies

### Long Term
1. **Multi-Repository Coordination**
   - Manage dependencies across repositories
   - Coordinate related merges
   - Atomic multi-repo operations

2. **Advanced Workflow Templates**
   - Custom merge strategies per sprint type
   - Conditional approval workflows
   - Integration with external systems

3. **Performance Optimization**
   - Parallel dry-run processing
   - Incremental conflict detection
   - Distributed merge operations

## Best Practices

### For Developers
1. Keep sprints focused and small
2. Update DAILY_LOG.md regularly
3. Coordinate on shared components
4. Test thoroughly before marking complete

### For Planning Team
1. Review merge queue daily
2. Prioritize conflict resolution
3. Learn from conflict patterns
4. Adjust sprint planning based on conflicts

### For System Maintenance
1. Monitor queue performance
2. Analyze conflict trends
3. Update resolution strategies
4. Maintain git repository health

## Troubleshooting

### Common Issues

**Sprints not appearing in merge queue**
- Check DAILY_LOG.md status is exactly "Ready for Merge"
- Verify sprint coordinator is running
- Check API endpoint connectivity

**Dry-run failures**
- Ensure branches are up to date
- Check for uncommitted changes
- Verify git configuration

**Auto-merge failures**
- Check git credentials
- Verify push permissions
- Review branch protection rules

## Summary

TektonCore's automated merge process transforms the traditionally manual and error-prone process of code integration into an intelligent, automated workflow. By combining git operations with sprint management and AI-powered conflict resolution, we maintain high development velocity while ensuring code quality and system stability.

The system exemplifies Tekton's philosophy: let humans make important decisions while automating everything else. Clean merges flow through automatically, conflicts are presented clearly for resolution, and the entire process learns and improves over time.

---

*Last Updated: 2025-01-31*
*Version: 1.0*