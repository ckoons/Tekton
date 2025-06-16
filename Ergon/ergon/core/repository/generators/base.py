"""
Base tool generator module.

Defines the main ToolGenerator class that orchestrates the tool generation process.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple

from ergon.utils.config.settings import settings
from ergon.core.llm.client import LLMClient
from ergon.core.docs.document_store import document_store
from ergon.core.configuration.wrapper import ConfigurationGenerator
from ergon.core.memory.rag import RAGUtils

# Import generator modules
from ergon.core.repository.generators.python_generator import PythonGenerator
from ergon.core.repository.generators.javascript_generator import JavaScriptGenerator
from ergon.core.repository.generators.shell_generator import ShellGenerator
from ergon.core.repository.generators.documentation_generator import DocumentationGenerator
from ergon.core.repository.analysis.code_analyzer import CodeAnalyzer
from ergon.core.repository.utils.file_helpers import get_file_extension

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class ToolGenerator:
    """
    AI-driven tool generator.
    
    This class leverages LLMs and RAG to generate tools based on descriptions.
    """
    
    def __init__(
        self, 
        model_name: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize the tool generator.
        
        Args:
            model_name: Name of the model to use for generation (defaults to settings)
            temperature: Temperature for generation (0-1)
        """
        self.model_name = model_name or settings.default_model
        self.temperature = temperature
        self.llm_client = LLMClient(model_name=self.model_name, temperature=self.temperature)
        self.configuration_generator = ConfigurationGenerator()
        self.rag = RAGUtils()
        
        # Initialize generators
        self.python_generator = PythonGenerator(self.llm_client)
        self.javascript_generator = JavaScriptGenerator(self.llm_client)
        self.shell_generator = ShellGenerator(self.llm_client)
        self.documentation_generator = DocumentationGenerator(self.llm_client)
        self.code_analyzer = CodeAnalyzer(self.llm_client)
    
    async def generate(
        self, 
        name: str, 
        description: str,
        implementation_type: str = "python",
        capabilities: Optional[List[Dict[str, str]]] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a new tool.
        
        Args:
            name: Name of the tool
            description: Description of the tool
            implementation_type: Implementation type (python, js, bash, etc.)
            capabilities: Optional list of capabilities
            parameters: Optional list of parameters
        
        Returns:
            Dictionary with tool details and files
        """
        # Validate name (alphanumeric with underscores)
        if not name.replace("_", "").isalnum():
            raise ValueError("Tool name must contain only alphanumeric characters and underscores")
        
        # Get relevant documentation
        relevant_docs = await self._get_relevant_documentation(name, description, implementation_type)
        
        # Generate tool files and metadata
        tool_files = await self._generate_tool_files(name, description, implementation_type, capabilities, parameters, relevant_docs)
        
        # Generate parameters if not provided
        if not parameters:
            parameters = await self.code_analyzer.extract_parameters(
                name, description, implementation_type, tool_files
            )
        
        # Generate capabilities if not provided
        if not capabilities:
            capabilities = await self.code_analyzer.extract_capabilities(
                name, description, implementation_type, tool_files
            )
        
        # Return tool data
        return {
            "name": name,
            "description": description,
            "implementation_type": implementation_type,
            "entry_point": f"{name.lower()}.{get_file_extension(implementation_type)}",
            "capabilities": capabilities,
            "parameters": parameters,
            "files": tool_files
        }
    
    async def _get_relevant_documentation(self, name: str, description: str, implementation_type: str) -> str:
        """Get relevant documentation for tool generation."""
        # Construct search query
        query = f"Generate a {implementation_type} tool named {name} that {description}"
        
        # Get relevant documentation
        documentation = await document_store.get_relevant_documentation(query, limit=3)
        
        return documentation
    
    async def _generate_tool_files(
        self,
        name: str,
        description: str,
        implementation_type: str,
        capabilities: Optional[List[Dict[str, str]]],
        parameters: Optional[List[Dict[str, Any]]],
        relevant_docs: str
    ) -> List[Dict[str, str]]:
        """Generate tool implementation files."""
        files = []
        
        if implementation_type == "python":
            # Generate main Python file
            main_file = await self.python_generator.generate_tool(
                name, description, capabilities, parameters, relevant_docs
            )
            files.append({
                "filename": f"{name.lower()}.py",
                "file_type": "python",
                "content": main_file
            })
            
            # Generate test file
            test_file = await self.python_generator.generate_test(name, description)
            files.append({
                "filename": f"test_{name.lower()}.py",
                "file_type": "python",
                "content": test_file
            })
            
            # Generate README
            readme = await self.documentation_generator.generate_readme(
                name, description, implementation_type, capabilities, parameters
            )
            files.append({
                "filename": "README.md",
                "file_type": "markdown",
                "content": readme
            })
            
            # Generate requirements.txt
            requirements = await self.documentation_generator.generate_requirements(
                name, description, implementation_type
            )
            files.append({
                "filename": "requirements.txt",
                "file_type": "requirements",
                "content": requirements
            })
        
        elif implementation_type in ["js", "javascript", "typescript"]:
            # Generate main JS/TS file
            main_file = await self.javascript_generator.generate_tool(
                name, description, capabilities, parameters, relevant_docs, implementation_type
            )
            ext = "ts" if implementation_type == "typescript" else "js"
            files.append({
                "filename": f"{name.lower()}.{ext}",
                "file_type": implementation_type,
                "content": main_file
            })
            
            # Generate test file
            test_file = await self.javascript_generator.generate_test(
                name, description, implementation_type
            )
            files.append({
                "filename": f"{name.lower()}.test.{ext}",
                "file_type": implementation_type,
                "content": test_file
            })
            
            # Generate README
            readme = await self.documentation_generator.generate_readme(
                name, description, implementation_type, capabilities, parameters
            )
            files.append({
                "filename": "README.md",
                "file_type": "markdown",
                "content": readme
            })
            
            # Generate package.json
            package_json = await self.documentation_generator.generate_package_json(
                name, description, implementation_type
            )
            files.append({
                "filename": "package.json",
                "file_type": "json",
                "content": package_json
            })
        
        elif implementation_type in ["bash", "shell"]:
            # Generate main shell script
            main_file = await self.shell_generator.generate_tool(
                name, description, capabilities, parameters, relevant_docs
            )
            files.append({
                "filename": f"{name.lower()}.sh",
                "file_type": "shell",
                "content": main_file
            })
            
            # Generate README
            readme = await self.documentation_generator.generate_readme(
                name, description, implementation_type, capabilities, parameters
            )
            files.append({
                "filename": "README.md",
                "file_type": "markdown",
                "content": readme
            })
        
        # Return all generated files
        return files


# Convenience function to generate a tool synchronously
def generate_tool(
    name: str, 
    description: str,
    implementation_type: str = "python",
    capabilities: Optional[List[Dict[str, str]]] = None,
    parameters: Optional[List[Dict[str, Any]]] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Generate a new tool.
    
    Args:
        name: Name of the tool
        description: Description of the tool
        implementation_type: Implementation type (python, js, bash, etc.)
        capabilities: Optional list of capabilities
        parameters: Optional list of parameters
        model_name: Name of the model to use for generation
        temperature: Temperature for generation
    
    Returns:
        Dictionary with tool details and files
    """
    generator = ToolGenerator(model_name=model_name, temperature=temperature)
    return asyncio.run(generator.generate(name, description, implementation_type, capabilities, parameters))