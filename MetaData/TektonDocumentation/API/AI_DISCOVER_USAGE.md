# ai-discover Command Reference

## Command Structure
```bash
ai-discover [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

## Global Options
- `--json` - Output in JSON format (must come BEFORE the command)
- `--verbose` or `-v` - Verbose output

## Commands

### list - List available AIs
```bash
# List all AIs (human readable)
ai-discover list

# List all AIs (JSON format)
ai-discover --json list

# Filter by role
ai-discover --json list --role planning

# Filter by capability
ai-discover --json list --capability code-analysis
```

### info - Get AI information
```bash
# Get info for specific AI
ai-discover info apollo-ai

# JSON format
ai-discover --json info apollo-ai
```

### test - Test AI connections
```bash
# Test all AIs
ai-discover test

# Test specific AI
ai-discover test apollo-ai

# JSON format
ai-discover --json test
```

### schema - Get interaction schema
```bash
# Get schema for an AI
ai-discover schema rhetor-ai

# JSON format
ai-discover --json schema rhetor-ai
```

### manifest - Get platform manifest
```bash
# Get platform discovery manifest
ai-discover manifest

# JSON format
ai-discover --json manifest
```

### best - Find best AI for role
```bash
# Find best AI for planning
ai-discover best planning

# JSON format
ai-discover --json best planning
```

## Common Usage Patterns

### For aish integration
```python
# Get all AIs with connection info
cmd = ["ai-discover", "--json", "list"]

# Parse output to get:
# - id: "apollo-ai"
# - connection: {"host": "localhost", "port": 45007}
```

### From command line
```bash
# Quick check what's available
ai-discover list

# Detailed info with socket details
ai-discover --json info apollo-ai | jq '.connection'

# Test connectivity
ai-discover test apollo-ai
```

## Important Notes
1. The `--json` flag must come BEFORE the command
2. Commands are subcommands, not flags (use `list` not `--list`)
3. The tool works from any directory with proper PATH setup
4. Output includes full connection details for socket communication