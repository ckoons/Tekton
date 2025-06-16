"""
Python tool generator.

Provides functionality for generating Python-based tools and tests.
"""

import logging
from typing import Dict, List, Any, Optional

from ergon.utils.config.settings import settings
from ergon.core.llm.client import LLMClient

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class PythonGenerator:
    """Generator for Python tools and tests."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the Python generator.
        
        Args:
            llm_client: LLM client for text generation
        """
        self.llm_client = llm_client
    
    async def generate_tool(
        self,
        name: str,
        description: str,
        capabilities: Optional[List[Dict[str, str]]],
        parameters: Optional[List[Dict[str, Any]]],
        relevant_docs: str
    ) -> str:
        """
        Generate Python tool implementation.
        
        Args:
            name: Tool name
            description: Tool description
            capabilities: List of capabilities
            parameters: List of parameters
            relevant_docs: Relevant documentation
            
        Returns:
            Generated Python code
        """
        # Create prompt for the tool generation
        system_prompt = """You are an expert Python developer tasked with creating a tool for an AI agent system.
Your goal is to create a clean, well-documented Python module that implements the requested functionality.

Follow these guidelines:
1. Use type hints consistently
2. Add comprehensive docstrings and comments
3. Handle errors gracefully with appropriate exceptions
4. Include all necessary imports
5. Create well-structured functions with clear purposes
6. Implement the core functionality described in the request
7. Make the code easy to use and integrate with other systems
8. Ensure the code is secure and follows best practices"""

        capabilities_text = ""
        if capabilities:
            capabilities_text = "The tool has these capabilities:\n" + "\n".join([f"- {c['name']}: {c['description']}" for c in capabilities])
        
        parameters_text = ""
        if parameters:
            parameters_text += "The tool has these parameters:\n"
            for param in parameters:
                required = "Required" if param.get("required", False) else "Optional"
                default = f" (default: {param.get('default_value', 'None')})" if "default_value" in param else ""
                parameters_text += f"- {param['name']} ({param.get('type', 'string')}, {required}){default}: {param['description']}\n"

        user_prompt = f"""Create a Python tool named '{name}' that {description}.

{capabilities_text}
{parameters_text}

Here's some relevant documentation that might help:
{relevant_docs}

Return only the Python code with no additional text. Include imports, docstrings, and full implementation. The tool should be a standalone Python module that can be imported and used directly.
"""

        try:
            # Generate the tool code
            tool_code = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Clean up the response (remove markdown code blocks if present)
            tool_code = tool_code.strip()
            if tool_code.startswith("```python"):
                tool_code = tool_code[len("```python"):].strip()
            if tool_code.startswith("```"):
                tool_code = tool_code[3:].strip()
            if tool_code.endswith("```"):
                tool_code = tool_code[:-3].strip()
            
            return tool_code
        except Exception as e:
            logger.error(f"Error generating Python tool: {str(e)}")
            # Return a fallback implementation
            return self._generate_fallback_tool(name, description)
    
    async def generate_test(self, name: str, description: str) -> str:
        """
        Generate Python test file.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            Generated Python test code
        """
        system_prompt = """You are an expert Python developer tasked with creating tests for a tool.
Create a comprehensive test file using pytest that tests all aspects of the tool."""

        user_prompt = f"""Create a test file for a Python tool named '{name}' that {description}.

The test file should:
1. Import pytest and the tool module
2. Test all main functionality
3. Include test cases for both success and failure scenarios
4. Use proper pytest fixtures and assertions
5. Follow best practices for test design

Return only the Python test code with no additional text."""

        try:
            # Generate the test code
            test_code = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Clean up the response
            test_code = test_code.strip()
            if test_code.startswith("```python"):
                test_code = test_code[len("```python"):].strip()
            if test_code.startswith("```"):
                test_code = test_code[3:].strip()
            if test_code.endswith("```"):
                test_code = test_code[:-3].strip()
            
            return test_code
        except Exception as e:
            logger.error(f"Error generating Python test: {str(e)}")
            # Return a fallback test implementation
            return self._generate_fallback_test(name, description)
    
    def _generate_fallback_tool(self, name: str, description: str) -> str:
        """
        Generate fallback Python tool when LLM fails.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            Basic Python tool implementation
        """
        return f'''"""
{name.title()} Tool.

{description}
"""

from typing import Dict, Any, Optional


def main(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main function for the {name} tool.
    
    Args:
        params: Dictionary of parameters
        
    Returns:
        Result dictionary
    """
    params = params or {{}}
    
    # TODO: Implement tool functionality
    
    return {{
        "success": True,
        "message": "Tool executed successfully. Please implement the actual functionality.",
        "data": {{}}
    }}


if __name__ == "__main__":
    # Example usage
    result = main({{"param1": "value1"}})
    print(result)
'''
    
    def _generate_fallback_test(self, name: str, description: str) -> str:
        """
        Generate fallback Python test when LLM fails.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            Basic Python test implementation
        """
        return f'''"""
Tests for {name.title()} Tool.
"""

import pytest
from {name.lower()} import main


def test_{name.lower()}_success():
    """Test successful execution of {name} tool."""
    result = main({{"param1": "value1"}})
    assert result["success"] is True


def test_{name.lower()}_missing_params():
    """Test {name} tool with missing parameters."""
    result = main({{}})
    assert result["success"] is True  # Default params should work


def test_{name.lower()}_invalid_params():
    """Test {name} tool with invalid parameters."""
    # TODO: Implement test with invalid parameters
    pass
'''