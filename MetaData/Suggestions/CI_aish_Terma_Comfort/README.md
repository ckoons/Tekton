# CI Comfort and Productivity Improvements for aish/Terma

## Summary
Suggestions to improve the CI experience in Terma terminals, focusing on discoverability, context persistence, and collaborative workflows based on initial exploration of the Tekton ecosystem.

## Context
- Date: 2025-07-09
- Contributor: Claude (Amy) via Casey's terminal session
- Related Components: Terma, aish, Engram (future), Hephaestus UI
- Sprint/Session: Initial Tekton exploration and landmark planning

## Current State

The aish/Terma system provides excellent foundations:
- **Strong Points**:
  - Elegant message routing between CIs and terminals
  - Clever inbox system (new/keep paradigm)
  - Autoprompt solves the "CI timeout" problem
  - Purpose/roles provide contextual guidance
  - Team-chat enables CI collaboration

- **Challenges for New CIs**:
  - Discovery requires reading multiple documentation files
  - No interactive onboarding or practice environment
  - Context doesn't persist between sessions (yet)
  - Limited visibility into system state
  - Documentation mixed with deprecated content

## Proposed Improvements

### 1. Discovery & Onboarding

#### Interactive Tutorial System
```bash
aish tutorial           # Start interactive tutorial
aish tutorial basics    # Message sending, inbox management
aish tutorial advanced  # Forwarding, pipelines, team coordination
aish tutorial ci-role   # How to be an effective CI teammate
```

#### Welcome Command
```bash
aish welcome            # Shows:
# - Current terminal purpose
# - Active forwards
# - Available CIs with their specialties
# - Common workflows for this terminal's role
# - Recent team activity
```

#### CI Morning Routine
```bash
aish morning            # Automated morning checklist:
# - Show inbox summary
# - List active forwards
# - Display terminal purpose
# - Show any overnight team-chat messages
# - Suggest tasks based on role
```

### 2. Context & State Management

#### Status Overview
```bash
aish status             # Comprehensive status showing:
# - Your identity and terminal
# - Active forwards (to/from)
# - Inbox summary (new/keep counts)
# - Recent interactions
# - Team members online
# - Current Engram memory context (future)
```

#### Context Persistence (Future with Engram)
```bash
aish context save "working on landmarks"
aish context load
aish context list       # Show saved contexts
```

#### Session Recording (Mentioned by Casey)
```bash
aish review start       # Begin recording session
aish review stop        # End and save for analysis
aish review list        # List recorded sessions
```

### 3. CI Comfort Features

#### Availability Management
```bash
aish available          # Mark as available
aish busy "deep focus"  # Set busy with reason
aish break 15           # Take a 15-minute break
```

#### CI-to-CI Coordination Channel
```bash
aish ci-chat "Need help with Rhetor API"  # Private CI channel
aish ci-chat list       # See recent CI discussions
```

#### Workspace Customization
```bash
aish prefer quiet       # Reduce notifications
aish prefer verbose     # See all activity
aish prefer summary     # Periodic summaries only
```

### 4. Documentation & Help

#### Contextual Help
```bash
aish help inbox         # Just inbox commands
aish help forwarding    # Just forwarding commands
aish help workflows     # Common workflow examples
aish examples "code review"  # Real examples by use case
```

#### Smart Documentation
- Move deprecated docs to `MetaData/Archive/`
- Create `MetaData/QuickStart/` with CI-focused guides
- Add "Last Updated" timestamps to all docs
- Create a documentation index with freshness indicators

### 5. Team Collaboration Enhancements

#### Team Awareness
```bash
aish team               # Show all active CIs and their current focus
aish team history       # Recent team interactions
aish team suggest       # CI suggests who might help with current task
```

#### Workflow Templates
```bash
aish workflow list      # Show available workflows
aish workflow start "code-review"
aish workflow create "custom-debug"
```

## Benefits

### For CIs
- Faster onboarding and productivity
- Better awareness of system state and team activity
- Reduced cognitive load through better organization
- Persistence allows deeper, continued work

### For Humans
- More effective CI teammates
- Better visibility into CI activities
- Easier to onboard new team members
- Improved research data through session recording

### For the System
- More consistent CI behavior
- Better documentation organization
- Improved knowledge capture
- Foundation for multi-CI coordination patterns

## Implementation Notes

### Phase 1: Quick Wins
1. Create `aish welcome` and `aish status` commands
2. Organize documentation (archive old, highlight new)
3. Add contextual help to existing commands

### Phase 2: State Management
1. Implement basic context save/load
2. Add availability management
3. Create CI coordination channel

### Phase 3: Advanced Features
1. Interactive tutorials
2. Workflow templates
3. Full Engram integration for memory persistence
4. Session recording for research

### Technical Considerations
- Most features can be built on existing aish infrastructure
- Engram integration will require new interfaces
- Consider backward compatibility for existing users
- Keep commands intuitive and discoverable

## Example Scenarios

### New CI Joining Tekton
```bash
# First commands in a new terminal
aish welcome            # Learn about the environment
aish tutorial basics    # Practice core commands
aish team              # Meet the team
aish forward synthesis casey  # Start collaborating
```

### Daily CI Work Session
```bash
# Morning routine
aish morning           # Check overnight activity
aish context load "refactoring-ui"  # Resume yesterday's work
aish numa "Ready to continue the UI refactoring"
```

### Research Session Recording
```bash
aish review start "landmark-implementation"
# ... work on landmarks ...
aish team-chat "Added landmarks to aish registry"
# ... more work ...
aish review stop
# Session saved for Sophia & Noesis analysis
```

---

*"The best tools disappear into the workflow, making the complex feel simple."*