# Tekton LLM Client

A unified client library for LLM integration in Tekton components.

## Overview

The `tekton-llm-client` package provides a standardized way to integrate with large language models (LLMs) in Tekton components. It uses the Rhetor component as the centralized LLM service, eliminating duplicate adapter implementations and providing consistent patterns across components.

## Installation

```bash
pip install tekton-llm-client
```

Or from the source code:

```bash
cd tekton-llm-client
pip install -e .
```

## Features

- Unified interface for LLM operations
- Support for synchronous and streaming responses
- HTTP and WebSocket protocols
- Built-in graceful degradation with fallbacks
- Comprehensive error handling
- Retry logic for reliability
- Token counting and optimization utilities
- JavaScript client for frontend components
- **New in v0.2.0:**
  - Shared prompt templates with Jinja2 templating
  - Response handlers for JSON and structured outputs
  - Advanced streaming response processing
  - Configuration utilities for settings management

## Usage

### Basic Usage

```python
import asyncio
from tekton_llm_client import TektonLLMClient

async def main():
    # Initialize the client
    client = TektonLLMClient(
        component_id="my-component",
        rhetor_url="http://localhost:8003"  # URL to your Rhetor service
    )
    
    # Initialize the connection
    await client.initialize()
    
    # Generate text
    response = await client.generate_text(
        prompt="What is the capital of France?",
        system_prompt="You are a helpful assistant that provides accurate information."
    )
    
    print(f"Response: {response.content}")
    
    # Clean up
    await client.shutdown()

# Run the async function
asyncio.run(main())
```

### Chat Conversation

```python
import asyncio
from tekton_llm_client import TektonLLMClient
from tekton_llm_client.models import Message, MessageRole

async def chat_example():
    # Initialize the client
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Create a conversation
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="Hello, how are you?"),
        Message(role=MessageRole.ASSISTANT, content="I'm doing well! How can I help you today?"),
        Message(role=MessageRole.USER, content="What's the weather like in Paris?")
    ]
    
    # Get a response
    response = await client.generate_chat_response(messages=messages)
    
    print(f"Assistant: {response.content}")
    
    # Clean up
    await client.shutdown()

asyncio.run(chat_example())
```

### Streaming

```python
import asyncio
from tekton_llm_client import TektonLLMClient
from tekton_llm_client.models import StreamingChunk

async def streaming_example():
    # Initialize the client
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Define a callback for streaming chunks
    def handle_chunk(chunk: StreamingChunk):
        print(chunk.chunk, end="", flush=True)
        if chunk.done:
            print("\n--- Streaming complete ---")
    
    # Stream a response
    prompt = "Write a short poem about artificial intelligence."
    
    print("Streaming response:\n")
    
    async for chunk in client.generate_text(
        prompt=prompt,
        streaming=True
    ):
        handle_chunk(chunk)
    
    # Clean up
    await client.shutdown()

asyncio.run(streaming_example())
```

### WebSocket Client

```python
import asyncio
from tekton_llm_client import TektonLLMWebSocketClient
from tekton_llm_client.models import StreamingChunk

async def websocket_example():
    # Initialize the WebSocket client
    client = TektonLLMWebSocketClient(
        component_id="my-component",
        on_message=lambda msg: print(f"Message received: {msg}"),
        on_error=lambda err: print(f"Error: {err}"),
        on_close=lambda: print("Connection closed")
    )
    
    # Connect to the server
    await client.connect()
    
    # Generate a response
    request_id = await client.generate(
        prompt="What is the meaning of life?",
        context_id="philosophy",
        callback=lambda chunk: print(chunk.chunk, end="", flush=True)
    )
    
    # Wait for a bit
    await asyncio.sleep(10)
    
    # Disconnect
    await client.disconnect()

asyncio.run(websocket_example())
```

### Advanced Features

```python
import asyncio
from tekton_llm_client import TektonLLMClient
from tekton_llm_client.utils import count_tokens, optimize_messages_for_token_limit

async def advanced_example():
    # Initialize the client
    client = TektonLLMClient(
        component_id="my-component",
        provider_id="anthropic",
        model_id="claude-3-sonnet-20240229",
        use_fallback=True  # Enable fallback if primary service is unavailable
    )
    await client.initialize()
    
    # Count tokens in text
    text = "This is a sample text that we'll count tokens for."
    token_count = count_tokens(text, model="claude-3-sonnet-20240229")
    print(f"Token count: {token_count}")
    
    # Create a long conversation
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about AI."},
        {"role": "assistant", "content": "Artificial Intelligence (AI) refers to systems designed to perform tasks that typically require human intelligence..."},
        # ... more messages ...
        {"role": "user", "content": "What are the ethical concerns?"}
    ]
    
    # Optimize for token limit
    optimized_messages = optimize_messages_for_token_limit(
        messages=messages,
        max_tokens=4000,
        model="claude-3-sonnet-20240229",
        keep_system_prompt=True
    )
    
    # Use optimized messages
    response = await client.generate_chat_response(
        messages=optimized_messages,
        options={
            "temperature": 0.5,
            "max_tokens": 1000,
            "fallback_provider": "simulated",  # Fallback provider if primary fails
            "retry_count": 2  # Number of retries on failure
        }
    )
    
    print(f"Response: {response.content}")
    
    # Clean up
    await client.shutdown()

asyncio.run(advanced_example())
```

## JavaScript Client

For frontend components, a JavaScript client is also provided. See the [JavaScript README](js/README.md) for more information.

## Error Handling

The client includes comprehensive error handling with specific exception types:

- `TektonLLMError`: Base exception for all client errors
- `ConnectionError`: Connection to the LLM service failed
- `TimeoutError`: Request timed out
- `AuthenticationError`: Authentication with the LLM service failed
- `ServiceUnavailableError`: LLM service is unavailable
- `RateLimitError`: Rate limit exceeded
- `InvalidRequestError`: Request was invalid
- `AdapterError`: Error with a specific LLM adapter
- `FallbackError`: All fallback options failed

Example:

```python
import asyncio
from tekton_llm_client import TektonLLMClient
from tekton_llm_client.exceptions import (
    TektonLLMError, ConnectionError, TimeoutError, 
    ServiceUnavailableError
)

async def error_handling_example():
    client = TektonLLMClient(component_id="my-component")
    
    try:
        await client.initialize()
        response = await client.generate_text("Hello, world!")
        print(f"Response: {response.content}")
    except ConnectionError:
        print("Failed to connect to the LLM service")
    except TimeoutError:
        print("Request timed out")
    except ServiceUnavailableError:
        print("LLM service is currently unavailable")
    except TektonLLMError as e:
        print(f"LLM error: {str(e)}")
    finally:
        await client.shutdown()

asyncio.run(error_handling_example())
```

## Environment Variables

The client uses these environment variables if set:

- `RHETOR_URL`: URL for the Rhetor API (default: `http://localhost:8003`)
- `RHETOR_WS_URL`: WebSocket URL for Rhetor (default: derived from `RHETOR_URL`)
- `RHETOR_DEFAULT_PROVIDER`: Default provider ID (default: `anthropic`)
- `RHETOR_DEFAULT_MODEL`: Default model ID
- `RHETOR_AUTH_TOKEN`: Authentication token for Rhetor API
- `RHETOR_TIMEOUT`: Default timeout in seconds (default: `30`)
- `RHETOR_MAX_RETRIES`: Default number of retries (default: `3`)

## New Features (v0.2.0)

### Prompt Templates

The new prompt template system provides a standardized way to manage and render prompt templates with variable substitution:

```python
import asyncio
from tekton_llm_client import TektonLLMClient, PromptTemplateRegistry

async def template_example():
    # Create a template registry
    registry = PromptTemplateRegistry()
    
    # Register a custom template
    registry.register({
        "name": "code_review",
        "template": "Review this {{ language }} code:\n\n```{{ language }}\n{{ code }}\n```\n\nFocus on {{ focus_area }}.",
        "description": "Template for code review tasks."
    })
    
    # Create a client
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Render the template
    code = "function add(a, b) { return a + b; }"
    prompt = registry.render(
        "code_review",
        language="javascript",
        code=code,
        focus_area="best practices"
    )
    
    # Use the rendered prompt
    response = await client.generate_text(prompt=prompt)
    print(f"Response: {response.content}")
    
    await client.shutdown()

asyncio.run(template_example())
```

The system includes:
- Template registry for managing common templates
- Jinja2-based variable substitution
- Template loading from files or embedded resources
- Default templates for common tasks

### Response Handlers

New response handlers help process and parse LLM outputs in various formats:

```python
import asyncio
from tekton_llm_client import (
    TektonLLMClient, parse_json, 
    StructuredOutputParser, OutputFormat
)

async def response_handler_example():
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Get JSON response
    system_prompt = "You are a JSON-only assistant. Always respond with valid JSON."
    prompt = "List the top 3 programming languages with a 'name' and 'type' field."
    
    response = await client.generate_text(
        prompt=prompt,
        system_prompt=system_prompt
    )
    
    # Parse JSON response
    try:
        data = parse_json(response.content)
        print("Languages:")
        for lang in data.get("languages", []):
            print(f"- {lang['name']} ({lang['type']})")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
    
    # Parse structured lists
    list_prompt = "List 5 tips for writing clean code."
    list_response = await client.generate_text(list_prompt)
    
    parser = StructuredOutputParser(format=OutputFormat.LIST)
    tips = parser.parse(list_response.content)
    
    print("\nCoding tips:")
    for i, tip in enumerate(tips, 1):
        print(f"{i}. {tip}")
    
    await client.shutdown()

asyncio.run(response_handler_example())
```

Features include:
- JSON parsing with robust error handling
- Structured output parsing for lists, key-value pairs, and more
- Advanced streaming response processing
- Validation with Pydantic models

### Configuration Utilities

Configuration utilities help manage settings from environment variables and files:

```python
import asyncio
from tekton_llm_client import (
    TektonLLMClient, ClientSettings, LLMSettings,
    load_settings, save_settings
)

async def config_example():
    # Create default settings
    settings = ClientSettings(
        component_id="my-component",
        llm=LLMSettings(
            provider="anthropic",
            model="claude-3-haiku-20240307",
            temperature=0.7
        )
    )
    
    # Save settings to file
    save_settings(settings, "/tmp/llm_settings.json")
    
    # Load settings from file (and environment variables)
    loaded_settings = load_settings(
        component_id="my-component",
        file_path="/tmp/llm_settings.json",
        load_from_env=True
    )
    
    # Create client using settings
    client = TektonLLMClient(
        component_id=loaded_settings.component_id,
        provider_id=loaded_settings.llm.provider,
        model_id=loaded_settings.llm.model,
        temperature=loaded_settings.llm.temperature
    )
    
    await client.initialize()
    # Use client...
    await client.shutdown()

asyncio.run(config_example())
```

Features include:
- Environment variable management
- Settings loading from files
- Pydantic models for settings validation
- Default values and overrides

## License

MIT