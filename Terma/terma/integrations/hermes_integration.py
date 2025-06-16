"""Integration with Hermes message bus"""

import json
import logging
import asyncio
import aiohttp
import requests
from typing import Dict, Any, Optional, List, Callable, Awaitable
from ..core.session_manager import SessionManager
from ..utils.logging import setup_logging

logger = setup_logging()

class HermesIntegration:
    """Handles integration with the Hermes message bus for terminal operations"""
    
    def __init__(self, api_url=None, session_manager=None, component_name="Terma"):
        """Initialize the Hermes integration
        
        Args:
            api_url: URL of the Hermes API
            session_manager: SessionManager instance to manage terminal sessions
            component_name: Name of this component
        """
        self.api_url = api_url or "http://localhost:8000"
        self.session_manager = session_manager
        self.component_name = component_name
        self.capabilities = self._get_capabilities()
        self.handlers = self._setup_handlers()
        self.is_registered = False
        self.heartbeat_task = None
        self.event_subscribers = {}
    
    def _get_capabilities(self) -> List[Dict[str, Any]]:
        """Get the capabilities for Terma
        
        Returns:
            List of capability definitions
        """
        return [
            {
                "name": "terminal.create",
                "description": "Create a new terminal session",
                "parameters": {
                    "shell_command": {
                        "type": "string",
                        "description": "Optional shell command to run",
                        "required": False
                    }
                },
                "returns": {
                    "session_id": {
                        "type": "string",
                        "description": "ID of the created session"
                    }
                }
            },
            {
                "name": "terminal.close",
                "description": "Close a terminal session",
                "parameters": {
                    "session_id": {
                        "type": "string",
                        "description": "ID of the session to close",
                        "required": True
                    }
                },
                "returns": {
                    "status": {
                        "type": "string",
                        "description": "Operation status"
                    }
                }
            },
            {
                "name": "terminal.write",
                "description": "Write data to a terminal session",
                "parameters": {
                    "session_id": {
                        "type": "string",
                        "description": "ID of the session to write to",
                        "required": True
                    },
                    "data": {
                        "type": "string",
                        "description": "Data to write",
                        "required": True
                    }
                },
                "returns": {
                    "status": {
                        "type": "string",
                        "description": "Operation status"
                    }
                }
            },
            {
                "name": "terminal.read",
                "description": "Read data from a terminal session",
                "parameters": {
                    "session_id": {
                        "type": "string",
                        "description": "ID of the session to read from",
                        "required": True
                    }
                },
                "returns": {
                    "data": {
                        "type": "string",
                        "description": "Terminal output data"
                    }
                }
            },
            {
                "name": "terminal.list",
                "description": "List all terminal sessions",
                "parameters": {},
                "returns": {
                    "sessions": {
                        "type": "array",
                        "description": "List of session information"
                    }
                }
            },
            {
                "name": "terminal.resize",
                "description": "Resize a terminal session",
                "parameters": {
                    "session_id": {
                        "type": "string",
                        "description": "ID of the session to resize",
                        "required": True
                    },
                    "rows": {
                        "type": "integer",
                        "description": "Number of rows",
                        "required": True
                    },
                    "cols": {
                        "type": "integer",
                        "description": "Number of columns",
                        "required": True
                    }
                },
                "returns": {
                    "status": {
                        "type": "string",
                        "description": "Operation status"
                    }
                }
            }
        ]
    
    def _setup_handlers(self) -> Dict[str, Callable]:
        """Set up command handlers
        
        Returns:
            Dictionary of command handlers
        """
        return {
            "terminal.create": self._handle_create_terminal,
            "terminal.close": self._handle_close_terminal,
            "terminal.write": self._handle_write_terminal,
            "terminal.read": self._handle_read_terminal,
            "terminal.list": self._handle_list_terminals,
            "terminal.resize": self._handle_resize_terminal
        }
    
    def register_capabilities(self):
        """Register Terma capabilities with Hermes"""
        if not self.session_manager:
            logger.error("Cannot register capabilities: session_manager not set")
            return False
        
        try:
            registration_data = {
                "name": self.component_name,
                "description": "Terminal integration system for Tekton",
                "version": "0.1.0",
                "capabilities": self.capabilities,
                "endpoints": {
                    "api": "http://localhost:8765/api",
                    "websocket": "ws://localhost:8765/ws"
                }
            }
            
            # Register with Hermes
            registration_url = f"{self.api_url}/api/register"
            response = requests.post(registration_url, json=registration_data)
            
            if response.status_code == 200:
                logger.info(f"Successfully registered {self.component_name} with Hermes")
                self.is_registered = True
                # Start heartbeat
                self._start_heartbeat()
                # Subscribe to events
                self._subscribe_to_events()
                return True
            else:
                logger.error(f"Error registering with Hermes: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return False
    
    def _start_heartbeat(self):
        """Start sending heartbeat to Hermes"""
        if self.heartbeat_task and not self.heartbeat_task.done():
            return
        
        loop = asyncio.get_event_loop()
        self.heartbeat_task = loop.create_task(self._heartbeat_loop())
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat to Hermes"""
        try:
            while self.is_registered:
                await self._send_heartbeat()
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
        except asyncio.CancelledError:
            logger.info("Heartbeat task cancelled")
        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")
    
    async def _send_heartbeat(self):
        """Send a heartbeat to Hermes"""
        try:
            async with aiohttp.ClientSession() as session:
                heartbeat_url = f"{self.api_url}/api/heartbeat"
                payload = {
                    "component": self.component_name,
                    "status": "healthy",
                    "timestamp": asyncio.get_event_loop().time(),
                    "metrics": {
                        "active_sessions": len(self.session_manager.sessions) if self.session_manager else 0
                    }
                }
                
                async with session.post(heartbeat_url, json=payload) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to send heartbeat: {response.status}")
                        text = await response.text()
                        logger.warning(f"Response: {text}")
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
    
    def _subscribe_to_events(self):
        """Subscribe to events from Hermes"""
        try:
            # Subscribe to terminal-related events
            events_to_subscribe = [
                "terminal.session.created",
                "terminal.session.closed",
                "terminal.output.available",
                "terminal.command.executed"
            ]
            
            # Register event subscriptions
            subscription_url = f"{self.api_url}/api/subscribe"
            for event in events_to_subscribe:
                payload = {
                    "component": self.component_name,
                    "event": event,
                    "callback_url": f"http://localhost:8765/api/events"
                }
                
                response = requests.post(subscription_url, json=payload)
                if response.status_code == 200:
                    logger.info(f"Subscribed to event: {event}")
                else:
                    logger.warning(f"Failed to subscribe to event {event}: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error subscribing to events: {e}")
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a message from Hermes
        
        Args:
            message: The message to handle
            
        Returns:
            The response to send back
        """
        try:
            # Extract message details
            command = message.get("command")
            payload = message.get("payload", {})
            source = message.get("source", "unknown")
            message_id = message.get("id", "unknown")
            
            logger.info(f"Received message from {source} with command {command}")
            
            # Find the appropriate handler
            handler = self.handlers.get(command)
            
            if handler:
                # Execute the handler
                result = await handler(payload)
                
                # Create response
                response = {
                    "id": message_id,
                    "status": "success",
                    "source": self.component_name,
                    "target": source,
                    "response_to": command,
                    "payload": result
                }
                
                logger.info(f"Sending response for command {command}")
                return response
            else:
                # Command not supported
                logger.warning(f"Unsupported command: {command}")
                return {
                    "id": message_id,
                    "status": "error",
                    "source": self.component_name,
                    "target": source,
                    "response_to": command,
                    "error": f"Unsupported command: {command}"
                }
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {
                "id": message.get("id", "unknown"),
                "status": "error",
                "source": self.component_name,
                "target": message.get("source", "unknown"),
                "response_to": message.get("command", "unknown"),
                "error": str(e)
            }
    
    async def publish_event(self, event_name: str, payload: Dict[str, Any]):
        """Publish an event to Hermes
        
        Args:
            event_name: Name of the event
            payload: Event payload
        """
        if not self.is_registered:
            logger.warning(f"Cannot publish event {event_name}: not registered with Hermes")
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                event_url = f"{self.api_url}/api/events/publish"
                event_data = {
                    "component": self.component_name,
                    "event": event_name,
                    "payload": payload,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                async with session.post(event_url, json=event_data) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to publish event {event_name}: {response.status}")
                        text = await response.text()
                        logger.warning(f"Response: {text}")
        
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
    
    async def _handle_create_terminal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create terminal command
        
        Args:
            payload: Command payload
            
        Returns:
            Response payload
        """
        if not self.session_manager:
            return {"error": "Session manager not available"}
        
        shell_command = payload.get("shell_command")
        
        # Create session
        session_id = self.session_manager.create_session(shell_command=shell_command)
        
        if session_id:
            # Publish event
            await self.publish_event("terminal.session.created", {
                "session_id": session_id,
                "shell_command": shell_command
            })
            
            return {"session_id": session_id}
        else:
            return {"error": "Failed to create session"}
    
    async def _handle_close_terminal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle close terminal command
        
        Args:
            payload: Command payload
            
        Returns:
            Response payload
        """
        if not self.session_manager:
            return {"error": "Session manager not available"}
        
        session_id = payload.get("session_id")
        if not session_id:
            return {"error": "Missing session_id parameter"}
        
        # Close session
        success = self.session_manager.close_session(session_id)
        
        if success:
            # Publish event
            await self.publish_event("terminal.session.closed", {
                "session_id": session_id
            })
            
            return {"status": "success"}
        else:
            return {"error": f"Failed to close session {session_id}"}
    
    async def _handle_write_terminal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle write terminal command
        
        Args:
            payload: Command payload
            
        Returns:
            Response payload
        """
        if not self.session_manager:
            return {"error": "Session manager not available"}
        
        session_id = payload.get("session_id")
        data = payload.get("data")
        
        if not session_id:
            return {"error": "Missing session_id parameter"}
        if not data:
            return {"error": "Missing data parameter"}
        
        # Write to session
        success = self.session_manager.write_to_session(session_id, data)
        
        if success:
            return {"status": "success", "bytes_written": len(data)}
        else:
            return {"error": f"Failed to write to session {session_id}"}
    
    async def _handle_read_terminal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle read terminal command
        
        Args:
            payload: Command payload
            
        Returns:
            Response payload
        """
        if not self.session_manager:
            return {"error": "Session manager not available"}
        
        session_id = payload.get("session_id")
        size = payload.get("size", 1024)
        
        if not session_id:
            return {"error": "Missing session_id parameter"}
        
        # Read from session
        data = self.session_manager.read_from_session(session_id, size)
        
        if data is not None:
            return {"data": data}
        else:
            return {"error": f"Failed to read from session {session_id}"}
    
    async def _handle_list_terminals(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list terminals command
        
        Args:
            payload: Command payload
            
        Returns:
            Response payload
        """
        if not self.session_manager:
            return {"error": "Session manager not available"}
        
        # List sessions
        sessions = self.session_manager.list_sessions()
        
        return {"sessions": sessions}
    
    async def _handle_resize_terminal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resize terminal command
        
        Args:
            payload: Command payload
            
        Returns:
            Response payload
        """
        if not self.session_manager:
            return {"error": "Session manager not available"}
        
        session_id = payload.get("session_id")
        rows = payload.get("rows")
        cols = payload.get("cols")
        
        if not session_id:
            return {"error": "Missing session_id parameter"}
        if not rows or not cols:
            return {"error": "Missing rows or cols parameters"}
        
        # Resize session
        success = self.session_manager.resize_session(session_id, rows, cols)
        
        if success:
            return {"status": "success"}
        else:
            return {"error": f"Failed to resize session {session_id}"}
