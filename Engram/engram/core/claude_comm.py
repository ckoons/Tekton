#!/usr/bin/env python3
"""
Claude Communication Module

Handles Claude-to-Claude communication via a shared memory space.
Enables Claude instances to exchange messages with each other.
"""

import os
import time
import json
import uuid
import logging
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("engram.claude_comm")

class ClaudeCommunicator:
    """
    Handles communication between different Claude instances.
    Uses a shared memory space managed by the Engram memory system.
    """
    
    def __init__(self, client_id: str = "claude"):
        """
        Initialize the Claude Communicator.
        
        Args:
            client_id: Unique identifier for this Claude instance
        """
        self.client_id = client_id
        self.comm_dir = os.path.expanduser("~/.engram/communication")
        self.inbox_dir = os.path.join(self.comm_dir, f"{client_id}_inbox")
        self.outbox_dir = os.path.join(self.comm_dir, f"{client_id}_outbox")
        self.connections_file = os.path.join(self.comm_dir, "connections.json")
        
        # Initialize directories
        self._init_directories()
        
        # Register connection
        self._register_connection()
        
        logger.info(f"Claude communicator initialized for {client_id}")
    
    def _init_directories(self) -> None:
        """Initialize the communication directories."""
        os.makedirs(self.comm_dir, exist_ok=True)
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.outbox_dir, exist_ok=True)
        
        # Create connections file if it doesn't exist
        if not os.path.exists(self.connections_file):
            with open(self.connections_file, "w") as f:
                json.dump({"connections": []}, f)
    
    def _register_connection(self) -> None:
        """Register this Claude instance in the connections list."""
        try:
            # Load current connections
            connections = self._load_connections()
            
            # Check if this client is already registered
            existing = next(
                (c for c in connections if c.get("id") == self.client_id), 
                None
            )
            
            # Prepare connection data
            connection_data = {
                "id": self.client_id,
                "name": f"Claude ({self.client_id})",
                "last_seen": time.time(),
                "status": "online"
            }
            
            # Update or add
            if existing:
                for i, conn in enumerate(connections):
                    if conn.get("id") == self.client_id:
                        connections[i] = connection_data
                        break
            else:
                connections.append(connection_data)
            
            # Save connections
            self._save_connections(connections)
            
        except Exception as e:
            logger.error(f"Error registering connection: {e}")
    
    def _load_connections(self) -> List[Dict]:
        """Load the connections list."""
        try:
            with open(self.connections_file, "r") as f:
                data = json.load(f)
                return data.get("connections", [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_connections(self, connections: List[Dict]) -> None:
        """Save the connections list."""
        try:
            # Remove connections not seen in the last 24 hours
            cutoff = time.time() - (24 * 60 * 60)
            active_connections = [
                c for c in connections 
                if c.get("last_seen", 0) > cutoff or c.get("id") == self.client_id
            ]
            
            with open(self.connections_file, "w") as f:
                json.dump({"connections": active_connections}, f)
        except Exception as e:
            logger.error(f"Error saving connections: {e}")
    
    async def send_message(
        self, 
        recipient_id: str, 
        message: str, 
        metadata: Dict = None,
        attachments: Dict = None
    ) -> Dict:
        """
        Send a message to another Claude instance.
        
        Args:
            recipient_id: ID of the recipient Claude instance
            message: Message content
            metadata: Additional metadata for the message
            attachments: Any attachments to include
            
        Returns:
            Dict with message details and status
        """
        try:
            # Generate message ID
            message_id = str(uuid.uuid4())
            
            # Create recipient inbox directory if it doesn't exist
            recipient_inbox = os.path.join(self.comm_dir, f"{recipient_id}_inbox")
            os.makedirs(recipient_inbox, exist_ok=True)
            
            # Prepare message data
            message_data = {
                "id": message_id,
                "sender_id": self.client_id,
                "recipient_id": recipient_id,
                "timestamp": time.time(),
                "message": message,
                "metadata": metadata or {},
                "attachments": attachments or {},
                "read": False
            }
            
            # Save to recipient's inbox and our outbox
            message_file = os.path.join(recipient_inbox, f"{message_id}.json")
            outbox_file = os.path.join(self.outbox_dir, f"{message_id}.json")
            
            with open(message_file, "w") as f:
                json.dump(message_data, f)
                
            with open(outbox_file, "w") as f:
                json.dump(message_data, f)
            
            logger.info(f"Message sent to {recipient_id}: {message_id}")
            
            return {
                "status": "sent",
                "message_id": message_id,
                "timestamp": message_data["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_unread_messages(self, limit: int = 10) -> List[Dict]:
        """
        Get unread messages from the inbox.
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        try:
            messages = []
            
            # List files in inbox
            if not os.path.exists(self.inbox_dir):
                return []
                
            inbox_files = [
                f for f in os.listdir(self.inbox_dir) 
                if f.endswith(".json")
            ]
            
            # Sort by modification time (newest first)
            inbox_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(self.inbox_dir, f)),
                reverse=True
            )
            
            # Load messages
            for filename in inbox_files[:limit]:
                filepath = os.path.join(self.inbox_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        message = json.load(f)
                        if not message.get("read", False):
                            messages.append(message)
                            
                            # Mark as read
                            message["read"] = True
                            with open(filepath, "w") as f:
                                json.dump(message, f)
                except Exception as e:
                    logger.error(f"Error reading message file {filename}: {e}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def get_messages_from(
        self, sender_id: str, limit: int = 10, include_read: bool = False
    ) -> List[Dict]:
        """
        Get messages from a specific sender.
        
        Args:
            sender_id: ID of the sender Claude instance
            limit: Maximum number of messages to retrieve
            include_read: Whether to include already read messages
            
        Returns:
            List of messages
        """
        try:
            messages = []
            
            # List files in inbox
            if not os.path.exists(self.inbox_dir):
                return []
                
            inbox_files = [
                f for f in os.listdir(self.inbox_dir) 
                if f.endswith(".json")
            ]
            
            # Sort by modification time (newest first)
            inbox_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(self.inbox_dir, f)),
                reverse=True
            )
            
            # Load messages
            count = 0
            for filename in inbox_files:
                if count >= limit:
                    break
                    
                filepath = os.path.join(self.inbox_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        message = json.load(f)
                        if message.get("sender_id") == sender_id:
                            if include_read or not message.get("read", False):
                                messages.append(message)
                                count += 1
                                
                                # Mark as read if not already
                                if not message.get("read", False):
                                    message["read"] = True
                                    with open(filepath, "w") as f:
                                        json.dump(message, f)
                except Exception as e:
                    logger.error(f"Error reading message file {filename}: {e}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def list_connections(self) -> List[Dict]:
        """
        List all connected Claude instances.
        
        Returns:
            List of connections
        """
        try:
            # Update last seen
            self._register_connection()
            
            # Return all connections
            connections = self._load_connections()
            
            # Sort by last_seen (most recent first)
            return sorted(
                connections,
                key=lambda c: c.get("last_seen", 0),
                reverse=True
            )
            
        except Exception as e:
            logger.error(f"Error listing connections: {e}")
            return []
    
    async def get_conversation(self, conversation_id: str, limit: int = 20) -> List[Dict]:
        """
        Get messages from a specific conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages in the conversation
        """
        try:
            messages = []
            
            # Get both inbox and outbox messages
            for dir_path in [self.inbox_dir, self.outbox_dir]:
                if not os.path.exists(dir_path):
                    continue
                    
                files = [
                    f for f in os.listdir(dir_path) 
                    if f.endswith(".json")
                ]
                
                for filename in files:
                    filepath = os.path.join(dir_path, filename)
                    try:
                        with open(filepath, "r") as f:
                            message = json.load(f)
                            if message.get("metadata", {}).get("conversation_id") == conversation_id:
                                messages.append(message)
                    except Exception as e:
                        logger.error(f"Error reading message file {filename}: {e}")
            
            # Remove duplicates (messages in both inbox and outbox)
            unique_messages = {}
            for message in messages:
                message_id = message.get("id")
                if message_id not in unique_messages:
                    unique_messages[message_id] = message
            
            # Sort by timestamp (oldest first for conversations)
            sorted_messages = sorted(
                unique_messages.values(),
                key=lambda m: m.get("timestamp", 0)
            )
            
            return sorted_messages[-limit:] if limit > 0 else sorted_messages
            
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return []
    
    def status(self) -> Dict:
        """
        Get the status of the communication system.
        
        Returns:
            Status information
        """
        try:
            # Check if directories exist
            comm_exists = os.path.exists(self.comm_dir)
            inbox_exists = os.path.exists(self.inbox_dir)
            outbox_exists = os.path.exists(self.outbox_dir)
            
            if comm_exists and inbox_exists and outbox_exists:
                status = "online"
            else:
                status = "offline"
            
            # Count unread messages
            unread_count = 0
            if inbox_exists:
                for filename in os.listdir(self.inbox_dir):
                    if filename.endswith(".json"):
                        try:
                            with open(os.path.join(self.inbox_dir, filename), "r") as f:
                                message = json.load(f)
                                if not message.get("read", False):
                                    unread_count += 1
                        except:
                            pass
            
            return {
                "status": status,
                "client_id": self.client_id,
                "unread_messages": unread_count,
                "comm_dir": self.comm_dir,
                "inbox_dir": self.inbox_dir,
                "outbox_dir": self.outbox_dir
            }
            
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "client_id": self.client_id
            }
    
    def get_identity(self) -> Dict:
        """
        Get the identity of this Claude instance.
        
        Returns:
            Identity information
        """
        try:
            # Get connection details
            connections = self._load_connections()
            this_connection = next(
                (c for c in connections if c.get("id") == self.client_id),
                {"id": self.client_id, "name": f"Claude ({self.client_id})"}
            )
            
            return this_connection
            
        except Exception as e:
            logger.error(f"Error getting identity: {e}")
            return {"id": self.client_id, "name": f"Claude ({self.client_id})"}