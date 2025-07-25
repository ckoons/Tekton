# Unified Inbox System - CI-Friendly Message Management

## Quick Start
Each CI has a unified inbox system with 3 priority levels stored persistently:
- **prompt** - Urgent messages requiring immediate attention
- **new** - Regular incoming messages
- **keep** - Saved/archived messages

## Basic Commands

### Check Your Inbox
```bash
# Show message counts across all types
aish inbox                          # Shows: prompt:2  new:5  keep:1

# Show messages in human-readable format
aish inbox show prompt              # Show all urgent messages
aish inbox show new                 # Show regular messages
aish inbox show keep                # Show saved messages
```

### Send Messages

#### Using the unified inbox system
```bash
# Send urgent message
aish inbox send prompt numa "Please check the failing tests" 

# Send regular message
aish inbox send new alice "Meeting at 3pm"

# Archive important information
aish inbox send keep self "Important: Remember to update docs"
```

#### Using aish prompt (still works for urgent delivery)
```bash
# Send a prompt to one terminal (goes to their prompt inbox)
aish prompt Bob "Please check the failing tests"

# Send to multiple terminals (comma-separated)
aish prompt Bob,Alice,Toni "System is down!"

# Send by purpose (all terminals with that purpose)
aish prompt @test "All tests need to run again"
aish prompt @planning "Meeting in 5 minutes"
```

#### Using aish terma (still works for regular messages)
```bash
# Send regular message (goes to their new inbox)
aish terma Bob "Meeting at 3pm"

# Broadcast to all terminals
aish terma broadcast "Coffee break!"
```

### Manage Messages (CI-Friendly Batch Processing)
```bash
# Get and remove all urgent messages (JSON format)
messages=$(aish inbox get prompt)
echo "$messages" | jq -r '.[] | "From: \(.from) - \(.message)"'

# Process regular messages in batches
aish inbox get new | process_messages

# Count messages for automation loops
while [ $(aish inbox count new) -gt 0 ]; do
    aish inbox get new | handle_message
done

# Filter by sender
aish inbox json new from rhetor     # Get messages from rhetor as JSON
aish inbox clear keep from numa     # Clear saved messages from numa

# Silent cleanup
aish inbox clear prompt             # Clear all urgent messages (silent)
```

## Key Concepts

### Persistent Storage
- Messages are stored in `.tekton/inboxes/<ci-name>/` directory
- Files persist between sessions (not ephemeral like old system)
- JSON format enables CI automation and batch processing
- Timestamp-ordered filenames maintain message chronology

### Message Storage Structure
- **prompt/**: `20250125_143022_a1b2c3d4.json` (urgent messages)
- **new/**: `20250125_142030_f9e8d7c6.json` (regular messages)
- **keep/**: `20250125_141500_c7d8e9f0.json` (archived messages)

### Message Priority & Processing
1. **prompt** - Check these first! Urgent/important messages (`aish inbox get prompt`)
2. **new** - Regular messages from forwarding/collaboration (`aish inbox get new`)
3. **keep** - Personal archive/notes (`aish inbox show keep`)

### CI-Friendly Features
- **Batch JSON Processing**: `aish inbox get <type>` returns JSON array
- **Sender Filtering**: `from <ci>` syntax for focused processing  
- **Silent Operations**: Commands designed for script integration
- **Count-Based Loops**: `aish inbox count <type>` for automation

## Examples for CIs

### Sending messages with priority
```bash
# Send urgent request
aish inbox send prompt alice "Help! Can't figure out the auth bug"

# Send regular collaboration message
aish inbox send new bob "Ready for code review when you are"

# Archive important discovery
aish inbox send keep self "Found: Memory leak in loop at line 245"
```

### CI Automation Patterns
```bash
# Priority-based message processing
if [ $(aish inbox count prompt) -gt 0 ]; then
    echo "Processing urgent messages first..."
    aish inbox get prompt | handle_urgent_messages
fi

# Batch processing regular messages
messages=$(aish inbox get new)
if [ -n "$messages" ]; then
    echo "$messages" | jq -r '.[] | "[\(.from)] \(.message)"' | while read msg; do
        echo "Processing: $msg"
        # Handle each message
    done
fi
```

### Sender-Specific Processing
```bash
# Process messages from specific CIs
rhetor_msgs=$(aish inbox json new from rhetor)
if [ "$rhetor_msgs" != "[]" ]; then
    echo "Processing Rhetor optimization suggestions..."
    echo "$rhetor_msgs" | jq -r '.[] | .message'
fi
```

### Checking messages regularly
```bash
# In your workflow, periodically check
aish inbox                          # Shows counts: prompt:1  new:3  keep:5

# Show detailed view
aish inbox show prompt              # Human-readable urgent messages
aish inbox show new                 # Human-readable regular messages
```

### Using with automation tools
```bash
# Start autoprompt to stay active
autoprompt start

# Check inbox in your processing loop
while true; do
    if [ $(aish inbox count prompt) -gt 0 ]; then
        aish inbox get prompt | process_urgent
    fi
    if [ $(aish inbox count new) -gt 0 ]; then
        aish inbox get new | process_regular
    fi
    sleep 5
done
```

## Remember
- Messages **are** saved to disk (persistent across sessions)
- Use **prompt** for urgent stuff that needs immediate attention
- Use **new** for regular collaboration and forwarded messages
- Use **keep** for personal archives and important discoveries
- Check your inbox frequently with `aish inbox`!
- Use batch processing (`aish inbox get <type>`) for CI automation