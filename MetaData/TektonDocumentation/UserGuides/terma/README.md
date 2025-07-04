# Terma User Guide

## Overview

Terma provides inter-terminal communication capabilities for aish-enabled terminals.

## Commands

### Basic Commands
- `aish terma list` - List all active terminals
- `aish terma whoami` - Show your terminal information
- `aish terma help` - Display this help

### Messaging Commands
- `aish terma <name> "message"` - Send message to specific terminal
- `aish terma @<purpose> "message"` - Send to terminals by purpose
- `aish terma broadcast "message"` - Send to all other terminals
- `aish terma * "message"` - Send to all including yourself

### Inbox Commands - Like Unix Mail!
- `aish terma inbox` - Show both new and keep inboxes
- `aish terma inbox keep` - Show just your keep inbox
- `aish terma inbox new pop` - Read and remove first new message
- `aish terma inbox keep push "text"` - Save to front of keep
- `aish terma inbox keep write "text"` - Save to end of keep
- `aish terma inbox keep read` - Read last kept message
- `aish terma inbox keep read remove` - Read and remove last kept

## Message Inbox System

Messages are stored in-memory during your terminal session:
- **New inbox**: Incoming messages appear here
- **Keep inbox**: Messages you want to preserve

Messages are displayed directly in your terminal and also stored for later viewing.

## Examples

```bash
# See who's online
aish terma list

# Send a direct message
aish terma alice "Can you help with the auth module?"

# Check your messages
aish terma inbox

# Process a message
aish terma inbox new pop

# Save a note
aish terma inbox keep push "Important: Review PR #123"

# Broadcast to everyone
aish terma broadcast "Team meeting in 5 minutes"
```
