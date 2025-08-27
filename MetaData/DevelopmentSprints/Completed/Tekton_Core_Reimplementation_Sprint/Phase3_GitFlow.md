# Phase 3: GitFlow Automation (Optional)

## Overview

Add minimal GitFlow automation to support CI terminals working independently. This phase is optional and should only be implemented if the manual workflow from Phases 1-2 proves successful but needs efficiency improvements.

## Timeline: Week 4 (If Desired)

### Day 1-2: AI-Friendly Scripts

**Create GitFlow Helper Scripts**
```bash
tekton-core/scripts/
├── create-feature-branch.sh
├── run-tests.sh
├── create-pr.sh
├── check-merge-ready.sh
└── cleanup-branch.sh
```

**Example: create-feature-branch.sh**
```bash
#!/bin/bash
# Usage: ./create-feature-branch.sh <issue-number> <branch-description>

ISSUE_NUMBER=$1
DESCRIPTION=$2
TERMINAL_NAME=$TEKTON_NAME

if [ -z "$ISSUE_NUMBER" ] || [ -z "$DESCRIPTION" ]; then
    echo "Usage: $0 <issue-number> <branch-description>"
    exit 1
fi

BRANCH_NAME="feature/${TERMINAL_NAME}-${ISSUE_NUMBER}-${DESCRIPTION}"

# Create and checkout branch
git checkout -b "$BRANCH_NAME"

# Notify tekton-core
curl -X POST http://localhost:8017/api/v1/gitflow/branch-created \
    -H "Content-Type: application/json" \
    -d "{
        \"issue\": $ISSUE_NUMBER,
        \"branch\": \"$BRANCH_NAME\",
        \"terminal\": \"$TERMINAL_NAME\"
    }"

echo "Created branch: $BRANCH_NAME"
```

### Day 3-4: CI Terminal Prompts

**Add GitFlow Prompts to aish**
```python
# In aish terminal, add GitFlow awareness

class GitFlowAssistant:
    """Helps CI terminals follow GitFlow"""
    
    def suggest_next_action(self, project_state):
        """Suggest next GitFlow step based on state"""
        
        if not project_state.has_branch:
            return "Create feature branch: ./scripts/create-feature-branch.sh ISSUE_NUM description"
        
        elif project_state.has_uncommitted_changes:
            return "Commit your changes: git add . && git commit -m 'Your message'"
        
        elif not project_state.tests_run:
            return "Run tests: ./scripts/run-tests.sh"
        
        elif project_state.tests_passing and not project_state.has_pr:
            return "Create PR: ./scripts/create-pr.sh"
        
        else:
            return "Branch ready for review. Check PR status."
```

**Integration with Terminal Sessions**
```bash
# When CI starts work
aish tekton-core assign-issue 123 alice

# tekton-core responds with
"Issue #123 assigned. Suggested commands:
1. cd /path/to/project
2. ./scripts/create-feature-branch.sh 123 add-caching
3. Start development"
```

### Day 5-6: Automated Workflows

**Simple Automation Rules**
```python
class GitFlowAutomation:
    """Minimal automation for common patterns"""
    
    async def on_tests_pass(self, project_id, branch):
        """When tests pass, suggest PR creation"""
        await self.notify_terminal(
            f"Tests passed on {branch}. Ready to create PR? Run: ./scripts/create-pr.sh"
        )
    
    async def on_pr_approved(self, project_id, pr_id):
        """When PR approved, offer to merge"""
        await self.notify_terminal(
            f"PR #{pr_id} approved! Merge with: tekton-core merge-pr {pr_id}"
        )
    
    async def on_merge_complete(self, project_id, branch):
        """After merge, offer cleanup"""
        await self.notify_terminal(
            f"Merge complete! Clean up with: ./scripts/cleanup-branch.sh {branch}"
        )
```

**Optional: Issue-to-PR Tracking**
```python
# Track complete lifecycle
class IssueLifecycle:
    """Track issue from assignment to merge"""
    
    states = [
        "unassigned",
        "assigned",
        "branch_created",
        "development",
        "tests_running",
        "tests_passed",
        "pr_created",
        "pr_approved",
        "merged",
        "closed"
    ]
    
    def advance_state(self, issue_id, new_state):
        """Move issue to next state"""
        # Update tracking
        # Notify interested parties
        # Suggest next actions
```

### Day 7: Testing & Documentation

**Test Scenarios**
1. CI completes full GitFlow cycle
2. Multiple CIs work on different features
3. Handling of merge conflicts
4. Recovery from test failures

**Documentation for CIs**
```markdown
# GitFlow Quick Reference for CI Terminals

## Starting Work
1. Get assigned an issue via tekton-core
2. Create feature branch: `./scripts/create-feature-branch.sh ISSUE description`
3. Make changes and commit regularly

## Development Flow
1. Write code
2. Commit changes: `git commit -m "Clear message"`
3. Run tests: `./scripts/run-tests.sh`
4. Fix any failures and re-test

## Creating PR
1. Ensure all tests pass
2. Create PR: `./scripts/create-pr.sh`
3. Monitor PR status in tekton-core dashboard

## After Approval
1. Merge will be handled by human or senior AI
2. Clean up branch: `./scripts/cleanup-branch.sh`
3. Ready for next issue!
```

## Minimal API Additions

```python
# GitFlow endpoints (optional)
POST /api/v1/gitflow/branch-created
POST /api/v1/gitflow/tests-complete
POST /api/v1/gitflow/pr-created
GET /api/v1/gitflow/suggest-next/{issue_id}

# Automation helpers
POST /api/v1/automation/merge-pr/{pr_id}
POST /api/v1/automation/cleanup-branch
```

## Configuration

```yaml
# GitFlow automation settings
gitflow:
  enabled: false  # Opt-in only
  auto_create_pr: false
  auto_merge_approved: false
  require_tests: true
  
  scripts:
    path: "./scripts/"
    available:
      - create-feature-branch.sh
      - run-tests.sh
      - create-pr.sh
      - cleanup-branch.sh
```

## Success Criteria

### If Implemented
- [ ] Helper scripts work reliably
- [ ] CI terminals can complete full GitFlow
- [ ] Clear prompts guide CI actions
- [ ] No automation surprises
- [ ] Human retains final control

### Decision Point
Only implement Phase 3 if:
1. Manual workflow is proven but tedious
2. CIs request more structure
3. Clear patterns emerge from Phase 1-2
4. Time and energy remain

## Alternative: Skip Phase 3

If manual workflow is smooth enough:
- Document best practices from Phase 1-2
- Let CIs develop their own patterns
- Keep full human control
- Save development time

---
*"Automation should help, not replace judgment"*