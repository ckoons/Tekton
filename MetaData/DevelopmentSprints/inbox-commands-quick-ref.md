# AISH Terma Inbox - Quick Command Reference

## Essential Inbox Commands

### View Messages
```bash
aish terma inbox              # Show all messages (new + keep)
aish terma inbox new pop      # Read & remove one new message
aish terma inbox keep         # Show kept messages only
```

### Manage Inbox
```bash
# Clear all old messages quickly
for i in {1..20}; do aish terma inbox new pop > /dev/null 2>&1; done

# Keep important messages
aish terma inbox keep push "Remember to review PR #123"
aish terma inbox keep write "Meeting notes: discussed new features..."

# Read kept messages
aish terma inbox keep read           # Show kept messages
aish terma inbox keep read remove    # Show and clear kept messages
```

### Proposed Improvements (TODO)
```bash
# These would be nice to have:
aish terma inbox clear               # Clear all new messages
aish terma inbox new                 # Show only new messages
aish terma inbox pop all             # Pop all messages at once
aish terma inbox filter "Iris"       # Show messages from specific sender
aish terma inbox --json              # JSON output for CI processing
```

## Message Filtering (Current Workaround)
```bash
# Filter by sender
aish terma inbox | grep "Iris:"
aish terma inbox | grep -E "Iris:|Cali:"

# Filter by content
aish terma inbox | grep -i "json"

# Show recent messages only
aish terma inbox | grep "16:"        # Messages from 4pm hour
```

## Pro Tips
1. Pop old system messages in bulk to declutter
2. Use 'keep' inbox for important reminders
3. Filter with grep for now until better commands exist
4. Check inbox regularly - messages accumulate!