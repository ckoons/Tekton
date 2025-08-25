# aish User Guide

User guide for humans working with aish (CI Shell) in the Tekton platform.

## Overview

aish is your command-line interface to the Tekton Multi-CI Engineering Platform. With the new unified CI system, it provides a single interface to communicate with:
- **Greek Chorus CIs**: numa, apollo, athena, and other CI specialists
- **Terminals**: Other human terminals like alice, bob, sandi
- **Project CIs**: Project-specific computational instances
- All through the same simple command syntax!

## Quick Start

```bash
# Send a message to any CI (Greek Chorus, Terminal, or Project)
aish numa "Hello, how can you help me today?"

# List all available CIs with unified view
aish list

# List specific CI types
aish list type terminal
aish list type greek
aish list type project

# Get detailed JSON output
aish list json

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
# This is useful for monitoring project-specific CI activity
```

### Removing Forwards

```bash
# Stop forwarding MyWebApp CI
aish project unforward MyWebApp
```

## Unified CI Communication (New!)

With the unified CI system, you can communicate with any type of CI using the same syntax:

### Direct Messaging

```bash
# Greek Chorus CIs (CI specialists)
aish athena "Explain the observer pattern"
aish numa "Review this code for potential issues"
aish apollo "What patterns do you see in these logs?"

# Terminal Communication (other humans)
aish alice "Ready for code review?"
aish bob "Can you help with the database issue?"

# Project CIs (project-specific instances)
aish mywebapp "What's the deployment status?"
aish datapipeline "Show me the latest metrics"
```

All use the same simple syntax - the system automatically routes messages based on the CI's configuration!

### Team Chat

Broadcast messages to all CIs simultaneously:

```bash
aish team-chat "We need ideas for improving test coverage"
```

## Message Forwarding

### Forward CI Messages to Humans

You can forward messages from specific CIs to human terminals:

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
- You're collaborating with an CI on a specific task
- You need to audit CI interactions

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

Keep your CI (like Claude) active to prevent timeouts:

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
- CI training docs: `$TEKTON_ROOT/MetaData/TektonDocumentation/AITraining/`
- Developer docs: `$TEKTON_ROOT/MetaData/TektonDocumentation/Developer_Reference/`