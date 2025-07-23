# Sprint: CI Workflow Creation Template

## Overview
Create comprehensive workflows for CIs to effectively use Tekton tools, debug issues, and develop software. Focus on documenting real processes that work, not theoretical approaches.

## Goals
1. **Reduce Guesswork**: Clear workflows so CIs don't have to figure things out
2. **Handle Errors**: Specific steps for common problems
3. **Build Patterns**: Reusable processes for development tasks

## Phase 1: Tool Usage Workflows [0% Complete]

### Tasks
- [ ] Create "Message Routing Debug" workflow
  - Check forwarding with `aish forward list`
  - Test with self-forward
  - Verify with `aish status`
  
- [ ] Create "Output Preservation" workflow
  - When to use `aish --capture`
  - Where captures are stored
  - How to retrieve historical outputs
  
- [ ] Create "System Health Check" workflow
  - Quick check: `tekton status --json | jq '.system'`
  - Component check: `tekton status [component]`
  - When to restart vs investigate

- [ ] Create "Multi-Environment Testing" workflow
  - Using `tekton -c X status`
  - Switching between Coder environments
  - Verifying correct environment loaded

### Success Criteria
- [ ] CIs can debug routing without guessing
- [ ] Output capture becomes natural habit
- [ ] Health checks are quick and decisive

## Phase 2: Development Workflows [0% Complete]

### Tasks
- [ ] Create "Feature Development" workflow
  - Check system health first
  - Set up forwarding for testing
  - Capture important outputs
  - Verify changes in correct environment

- [ ] Create "Bug Investigation" workflow
  - Reproduce issue
  - Check component status
  - Find relevant logs
  - Test fixes incrementally

- [ ] Create "UI Development" workflow
  - Hot reload verification
  - Browser cache clearing
  - Network tab debugging
  - Console error checking

### Success Criteria
- [ ] Consistent development approach
- [ ] Faster bug resolution
- [ ] Less time lost to environment issues

## Phase 3: Troubleshooting Workflows [0% Complete]

### Tasks
- [ ] Create "Port Conflict Resolution" workflow
  - Identify conflict with `tekton status`
  - Find process using port
  - Safe termination steps

- [ ] Create "Component Not Responding" workflow
  - Status check
  - Log location and review
  - Restart procedures
  - Verification steps

- [ ] Create "Message Not Delivered" workflow
  - Check forwarding
  - Verify component running
  - Test with simple message
  - Escalation path

- [ ] Create "Environment Mismatch" workflow
  - Verify TEKTON_ROOT
  - Check loaded environment
  - Confirm correct Coder-X
  - Fix path issues

### Success Criteria
- [ ] Common issues resolved quickly
- [ ] Clear escalation paths
- [ ] Minimal downtime

## Phase 4: Error Pattern Recognition [0% Complete]

### Tasks
- [ ] Document "Connection Refused" patterns
  - Port not open
  - Service not running
  - Firewall blocking
  - Wrong endpoint

- [ ] Document "Permission Denied" patterns
  - File ownership
  - Directory permissions
  - Cross-environment access

- [ ] Document "Silent Failure" patterns
  - Exit code 0 but nothing happened
  - Partial execution
  - Timeout without error

### Success Criteria
- [ ] CIs recognize error patterns
- [ ] Know immediate fix attempts
- [ ] Understand when to escalate

## Phase 5: CI Behavioral Patterns [0% Complete]

### Tasks
- [ ] Create "Ask First" pattern
  - List intended actions
  - State assumptions
  - Request validation
  - Then implement

- [ ] Create "Test Small" pattern
  - Minimal test case
  - Verify approach
  - Then scale up

- [ ] Create "Document Success" pattern
  - What worked
  - Why it worked
  - How to repeat

### Success Criteria
- [ ] Less rework from bad assumptions
- [ ] Faster correct implementations
- [ ] Knowledge accumulation

## Phase 6: Workflow Documentation Format [0% Complete]

### Tasks
- [ ] Create workflow template structure
- [ ] Build quick reference cards
- [ ] Design decision trees
- [ ] Create example scenarios

### Template Structure
```markdown
# Workflow: [Name]

## When to Use
[Specific trigger conditions]

## Prerequisites
- [ ] Required state/tools

## Steps
1. First action → Expected result
2. Second action → Expected result
3. Decision point:
   - If X: Go to step 4a
   - If Y: Go to step 4b

## Common Issues
- Error: [message] → Fix: [action]

## Success Verification
- [ ] Check this
- [ ] Verify that

## Next Workflows
- If still broken: [Escalation workflow]
- If fixed: [Verification workflow]
```

## Technical Decisions
- Workflows must be tested and proven
- Each workflow solves a real problem
- Keep steps concrete and actionable
- Include actual commands, not abstractions

## Out of Scope
- Theoretical best practices
- Untested procedures
- Generic advice
- Platform-specific details (focus on Tekton)

## Files to Create
```
/MetaData/DevelopmentSprints/CI_Workflow_Creation_Template_Sprint/
├── Workflows/
│   ├── Tool_Usage/
│   ├── Development/
│   ├── Troubleshooting/
│   └── Error_Patterns/
├── Templates/
│   └── workflow_template.md
└── Quick_Reference/
    └── decision_trees/
```