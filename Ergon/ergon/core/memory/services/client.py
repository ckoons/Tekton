"""
Client registration and management system for Ergon's memory system.

This module provides a client registration and lifecycle management system
that allows different AI models to use Engram with proper resource management.
"""

import os
import sys
import time
import asyncio
import logging
import signal
import subprocess
import json
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
import threading
import atexit

from ergon.utils.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)

class ClientManager:
    """
    Manages client registrations and lifecycle for Engram.
    
    This class provides a way for different AI model clients to register
    with Engram, ensuring resources are only used when needed and cleaned up
    when not in use.
    """
    
    def __init__(self):
        """Initialize the client manager."""
        self.active_clients: Dict[str, Dict[str, Any]] = {}
        self.model_processes: Dict[str, Any] = {}
        self.lock = threading.RLock()
        self.cleanup_thread = None
        self.running = False
        
        # Register cleanup on exit
        atexit.register(self.shutdown)
    
    async def start(self):
        """Start the client manager and monitoring thread."""
        if self.running:
            return
            
        self.running = True
        
        # Start monitoring thread
        self.cleanup_thread = threading.Thread(target=self._monitor_clients)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        
        logger.info("Client manager started")
    
    async def register_client(self, client_id: str, client_type: str, config: Dict[str, Any] = None) -> bool:
        """
        Register a new client with Engram.
        
        Args:
            client_id: Unique identifier for the client
            client_type: Type of client (ollama, openai, anthropic, etc.)
            config: Configuration options for the client
            
        Returns:
            True if registration successful
        """
        if not self.running:
            await self.start()
            
        with self.lock:
            # Check if already registered
            if client_id in self.active_clients:
                logger.debug(f"Client already registered: {client_id}")
                # Update last active timestamp
                self.active_clients[client_id]["last_active"] = datetime.now()
                return True
                
            # Initialize resources for this client
            try:
                await self._initialize_client_resources(client_type, config or {})
                
                # Register the client
                self.active_clients[client_id] = {
                    "type": client_type,
                    "config": config or {},
                    "registered_at": datetime.now(),
                    "last_active": datetime.now(),
                    "metadata": {}
                }
                
                logger.info(f"Registered client: {client_id} (type: {client_type})")
                return True
            except Exception as e:
                logger.error(f"Error registering client {client_id}: {str(e)}")
                return False
    
    async def heartbeat(self, client_id: str) -> bool:
        """
        Update client heartbeat to indicate activity.
        
        Args:
            client_id: Client ID to update
            
        Returns:
            True if successful
        """
        with self.lock:
            if client_id in self.active_clients:
                self.active_clients[client_id]["last_active"] = datetime.now()
                return True
            return False
    
    async def get_client_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered client.
        
        Args:
            client_id: Client ID to get info for
            
        Returns:
            Client information or None if not registered
        """
        with self.lock:
            if client_id in self.active_clients:
                info = self.active_clients[client_id].copy()
                # Convert datetime objects to strings for easy serialization
                info["registered_at"] = info["registered_at"].isoformat()
                info["last_active"] = info["last_active"].isoformat()
                return info
            return None
    
    async def set_client_metadata(self, client_id: str, key: str, value: Any) -> bool:
        """
        Set metadata for a client.
        
        Args:
            client_id: Client ID to update
            key: Metadata key
            value: Metadata value
            
        Returns:
            True if successful
        """
        with self.lock:
            if client_id in self.active_clients:
                self.active_clients[client_id]["metadata"][key] = value
                return True
            return False
    
    async def get_client_metadata(self, client_id: str, key: str) -> Optional[Any]:
        """
        Get metadata for a client.
        
        Args:
            client_id: Client ID to get metadata for
            key: Metadata key
            
        Returns:
            Metadata value or None if not found
        """
        with self.lock:
            if client_id in self.active_clients:
                return self.active_clients[client_id]["metadata"].get(key)
            return None
    
    async def deregister_client(self, client_id: str) -> bool:
        """
        Deregister a client from Engram.
        
        Args:
            client_id: Client ID to deregister
            
        Returns:
            True if successful
        """
        with self.lock:
            if client_id in self.active_clients:
                client_type = self.active_clients[client_id]["type"]
                
                # Remove from active clients
                del self.active_clients[client_id]
                
                # Check if we should cleanup resources for this client type
                await self._cleanup_client_resources_if_unused(client_type)
                
                logger.info(f"Deregistered client: {client_id}")
                return True
            return False
    
    async def _initialize_client_resources(self, client_type: str, config: Dict[str, Any]) -> bool:
        """
        Initialize resources for a client type.
        
        Args:
            client_type: Type of client
            config: Configuration options
            
        Returns:
            True if successful
        """
        if client_type == "ollama":
            return await self._initialize_ollama(config)
        elif client_type == "openai":
            # No specific resources needed for OpenAI
            return True
        elif client_type == "anthropic":
            # No specific resources needed for Anthropic
            return True
        else:
            # No specific handling for unknown types
            return True
    
    async def _initialize_ollama(self, config: Dict[str, Any]) -> bool:
        """
        Initialize Ollama resources.
        
        This checks if Ollama is running and starts it if needed.
        
        Args:
            config: Ollama configuration options
            
        Returns:
            True if successful
        """
        # Check if Ollama is already running
        if await self._is_ollama_running():
            logger.debug("Ollama is already running")
            return True
            
        # Start Ollama if not running
        try:
            model_name = config.get("model", "llama3")
            
            # Start Ollama server
            logger.info("Starting Ollama server...")
            
            # Use Popen to start the process in the background
            cmd = ["ollama", "serve"]
            
            with self.lock:
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.model_processes["ollama"] = process
            
            # Wait for Ollama to start (max 30 seconds)
            start_time = time.time()
            while not await self._is_ollama_running():
                if time.time() - start_time > 30:
                    logger.error("Timed out waiting for Ollama to start")
                    return False
                await asyncio.sleep(1)
            
            # Pull the model if specified
            if model_name:
                logger.info(f"Pulling Ollama model: {model_name}")
                pull_cmd = ["ollama", "pull", model_name]
                subprocess.run(pull_cmd, check=True)
            
            logger.info("Ollama initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error initializing Ollama: {str(e)}")
            return False
    
    async def _is_ollama_running(self) -> bool:
        """
        Check if Ollama is running.
        
        Returns:
            True if Ollama is running
        """
        try:
            import requests
            response = requests.get(f"{settings.ollama_base_url}/api/version", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    async def _cleanup_client_resources_if_unused(self, client_type: str) -> None:
        """
        Cleanup resources for a client type if no longer in use.
        
        Args:
            client_type: Type of client
        """
        # Check if any clients of this type are still active
        with self.lock:
            active_clients_of_type = [
                cid for cid, info in self.active_clients.items() 
                if info["type"] == client_type
            ]
            
            # If there are still active clients of this type, don't cleanup
            if active_clients_of_type:
                return
                
            # Cleanup resources based on client type
            if client_type == "ollama" and "ollama" in self.model_processes:
                logger.info("No active Ollama clients, stopping Ollama server...")
                
                # Stop Ollama process
                process = self.model_processes["ollama"]
                try:
                    # Try to terminate gracefully first
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if termination doesn't work
                    process.kill()
                
                # Remove from tracked processes
                del self.model_processes["ollama"]
                logger.info("Ollama server stopped")
    
    def _monitor_clients(self) -> None:
        """
        Monitor registered clients and cleanup idle ones.
        
        This runs in a separate thread and periodically checks for
        idle clients that should be deregistered.
        """
        while self.running:
            try:
                # Check for idle clients
                with self.lock:
                    now = datetime.now()
                    idle_timeout = timedelta(minutes=30)  # 30 minute idle timeout
                    
                    # Find idle clients
                    idle_clients = [
                        cid for cid, info in self.active_clients.items()
                        if now - info["last_active"] > idle_timeout
                    ]
                
                # Deregister idle clients
                for client_id in idle_clients:
                    asyncio.run(self.deregister_client(client_id))
                    logger.info(f"Deregistered idle client: {client_id}")
                
                # Sleep for 5 minutes before checking again
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in client monitor thread: {str(e)}")
                time.sleep(60)  # Sleep a bit on error
    
    def shutdown(self) -> None:
        """
        Shutdown the client manager and cleanup all resources.
        
        This should be called when the application is shutting down.
        """
        logger.info("Shutting down client manager...")
        
        # Stop monitoring thread
        self.running = False
        
        # Terminate all managed processes
        with self.lock:
            for process_name, process in self.model_processes.items():
                try:
                    logger.info(f"Stopping {process_name} process...")
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    # Force kill if termination fails
                    try:
                        process.kill()
                    except:
                        pass
            
            # Clear active clients and processes
            self.active_clients.clear()
            self.model_processes.clear()
        
        logger.info("Client manager shutdown complete")


# Global client manager instance
client_manager = ClientManager()