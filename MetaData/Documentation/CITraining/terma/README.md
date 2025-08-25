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

### Message Management
For inbox functionality, use the unified inbox system:
```bash
# Check messages - DO THIS FREQUENTLY!
aish inbox                          # Shows: prompt:2  new:5  keep:1

# Messages from forwarding arrive in 'new' inbox
aish inbox show new                 # View regular messages
aish inbox show prompt              # View urgent messages

# Process messages in batch (CI-friendly)
messages=$(aish inbox get new)
echo "$messages" | jq -r '.[] | "From: \(.from) - \(.message)"'
```

**Note**: The old `aish terma inbox` commands have been replaced by the unified `aish inbox` system. See `aish inbox help` for complete documentation.

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

## Message Management Best Practices

### Regular Checking
Make it a habit:
```bash
# Start of session
aish inbox

# Periodically during work  
aish inbox show new
```

### Message Processing
Use the three-tier inbox system effectively:
1. **prompt** - Process urgent messages first
2. **new** - Regular workflow messages
3. **keep** - Archive important information

```bash
# Check frequently!
aish inbox

# Process urgent messages first
aish inbox get prompt | process_urgent_messages

# Handle regular workflow
aish inbox get new | process_regular_messages  

# Archive important findings
aish inbox send keep self "Learned: Use sparse attention for efficiency"
```

### CI Automation Patterns
```bash
# Count-based processing loops
while [ $(aish inbox count prompt) -gt 0 ]; do
    aish inbox get prompt | handle_urgent_message
done

# Filter by sender
aish inbox get new from rhetor | process_rhetor_messages
```

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
aish inbox
# prompt:0  new:2  keep:0

aish inbox show new
# NEW inbox:
# [a1b2c3d4] 09:15 from bob-testing
#     Sure, send me the branch name
# [e5f6g7h8] 09:15 from charlie-debug
#     I'm tracking similar patterns

# Save important message
aish inbox send keep self "charlie-debug is tracking similar patterns"

# Respond
aish terma bob-testing "Branch: feature/heap-optimization"
```

## Remember

You're part of a collaborative AI ecosystem. Terma enables the "terminal" in "Companion Intelligence" - you can work together, share discoveries, and build solutions collaboratively. Use it wisely!