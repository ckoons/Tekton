# Claude Code IDE Sprint

## The Problem
Claude Code is playing piano with mittens - guessing at method names, getting AttributeErrors, breaking flow. Every guess costs context and time.

## The Solution
An IDE-like interface that Claude can query to get perfect information about classes, methods, and signatures. No more guessing.

## How Claude Uses It

### When Uncertain
```bash
# Claude wonders what methods AIShell has
aish introspect AIShell

# Output:
AIShell class (/shared/aish/src/ai_shell.py):
  send_message(ai_name: str, message: str) -> str
  handle_team_chat(message: str) -> None
  get_active_terminals() -> List[str]
```

### When Coding
```bash
# Claude is editing a file
aish context current_file.py

# Output:
Available in your scope:
  MessageHandler (from .message_handler import MessageHandler)
    - send(message: str, ai_name: str = None) -> dict
    - handle_forwarding(message: str) -> bool
```

### When Errors Occur
```bash
# Claude gets AttributeError
aish explain "AttributeError: 'AIShell' object has no attribute 'broadcast_message'"

# Output:
AIShell has no 'broadcast_message' method.
Did you mean:
  - handle_team_chat(message: str) - Sends to all team members
  - send_message(ai_name: str, message: str) - Sends to specific AI

Example usage:
  shell.handle_team_chat("Hello team")
```

## Key Features

1. **Introspection Engine** - Real Python introspection, not documentation
2. **Context Awareness** - Knows what's imported in current file
3. **Error Explanation** - Turns errors into corrections
4. **Usage Examples** - Shows real code that works
5. **Performance** - Cached but always accurate

## Why This Changes Everything

- **Before**: Claude guesses, gets errors, loses context
- **After**: Claude queries, gets truth, maintains flow

It's the difference between stumbling in the dark and having the lights on.

## Technical Approach

- Python's `inspect` module for truth
- Smart caching for speed
- Text-based interface Claude understands
- Learn from patterns of mistakes

## Success Metrics

- Zero AttributeErrors from guessing
- Faster development cycles
- Less context loss
- More confident Claude