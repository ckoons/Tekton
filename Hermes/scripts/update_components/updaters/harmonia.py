"""
Updater for Harmonia component.
"""

from pathlib import Path
from typing import List, Optional

from ..utils.file import read_file, write_file, file_exists
from ..utils.module import find_suitable_files
from ..utils.code import (
    is_already_updated, 
    replace_logging_imports, 
    replace_logger_initialization
)
from ..templates.logging_imports import get_readme_content


def update_harmonia(harmonia_path: Path, logger) -> bool:
    """
    Update Harmonia to use centralized services.
    
    Args:
        harmonia_path: Path to Harmonia directory
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("Updating Harmonia...")
    
    # Check if Harmonia exists
    if not harmonia_path.exists():
        logger.warn(f"Harmonia not found at {harmonia_path}")
        return False
    
    # Find suitable files to update
    suitable_files = find_suitable_files(harmonia_path, [
        harmonia_path / "harmonia" / "core" / "engine.py",
        harmonia_path / "harmonia" / "core" / "workflow.py",
        harmonia_path / "harmonia" / "core" / "state.py"
    ])
    
    updated_any = False
    
    for file_path in suitable_files:
        # Read the file
        content = read_file(file_path)
        if not content:
            logger.error(f"Failed to read {file_path}")
            continue
        
        # Check if already updated
        if is_already_updated(content):
            logger.info(f"{file_path.name} already updated to use Centralized Logging")
            updated_any = True
            continue
        
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
                    # Get module name based on file path
                    module_name = f'"harmonia.{file_path.stem}"'
                    content = replace_logger_initialization(content, module_name)
                    break
        
        # Write the updated file
        if not write_file(file_path, content):
            logger.error(f"Failed to write updated content to {file_path}")
            continue
        
        logger.info(f"Successfully updated {file_path.name} to use Centralized Logging")
        updated_any = True
    
    if updated_any:
        # Create a README file to explain the changes
        readme_path = harmonia_path / "LOGGING_UPDATE.md"
        readme_content = get_readme_content("Harmonia")
        
        if not write_file(readme_path, readme_content):
            logger.error(f"Failed to write README to {readme_path}")
            # Continue anyway, this is not critical
        else:
            logger.info("Created LOGGING_UPDATE.md for Harmonia with information about the changes")
    
    return updated_any