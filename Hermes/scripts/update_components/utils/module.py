"""
Module importing utilities for component updates.
"""

import importlib.util
import logging
from pathlib import Path
from typing import Any, Optional

# Get logger
logger = logging.getLogger("hermes.scripts.update_components.utils.module")


def import_module_from_file(path: Path) -> Optional[Any]:
    """
    Import a module from a file path.
    
    Args:
        path: Path to the Python file
        
    Returns:
        Imported module, or None if import failed
    """
    try:
        module_name = path.stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            logger.error(f"Failed to create spec for {path}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Error importing module from {path}: {e}")
        return None


def find_suitable_files(base_path: Path, candidates: list) -> list:
    """
    Find suitable files from a list of candidates.
    
    Args:
        base_path: Base directory to look in
        candidates: List of relative paths to check
        
    Returns:
        List of Path objects for existing files
    """
    existing_files = []
    for candidate in candidates:
        if isinstance(candidate, str):
            candidate_path = base_path / candidate
        else:
            candidate_path = candidate
            
        if candidate_path.exists():
            existing_files.append(candidate_path)
            
    return existing_files