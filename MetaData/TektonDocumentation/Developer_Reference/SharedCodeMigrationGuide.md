# Shared Code Migration Guide

This guide explains how to migrate Tekton components to use the standardized shared code utilities, including component registration and LLM client features.

## Overview

The Tekton Shared Code Sprint implemented several key improvements:

1. **Standardized Component Registration**: A unified registration system using `tekton-register` utility
2. **Enhanced LLM Client**: Improved tekton-llm-client with prompt templates and response handlers
3. **Shared Utilities**: Common utilities for logging, port management, and configuration

This guide explains how to migrate existing components to use these features.

## Migrating to tekton-register

The old registration method using individual `register_with_hermes.py` scripts has been replaced with the `tekton-register` utility.

### Migration Steps

1. **Replace registration code in setup.sh or launch scripts**:

   Old approach:
   ```bash
   # Old approach - individual registration script
   python register_with_hermes.py
   ```

   New approach:
   ```bash
   # New approach - standardized tekton-register utility
   ${TEKTON_ROOT}/scripts/tekton-register register --component component_id --config ${TEKTON_ROOT}/config/components/component.yaml &
   REGISTER_PID=$!

   # Trap to unregister on exit
   trap "${TEKTON_ROOT}/scripts/tekton-register unregister --component component_id" EXIT SIGINT SIGTERM
   ```

2. **Add proper error handling and signal trapping**:

   ```bash
   # Error handling function
   handle_error() {
     echo "Error: $1" >&2
     ${TEKTON_ROOT}/scripts/tekton-register unregister --component component_id
     exit 1
   }

   # Trap signals for graceful shutdown
   trap "${TEKTON_ROOT}/scripts/tekton-register unregister --component component_id; exit" EXIT SIGINT SIGTERM
   ```

3. **Remove old register_with_hermes.py scripts** once migration is complete.

## Migrating to Enhanced LLM Client

The tekton-llm-client now includes prompt templates, response handlers, and configuration utilities.

### Migration Steps

1. **Update imports**:

   Old approach:
   ```python
   from tekton_llm_client import TektonLLMClient
   ```

   New approach:
   ```python
   from tekton_llm_client import (
       TektonLLMClient,
       PromptTemplateRegistry, PromptTemplate, load_template,
       JSONParser, parse_json, extract_json,
       StreamHandler, collect_stream,
       StructuredOutputParser, OutputFormat,
       ClientSettings, LLMSettings, load_settings
   )
   ```

2. **Replace custom prompt construction with PromptTemplateRegistry**:

   Old approach:
   ```python
   def generate_prompt(context, query):
       return f"""
       Given the following context:
       {context}
       
       Answer this question: {query}
       """
   ```

   New approach:
   ```python
   # Create a template registry
   registry = PromptTemplateRegistry()
   
   # Register a template
   registry.register({
       "name": "question_answering",
       "template": """
       Given the following context:
       {{ context }}
       
       Answer this question: {{ query }}
       """,
       "description": "Template for answering questions with context."
   })
   
   # Use the template
   prompt = registry.render(
       "question_answering",
       context=context,
       query=query
   )
   ```

3. **Replace custom JSON parsing with parse_json and StructuredOutputParser**:

   Old approach:
   ```python
   import json
   
   def extract_items(response):
       try:
           # Try to extract JSON
           response_text = response.content
           json_start = response_text.find("{")
           json_end = response_text.rfind("}") + 1
           if json_start >= 0 and json_end > json_start:
               json_str = response_text[json_start:json_end]
               return json.loads(json_str)
       except:
           # Fall back to manual parsing
           items = []
           lines = response_text.split("\n")
           for line in lines:
               if line.strip().startswith("-"):
                   items.append(line.strip()[1:].strip())
           return items
   ```

   New approach:
   ```python
   # For JSON responses
   try:
       data = parse_json(response.content)
       # Use the parsed data
   except Exception as e:
       # Handle parsing error
       print(f"Parsing error: {e}")
   
   # For list responses
   parser = StructuredOutputParser(format=OutputFormat.LIST)
   items = parser.parse(response.content)
   ```

4. **Update streaming handlers**:

   Old approach:
   ```python
   async def process_stream(stream):
       full_text = ""
       async for chunk in stream:
           full_text += chunk
           print(chunk, end="", flush=True)
       return full_text
   ```

   New approach:
   ```python
   handler = StreamHandler()
   
   # Process stream with live output
   result = await handler.process_stream(
       stream,
       # Optional transformation
       transform=lambda text: text.replace("X", "Y")
   )
   ```

5. **Update configuration management**:

   Old approach:
   ```python
   import os
   
   def get_api_key():
       return os.environ.get("API_KEY", "")
   
   def get_model():
       return os.environ.get("MODEL", "default-model")
   ```

   New approach:
   ```python
   from tekton_llm_client.config import get_env, load_settings
   
   # Use environment utilities
   api_key = get_env("API_KEY", "")
   
   # Or use structured settings
   settings = load_settings(
       component_id="my-component",
       load_from_env=True
   )
   
   client = TektonLLMClient(
       component_id=settings.component_id,
       provider_id=settings.llm.provider,
       model_id=settings.llm.model
   )
   ```

## Example: Complete Migration

Here's an example of a fully migrated component:

```bash
#!/bin/bash
# Launch script for MyComponent

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ "$SCRIPT_DIR" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    TEKTON_ROOT=$(cd "$SCRIPT_DIR" && cd "$(readlink "${BASH_SOURCE[0]}" | xargs dirname | xargs dirname)" && pwd)
else
    # Script is running from component directory
    TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Error handling
handle_error() {
    echo "Error: $1" >&2
    ${TEKTON_ROOT}/scripts/tekton-register unregister --component my-component
    exit 1
}

# Register with Hermes using tekton-register
echo "Registering MyComponent with Hermes..."
${TEKTON_ROOT}/scripts/tekton-register register --component my-component --config ${TEKTON_ROOT}/config/components/my-component.yaml &
REGISTER_PID=$!

# Start the component
echo "Starting MyComponent..."
python -m my_component.api.app --port 8123 || handle_error "Failed to start MyComponent"

# Trap signals for graceful shutdown
trap "${TEKTON_ROOT}/scripts/tekton-register unregister --component my-component; exit" EXIT SIGINT SIGTERM

# Wait for component to finish
wait
```

## Python Example with Enhanced LLM Client

```python
import asyncio
from tekton_llm_client import (
    TektonLLMClient,
    PromptTemplateRegistry,
    parse_json,
    StreamHandler,
    ClientSettings,
    load_settings
)

# Initialize prompt registry with templates from files
registry = PromptTemplateRegistry()
registry.load_from_directory("templates")

async def generate_response(input_text, context_id):
    # Load settings
    settings = load_settings("my-component")
    
    # Create client
    client = TektonLLMClient(
        component_id=settings.component_id,
        provider_id=settings.llm.provider,
        model_id=settings.llm.model
    )
    await client.initialize()
    
    try:
        # Render prompt from template
        prompt = registry.render(
            "analysis",
            input=input_text,
            options={"structured": True}
        )
        
        # Generate response
        response = await client.generate_text(
            prompt=prompt,
            system_prompt="You are an analysis assistant."
        )
        
        # Parse JSON response
        result = parse_json(response.content)
        return result
    
    finally:
        await client.shutdown()

if __name__ == "__main__":
    asyncio.run(generate_response("Analyze this text", "context-123"))
```

## Troubleshooting

- **Component not registering**: Ensure your component YAML is in the correct location and the component ID matches
- **Template not found**: Check that you're using the correct template name and that the template exists
- **Parse error**: Use the correct parser for your expected output format (JSON, list, etc.)
- **Client initialization failed**: Verify that the Rhetor service is running and accessible

## Additional Resources

- **tekton-register help**: Run `tekton-register --help` for command usage
- **Enhanced client examples**: See `tekton-llm-client/examples/enhanced_usage.py`
- **Shared utilities documentation**: See `docs/SHARED_COMPONENT_UTILITIES.md`
- **Component lifecycle guide**: See `docs/COMPONENT_LIFECYCLE.md`