# aish Terminal User Guide

**Version**: 3.0.0  
**Last Updated**: July 2, 2025

## Overview

aish (AI Shell) provides seamless CI integration in your terminal through the Tekton platform. This guide covers how to use aish in Tekton-managed terminals.

## Getting Started

### Launching an aish Terminal

1. **Via Hephaestus UI**: Navigate to Terma component and click "Launch Terminal"
2. **Via Command Line**: Run the Terma launcher directly
3. **Via MCP API**: Use the `/tools/launch_terminal` endpoint

When launched, you'll see:
```
aish-proxy active (v3.0.0) - Usage: aish <ai-name> [message]
```

## Basic Commands

### Direct CI Interaction

```bash
# Ask Apollo a question
aish apollo "What is the chronology of C, Rust and Python?"

# Get help from Athena
aish athena "Explain the Tekton architecture"

# Consult Prometheus for planning
aish prometheus "Help me plan a new feature"
```

### Piping Data to CIs

```bash
# Send file contents to an AI
cat code.py | aish athena

# Process command output
ls -la | aish apollo "What files look important?"

# Chain CIs together
echo "Write a haiku about coding" | aish apollo | aish athena
```

### Team Communication

```bash
# Broadcast to all CIs
aish team-chat "Starting new development sprint"

# Multi-AI collaboration
aish team-chat "Need help debugging authentication issue"
```

### Listing Available CIs

```bash
# Show all available CI specialists
aish -l
```

## Available CI Specialists

| CI Name | Specialization | Best For |
|---------|---------------|----------|
| apollo | Prediction & Analysis | Code predictions, performance analysis |
| athena | Knowledge & Code Quality | Architecture review, best practices |
| rhetor | Prompt Engineering | LLM optimization, prompt design |
| prometheus | Planning & Strategy | Project planning, task breakdown |
| hermes | Service Coordination | System integration, messaging |
| ergon | Agent Management | Automated workflows, agent tasks |
| engram | Memory & Context | Historical queries, context retrieval |
| telos | Requirements | Requirements analysis, goal setting |
| sophia | Machine Learning | ML guidance, model selection |

## Advanced Usage

### Pipeline Examples

```bash
# Code review pipeline
cat mycode.py | aish athena | aish team-chat

# Documentation generation
echo "Document this function" | aish apollo > docs.md

# Multi-stage analysis
git diff | aish athena "Review changes" | aish prometheus "Suggest tests"
```

### Working with Files

```bash
# Analyze a file
aish athena < config.json

# Save CI response
aish apollo "Generate Python boilerplate" > template.py

# Append to existing file
aish prometheus "Next steps for project" >> TODO.md
```

### Environment Variables

You can customize aish behavior:

```bash
# Use different Rhetor endpoint
export RHETOR_ENDPOINT="http://custom-host:8003"

# Enable debug output
export AISH_DEBUG=1
```

## Terminal Features

### Shell Integration

aish works transparently with your shell:
- All non-AI commands pass through unchanged
- Shell aliases and functions work normally
- Command history includes both shell and CI commands

### Session Context

Each terminal maintains context:
- `TEKTON_TERMINAL_PURPOSE` - Set when launching with purpose
- `AISH_AI_PRIORITY` - Priority for CI requests
- Session history available via `aish-history`

## Troubleshooting

### Common Issues

**No CI Response**
- Check Rhetor is running: `curl http://localhost:8003/health`
- Verify network connectivity
- Try `aish -l` to list available CIs

**Command Not Found**
- Ensure you're in an aish-enabled terminal
- Check for "aish-proxy active" message on launch
- Verify PATH includes aish location

**Slow Responses**
- CI processing takes time for complex queries
- Check system resources
- Consider simpler, focused queries

### Debug Mode

Enable debug output for troubleshooting:
```bash
export AISH_DEBUG=1
aish apollo "test message"
```

## Best Practices

1. **Be Specific**: Clear, focused questions get better responses
2. **Use the Right AI**: Each specialist has strengths - match CI to task
3. **Pipeline for Complex Tasks**: Chain CIs for multi-step analysis
4. **Save Important Responses**: Redirect output to files for reference

## Examples by Use Case

### Code Development
```bash
# Generate boilerplate
aish apollo "Create FastAPI endpoint for user auth" > auth.py

# Review changes
git diff | aish athena "Security review"

# Debug assistance
cat error.log | aish ergon "Diagnose issue"
```

### Project Planning
```bash
# Break down features
aish prometheus "Plan chat feature implementation"

# Requirements analysis
cat requirements.txt | aish telos "Analyze dependencies"
```

### Learning & Documentation
```bash
# Explain code
cat complex_function.py | aish sophia "Explain this algorithm"

# Generate documentation
aish athena "Document REST API best practices" > API_GUIDE.md
```

## Integration with Tekton

aish terminals are fully integrated with Tekton:
- Automatic service discovery via Hermes
- Memory persistence through Engram
- Coordinated workflows with Harmonia
- Task tracking via Metis

## Getting Help

- **In Terminal**: `aish --help`
- **List CIs**: `aish -l`
- **Tekton Status**: `tekton-status`
- **Documentation**: This guide and component docs

Remember: aish enhances your terminal - it doesn't replace it. Use it as a powerful addition to your normal workflow!