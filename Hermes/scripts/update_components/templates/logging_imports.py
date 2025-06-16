"""
Templates for updating logging imports.
"""

# Template for the centralized logging imports
CENTRALIZED_LOGGING_IMPORTS = """# Import Centralized Logging System
try:
    from hermes.utils.logging_helper import setup_logging
    USE_CENTRALIZED_LOGGING = True
except ImportError:
    # Fall back to standard logging if Hermes is not available
    import logging
    USE_CENTRALIZED_LOGGING = False
"""

# Template for the centralized logger initialization
CENTRALIZED_LOGGER_INIT = """if USE_CENTRALIZED_LOGGING:
    # Use Centralized Logging System
    logger = setup_logging({module_name})
else:
    # Fall back to standard logging
    logger = logging.getLogger({module_name})
"""

# Template for updating standard logging init
def get_logger_init_replacement(module_name: str) -> str:
    """
    Get the replacement template for logger initialization.
    
    Args:
        module_name: Name of the module for the logger
        
    Returns:
        Formatted template string
    """
    return CENTRALIZED_LOGGER_INIT.format(module_name=module_name)


# Template for README file explaining the changes
README_TEMPLATE = """# Centralized Logging Update

{component} has been updated to use the Centralized Logging System (CLS) from Hermes. This provides the following benefits:

1. **Structured Logging**: All logs follow a standardized schema
2. **Schema Versioning**: Log schema evolution is tracked for backward compatibility
3. **Effective Timestamps**: Distinguish between when an event occurred vs. when it was logged
4. **Log Levels**: Standardized log levels (FATAL, ERROR, WARN, INFO, NORMAL, DEBUG, TRACE)
5. **Contextual Information**: Rich context for all log entries
6. **Correlation**: Track related log entries across components
7. **Storage**: Logs are stored centrally for easier debugging and analysis

## Compatibility

The update is backward compatible - if Hermes is not available, {component} will fall back to using standard Python logging.

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

More {component} modules will be updated to use the Centralized Logging System in future updates.
"""

def get_readme_content(component_name: str) -> str:
    """
    Get the content for the README file explaining the changes.
    
    Args:
        component_name: Name of the component being updated
        
    Returns:
        Formatted README content
    """
    return README_TEMPLATE.format(component=component_name)