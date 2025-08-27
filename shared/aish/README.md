# aish - The CI Shell

A thin client providing CI orchestration and inter-terminal communication for the Tekton platform.

## Features

- **Direct CI Communication**: Send messages to any Tekton CI specialist
- **Inter-Terminal Messaging**: Communicate between aish-enabled terminals
- **Unix-style Inbox**: Manage messages with new/keep inboxes
- **Pipeline Support**: Chain CI operations together
- **Help System**: Integrated documentation paths

## Components

- `aish` - Main command for CI interaction
- `aish-proxy` - Terminal enhancement providing heartbeat and message display
- `aish-history` - History management tool
- `src/` - Core Python implementation

## Usage

### Basic CI Commands

```bash
# Direct message to CI (NEW: quoted messages now work!)
aish numa "How do I optimize this workflow?"
aish apollo "Analyze this codebase for issues"

# Pipe input to AI
echo "What patterns exist here?" | aish noesis
cat file.py | aish athena

# Multiple word messages work
aish sophia "explain machine learning concepts"
```

### Inter-Terminal Communication (Terma)

```bash
# List active terminals
aish terma list

# Send direct message
aish terma alice "Need help with the auth module"

# Broadcast to all
aish terma broadcast "Team meeting in 5 minutes"

# Send by purpose
aish terma @planning "Sprint planning at 3pm"
```

### Inbox Management

```bash
# Check both inboxes
aish terma inbox

# Pop message from new (FIFO)
aish terma inbox new pop

# Save to keep inbox
aish terma inbox keep push "Important note"
aish terma inbox keep write "Another note"

# Read from keep (LIFO)
aish terma inbox keep read
aish terma inbox keep read remove  # Read and remove
```

## Integration with Terma

When launched via Terma, terminals automatically have:
- aish available in PATH
- Heartbeat communication with Terma
- Inter-terminal messaging capabilities
- Inbox functionality

## Environment Variables

- `RHETOR_ENDPOINT` - Override default Rhetor endpoint (default: http://localhost:8003)
- `AISH_ACTIVE` - Set by aish-proxy when active
- `AISH_DEBUG` - Enable debug output
- `TERMA_SESSION_ID` - Set by Terma for terminal tracking
- `TEKTON_NAME` - Terminal name for messaging

## Known Issues

1. **Inbox Operations**: Only work in terminals started AFTER July 4, 2025. Older terminals display messages but command processing (pop/push) doesn't modify state.

2. **Socket Communication**: Some CI specialists may fail with "Failed to send message". This typically means:
   - The CI process crashed
   - Port conflict
   
   **Fix**: Restart affected CI components

3. **stdin Detection**: Fixed - aish now correctly prioritizes command-line arguments over stdin detection.

## Troubleshooting

### "No message provided" Error
- Update to latest aish version
- The syntax `aish numa "hello"` now works correctly

### CI Not Responding
1. Check if CI is running: `tekton-status`
2. Check port is open: `nc -zv localhost 45000`
3. Restart component if needed

### Inbox Commands Not Working
- Only terminals started after the fix have working inbox command processing
- Messages still display correctly in all terminals
- Restart your terminal session to get the latest code

## Development

### Running Tests
```bash
./test_aish.sh  # Basic syntax tests
```

### Port Management
- Configurable port formula: CI port = TEKTON_AI_PORT_BASE + (component_port - TEKTON_PORT_BASE)
- Check port alignment: `scripts/check_port_alignment.py`
- `cleanup_orphan_processes.py`: Detect and remove orphaned CI processes

### Orphan Process Cleanup
- Automatic cleanup via Shared Services (every 6 hours)
- Manual cleanup: `python3 cleanup_orphan_processes.py`
- Safe detection with multiple verification steps
- See `shared/services/README.md` for service configuration

### New Features (July 2025)
- Fixed quoted message syntax
- Simplified to fixed port system
- Component-specific CI management
- Launch flags: `-n` (no AI)

---

Part of the Tekton Multi-CI Engineering Platform
