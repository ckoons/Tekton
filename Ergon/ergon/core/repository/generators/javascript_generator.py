"""
JavaScript/TypeScript tool generator.

Provides functionality for generating JavaScript and TypeScript-based tools and tests.
"""

import logging
from typing import Dict, List, Any, Optional

from ergon.utils.config.settings import settings
from ergon.core.llm.client import LLMClient

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class JavaScriptGenerator:
    """Generator for JavaScript/TypeScript tools and tests."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the JavaScript/TypeScript generator.
        
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
        relevant_docs: str,
        implementation_type: str = "javascript"
    ) -> str:
        """
        Generate JavaScript/TypeScript tool implementation.
        
        Args:
            name: Tool name
            description: Tool description
            capabilities: List of capabilities
            parameters: List of parameters
            relevant_docs: Relevant documentation
            implementation_type: "javascript" or "typescript"
            
        Returns:
            Generated JS/TS code
        """
        # Determine which language to use
        is_typescript = implementation_type.lower() == "typescript"
        language = "TypeScript" if is_typescript else "JavaScript"
        
        system_prompt = f"""You are an expert {language} developer tasked with creating a tool for an AI agent system.
Your goal is to create a clean, well-documented {language} module that implements the requested functionality.

Follow these guidelines:
1. Use proper types (interfaces/types for TypeScript, JSDoc for JavaScript)
2. Add comprehensive comments
3. Handle errors gracefully
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

        user_prompt = f"""Create a {language} tool named '{name}' that {description}.

{capabilities_text}
{parameters_text}

Here's some relevant documentation that might help:
{relevant_docs}

Return only the {language} code with no additional text. Include imports, comments, and full implementation. The tool should be a standalone module that can be imported and used directly.
"""

        try:
            # Generate the tool code
            tool_code = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Clean up the response
            tool_code = tool_code.strip()
            if tool_code.startswith(f"```{language.lower()}"):
                tool_code = tool_code[len(f"```{language.lower()}"):].strip()
            elif tool_code.startswith("```js") or tool_code.startswith("```ts"):
                tool_code = tool_code[5:].strip()
            elif tool_code.startswith("```javascript") or tool_code.startswith("```typescript"):
                tool_code = tool_code[14:].strip()
            if tool_code.startswith("```"):
                tool_code = tool_code[3:].strip()
            if tool_code.endswith("```"):
                tool_code = tool_code[:-3].strip()
            
            return tool_code
        except Exception as e:
            logger.error(f"Error generating {language} tool: {str(e)}")
            # Return a fallback implementation
            if is_typescript:
                return self._generate_fallback_typescript_tool(name, description)
            else:
                return self._generate_fallback_js_tool(name, description)
    
    async def generate_test(self, name: str, description: str, implementation_type: str = "javascript") -> str:
        """
        Generate JavaScript/TypeScript test file.
        
        Args:
            name: Tool name
            description: Tool description
            implementation_type: "javascript" or "typescript"
            
        Returns:
            Generated JS/TS test code
        """
        # Determine which language to use
        is_typescript = implementation_type.lower() == "typescript"
        language = "TypeScript" if is_typescript else "JavaScript"
        framework = "Jest"
        
        system_prompt = f"""You are an expert {language} developer tasked with creating tests for a tool.
Create a comprehensive test file using {framework} that tests all aspects of the tool."""

        user_prompt = f"""Create a test file for a {language} tool named '{name}' that {description}.

The test file should:
1. Import {framework} and the tool module
2. Test all main functionality
3. Include test cases for both success and failure scenarios
4. Use proper {framework} matchers and assertions
5. Follow best practices for test design

Return only the {language} test code with no additional text."""

        try:
            # Generate the test code
            test_code = await self.llm_client.acomplete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Clean up the response
            test_code = test_code.strip()
            if test_code.startswith(f"```{language.lower()}"):
                test_code = test_code[len(f"```{language.lower()}"):].strip()
            elif test_code.startswith("```js") or test_code.startswith("```ts"):
                test_code = test_code[5:].strip()
            elif test_code.startswith("```javascript") or test_code.startswith("```typescript"):
                test_code = test_code[14:].strip()
            if test_code.startswith("```"):
                test_code = test_code[3:].strip()
            if test_code.endswith("```"):
                test_code = test_code[:-3].strip()
            
            return test_code
        except Exception as e:
            logger.error(f"Error generating {language} test: {str(e)}")
            # Return a fallback test implementation
            if is_typescript:
                return self._generate_fallback_typescript_test(name, description)
            else:
                return self._generate_fallback_js_test(name, description)
    
    def _generate_fallback_js_tool(self, name: str, description: str) -> str:
        """
        Generate fallback JavaScript tool when LLM fails.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            Basic JavaScript tool implementation
        """
        return f'''/**
 * {name.title()} Tool.
 *
 * {description}
 */

/**
 * Main function for the {name} tool.
 * @param {{Object}} params - Dictionary of parameters
 * @returns {{Object}} Result object
 */
function main(params = {{}}) {{
  // TODO: Implement tool functionality
  
  return {{
    success: true,
    message: "Tool executed successfully. Please implement the actual functionality.",
    data: {{}}
  }};
}}

module.exports = {{ main }};
'''
    
    def _generate_fallback_typescript_tool(self, name: str, description: str) -> str:
        """
        Generate fallback TypeScript tool when LLM fails.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            Basic TypeScript tool implementation
        """
        return f'''/**
 * {name.title()} Tool.
 *
 * {description}
 */

interface Params {{
  [key: string]: any;
}}

interface Result {{
  success: boolean;
  message: string;
  data: any;
}}

/**
 * Main function for the {name} tool.
 * @param params - Dictionary of parameters
 * @returns Result object
 */
export function main(params: Params = {{}}): Result {{
  // TODO: Implement tool functionality
  
  return {{
    success: true,
    message: "Tool executed successfully. Please implement the actual functionality.",
    data: {{}}
  }};
}}

// For CommonJS compatibility
export default {{ main }};
'''
    
    def _generate_fallback_js_test(self, name: str, description: str) -> str:
        """
        Generate fallback JavaScript test when LLM fails.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            Basic JavaScript test implementation
        """
        return f'''/**
 * Tests for {name.title()} Tool.
 */

const {{ main }} = require('./{name.lower()}');

describe('{name} Tool', () => {{
  test('should execute successfully with parameters', () => {{
    const result = main({{ param1: 'value1' }});
    expect(result.success).toBe(true);
  }});

  test('should execute successfully with no parameters', () => {{
    const result = main();
    expect(result.success).toBe(true);
  }});

  test('should handle invalid parameters', () => {{
    // TODO: Implement test with invalid parameters
  }});
}});
'''
    
    def _generate_fallback_typescript_test(self, name: str, description: str) -> str:
        """
        Generate fallback TypeScript test when LLM fails.
        
        Args:
            name: Tool name
            description: Tool description
            
        Returns:
            Basic TypeScript test implementation
        """
        return f'''/**
 * Tests for {name.title()} Tool.
 */

import {{ main }} from './{name.lower()}';

describe('{name} Tool', () => {{
  test('should execute successfully with parameters', () => {{
    const result = main({{ param1: 'value1' }});
    expect(result.success).toBe(true);
  }});

  test('should execute successfully with no parameters', () => {{
    const result = main();
    expect(result.success).toBe(true);
  }});

  test('should handle invalid parameters', () => {{
    // TODO: Implement test with invalid parameters
  }});
}});
'''