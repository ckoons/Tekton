#!/usr/bin/env python3
"""
Tekton Component Startup

Contains functions for starting Tekton components.
"""

import os
import sys
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List

from .components import COMPONENTS, running_components, running_lock

logger = logging.getLogger("tekton.startup")

# Initialize imports for startup
try:
    # Add Ergon to the Python path if not already there
    TEKTON_ROOT = Path.home() / ".tekton"
    ERGON_ROOT = Path(__file__).parent.parent.parent.absolute()
    if str(ERGON_ROOT) not in sys.path:
        sys.path.insert(0, str(ERGON_ROOT))
    
    # Import Ergon modules
    from ergon.utils.config.settings import settings
    from ergon.core.database.engine import init_db
    from ergon.core.memory import client_manager
except ImportError as e:
    logger.error(f"Error importing Ergon modules: {e}")
    logger.error("Please make sure Ergon is installed correctly.")
    sys.exit(1)

async def start_database() -> bool:
    """
    Initialize the database services.
    
    Returns:
        True if successful
    """
    logger.info("Starting database services...")
    
    try:
        # Ensure the Tekton home directory exists
        os.makedirs(settings.tekton_home, exist_ok=True)
        
        # Initialize the SQLite database if needed
        db_path = settings.database_url.replace("sqlite:///", "")
        if not os.path.exists(db_path):
            logger.info("Initializing SQLite database...")
            init_db()
        
        # Initialize the vector database directory if needed
        os.makedirs(settings.vector_db_path, exist_ok=True)
        
        logger.info("Database services initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database services: {e}")
        return False

async def start_engram() -> bool:
    """
    Start the Engram memory service.
    
    Returns:
        True if successful
    """
    logger.info("Starting Engram memory service...")
    
    try:
        # Initialize the client manager
        await client_manager.start()
        
        # Register Engram as a core service
        engram_config = {
            "service_type": "core",
            "description": "Central memory service"
        }
        
        client_id = COMPONENTS["engram"]["client_id"]
        success = await client_manager.register_client(
            client_id=client_id,
            client_type="engram",
            config=engram_config
        )
        
        if success:
            logger.info("Engram memory service started successfully")
            return True
        else:
            logger.error("Failed to register Engram client")
            return False
    except Exception as e:
        logger.error(f"Error starting Engram memory service: {e}")
        return False

async def start_ergon() -> bool:
    """
    Start the Ergon agent framework and register it with Engram.
    
    Returns:
        True if successful
    """
    logger.info("Starting Ergon agent framework...")
    
    try:
        # Register Ergon with Engram
        ergon_config = {
            "service_type": "framework",
            "description": "Agent and tool framework"
        }
        
        client_id = COMPONENTS["ergon"]["client_id"]
        success = await client_manager.register_client(
            client_id=client_id,
            client_type="ergon",
            config=ergon_config
        )
        
        if success:
            # Set metadata for Ergon client
            await client_manager.set_client_metadata(
                client_id=client_id,
                key="framework_version",
                value="1.0"
            )
            
            logger.info("Ergon agent framework started and registered with Engram")
            return True
        else:
            logger.error("Failed to register Ergon with Engram")
            return False
    except Exception as e:
        logger.error(f"Error starting Ergon agent framework: {e}")
        return False

async def start_ollama(model_name: str = "llama3") -> bool:
    """
    Start Ollama integration.
    
    Args:
        model_name: Ollama model to use
        
    Returns:
        True if successful
    """
    logger.info(f"Starting Ollama integration with model {model_name}...")
    
    try:
        # Register Ollama client
        success = await client_manager.register_client(
            client_id="ollama_service",
            client_type="ollama",
            config={"model": model_name}
        )
        
        if success:
            logger.info(f"Ollama integration started with model {model_name}")
            return True
        else:
            logger.error("Failed to register Ollama client")
            return False
    except Exception as e:
        logger.error(f"Error starting Ollama integration: {e}")
        return False

async def start_claude(model_name: str = "claude-3-sonnet-20240229") -> bool:
    """
    Start Claude integration.
    
    Args:
        model_name: Claude model to use
        
    Returns:
        True if successful
    """
    logger.info(f"Starting Claude integration with model {model_name}...")
    
    try:
        # Check if Anthropic API key is set
        if not settings.has_anthropic:
            logger.error("Anthropic API key not configured. Please set ANTHROPIC_API_KEY in your environment.")
            return False
        
        # Register Claude client
        success = await client_manager.register_client(
            client_id="claude_service",
            client_type="claude",
            config={"model": model_name}
        )
        
        if success:
            logger.info(f"Claude integration started with model {model_name}")
            return True
        else:
            logger.error("Failed to register Claude client")
            return False
    except Exception as e:
        logger.error(f"Error starting Claude integration: {e}")
        return False

async def start_openai(model_name: str = "gpt-4o-mini") -> bool:
    """
    Start OpenAI integration.
    
    Args:
        model_name: OpenAI model to use
        
    Returns:
        True if successful
    """
    logger.info(f"Starting OpenAI integration with model {model_name}...")
    
    try:
        # Check if OpenAI API key is set
        if not settings.has_openai:
            logger.error("OpenAI API key not configured. Please set OPENAI_API_KEY in your environment.")
            return False
        
        # Register OpenAI client
        success = await client_manager.register_client(
            client_id="openai_service",
            client_type="openai",
            config={"model": model_name}
        )
        
        if success:
            logger.info(f"OpenAI integration started with model {model_name}")
            return True
        else:
            logger.error("Failed to register OpenAI client")
            return False
    except Exception as e:
        logger.error(f"Error starting OpenAI integration: {e}")
        return False

async def start_component(component_id: str, config: Dict[str, Any] = None) -> bool:
    """
    Start a specific component.
    
    Args:
        component_id: ID of the component to start
        config: Optional configuration for the component
        
    Returns:
        True if successful
    """
    # Check if the component exists
    if component_id not in COMPONENTS:
        logger.error(f"Component {component_id} does not exist")
        return False
    
    # Check if the component is already running
    with running_lock:
        if component_id in running_components:
            logger.info(f"Component {component_id} is already running")
            return True
    
    # Check if dependencies are running
    component = COMPONENTS[component_id]
    for dependency in component["dependencies"]:
        with running_lock:
            if dependency not in running_components:
                logger.error(f"Cannot start {component_id} because dependency {dependency} is not running")
                return False
    
    # Start the component based on its type
    success = False
    if component_id == "database":
        success = await start_database()
    elif component_id == "engram":
        success = await start_engram()
    elif component_id == "ergon":
        success = await start_ergon()
    elif component_id == "ollama":
        model_name = config.get("model", "llama3") if config else "llama3"
        success = await start_ollama(model_name)
    elif component_id == "claude":
        model_name = config.get("model", "claude-3-sonnet-20240229") if config else "claude-3-sonnet-20240229"
        success = await start_claude(model_name)
    elif component_id == "openai":
        model_name = config.get("model", "gpt-4o-mini") if config else "gpt-4o-mini"
        success = await start_openai(model_name)
    
    # Update running components
    if success:
        with running_lock:
            running_components[component_id] = {
                "started_at": time.time(),
                "config": config or {}
            }
    
    return success

async def start_all_components(include_optional: bool = False) -> bool:
    """
    Start all Tekton components in the correct dependency order.
    
    Args:
        include_optional: Whether to include optional components
        
    Returns:
        True if all required components started successfully
    """
    logger.info(f"Starting all Tekton components (include_optional={include_optional})...")
    
    # Get components in startup order
    component_ids = sorted(
        COMPONENTS.keys(),
        key=lambda c: COMPONENTS[c]["startup_sequence"]
    )
    
    # Start each component
    all_required_success = True
    for component_id in component_ids:
        component = COMPONENTS[component_id]
        
        # Skip optional components if not requested
        if component.get("optional", False) and not include_optional:
            continue
        
        success = await start_component(component_id)
        
        # If a required component fails, mark the overall start as failed
        if not success and not component.get("optional", False):
            all_required_success = False
    
    # Return success only if all required components started
    return all_required_success