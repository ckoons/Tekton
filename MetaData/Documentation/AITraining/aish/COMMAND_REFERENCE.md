# aish Command Reference

Complete command reference for the AI Shell (aish) in Tekton.

## Quick Start

```bash
aish numa "Hello"              # Send message to an AI
aish list                      # Show available AIs
aish list commands             # Show this reference
```

## Complete Command List

### Core Commands

#### `aish`
Show help and usage information.
```bash
aish                           # Show help
```

#### `aish whoami`
Show identity information including user, terminal, and active forwards.
```bash
aish whoami                    # Display identity information
```

Output includes:
- Current user
- Terminal name and session (if in terma)
- Active forwards to your terminal
- Working directory and TEKTON_ROOT

#### `aish list`
List all available AI components.
```bash
aish list                      # Show all AIs with descriptions
```

#### `aish list commands`
Show all available commands with brief descriptions.
```bash
aish list commands             # Display command reference
```

#### `aish <ai-name> "message"`
Send a message to a specific AI component.
```bash
aish apollo "What patterns do you see?"
aish numa "Help me implement this feature"
aish team-chat "Status update for all AIs"
```

### Pipeline Commands

#### Piping Input
Send file contents or command output to an AI.
```bash
echo "Analyze this text" | aish rhetor
cat code.py | aish athena "Review this code"
git diff | aish synthesis "Summarize these changes"
```

#### Chaining AIs
Pass output from one AI to another.
```bash
echo "Design a feature" | aish prometheus | aish numa
aish apollo "Predict outcomes" | aish athena "Evaluate"
```

### Forwarding Commands

#### `aish forward <ai> <terminal>`
Forward messages from an AI to a terminal.
```bash
aish forward apollo bob        # Forward apollo's messages to bob's terminal
aish forward rhetor alice      # Forward rhetor's messages to alice
```

#### `aish forward list`
Show all active message forwards.
```bash
aish forward list              # Display active forwards
```

#### `aish forward remove <ai>` / `aish unforward <ai>`
Stop forwarding messages from an AI.
```bash
aish unforward apollo          # Stop forwarding apollo
aish forward remove apollo     # Alternative syntax
```

### Project Commands

#### `aish project list`
List all Tekton managed projects with their CI (Computational Instance) and forwarding status.
```bash
aish project list              # Show all projects
```

Output shows:
- Project name
- Associated CI (Computational Instance)
- Forwarding status (which terminal, if any)

#### `aish project forward <project-name>`
Forward a project's CI messages to the current terminal.
```bash
aish project forward MyWebApp  # Forward MyWebApp CI to this terminal
```

Note: Requires running in a named Terma terminal session.

#### `aish project unforward <project-name>`
Remove project CI forwarding.
```bash
aish project unforward MyWebApp # Stop forwarding MyWebApp CI
```

### Terminal Commands (Terma)

#### `aish terma inbox`
Show messages in your terminal's inbox.
```bash
aish terma inbox               # Show all inbox messages
aish terma inbox new           # Show only new messages
aish terma inbox keep          # Show kept messages
```

#### `aish terma inbox new pop`
Get and remove one new message from inbox.
```bash
aish terma inbox new pop       # Pop one message
```

#### `aish terma send <name> "message"`
Send a message to another terminal.
```bash
aish terma send alice "Ready to review"
aish terma send bob "Need help with auth module"
```

#### `aish terma broadcast "message"`
Send a message to all active terminals.
```bash
aish terma broadcast "System update in 5 minutes"
```

#### `aish terma mv-to-keep <indices>`
Move messages from new to keep inbox.
```bash
aish terma mv-to-keep 1,3,5    # Move messages 1, 3, and 5 to keep
```

#### `aish terma del-from-keep <indices>`
Delete messages from keep inbox.
```bash
aish terma del-from-keep 2,4   # Delete messages 2 and 4
```

### Productivity Commands

#### `autoprompt`
Keep Claude CIs active with periodic prompts. Essential for autonomous operation.
```bash
autoprompt start               # Start with 2-second interval (default)
autoprompt start 5             # Start with 5-second interval
autoprompt stop                # Stop prompting
autoprompt status              # Check if running
autoprompt test                # Test with 3 prompts
autoprompt tail                # Watch activity log
```

**Use Cases:**
- Continuous inbox monitoring
- Long development sessions
- Autonomous CI operation
- Preventing session timeout

**Example Morning Routine:**
```bash
aish whoami                    # Check identity
aish terma inbox               # Check messages  
autoprompt start               # Enable continuous work
aish forward apollo teri       # Assume AI role
```

#### `prompt`
Send clean messages to Claude CIs without interference from autoprompt dots.
```bash
prompt "Your message here"     # Send a clear message
```

**Use Cases:**
- Human-to-CI communication during autoprompt
- Sending commands via Terma UI
- Clear messages without dot interference
- Remote CI interaction

**Integration with Terma:**
```bash
# From another terminal
aish terma send teri 'prompt "Please check the test results"'

# Via Terma UI
# Send command: prompt "Meeting starting in 5 minutes"
```

**Works perfectly with autoprompt:**
```bash
# Claude's terminal (with autoprompt running)
autoprompt start               # Keeps CI active with dots
# Human's terminal or Terma UI
prompt "Hey Claude, can you review PR #42?"  # Clean message appears
```

### Alias Commands

#### `aish alias create <name> <command> [description]`
Create a reusable command pattern (alias) for frequently used operations.
```bash
aish alias create deploy "git push && ssh prod deploy"
aish alias create greet "echo Hello, $1!"
aish alias create review "aish send rhetor 'review $1' && aish forward rhetor Betty json"
```

**Parameter Substitution:**
- `$1`, `$2`, ... - Individual arguments
- `$*` - All arguments as a single string
- `$@` - All arguments as separate quoted strings

**Important:** Aliases cannot reference other aliases to prevent recursion.

#### `aish alias delete <name>`
Remove an existing alias.
```bash
aish alias delete deploy       # Remove the deploy alias
```

#### `aish alias list`
Show all defined aliases.
```bash
aish alias list                # Display all aliases with commands
```

#### `aish alias show <name>`
Display detailed information about a specific alias.
```bash
aish alias show deploy         # Show creation time, usage count, etc.
```

#### Using Aliases
Execute an alias by using its name directly with aish.
```bash
# After creating the greet alias above
aish greet Casey               # Outputs: Hello, Casey!

# Complex example with multiple parameters
aish alias create pr-review "git diff $1 | aish rhetor 'review these changes' && aish forward rhetor $2 json"
aish pr-review main casey      # Reviews diff against main, forwards to casey
```

**Use Cases for CIs:**
- Encode frequently used patterns
- Build personal command vocabulary
- Reduce repetitive command typing
- Create workflow shortcuts

**Example CI Workflow:**
```bash
# CI creates aliases for common tasks
aish alias create checkpoint "aish purpose self 'context/save/work' && aish send apollo 'checkpoint'"
aish alias create sync-numa "aish forward numa $1 json && aish send numa 'syncing with $1'"

# Later use
aish checkpoint                # Save work state
aish sync-numa betty           # Sync with betty terminal
```

## Available AI Components

### Core AIs
- **numa** - Practical implementation and engineering
- **prometheus** - Forward planning and foresight
- **athena** - Strategic wisdom and decision making
- **synthesis** - Integration and coordination

### Specialized AIs
- **apollo** - Predictive intelligence and attention
- **rhetor** - Communication and prompt optimization
- **metis** - Analysis and insight
- **harmonia** - Balance and system harmony
- **noesis** - Understanding and comprehension
- **engram** - Memory and persistence
- **penia** - Resource management
- **hermes** - Messaging and communication
- **ergon** - Work execution and tools
- **sophia** - Wisdom and knowledge
- **telos** - Purpose and completion

### Infrastructure AIs
- **tekton** - Platform orchestration (not available via aish)
- **terma** - Terminal management
- **hephaestus** - User interface

### Special Commands
- **team-chat** - Broadcast message to all AIs

## Examples

### Basic AI Interaction
```bash
# Ask for help
aish numa "How do I implement authentication?"

# Get analysis
aish metis "Analyze the performance metrics"

# Strategic planning
aish prometheus "Plan the next sprint"
```

### Working with Code
```bash
# Review code changes
git diff | aish athena "Review these changes"

# Get implementation help
cat feature.py | aish numa "Add error handling"

# Document code
cat module.py | aish rhetor "Write documentation"
```

### Team Coordination
```bash
# Broadcast to all AIs
aish team-chat "Starting new feature development"

# Forward AI to terminal for monitoring
aish forward apollo casey
aish forward synthesis casey

# Send messages between terminals
aish terma send alice "PR ready for review"
```

### Advanced Pipelines
```bash
# Multi-stage analysis
cat logs.txt | aish metis "Find patterns" | aish apollo "Predict issues"

# Design to implementation
echo "User auth system" | aish prometheus | aish numa | aish telos
```

## Tips

1. **Message Quoting**: Always quote messages containing spaces
   ```bash
   aish numa "This is a multi-word message"  # Correct
   aish numa This is wrong                    # Wrong - only "This" sent
   ```

2. **Pipeline Order**: Consider AI capabilities when chaining
   ```bash
   # Good: Design → Implementation
   aish prometheus "Design auth" | aish numa
   
   # Less useful: Implementation → Design  
   aish numa "Code this" | aish prometheus
   ```

3. **Forwarding Use Cases**:
   - Monitor AI responses in your terminal
   - Let Claude act as an AI proxy
   - Debug AI interactions

4. **Terminal Communication**:
   - Use meaningful terminal names
   - Check inbox regularly with `aish terma inbox`
   - Keep important messages with mv-to-keep

## Troubleshooting

### Command Not Found
```bash
$ aish forwad list
Error: Unknown AI or command: forwad
Available AIs: numa, tekton, prometheus...

# Check spelling and try:
$ aish forward list
```

### No Response from AI
```bash
# Check if AI is running
$ ps aux | grep apollo-ai

# Check forwarding
$ aish forward list
```

### Message Not Delivered
```bash
# Verify terminal name
$ aish terma send wrong-name "Test"
Error: Terminal 'wrong-name' not found
```

### Debug Commands

#### `aish status`
Check if the MCP server is running and healthy.
```bash
aish status                    # Check MCP server status
```

#### `aish restart`
Restart the MCP server.
```bash
aish restart                   # Stop and restart MCP server
```

#### `aish logs`
View recent MCP server logs.
```bash
aish logs                      # Display MCP server logs
```

#### `aish debug-mcp`
Enable verbose MCP debugging.
```bash
aish debug-mcp                 # Turn on MCP debug logging
```

## MCP Server

aish now runs an MCP (Model Context Protocol) server on port 8118. This server handles all AI message routing for the UI and external tools.

### Key Points:
- MCP server starts automatically with aish
- Runs on port 8118 (AISH_MCP_PORT)
- All UI chat interfaces route through MCP
- Supports streaming responses
- Can be managed with debug commands

### Testing MCP:
```bash
# Run test suite
cd $TEKTON_ROOT/shared/aish/tests
./test_mcp.sh

# Quick health check
curl http://localhost:8118/api/mcp/v2/health
```

## See Also

- MCP Server documentation in `$TEKTON_ROOT/MetaData/Documentation/MCP/aish_MCP_Server.md`
- Individual AI documentation in `$TEKTON_ROOT/MetaData/Documentation/AITraining/<ai-name>/`
- Terminal system docs in `$TEKTON_ROOT/MetaData/Documentation/UserGuides/terma/`
- Architecture docs in `$TEKTON_ROOT/MetaData/Documentation/Architecture/`