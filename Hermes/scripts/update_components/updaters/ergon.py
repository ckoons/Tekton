"""
Updater for Ergon component.
"""

from pathlib import Path
from typing import Optional

from ..utils.file import read_file, write_file
from ..utils.code import (
    is_already_updated, 
    replace_logging_imports, 
    replace_logger_initialization,
    extract_logger_name
)
from ..templates.logging_imports import get_readme_content


def update_ergon(ergon_path: Path, logger) -> bool:
    """
    Update Ergon to use centralized services.
    
    Args:
        ergon_path: Path to Ergon directory
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("Updating Ergon...")
    
    # Check if Ergon exists
    if not ergon_path.exists():
        logger.warn(f"Ergon not found at {ergon_path}")
        return False
    
    # Update main.py
    main_py_path = ergon_path / "ergon" / "cli" / "main.py"
    
    if not main_py_path.exists():
        logger.warn(f"Main module not found: {main_py_path}")
        # Try finding another suitable file
        app_py_path = ergon_path / "ergon" / "api" / "app.py"
        if app_py_path.exists():
            main_py_path = app_py_path
            logger.info(f"Using alternative file: {main_py_path}")
        else:
            logger.error("No suitable files found to update")
            return False
    
    # Read the file
    content = read_file(main_py_path)
    if not content:
        logger.error(f"Failed to read {main_py_path}")
        return False
    
    # Check if already updated
    if is_already_updated(content):
        logger.info("Ergon already updated to use Centralized Logging")
        return True
    
    # Find logging imports
    if "import logging" in content:
        # Replace standard logging with centralized logging
        content = replace_logging_imports(content)
        
        # Find logger initialization
        logger_init_patterns = [
            "logger = logging.getLogger",
            "logging.basicConfig"
        ]
        
        for pattern in logger_init_patterns:
            if pattern in content:
                content = replace_logger_initialization(content)
                break
    
    # Write the updated file
    if not write_file(main_py_path, content):
        logger.error(f"Failed to write updated content to {main_py_path}")
        return False
    
    logger.info(f"Successfully updated Ergon to use Centralized Logging")
    
    # Create a README file to explain the changes
    readme_path = ergon_path / "LOGGING_UPDATE.md"
    readme_content = get_readme_content("Ergon")
    
    if not write_file(readme_path, readme_content):
        logger.error(f"Failed to write README to {readme_path}")
        # Continue anyway, this is not critical
    else:
        logger.info("Created LOGGING_UPDATE.md for Ergon with information about the changes")
    
    return True