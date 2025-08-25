# Tekton Logging System

## Overview

The Tekton logging system provides a unified, consistent approach to logging across all components of the Tekton Multi-CI Engineering Platform. It ensures that all components produce logs in a standardized format, making debugging and monitoring easier across the distributed system.

## Architecture

### Core Components

1. **Centralized Logging Setup** (`shared/utils/logging_setup.py`)
   - Provides `setup_component_logging()` function used by all components
   - Handles environment variable configuration
   - Suppresses noisy external library logs
   - Returns configured logger instances

2. **Log Format Definitions** (`shared/utils/tekton_log_formats.py`)
   - Defines standard log formats available to all components
   - Supports multiple format types: compact, standard, detailed, debug, minimal, json
   - Allows component-specific format overrides

3. **Enhanced Launcher** (`scripts/enhanced_tekton_launcher.py`)
   - Captures all component output (stdout/stderr)
   - Writes logs to `$TEKTON_ROOT/.tekton/logs/<component>.log`
   - Handles both Python formatted logs and bash script output
   - Strips ANSI color codes for clean log files
   - Prevents double timestamps for Python logs

4. **Environment Manager** (`shared/utils/env_manager.py`)
   - Loads logging configuration from `.env.tekton`
   - Manages component-specific and global log settings
   - Provides helper functions for environment variables

## Configuration

### Environment Variables

Configuration is managed through environment variables, typically set in `.env.tekton`:

```bash
# Global settings
TEKTON_LOG_LEVEL=INFO                    # Default log level for all components
TEKTON_LOG_FORMAT=standard               # Default log format

# Component-specific overrides
APOLLO_LOG_FORMAT=detailed               # Apollo uses detailed format
HERMES_LOG_FORMAT=debug                  # Hermes uses debug format
ENGRAM_LOG_FORMAT=standard              # Engram uses standard format
# ... etc for each component
```

### Available Log Levels

Standard Python logging levels are supported:
- `TRACE` - Most detailed debugging information
- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages (default)
- `WARN` - Warning messages
- `ERROR` - Error messages
- `FATAL` - Critical error messages
- `OFF` - Disable logging

### Available Log Formats

Six predefined formats are available:

1. **compact**: `%(asctime)s %(message)s`
   - Minimal format for simple messages

2. **standard**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
   - Default format for most components

3. **detailed**: `%(asctime)s [%(name)s] [%(levelname)s] %(module)s: %(message)s`
   - Includes module information, used by Apollo

4. **debug**: `%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s`
   - Includes file location for debugging

5. **minimal**: `%(levelname)s: %(message)s`
   - Very clean output without timestamps

6. **json**: Structured JSON format for log aggregation systems

## Log Storage

### Directory Structure

All logs are stored in:
```
$TEKTON_ROOT/.tekton/logs/
├── apollo.log
├── hermes.log
├── engram.log
├── rhetor.log
├── ... (one file per component)
```

### Log File Format

Each log file contains:
- Header with launch information (timestamp, command, directory, port)
- Component output with appropriate formatting
- Python logs: Preserved with original timestamps
- Bash/stdout output: Prefixed with `[STDOUT]` or `[STDERR]` and timestamp

Example log file:
```
============================================================
Component: hermes
Started: 2025-06-05 10:15:23
Command: bash run_hermes.sh
Directory: /Users/user/Tekton/Hermes
Port: 8001
============================================================

2025-06-05 10:15:24 - hermes - INFO - Initialized hermes logging at level INFO
2025-06-05 10:15:25 [STDOUT] Starting Hermes service...
2025-06-05 10:15:26 - hermes.api - INFO - Server started on port 8001
```

## Implementation Guide

### For New Components

1. Import the logging setup:
```python
from shared.utils.logging_setup import setup_component_logging
```

2. Initialize logging early in your component:
```python
# In __main__.py or main entry point
logger = setup_component_logging("mycomponent")
logger.info("Component starting...")
```

3. Use child loggers for modules:
```python
# In submodules
logger = logging.getLogger("mycomponent.submodule")
```

### For Existing Components

Most Tekton components already use `setup_component_logging`. If you find one that doesn't:

1. Replace custom logging setup with:
```python
from shared.utils.logging_setup import setup_component_logging
logger = setup_component_logging("component_name")
```

2. Remove any `logging.basicConfig()` calls
3. Update logger names to use the component name

## How Logs Are Processed

### Launch Time

1. Launcher creates log directory if needed
2. Opens log file for component
3. Starts component process with stdout/stderr captured
4. Spawns LogReader threads for each stream

### Runtime

1. **LogReader threads** continuously read from stdout/stderr
2. **ANSI stripping**: Color codes are removed for clean logs
3. **Timestamp detection**: 
   - Python logs with timestamps are preserved as-is
   - Other output gets timestamp + [STDOUT/STDERR] prefix
4. **Real-time writing**: Logs are flushed immediately
5. **Error highlighting**: ERROR lines are also printed to console

### Shutdown

1. LogReader threads stop when process ends
2. Log files remain open for inspection
3. New launches append to existing log files

## Best Practices

### For Component Developers

1. **Use the standard setup**: Always use `setup_component_logging()`
2. **Log at appropriate levels**: 
   - DEBUG for detailed debugging info
   - INFO for general flow and state changes
   - WARNING for recoverable issues
   - ERROR for failures
3. **Use child loggers**: For modules within a component
4. **Avoid print()**: Use logger instead for consistent formatting
5. **Include context**: Log meaningful information, not just "Started"

### For System Administrators

1. **Monitor log sizes**: Logs are appended to, not rotated automatically
2. **Use --save-logs**: Pass this flag to launcher to preserve logs between runs
3. **Check log formats**: Adjust TEKTON_LOG_FORMAT for your needs
4. **Debug issues**: Use debug format for troubleshooting specific components

## Troubleshooting

### Common Issues

1. **Double timestamps in logs**
   - Cause: Old launcher version or custom logging
   - Fix: Update to latest launcher, use setup_component_logging

2. **Missing logs**
   - Cause: Component crashed before logging initialized
   - Fix: Check component directory for error output

3. **Logs not updating**
   - Cause: Component buffering output
   - Fix: Ensure stdout is unbuffered (Python: use -u flag)

4. **Wrong format**
   - Cause: Environment variable not loaded
   - Fix: Check .env.tekton is being loaded properly

### Debug Mode

Enable debug logging for all components:
```bash
# In .env.tekton
TEKTON_LOG_LEVEL=DEBUG
TEKTON_LOG_FORMAT=debug
```

Or for specific component:
```bash
HERMES_LOG_LEVEL=DEBUG
HERMES_LOG_FORMAT=debug
```

## Examples

### Basic Component Logging

```python
# mycomponent/__main__.py
from shared.utils.logging_setup import setup_component_logging

def main():
    logger = setup_component_logging("mycomponent")
    logger.info("MyComponent starting...")
    
    try:
        # Component logic
        logger.debug("Processing request...")
        result = process_data()
        logger.info(f"Processed {len(result)} items")
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
```

### Module-Specific Logging

```python
# mycomponent/processor.py
import logging

logger = logging.getLogger("mycomponent.processor")

def process_data():
    logger.debug("Starting data processing")
    # ... processing logic
    logger.info("Data processing complete")
```

### Custom Format for Special Cases

```python
# For a component that needs custom formatting
logger = setup_component_logging(
    "special_component",
    format_string="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
```

## Integration with Other Systems

### Log Aggregation

The JSON format is designed for log aggregation systems:
```bash
# In .env.tekton
TEKTON_LOG_FORMAT=json
```

This produces structured logs that can be easily parsed by tools like:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Splunk
- CloudWatch Logs
- Datadog

### Monitoring

Log files can be monitored with standard tools:
```bash
# Watch a component's logs
tail -f $TEKTON_ROOT/.tekton/logs/hermes.log

# Monitor all ERROR messages
tail -f $TEKTON_ROOT/.tekton/logs/*.log | grep ERROR

# Count warnings per component
grep WARNING $TEKTON_ROOT/.tekton/logs/*.log | cut -d: -f1 | sort | uniq -c
```

## Future Enhancements

Planned improvements to the logging system:

1. **Log Rotation**: Automatic rotation based on size/age
2. **Centralized Log Server**: Optional forwarding to central log aggregator
3. **Performance Metrics**: Include performance data in logs
4. **Structured Logging**: Enhanced structured logging support
5. **Log Levels via API**: Dynamic log level adjustment without restart

## Summary

The Tekton logging system provides:
- **Consistency**: All components use the same logging setup
- **Flexibility**: Multiple formats and component-specific overrides
- **Clarity**: Clean, readable logs without ANSI codes
- **Debugging**: File locations and detailed formats when needed
- **Integration**: JSON format for log aggregation systems

By following these guidelines and using the provided utilities, all Tekton components maintain consistent, useful logs that aid in development, debugging, and operations.