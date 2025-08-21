"""
Tekton Startup Utilities

Provides common startup functionality for Tekton components including
environment variable loading, configuration setup, and initialization logging.

Usage:
    from shared.utils.tekton_startup import initialize_tekton_environment
    
    # At the start of your component
    initialize_tekton_environment(component_name="apollo")
"""

import os
from shared.env import TektonEnviron
import sys
import logging
from pathlib import Path
from typing import Dict, Optional

# Try to import TektonEnvManager
try:
    from .env_manager import TektonEnvManager
    ENV_MANAGER_AVAILABLE = True
except ImportError:
    ENV_MANAGER_AVAILABLE = False

logger = logging.getLogger(__name__)

def initialize_tekton_environment(
    component_name: str,
    auto_load: bool = True,
    log_level: Optional[str] = None
) -> Dict[str, str]:
    """
    Initialize Tekton environment for a component.
    
    Args:
        component_name: Name of the component (e.g., 'apollo', 'hermes')
        auto_load: Whether to automatically load environment files
        log_level: Override log level (if None, uses environment setting)
        
    Returns:
        Dictionary of environment variables after loading
    """
    print(f"[{component_name.upper()}] Initializing Tekton environment...")
    
    try:
        if ENV_MANAGER_AVAILABLE and auto_load:
            # Use TektonEnvManager for full three-tier loading
            env_manager = TektonEnvManager()
            env_data = env_manager.load_environment()
            
            # Configure logging level from environment
            setup_component_logging(component_name, log_level)
            
            # Log component-specific environment info
            log_component_environment(component_name, env_manager)
            
            logger.info(f"[{component_name.upper()}] Environment initialized with TektonEnvManager")
            return env_data
            
        else:
            # Fallback to basic environment loading
            if not ENV_MANAGER_AVAILABLE:
                print(f"[{component_name.upper()}] TektonEnvManager not available, using basic environment")
            
            # Check if environment is already loaded by C launcher
            if TektonEnviron.get('_TEKTON_ENV_FROZEN') == '1':
                print(f"[{component_name.upper()}] Using environment loaded by Tekton launcher")
            else:
                print(f"[{component_name.upper()}] Warning: Environment not loaded by Tekton launcher")
                print(f"[{component_name.upper()}] Please run this component using the 'tekton' command")
            
            # Configure logging
            setup_component_logging(component_name, log_level)
            
            logger.info(f"[{component_name.upper()}] Environment initialized (basic mode)")
            return dict(os.environ)
            
    except Exception as e:
        print(f"[{component_name.upper()}] Error initializing environment: {e}")
        # Continue with system environment
        setup_component_logging(component_name, log_level)
        return dict(os.environ)

def setup_component_logging(component_name: str, log_level_override: Optional[str] = None) -> None:
    """
    Setup logging for a Tekton component.
    
    Args:
        component_name: Name of the component
        log_level_override: Override the environment log level setting
    """
    # Determine log level
    if log_level_override:
        log_level = log_level_override.upper()
    else:
        log_level = TektonEnviron.get('TEKTON_LOG_LEVEL', 'INFO').upper()
    
    # Map log level strings to logging constants
    level_map = {
        'TRACE': logging.DEBUG,  # Python doesn't have TRACE, use DEBUG
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARN': logging.WARNING,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'FATAL': logging.CRITICAL,
        'CRITICAL': logging.CRITICAL,
        'OFF': logging.CRITICAL + 1  # Effectively disable logging
    }
    
    numeric_level = level_map.get(log_level, logging.INFO)
    
    # Configure root logger for the component
    logging.basicConfig(
        level=numeric_level,
        format=f'%(asctime)s [{component_name.upper()}] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set level for all existing loggers
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).setLevel(numeric_level)
    
    logger.info(f"Logging configured for {component_name} at level {log_level}")

def log_component_environment(component_name: str, env_manager=None) -> None:
    """
    Log relevant environment information for a component.
    
    Args:
        component_name: Name of the component
        env_manager: Optional TektonEnvManager instance
    """
    try:
        # Log component port
        port_var = f"{component_name.upper()}_PORT"
        port = TektonEnviron.get(port_var)
        if port:
            logger.info(f"Component port: {port}")
        
        # Log debug settings
        debug_enabled = TektonEnviron.get('TEKTON_DEBUG', 'false').lower() == 'true'
        if debug_enabled:
            logger.info("Debug mode enabled")
        
        # Log key Tekton settings
        key_settings = [
            'SHOW_GREEK_NAMES',
            'TEKTON_THEME_MODE',
            'TEKTON_AUTO_LAUNCH',
            'TEKTON_MCP_ENABLED'
        ]
        
        for setting in key_settings:
            value = TektonEnviron.get(setting)
            if value:
                logger.debug(f"{setting}: {value}")
                
    except Exception as e:
        logger.warning(f"Error logging environment info: {e}")

def get_component_port(component_name: str, default: Optional[int] = None) -> Optional[int]:
    """
    Get the port for a component from environment variables.
    
    Args:
        component_name: Name of the component
        default: Default port if not found
        
    Returns:
        Port number or None if not found and no default
    """
    port_var = f"{component_name.upper()}_PORT"
    port_str = TektonEnviron.get(port_var)
    
    if port_str:
        try:
            return int(port_str)
        except ValueError:
            logger.warning(f"Invalid port value for {port_var}: {port_str}")
    
    return default

def is_debug_enabled() -> bool:
    """
    Check if debug mode is enabled.
    
    Returns:
        True if debug mode is enabled
    """
    return TektonEnviron.get('TEKTON_DEBUG', 'false').lower() == 'true'

def get_tekton_setting(key: str, default: str = '') -> str:
    """
    Get a Tekton setting from environment variables.
    
    Args:
        key: Setting key (with or without TEKTON_ prefix)
        default: Default value if not found
        
    Returns:
        Setting value
    """
    # Add TEKTON_ prefix if not present
    if not key.startswith('TEKTON_'):
        key = f'TEKTON_{key}'
    
    return TektonEnviron.get(key, default)

def get_tekton_bool_setting(key: str, default: bool = False) -> bool:
    """
    Get a boolean Tekton setting from environment variables.
    
    Args:
        key: Setting key (with or without TEKTON_ prefix)
        default: Default value if not found
        
    Returns:
        Boolean setting value
    """
    value = get_tekton_setting(key, str(default)).lower()
    return value in ('true', 'yes', '1', 'y', 't', 'on')

# Convenience function for common startup pattern
def tekton_component_startup(component_name: str) -> Dict[str, str]:
    """
    Convenience function for standard Tekton component startup.
    
    Args:
        component_name: Name of the component
        
    Returns:
        Dictionary of environment variables
    """
    print(f"🚀 Starting {component_name.title()} component...")
    
    # Initialize environment
    env_data = initialize_tekton_environment(component_name)
    
    # Log startup info
    port = get_component_port(component_name)
    if port:
        logger.info(f"🌐 {component_name.title()} will run on port {port}")
    
    debug = is_debug_enabled()
    if debug:
        logger.info("🐛 Debug mode enabled")
    
    logger.info(f"✅ {component_name.title()} startup complete")
    
    return env_data