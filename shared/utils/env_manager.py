"""
Tekton Environment Variable Manager

Provides centralized management of environment variables across the Tekton system
using a three-tier approach:
1. ~/.env - User-wide settings shared with all applications  
2. Tekton/.env.tekton - Project settings (tracked in git)
3. Tekton/.env.local - Secrets/API keys (gitignored)

Usage:
    from shared.utils.env_manager import TektonEnvManager
    
    # Load environment on startup
    env_manager = TektonEnvManager()
    env_data = env_manager.load_environment()
    
    # Save settings to .env.tekton
    env_manager.save_tekton_settings({
        'SHOW_GREEK_NAMES': 'true',
        'TEKTON_THEME_MODE': 'dark'
    })
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any, List, Union
import logging

try:
    from dotenv import load_dotenv, set_key
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)

class TektonEnvManager:
    """
    Manages Tekton environment variables using a three-tier approach.
    
    Reading Priority (later files override earlier ones):
    1. ~/.env (user-wide settings)
    2. Tekton/.env.tekton (project settings, tracked)
    3. Tekton/.env.local (secrets, gitignored)
    """
    
    def __init__(self, tekton_root: Optional[Path] = None):
        """
        Initialize the environment manager.
        
        Args:
            tekton_root: Path to Tekton root directory (auto-detected if None)
        """
        # Detect Tekton root directory
        if tekton_root is None:
            self.tekton_root = self._find_tekton_root()
        else:
            self.tekton_root = Path(tekton_root)
        
        # Define environment file paths
        self.user_env = Path.home() / ".env"
        self.tekton_env = self.tekton_root / ".env.tekton"
        self.local_env = self.tekton_root / ".env.local"
        
        # Track loaded environment state
        self._loaded_env: Dict[str, str] = {}
        self._original_env: Dict[str, str] = {}
        
        if not DOTENV_AVAILABLE:
            logger.warning("python-dotenv not available. Install with: pip install python-dotenv")
    
    def _find_tekton_root(self) -> Path:
        """
        Find the Tekton root directory by looking for .env.tekton or tekton-core.
        
        Returns:
            Path to Tekton root directory
            
        Raises:
            FileNotFoundError: If Tekton root cannot be found
        """
        # Start from current working directory and search upward
        current = Path.cwd()
        
        for path in [current] + list(current.parents):
            # Look for .env.tekton file (most reliable indicator)
            if (path / ".env.tekton").exists():
                return path
            
            # Look for multiple component directories as a strong indicator
            # If we find several component directories, this is likely the Tekton root
            component_dirs = ["Apollo", "Hermes", "Engram", "Rhetor", "Athena", "Synthesis", 
                             "Ergon", "Sophia", "Prometheus", "Harmonia", "Penia", "Metis", 
                             "Telos", "Hephaestus", "tekton-core"]
            component_count = sum(1 for comp in component_dirs if (path / comp).exists())
            
            # If we find at least 5 component directories, this is likely the root
            if component_count >= 5:
                return path
            
            # Look for the scripts directory with tekton scripts
            if (path / "scripts" / "enhanced_tekton_launcher.py").exists():
                return path
        
        # If TEKTON_ROOT environment variable is set, use it
        if 'TEKTON_ROOT' in os.environ:
            tekton_root = Path(os.environ['TEKTON_ROOT'])
            if tekton_root.exists():
                return tekton_root
        
        # Fallback to current directory
        logger.warning("Could not find Tekton root directory, using current directory")
        return Path.cwd()
    
    def load_environment(self) -> Dict[str, str]:
        """
        Load environment variables from all three tiers in priority order.
        
        Returns:
            Dictionary of all environment variables after loading
        """
        # Store original environment
        self._original_env = dict(os.environ)
        
        # Always set TEKTON_ROOT to the detected Tekton root
        os.environ['TEKTON_ROOT'] = str(self.tekton_root.absolute())
        logger.debug(f"Set TEKTON_ROOT to: {os.environ['TEKTON_ROOT']}")
        
        # Set TEKTON_LOG_DIR if not already set
        if 'TEKTON_LOG_DIR' not in os.environ:
            os.environ['TEKTON_LOG_DIR'] = os.path.join(os.environ['TEKTON_ROOT'], '.tekton', 'logs')
            logger.debug(f"Set TEKTON_LOG_DIR to: {os.environ['TEKTON_LOG_DIR']}")
        
        # Set TEKTON_DATA_DIR if not already set
        if 'TEKTON_DATA_DIR' not in os.environ:
            os.environ['TEKTON_DATA_DIR'] = os.path.join(os.environ['TEKTON_ROOT'], '.tekton', 'data')
            logger.debug(f"Set TEKTON_DATA_DIR to: {os.environ['TEKTON_DATA_DIR']}")
        
        # Load files in priority order (later files override earlier ones)
        env_files = [
            (self.user_env, "user"),
            (self.tekton_env, "tekton"),
            (self.local_env, "local")
        ]
        
        loaded_files = []
        
        for env_file, file_type in env_files:
            if env_file.exists():
                try:
                    if DOTENV_AVAILABLE:
                        # Use dotenv for proper parsing
                        load_dotenv(env_file, override=True)
                        loaded_files.append(f"{file_type} ({env_file})")
                    else:
                        # Fallback manual parsing
                        self._load_env_file_manual(env_file)
                        loaded_files.append(f"{file_type} ({env_file}) [manual]")
                except Exception as e:
                    logger.error(f"Error loading {file_type} env file {env_file}: {e}")
        
        # Update loaded environment state
        self._loaded_env = dict(os.environ)
        
        if loaded_files:
            logger.debug(f"Loaded environment from: {', '.join(loaded_files)}")
        else:
            logger.debug("No environment files found, using system environment only")
        
        return dict(os.environ)
    
    def _load_env_file_manual(self, env_file: Path) -> None:
        """
        Manually parse and load an environment file.
        
        Args:
            env_file: Path to environment file to load
        """
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Set environment variable
                        os.environ[key] = value
                    else:
                        logger.warning(f"Invalid line in {env_file}:{line_num}: {line}")
        except Exception as e:
            logger.error(f"Error manually parsing {env_file}: {e}")
    
    def get_current_environment(self) -> Dict[str, str]:
        """
        Get the current environment variables.
        
        Returns:
            Dictionary of current environment variables
        """
        return dict(os.environ)
    
    def get_tekton_variables(self) -> Dict[str, str]:
        """
        Get all Tekton-specific environment variables.
        
        Returns:
            Dictionary of Tekton environment variables
        """
        tekton_vars = {}
        
        # Known Tekton prefixes
        tekton_prefixes = [
            'TEKTON_',
            'SHOW_GREEK_NAMES',
            'HEPHAESTUS_PORT',
            'ENGRAM_PORT',
            'HERMES_PORT',
            'ERGON_PORT',
            'RHETOR_PORT',
            'TERMA_PORT',
            'ATHENA_PORT',
            'PROMETHEUS_PORT',
            'HARMONIA_PORT',
            'TELOS_PORT',
            'SYNTHESIS_PORT',
            'TEKTON_CORE_PORT',
            'METIS_PORT',
            'APOLLO_PORT',
            'BUDGET_PORT',
            'SOPHIA_PORT',
            'NUMA_PORT',
            'NOESIS_PORT'
        ]
        
        for key, value in os.environ.items():
            if any(key.startswith(prefix) for prefix in tekton_prefixes):
                tekton_vars[key] = value
        
        return tekton_vars
    
    def save_tekton_settings(self, settings: Dict[str, Union[str, bool, int, float]]) -> None:
        """
        Save settings to the .env.tekton file (tracked in git).
        
        Args:
            settings: Dictionary of settings to save
        """
        # Ensure .env.tekton exists
        if not self.tekton_env.exists():
            self.create_tekton_env_template()
        
        try:
            if DOTENV_AVAILABLE:
                # Use dotenv for proper handling
                for key, value in settings.items():
                    # Convert value to string
                    if isinstance(value, bool):
                        str_value = 'true' if value else 'false'
                    else:
                        str_value = str(value)
                    
                    set_key(str(self.tekton_env), key, str_value)
                    os.environ[key] = str_value
                    
                logger.info(f"Saved {len(settings)} settings to {self.tekton_env}")
            else:
                # Fallback manual saving
                self._save_env_file_manual(self.tekton_env, settings)
                
        except Exception as e:
            logger.error(f"Error saving settings to {self.tekton_env}: {e}")
            raise
    
    def _save_env_file_manual(self, env_file: Path, settings: Dict[str, Any]) -> None:
        """
        Manually save settings to an environment file.
        
        Args:
            env_file: Path to environment file
            settings: Settings to save
        """
        # Read existing file if it exists
        existing_lines = []
        existing_keys = set()
        
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    existing_lines.append(line.rstrip())
                    # Track existing keys
                    if '=' in line and not line.strip().startswith('#'):
                        key = line.split('=', 1)[0].strip()
                        existing_keys.add(key)
        
        # Update existing keys and add new ones
        updated_lines = []
        for line in existing_lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=', 1)[0].strip()
                if key in settings:
                    # Update existing key
                    value = settings[key]
                    if isinstance(value, bool):
                        str_value = 'true' if value else 'false'
                    else:
                        str_value = str(value)
                    updated_lines.append(f"{key}={str_value}")
                    settings.pop(key)  # Remove from settings to add
                else:
                    # Keep existing line unchanged
                    updated_lines.append(line)
            else:
                # Keep comments and empty lines
                updated_lines.append(line)
        
        # Add any new settings
        for key, value in settings.items():
            if isinstance(value, bool):
                str_value = 'true' if value else 'false'
            else:
                str_value = str(value)
            updated_lines.append(f"{key}={str_value}")
            os.environ[key] = str_value
        
        # Write updated file
        with open(env_file, 'w', encoding='utf-8') as f:
            for line in updated_lines:
                f.write(line + '\n')
        
        logger.info(f"Manually saved settings to {env_file}")
    
    def create_tekton_env_template(self) -> None:
        """
        Create a template .env.tekton file with all available Tekton settings.
        """
        template_content = '''#
# .env.tekton
#   This file is used to configure the Tekton Multi-AI Engineering Platform.
#   You should not place any 'secrets' such as API keys or passwords in this file. 
#   This file is uploaded to GitHub and is accessible to anyone who has access to the repository.
#   You may configure all Tekton environment, profile and settings using this file that are not 'secret'
#   For API keys and passwords or secret information, consider using ~/.env and Tekton/.env.local 
#

# UI Display Settings
# Whether to show Greek names for components (true/false)
SHOW_GREEK_NAMES=true

# Theme Settings
# Theme mode: 'dark' or 'light'
TEKTON_THEME_MODE=dark
# Theme color: 'blue', 'green', or 'purple'  
TEKTON_THEME_COLOR=blue

# Debug Settings
# Master switch for debug instrumentation (true/false)
TEKTON_DEBUG=false
# Log level: TRACE, DEBUG, INFO, WARN, ERROR, FATAL, OFF
TEKTON_LOG_LEVEL=INFO

# Vector Database Settings
# Preferred vector database: 'auto', 'faiss', 'chromadb', 'qdrant', 'lancedb'
# 'auto' will automatically select based on hardware (recommended)
TEKTON_VECTOR_DB=auto
# Force CPU-only mode for vector operations (true/false)
TEKTON_VECTOR_CPU_ONLY=false
# Enable GPU acceleration if available (true/false)
TEKTON_VECTOR_GPU_ENABLED=true

# Component Port Assignments (Single Port Architecture)
# UI system (using standard web port)
HEPHAESTUS_PORT=8080
# Memory system
ENGRAM_PORT=8000
# Service registry & messaging
HERMES_PORT=8001
# Agent system
ERGON_PORT=8002
# LLM management
RHETOR_PORT=8003
# Terminal system
TERMA_PORT=8004
# Knowledge graph
ATHENA_PORT=8005
# Planning system
PROMETHEUS_PORT=8006
# Workflow system
HARMONIA_PORT=8007
# Requirements system
TELOS_PORT=8008
# Execution engine
SYNTHESIS_PORT=8009
# Core orchestration
TEKTON_CORE_PORT=8010
# Task management system
METIS_PORT=8011
# Local Attention/Prediction system
APOLLO_PORT=8012
# Token/cost management system
BUDGET_PORT=8013
# Machine learning system
SOPHIA_PORT=8014

# Specialized Service Ports

# Terminal Settings
# Terminal mode: 'advanced' or 'simple'
TEKTON_TERMINAL_MODE=advanced
# Terminal font size in pixels (8-24)
TEKTON_TERMINAL_FONT_SIZE=14
# Terminal font family
TEKTON_TERMINAL_FONT_FAMILY='Courier New', monospace
# Terminal theme: 'default', 'light', 'dark', 'monokai', 'solarized'
TEKTON_TERMINAL_THEME=default
# Terminal cursor style: 'block', 'bar', 'underline'
TEKTON_TERMINAL_CURSOR_STYLE=block
# Terminal cursor blink (true/false)
TEKTON_TERMINAL_CURSOR_BLINK=true
# Terminal scrollback enabled (true/false)
TEKTON_TERMINAL_SCROLLBACK=true
# Terminal scrollback lines
TEKTON_TERMINAL_SCROLLBACK_LINES=1000

# Chat Settings
# Chat history enabled (true/false)
TEKTON_CHAT_HISTORY_ENABLED=true
# Maximum chat history entries
TEKTON_CHAT_HISTORY_MAX_ENTRIES=50

# Performance Settings
# Auto-launch components on startup (true/false)
TEKTON_AUTO_LAUNCH=true
# Component startup timeout in seconds
TEKTON_COMPONENT_TIMEOUT=30

# Integration Settings
# Enable MCP integration (true/false)
TEKTON_MCP_ENABLED=true
# Enable Hermes service discovery (true/false)
TEKTON_HERMES_DISCOVERY=true

# User Preferences (can be overridden by Profile settings)
# Default model for LLM operations
TEKTON_DEFAULT_MODEL=claude-3-sonnet
# Default provider for LLM operations  
TEKTON_DEFAULT_PROVIDER=anthropic
# Enable notifications (true/false)
TEKTON_NOTIFICATIONS_ENABLED=true

# Component Feature Flags
# Enable Apollo predictive features (true/false)
TEKTON_APOLLO_PREDICTIONS=true
# Enable Sophia machine learning features (true/false)
TEKTON_SOPHIA_ML=true
# Enable Budget cost tracking (true/false)
TEKTON_BUDGET_TRACKING=true
# Enable Ergon agent automation (true/false)
TEKTON_ERGON_AUTOMATION=true

# .env.tekton
'''
        
        try:
            with open(self.tekton_env, 'w', encoding='utf-8') as f:
                f.write(template_content)
            logger.info(f"Created template .env.tekton file at {self.tekton_env}")
        except Exception as e:
            logger.error(f"Error creating template .env.tekton file: {e}")
            raise
    
    def get_component_port(self, component: str) -> Optional[int]:
        """
        Get the port for a specific component.
        
        Args:
            component: Component name (e.g., 'hermes', 'ergon')
            
        Returns:
            Port number or None if not found
        """
        env_var = f"{component.upper()}_PORT"
        port_str = os.environ.get(env_var)
        
        if port_str:
            try:
                return int(port_str)
            except ValueError:
                logger.warning(f"Invalid port value for {env_var}: {port_str}")
        
        return None
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Boolean value
        """
        value = os.environ.get(key, str(default)).lower()
        return value in ('true', 'yes', '1', 'y', 't', 'on')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get an integer environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Integer value
        """
        value = os.environ.get(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}")
            return default
    
    def get_list(self, key: str, default: Optional[List[str]] = None, separator: str = ',') -> List[str]:
        """
        Get a list environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            separator: Separator character for splitting
            
        Returns:
            List of strings
        """
        if default is None:
            default = []
        
        value = os.environ.get(key)
        if value is None:
            return default
        
        if not value.strip():
            return []
        
        return [item.strip() for item in value.split(separator)]
    
    def has_local_env(self) -> bool:
        """
        Check if .env.local file exists.
        
        Returns:
            True if .env.local exists, False otherwise
        """
        return self.local_env.exists()
    
    def create_local_env_template(self) -> None:
        """
        Create a template .env.local file for secrets.
        """
        template_content = '''#
# .env.local
# Local environment variables for secrets and API keys
# This file is gitignored and should never be committed to the repository
#

# API Keys (keep these secret!)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
# GITHUB_TOKEN=your_github_token_here

# Database URLs (if needed)
# DATABASE_URL=your_database_url_here
# REDIS_URL=your_redis_url_here

# External Service Credentials
# AWS_ACCESS_KEY_ID=your_aws_key_here
# AWS_SECRET_ACCESS_KEY=your_aws_secret_here

# Custom Local Overrides
# Any Tekton setting can be overridden here for local development
# Example: TEKTON_DEBUG=true for local debugging

'''
        
        try:
            with open(self.local_env, 'w', encoding='utf-8') as f:
                f.write(template_content)
            logger.info(f"Created template .env.local file at {self.local_env}")
        except Exception as e:
            logger.error(f"Error creating template .env.local file: {e}")
            raise
    
    def ensure_gitignore(self) -> None:
        """
        Ensure .env.local is in .gitignore file.
        """
        gitignore_path = self.tekton_root / ".gitignore"
        
        try:
            # Read existing .gitignore
            existing_content = ""
            if gitignore_path.exists():
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Check if .env.local is already ignored
            if '.env.local' not in existing_content:
                # Add .env.local to .gitignore
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    if existing_content and not existing_content.endswith('\n'):
                        f.write('\n')
                    f.write('# Local environment variables (secrets)\n')
                    f.write('.env.local\n')
                
                logger.info("Added .env.local to .gitignore")
            
        except Exception as e:
            logger.warning(f"Could not update .gitignore: {e}")


# Global instance for convenient access
_global_env_manager: Optional[TektonEnvManager] = None

def get_env_manager() -> TektonEnvManager:
    """
    Get the global TektonEnvManager instance.
    
    Returns:
        Global TektonEnvManager instance
    """
    global _global_env_manager
    if _global_env_manager is None:
        _global_env_manager = TektonEnvManager()
    return _global_env_manager

def load_tekton_environment() -> Dict[str, str]:
    """
    Convenience function to load Tekton environment.
    
    Returns:
        Dictionary of environment variables
    """
    return get_env_manager().load_environment()

def save_tekton_settings(**settings) -> None:
    """
    Convenience function to save Tekton settings.
    
    Args:
        **settings: Settings to save as keyword arguments
    """
    get_env_manager().save_tekton_settings(settings)

def get_tekton_var(key: str, default: Any = None) -> Any:
    """
    Convenience function to get a Tekton environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value
    """
    return os.environ.get(key, default)
