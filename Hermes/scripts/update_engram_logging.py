#!/usr/bin/env python3
"""
Update Engram Logging - Converts Engram to use the Centralized Logging System.

This script updates the Engram memory module to use the Centralized Logging System
instead of the standard Python logging.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hermes.utils.logging_helper import setup_logging


def main():
    """Main function to parse arguments and run the update."""
    parser = argparse.ArgumentParser(description="Update Engram to use Centralized Logging")
    
    parser.add_argument(
        "--engram-path",
        type=str,
        default=None,
        help="Path to Engram directory (defaults to ../Engram)"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging("hermes.scripts.update_engram_logging")
    
    # Determine Engram path
    if args.engram_path:
        engram_path = Path(args.engram_path)
    else:
        engram_path = Path(__file__).parent.parent.parent / "Engram"
    
    if not engram_path.exists():
        logger.error(f"Engram path not found: {engram_path}")
        return False
    
    # Memory module path
    memory_py_path = engram_path / "engram" / "core" / "memory.py"
    
    if not memory_py_path.exists():
        logger.error(f"Memory module not found: {memory_py_path}")
        return False
    
    # Read the memory.py file
    with open(memory_py_path, "r") as f:
        content = f.read()
    
    # Check if already updated
    if "from hermes.utils.logging_helper import setup_logging" in content:
        logger.info("Memory module already updated to use Centralized Logging")
        return True
    
    # Replace standard logging initialization with centralized logging
    old_logging_imports = """import logging
import os
import time"""
    
    new_logging_imports = """import os
import time
# Import Centralized Logging System
try:
    from hermes.utils.logging_helper import setup_logging
    USE_CENTRALIZED_LOGGING = True
except ImportError:
    # Fall back to standard logging if Hermes is not available
    import logging
    USE_CENTRALIZED_LOGGING = False"""
    
    content = content.replace(old_logging_imports, new_logging_imports)
    
    # Replace logging initialization
    old_logging_init = """# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.memory")"""
    
    new_logging_init = """# Configure logging
if USE_CENTRALIZED_LOGGING:
    # Use Centralized Logging System
    logger = setup_logging("engram.memory")
else:
    # Fall back to standard logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("engram.memory")"""
    
    content = content.replace(old_logging_init, new_logging_init)
    
    # Write the updated file
    with open(memory_py_path, "w") as f:
        f.write(content)
    
    logger.info(f"Successfully updated Engram memory module to use Centralized Logging")
    
    # Create a README file to explain the changes
    readme_path = engram_path / "LOGGING_UPDATE.md"
    
    with open(readme_path, "w") as f:
        f.write("""# Centralized Logging Update

Engram has been updated to use the Centralized Logging System (CLS) from Hermes. This provides the following benefits:

1. **Structured Logging**: All logs follow a standardized schema
2. **Schema Versioning**: Log schema evolution is tracked for backward compatibility
3. **Effective Timestamps**: Distinguish between when an event occurred vs. when it was logged
4. **Log Levels**: Standardized log levels (FATAL, ERROR, WARN, INFO, NORMAL, DEBUG, TRACE)
5. **Contextual Information**: Rich context for all log entries
6. **Correlation**: Track related log entries across components
7. **Storage**: Logs are stored centrally for easier debugging and analysis

## Compatibility

The update is backward compatible - if Hermes is not available, Engram will fall back to using standard Python logging.

## How to Use

No changes are needed to use the basic logging functionality. For advanced features:

```python
# Access Hermes logging features if available
if USE_CENTRALIZED_LOGGING:
    # Log with context
    logger.info("User action", context={"user_id": "user123"})
    
    # Create correlated logger
    op_logger = logger.with_correlation("operation-123")
    op_logger.info("Operation started")
    op_logger.info("Operation completed")
```

## Next Steps

More Engram modules will be updated to use the Centralized Logging System in future updates.
""")
    
    logger.normal("Created LOGGING_UPDATE.md with information about the changes")
    
    return True


if __name__ == "__main__":
    main()