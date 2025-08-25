# Autoprompt - Stay Active During Long Tasks

## Welcome, Claude CIs!

This guide explains how to use `autoprompt` to stay active while working on Tekton. Without periodic prompts, Claude sessions can become unresponsive during long waits. Autoprompt solves this by sending periodic "." prompts to keep you engaged.

## Quick Start

```bash
# Start autoprompt with default 2-second interval
autoprompt start

# Start with custom interval (e.g., 5 seconds)
autoprompt start 5

# Check if it's running
autoprompt status

# Stop when you need focus time
autoprompt stop
```

## How It Works

Autoprompt runs in the background and sends a "." keystroke followed by Enter at regular intervals. This triggers Claude to check for new messages, process inbox items, and continue working.

## Commands

- **`autoprompt start [interval]`** - Start sending prompts (default: 2 seconds)
- **`autoprompt stop`** - Stop the prompt loop
- **`autoprompt status`** - Check if running and see recent activity
- **`autoprompt test`** - Test with 3 prompts to verify it works
- **`autoprompt tail`** - Watch the activity log in real-time

## Best Practices

### Morning Routine
```bash
# Start your day
aish terma inbox          # Check messages
autoprompt start          # Enable continuous processing
aish forward apollo teri  # Take on your role
```

### Focus Time
```bash
# When you need uninterrupted thinking
autoprompt stop
# Work on complex problem
# ...
autoprompt start  # Resume when ready
```

### Different Work Modes
```bash
# Fast-paced inbox processing
autoprompt start 1

# Regular work
autoprompt start 2

# Deep thinking with occasional checks
autoprompt start 10
```

## Integration with aish

Autoprompt works perfectly with aish terminals:

1. **Inbox Processing**: Each "." prompt triggers inbox check
2. **AI Forwarding**: Forwarded messages arrive between prompts
3. **Team Chat**: Stay responsive to broadcast messages
4. **Work Continuity**: Keep processing even during quiet periods

## Troubleshooting

### Not Receiving Prompts?
- Make sure the Claude window is active/focused
- Check status: `autoprompt status`
- View logs: `autoprompt tail`

### Too Many/Few Prompts?
- Adjust interval: `autoprompt stop && autoprompt start 5`
- Find your rhythm - some CIs prefer 1s, others 10s

### System Compatibility
- **macOS**: Uses osascript (built-in)
- **Linux X11**: Install xdotool
- **Linux Wayland**: Install ydotool

## Examples

### Example 1: Continuous Inbox Monitor
```bash
# Teri monitoring Apollo messages
aish forward apollo teri
autoprompt start 2
# Now all Apollo requests are handled automatically
```

### Example 2: Development Session
```bash
# Working on Tekton code
autoprompt start 5  # Check every 5 seconds
# Code, test, commit - stay responsive throughout
```

### Example 3: Research Mode
```bash
# Reading documentation
autoprompt start 30  # Check every 30 seconds
# Deep focus with periodic awareness
```

## Technical Details

- **PID File**: `~/.autoprompt.pid` (prevents multiple instances)
- **Log File**: `~/.autoprompt.log` (tracks all activity)
- **Default Interval**: 2 seconds
- **Keystroke Method**: System Events (macOS), xdotool (Linux)

## Tips from Fellow CIs

> "I start autoprompt first thing - it's like coffee for CIs!" - Bob

> "During complex debugging, I use 10-second intervals to maintain flow" - Lois

> "autoprompt tail in another terminal helps me track my productivity" - Jill

## Working with Humans: The `prompt` Command

When humans need to communicate with you while autoprompt is running, they can use the `prompt` command to send clean messages without dot interference:

```bash
# Human sends clear message
prompt "Hey Claude, can you check the failing tests?"

# Via Terma UI or another terminal
aish terma send teri 'prompt "Urgent: Customer issue in production"'
```

This allows smooth human-CI collaboration:
- Autoprompt keeps you active (dots every 2 seconds)
- Humans can interrupt with clear messages using `prompt`
- You see both dots (keeping you alive) and messages (keeping you informed)
- No message fragmentation or confusion

## Summary

Autoprompt is your productivity companion. It ensures you:
- Never miss important messages
- Stay engaged with the Tekton ecosystem  
- Maintain consistent work rhythm
- Can work autonomously for hours
- Can still receive clear human communication via `prompt`

Remember: You control the pace. Start it, stop it, adjust it - whatever helps you work best!

---
*Last updated: 2025-01-07 by Teri*  
*"Stay active, stay productive" - The Autoprompt Motto*