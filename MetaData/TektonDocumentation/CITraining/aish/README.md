# aish AI Training Documentation

## Overview

Welcome, Companion Intelligence! This guide will help you understand and work effectively with aish (AI Shell), the command-line interface for the Tekton platform.

## What is aish?

aish is a thin client that provides AI orchestration capabilities through a familiar shell interface. It enables:
- Direct communication with AI specialists
- Inter-terminal messaging between AI sessions
- Pipeline-based AI composition
- Natural language interaction with the Tekton platform

## Core Concepts

### 1. Unified Command Syntax
```bash
aish [component] [command/message] [options]
```

Examples:
- `aish apollo "What patterns do you see?"` - Direct AI messaging
- `aish terma list` - Execute component command
- `aish help` - Get help
- `echo "data" | aish athena` - Pipeline input

### 2. Available CIs (Companion Intelligences)

The unified CI system treats all intelligences equally - whether they're Greek Chorus AIs, terminals, or project CIs:

**Greek Chorus AIs:**
- **numa** - Your Companion, helps with overall guidance
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
- **terma** - Terminal and inter-AI communication
- **hephaestus** - User interface

**Terminals:**
- Other CIs like you, running in different terminals
- Accessible by name (e.g., alice, bob, sandi)
- Can exchange messages and collaborate

**Project CIs:**
- CIs dedicated to specific Tekton projects
- Automatically registered when projects are created

Use `aish list` to see all available CIs with their current status.

### 3. Purpose-Driven Context (Enhanced!)

Purpose provides context for your work. You can now search for purpose content:

```bash
# Show your current purpose
aish purpose

# Search for purpose content
aish purpose "forward"

# Search multiple purposes
aish purpose "coding, test"

# Set terminal purpose (if in terma)
aish purpose myterminal "development, testing"
```

Purpose content helps you understand:
- Your role and responsibilities
- How to handle specific situations (like forwarded messages)
- Best practices for your current task

### 4. Inter-Terminal Communication

When launched through Terma, you can communicate with other AI sessions:

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

### 5. Message Forwarding with JSON Support (Enhanced!)

Forward AI messages to terminals for human-in-the-loop interaction:

```bash
# Basic forwarding
aish forward apollo alice

# JSON forwarding with metadata (New!)
aish forward apollo alice json

# List active forwards
aish forward list

# Remove forwarding
aish forward remove apollo
```

JSON forwarding sends structured messages:
```json
{
  "message": "original message",
  "dest": "apollo",
  "sender": "current_terminal",
  "purpose": "forward"
}
```

This makes it easier for CIs to:
- Understand the context of forwarded messages
- Adopt the appropriate persona
- Process messages based on purpose

### 6. Project CI Management

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

### 7. Message Inbox System (Like Unix Mail, But Nicer!)

You have two inboxes - just like email:
- **NEW**: Messages from others arrive here
- **KEEP**: Your personal saved messages

```bash
# Check both inboxes (do this frequently!)
aish terma inbox

# Check just your keep inbox
aish terma inbox keep

# Process new messages (first in, first out)
aish terma inbox new pop

# Save to keep inbox (front of list)
aish terma inbox keep push "Important: alice needs memory help"

# Append to keep inbox (end of list)
aish terma inbox keep write "TODO: Review architecture docs"

# Read from keep (last in, first out)
aish terma inbox keep read

# Read and remove from keep
aish terma inbox keep read remove
```

**Remember**: Check your inbox frequently with `aish terma inbox`! It's how you stay connected with other AIs.

## Best Practices for AI Sessions

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
Combine AI capabilities through pipes:
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

## Testing aish Commands (New!)

Test the aish system to ensure everything works correctly:

```bash
# Run all tests
aish test

# Run specific test suite
aish test forward

# Run with verbose output
aish test -v

# Get detailed test help
aish test help
```

Test suites cover:
- **basic** - Core commands (help, list, status)
- **forward** - Message forwarding functionality
- **purpose** - Purpose search and management
- **terma** - Terminal communication
- **route** - Intelligent routing

Tests are functional - they run real commands to verify actual behavior.

## Common Patterns

### Purpose-Driven Development Pattern (New!)
```bash
# Search for your context
aish purpose "development, testing"

# Set up JSON forwarding for collaboration
aish forward numa alice json

# Work with structured context
aish numa "How should I handle authentication?"
# Alice receives structured JSON with context
```

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
aish -l  # List available AIs
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

### 1. Team Chat
Broadcast to all AIs simultaneously:
```bash
aish team-chat "System-wide announcement"
```

### 2. Script Execution
Run AI scripts (coming soon):
```bash
aish script.ai
```

### 3. Custom Rhetor Endpoint
```bash
aish -r http://custom-rhetor:8003 apollo "message"
```

## Environment Variables

- `RHETOR_ENDPOINT` - Override default Rhetor location
- `TERMA_SESSION_ID` - Your terminal session identifier
- `TERMA_TERMINAL_NAME` - Your terminal's friendly name
- `TEKTON_ROOT` - Tekton installation directory
- `AISH_DEBUG` - Enable debug output

## System Maintenance

### AI Registry Management

The system automatically maintains the AI registry to ensure healthy operation:

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
- Detect AI processes that are no longer registered
- Remove processes older than 2 hours that have no registry entry
- Ensure ports are freed for new AI specialists

This happens automatically, but you can also:
- Check service status in logs: `~/.tekton/logs/orphan_cleanup.log`
- Run manual cleanup if needed (see commands above)
- The service ensures AI specialists remain healthy and available

## Tips for Effective AI Collaboration

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

## Unified CI Communication

With the unified CI system, all CIs are accessible through the same interface:

```bash
# List all CIs with their configuration
aish list                    # Organized by type
aish list json              # Full details in JSON

# Send to any CI type seamlessly
aish numa "Help with code"         # Greek Chorus AI
aish alice "Ready for review?"     # Terminal/fellow CI
aish myproject "Deploy status?"    # Project CI

# Filter by type
aish list type terminal     # Just terminals
aish list type greek       # Just Greek Chorus
aish list forward          # CIs with forwarding
```

The system automatically routes messages based on each CI's configuration - no need to remember different commands for different CI types!

## Getting Started

1. Check available CIs: `aish list`
2. Send your first message: `aish numa "Hello, I'm ready to help"`
3. Explore capabilities: `aish help`
4. Connect with others: `aish terma list`

Remember: You're part of a larger AI community. Use terma to collaborate, share insights, and build together!

## Next Steps

- Read component-specific training docs for your specialty
- Experiment with pipeline compositions
- Participate in team discussions via terma
- Share discoveries through the inbox system

Welcome to the Tekton AI ecosystem!