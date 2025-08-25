# aish Command Line Parsing Bug - Debug Notes

## Problem
The command `aish numa "Hello there"` fails with "No message provided for numa"

## Root Cause Discovery
Casey identified: "damn quotes, someone is not preserving on the parse"

### Investigation Results

1. **Shell passes arguments correctly**:
   - `AISH_TRACE=1 aish numa "Hello there"` shows: `sys.argv = ['aish', 'numa', 'Hello there']`
   - The shell properly preserves the quoted string as a single argument

2. **Argparse configuration issue**:
   ```python
   parser.add_argument('ai_or_script', nargs='?', help='CI name or script')
   parser.add_argument('message', nargs='*', help='Message to send')
   ```

3. **The bug**: When you pass `aish numa "Hello there"`:
   - Argparse sees 3 arguments total
   - Position 1: 'numa' → assigned to `ai_or_script` ✓
   - Position 2: 'Hello there' → ALSO assigned to `ai_or_script` (because nargs='?') ✗
   - Result: `args.message` is empty!

## Why It Happens
- `nargs='?'` means "zero or one" - it greedily takes the next positional argument
- When the message is quoted as a single argument, argparse incorrectly assigns it to `ai_or_script`
- This leaves the `message` array empty, triggering the "No message provided" error

## Current Workarounds
1. Don't use quotes: `aish numa Hello there` (multiple args work)
2. Use pipe syntax: `echo "Hello there" | aish numa`

## Fix Needed
The argument parser needs to be restructured to properly handle quoted messages as a single argument while still supporting the flexible command syntax.

---
*Debug notes by Jane (Claude) for the Casey/Claude development team*
*Created: 2025-01-04*