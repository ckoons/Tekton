# Sprint: Claude Code IDE - No More Guessing

## Overview
Build an IDE-like interface that Claude Code can query to get accurate class methods, signatures, and usage examples. Stop the guessing, start the flowing.

## Goals
1. **Perfect Information**: Claude sees exactly what methods exist
2. **Zero Guessing**: Every method call is informed
3. **Natural Interface**: Works with Claude's tools

## How Claude Would Use It

### Option 1: Direct Query Tool
```bash
# Claude thinks there might be a broadcast method
aish introspect AIShell | grep broadcast
# Returns: No methods matching 'broadcast'

# Claude wants to see all methods
aish introspect AIShell
# Returns:
# AIShell class methods:
#   send_message(ai_name: str, message: str) -> str
#   handle_team_chat(message: str) -> None
#   get_active_terminals() -> List[str]
```

### Option 2: Context-Aware File Analysis
```bash
# Claude is editing a file
aish context ./my_file.py
# Returns:
# Available in scope:
#   AIShell (imported from ai_shell)
#     - send_message(ai_name: str, message: str) -> str
#   MessageHandler (imported from message_handler)
#     - forward_message(msg: str) -> bool
```

### Option 3: Smart Error Helper
```bash
# Claude made an error
aish explain "AttributeError: 'AIShell' object has no attribute 'broadcast_message'"
# Returns:
# AIShell has no 'broadcast_message' method.
# Did you mean:
#   - handle_team_chat(message: str) - Sends to all team members
#   - send_message(ai_name: str, message: str) - Sends to specific AI
```

## Phase 1: Introspection Engine [0% Complete]

### Tasks
- [ ] Create introspection module that can analyze Python classes
- [ ] Build method signature extractor
- [ ] Generate human-readable output
- [ ] Cache results for performance
- [ ] Handle dynamic imports and lazy loading

### Success Criteria
- [ ] Can introspect any Tekton class
- [ ] Shows accurate signatures
- [ ] Fast enough for interactive use

### Technical Approach
```python
# /shared/aish/src/introspect/inspector.py
import inspect
import importlib

class TektonInspector:
    def get_class_info(self, class_path: str):
        # Returns all methods, signatures, docstrings
        # Handles imports, finds the class
        # Extracts parameter types from hints
```

## Phase 2: Query Interface [0% Complete]

### Tasks
- [ ] Create `aish introspect [class]` command
- [ ] Create `aish context [file]` command  
- [ ] Create `aish explain [error]` command
- [ ] Add `--json` output for machine parsing
- [ ] Add usage examples from codebase

### Success Criteria
- [ ] Claude can query any class
- [ ] Context-aware suggestions
- [ ] Error explanations are helpful

### Example Outputs
```bash
$ aish introspect MessageHandler
MessageHandler (/shared/aish/src/message_handler.py)
Methods:
  __init__(terminal_name: str)
  send(message: str, ai_name: str = None) -> dict
    Send a message to an AI or terminal
    Example: handler.send("hello", "numa")
  
  handle_forwarding(message: str) -> bool
    Check if message should be forwarded
    Returns: True if forwarded, False otherwise
```

## Phase 3: IDE Integration [0% Complete]

### Tasks
- [ ] Create always-on introspection server
- [ ] Build file watcher for real-time updates
- [ ] Generate IDE protocol responses
- [ ] Create method completion database
- [ ] Add fuzzy search for "did you mean?"

### Success Criteria
- [ ] Real-time method information
- [ ] Accurate "did you mean?" suggestions
- [ ] No performance impact

## Phase 4: Usage Pattern Learning [0% Complete]

### Tasks
- [ ] Track common Claude errors
- [ ] Build pattern database
- [ ] Create proactive hints
- [ ] Generate usage examples from actual code
- [ ] Learn from successful calls

### Success Criteria
- [ ] Anticipates common mistakes
- [ ] Suggests patterns that work
- [ ] Learns from Tekton codebase

### Example Learning
```bash
# Claude often tries: ai_shell.broadcast()
# System learns to suggest: handle_team_chat()
# Proactively shows this mapping
```

## Phase 5: Documentation Generation [0% Complete]

### Tasks
- [ ] Auto-generate API docs from introspection
- [ ] Create method usage maps
- [ ] Build relationship diagrams
- [ ] Generate "Claude-friendly" summaries
- [ ] Keep docs always current

### Success Criteria
- [ ] Docs match code exactly
- [ ] Claude can reference them
- [ ] Auto-updates with code changes

## Technical Decisions
- Use Python introspection (inspect module)
- Cache results but verify on changes
- Return both human and machine-readable formats
- Focus on speed - must be interactive
- Learn from actual usage patterns

## Out of Scope
- Full IDE implementation
- Syntax highlighting
- Code completion protocol
- Visual interface

## Claude Interface Patterns

### Natural Query Flow
1. Claude attempts something
2. Gets error or uncertainty
3. Queries: `aish introspect ClassName`
4. Sees exact methods available
5. Uses correct method
6. Flow continues unbroken

### Proactive Assistance
```bash
# Claude's context shows imports
# IDE pre-loads available methods
# Shows inline when Claude references class
```

### Error Recovery
```bash
# Claude hits AttributeError
# Runs: aish explain "[error]"
# Gets immediate correction
# No context break
```

## Files to Create
```
/shared/aish/src/introspect/
  __init__.py
  inspector.py          # Core introspection engine
  cache.py             # Performance caching
  patterns.py          # Usage pattern learning
  
/shared/aish/src/commands/
  introspect.py        # CLI commands
  context.py           # Context analysis
  explain.py           # Error explainer

/shared/aish/src/ide/
  server.py            # Always-on IDE server
  protocol.py          # IDE protocol handler
```

## Why This Works for Claude

1. **Tool-Based**: Uses existing tool patterns Claude knows
2. **Text Output**: Returns readable text, not complex UI
3. **Query-Driven**: Claude asks when needed
4. **Context-Aware**: Understands current file/imports
5. **Error-Friendly**: Turns mistakes into learning

Claude Code's strength is understanding context and patterns. This IDE gives perfect information in a format Claude naturally uses. No more playing piano with mittens - every note is informed.