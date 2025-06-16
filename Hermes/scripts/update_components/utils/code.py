"""
Code analysis and modification utilities for component updates.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any


def is_already_updated(content: str) -> bool:
    """
    Check if code is already updated to use centralized logging.
    
    Args:
        content: File content to check
        
    Returns:
        True if already updated, False otherwise
    """
    return "from hermes.utils.logging_helper import setup_logging" in content


def find_import_section_end(content: str) -> int:
    """
    Find the end of the import section in a Python file.
    
    Args:
        content: File content to analyze
        
    Returns:
        Line index of the last import statement
    """
    lines = content.split("\n")
    import_section_end = 0
    
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            import_section_end = i
    
    return import_section_end


def replace_logging_imports(content: str) -> str:
    """
    Replace standard logging imports with centralized logging.
    
    Args:
        content: Original file content
        
    Returns:
        Updated file content
    """
    if "import logging\n" in content:
        return content.replace(
            "import logging\n",
            "# Import Centralized Logging System\n"
            "try:\n"
            "    from hermes.utils.logging_helper import setup_logging\n"
            "    USE_CENTRALIZED_LOGGING = True\n"
            "except ImportError:\n"
            "    # Fall back to standard logging if Hermes is not available\n"
            "    import logging\n"
            "    USE_CENTRALIZED_LOGGING = False\n"
        )
    else:
        # More complex case, add after imports
        import_section_end = find_import_section_end(content)
        
        if import_section_end > 0:
            lines = content.split("\n")
            lines.insert(import_section_end + 1, "")
            lines.insert(import_section_end + 2, "# Import Centralized Logging System")
            lines.insert(import_section_end + 3, "try:")
            lines.insert(import_section_end + 4, "    from hermes.utils.logging_helper import setup_logging")
            lines.insert(import_section_end + 5, "    USE_CENTRALIZED_LOGGING = True")
            lines.insert(import_section_end + 6, "except ImportError:")
            lines.insert(import_section_end + 7, "    # Fall back to standard logging if Hermes is not available")
            lines.insert(import_section_end + 8, "    import logging")
            lines.insert(import_section_end + 9, "    USE_CENTRALIZED_LOGGING = False")
            return "\n".join(lines)
        
        return content


def extract_logger_name(content: str) -> str:
    """
    Extract logger name from logging configuration.
    
    Args:
        content: File content to analyze
        
    Returns:
        Logger name as a string including quotes
    """
    # Try different patterns to extract logger name
    patterns = [
        r'logger = logging\.getLogger\("([^"]+)"\)',
        r"logger = logging\.getLogger\('([^']+)'\)",
        r"logger = logging\.getLogger\(__name__\)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            if pattern.endswith("__name__\\)"):
                return "__name__"
            else:
                return f'"{match.group(1)}"'
    
    # Default name based on filename
    return '"component"'


def replace_logger_initialization(content: str, module_name: Optional[str] = None) -> str:
    """
    Replace standard logger initialization with centralized logging.
    
    Args:
        content: Original file content
        module_name: Optional module name to use for the logger
        
    Returns:
        Updated file content with logger initialization replaced
    """
    # Determine module name if not provided
    if module_name is None:
        module_name = extract_logger_name(content)
    
    # Replace simple logger initialization
    if "logger = logging.getLogger" in content:
        # Extract the actual pattern with the module name
        regex = r'logger = logging\.getLogger\([^)]+\)'
        match = re.search(regex, content)
        if match:
            original = match.group(0)
            replacement = (
                f'if USE_CENTRALIZED_LOGGING:\n'
                f'    # Use Centralized Logging System\n'
                f'    logger = setup_logging({module_name})\n'
                f'else:\n'
                f'    # Fall back to standard logging\n'
                f'    logger = logging.getLogger({module_name})'
            )
            return content.replace(original, replacement)
    
    # Check for basicConfig + getLogger pattern
    if "logging.basicConfig" in content:
        # Look for patterns like logging.basicConfig(...) followed by logger = logging.getLogger(...)
        parts = content.split("logging.basicConfig")
        if len(parts) > 1 and "getLogger" in parts[1].split("\n\n")[0]:
            config_part = "logging.basicConfig" + parts[1].split("\n\n")[0]
            
            # Extract module name from getLogger if present
            config_module_name = module_name
            if "logger = logging.getLogger(" in config_part:
                config_module_name = extract_logger_name(config_part)
            
            replacement = (
                f'if USE_CENTRALIZED_LOGGING:\n'
                f'    # Use Centralized Logging System\n'
                f'    logger = setup_logging({config_module_name})\n'
                f'else:\n'
                f'    # Fall back to standard logging\n'
                f'    {config_part}'
            )
            
            return content.replace(config_part, replacement)
    
    return content