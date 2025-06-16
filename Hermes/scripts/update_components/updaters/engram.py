"""
Updater for Engram component.
"""

from pathlib import Path
import subprocess
import sys
from typing import Optional

from ..utils.file import read_file, write_file
from ..utils.code import is_already_updated, replace_logging_imports, replace_logger_initialization
from ..templates.logging_imports import get_readme_content


def update_engram(engram_path: Path, logger) -> bool:
    """
    Update Engram to use centralized services.
    
    Args:
        engram_path: Path to Engram directory
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("Updating Engram...")
    
    # Check if Engram exists
    if not engram_path.exists():
        logger.warn(f"Engram not found at {engram_path}")
        return False
    
    # Run update_engram_logging.py if it exists
    try:
        update_script = Path(__file__).parent.parent.parent / "update_engram_logging.py"
        if update_script.exists():
            # Run as a subprocess
            result = subprocess.run(
                [sys.executable, str(update_script), "--engram-path", str(engram_path)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("Successfully updated Engram logging")
                logger.debug(result.stdout)
                return True
            else:
                logger.error(f"Failed to update Engram logging: {result.stderr}")
                return False
        else:
            # Manual update
            logger.info("Update script not found, updating manually...")
            return _update_engram_manually(engram_path, logger)
    except Exception as e:
        logger.error(f"Error updating Engram: {e}")
        return False


def _update_engram_manually(engram_path: Path, logger) -> bool:
    """
    Manually update Engram to use centralized logging.
    
    Args:
        engram_path: Path to Engram directory
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    # Memory module path
    memory_py_path = engram_path / "engram" / "core" / "memory.py"
    
    if not memory_py_path.exists():
        logger.error(f"Memory module not found: {memory_py_path}")
        return False
    
    # Read the memory.py file
    content = read_file(memory_py_path)
    if not content:
        logger.error(f"Failed to read {memory_py_path}")
        return False
    
    # Check if already updated
    if is_already_updated(content):
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
    if not write_file(memory_py_path, content):
        logger.error(f"Failed to write updated content to {memory_py_path}")
        return False
    
    logger.info(f"Successfully updated Engram memory module to use Centralized Logging")
    
    # Create a README file to explain the changes
    readme_path = engram_path / "LOGGING_UPDATE.md"
    readme_content = get_readme_content("Engram")
    
    if not write_file(readme_path, readme_content):
        logger.error(f"Failed to write README to {readme_path}")
        # Continue anyway, this is not critical
    else:
        logger.info("Created LOGGING_UPDATE.md with information about the changes")
    
    return True