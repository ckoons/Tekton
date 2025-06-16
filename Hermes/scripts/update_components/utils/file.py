"""
File manipulation utilities for component updates.
"""

from pathlib import Path
import importlib.util
import shutil
import logging

# Get logger
logger = logging.getLogger("hermes.scripts.update_components.utils.file")


def write_file(file_path: Path, content: str) -> bool:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, "w") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return False


def read_file(file_path: Path) -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content as string, or empty string if file doesn't exist
    """
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""


def file_exists(file_path: Path) -> bool:
    """
    Check if a file exists.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file exists, False otherwise
    """
    return file_path.exists() and file_path.is_file()


def create_directory(dir_path: Path) -> bool:
    """
    Create a directory if it doesn't exist.
    
    Args:
        dir_path: Path to the directory
        
    Returns:
        True if successful, False otherwise
    """
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {dir_path}: {e}")
        return False


def copy_file(src_path: Path, dst_path: Path) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        src_path: Source file path
        dst_path: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        shutil.copy2(src_path, dst_path)
        return True
    except Exception as e:
        logger.error(f"Error copying file from {src_path} to {dst_path}: {e}")
        return False