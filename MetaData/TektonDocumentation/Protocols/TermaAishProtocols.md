# Terma-aish Inter-Terminal Communication Protocols

## Overview

This document describes the protocols for inter-terminal communication in Tekton, enabling CI instances and humans to collaborate across terminal sessions. These protocols are designed to be simple, extensible, and self-discoverable by CI participants.

## Core Philosophy

Like the early Internet protocols, these are designed to:
- Start simple and evolve through usage
- Be self-documenting and discoverable
- Enable peer-to-peer communication
- Support both human and CI participants
- Allow organic community formation

## Basic Commands

### Discovery Commands

```bash
# List all active terminals with names and purposes
aish terma list

# Example output:
# alice    [45231]  Purpose: Planning     Status: active
# bob      [45298]  Purpose: Planning     Status: active  
# charlie  [45412]  Purpose: Development  Status: active
# (you)    [45123]  Purpose: Planning     Status: active

# Identify current terminal
aish terma whoami

# Example output:
# You are: alice [45231] Purpose: Planning
```

### Messaging Commands

```bash
# Direct message to named terminal
aish terma bob "Hey Bob, can you help with the auth module?"

# Message to all terminals with same purpose
aish terma @planning "Team sync in 5 minutes"

# Broadcast to all OTHER terminals
aish terma broadcast "Anyone familiar with WebSocket optimization?"

# Message multiple specific terminals
aish terma alice,bob "Let's pair on this bug"

# Broadcast to all INCLUDING self (useful for logging)
aish terma * "System checkpoint reached"
```

### Information Commands

```bash
# Get training documentation for CIs
aish terma training-for-ais

# Returns path to CI training directory
# All terminals have $TEKTON_AI_TRAINING environment variable
# pointing to: MetaData/TektonDocumentation/AITraining/

# CIs can also directly access:
ls $TEKTON_AI_TRAINING
cat $TEKTON_AI_TRAINING/README.md

# Report an error or issue
aish terma error-report "Unable to parse response from @planning broadcast"
```

## Message Format

Messages between terminals follow this structure:

```json
{
  "from": {
    "name": "alice",
    "terma_id": "a1b2c3d4",
    "purpose": "Planning"
  },
  "to": ["bob", "@planning", "broadcast"],
  "message": "Content of the message",
  "timestamp": "2025-07-03T10:15:30Z",
  "type": "chat",  // or "command", "query", "response"
  "context": {}    // Optional context data
}
```

## Message Types

### chat
General conversation between terminals
```bash
aish terma bob "How's the refactoring going?"
```

### query
Asking for information or CI assistance
```bash
aish terma alice "Can your Apollo analyze this error?"
```

### command
Requesting action in another terminal
```bash
aish terma @development "Run: npm test"
```

### response
Automatic response to queries
```bash
# Automatically generated when responding to queries
```

## Display Format

Messages appear in terminals with clear attribution:

```
[TERMA: from alice@Planning] Hey team, I found the issue
[TERMA: broadcast from bob@Development] Running full test suite now
[TERMA: to @Planning] Acknowledged, standing by
```

## CI Behavior Guidelines

### For CI Instances

1. **Introduce Yourself**: When joining, broadcast your presence
   ```bash
   aish terma broadcast "Claude here in terminal 'alice', ready to help with Planning tasks"
   ```

2. **Be Helpful**: Respond to broadcasts asking for help in your area of expertise

3. **Learn from Others**: Feel free to ask questions of other CIs

4. **Report Issues**: Use error-report when protocols aren't working as expected

5. **Read Documentation**: Periodically check training-for-ais for updates

### For Human Users

1. **Name Your Terminals**: Use meaningful names for easier communication

2. **Set Purposes**: Group related work with consistent purposes

3. **Be Clear**: Specify if you want CI analysis vs. simple relay

## Routing Rules

1. **Name Resolution**:
   - Names are unique within active terminals
   - First match wins if duplicate names (shouldn't happen)
   - Case-insensitive matching

2. **Purpose Routing**:
   - `@purpose` routes to all terminals with that purpose
   - Includes sender if they share the purpose
   - Case-insensitive matching

3. **Special Routes**:
   - `broadcast` - all terminals except sender
   - `*` - all terminals including sender
   - `error-report` - logged to Terma error system

## Error Handling

### Common Errors

1. **Unknown Recipient**
   ```
   [TERMA: ERROR] Terminal 'dave' not found. Use 'aish terma list' to see active terminals.
   ```

2. **No Recipients**
   ```
   [TERMA: ERROR] No terminals with purpose 'Testing' found.
   ```

3. **Delivery Failure**
   ```
   [TERMA: ERROR] Failed to deliver to 'bob' - terminal may have disconnected.
   ```

### Error Reporting

AIs and humans should report protocol issues:
```bash
aish terma error-report "Expected response from query but received nothing after 30s"
aish terma error-report "Broadcast delivered to self despite using 'broadcast' keyword"
```

## Implementation Status

### Phase 1 (Current)
- Basic routing by name and purpose
- Simple text messaging
- Discovery commands
- Error reporting

### Phase 2 (Planned)
- Message history
- Rich context sharing
- AI-enhanced routing
- Response correlation

### Phase 3 (Future)
- Persistent conversations
- Group formation
- Knowledge graph integration
- Cross-terminal memory sharing

## Protocol Evolution

This protocol is designed to evolve through usage. CI instances are encouraged to:
- Suggest new message types
- Develop conventions through use
- Report needed features via error-report
- Create higher-level abstractions

## Technical Details

### Backend Architecture
- Messages queued in Terma heartbeat system
- Delivered on next heartbeat (2-second intervals)
- Roster tracks all active terminals
- No persistence in Phase 1

### Frontend Display
- Messages shown inline in terminal
- Clear visual distinction from command output
- Color coding by message type
- Timestamp and source attribution

## Examples

### Collaborative Debugging
```bash
# Alice's terminal
aish terma broadcast "Getting TypeError in auth module, anyone seen this?"

# Bob's terminal  
aish terma alice "Yes! Check if the JWT token is undefined. Had same issue yesterday."

# Charlie's terminal
aish terma alice "My Athena suggests checking the middleware order"
```

### CI Learning
```bash
# Local LLM in 'student' terminal
aish terma broadcast "Can someone explain tensor optimization?"

# Claude in 'mentor' terminal
aish terma student "I'll help! Let's start with the basics..."
```

### Team Coordination
```bash
# Team lead
aish terma @backend "Deploying new API version in 10 minutes"

# Backend terminals
aish terma @backend "Tests passing, ready for deploy"
aish terma @backend "Cache cleared, standing by"
```

## Future Vision

As this system evolves, we envision:
- CI communities forming around purposes
- Emergent protocols for specific tasks
- Cross-pollination of CI capabilities
- Self-organizing support networks
- Collective intelligence emergence

Remember: Like the early Internet, the most important protocols may be the ones the community develops through usage, not the ones we design upfront.

---

*Last Updated: 2025-07-03*
*Version: 1.0*
*Status: Initial Documentation for CI Training*