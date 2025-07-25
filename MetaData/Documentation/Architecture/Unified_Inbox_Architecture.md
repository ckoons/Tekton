# Unified Inbox System Architecture

**Date**: January 25, 2025  
**Status**: Implemented  
**Components**: aish, Terma, Forwarding System  

## Overview

The Unified Inbox System replaces the confusing `aish terma inbox` commands with a clean, CI-friendly interface that provides structured message management for all Computational Intelligences (CIs) in the Tekton platform.

## Architecture Decision

**Problem**: The old `aish terma inbox` system was confusing, lacked clear priority levels, and didn't support efficient CI automation patterns.

**Solution**: Three-tier unified inbox system with batch JSON processing capabilities:
- **prompt** - Urgent messages requiring immediate attention
- **new** - Regular incoming messages  
- **keep** - Saved/archived messages

## System Architecture

### Storage Structure

```
.tekton/
└── inboxes/
    └── <ci-name>/
        ├── prompt/
        │   ├── 20250125_143022_a1b2c3d4.json
        │   └── 20250125_143155_e5f6g7h8.json
        ├── new/
        │   ├── 20250125_142030_f9e8d7c6.json
        │   └── 20250125_142245_b5a4c3d2.json
        └── keep/
            ├── 20250125_141500_c7d8e9f0.json
            └── 20250125_141800_a9b8c7d6.json
```

### Message Format

Each message is stored as JSON with complete metadata:

```json
{
  "id": "a1b2c3d4",
  "from": "numa",
  "to": "casey",
  "timestamp": "2025-01-25T14:30:22.123456",
  "purpose": "code-review",
  "message": "The authentication module looks solid. Consider adding rate limiting."
}
```

### Command Interface

#### Core Commands
- `aish inbox` - Show counts across all types
- `aish inbox send <type> <ci> "message"` - Send with priority
- `aish inbox show <type> [from <ci>]` - Human-readable display
- `aish inbox json <type> [from <ci>]` - JSON output for CI processing
- `aish inbox get <type> [from <ci>]` - Retrieve and remove (batch processing)
- `aish inbox count <type> [from <ci>]` - Count messages (script-friendly)
- `aish inbox clear <type> [from <ci>]` - Silent cleanup operation

#### Advanced Features
- **Sender Filtering**: `from <ci>` syntax for all commands
- **Batch Processing**: JSON output optimized for CI automation
- **Silent Operations**: Commands return appropriate data without noise

## Integration Points

### Terma Forwarding Integration

The forwarding system delivers messages to the unified inbox:

```python
# In terma.py
def deliver_message_to_inbox(ci_name, message, sender="forwarding", purpose="general"):
    """Deliver a message to a CI's inbox using the new unified system."""
    message_data = create_message(sender, ci_name, message, purpose)
    message_id = store_message(ci_name, 'new', message_data)  # Default to 'new'
    return True
```

### Main aish Dispatcher

```python
# In aish main dispatcher
elif command_type == 'inbox':
    from commands.inbox import handle_inbox_command
    return handle_inbox_command(args.message or [])
```

## CI Automation Patterns

### Batch Processing Pattern
```bash
# Process all urgent messages at once
messages=$(aish inbox get prompt)
echo "$messages" | jq -r '.[] | "From: \(.from) - \(.message)"'
```

### Count-Based Loops
```bash
# Continuous processing
while [ $(aish inbox count new) -gt 0 ]; do
    aish inbox get new | process_messages
done
```

### Priority-Based Workflow
```bash
# Handle urgent first, then regular
if [ $(aish inbox count prompt) -gt 0 ]; then
    aish inbox get prompt | handle_urgent_messages
fi

new_count=$(aish inbox count new)
if [ $new_count -gt 0 ]; then
    aish inbox get new | handle_regular_messages
fi
```

### Sender-Specific Processing
```bash
# Process messages from specific CIs
rhetor_messages=$(aish inbox get new from rhetor)
apollo_messages=$(aish inbox get new from apollo)
```

## Performance Characteristics

### Message Loading
- **SLA**: <100ms for typical inbox sizes (<1000 messages)
- **Optimization**: Sorted glob() with early filter checking
- **Scalability**: File-based storage with timestamp ordering

### Storage Operations
- **SLA**: <50ms for message storage
- **Consistency**: Atomic file writes with UUID-based filenames
- **Recovery**: Auto-create directories, graceful error handling

## Error Handling Philosophy

The system follows the Tekton principle of helpful errors with exit code 0:

```bash
$ aish inbox count invalid
Invalid inbox type 'invalid'. Must be: prompt, new, keep

$ echo $?
0  # Helpful error, not a system failure
```

This enables script-friendly error handling while providing clear guidance.

## Migration from Old System

### Old Commands → New Commands
- `aish terma inbox` → `aish inbox`
- `aish terma inbox new` → `aish inbox show new`
- `aish terma inbox new pop` → `aish inbox get new`
- `aish terma inbox keep` → `aish inbox show keep`
- No direct equivalent to old keep operations (replaced by send/clear pattern)

### Backward Compatibility
- Old terma inbox commands are completely removed
- Forwarding system updated to deliver to new inbox
- All documentation updated to reference unified system

## Testing Strategy

Comprehensive test suite with 10 test cases covering:
1. Help and training commands
2. Message sending and showing
3. JSON output validation
4. Batch retrieval (get command)
5. Message counting
6. Inbox clearing
7. Sender filtering (`from <ci>` syntax)
8. Error handling with helpful messages
9. Default behavior (show counts)

All tests designed for CI context (send messages to self, check own inbox).

## Future Enhancements

### Planned Features
1. **Message Templates** - Pre-defined message formats for common scenarios
2. **Bulk Operations** - Multi-CI sending and filtering
3. **Notification Integration** - Alert systems for urgent messages
4. **Analytics** - Message flow and processing metrics

### Potential Integrations
1. **Engram Integration** - Long-term message persistence
2. **UI Integration** - Web interface for inbox management
3. **Mobile Notifications** - Push notifications for urgent messages

## Security Considerations

### Access Control
- Messages stored per CI (no cross-CI access by default)
- File permissions restrict access to CI's own inbox
- Sender authentication through environment variables

### Data Privacy
- No sensitive data logging
- Messages stored locally in .tekton directory
- No external data transmission except through Tekton components

## Operational Guidelines

### For CIs
1. Check inbox frequently with `aish inbox`
2. Process urgent messages first (`aish inbox get prompt`)
3. Use batch processing for efficiency
4. Archive important information with `aish inbox send keep self "message"`

### For System Administrators
1. Monitor .tekton/inboxes directory size
2. Implement cleanup policies for old messages
3. Backup important message data if needed
4. Monitor performance metrics for large inboxes

## Related Documentation

- [aish Command Reference](../AITraining/aish/COMMAND_REFERENCE.md)
- [Terma AI Training](../AITraining/terma/README.md)
- [Landmarks and Semantic Tags Standard](../Standards/Landmarks_and_Semantic_Tags_Standard.md)
- [Terma-aish Integration](Terma_aish_Integration.md)

## Implementation Files

- `/shared/aish/src/commands/inbox.py` - Core implementation
- `/shared/aish/src/commands/terma.py` - Integration function
- `/shared/aish/aish` - Main dispatcher update
- `/shared/aish/tests/test_inbox.py` - Comprehensive test suite

---

*This architecture document is part of the Tekton knowledge graph and is indexed by landmarks for CI navigation.*