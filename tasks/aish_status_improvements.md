# Task: Improve `aish status` Command

## Current Issues
The `aish status` command is not providing complete or accurate information. Many components are missing and key system information is not displayed.

## Required Improvements

### 1. System Information (Top Section)
```
aish Status Report
==================================================
TEKTON_ROOT: /Users/cskoons/projects/github/Coder-C
Tekton Core: ✓ Running (v2.0.0) on port 8310
aish MCP: ✓ Running (v1.0.0) on port 8318
==================================================
```

### 2. Greek Chorus Components (Complete List)
Currently missing: engram, hermes, ergon, terma, penia, noesis, hephaestus, iris
Should show ALL components with their status and ports:
- Regular CI ports (83xx)
- AI specialist ports (42xxx)

### 3. CI Tools Status
```
CI Tools:
------------------------------
  ✓ echo_tool      (available)
  ✓ message_bus    (socket: /tmp/ci_message_bus.sock)
  ✓ context_manager (available)
```

### 4. Active Forwards (Enhanced)
```
Active AI Forwards:
------------------------------
  apollo     → Terminal: Casey (TTY: /dev/ttys001)
  iris       → Terminal: Casey (TTY: /dev/ttys002)
  
Active Project Forwards:
------------------------------
  Tekton     → Terminal: Beth (TTY: /dev/ttys003)
  claude-code → Terminal: None
```

### 5. Terminal Detection (Improved)
```
Active Terminals:
------------------------------
  Casey: /dev/ttys001 (apollo)
  Casey: /dev/ttys002 (iris)
  Beth:  /dev/ttys003 (Tekton)
```

### 6. Connection Status
```
Component Connections:
------------------------------
  MCP → aish: ✓ Connected
  MCP → Tekton: ✓ Connected
  Message Bus: ✓ Active (3 clients)
```

### 7. Recent Activity (Enhanced)
```
Recent Commands (last 10):
------------------------------
  1. [2025-08-05 10:15:23] apollo: "Hello from Casey"
  2. [2025-08-05 10:14:15] team-chat: "Planning session"
  3. [2025-08-05 10:13:00] aish restart
  ...
```

## Implementation Notes

1. **Component Detection**: 
   - Check `shared/aish/src/registry/ci_registry.py` for complete component list
   - Verify both CI ports (83xx) and AI ports (42xxx)

2. **Process Detection**:
   - Use `ps aux | grep` to find running processes
   - Check for both Python processes and CI tools

3. **Terminal Detection**:
   - Parse `who` or `w` command output
   - Match with forward configurations

4. **Version Information**:
   - Read from version files or query endpoints
   - Show "Unknown" if not available

5. **Color Coding**:
   - ✓ Green for active/connected
   - ✗ Red for inactive/error
   - ? Yellow for unknown status

## Priority
High - This is a critical diagnostic tool for the Tekton ecosystem

## Assigned to: Iris