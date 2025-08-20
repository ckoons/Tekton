"""
Tekton Environment Management

Provides controlled environment configuration loading and access.
Only the main tekton script should use TektonEnvironLock.
All other modules should use TektonEnviron.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Module-level storage for frozen environment
_frozen_env: Dict[str, str] = {}
_is_loaded: bool = False

# Setup logging
logger = logging.getLogger(__name__)


class TektonEnvironLock:
    """
    Environment loader - ONLY for use by main tekton script.
    Loads environment files in correct order and freezes the result.
    """
    
    @staticmethod
    def load() -> None:
        """
        Load environment from multiple sources in order:
        1. Current os.environ
        2. ~/.env
        3. $TEKTON_ROOT/.env.tekton
        4. $TEKTON_ROOT/.env.local
        
        Each file overwrites values from previous sources.
        Updates both os.environ and the frozen copy.
        """
        global _frozen_env, _is_loaded
        
        if _is_loaded:
            logger.warning("TektonEnvironLock.load() called multiple times - ignoring")
            return
        
        # Start with current environment
        env_dict = dict(os.environ)
        
        # TEKTON_ROOT must already be set in environment
        # (the main scripts run from any directory and must have it set)
        if 'TEKTON_ROOT' not in env_dict:
            raise RuntimeError("TEKTON_ROOT not set in environment")
        
        # Load files in order
        env_files = [
            Path.home() / '.env',
            Path(env_dict.get('TEKTON_ROOT', '')) / '.env.tekton',
            Path(env_dict.get('TEKTON_ROOT', '')) / '.env.local'
        ]
        
        for env_file in env_files:
            if env_file.exists():
                logger.debug(f"Loading environment from: {env_file}")
                _load_env_file(env_file, env_dict)
        
        # Set internal system variable to indicate environment is frozen
        # This allows subprocesses to detect they have the frozen environment
        env_dict['_TEKTON_ENV_FROZEN'] = '1'
        
        # Construct and set PATH and PYTHONPATH using TEKTON_ROOT
        tekton_root = env_dict.get('TEKTON_ROOT', '')
        if tekton_root:
            # Construct PATH - add Tekton directories to the beginning
            current_path = env_dict.get('PATH', '')
            tekton_paths = [
                f"{tekton_root}/scripts",
                f"{tekton_root}/shared/aish",
                f"{tekton_root}/tekton-core/scripts/bin",
                f"{tekton_root}/shared/ci_tools"
            ]
            # Only add paths that exist
            existing_tekton_paths = [p for p in tekton_paths if Path(p).exists()]
            if existing_tekton_paths:
                new_path = ':'.join(existing_tekton_paths) + ':' + current_path
                env_dict['PATH'] = new_path
                logger.debug(f"Set PATH with Tekton directories: {':'.join(existing_tekton_paths)}")
            
            # Construct PYTHONPATH - add Tekton modules
            current_pythonpath = env_dict.get('PYTHONPATH', '')
            python_paths = [
                tekton_root,
                f"{tekton_root}/shared",
                f"{tekton_root}/tekton"
            ]
            # Only add paths that exist
            existing_python_paths = [p for p in python_paths if Path(p).exists()]
            if existing_python_paths:
                new_pythonpath = ':'.join(existing_python_paths)
                if current_pythonpath:
                    new_pythonpath = new_pythonpath + ':' + current_pythonpath
                env_dict['PYTHONPATH'] = new_pythonpath
                logger.debug(f"Set PYTHONPATH with Tekton modules: {':'.join(existing_python_paths)}")
        
        # Update os.environ with the merged result
        os.environ.clear()
        os.environ.update(env_dict)
        
        # Freeze a copy for TektonEnviron
        _frozen_env = dict(env_dict)
        _is_loaded = True
        
        logger.info(f"Environment loaded and frozen with {len(_frozen_env)} variables")
    


class TektonEnviron:
    """
    Read-only environment access for all Tekton modules.
    Provides the frozen environment state.
    
    The environment must be loaded by TektonEnvironLock.load() before use.
    This is typically done by the main tekton script. Secondary scripts
    (like tekton-status, tekton-launch) should check is_loaded() first
    and redirect users to the main tekton command if not loaded.
    
    Module state:
        _is_loaded: Boolean flag indicating if environment has been loaded
        _frozen_env: Dictionary containing the frozen environment state
    """
    
    @staticmethod
    def all() -> Dict[str, str]:
        """
        Get a copy of the entire frozen environment.
        
        Usage:
            import os
            from shared.env import TektonEnviron
            os.environ = TektonEnviron.all()
        """
        if not _is_loaded and os.environ.get('_TEKTON_ENV_FROZEN') != '1':
            # If accessed before load AND not in a subprocess with frozen env
            logger.warning("TektonEnviron accessed before TektonEnvironLock.load() - returning current os.environ")
        return dict(os.environ)  # Always return current environment
    
    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a single environment variable."""
        if not _is_loaded and os.environ.get('_TEKTON_ENV_FROZEN') != '1':
            # If accessed before load AND not in a subprocess with frozen env
            logger.warning(f"TektonEnviron.get('{key}') called before TektonEnvironLock.load()")
        return os.environ.get(key, default)  # Always use current environment
    
    @staticmethod
    def set(key: str, value: str) -> None:
        """
        No-op setter that logs attempts to modify environment.
        This helps identify code that tries to change environment.
        """
        logger.debug(f"Attempted environment change ignored: {key}={value}")
    
    @staticmethod
    def is_loaded() -> bool:
        """
        Check if environment has been loaded by TektonEnvironLock.
        
        This checks both the in-memory flag (for the current process) and
        the _TEKTON_ENV_FROZEN environment variable (for subprocesses that
        received the frozen environment).
        
        Returns:
            True if environment has been loaded and frozen, False otherwise
        """
        return _is_loaded or os.environ.get('_TEKTON_ENV_FROZEN') == '1'


class TektonEnvironUpdate:
    """
    Hidden environment updater - DO NOT USE without careful review.
    This class is intentionally not exposed in normal imports.
    """
    
    @staticmethod
    def update(key: str, value: str) -> None:
        """Actually update the frozen environment - use with extreme caution."""
        global _frozen_env
        if not _is_loaded:
            raise RuntimeError("Cannot update environment before TektonEnvironLock.load()")
        
        logger.warning(f"TektonEnvironUpdate: Modifying frozen environment {key}={value}")
        _frozen_env[key] = value
        # Also update os.environ to maintain consistency
        os.environ[key] = value



def _load_env_file(filepath: Path, env_dict: Dict[str, str]) -> None:
    """Load a .env file and update the environment dictionary."""
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Skip lines without '='
                if '=' not in line:
                    continue
                
                # Parse key=value
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Update the dictionary
                env_dict[key] = value
                logger.debug(f"  Set {key} from {filepath.name}")
                
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")