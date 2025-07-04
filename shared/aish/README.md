# aish - The AI Shell

A thin client providing AI orchestration and inter-terminal communication for the Tekton platform.

## Features

- **Direct AI Communication**: Send messages to any Tekton AI specialist
- **Inter-Terminal Messaging**: Communicate between aish-enabled terminals
- **Unix-style Inbox**: Manage messages with new/keep inboxes
- **Pipeline Support**: Chain AI operations together
- **Help System**: Integrated documentation paths

## Components

- `aish` - Main command for AI interaction
- `aish-proxy` - Terminal enhancement providing heartbeat and message display
- `aish-history` - History management tool
- `clean_registry.py` - AI registry maintenance
- `launch_component_ai.py` - Atomic AI specialist replacement
- `src/` - Core Python implementation

## Usage

### Basic AI Commands

```bash
# Direct message to AI (NEW: quoted messages now work!)
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
- `TERMA_TERMINAL_NAME` - Terminal name for messaging

## Known Issues

1. **Inbox Operations**: Only work in terminals started AFTER July 4, 2025. Older terminals display messages but command processing (pop/push) doesn't modify state.

2. **Socket Communication**: Some AI specialists may fail with "Failed to send message". This typically means:
   - The AI process crashed
   - Port conflict
   - Registry out of sync
   
   **Fix**: Run `python3 clean_registry.py` and restart affected components

3. **stdin Detection**: Fixed - aish now correctly prioritizes command-line arguments over stdin detection.

## Troubleshooting

### "No message provided" Error
- Update to latest aish version
- The syntax `aish numa "hello"` now works correctly

### AI Not Responding
1. Check if AI is registered: `tekton-status`
2. Clean registry: `python3 clean_registry.py`
3. Restart component: `./run_rhetor.sh --clean-registry`

### Inbox Commands Not Working
- Only terminals started after the fix have working inbox command processing
- Messages still display correctly in all terminals
- Restart your terminal session to get the latest code

## Development

### Running Tests
```bash
./test_aish.sh  # Basic syntax tests
```

### Registry Management
- `clean_registry.py`: Remove stale AI entries
- `launch_component_ai.py`: Atomic AI replacement
- `cleanup_orphan_processes.py`: Detect and remove orphaned AI processes
- Registry located at: `~/.tekton/ai_registry/platform_ai_registry.json`

### Orphan Process Cleanup
- Automatic cleanup via Shared Services (every 6 hours)
- Manual cleanup: `python3 cleanup_orphan_processes.py`
- Safe detection with multiple verification steps
- See `shared/services/README.md` for service configuration

### New Features (July 2025)
- Fixed quoted message syntax
- Added registry cleanup on Rhetor startup
- Component-specific AI replacement
- Launch flags: `-n` (no AI), `--clean-registry`

---

Part of the Tekton Multi-AI Engineering Platform