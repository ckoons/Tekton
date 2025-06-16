"""
JSON parsing utilities for LLM responses.

This module provides utilities for parsing JSON from LLM responses, with
robust error handling for common issues.
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Union, TypeVar, Type, cast
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class JSONParsingError(Exception):
    """Exception raised when JSON parsing fails."""
    
    def __init__(self, message: str, content: str, partial_data: Optional[Dict[str, Any]] = None):
        """
        Initialize a JSON parsing error.
        
        Args:
            message: Error message
            content: Original content that failed to parse
            partial_data: Any partial data that was extracted
        """
        self.message = message
        self.content = content
        self.partial_data = partial_data
        super().__init__(message)

class JSONParser:
    """
    Parser for extracting and validating JSON from LLM responses.
    """
    
    @staticmethod
    def extract_json(text: str) -> str:
        """
        Extract JSON content from a string, which may include markdown or other text.
        
        Args:
            text: The text to extract JSON from
            
        Returns:
            The extracted JSON string
            
        Raises:
            JSONParsingError: If no JSON found
        """
        # Try to find JSON in a code block (```json ... ```)
        json_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(json_block_pattern, text, re.DOTALL)
        
        if matches:
            # Use the largest match as it's likely to be the main JSON object
            return max(matches, key=len).strip()
            
        # Look for JSON with curly braces if no code block found
        if '{' in text and '}' in text:
            # Find the outermost pair of curly braces
            start = text.find('{')
            
            # Find balanced closing brace
            open_count = 1
            pos = start + 1
            
            while pos < len(text) and open_count > 0:
                if text[pos] == '{':
                    open_count += 1
                elif text[pos] == '}':
                    open_count -= 1
                pos += 1
                
            if open_count == 0:
                # Found balanced braces
                return text[start:pos].strip()
        
        # No JSON found in recognized format
        raise JSONParsingError("No valid JSON content found", text)
    
    @staticmethod
    def fix_common_issues(json_str: str) -> str:
        """
        Fix common issues in JSON produced by LLMs.
        
        Args:
            json_str: JSON string to fix
            
        Returns:
            Fixed JSON string
        """
        # Remove any leading/trailing whitespace
        json_str = json_str.strip()
        
        # Fix trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Fix missing quotes around keys
        json_str = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1 "\2":', json_str)
        
        # Fix single quotes
        in_string = False
        result = []
        
        for i, char in enumerate(json_str):
            if char == '"' and (i == 0 or json_str[i-1] != '\\'):
                in_string = not in_string
                result.append(char)
            elif char == "'" and not in_string:
                result.append('"')
            else:
                result.append(char)
                
        json_str = ''.join(result)
        
        # Handle cases where LLM adds explanatory text at the beginning or end
        if not json_str.startswith('{') and not json_str.startswith('['):
            # Try to find the first occurrence of { or [
            start_idx = min(
                json_str.find('{') if json_str.find('{') != -1 else len(json_str),
                json_str.find('[') if json_str.find('[') != -1 else len(json_str)
            )
            
            if start_idx < len(json_str):
                json_str = json_str[start_idx:]
        
        # Similarly, trim anything after the JSON object/array
        if not json_str.endswith('}') and not json_str.endswith(']'):
            # Find the last occurrence of } or ]
            end_idx = max(json_str.rfind('}'), json_str.rfind(']'))
            
            if end_idx != -1:
                json_str = json_str[:end_idx+1]
        
        return json_str
    
    @staticmethod
    def parse(text: str) -> Dict[str, Any]:
        """
        Parse JSON from a string, handling common issues.
        
        Args:
            text: The text to parse
            
        Returns:
            Parsed JSON as a dictionary
            
        Raises:
            JSONParsingError: If parsing fails
        """
        try:
            # First try to parse as-is
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                # Try to extract JSON from a larger text
                json_str = JSONParser.extract_json(text)
                
                # Try parsing the extracted JSON
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # Fix common issues and try again
                    fixed_json = JSONParser.fix_common_issues(json_str)
                    return json.loads(fixed_json)
                    
            except (json.JSONDecodeError, JSONParsingError) as e:
                logger.error(f"Failed to parse JSON: {str(e)}")
                raise JSONParsingError(f"Failed to parse JSON: {str(e)}", text)
    
    @staticmethod
    def parse_as_model(text: str, model_class: Type[T]) -> T:
        """
        Parse JSON and validate against a Pydantic model.
        
        Args:
            text: The text to parse
            model_class: Pydantic model class to validate against
            
        Returns:
            Instance of the model class
            
        Raises:
            JSONParsingError: If parsing or validation fails
        """
        try:
            data = JSONParser.parse(text)
            
            # Now validate with the model
            return model_class.model_validate(data)
            
        except ValidationError as e:
            logger.error(f"JSON validation failed: {str(e)}")
            raise JSONParsingError(f"JSON validation failed: {str(e)}", text, 
                                  partial_data=data if 'data' in locals() else None)
        except JSONParsingError:
            # Re-raise existing JSONParsingError
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise JSONParsingError(f"Error parsing JSON: {str(e)}", text)


# Convenience functions
def parse_json(text: str) -> Dict[str, Any]:
    """
    Parse JSON from an LLM response.
    
    Args:
        text: The text to parse
        
    Returns:
        Parsed JSON as a dictionary
        
    Raises:
        JSONParsingError: If parsing fails
    """
    return JSONParser.parse(text)

def extract_json(text: str) -> str:
    """
    Extract JSON string from an LLM response.
    
    Args:
        text: The text to extract JSON from
        
    Returns:
        Extracted JSON as a string
        
    Raises:
        JSONParsingError: If no JSON found
    """
    return JSONParser.extract_json(text)