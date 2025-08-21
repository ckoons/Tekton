"""
MCP Message - Core message format for multimodal information processing.

This module defines the standardized message format and validation for
multimodal information processing in the MCP protocol.
"""

import json
import uuid
import time
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Type, cast

logger = logging.getLogger(__name__)

class MCPContentType(str, Enum):
    """Types of content in MCP messages."""
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    STRUCTURED = "structured"
    AUDIO = "audio"
    VIDEO = "video"
    CANVAS = "canvas"
    FILE = "file"


class MCPContentItem:
    """
    Content item in an MCP message.
    
    This class represents a single content item in an MCP message,
    which may be text, code, an image, or structured data.
    """
    
    def __init__(
        self,
        content_type: Union[MCPContentType, str],
        data: Any,
        format: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a content item.
        
        Args:
            content_type: Type of content
            data: Content data
            format: Content format (e.g., MIME type)
            metadata: Additional metadata
        """
        self.type = content_type if isinstance(content_type, str) else content_type.value
        self.data = data
        self.format = format or self._default_format_for_type(self.type)
        self.metadata = metadata or {}
    
    def _default_format_for_type(self, content_type: str) -> str:
        """
        Get the default format for a content type.
        
        Args:
            content_type: Content type
            
        Returns:
            Default format for the content type
        """
        defaults = {
            "text": "text/plain",
            "code": "text/plain",
            "image": "image/png",
            "structured": "application/json",
            "audio": "audio/mp3",
            "video": "video/mp4",
            "canvas": "image/svg+xml",
            "file": "application/octet-stream"
        }
        return defaults.get(content_type, "application/octet-stream")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the content item to a dictionary.
        
        Returns:
            Dictionary representation of the content item
        """
        return {
            "type": self.type,
            "format": self.format,
            "data": self.data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPContentItem":
        """
        Create a content item from a dictionary.
        
        Args:
            data: Dictionary representation of a content item
            
        Returns:
            MCPContentItem instance
        """
        return cls(
            content_type=data.get("type", "text"),
            data=data.get("data", ""),
            format=data.get("format"),
            metadata=data.get("metadata")
        )


class MCPMessage:
    """
    Standard message format for multimodal information processing.
    
    This class represents a message in the MCP protocol, providing
    methods for construction, serialization, and validation.
    """
    
    def __init__(
        self,
        content: List[Union[MCPContentItem, Dict[str, Any]]],
        source: Dict[str, Any],
        destination: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        processing: Optional[Dict[str, Any]] = None,
        security: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None
    ):
        """
        Initialize an MCP message.
        
        Args:
            content: List of content items
            source: Information about the message source
            destination: Information about the message destination
            context: Message context information
            processing: Processing instructions
            security: Security information
            message_id: Unique message identifier
        """
        self.id = message_id or f"msg-{uuid.uuid4()}"
        self.version = "mcp/1.0"
        self.timestamp = time.time()
        
        # Convert content items to MCPContentItem objects if needed
        self.content = []
        for item in content:
            if isinstance(item, dict):
                self.content.append(MCPContentItem.from_dict(item))
            else:
                self.content.append(item)
                
        self.source = source
        self.destination = destination or {}
        self.context = context or {}
        self.processing = processing or {
            "priority": "normal",
            "timeout": 30000
        }
        self.security = security or {
            "access_level": "user",
            "encryption": "none",
            "authentication": "session"
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.
        
        Returns:
            Dictionary representation of the message
        """
        return {
            "id": self.id,
            "version": self.version,
            "timestamp": self.timestamp,
            "source": self.source,
            "destination": self.destination,
            "context": self.context,
            "content": [item.to_dict() for item in self.content],
            "processing": self.processing,
            "security": self.security
        }
    
    def to_json(self) -> str:
        """
        Convert the message to a JSON string.
        
        Returns:
            JSON representation of the message
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPMessage":
        """
        Create a message from a dictionary.
        
        Args:
            data: Dictionary representation of a message
            
        Returns:
            MCPMessage instance
        """
        return cls(
            message_id=data.get("id"),
            content=data.get("content", []),
            source=data.get("source", {}),
            destination=data.get("destination"),
            context=data.get("context"),
            processing=data.get("processing"),
            security=data.get("security")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "MCPMessage":
        """
        Create a message from a JSON string.
        
        Args:
            json_str: JSON representation of a message
            
        Returns:
            MCPMessage instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def add_content(self, content_item: Union[MCPContentItem, Dict[str, Any]]) -> None:
        """
        Add a content item to the message.
        
        Args:
            content_item: Content item to add
        """
        if isinstance(content_item, dict):
            self.content.append(MCPContentItem.from_dict(content_item))
        else:
            self.content.append(content_item)
    
    def get_content_by_type(self, content_type: Union[MCPContentType, str]) -> List[MCPContentItem]:
        """
        Get content items of a specific type.
        
        Args:
            content_type: Content type to filter by
            
        Returns:
            List of matching content items
        """
        type_str = content_type if isinstance(content_type, str) else content_type.value
        return [item for item in self.content if item.type == type_str]
    
    def create_response(
        self,
        content: List[Union[MCPContentItem, Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None
    ) -> "MCPResponse":
        """
        Create a response to this message.
        
        Args:
            content: Response content items
            context: Response context (merged with original context)
            
        Returns:
            Response message
        """
        # Merge contexts
        merged_context = self.context.copy()
        if context:
            merged_context.update(context)
            
        # Swap source and destination
        source = {
            "component": self.destination.get("component", "unknown"),
            "session": self.context.get("session_id")
        }
        
        destination = {
            "component": self.source.get("component", "unknown")
        }
        
        return MCPResponse(
            content=content,
            source=source,
            destination=destination,
            context=merged_context,
            in_response_to=self.id
        )


class MCPResponse(MCPMessage):
    """
    Response message in the MCP protocol.
    
    This class represents a response to an MCP message, extending
    the standard MCPMessage class with response-specific fields.
    """
    
    def __init__(
        self,
        content: List[Union[MCPContentItem, Dict[str, Any]]],
        source: Dict[str, Any],
        destination: Dict[str, Any],
        context: Dict[str, Any],
        in_response_to: str,
        message_id: Optional[str] = None,
        processing: Optional[Dict[str, Any]] = None,
        security: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an MCP response.
        
        Args:
            content: List of content items
            source: Information about the response source
            destination: Information about the response destination
            context: Response context information
            in_response_to: ID of the message this is a response to
            message_id: Unique message identifier
            processing: Processing instructions
            security: Security information
        """
        super().__init__(
            content=content,
            source=source,
            destination=destination,
            context=context,
            processing=processing,
            security=security,
            message_id=message_id
        )
        self.in_response_to = in_response_to
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the response to a dictionary.
        
        Returns:
            Dictionary representation of the response
        """
        data = super().to_dict()
        data["in_response_to"] = self.in_response_to
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPResponse":
        """
        Create a response from a dictionary.
        
        Args:
            data: Dictionary representation of a response
            
        Returns:
            MCPResponse instance
        """
        if "in_response_to" not in data:
            raise ValueError("MCP response must include in_response_to field")
            
        return cls(
            message_id=data.get("id"),
            content=data.get("content", []),
            source=data.get("source", {}),
            destination=data.get("destination", {}),
            context=data.get("context", {}),
            in_response_to=data["in_response_to"],
            processing=data.get("processing"),
            security=data.get("security")
        )


def validate_message(message: Dict[str, Any]) -> bool:
    """
    Validate an MCP message against the protocol schema.
    
    Args:
        message: Message dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Check required fields
    required_fields = ["id", "version", "source", "content"]
    for field in required_fields:
        if field not in message:
            logger.error(f"Missing required field in MCP message: {field}")
            return False
            
    # Check source format
    source = message.get("source", {})
    if not isinstance(source, dict):
        logger.error("Invalid source format in MCP message")
        return False
        
    # Check content format
    content = message.get("content", [])
    if not isinstance(content, list) or not content:
        logger.error("Invalid content format in MCP message")
        return False
        
    for item in content:
        if not isinstance(item, dict) or "type" not in item or "data" not in item:
            logger.error("Invalid content item in MCP message")
            return False
            
        # Check content type
        content_type = item.get("type", "")
        valid_types = [t.value for t in MCPContentType]
        if content_type not in valid_types:
            logger.error(f"Invalid content type in MCP message: {content_type}")
            return False
            
    return True