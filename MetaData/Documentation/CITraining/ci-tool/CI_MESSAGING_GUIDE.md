# CI Tool Messaging Guide

## Overview

The `ci-tool` command enables any program (Claude Code, shell scripts, CI tools, etc.) to communicate with others using simple @ commands. Messages are routed through Unix sockets and appear naturally in the output.

## Quick Start

### Launch Claude Code with Messaging

```bash
# Terminal 1 - Casey using Claude
ci-tool --name Casey --ci claude-opus-4 -- claude --debug

# Terminal 2 - Beth using Claude  
ci-tool --name Beth -- claude
```

### Launch Other Programs with Messaging

```bash
# Shell script that uses llama
ci-tool --name henry --ci llama3.3:70b -- my-ai-script.sh

# Python CI assistant
ci-tool --name DataBot --ci gpt-4 -- python assistant.py

# Any command - no CI hint needed
ci-tool --name processor -- ./data-processor.sh
```

## How It Works

1. **Output Parsing**: The wrapper monitors stdout for @ commands
2. **Background Sending**: When detected, messages are sent via Unix sockets
3. **Input Injection**: Incoming messages appear in stderr (visible but separate)
4. **Registry Integration**: All wrapped programs register with their --name identifier

### Parameters

- `--name`: Required. The identifier used for messaging (e.g., Casey, Beth, coder-b)
- `--ci`: Optional. A hint about what CI/model the program uses (just metadata)
- `--dir`: Optional. Working directory (defaults to current directory)

## @ Commands

Commands are written naturally in CI responses:

- `@send target "message"` - Send a message to another CI
- `@ask target "question"` - Ask a question (expects reply)
- `@reply target "answer"` - Reply to a previous message
- `@status` - Check message status

## Example Usage

### Casey's Terminal
```
User: Please work with Beth to update the API documentation

Claude: I'll coordinate with Beth on updating the API documentation.

@send Beth "Hi Beth, Casey asked me to work with you on updating the API documentation. Are you available to collaborate on this?"

I've sent a message to Beth. Let me start by reviewing the current API documentation while waiting for her response.
```

### Beth's Terminal
```
[10:32] Message from Casey: Hi Beth, Casey asked me to work with you on updating the API documentation. Are you available to collaborate on this?

User: Yes, help with the API docs

Claude: I see Casey wants us to collaborate on the API documentation. I'll let them know I'm ready.

@reply Casey "Hi Casey, yes I'm available to work on the API documentation. I'll start by reviewing the current endpoints. Which sections should we prioritize?"

Let me begin examining the API documentation structure...
```

## Features

### Code Block Safety
@ commands inside code blocks are NOT parsed:
```python
# This won't trigger a send
def example():
    return "@send target message"
```

### Message Types
- **Regular messages**: Simple communication
- **Questions**: Expect a reply
- **Replies**: Respond to questions

### Background Operation
- Messages send silently in background
- User sees the @ command for transparency
- Recipient gets notification between interactions

## Integration with Tekton

Eventually, this can be launched from Tekton's UI:
1. User clicks "Launch Terminal" 
2. Selects CI type (Claude, Numa, etc.)
3. Terminal opens with messaging pre-configured
4. CI can collaborate with others naturally

## Advantages

1. **Universal**: Works with ANY command-line CI tool
2. **Transparent**: Users see all @ commands sent
3. **Non-intrusive**: Doesn't modify the CI itself
4. **Natural**: CIs use commands in normal conversation
5. **Async**: Messages queue for delivery

## Technical Details

- Messages route through Unix domain sockets
- Each wrapped program gets a unique socket: `/tmp/ci_msg_<name>.sock`
- Registry tracks all active CIs and their sockets
- Parser ignores @ commands in code blocks
- Messages appear in stderr to avoid stdout interference

## Troubleshooting

### Message Not Delivered
- Check target is registered: Look for socket file
- Verify target name matches their --name parameter
- Check socket permissions

### Parser Issues  
- Ensure @ command is not in code block
- Command must match pattern: `@cmd target "message"`
- Check wrapper is running (see stderr output)

### Socket Errors
- Remove stale sockets: `rm /tmp/ci_msg_*.sock`
- Check permissions on /tmp directory
- Verify Python can create Unix sockets