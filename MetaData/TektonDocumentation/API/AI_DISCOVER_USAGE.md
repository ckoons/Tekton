# ai-discover Tool Usage Guide

## Overview

The `ai-discover` tool has been significantly enhanced as part of the Unified AI Interface. It now provides comprehensive AI discovery, monitoring, testing, and management capabilities.

## New Features (Enhanced Version)

### Real-time Monitoring
```bash
# Watch AI status in real-time with live updates
ai-discover watch
```

### Streaming Support
```bash
# Test streaming capabilities
ai-discover stream apollo-ai "Tell me a story"
```

### Performance Benchmarking
```bash
# Benchmark AI response times
ai-discover benchmark --iterations 10

# Benchmark specific AIs
ai-discover benchmark apollo-ai athena-ai --iterations 5
```

### Intelligent Routing
```bash
# Test routing engine
ai-discover route "analyze this code"

# Test with execution
ai-discover route "analyze this code" --execute

# Test with preferred AI
ai-discover route "document this" --preferred hermes-ai --capabilities documentation
```

### Enhanced Discovery
```bash
# List with filters
ai-discover list --role planning --status healthy
ai-discover list --capability code_analysis --min-success-rate 0.9

# JSON output for scripting
ai-discover list --json | jq '.ais[] | select(.status == "healthy")'
```

### Statistics
```bash
# View registry statistics
ai-discover stats

# JSON format
ai-discover stats --json
```

## Legacy Commands (Still Supported)

The following commands still work but show deprecation notices:

- `ai-discover info <ai_id>` → Use `list --json` with filtering
- `ai-discover manifest` → Use `stats`
- `ai-discover schema <ai_id>` → Schemas are now standardized
- `ai-discover best <role>` → Use `route`

## Common Use Cases

### 1. Daily Operations
```bash
# Check AI health
ai-discover list --status healthy

# Monitor in real-time
ai-discover watch
```

### 2. Debugging
```bash
# Test specific AI
ai-discover test apollo-ai -v

# Test all AIs
ai-discover test

# Check streaming
ai-discover stream apollo-ai "Hello"
```

### 3. Performance Analysis
```bash
# Benchmark all healthy AIs
ai-discover benchmark

# Compare specific AIs
ai-discover benchmark apollo-ai athena-ai minerva-ai
```

### 4. Integration Testing
```bash
# Test routing decisions
ai-discover route "analyze code" --capabilities code_analysis

# Verify AI is reachable
ai-discover test apollo-ai --json
```

## Output Formats

### Rich Format (Default)
Beautiful tables and live updates when `rich` library is installed:
```bash
pip install rich
ai-discover list
```

### Simple Format
Plain text output:
```bash
ai-discover list --simple
```

### JSON Format
Machine-readable output:
```bash
ai-discover list --json
ai-discover test --json
ai-discover benchmark --json
```

## Environment Variables

- `TEKTON_ROOT` - Path to Tekton installation (auto-detected)

## Advanced Usage

### Scripting
```bash
# Get all healthy AIs as JSON array
healthy_ais=$(ai-discover list --status healthy --json | jq -r '.ais[].id')

# Test each healthy AI
for ai in $healthy_ais; do
    ai-discover test "$ai" --json > "test_${ai}.json"
done
```

### Monitoring Script
```python
import subprocess
import json
import time

while True:
    result = subprocess.run(
        ['ai-discover', 'stats', '--json'],
        capture_output=True,
        text=True
    )
    stats = json.loads(result.stdout)
    print(f"Healthy: {stats['status_breakdown']['healthy']}")
    time.sleep(60)
```

## Migration from Old Version

If you have scripts using the old ai-discover:

```bash
# Old way
ai-discover list | grep apollo
ai-discover info apollo-ai

# New way
ai-discover list --json | jq '.ais[] | select(.id == "apollo-ai")'
```

## Troubleshooting

### No AIs Found
```bash
# Check if registry is populated
ls -la ~/.tekton/ai_registry/

# Run migration if needed
python3 $TEKTON_ROOT/shared/ai/migrate_registry.py
```

### Import Errors
```bash
# Ensure TEKTON_ROOT is set
export TEKTON_ROOT=/path/to/Tekton

# Or run from Tekton directory
cd $TEKTON_ROOT && scripts/ai-discover list
```

## See Also

- [Unified AI Interface Architecture](../Architecture/UnifiedAIInterface.md)
- [Socket Client API](../../../shared/ai/socket_client.py)
- [Unified Registry API](../../../shared/ai/unified_registry.py)