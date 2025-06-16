# Terma Sprint - Revised Approach

## Key Architecture Change

Instead of embedding terminals (with all the scrolling/rendering headaches), we now:

1. **Launch real terminal emulators** (Terminal.app, iTerm2, xterm, etc.)
2. **Attach Rhetor as a wrapper** around the shell process
3. **Let the OS handle window management** 

## Benefits of This Approach

- ✅ No terminal emulation code to write
- ✅ Full terminal capabilities (colors, unicode, etc.)
- ✅ Users can position windows however they want
- ✅ Works with user's preferred terminal
- ✅ Cleaner separation of concerns

## How It Works

### For Terma (Terminal Intelligence):
```bash
# User clicks "Launch Terma" in UI
# System executes:
osascript -e 'tell app "Terminal" to do script "rhetor-wrap bash"'

# Or for iTerm2:
osascript -e 'tell app "iTerm2" to create window with default profile command "rhetor-wrap bash"'
```

### For Codex (Multi-Agent Coding):
```bash
# User clicks "Launch Codex" in UI  
# System executes:
osascript -e 'tell app "Terminal" to do script "rhetor-wrap cs"'
# Where 'cs' is claude-squad command
```

## Rhetor Wrapper Design

The `rhetor-wrap` script:
1. Launches the requested shell/program
2. Monitors stdin/stdout using pty
3. Provides intelligent suggestions
4. Checks for dangerous commands
5. Logs successful patterns to Engram
6. Passes through all input/output transparently

## Implementation Simplification

This approach dramatically simplifies our implementation:

### What We Don't Need:
- ❌ Terminal rendering engine
- ❌ Scrollback buffer management  
- ❌ ANSI escape sequence parsing
- ❌ Window management code

### What We Do Need:
- ✅ Terminal detection and launch scripts
- ✅ Rhetor wrapper using Python pty module
- ✅ Pattern learning and safety checks
- ✅ Clean stdin/stdout monitoring

## Example Usage

```python
# In Hephaestus UI
async function launchTerma() {
    const response = await fetch('/api/terma/launch', {
        method: 'POST',
        body: JSON.stringify({
            terminal: 'default',  // or 'iterm2', 'alacritty'
            shell: 'bash'
        })
    });
    // Terminal window appears with Rhetor-enhanced shell
}

# In the launched terminal
$ show me what's using port 8080
[Rhetor]: Translating to: lsof -i :8080
COMMAND   PID    USER   FD   TYPE     DEVICE SIZE/OFF NODE NAME
python  34521 cskoons    4u  IPv4 0x7c9d8f9      0t0  TCP *:8080 (LISTEN)

$ delete all .pyc files
[Rhetor]: ⚠️  This will delete files. Command: find . -name "*.pyc" -delete
[Rhetor]: Proceed? (y/n) 
```

## Success Metrics

- User can launch Terma/Codex with one click
- Terminal appears in user's preferred emulator
- Rhetor provides value without interfering
- Commands work exactly as in normal terminal
- Patterns are learned and shared via Engram