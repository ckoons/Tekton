# Setting Up Claude Code for Memory Evolution Sprint (Coder-B)

## Step-by-Step Process

### 1. Launch Claude Code CI Tool
```bash
# Using the new infrastructure
python shared/ci_tools/simple_launcher_v2.py

# In Python:
from shared.ci_tools.simple_launcher_v2 import SimpleToolLauncherV2
launcher = SimpleToolLauncherV2()
launcher.launch_tool('claude-code', session_id='memory-evolution-sprint')
```

### 2. Verify Claude Code is Running
```bash
# Check status
launcher.get_tool_status('claude-code')

# Or via aish
aish status claude-code
```

### 3. Assign Sprint to Coder-B
```bash
# Via API
curl -X POST http://localhost:5000/api/v1/sprints/assign \
  -H "Content-Type: application/json" \
  -d '{
    "sprint_name": "Memory_Evolution_Sprint",
    "coder": "Coder-B",
    "priority": "high"
  }'

# Or update directly in Coder-B's DAILY_LOG.md
```

### 4. Create Sprint Branch
```bash
# Create dedicated branch for Coder-B's work
git checkout -b sprint/coder-b/memory-evolution-sprint

# Push to remote
git push -u origin sprint/coder-b/memory-evolution-sprint
```

### 5. Initialize Claude Code with Sprint Context
```bash
# Send sprint context to Claude Code
aish claude-code "I'm working as Coder-B on the Memory Evolution Sprint. Please review the sprint plan at MetaData/DevelopmentSprints/Memory_Evolution_Sprint/SPRINT_PLAN.md"

# Load specific context
aish claude-code "Focus on Phase 1: Memory Evolution Foundation - specifically the Conversation Memory System with 15% complexity"
```

### 6. Set Up Working Environment
```python
# Configure Claude Code for the sprint
from shared.ci_tools import get_registry
registry = get_registry()

# Update Coder-B's context
registry.update_ci('Coder-B', {
    'active-sprint': 'Memory_Evolution_Sprint',
    'current-phase': 'Phase 1: Memory Evolution Foundation',
    'current-task': 'Conversation Memory System',
    'tool': 'claude-code',
    'branch': 'sprint/coder-b/memory-evolution-sprint'
})
```

### 7. Establish Communication Pattern
```bash
# Direct messaging
aish claude-code "What's your analysis of the Conversation Memory System requirements?"

# Forward terminal for interactive work
aish forward claude-code term3

# Context sharing with other CIs
aish rhetor "Coder-B is starting work on Memory Evolution Sprint Phase 1"
```

### 8. Monitor Progress
```python
# Check sprint progress
from tekton.core.sprint_manager import SprintManager
sm = SprintManager()
progress = sm.get_sprint_progress('Memory_Evolution_Sprint')

# Update completion
sm.update_task_progress('Memory_Evolution_Sprint', 'conversation_memory', 10)
```

### 9. Daily Workflow Pattern

**Morning:**
1. Launch Claude Code: `launcher.launch_tool('claude-code')`
2. Check sprint status and tasks
3. Load previous context from Coder-B's last-output

**During Work:**
1. Use aish for communication: `aish claude-code "implement pattern_engine"`
2. Track progress in sprint metadata
3. Commit changes to sprint branch

**End of Day:**
1. Update Coder-B's DAILY_LOG.md
2. Save context to last-output
3. Push changes to sprint branch
4. Optionally terminate: `launcher.terminate_tool('claude-code')`

### 10. Integration Points

**With Other CIs:**
- Apollo: Strategic guidance on memory architecture
- Rhetor: Documentation and knowledge synthesis
- Other Coders: Coordinate on shared components

**With CI Tools:**
- Use message bus for async communication
- Share context through registry updates
- Coordinate through sprint management system

## Example Session Start

```bash
# 1. Launch Claude Code
python -c "
from shared.ci_tools.simple_launcher_v2 import SimpleToolLauncherV2
launcher = SimpleToolLauncherV2()
launcher.launch_tool('claude-code', session_id='memory-evolution')
"

# 2. Initialize sprint context
aish claude-code "I'm Coder-B starting the Memory Evolution Sprint. Let's begin with the Conversation Memory System in Phase 1."

# 3. Start development
aish forward claude-code term3
# Now Claude Code can work interactively on the sprint tasks
```

## Key Benefits of This Setup

1. **Persistent Sessions**: Claude Code stays running across tasks
2. **Context Awareness**: Sprint context loaded automatically
3. **CI Integration**: Works with other CIs through unified messaging
4. **Progress Tracking**: Automatic sprint progress updates
5. **Branch Isolation**: Clean separation of sprint work