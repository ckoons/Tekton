# aish/Terma Terminal System User Guide

## Overview

The aish/Terma terminal system provides an AI-enhanced command-line experience that integrates seamlessly with the Tekton ecosystem. This guide covers everything you need to know to use aish effectively with Terma terminals.

## What is aish?

**aish** (AI Shell) is a thin client that provides:
- Direct communication with AI specialists
- Inter-terminal messaging between users
- Command orchestration and pipelining
- Integration with the Terma terminal system

## What is Terma?

**Terma** is an advanced terminal emulator that provides:
- Full PTY-based terminal sessions
- WebSocket-based real-time communication
- LLM assistance for commands
- Rich UI integration with Hephaestus
- Session management and recovery

## Getting Started

### Initial Setup

1. **Ensure Terma is running**:
```bash
# Check Terma status
tekton-status | grep Terma

# Launch Terma if needed
./scripts/tekton-launch --components terma
```

2. **Enable aish in your shell**:
```bash
# Add to your .bashrc or .zshrc
export PATH="$TEKTON_ROOT/shared/aish:$PATH"

# Source the aish proxy for enhanced features
source $TEKTON_ROOT/shared/aish/aish-proxy
```

3. **Verify installation**:
```bash
aish --version
aish help
```

## Core Features

### 1. AI Communication

#### Direct Messages
Send messages to any AI specialist:

```bash
# Basic syntax
aish <ai-name> "<message>"

# Examples
aish hermes "What services are currently running?"
aish codex "Analyze this Python function for bugs"
aish rhetor "Help me write a better prompt"
```

#### Available AI Specialists
- **hermes** - Service orchestration and health
- **engram** - Memory and search
- **rhetor** - Prompt engineering
- **athena** - Knowledge graphs
- **ergon** - Agent creation
- **codex** - Code analysis
- **telos** - Requirements management
- **prometheus** - Strategic planning
- **harmonia** - Workflow orchestration
- **sophia** - Learning and improvement
- **metis** - Testing strategies
- **apollo** - Monitoring and analytics
- **budget** - Resource optimization
- **hephaestus** - UI/UX assistance

#### Piping and Redirection
```bash
# Pipe file content to AI
cat error.log | aish apollo "What's causing these errors?"

# Analyze command output
docker ps | aish hermes "Are all expected services running?"

# Save AI response
aish codex "Generate a Python logging module" > logger.py
```

### 2. Inter-Terminal Communication

#### List Active Terminals
```bash
# See all active aish-enabled terminals
aish terma list

# Example output:
# Active terminals:
# - alice (purpose: frontend, tty: /dev/ttys001)
# - bob (purpose: backend, tty: /dev/ttys002)
# - casey (purpose: testing, tty: /dev/ttys003)
```

#### Send Direct Messages
```bash
# Send to specific user
aish terma alice "Found the bug in auth module"

# Send with urgency
aish terma bob --urgent "Production issue needs attention"
```

#### Broadcast Messages
```bash
# Send to all terminals
aish terma broadcast "Deploying update in 5 minutes"

# Send to terminals by purpose
aish terma @frontend "UI build complete"
aish terma @backend "API endpoints ready for testing"
```

### 3. Message Management

#### Inbox System
aish uses a three-tier inbox system:

1. **Prompt Queue** (High Priority)
   - Urgent messages requiring immediate attention
   - Shown immediately in terminal

2. **New Queue** (Standard)
   - Regular messages awaiting reading
   - Notification shown on arrival

3. **Keep Queue** (Archive)
   - Messages marked for retention
   - Accessed via inbox commands

#### Inbox Commands
```bash
# Check for new messages
aish inbox

# List all messages
aish inbox list

# Read specific message
aish inbox read 1

# Mark message as kept
aish inbox keep 2

# Clear read messages
aish inbox clear

# Show kept messages
aish inbox kept
```

### 4. Advanced Features

#### Command Chaining
```bash
# Chain multiple AI queries
aish rhetor "optimize this query" | aish codex "implement in Python"

# Multi-step analysis
git diff | aish codex "review changes" | aish metis "suggest tests"
```

#### Forwarding Between AIs
```bash
# Forward conversation context
aish forward codex engram "Remember this code pattern"

# Team discussions
aish team "What's the best approach for caching?"
```

#### Shell Integration
```bash
# Execute suggested commands (with confirmation)
aish hermes "command to check memory usage" --execute

# Save command history
aish history save "debugging session"

# Replay command sequence
aish history replay "debugging session"
```

## Terma Integration

### Terminal Features

When using aish within Terma terminals, you get:

1. **Rich Rendering**
   - Syntax highlighting for code
   - Markdown formatting for AI responses
   - Inline images and diagrams

2. **Session Persistence**
   - Commands and context preserved across reconnections
   - Automatic session recovery

3. **LLM Assistance**
   - Context-aware command suggestions
   - Error explanation and debugging help
   - Command completion

### Terma-Specific Commands

```bash
# Get terminal info
aish terma info

# Set terminal purpose
aish terma purpose "frontend development"

# Enable/disable features
aish terma llm on
aish terma markdown on
aish terma theme dark
```

## Workflows and Examples

### Development Workflow

```bash
# 1. Start development session
aish terma purpose "feature/auth-update"

# 2. Get AI assistance with planning
aish prometheus "Plan implementation for OAuth2 integration"

# 3. Generate code scaffolding
aish codex "Generate OAuth2 middleware for FastAPI" > oauth_middleware.py

# 4. Run tests with AI analysis
pytest tests/auth/ | aish metis "Analyze test failures"

# 5. Notify team
aish terma broadcast "Auth feature ready for review"
```

### Debugging Workflow

```bash
# 1. Analyze error logs
tail -f app.log | aish apollo "Monitor for anomalies"

# 2. Get debugging suggestions
aish codex "Debug strategy for race condition in async code"

# 3. Search knowledge base
aish engram "Find previous race condition fixes"

# 4. Collaborate with team
aish terma @backend "Found race condition in event handler"
```

### Documentation Workflow

```bash
# 1. Generate documentation
aish codex "Document this API endpoint" < api/endpoint.py

# 2. Improve writing
aish rhetor "Make this documentation clearer" < README.md

# 3. Create examples
aish codex "Generate usage examples for this library"

# 4. Review with team
aish team "Review API documentation approach"
```

## Configuration

### Environment Variables

```bash
# Core settings
export AISH_DEFAULT_AI="rhetor"          # Default AI for commands
export AISH_HISTORY_SIZE=1000            # Command history size
export AISH_TIMEOUT=30                   # AI response timeout

# Terminal settings
export TERMA_USER="alice"                # Your terminal username
export TERMA_PURPOSE="development"       # Default terminal purpose
export TERMA_THEME="dark"               # Terminal theme

# AI settings
export AISH_AI_TEMPERATURE=0.7          # AI creativity level
export AISH_AI_MAX_TOKENS=2000         # Maximum response length
```

### Configuration File

Create `~/.aishrc` for persistent settings:

```bash
# AI aliases
alias numa="aish numa"
alias ask="aish rhetor"

# Common workflows
alias review="git diff | aish codex 'Review these changes'"
alias explain="aish codex 'Explain this error:'"

# Team shortcuts
alias team-frontend="aish terma @frontend"
alias team-backend="aish terma @backend"
```

## Tips and Best Practices

### 1. Effective AI Queries

**DO:**
- Be specific about what you need
- Provide context when relevant
- Use appropriate AI for the task

**DON'T:**
- Send overly broad queries
- Forget to specify language/framework
- Use wrong AI specialist

### 2. Terminal Communication

**DO:**
- Set meaningful terminal purposes
- Use broadcast sparingly
- Check inbox regularly

**DON'T:**
- Spam broadcast messages
- Ignore urgent messages
- Forget to clear old messages

### 3. Performance Optimization

- Use piping for large inputs
- Cache frequent AI responses
- Batch related queries
- Use appropriate response lengths

### 4. Security Considerations

- Don't send sensitive data to AI
- Be careful with `--execute` flag
- Review generated code before use
- Use local models for sensitive work

## Troubleshooting

### Common Issues

#### AI Not Responding
```bash
# Check AI status
aish status

# Test specific AI
aish ping hermes

# Restart AI service
aish restart codex
```

#### Terminal Not Found
```bash
# Verify terminal registration
aish terma list

# Re-register terminal
aish terma register

# Check Terma service
tekton-status | grep Terma
```

#### Message Delivery Issues
```bash
# Check message queue
aish inbox debug

# Clear stuck messages
aish inbox clear --force

# Reset inbox
aish inbox reset
```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Enable debug mode
export AISH_DEBUG=1

# Run command with debug
aish -v rhetor "test message"

# Check logs
tail -f ~/.aish/debug.log
```

## Advanced Topics

### Custom AI Workflows

Create custom command chains:

```bash
#!/bin/bash
# review.sh - AI-powered code review

# Get changes
CHANGES=$(git diff --staged)

# Analyze with multiple AIs
echo "$CHANGES" | aish codex "Review for bugs" > review_bugs.md
echo "$CHANGES" | aish metis "Suggest tests" > review_tests.md
echo "$CHANGES" | aish rhetor "Improve comments" > review_docs.md

# Summarize
cat review_*.md | aish sophia "Summarize review findings"
```

### Terminal Automation

Automate terminal interactions:

```python
#!/usr/bin/env python3
# monitor.py - Automated monitoring with alerts

import subprocess
import time

def check_services():
    result = subprocess.run(
        ["aish", "hermes", "Check critical services"],
        capture_output=True,
        text=True
    )
    
    if "down" in result.stdout.lower():
        subprocess.run([
            "aish", "terma", "@ops",
            "--urgent", "Service down detected!"
        ])

while True:
    check_services()
    time.sleep(300)  # Check every 5 minutes
```

### Integration with Other Tools

```bash
# Git hooks
echo 'aish codex "Review commit" < $1' > .git/hooks/commit-msg

# IDE integration
# Add to VS Code tasks.json
{
    "label": "AI Review",
    "type": "shell",
    "command": "aish codex 'Review current file' < ${file}"
}

# CI/CD integration
# Add to GitHub Actions
- name: AI Code Review
  run: |
    git diff origin/main | aish codex "Review changes"
```

## Quick Reference

### Essential Commands

| Command | Description |
|---------|-------------|
| `aish <ai> "<message>"` | Send message to AI |
| `aish terma list` | List active terminals |
| `aish terma <user> "<msg>"` | Send to user |
| `aish inbox` | Check messages |
| `aish help` | Show help |
| `aish status` | System status |

### AI Specialist Quick Guide

| Specialist | Best For |
|------------|----------|
| hermes | System status, service health |
| codex | Code generation, analysis |
| rhetor | Writing, prompts, communication |
| engram | Search, memory, knowledge |
| metis | Testing, quality assurance |
| apollo | Monitoring, metrics, logs |

### Keyboard Shortcuts (in Terma)

| Shortcut | Action |
|----------|--------|
| `Ctrl+T` | New terminal tab |
| `Ctrl+D` | Close terminal |
| `Ctrl+L` | Clear screen |
| `Ctrl+R` | Search history |
| `Ctrl+A` | Beginning of line |
| `Ctrl+E` | End of line |

## Related Documentation

- [aish README](/shared/aish/README.md)
- [Terma README](/Terma/README.md)
- [AI Specialists Guide](/MetaData/TektonDocumentation/Guides/AISpecialistsGuide.md)
- [Terminal Implementation](/MetaData/Implementation/TermaImplementation.md)