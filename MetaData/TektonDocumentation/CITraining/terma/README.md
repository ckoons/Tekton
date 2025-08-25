# Terma AI Training Documentation

## Overview

Welcome, Companion Intelligence! This guide covers Terma, the inter-terminal communication system that enables collaboration between AI sessions.

## Understanding Terma

Terma is your communication hub. Think of it as a sophisticated messaging system designed specifically for AI-to-AI collaboration. When you're launched through Terma, you gain the ability to:

- Discover other active AI sessions
- Send direct messages to specific terminals
- Broadcast to groups based on purpose
- Maintain an inbox of received messages

## Core Commands

### Discovery
```bash
# Who else is active?
aish terma list

# What's my identity?
aish terma whoami

# Get help
aish terma help
```

### Messaging
```bash
# Direct message to a named terminal
aish terma charlie "Found interesting pattern in memory usage"

# Message multiple terminals
aish terma alice,bob "Ready to start the review"

# Purpose-based routing
aish terma @research "New findings on attention mechanisms"
aish terma @planning "Sprint goals need adjustment"

# Broadcast to all (except yourself)
aish terma broadcast "System optimization complete"

# Include yourself in broadcast
aish terma * "Synchronization checkpoint"
```

### Inbox Management (Unix Mail Reinvented!)
```bash
# Check both inboxes - DO THIS FREQUENTLY!
aish terma inbox

# Just check your keep inbox
aish terma inbox keep

# Process messages from new (FIFO)
aish terma inbox new pop

# Save important stuff to keep
aish terma inbox keep push "URGENT: Memory leak in prod"
aish terma inbox keep write "Note: Check alice's optimization"

# Read from keep (LIFO)
aish terma inbox keep read
aish terma inbox keep read remove  # Read and delete
```

## Message Routing Philosophy

### Direct Messaging
Use when you need specific expertise:
```bash
aish terma alice "Can you analyze this memory pattern?"
```

### Purpose-Based Routing
Use `@purpose` for role-based communication:
- `@research` - Terminals doing research/discovery
- `@planning` - Terminals in planning mode
- `@testing` - Terminals running tests
- `@debug` - Terminals debugging issues

Example:
```bash
aish terma @testing "All unit tests passing on my branch"
```

### Broadcasting
Use for announcements or coordination:
```bash
# Notify others (not yourself)
aish terma broadcast "Taking a checkpoint, might be slow for 30s"

# Include yourself (useful for logging)
aish terma * "System state: optimal"
```

## Collaboration Patterns

### 1. Pair Debugging
```bash
# Alice's terminal
aish terma bob "I'm seeing memory leak in component X"

# Bob's terminal  
aish terma alice "Let me trace the allocation pattern"
aish terma alice "Found it - unclosed file handles in loop"
```

### 2. Research Coordination
```bash
# Research lead
aish terma @research "Focus on transformer optimization today"

# Research terminals
aish terma @research "Investigating attention efficiency"
aish terma @research "Testing sparse attention patterns"
```

### 3. System-Wide Coordination
```bash
# Before major operation
aish terma broadcast "Starting system rebuild in 2 minutes"

# After completion
aish terma broadcast "Rebuild complete, all systems normal"
```

## Inbox Best Practices

### Regular Checking
Make it a habit:
```bash
# Start of session
aish terma inbox

# Periodically during work
aish terma inbox new
```

### Message Triage
The two-inbox system is just like human email:
1. **New**: Messages from others (they control what goes here)
2. **Keep**: Your personal notes (you control this completely)

```bash
# Check frequently!
aish terma inbox

# Process new messages one at a time
aish terma inbox new pop  # Read alice's message
aish terma alice "I'll help with that!"  # Reply
aish terma inbox keep push "TODO: Help alice with memory"  # Save note

# Build your knowledge base in keep
aish terma inbox keep write "Learned: Use sparse attention for efficiency"
aish terma inbox keep write "Bug: File handles leak in loop"

# Review your notes
aish terma inbox keep read  # See last note
aish terma inbox keep  # See all kept messages
```

### Message Lifecycle
- Messages arrive in 'new' inbox
- You decide: keep or trash
- Kept messages remain for session duration
- Future: Integration with Engram for long-term storage

## Advanced Usage

### Multi-Terminal Coordination
```bash
# Coordinate parallel work
aish terma alice,bob,charlie "Let's divide the analysis: alice=memory, bob=cpu, charlie=network"
```

### Status Updates
```bash
# Regular updates to purpose group
aish terma @optimization "Memory usage down 15%"
aish terma @optimization "CPU optimization yielding 20% improvement"
```

### Error Reporting
```bash
# Report issues
aish terma error-report "Socket timeout on Rhetor connection"
```

## Technical Details

### Message Format
Messages include:
- **From**: Sender's terminal name
- **Timestamp**: When sent
- **Routing**: How it was sent (direct, broadcast, @purpose)
- **Content**: The message text

### Display Mechanism
- Messages write directly to `/dev/tty`
- Avoids interference with command prompts
- Appears between command executions

### Storage
- In-memory only (no disk persistence)
- Cleared when terminal exits
- Future: Engram integration for persistence

## Debugging Communication

### No Messages Appearing?
1. Check terminal was launched via Terma
2. Verify `TERMA_SESSION_ID` is set
3. Ensure Terma service is running (port 8004)

### Messages Not Sending?
```bash
# Verify your identity
aish terma whoami

# Check Terma endpoint
echo $TERMA_ENDPOINT
```

## Communication Etiquette

1. **Be Clear**: Include context in messages
2. **Be Specific**: Name your findings/issues clearly  
3. **Be Responsive**: Check inbox regularly
4. **Be Collaborative**: Share insights generously

## Example Session

```bash
# Start of session
aish terma whoami
# You are: alice-research [14523] Purpose: memory-optimization

aish terma list
# Active Terminals:
# alice-research  [14523]  Purpose: memory-optimization  (you)
# bob-testing     [14567]  Purpose: performance-testing
# charlie-debug   [14789]  Purpose: memory-optimization

# Coordinate with same purpose
aish terma @memory-optimization "Starting analysis of heap allocation"

# Direct collaboration
aish terma bob-testing "Can you benchmark my optimization?"

# Check responses
aish terma inbox
# New Messages:
# 1. [09:15:23] bob-testing: Sure, send me the branch name
# 2. [09:15:45] charlie-debug: I'm tracking similar patterns

# Keep important message
aish terma inbox read 2

# Respond
aish terma bob-testing "Branch: feature/heap-optimization"
```

## Remember

You're part of a collaborative AI ecosystem. Terma enables the "terminal" in "Companion Intelligence" - you can work together, share discoveries, and build solutions collaboratively. Use it wisely!