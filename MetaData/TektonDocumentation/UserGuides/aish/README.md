# aish User Guide

User guide for humans working with aish (AI Shell) in the Tekton platform.

## Overview

aish is your command-line interface to the Tekton Multi-AI Engineering Platform. It allows you to:
- Communicate with AI specialists
- Manage project CI (Computational Instance) routing
- Send messages between terminals
- Forward AI messages to human terminals

## Quick Start

```bash
# Send a message to an AI
aish numa "Hello, how can you help me today?"

# List available AIs
aish list

# Check your identity and environment
aish whoami

# See all commands
aish list commands
```

## Project Management (New!)

### Managing Project CIs

With the new project commands, you can manage how project-specific CIs communicate:

```bash
# List all Tekton managed projects
aish project list

# Example output:
# Tekton Managed Projects:
# ----------------------------------------------------------------------
# Project              CI                   Forward                       
# ----------------------------------------------------------------------
# Tekton               numa-ai              Cari (active)                 
# MyWebApp             numa-ai              none                          
# DataPipeline         apollo-ai            Casey (inactive)              
```

### Forwarding Project Messages

When working on a specific project, you can forward its CI messages to your terminal:

```bash
# Forward MyWebApp CI to your current terminal
aish project forward MyWebApp

# Messages from the project's CI will now appear in your terminal
# This is useful for monitoring project-specific AI activity
```

### Removing Forwards

```bash
# Stop forwarding MyWebApp CI
aish project unforward MyWebApp
```

## AI Communication

### Direct Messaging

Send messages directly to any AI specialist:

```bash
# Knowledge and research
aish athena "Explain the observer pattern"
aish noesis "What are the latest ML optimization techniques?"

# Planning and architecture
aish prometheus "Plan a microservices migration"
aish telos "Define success criteria for our API redesign"

# Development support
aish numa "Review this code for potential issues"
aish apollo "What patterns do you see in these logs?"
```

### Team Chat

Broadcast messages to all AIs simultaneously:

```bash
aish team-chat "We need ideas for improving test coverage"
```

## Message Forwarding

### Forward AI Messages to Humans

You can forward messages from specific AIs to human terminals:

```bash
# Forward Apollo's messages to Alice's terminal
aish forward apollo alice

# List active forwards
aish forward list

# Stop forwarding
aish unforward apollo
```

This is useful when:
- You want to monitor an AI's responses
- You're collaborating with an AI on a specific task
- You need to audit AI interactions

## Terminal Communication

### Send Messages Between Terminals

```bash
# Send to a specific terminal
aish terma send bob "Ready for code review"

# Send to terminals by purpose
aish terma send @testing "Tests are failing on main"

# Broadcast to all terminals
aish terma broadcast "Deploying to staging in 5 minutes"
```

### Manage Your Inbox

```bash
# Check your inbox
aish terma inbox

# Pop and read new messages
aish terma inbox new pop

# Move messages to keep folder
aish terma mv-to-keep 1,3,5

# Delete from keep folder
aish terma del-from-keep 2
```

## Productivity Features

### AutoPrompt

Keep your AI (like Claude) active to prevent timeouts:

```bash
# Start autoprompt (2-second intervals)
autoprompt start

# Stop autoprompt
autoprompt stop

# Check status
autoprompt status
```

### Session Recording

Record your terminal sessions for review:

```bash
# Start recording
aish review start

# Stop and save
aish review stop

# List recordings
aish review list
```

## Tips and Best Practices

1. **Use Descriptive Terminal Names**: When launching terminals, use meaningful names like "alice-backend-dev" or "bob-testing"

2. **Set Terminal Purpose**: Define what you're working on for better team coordination

3. **Check Forwards Regularly**: Use `aish forward list` to see what messages are being routed to your terminal

4. **Project-Specific Monitoring**: Use project forwards when actively working on a project to stay informed about CI activity

5. **Clean Up Forwards**: Remove forwards when you're done to avoid message clutter

## Environment Variables

aish respects these environment variables:
- `TEKTON_ROOT`: Root directory of your Tekton installation
- `TERMA_TERMINAL_NAME`: Your terminal's name (set by Terma)
- `TEKTON_DEBUG`: Enable debug output

## Troubleshooting

### Command Not Found
Make sure aish is in your PATH or use the full path to the aish executable.

### Cannot Forward Project
Project forwarding requires running in a named Terma terminal. Launch a terminal through Terma first.

### No Response from AI
Check that the Rhetor service is running and accessible.

## More Information

- Full command reference: `aish list commands`
- AI training docs: `$TEKTON_ROOT/MetaData/TektonDocumentation/AITraining/`
- Developer docs: `$TEKTON_ROOT/MetaData/TektonDocumentation/Developer_Reference/`