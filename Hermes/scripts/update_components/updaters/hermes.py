"""
Updater for Hermes's internal components.
"""

from pathlib import Path
from typing import List, Optional

from ..utils.file import read_file, write_file, file_exists
from ..utils.module import find_suitable_files
from ..utils.code import extract_logger_name


def update_hermes_itself(hermes_path: Path, logger) -> bool:
    """
    Update Hermes's internal files to use the Centralized Logging System.
    
    Args:
        hermes_path: Path to Hermes directory
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("Updating Hermes's internal files...")
    
    # Files to update
    files_to_update = find_suitable_files(hermes_path, [
        hermes_path / "hermes" / "core" / "vector_engine.py",
        hermes_path / "hermes" / "core" / "message_bus.py",
        hermes_path / "hermes" / "core" / "service_discovery.py",
        hermes_path / "hermes" / "core" / "registration.py"
    ])
    
    updated_any = False
    
    for file_path in files_to_update:
        # Read the file
        content = read_file(file_path)
        if not content:
            logger.error(f"Failed to read {file_path}")
            continue
        
        # Skip if already using the centralized logging
        if "from hermes.utils.logging_helper import setup_logging" in content:
            logger.info(f"{file_path.name} already using the Centralized Logging System")
            continue
        
        # Check if using standard logging
        if "import logging" in content and "logger = logging.getLogger" in content:
            # Extract module name
            if 'logger = logging.getLogger("' in content:
                module_name = content.split('logger = logging.getLogger("')[1].split('"')[0]
                module_name_str = f'"{module_name}"'
            elif "logger = logging.getLogger('" in content:
                module_name = content.split("logger = logging.getLogger('")[1].split("'")[0]
                module_name_str = f"'{module_name}'"
            elif "logger = logging.getLogger(__name__" in content:
                module_name = file_path.stem
                module_name_str = "__name__"
            else:
                module_name = file_path.stem
                module_name_str = f'"hermes.core.{module_name}"'
            
            # Replace imports
            content = content.replace(
                "import logging",
                "from hermes.core.logging import get_logger"
            )
            
            # Replace logger initialization
            logger_pattern = f"logger = logging.getLogger({module_name_str})"
            if logger_pattern in content:
                content = content.replace(
                    logger_pattern,
                    f"logger = get_logger({module_name_str})"
                )
            else:
                # Try to find the logger initialization pattern
                import re
                pattern = r'logger = logging\.getLogger\([^)]+\)'
                match = re.search(pattern, content)
                if match:
                    original = match.group(0)
                    content = content.replace(
                        original,
                        f"logger = get_logger({module_name_str})"
                    )
            
            # Write the updated file
            if not write_file(file_path, content):
                logger.error(f"Failed to write updated content to {file_path}")
                continue
            
            logger.info(f"Updated {file_path.name} to use the Centralized Logging System")
            updated_any = True
    
    return updated_any