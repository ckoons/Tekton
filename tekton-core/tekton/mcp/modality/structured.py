"""
Structured Data Processor - Processor for structured data content.

This module provides a processor for structured data content in the MCP protocol.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union

from tekton.mcp.message import MCPContentItem
from tekton.mcp.modality.base import ModalityProcessor

logger = logging.getLogger(__name__)

class StructuredDataProcessor(ModalityProcessor):
    """
    Processor for structured data content.
    
    This class provides methods for processing and validating
    structured data content in the MCP protocol.
    """
    
    def __init__(self):
        """Initialize the structured data processor."""
        super().__init__()
        logger.info("Structured data processor initialized")
    
    async def process(
        self,
        content_item: MCPContentItem,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a structured data content item.
        
        Args:
            content_item: Structured data content item to process
            context: Processing context
            
        Returns:
            Processing result
        """
        # Validate content item
        if not await self.validate(content_item):
            return {
                "error": "Invalid structured data content item",
                "processed": False
            }
            
        # Extract structured data
        data = content_item.data
        
        # Ensure data is parsed if it's a JSON string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return {
                    "error": "Invalid JSON data",
                    "processed": False
                }
        
        # Process the structured data
        # For now, just do basic analysis; this would normally involve
        # more sophisticated schema validation and analysis
        
        # Create processed result
        processed_result = {
            "original_data": data,
            "analysis": {
                "structure": self._analyze_structure(data),
                "schema": self._derive_schema(data),
                "summary": self._generate_summary(data)
            },
            "processed": True
        }
        
        return processed_result
    
    async def validate(self, content_item: MCPContentItem) -> bool:
        """
        Validate a structured data content item.
        
        Args:
            content_item: Content item to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check content type
        if content_item.type != "structured":
            logger.warning(f"Invalid content type for structured data processor: {content_item.type}")
            return False
            
        # Check data format
        if not isinstance(content_item.data, (dict, list, str)):
            logger.warning("Invalid data format for structured data processor")
            return False
            
        # If data is a string, try to parse as JSON
        if isinstance(content_item.data, str):
            try:
                json.loads(content_item.data)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON string data")
                return False
            
        # Check content format (MIME type)
        valid_formats = self.get_supported_formats()
        if content_item.format not in valid_formats:
            logger.warning(f"Unsupported format for structured data processor: {content_item.format}")
            # Still return True as we can process most structured data formats regardless
            
        return True
    
    def get_supported_formats(self) -> List[str]:
        """
        Get the formats supported by this processor.
        
        Returns:
            List of supported format strings
        """
        return [
            "application/json",
            "application/ld+json",
            "application/x-yaml",
            "application/xml",
            "text/csv"
        ]
    
    def _analyze_structure(self, data: Union[Dict[str, Any], List[Any]]) -> Dict[str, Any]:
        """
        Analyze the structure of structured data.
        
        Args:
            data: Structured data to analyze
            
        Returns:
            Structure analysis result
        """
        # Determine type
        data_type = type(data).__name__
        
        if isinstance(data, dict):
            # Analyze dictionary
            return {
                "type": "object",
                "keys": list(data.keys()),
                "key_count": len(data),
                "top_level_types": {k: type(v).__name__ for k, v in data.items()}
            }
        elif isinstance(data, list):
            # Analyze list
            return {
                "type": "array",
                "length": len(data),
                "item_types": [type(item).__name__ for item in data[:10]]  # First 10 items
            }
        else:
            # Should not reach here due to validation
            return {
                "type": data_type,
                "error": "Unsupported data type"
            }
    
    def _derive_schema(self, data: Union[Dict[str, Any], List[Any]]) -> Dict[str, Any]:
        """
        Derive a schema from structured data.
        
        Args:
            data: Structured data to analyze
            
        Returns:
            Derived schema
        """
        # In a real implementation, this would derive a more complete schema
        # For now, just generate a basic schema
        
        if isinstance(data, dict):
            properties = {}
            for key, value in data.items():
                properties[key] = self._get_property_schema(value)
                
            return {
                "type": "object",
                "properties": properties,
                "required": list(data.keys())
            }
        elif isinstance(data, list):
            if data:
                # Sample the first item for array item schema
                item_schema = self._get_property_schema(data[0])
            else:
                item_schema = {"type": "unknown"}
                
            return {
                "type": "array",
                "items": item_schema
            }
        else:
            # Should not reach here due to validation
            return {"type": "unknown"}
    
    def _get_property_schema(self, value: Any) -> Dict[str, Any]:
        """
        Get a schema for a property value.
        
        Args:
            value: Property value to analyze
            
        Returns:
            Property schema
        """
        if isinstance(value, dict):
            return {"type": "object"}
        elif isinstance(value, list):
            return {"type": "array"}
        elif isinstance(value, str):
            return {"type": "string"}
        elif isinstance(value, int):
            return {"type": "integer"}
        elif isinstance(value, float):
            return {"type": "number"}
        elif isinstance(value, bool):
            return {"type": "boolean"}
        elif value is None:
            return {"type": "null"}
        else:
            return {"type": type(value).__name__}
    
    def _generate_summary(self, data: Union[Dict[str, Any], List[Any]]) -> str:
        """
        Generate a summary of structured data.
        
        Args:
            data: Structured data to analyze
            
        Returns:
            Generated summary
        """
        # In a real implementation, this would generate a more informative summary
        # For now, just provide basic information
        
        if isinstance(data, dict):
            if "type" in data and "name" in data:
                return f"{data.get('type', 'Object')} named '{data.get('name', 'unknown')}'"
            elif "id" in data and "name" in data:
                return f"Object with ID {data.get('id')} named '{data.get('name', 'unknown')}'"
            else:
                return f"Object with {len(data)} properties"
        elif isinstance(data, list):
            if len(data) == 0:
                return "Empty array"
            elif all(isinstance(item, dict) for item in data):
                # Check for common identifying fields in list of objects
                if all("id" in item for item in data):
                    return f"Array of {len(data)} objects with IDs"
                elif all("name" in item for item in data):
                    return f"Array of {len(data)} named objects"
                else:
                    return f"Array of {len(data)} objects"
            else:
                return f"Array of {len(data)} items"
        else:
            # Should not reach here due to validation
            return "Unknown structured data"