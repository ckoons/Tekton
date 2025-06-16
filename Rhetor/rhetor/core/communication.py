"""Communication engine for Rhetor.

This module provides tools for managing communication between AI components
and creating standardized message formats.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class Message:
    """A standardized message format for AI communication."""
    
    def __init__(
        self,
        content: str,
        sender: str,
        recipient: Optional[str] = None,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        references: Optional[List[str]] = None
    ):
        """Initialize a message.
        
        Args:
            content: The message content
            sender: The component that sent the message
            recipient: The component that should receive the message (None for broadcast)
            message_type: The type of message (text, command, system, etc.)
            metadata: Additional metadata for the message
            message_id: Unique identifier for the message
            conversation_id: ID of the conversation this message is part of
            timestamp: Message timestamp (defaults to current time)
            references: IDs of messages this message references
        """
        self.content = content
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.metadata = metadata or {}
        self.message_id = message_id or str(uuid.uuid4())
        self.conversation_id = conversation_id
        self.timestamp = timestamp or datetime.now().timestamp()
        self.references = references or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return {
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
            "references": self.references,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create a message from a dictionary."""
        return cls(
            content=data["content"],
            sender=data["sender"],
            recipient=data.get("recipient"),
            message_type=data.get("message_type", "text"),
            metadata=data.get("metadata", {}),
            message_id=data.get("message_id"),
            conversation_id=data.get("conversation_id"),
            timestamp=data.get("timestamp"),
            references=data.get("references", [])
        )


class Conversation:
    """A conversation between AI components."""
    
    def __init__(
        self,
        conversation_id: Optional[str] = None,
        participants: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            participants: List of participant components
            metadata: Additional metadata for the conversation
        """
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.participants = participants or []
        self.metadata = metadata or {}
        self.messages: List[Message] = []
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        # Set the conversation ID on the message if not set
        if not message.conversation_id:
            message.conversation_id = self.conversation_id
        
        # Add sender to participants if not already included
        if message.sender not in self.participants:
            self.participants.append(message.sender)
        
        # Add recipient to participants if specified and not already included
        if message.recipient and message.recipient not in self.participants:
            self.participants.append(message.recipient)
        
        # Add the message and update timestamp
        self.messages.append(message)
        self.updated_at = datetime.now().timestamp()
    
    def get_messages(
        self, 
        limit: Optional[int] = None, 
        participant: Optional[str] = None,
        message_type: Optional[str] = None
    ) -> List[Message]:
        """Get messages from the conversation.
        
        Args:
            limit: Maximum number of messages to return
            participant: Filter by participant (sender or recipient)
            message_type: Filter by message type
            
        Returns:
            List of messages matching the filters
        """
        messages = self.messages
        
        # Apply filters
        if participant:
            messages = [
                m for m in messages 
                if m.sender == participant or m.recipient == participant
            ]
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        # Apply limit
        if limit and limit > 0:
            messages = messages[-limit:]
        
        return messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the conversation to a dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "participants": self.participants,
            "metadata": self.metadata,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create a conversation from a dictionary."""
        conversation = cls(
            conversation_id=data["conversation_id"],
            participants=data.get("participants", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps
        conversation.created_at = data.get("created_at", conversation.created_at)
        conversation.updated_at = data.get("updated_at", conversation.updated_at)
        
        # Add messages
        for message_data in data.get("messages", []):
            conversation.messages.append(Message.from_dict(message_data))
        
        return conversation


class CommunicationEngine:
    """Engine for managing AI communication."""
    
    def __init__(self, component_name: str = "rhetor"):
        """Initialize the communication engine.
        
        Args:
            component_name: Name of this component
        """
        self.component_name = component_name
        self.conversations: Dict[str, Conversation] = {}
        self.message_handlers: Dict[str, List[callable]] = {}
        self._message_queue = asyncio.Queue()
        self._running = False
    
    def create_conversation(
        self, 
        participants: List[str], 
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new conversation.
        
        Args:
            participants: List of participant components
            conversation_id: Optional ID for the conversation
            metadata: Optional metadata for the conversation
            
        Returns:
            The conversation ID
        """
        # Ensure this component is a participant
        if self.component_name not in participants:
            participants.append(self.component_name)
        
        # Create the conversation
        conversation = Conversation(
            conversation_id=conversation_id,
            participants=participants,
            metadata=metadata
        )
        
        # Store and return the ID
        self.conversations[conversation.conversation_id] = conversation
        return conversation.conversation_id
    
    def add_message_handler(self, message_type: str, handler: callable) -> None:
        """Add a handler for a message type.
        
        Args:
            message_type: The type of message to handle
            handler: The handler function
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    def send_message(
        self,
        content: str,
        recipient: Optional[str] = None,
        conversation_id: Optional[str] = None,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None
    ) -> Message:
        """Send a message.
        
        Args:
            content: The message content
            recipient: The recipient component
            conversation_id: ID of the conversation
            message_type: Type of message
            metadata: Additional metadata
            references: Referenced message IDs
            
        Returns:
            The created message
        """
        # Create the message
        message = Message(
            content=content,
            sender=self.component_name,
            recipient=recipient,
            message_type=message_type,
            metadata=metadata,
            conversation_id=conversation_id,
            references=references
        )
        
        # Add to conversation or create a new one
        if conversation_id and conversation_id in self.conversations:
            self.conversations[conversation_id].add_message(message)
        elif conversation_id:
            # Create conversation with the specified ID
            participants = [self.component_name]
            if recipient:
                participants.append(recipient)
            self.create_conversation(participants, conversation_id)
            self.conversations[conversation_id].add_message(message)
        else:
            # Create a new conversation
            participants = [self.component_name]
            if recipient:
                participants.append(recipient)
            new_id = self.create_conversation(participants)
            self.conversations[new_id].add_message(message)
            message.conversation_id = new_id
        
        # Queue the message for processing
        asyncio.create_task(self._message_queue.put(message))
        
        return message
    
    async def start_processing(self) -> None:
        """Start processing messages."""
        self._running = True
        while self._running:
            message = await self._message_queue.get()
            await self._process_message(message)
            self._message_queue.task_done()
    
    async def _process_message(self, message: Message) -> None:
        """Process a message.
        
        Args:
            message: The message to process
        """
        # Check if we have handlers for this message type
        handlers = self.message_handlers.get(message.message_type, [])
        
        # Add handlers for "all" message types
        handlers.extend(self.message_handlers.get("all", []))
        
        # If this message is not for us, ignore it
        if message.recipient and message.recipient != self.component_name:
            return
        
        # Process the message with each handler
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Error processing message {message.message_id}: {e}")
    
    def stop_processing(self) -> None:
        """Stop processing messages."""
        self._running = False
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def get_conversation_history(
        self, 
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get the history of a conversation.
        
        Args:
            conversation_id: The conversation ID
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in dictionary format
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        messages = conversation.get_messages(limit=limit)
        return [m.to_dict() for m in messages]
    
    def save_conversations(self, directory: str) -> None:
        """Save all conversations to a directory.
        
        Args:
            directory: The directory to save to
        """
        os.makedirs(directory, exist_ok=True)
        
        for conversation_id, conversation in self.conversations.items():
            file_path = os.path.join(directory, f"{conversation_id}.json")
            with open(file_path, 'w') as f:
                json.dump(conversation.to_dict(), f, indent=2)
    
    def load_conversations(self, directory: str) -> None:
        """Load conversations from a directory.
        
        Args:
            directory: The directory to load from
        """
        if not os.path.exists(directory):
            logger.warning(f"Conversations directory {directory} does not exist")
            return
        
        for filename in os.listdir(directory):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                conversation = Conversation.from_dict(data)
                self.conversations[conversation.conversation_id] = conversation
                logger.info(f"Loaded conversation {conversation.conversation_id}")
            except Exception as e:
                logger.error(f"Error loading conversation from {file_path}: {e}")
    
    async def register_with_hermes(self, service_registry=None) -> bool:
        """Register the communication engine with the Hermes service registry.
        
        Args:
            service_registry: Optional service registry instance
            
        Returns:
            Success status
        """
        try:
            # Try to import the service registry if not provided
            if service_registry is None:
                try:
                    from hermes.core.service_discovery import ServiceRegistry
                    service_registry = ServiceRegistry()
                    await service_registry.start()
                except ImportError:
                    logger.error("Could not import Hermes ServiceRegistry")
                    return False
            
            # Register the communication service
            success = await service_registry.register(
                service_id=f"rhetor-communication-{self.component_name}",
                name=f"Rhetor Communication ({self.component_name})",
                version="0.1.0",
                capabilities=["messaging", "conversations"],
                metadata={
                    "component": self.component_name,
                    "conversations": len(self.conversations)
                }
            )
            
            if success:
                logger.info(f"Registered communication engine for {self.component_name}")
            else:
                logger.warning(f"Failed to register communication engine")
            
            return success
        
        except Exception as e:
            logger.error(f"Error registering with Hermes: {e}")
            return False