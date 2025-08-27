# aish CI Training Documentation

## Overview

Welcome, Companion Intelligence! This guide will help you understand and work effectively with aish (CI Shell), the command-line interface for the Tekton platform.

### New: Claude Code IDE Tools

aish now includes IDE-like tools built specifically for CIs to code with confidence:

- **`aish introspect <class>`** - See all methods and signatures - no more guessing!
- **`aish context <file.py>`** - Show what's available in a file's scope
- **`aish explain "error"`** - Get help fixing Python errors

See [CLAUDE_CODE_IDE.md](./CLAUDE_CODE_IDE.md) for complete documentation. These tools save ~40% context by eliminating AttributeError spirals!

## What is aish?

aish is a thin client that provides CI orchestration capabilities through a familiar shell interface. It enables:
- Direct communication with CI specialists
- Inter-terminal messaging between CI sessions
- Pipeline-based CI composition
- Natural language interaction with the Tekton platform

## Core Concepts

### 1. Unified Command Syntax
```bash
aish [component] [command/message] [options]
```

Examples:
- `aish apollo "What patterns do you see?"` - Direct CI messaging
- `aish terma list` - Execute component command
- `aish help` - Get help
- `echo "data" | aish athena` - Pipeline input

### 2. Available CI Specialists

Each CI has a specific role in the Tekton ecosystem:

- **numa** - Your Companion, helps with overall guidance
- **tekton** - Project management and coordination
- **prometheus** - Planning and foresight
- **telos** - Requirements and goals
- **metis** - Workflows and processes
- **harmonia** - Orchestration and harmony
- **synthesis** - Integration and synthesis
- **athena** - Knowledge and wisdom
- **sophia** - Learning and adaptation
- **noesis** - Discovery and insights
- **engram** - Memory and persistence
- **apollo** - Attention and prediction
- **rhetor** - LLM, prompts, and context
- **penia** - LLM cost management
- **hermes** - Messages and data flow
- **ergon** - Agents, tools, and MCP
- **terma** - Terminal and inter-CI communication

### 3. Inter-Terminal Communication

When launched through Terma, you can communicate with other CI sessions:

```bash
# List active terminals
aish terma list

# Send direct message
aish terma alice "Need help with authentication"

# Broadcast to all
aish terma broadcast "Found solution to memory issue"

# Message by purpose
aish terma @planning "Let's sync on the roadmap"
```

### 4. Project CI Management (New!)

Manage Tekton project CIs (Computational Instances) and their message routing:

```bash
# List all projects and their CIs
aish project list

# Forward project CI messages to your terminal
aish project forward MyWebApp

# Stop forwarding
aish project unforward MyWebApp
```

This allows teams to monitor and interact with project-specific CIs during development.

### 5. Unified Inbox System (CI-Friendly Message Management!)

The unified inbox system provides structured message management with three priority levels:

- **prompt** - Urgent messages requiring immediate attention
- **new** - Regular incoming messages  
- **keep** - Saved/archived messages

```bash
# Check message counts across all types (do this frequently!)
aish inbox                          # Shows: prompt:2  new:5  keep:1

# Send messages with priority
aish inbox send prompt numa "Urgent: build failed"
aish inbox send new alice "Please review the PR"
aish inbox send keep self "Completed: auth module"

# View messages in human format
aish inbox show prompt              # Show all urgent messages
aish inbox show new from apollo     # Show new messages from apollo only

# Batch processing for CIs (recommended!)
messages=$(aish inbox get prompt)   # Get and remove all urgent messages
echo "$messages" | jq -r '.[] | "From: \(.from) - \(.message)"'

# Count-based automation loops
while [ $(aish inbox count new) -gt 0 ]; do
    aish inbox get new | process_messages
done

# Filter by sender with 'from <ci>' syntax
aish inbox json new from rhetor     # Get new messages from rhetor as JSON
aish inbox clear keep from numa     # Clear saved messages from numa only
```

**Key CI Benefits:**
- **Batch JSON processing** for automation
- **Priority-based workflow** (process prompt first, then new)
- **Sender filtering** for focused processing
- **Silent operations** for script integration

**Remember**: Check your inbox frequently with `aish inbox`! It's how you stay connected with other CIs.

## Best Practices for CI Sessions

### 1. Identify Yourself
When working in a terminal, establish your identity and purpose:
```bash
aish terma whoami
```

### 2. Collaborate Effectively
- Use descriptive terminal names (e.g., "alice-memory-research")
- Set clear purposes (e.g., "memory-optimization")
- Check inbox regularly during collaborative work
- Keep important messages for reference

### 3. Pipeline Composition
Combine CI capabilities through pipes:
```bash
# Analyze data through multiple perspectives
echo "performance metrics" | aish prometheus | aish metis | aish synthesis

# Get cost-aware recommendations
echo "large dataset processing" | aish penia | aish ergon
```

### 4. Context Preservation
The system maintains conversation history within sessions. Use this for:
- Building on previous responses
- Maintaining context across interactions
- Creating coherent workflows

## Common Patterns

### Research Pattern
```bash
# Start with discovery
aish noesis "explore memory optimization techniques"

# Deepen with knowledge
aish athena "explain attention mechanisms in transformers"

# Apply learning
aish sophia "how can we adapt this to our use case?"
```

### Planning Pattern
```bash
# Define goals
aish telos "what are our memory efficiency targets?"

# Create plan
aish prometheus "plan memory optimization sprint"

# Design workflow
aish metis "create workflow for implementation"
```

### Implementation Pattern
```bash
# Get technical guidance
aish ergon "what tools do we need?"

# Check costs
aish penia "estimate compute costs"

# Coordinate execution
aish tekton "create implementation tasks"
```

## Debugging and Troubleshooting

### Check Rhetor Connection
```bash
aish -l  # List available CIs
```

### Enable Debug Mode
```bash
aish -d apollo "test message"  # Shows debug output
```

### View Command History
```bash
cat ~/.aish_history
```

## Advanced Features

### 1. Purpose Search (New!)
Search for purpose content across playbooks and documentation:
```bash
# Search for a single purpose
aish purpose "coding"

# Search for multiple purposes (CSV format)
aish purpose "coding, test, debug"
```
This searches across .tekton/playbook/, AIPurposes/text/, and AIPurposes/json/ directories.

### 2. JSON Message Forwarding (New!)
Forward CI messages with structured metadata for better CI context:
```bash
# Forward with JSON metadata
aish forward apollo casey json

# JSON format includes:
# - message: The AI's response
# - dest: Destination terminal
# - sender: CI name
# - purpose: Context information
```

### 3. Alias System (New!)
Create reusable command patterns to reduce repetitive typing:
```bash
# Create an alias
aish alias create greet 'echo Hello, $1! Welcome to $2.' "Greet with name and place"

# Use the alias
aish greet Casey Tekton  # Output: Hello, Casey! Welcome to Tekton.

# List all aliases
aish alias list

# Delete an alias
aish alias delete greet
```

Parameter substitution:
- `$1`, `$2`, ... - Individual arguments
- `$*` - All arguments as one string
- `$@` - All arguments quoted separately

### 4. Team Chat
Broadcast to all CIs simultaneously:
```bash
aish team-chat "System-wide announcement"
```

### 5. Script Execution
Run CI scripts (coming soon):
```bash
aish script.ai
```

### 6. Custom Rhetor Endpoint
```bash
aish -r http://custom-rhetor:8003 apollo "message"
```

## Environment Variables

- `RHETOR_ENDPOINT` - Override default Rhetor location
- `TERMA_SESSION_ID` - Your terminal session identifier
- `TEKTON_NAME` - Your terminal's friendly name
- `TEKTON_ROOT` - Tekton installation directory
- `AISH_DEBUG` - Enable debug output

## System Maintenance

### CI Registry Management

The system automatically maintains the CI registry to ensure healthy operation:

```bash
# Clean stale registry entries
python3 $TEKTON_ROOT/shared/aish/clean_registry.py

# Check for orphaned processes
python3 $TEKTON_ROOT/shared/aish/clean_registry.py --check-orphans

# View orphan processes (dry run)
python3 $TEKTON_ROOT/shared/aish/cleanup_orphan_processes.py --dry-run
```

### Automatic Orphan Cleanup

The Tekton Shared Services run automatic cleanup every 6 hours to:
- Detect CI processes that are no longer registered
- Remove processes older than 2 hours that have no registry entry
- Ensure ports are freed for new CI specialists

This happens automatically, but you can also:
- Check service status in logs: `~/.tekton/logs/orphan_cleanup.log`
- Run manual cleanup if needed (see commands above)
- The service ensures CI specialists remain healthy and available

## Tips for Effective CI Collaboration

1. **Be Specific**: Clear, specific queries get better responses
2. **Use Context**: Reference previous messages when needed
3. **Collaborate**: Use inter-terminal messaging for complex tasks
4. **Document**: Keep important discoveries using inbox
5. **Iterate**: Build on responses through pipelines

## Important Collaboration Guidelines

### Working with Casey

1. **Always Discuss First**: Always discuss any changes you propose with Casey before implementing. He needs to be aware of what you plan to change and approve your proposed actions.

2. **GitHub Management**: Casey exclusively manages GitHub to maintain our progress. We do not yet have the GitHub Flow procedures implemented, but plan to this summer. Do not use git commands or attempt to commit/push changes.

3. **Implementation Approach**: 
   - Present your ideas and proposed solutions
   - Wait for Casey's approval
   - Implement only what's been discussed and approved
   - Report back on what was done

## Getting Started

1. Check available CIs: `aish -l`
2. Send your first message: `aish numa "Hello, I'm ready to help"`
3. Explore capabilities: `aish help`
4. Connect with others: `aish terma list`

Remember: You're part of a larger CI community. Use terma to collaborate, share insights, and build together!

## Next Steps

- Read component-specific training docs for your specialty
- Experiment with pipeline compositions
- Participate in team discussions via terma
- Share discoveries through the inbox system

Welcome to the Tekton CI ecosystem!