"""
Documentation generator.

Provides functionality for generating documentation files like
README, requirements.txt, and package.json.
"""

import logging
from typing import Dict, List, Any, Optional

from ergon.utils.config.settings import settings
from ergon.core.llm.client import LLMClient

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class DocumentationGenerator:
    """Generator for tool documentation files."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the documentation generator.
        
        Args:
            llm_client: LLM client for text generation
        """
        self.llm_client = llm_client
    
    async def generate_readme(
        self,
        name: str,
        description: str,
        implementation_type: str,
        capabilities: Optional[List[Dict[str, str]]],
        parameters: Optional[List[Dict[str, Any]]]
    ) -> str:
        """
        Generate README file.
        
        Args:
            name: Tool name
            description: Tool description
            implementation_type: Tool implementation type
            capabilities: List of capabilities
            parameters: List of parameters
            
        Returns:
            Generated README markdown
        """
        system_prompt = """You are an expert technical writer tasked with creating a README for a tool.
Create a comprehensive README that explains how to use the tool, its purpose, and provides examples."""

        capabilities_text = ""
        if capabilities:
            capabilities_text = "## Capabilities\n\n" + "\n".join([f"- **{c['name']}**: {c['description']}" for c in capabilities]) + "\n\n"
        
        parameters_text = ""
        if parameters:
            parameters_text += "## Parameters\n\n"
            for param in parameters:
                required = "Required" if param.get("required", False) else "Optional"
                default = f" (default: `{param.get('default_value', 'None')})`" if "default_value" in param else ""
                parameters_text += f"- **{param['name']}** ({param.get('type', 'string')}, {required}){default}: {param['description']}\n"
            parameters_text += "\n"

        user_prompt = f"""Create a README for a {implementation_type} tool named '{name}' that {description}.

Include these sections:
1. Introduction/Overview
2. Installation
3. Usage
4. Examples
5. Parameters (if applicable)
6. Capabilities (if applicable)
7. License

{capabilities_text}
{parameters_text}

Return only the markdown content with no additional text."""

        try:
            # Generate the README
            readme = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            return readme
        except Exception as e:
            logger.error(f"Error generating README: {str(e)}")
            # Return a fallback README
            return self._generate_fallback_readme(name, description, implementation_type)
    
    async def generate_requirements(self, name: str, description: str, implementation_type: str) -> str:
        """
        Generate requirements.txt file for Python tools.
        
        Args:
            name: Tool name
            description: Tool description
            implementation_type: Tool implementation type
            
        Returns:
            Generated requirements.txt content
        """
        if implementation_type != "python":
            return ""
            
        system_prompt = """You are an expert Python developer tasked with creating a requirements.txt file for a tool.
Create a concise requirements.txt with the minimal dependencies needed for the tool to function."""

        user_prompt = f"""Create a requirements.txt file for a Python tool named '{name}' that {description}.

List only the essential dependencies with appropriate version constraints.
Do not include development dependencies like pytest or flake8.
"""

        try:
            # Generate the requirements
            requirements = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Clean up the response
            requirements = requirements.strip()
            if requirements.startswith("```"):
                requirements = requirements[3:].strip()
            if requirements.endswith("```"):
                requirements = requirements[:-3].strip()
            
            return requirements
        except Exception as e:
            logger.error(f"Error generating requirements: {str(e)}")
            # Return a fallback requirements file
            return """# Core dependencies
requests>=2.25.0
pydantic>=1.8.0
"""
    
    async def generate_package_json(self, name: str, description: str, implementation_type: str) -> str:
        """
        Generate package.json for JavaScript/TypeScript tools.
        
        Args:
            name: Tool name
            description: Tool description
            implementation_type: Tool implementation type
            
        Returns:
            Generated package.json content
        """
        if implementation_type not in ["js", "javascript", "typescript"]:
            return ""
            
        system_prompt = """You are an expert JavaScript/TypeScript developer tasked with creating a package.json file for a tool.
Create a concise package.json with the minimal dependencies needed for the tool to function."""

        user_prompt = f"""Create a package.json file for a {implementation_type} tool named '{name}' that {description}.

Include:
1. Basic package info (name, version, description)
2. Main script entry point
3. Essential dependencies
4. Scripts for testing
5. Appropriate license
"""

        try:
            # Generate the package.json
            package_json = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Clean up the response
            package_json = package_json.strip()
            if package_json.startswith("```json"):
                package_json = package_json[7:].strip()
            if package_json.startswith("```"):
                package_json = package_json[3:].strip()
            if package_json.endswith("```"):
                package_json = package_json[:-3].strip()
            
            return package_json
        except Exception as e:
            logger.error(f"Error generating package.json: {str(e)}")
            # Return a fallback package.json
            return self._generate_fallback_package_json(name, description, implementation_type)
    
    def _generate_fallback_readme(self, name: str, description: str, implementation_type: str) -> str:
        """
        Generate fallback README when LLM fails.
        
        Args:
            name: Tool name
            description: Tool description
            implementation_type: Tool implementation type
            
        Returns:
            Basic README markdown
        """
        return f"""# {name.title()} Tool

{description}

## Installation

```bash
# Python tool
pip install -r requirements.txt

# JavaScript tool
npm install
```

## Usage

```python
# Python example
from {name.lower()} import main

result = main({{"param1": "value1"}})
print(result)
```

## Parameters

- **param1** (string, Optional): Example parameter

## License

MIT
"""
    
    def _generate_fallback_package_json(self, name: str, description: str, implementation_type: str) -> str:
        """
        Generate fallback package.json when LLM fails.
        
        Args:
            name: Tool name
            description: Tool description
            implementation_type: Tool implementation type
            
        Returns:
            Basic package.json content
        """
        is_ts = implementation_type == "typescript"
        ts_deps = """,
  "devDependencies": {
    "@types/jest": "^29.5.0",
    "@types/node": "^18.15.0",
    "typescript": "^5.0.0",
    "ts-jest": "^29.1.0"
  }""" if is_ts else ""
        
        return f"""{{
  "name": "{name.lower()}",
  "version": "0.1.0",
  "description": "{description}",
  "main": "{name.lower()}.{is_ts and 'js' or 'js'}",
  "scripts": {{
    "test": "jest"{is_ts and ',\n    "build": "tsc"' or ''}
  }},
  "keywords": [
    "ergon",
    "tool",
    "{name.lower()}"
  ],
  "author": "Ergon",
  "license": "MIT",
  "dependencies": {{
    "axios": "^1.3.0"
  }}{"" if not is_ts else ts_deps}
}}
"""