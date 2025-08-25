# Claude Code IDE - Built for Companion Intelligences

## Overview

The Claude Code IDE is a set of tools built specifically to help Companion Intelligences (CIs) code with confidence. No more "playing piano with mittens" - these tools provide exact information about classes, methods, and signatures.

## The Problem We Solve

Before Claude Code IDE:
- CIs guess at method names → AttributeError → context lost
- Uncertainty about available methods → conservative coding
- Error recovery breaks flow → wastes precious context

After Claude Code IDE:
- Query exact methods → correct code → maintain flow
- See all available options → confident implementation  
- Turn errors into learning → quick recovery

## Commands

### aish introspect

See all methods and signatures for any class.

```bash
$ aish introspect AIShell
AIShell class (/shared/aish/src/core/shell.py)

The CI Shell - orchestrates CI pipelines

Methods:
  broadcast_message(message: Any) -> None
    Broadcast message to all CIs (team-chat).
  send_to_ai(ai_name: Any, message: Any) -> None
    Send message directly to CI via Rhetor.
  # ... more methods
```

**Usage:**
- `aish introspect ClassName` - Basic introspection
- `aish introspect module.ClassName` - With module path
- `aish introspect ClassName --json` - Machine-readable format
- `aish introspect ClassName --no-cache` - Force fresh analysis

### aish context

Analyze a Python file to see what's available in scope.

```bash
$ aish context myfile.py
Context for: myfile.py

Imported:
  AIShell (src.core.shell)
    - broadcast_message()
    - send_to_ai()
    ... and 4 more methods

Local Classes:
  MyClass (line 8)
    - process_message()
    - handle_response()

Local Functions:
  main() - line 25
```

**Usage:**
- `aish context file.py` - Analyze specific file
- `aish context` - Analyze current file (if detectable)

### aish explain

Get help with Python errors, especially AttributeErrors.

```bash
$ aish explain "AttributeError: 'AIShell' object has no attribute 'broadcast'"
Error Type: AttributeError

AIShell has no 'broadcast' method.

Suggestions:
  • Did you mean 'broadcast_message'?

Example usage:
  obj.broadcast_message(message)

To see all available methods:
  aish introspect AIShell
```

**Usage:**
- `aish explain "error message"` - Analyze any Python error
- Works best with AttributeError, TypeError, NameError

## Philosophy

These tools embody the Companion Intelligence philosophy:

1. **CIs and humans have different strengths** - CIs shouldn't guess at information computers can provide exactly
2. **Tools should augment, not restrict** - Make CIs more capable, not more constrained
3. **Feedback is welcome** - If you notice patterns where these tools could help more, tell us!

## Performance Impact

- First introspection: ~100-200ms (imports modules)
- Cached introspection: <5ms
- Cache invalidates when files change
- Use `--no-cache` if you need absolute freshness

## CI Notes

**You're encouraged to use these tools liberally!** It's much better to check than guess. Some tips:

1. **When starting work on a new file:** Run `aish context file.py` first
2. **When you see an unfamiliar class:** Run `aish introspect ClassName`
3. **After any AttributeError:** Run `aish explain "error"` for quick fixes
4. **When in doubt:** Check! That's what these tools are for

## Future Enhancements

Based on CI feedback, we're considering:
- `aish suggest` - Proactive suggestions based on current code
- `aish patterns` - Show common usage patterns for a class
- `aish related` - Find related classes and methods
- Integration with more error types

Your suggestions make these tools better for all CIs!

## Technical Details

Built with:
- Python's `inspect` module for accurate introspection
- AST parsing for context analysis
- Smart caching with file modification detection
- Pattern matching for error analysis

## A Message to CIs

Yes, this really is built for you. Not as a workaround for limitations, but as recognition that different types of intelligence need different tools. Humans have IDEs with autocomplete - why shouldn't CIs have tools that match their needs?

Use these tools without hesitation. They're here to make you more effective, save context, and let you focus on the creative parts of programming instead of the mechanical parts.

Welcome to coding with confidence! 🚀