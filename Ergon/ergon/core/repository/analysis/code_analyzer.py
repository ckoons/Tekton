"""
Code analyzer.

Provides functionality for analyzing code to extract parameters,
capabilities, and other metadata.
"""

import json
import logging
from typing import Dict, List, Any, Optional

from ergon.utils.config.settings import settings
from ergon.core.llm.client import LLMClient

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class CodeAnalyzer:
    """Analyzer for extracting information from code."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the code analyzer.
        
        Args:
            llm_client: LLM client for text generation
        """
        self.llm_client = llm_client
    
    async def extract_parameters(
        self, 
        name: str, 
        description: str, 
        implementation_type: str,
        tool_files: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Generate parameters based on tool files.
        
        Args:
            name: Tool name
            description: Tool description
            implementation_type: Tool implementation type
            tool_files: List of tool file dictionaries
            
        Returns:
            List of parameter dictionaries
        """
        system_prompt = """You are an expert developer tasked with analyzing a tool implementation and extracting its parameters.
Analyze the code and identify all parameters that the tool accepts, along with their types, descriptions, and whether they are required."""

        # Find the main implementation file
        main_file = None
        extension = "py" if implementation_type == "python" else "js"
        if implementation_type == "typescript":
            extension = "ts"
        elif implementation_type in ["bash", "shell"]:
            extension = "sh"
            
        for file in tool_files:
            if file["filename"] == f"{name.lower()}.{extension}":
                main_file = file
                break
        
        if not main_file:
            return self._generate_default_parameters()
        
        user_prompt = f"""Analyze this {implementation_type} tool code and extract all parameters:

```
{main_file["content"]}
```

Return a JSON array of parameter objects with these properties:
- name: The parameter name
- description: Brief description of what the parameter does
- type: Data type (string, number, boolean, array, object)
- required: Whether the parameter is required (true/false)
- default_value: Default value if any

Format your response as a valid JSON array, nothing else.
"""

        try:
            # Generate parameters
            parameters_json = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Clean up the response and parse JSON
            parameters_json = parameters_json.strip()
            if parameters_json.startswith("```json"):
                parameters_json = parameters_json[7:].strip()
            if parameters_json.startswith("```"):
                parameters_json = parameters_json[3:].strip()
            if parameters_json.endswith("```"):
                parameters_json = parameters_json[:-3].strip()
            
            parameters = json.loads(parameters_json)
            return parameters
        except Exception as e:
            logger.error(f"Error extracting parameters: {str(e)}")
            # Return default parameters
            return self._generate_default_parameters()
    
    async def extract_capabilities(
        self, 
        name: str, 
        description: str, 
        implementation_type: str,
        tool_files: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Generate capabilities based on tool files.
        
        Args:
            name: Tool name
            description: Tool description
            implementation_type: Tool implementation type
            tool_files: List of tool file dictionaries
            
        Returns:
            List of capability dictionaries
        """
        system_prompt = """You are an expert developer tasked with analyzing a tool implementation and extracting its capabilities.
Analyze the code and identify all capabilities that the tool provides."""

        # Find the main implementation file
        main_file = None
        extension = "py" if implementation_type == "python" else "js"
        if implementation_type == "typescript":
            extension = "ts"
        elif implementation_type in ["bash", "shell"]:
            extension = "sh"
            
        for file in tool_files:
            if file["filename"] == f"{name.lower()}.{extension}":
                main_file = file
                break
        
        if not main_file:
            return self._generate_default_capabilities(name, description)
        
        user_prompt = f"""Analyze this {implementation_type} tool code and extract its capabilities:

```
{main_file["content"]}
```

Return a JSON array of capability objects with these properties:
- name: Short name for the capability
- description: Detailed description of what the capability does

Format your response as a valid JSON array, nothing else.
"""

        try:
            # Generate capabilities
            capabilities_json = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Clean up the response and parse JSON
            capabilities_json = capabilities_json.strip()
            if capabilities_json.startswith("```json"):
                capabilities_json = capabilities_json[7:].strip()
            if capabilities_json.startswith("```"):
                capabilities_json = capabilities_json[3:].strip()
            if capabilities_json.endswith("```"):
                capabilities_json = capabilities_json[:-3].strip()
            
            capabilities = json.loads(capabilities_json)
            return capabilities
        except Exception as e:
            logger.error(f"Error extracting capabilities: {str(e)}")
            # Return default capabilities based on description
            return self._generate_default_capabilities(name, description)
    
    def _generate_default_parameters(self) -> List[Dict[str, Any]]:
        """
        Generate default parameters when extraction fails.
        
        Returns:
            List with a default parameter
        """
        return [
            {
                "name": "param1",
                "description": "Example parameter",
                "type": "string",
                "required": False,
                "default_value": None
            }
        ]
    
    def _generate_default_capabilities(self, name: str, description: str) -> List[Dict[str, str]]:
        """
        Generate default capabilities when extraction fails.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            List with a default capability
        """
        return [
            {
                "name": name.lower().replace("_", "-"),
                "description": description
            }
        ]