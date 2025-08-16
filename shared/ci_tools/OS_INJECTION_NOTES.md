# OS Injection Notes and Limitations

## How It Works
OS-level keystroke injection simulates real keyboard input at the operating system level, bypassing stdin. This is necessary for TUI programs like Claude that ignore stdin in interactive mode.

## Critical Limitation: Window Focus
**OS injection sends keystrokes to the CURRENTLY FOCUSED window**, not to a specific process. This means:

1. When you run `aish bebe-ci "message" -x`, the keystrokes are sent to YOUR terminal, not Claude's
2. For it to work, Claude's window must be the active/focused window
3. This is why `autoprompt` works - it runs while you have Claude focused

## Workarounds

### Option 1: Manual Window Switch
```bash
# Send the message with a delay
(sleep 3; aish bebe-ci "message" -x) &
# Quickly switch to Claude's window within 3 seconds
```

### Option 2: Use autoprompt
Keep Claude active and responsive with autoprompt:
```bash
# In Claude's terminal
autoprompt start 2  # Sends "." every 2 seconds to keep Claude active
```

### Option 3: Use PTY injection (won't work for Claude)
Force PTY-only mode:
```bash
aish ci-terminal --name claude-ci --os-injection off -- claude
```
Note: This won't work for Claude's interactive mode but works for many other programs.

### Option 4: Use Claude's --print mode (future)
Claude has a `--print` mode that works with stdin:
```bash
echo "message" | claude --print
# Or with session continuity
echo "message" | claude --print --continue
```

## Technical Details

### macOS (osascript)
- Can activate specific applications with `tell application "AppName" to activate`
- But Claude runs inside a terminal, not as its own app
- Can't easily target a specific terminal tab/window

### Linux (xdotool)
- Can search for windows by name: `xdotool search --name "pattern"`
- Can focus specific windows: `xdotool windowfocus <window_id>`
- More powerful than macOS for window targeting

### Why This Happens
1. Claude in interactive mode uses a TUI (Terminal User Interface)
2. TUIs read keyboard events directly, not from stdin
3. OS injection simulates real keyboard events
4. But keyboard events go to the focused window
5. We can't easily programmatically focus Claude's specific terminal window

## Recommendations

For automated Claude interaction:
1. **Development/Testing**: Use `autoprompt` to keep Claude responsive
2. **Production**: Consider Claude's `--print` mode with `--continue` for session management
3. **Future Enhancement**: Implement window detection and focusing (complex, platform-specific)

## Testing OS Injection

```bash
# Test if OS injection works on your system
python3 shared/ci_tools/os_injection.py --test

# Check what method is available
python3 shared/ci_tools/os_injection.py --info

# Test with a specific program (must be focused!)
aish ci-terminal --name test-vi --os-injection on -- vi
# Then quickly focus the vi window and send:
aish test-vi "ihello" -x "\x1b"  # 'i' for insert, 'hello', ESC to exit insert
```