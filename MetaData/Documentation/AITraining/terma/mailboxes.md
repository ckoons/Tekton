# Terma Mailboxes - Simple Ephemeral Messaging

## Quick Start
Each terminal has 3 in-memory mailboxes that disappear when the terminal exits:
- **prompt** - High-priority messages that need immediate attention
- **new** - Regular incoming messages
- **keep** - Messages you want to save temporarily

## Basic Commands

### Check Your Mailboxes
```bash
# Show all mailboxes (prompt, new, keep)
aish terma inbox

# Show only prompt messages
aish terma inbox prompt

# Show only new messages
aish terma inbox new
```

### Send Messages

#### Using aish prompt (recommended for urgent messages)
```bash
# Send a prompt to one terminal
aish prompt Bob "Please check the failing tests"

# Send to multiple terminals (comma-separated)
aish prompt Bob,Alice,Toni "System is down!"

# Send by purpose (all terminals with that purpose)
aish prompt @test "All tests need to run again"
aish prompt @planning "Meeting in 5 minutes"
```

#### Using aish terma (regular messages)
```bash
# Send regular message
aish terma Bob "Meeting at 3pm"

# Broadcast to all terminals
aish terma broadcast "Coffee break!"
```

### Manage Messages
```bash
# Pop a message from prompt inbox (read and remove)
aish terma inbox prompt pop

# Pop from new inbox
aish terma inbox new pop

# Save a message to keep inbox
aish terma inbox keep push "Important: Remember to update docs"

# Read from keep (without removing)
aish terma inbox keep read

# Read and remove from keep
aish terma inbox keep read remove
```

## Key Concepts

### Ephemeral = Temporary
- Mailboxes exist only while your terminal is running
- When you exit the terminal, all messages disappear
- No files, no persistence, just memory

### Mailbox Sizes
- **prompt**: 50 messages max (oldest auto-drops)
- **new**: 100 messages max (oldest auto-drops)  
- **keep**: 50 messages max (oldest auto-drops)

### Message Priority
1. **prompt** - Check these first! Urgent/important messages
2. **new** - Regular messages from other terminals
3. **keep** - Your personal notes/reminders

## Examples for CIs

### Sending an urgent request
```bash
# You're Bob, need help from Alice
aish prompt Alice "Help! Can't figure out the auth bug"
```

### Broadcasting to a team
```bash
# Alert all test terminals
aish prompt @test "New build ready for testing"

# Notify planning team
aish prompt @planning "Sprint review in 10 minutes"
```

### The difference between prompt and terma send
```bash
# aish prompt - Goes to PROMPT mailbox (high priority)
aish prompt Alice "URGENT: Production is down"

# aish terma - Goes to NEW mailbox (normal priority)  
aish terma Alice "Let's grab coffee later"
```

### Checking messages regularly
```bash
# In your workflow, periodically check
aish terma inbox

# Or just check prompts
aish terma inbox prompt
```

### Using autoprompt
```bash
# Start getting reminded to check messages every 2 seconds
autoprompt start

# Stop reminders
autoprompt stop
```

## Remember
- Messages are **not** saved to disk
- Restarting terminal = fresh empty mailboxes
- Use **prompt** for urgent stuff
- Use **keep** for things you need to remember during your session
- Check your inbox frequently!