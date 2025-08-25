# Sprint: Claude/Cori Recommended Enhancements

## Overview
Implement quality-of-life improvements recommended by Claude/Cori to make Tekton and aish more effective for AI-assisted development sessions. These features focus on state inspection, error handling, testing, and session continuity.

## Goals
1. **Better Observability**: Know what's happening and what happened
2. **Safer Operations**: Dry-run mode and validation before execution  
3. **Session Continuity**: Remember context between Claude Code sessions

## Phase 1: Command Output Capture & State Inspection [0% Complete]

### Tasks
- [ ] Add `--capture` flag to aish commands
  - Store output in `.tekton/aish/captures/[timestamp]_[command].txt`
  - Symlink latest to `.tekton/aish/last_output.txt`
  - Example: `aish --capture numa "test"` saves response
  
- [ ] Create `tekton status` command with JSON output
  ```json
  {
    "timestamp": "2025-01-18T10:30:00Z",
    "components": {
      "numa": {"status": "running", "port": 8316, "ai_port": 42016},
      "apollo": {"status": "stopped", "port": 8312, "ai_port": 42012}
    },
    "forwarding": {
      "numa": "alice",
      "project:Tekton": "beth"
    },
    "active_sessions": ["alice", "beth", "cari"]
  }
  ```

- [ ] Create `aish status` command showing:
  - Active forwards (AI and project)
  - Available CIs and their states
  - Recent messages (last 5)
  - Active terminals

- [ ] Create `tekton verify` health check command
  - Check all components can start
  - Verify ports are available
  - Test basic connectivity
  - Return exit code 0 if healthy

### Success Criteria
- [ ] Can capture any aish command output
- [ ] Status commands provide machine-readable output
- [ ] Health check catches common issues
- [ ] Easy to parse in scripts

### Testing
```bash
# Test capture
aish --capture numa "hello"
cat .tekton/aish/last_output.txt  # Should contain Numa's response

# Test status
tekton status --json | jq '.components.numa.status'  # "running"

# Test health
tekton verify && echo "Healthy" || echo "Issues found"
```

## Phase 2: Dry Run Mode & Validation [0% Complete]

### Tasks
- [ ] Add `--dry-run` flag to aish commands
  - Show what would happen without executing
  - Display routing decisions
  - Example output:
  ```
  $ aish --dry-run numa "test"
  [DRY RUN] Would send to: numa-ai
  [DRY RUN] Forwarding active: numa -> alice
  [DRY RUN] Message would route to: terminal alice
  [DRY RUN] No actual message sent
  ```

- [ ] Add `--dry-run` to tekton commands
  - Show what components would be affected
  - List any conflicts or issues
  - Example:
  ```
  $ tekton --dry-run restart all
  [DRY RUN] Would stop: numa, apollo, athena (3 components)
  [DRY RUN] Would start: numa, apollo, athena
  [DRY RUN] Estimated time: 15 seconds
  [DRY RUN] No actual changes made
  ```

- [ ] Create `tekton validate [component]` command
  - Check for hardcoded ports/URLs
  - Verify TektonEnviron usage
  - Scan for common anti-patterns
  - Output report:
  ```
  Validating apollo...
  ✓ No hardcoded ports found
  ✗ Hardcoded URL found at line 45: "http://localhost:8000"
  ✓ Uses TektonEnviron correctly
  ✗ Found os.environ usage at line 89
  Score: 2/4 - Needs renovation
  ```

### Success Criteria
- [ ] Dry-run prevents accidental changes
- [ ] Clear explanation of what would happen
- [ ] Validation catches real issues
- [ ] Actionable output

### Testing
```bash
# Test dry-run forward
aish --dry-run forward numa alice
# Should show forwarding would be set, but not actually set it

# Test validation
tekton validate apollo > validation_report.txt
grep "hardcoded" validation_report.txt  # Should find issues
```

## Phase 3: Enhanced Error Context [0% Complete]

### Tasks
- [ ] Create structured error format for all commands
  ```python
  {
    "error": "Component failed to start",
    "component": "numa",
    "reason": "Port 42016 already in use",
    "details": {
      "port": 42016,
      "process_using_port": "python (PID: 12345)"
    },
    "suggestions": [
      "Run 'tekton stop numa' first",
      "Or kill process 12345: 'kill 12345'"
    ],
    "log_location": "~/.tekton/logs/numa_error_2025-01-18.log"
  }
  ```

- [ ] Add `--verbose-errors` flag for detailed diagnostics
- [ ] Create error recovery suggestions
- [ ] Log detailed errors with context

### Success Criteria
- [ ] Errors tell you how to fix them
- [ ] Can diagnose issues without debugging
- [ ] Logs contain full context
- [ ] Machine-readable error format

### Testing
```bash
# Test port conflict error
# Start numa twice to trigger port error
tekton start numa
tekton start numa 2>&1 | jq '.suggestions'
# Should show "Run 'tekton stop numa' first"
```

## Phase 4: Change Tracking [0% Complete]

### Tasks
- [ ] Create `tekton changes` command
  - Track all Tekton operations in session
  - Show files modified
  - List commands executed
  - Example output:
  ```
  Session started: 2025-01-18 10:00:00
  
  Commands executed:
  - tekton start numa
  - aish forward numa alice
  - tekton stop apollo
  
  Files modified:
  - .tekton/aish/forwarding.json
  - .tekton/logs/numa.log
  
  Components affected:
  - numa (started)
  - apollo (stopped)
  ```

- [ ] Add `--since` flag for time-based filtering
- [ ] Integration with git for code changes
- [ ] Session summary on exit

### Success Criteria
- [ ] Complete audit trail of session
- [ ] Easy to see what changed
- [ ] Can filter by time/component
- [ ] Helps with sprint handoffs

### Testing
```bash
# Make some changes
tekton start numa
aish forward numa alice

# Check what changed
tekton changes --since-session-start
# Should list both operations
```

## Phase 5: Test Helpers [0% Complete]

### Tasks
- [ ] Create `tekton test [component]` command
  - Auto-discover tests in tests/[component]/
  - Run with proper environment setup
  - Colorized output
  - Summary report

- [ ] Add `tekton test --integration` for cross-component tests
- [ ] Create `aish test forwarding` to verify forwarding works
  - Send test message
  - Verify it arrives at correct destination
  - Check both CI and project forwarding

- [ ] Add `--watch` mode for continuous testing

### Success Criteria
- [ ] One command to test any component
- [ ] Clear pass/fail output
- [ ] Integration tests are easy
- [ ] Can verify forwarding works

### Testing
```bash
# Test component
tekton test apollo
# Should run all apollo tests

# Test forwarding
aish forward numa alice
aish test forwarding numa
# Should confirm message reaches alice
```

## Phase 6: Sprint & Session Management [0% Complete]

### Tasks
- [ ] Create `tekton sprint status` command
  ```
  Current Sprint: MCP_Distributed_Tekton_Sprint
  Phase: 2 - UI Migration
  Progress: 35% Complete
  
  Completed Today:
  ✓ Updated window.AIChat
  ✓ Tested Projects Chat
  
  Blocked:
  - Waiting for Casey approval on port number
  
  Next: Update Builder Chat to use MCP
  ```

- [ ] Add `tekton sprint check "task description"`
  - Marks task complete in SPRINT_PLAN.md
  - Updates percentage automatically
  - Logs to DAILY_LOG.md

- [ ] Create session save/restore
  ```bash
  # End of session
  tekton session save "Worked on MCP, stuck on port decision"
  
  # Start of next session
  tekton session restore
  Session 2025-01-18 10:00:00 by Claude/Cori:
  - Status: "Worked on MCP, stuck on port decision"  
  - Changed: 5 files
  - Pending: Port decision for MCP server
  - Continue at: /shared/aish/src/mcp/server.py:45
  ```

- [ ] Add `.tekton/sessions/` for session history

### Success Criteria
- [ ] Sprint progress visible at a glance
- [ ] Session handoffs are seamless
- [ ] Context preserved between sessions
- [ ] Checklist updates are automated

### Testing
```bash
# Test sprint tracking
tekton sprint check "Create MCP server structure"
tekton sprint status | grep "Progress"
# Should show updated percentage

# Test session management
tekton session save "Test message"
tekton session restore | grep "Test message"
# Should preserve context
```

## Phase 7: Development Helpers [0% Complete]

### Tasks
- [ ] Create `aish trace` for message path debugging
  ```bash
  $ aish trace numa "test"
  [TRACE] Input: "test" to numa
  [TRACE] Checking forwarding registry...
  [TRACE] Found: numa -> alice
  [TRACE] Routing to terminal: alice
  [TRACE] Message delivered to alice's inbox
  [TRACE] Complete: numa -> forward -> alice
  ```

- [ ] Add `tekton logs --with-context` for related logs
  - Show component interactions
  - Highlight errors
  - Time-correlated events

- [ ] Create `tekton create component` scaffolding
  - Generate proper structure
  - Include TektonEnviron setup
  - Add test skeleton
  - Follow all patterns

### Success Criteria
- [ ] Can debug message routing easily
- [ ] Logs show full context
- [ ] New components start correctly
- [ ] Less manual setup needed

### Testing
```bash
# Test message tracing
aish forward numa alice
aish trace numa "hello"
# Should show forwarding path

# Test component creation
tekton create component --name TestAI --type specialist
ls TestAI/  # Should have proper structure
```

## Technical Decisions
- Store all enhanced data in `.tekton/` subdirectories
- Use JSON for machine-readable output
- Keep commands fast - no blocking operations
- Backward compatible - new flags don't break existing usage

## Out of Scope
- GUI for these features
- Remote Tekton system support (wait for manifest system)
- Automatic error recovery (just provide suggestions)

## Files to Update
```
# New commands
/bin/tekton (add status, verify, changes, test, sprint, session, validate, create)
/shared/aish/aish (add --capture, --dry-run, trace)

# New modules
/tekton/core/session_manager.py
/tekton/core/change_tracker.py  
/tekton/core/sprint_tracker.py
/tekton/core/validator.py
/shared/aish/src/commands/trace.py
/shared/aish/src/commands/test.py

# Storage locations
/.tekton/aish/captures/
/.tekton/sessions/
/.tekton/changes/
/.tekton/sprints/
```