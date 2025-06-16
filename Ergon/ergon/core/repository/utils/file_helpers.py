"""
File helper utilities.

Provides utility functions for file handling in the tool generator.
"""

def get_file_extension(implementation_type: str) -> str:
    """
    Get file extension for implementation type.
    
    Args:
        implementation_type: Implementation type (python, js, typescript, etc.)
        
    Returns:
        File extension string
    """
    extensions = {
        "python": "py",
        "js": "js",
        "javascript": "js",
        "typescript": "ts",
        "bash": "sh",
        "shell": "sh",
        "ruby": "rb",
        "go": "go",
        "rust": "rs"
    }
    return extensions.get(implementation_type.lower(), implementation_type.lower())


def clean_code_block(code: str) -> str:
    """
    Clean code by removing markdown code blocks.
    
    Args:
        code: Code string possibly with markdown code blocks
        
    Returns:
        Cleaned code string
    """
    code = code.strip()
    
    # Remove starting code block markers
    if code.startswith("```python"):
        code = code[len("```python"):].strip()
    elif code.startswith("```javascript"):
        code = code[len("```javascript"):].strip()
    elif code.startswith("```typescript"):
        code = code[len("```typescript"):].strip()
    elif code.startswith("```js"):
        code = code[len("```js"):].strip()
    elif code.startswith("```ts"):
        code = code[len("```ts"):].strip()
    elif code.startswith("```bash") or code.startswith("```sh"):
        code = code[len("```bash"):].strip()
    elif code.startswith("```shell"):
        code = code[len("```shell"):].strip()
    elif code.startswith("```json"):
        code = code[len("```json"):].strip()
    elif code.startswith("```"):
        code = code[3:].strip()
    
    # Remove ending code block marker
    if code.endswith("```"):
        code = code[:-3].strip()
    
    return code