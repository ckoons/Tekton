"""
Structured output parsers for LLM responses.

This module provides utilities for parsing structured outputs from LLMs,
such as JSON, YAML, and other formats.
"""

import re
import json
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Type, TypeVar, Generic, cast

from pydantic import BaseModel, ValidationError

from .json_parser import JSONParser, JSONParsingError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class OutputFormat(str, Enum):
    """Supported output formats."""
    JSON = "json"
    LIST = "list"
    KEY_VALUE = "key_value"
    MARKDOWN = "markdown"
    YAML = "yaml"

class FormatError(Exception):
    """Exception raised when output format is invalid."""
    pass

class StructuredOutputParser(Generic[T]):
    """
    Parser for structured outputs from LLMs.
    
    This class provides utilities to parse different structured output
    formats (JSON, lists, key-value pairs, etc.) with validation.
    """
    
    def __init__(self, format: OutputFormat = OutputFormat.JSON, model: Optional[Type[T]] = None):
        """
        Initialize the structured output parser.
        
        Args:
            format: Format of the output to parse
            model: Optional Pydantic model to validate against
        """
        self.format = format
        self.model = model
    
    def parse(self, text: str) -> Union[Dict[str, Any], List[Any], str, T]:
        """
        Parse structured output from an LLM response.
        
        Args:
            text: The text to parse
            
        Returns:
            Parsed output in the specified format
            
        Raises:
            FormatError: If parsing fails
        """
        try:
            # Parse the output based on the specified format
            if self.format == OutputFormat.JSON:
                result = JSONParser.parse(text)
            elif self.format == OutputFormat.LIST:
                result = self._parse_list(text)
            elif self.format == OutputFormat.KEY_VALUE:
                result = self._parse_key_value(text)
            elif self.format == OutputFormat.MARKDOWN:
                result = self._parse_markdown(text)
            elif self.format == OutputFormat.YAML:
                result = self._parse_yaml(text)
            else:
                raise FormatError(f"Unsupported format: {self.format}")
                
            # Validate against the model if provided
            if self.model is not None:
                try:
                    if isinstance(result, dict):
                        return self.model.model_validate(result)
                    elif isinstance(result, list):
                        return [self.model.model_validate(item) if isinstance(item, dict) else item for item in result]
                    else:
                        # Can't validate non-dict/list against a model
                        raise FormatError(f"Cannot validate {type(result)} against model {self.model.__name__}")
                except ValidationError as e:
                    raise FormatError(f"Validation failed: {str(e)}")
                    
            return result
            
        except JSONParsingError as e:
            # Convert JSON parsing errors to format errors
            raise FormatError(f"JSON parsing failed: {str(e)}")
        except Exception as e:
            raise FormatError(f"Error parsing {self.format}: {str(e)}")
    
    def _parse_list(self, text: str) -> List[str]:
        """
        Parse a list from an LLM response.
        
        Args:
            text: The text to parse
            
        Returns:
            List of items
            
        Raises:
            FormatError: If parsing fails
        """
        # Try to find lists with numbers (1. Item, 2. Item)
        numbered_pattern = r'(?:^|\n)\s*(\d+)\.\s+(.+?)(?=\n\s*\d+\.\s+|\n\s*$|$)'
        numbered_matches = re.findall(numbered_pattern, text, re.DOTALL)
        
        if numbered_matches:
            return [match[1].strip() for match in numbered_matches]
            
        # Try to find bullet lists (• Item, - Item, * Item)
        bullet_pattern = r'(?:^|\n)\s*[•\-\*]\s+(.+?)(?=\n\s*[•\-\*]\s+|\n\s*$|$)'
        bullet_matches = re.findall(bullet_pattern, text, re.DOTALL)
        
        if bullet_matches:
            return [match.strip() for match in bullet_matches]
            
        # Try to find newline-separated items
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) > 1:
            return lines
            
        # Try to find comma-separated items
        if ',' in text:
            return [item.strip() for item in text.split(',') if item.strip()]
            
        # If all else fails, treat the entire text as a single item
        return [text.strip()]
    
    def _parse_key_value(self, text: str) -> Dict[str, str]:
        """
        Parse key-value pairs from an LLM response.
        
        Args:
            text: The text to parse
            
        Returns:
            Dictionary of key-value pairs
            
        Raises:
            FormatError: If parsing fails
        """
        result = {}
        
        # Try to find key-value pairs in format "Key: Value"
        kv_pattern = r'(?:^|\n)\s*([^:\n]+):\s*(.+?)(?=\n\s*[^:\n]+:\s*|\n\s*$|$)'
        kv_matches = re.findall(kv_pattern, text, re.DOTALL)
        
        if kv_matches:
            for key, value in kv_matches:
                result[key.strip()] = value.strip()
            return result
            
        # Try to find key-value pairs in format "Key = Value"
        kv_equals_pattern = r'(?:^|\n)\s*([^=\n]+)=\s*(.+?)(?=\n\s*[^=\n]+=\s*|\n\s*$|$)'
        kv_equals_matches = re.findall(kv_equals_pattern, text, re.DOTALL)
        
        if kv_equals_matches:
            for key, value in kv_equals_matches:
                result[key.strip()] = value.strip()
            return result
            
        # If no patterns matched, raise an error
        raise FormatError("No key-value pairs found in the text")
    
    def _parse_markdown(self, text: str) -> Dict[str, Any]:
        """
        Parse Markdown from an LLM response.
        
        Args:
            text: The text to parse
            
        Returns:
            Dictionary with parsed Markdown structure
            
        Raises:
            FormatError: If parsing fails
        """
        result: Dict[str, Any] = {"content": text, "sections": {}}
        
        # Extract Markdown headers and their content
        header_pattern = r'(#{1,6})\s+(.+?)[\n\r]+((?:(?!#{1,6}\s+).+[\n\r]*)+)'
        headers = re.findall(header_pattern, text, re.DOTALL)
        
        if headers:
            for level, title, content in headers:
                section_key = title.strip()
                section_level = len(level)
                
                if section_level == 1:
                    # Top-level headers
                    result["sections"][section_key] = content.strip()
                elif section_level == 2:
                    # Second-level headers
                    if "subsections" not in result["sections"]:
                        result["sections"]["subsections"] = {}
                    result["sections"]["subsections"][section_key] = content.strip()
                else:
                    # All other headers are grouped by level
                    level_key = f"h{section_level}"
                    if level_key not in result["sections"]:
                        result["sections"][level_key] = {}
                    result["sections"][level_key][section_key] = content.strip()
        
        # Extract code blocks
        code_pattern = r'```([a-zA-Z0-9]*)\n(.*?)```'
        code_blocks = re.findall(code_pattern, text, re.DOTALL)
        
        if code_blocks:
            result["code_blocks"] = []
            for language, code in code_blocks:
                result["code_blocks"].append({
                    "language": language.strip() or "text",
                    "code": code.strip()
                })
        
        return result
    
    def _parse_yaml(self, text: str) -> Dict[str, Any]:
        """
        Parse YAML from an LLM response.
        
        Args:
            text: The text to parse
            
        Returns:
            Dictionary with parsed YAML data
            
        Raises:
            FormatError: If parsing fails
        """
        try:
            import yaml
            
            # Try to find YAML in code blocks
            yaml_block_pattern = r'```(?:yaml)?\s*\n?(.*?)\n?```'
            matches = re.findall(yaml_block_pattern, text, re.DOTALL)
            
            if matches:
                # Use the largest match
                yaml_text = max(matches, key=len).strip()
            else:
                # Assume the whole text is YAML
                yaml_text = text
                
            return yaml.safe_load(yaml_text)
            
        except ImportError:
            raise FormatError("YAML parsing requires pyyaml library")
        except Exception as e:
            raise FormatError(f"YAML parsing failed: {str(e)}")