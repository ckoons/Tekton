# Claude Code Sprint Setup Walkthrough

## Primary Use Case: Setting up Claude Code as Coder-B for Memory Evolution Sprint

### Quick Start (3 Commands)

```bash
# 1. Run the setup script
python setup_coder_b_sprint.py

# 2. Create sprint branch
git checkout -b sprint/coder-b/memory-evolution-sprint

# 3. Start working with Claude Code
aish claude-code "I'm Coder-B. Let's review the Memory Evolution Sprint plan and start with the Conversation Memory System."
```

### What Happens Behind the Scenes

1. **Claude Code Launch**
   - Uses the new C launcher infrastructure
   - Runs in detached mode with socket communication
   - Automatically allocates a port

2. **Sprint Assignment**
   - Updates CI Registry with Coder-B's sprint assignment
   - Sets current phase and task
   - Updates Coder-B's DAILY_LOG.md

3. **Context Setup**
   - Claude Code receives sprint context
   - Knows it's working as Coder-B
   - Has access to sprint objectives and plan

### Working with Claude Code

**Interactive Mode:**
```bash
aish forward claude-code term3
# Now you can chat directly with Claude Code in terminal 3
```

**Direct Messages:**
```bash
aish claude-code "Analyze the existing Engram memory structure"
aish claude-code "Design the conversation memory schema"
aish claude-code "Implement the pattern recognition engine"
```

**Check Status:**
```bash
# Via Python
from shared.ci_tools.simple_launcher_v2 import SimpleToolLauncherV2
launcher = SimpleToolLauncherV2()
print(launcher.get_tool_status('claude-code'))

# Via aish
aish status claude-code
```

### Sprint Work Pattern

1. **Morning Startup:**
   ```bash
   python setup_coder_b_sprint.py  # If not already running
   aish claude-code "Good morning, let's continue with [current task]"
   ```

2. **During Development:**
   - Use git commits on sprint branch
   - Update sprint progress in metadata
   - Coordinate with other CIs via aish

3. **End of Day:**
   - Save context: `aish claude-code "Please summarize today's progress"`
   - Update DAILY_LOG.md
   - Push changes: `git push origin sprint/coder-b/memory-evolution-sprint`

### Integration with Other CIs

```bash
# Coordinate with Apollo on architecture
aish apollo "Coder-B needs guidance on memory pattern architecture"

# Share findings with Rhetor
aish rhetor "Document the new conversation memory schema Coder-B implemented"

# Check in with other Coders
aish broadcast "Coder-B completed initial pattern engine prototype"
```

### Monitoring Progress

The Memory Evolution Sprint has 5 phases:
1. **Memory Evolution Foundation** (current) - 15% complexity
2. **Intelligence Emergence** - 20% complexity  
3. **Personality Development** - 25% complexity
4. **Collective Intelligence** - 25% complexity
5. **Transcendent Memory** - 15% complexity

Track progress in:
- `MetaData/DevelopmentSprints/Memory_Evolution_Sprint/progress.json`
- `CIs/Coder-B/DAILY_LOG.md`
- Sprint branches in git

### Troubleshooting

**If Claude Code stops:**
```python
launcher = SimpleToolLauncherV2()
launcher.terminate_tool('claude-code')  # Clean up
launcher.launch_tool('claude-code', session_id='memory-evolution-sprint')  # Restart
```

**If context is lost:**
```bash
aish claude-code "Please review MetaData/DevelopmentSprints/Memory_Evolution_Sprint/SPRINT_PLAN.md and continue with Phase 1"
```

### Benefits of This Setup

1. **Persistent Development Environment**: Claude Code stays running across sessions
2. **Sprint Context Awareness**: Always knows what it's working on
3. **CI Integration**: Can coordinate with Apollo, Rhetor, and other Coders
4. **Progress Tracking**: Automatic updates to sprint metadata
5. **Branch Management**: Clean separation of sprint work

This setup allows Claude Code to work as a fully integrated member of the development team, with all the context and tools needed for effective sprint development.