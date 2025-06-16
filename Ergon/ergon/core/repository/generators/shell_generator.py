"""
Shell script tool generator.

Provides functionality for generating shell script-based tools.
"""

import logging
from typing import Dict, List, Any, Optional

from ergon.utils.config.settings import settings
from ergon.core.llm.client import LLMClient

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class ShellGenerator:
    """Generator for shell script tools."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the shell script generator.
        
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
        Generate shell script tool implementation.
        
        Args:
            name: Tool name
            description: Tool description
            capabilities: List of capabilities
            parameters: List of parameters
            relevant_docs: Relevant documentation
            
        Returns:
            Generated shell script code
        """
        system_prompt = """You are an expert shell script developer tasked with creating a tool for an AI agent system.
Your goal is to create a clean, well-documented shell script that implements the requested functionality.

Follow these guidelines:
1. Add comprehensive comments
2. Handle errors gracefully
3. Include proper parameter parsing
4. Create well-structured functions with clear purposes
5. Implement the core functionality described in the request
6. Make the script easy to use and integrate with other systems
7. Ensure the code is secure and follows best practices"""

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

        user_prompt = f"""Create a shell script tool named '{name}' that {description}.

{capabilities_text}
{parameters_text}

Here's some relevant documentation that might help:
{relevant_docs}

Return only the shell script code with no additional text. Include comments and full implementation. The tool should be a standalone shell script that can be executed directly.
"""

        try:
            # Generate the tool code
            tool_code = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Clean up the response
            tool_code = tool_code.strip()
            if tool_code.startswith("```bash") or tool_code.startswith("```sh"):
                tool_code = tool_code[7:].strip()
            if tool_code.startswith("```shell"):
                tool_code = tool_code[9:].strip()
            if tool_code.startswith("```"):
                tool_code = tool_code[3:].strip()
            if tool_code.endswith("```"):
                tool_code = tool_code[:-3].strip()
            
            # Ensure script is executable
            if not tool_code.startswith("#!/"):
                tool_code = "#!/bin/bash\n\n" + tool_code
            
            return tool_code
        except Exception as e:
            logger.error(f"Error generating shell tool: {str(e)}")
            # Return a fallback implementation
            return self._generate_fallback_tool(name, description)
    
    def _generate_fallback_tool(self, name: str, description: str) -> str:
        """
        Generate fallback shell script tool when LLM fails.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            Basic shell script tool implementation
        """
        return f'''#!/bin/bash
# {name.title()} Tool
#
# {description}

# Function to display usage
function show_usage() {{
  echo "Usage: $(basename $0) [options]"
  echo "Options:"
  echo "  -h, --help     Show this help message"
  echo "  -p, --param1   Parameter 1 (example)"
  echo ""
  echo "Example: $(basename $0) --param1 value1"
}}

# Function to display error message
function error() {{
  echo "ERROR: $1" >&2
  show_usage
  exit 1
}}

# Parse command line arguments
PARAM1=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      show_usage
      exit 0
      ;;
    -p|--param1)
      PARAM1="$2"
      shift 2
      ;;
    *)
      error "Unknown option: $1"
      ;;
  esac
done

# TODO: Implement tool functionality

echo "Tool executed successfully. Please implement the actual functionality."
echo "Parameters:"
echo "  param1: $PARAM1"

exit 0
'''