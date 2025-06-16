#!/usr/bin/env python3
"""
Tekton Client - Unified launcher for Tekton's AI models and services.

This script provides a unified interface for starting and managing
different AI model clients (Claude, ChatGPT, Ollama) with Tekton's
memory and shared components.
"""

import os
import sys
import argparse
import asyncio
import json
import logging
import signal
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tekton_client")

# Add Ergon to the Python path if not already there
ERGON_ROOT = Path(__file__).parent.parent.absolute()
if str(ERGON_ROOT) not in sys.path:
    sys.path.insert(0, str(ERGON_ROOT))

# Import Ergon modules
try:
    from ergon.utils.config.settings import settings
    from ergon.core.memory import client_manager
    from ergon.core.database.engine import init_db
except ImportError as e:
    logger.error(f"Error importing Ergon modules: {e}")
    logger.error("Please make sure Ergon is installed correctly.")
    sys.exit(1)

# Define model types and defaults
MODEL_TYPES = {
    "ollama": {
        "default_model": "llama3",
        "description": "Run Ollama locally with Tekton memory integration"
    },
    "claude": {
        "default_model": "claude-3-sonnet-20240229",
        "description": "Run Claude with Tekton memory integration",
        "models": [
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20240620",
            "claude-3-7-sonnet-20250219"
        ]
    },
    "openai": {
        "default_model": "gpt-4o-mini",
        "description": "Run OpenAI models with Tekton memory integration",
        "models": [
            "gpt-3.5-turbo",
            "gpt-4o-mini",
            "gpt-4o"
        ]
    },
    "claudecode": {
        "default_model": "claude-3-7-sonnet-20250219",
        "description": "Run Claude Code with Tekton memory integration"
    }
}

async def register_client(model_type: str, client_id: str, model_name: Optional[str] = None) -> bool:
    """
    Register a client with the memory system.
    
    Args:
        model_type: Type of the client (ollama, claude, openai, etc.)
        client_id: Unique client ID
        model_name: Specific model to use (if None, uses the default for the type)
        
    Returns:
        True if registration was successful
    """
    # Get model name if not provided
    if not model_name:
        model_name = MODEL_TYPES.get(model_type, {}).get("default_model")
    
    # Create config
    config = {"model": model_name}
    
    # Initialize client manager
    await client_manager.start()
    
    # Register client
    success = await client_manager.register_client(
        client_id=client_id,
        client_type=model_type,
        config=config
    )
    
    return success

async def deregister_client(client_id: str) -> bool:
    """
    Deregister a client from the memory system.
    
    Args:
        client_id: Client ID to deregister
        
    Returns:
        True if successful
    """
    # Initialize client manager
    await client_manager.start()
    
    # Deregister client
    return await client_manager.deregister_client(client_id)

async def list_clients() -> List[Dict[str, Any]]:
    """
    List all registered clients.
    
    Returns:
        List of clients with their details
    """
    # Initialize client manager
    await client_manager.start()
    
    # Get client list
    clients = []
    with client_manager.lock:
        for client_id, info in client_manager.active_clients.items():
            client_info = await client_manager.get_client_info(client_id)
            if client_info:
                clients.append(client_info)
    
    return clients

async def launch_ollama(client_id: str, model_name: str) -> None:
    """
    Launch Ollama client.
    
    Args:
        client_id: Client ID
        model_name: Ollama model to use
    """
    # Register client (this will automatically start Ollama server if needed)
    logger.info(f"Launching Ollama with model {model_name}")
    success = await register_client("ollama", client_id, model_name)
    
    if success:
        logger.info(f"Ollama client registered successfully with ID: {client_id}")
        logger.info(f"Model: {model_name}")
        logger.info(f"Run your app/UI that connects to Ollama at {settings.ollama_base_url}")
        logger.info("Ollama is now managed by Tekton with full memory integration.")
        logger.info("Press Ctrl+C to stop.")
        
        # Keep the script running while waiting for signals
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            await deregister_client(client_id)
            logger.info("Ollama client deregistered. Goodbye!")
    else:
        logger.error(f"Failed to register Ollama client")

async def launch_claude(client_id: str, model_name: str) -> None:
    """
    Launch Claude client.
    
    Args:
        client_id: Client ID
        model_name: Claude model to use
    """
    # Check if Anthropic API key is set
    if not settings.has_anthropic:
        logger.error("Anthropic API key not configured. Please set ANTHROPIC_API_KEY in your environment.")
        return
    
    # Register client
    logger.info(f"Launching Claude with model {model_name}")
    success = await register_client("claude", client_id, model_name)
    
    if success:
        logger.info(f"Claude client registered successfully with ID: {client_id}")
        logger.info(f"Model: {model_name}")
        logger.info("Claude is now managed by Tekton with full memory integration.")
        logger.info("Press Ctrl+C to stop.")
        
        # Keep the script running while waiting for signals
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            await deregister_client(client_id)
            logger.info("Claude client deregistered. Goodbye!")
    else:
        logger.error(f"Failed to register Claude client")

async def launch_openai(client_id: str, model_name: str) -> None:
    """
    Launch OpenAI client.
    
    Args:
        client_id: Client ID
        model_name: OpenAI model to use
    """
    # Check if OpenAI API key is set
    if not settings.has_openai:
        logger.error("OpenAI API key not configured. Please set OPENAI_API_KEY in your environment.")
        return
    
    # Register client
    logger.info(f"Launching OpenAI with model {model_name}")
    success = await register_client("openai", client_id, model_name)
    
    if success:
        logger.info(f"OpenAI client registered successfully with ID: {client_id}")
        logger.info(f"Model: {model_name}")
        logger.info("OpenAI is now managed by Tekton with full memory integration.")
        logger.info("Press Ctrl+C to stop.")
        
        # Keep the script running while waiting for signals
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            await deregister_client(client_id)
            logger.info("OpenAI client deregistered. Goodbye!")
    else:
        logger.error(f"Failed to register OpenAI client")

async def launch_claudecode(client_id: str, model_name: str) -> None:
    """
    Launch Claude Code client.
    
    Args:
        client_id: Client ID
        model_name: Claude model to use for Claude Code
    """
    # Check if Anthropic API key is set
    if not settings.has_anthropic:
        logger.error("Anthropic API key not configured. Please set ANTHROPIC_API_KEY in your environment.")
        return
    
    # Register client
    logger.info(f"Launching Claude Code with model {model_name}")
    success = await register_client("claudecode", client_id, model_name)
    
    if success:
        logger.info(f"Claude Code client registered successfully with ID: {client_id}")
        logger.info(f"Model: {model_name}")
        
        # Tell user how to install Claude Code CLI
        logger.info("\nTo use Claude Code with Tekton memory integration:")
        logger.info("1. Install Claude Code CLI: pip install claude-api-cli")
        logger.info("2. Set ANTHROPIC_API_KEY in your environment")
        logger.info("3. Run: claude-cli")
        logger.info("\nClaude Code is now managed by Tekton with full memory integration.")
        logger.info("Press Ctrl+C to stop.")
        
        # Keep the script running while waiting for signals
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            await deregister_client(client_id)
            logger.info("Claude Code client deregistered. Goodbye!")
    else:
        logger.error(f"Failed to register Claude Code client")

def print_client_list(clients: List[Dict[str, Any]]) -> None:
    """
    Print a formatted list of clients.
    
    Args:
        clients: List of client information dictionaries
    """
    if not clients:
        print("No active clients registered.")
        return
    
    print("\nActive Tekton Clients:")
    print("----------------------")
    for client in clients:
        print(f"Client ID: {client['id']}")
        print(f"Type: {client['type']}")
        print(f"Model: {client['config'].get('model', 'Not specified')}")
        print(f"Registered at: {client['registered_at']}")
        print(f"Last active: {client['last_active']}")
        print("----------------------")

def main():
    """Main function for the Tekton client launcher."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Tekton Client - Unified launcher for AI models and services")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Common arguments for all model clients
    model_parent = argparse.ArgumentParser(add_help=False)
    model_parent.add_argument("--id", type=str, help="Client ID (defaults to model type)")
    
    # Ollama command
    ollama_parser = subparsers.add_parser("ollama", parents=[model_parent], help=MODEL_TYPES["ollama"]["description"])
    ollama_parser.add_argument("--model", type=str, default=MODEL_TYPES["ollama"]["default_model"], help="Ollama model to use")
    
    # Claude command
    claude_parser = subparsers.add_parser("claude", parents=[model_parent], help=MODEL_TYPES["claude"]["description"])
    claude_parser.add_argument("--model", type=str, default=MODEL_TYPES["claude"]["default_model"], help="Claude model to use")
    
    # OpenAI command
    openai_parser = subparsers.add_parser("openai", parents=[model_parent], help=MODEL_TYPES["openai"]["description"])
    openai_parser.add_argument("--model", type=str, default=MODEL_TYPES["openai"]["default_model"], help="OpenAI model to use")
    
    # Claude Code command
    claudecode_parser = subparsers.add_parser("claudecode", parents=[model_parent], help=MODEL_TYPES["claudecode"]["description"])
    claudecode_parser.add_argument("--model", type=str, default=MODEL_TYPES["claudecode"]["default_model"], help="Claude model to use for Claude Code")
    
    # List command
    subparsers.add_parser("list", help="List all registered clients")
    
    # Status command
    subparsers.add_parser("status", help="Show Tekton memory system status")
    
    # Help command
    help_parser = subparsers.add_parser("help", help="Show detailed help for a specific command")
    help_parser.add_argument("topic", nargs="?", choices=list(MODEL_TYPES.keys()) + ["all"], default="all", help="Help topic")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize database if needed
    db_path = settings.database_url.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        print("Initializing Tekton database...")
        init_db()
    
    # Run the selected command
    if args.command == "ollama":
        client_id = args.id or "ollama_default"
        asyncio.run(launch_ollama(client_id, args.model))
    
    elif args.command == "claude":
        client_id = args.id or "claude_default"
        asyncio.run(launch_claude(client_id, args.model))
    
    elif args.command == "openai":
        client_id = args.id or "openai_default"
        asyncio.run(launch_openai(client_id, args.model))
    
    elif args.command == "claudecode":
        client_id = args.id or "claudecode_default"
        asyncio.run(launch_claudecode(client_id, args.model))
    
    elif args.command == "list":
        clients = asyncio.run(list_clients())
        print_client_list(clients)
    
    elif args.command == "status":
        print("Tekton Memory System Status:")
        print(f"- Database path: {db_path}")
        print(f"- Vector store path: {settings.vector_db_path}")
        print(f"- Data directory: {settings.data_dir}")
        print(f"- Tekton home: {settings.tekton_home}")
        
        # Show clients
        clients = asyncio.run(list_clients())
        if clients:
            print(f"- Active clients: {len(clients)}")
        else:
            print("- No active clients")
            
        # Show services
        if settings.has_ollama:
            print("- Ollama service: Available")
        else:
            print("- Ollama service: Not available")
            
        if settings.has_anthropic:
            print("- Anthropic service: Available")
        else:
            print("- Anthropic service: Not available")
            
        if settings.has_openai:
            print("- OpenAI service: Available")
        else:
            print("- OpenAI service: Not available")
    
    elif args.command == "help":
        if args.topic == "all":
            print("Tekton Client - Unified launcher for AI models and services")
            print("\nAvailable commands:")
            
            for model_type, info in MODEL_TYPES.items():
                print(f"  {model_type}: {info['description']}")
                print(f"    Example: tekton_client {model_type} --model {info['default_model']}")
            
            print(f"  list: List all registered clients")
            print(f"  status: Show Tekton memory system status")
            print(f"  help: Show detailed help for a specific command")
            print("\nUse tekton_client help <command> for more information on a specific command.")
        else:
            # Show help for a specific command
            info = MODEL_TYPES.get(args.topic)
            if info:
                print(f"{args.topic.capitalize()}: {info['description']}")
                print(f"Example: tekton_client {args.topic} --model {info['default_model']}")
                
                if "models" in info:
                    print("\nAvailable models:")
                    for model in info["models"]:
                        print(f"  - {model}")
            else:
                print(f"No help available for {args.topic}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    # Setup signal handling
    def signal_handler(sig, frame):
        print("\nReceived interrupt signal, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    main()