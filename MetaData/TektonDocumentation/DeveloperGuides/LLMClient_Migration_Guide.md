# Migration Guide: Adopting the Tekton LLM Client

This guide helps Tekton component developers migrate from custom LLM adapter implementations to the standardized `tekton-llm-client` library.

## Overview

The Tekton LLM standardization initiative centralizes LLM integration through Rhetor, eliminating duplicate adapter implementations across components. This guide walks you through the steps to migrate your component to use the shared `tekton-llm-client` library.

## Benefits of Migration

- **Simplified Integration**: Consistent API across all components
- **Reduced Code Duplication**: Eliminates redundant LLM adapter implementations
- **Improved Reliability**: Built-in retries, error handling, and fallbacks
- **Better Performance**: Connection pooling and optimized streaming
- **Enhanced Maintainability**: Centralized updates and improvements

## Migration Process

### Step 1: Install the `tekton-llm-client` Package

Add the package to your component's requirements:

```bash
pip install tekton-llm-client
```

Or add to your requirements file:

```
tekton-llm-client>=0.1.0
```

### Step 2: Identify Current LLM Integration Points

Identify where your component interacts with LLMs:

- Direct API calls to providers (Anthropic, OpenAI, etc.)
- Custom LLM adapter implementations
- WebSocket/HTTP clients for streaming

### Step 3: Replace Client Initialization

#### Before:

```python
# Custom LLM adapter
class LLMAdapter:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or "claude-3-sonnet-20240229"
        self.client = anthropic.Anthropic(api_key=self.api_key)
```

#### After:

```python
from tekton_llm_client import TektonLLMClient

# Initialize the standardized client
async def initialize_llm_client():
    client = TektonLLMClient(
        component_id="your-component-name",
        rhetor_url=os.environ.get("RHETOR_URL", "http://localhost:8003"),
        provider_id="anthropic",
        model_id="claude-3-sonnet-20240229"
    )
    
    # Initialize connection
    await client.initialize()
    return client
```

### Step 4: Replace Text Generation Calls

#### Before:

```python
async def generate_response(prompt, system_prompt=None):
    try:
        completion = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.content[0].text
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"Error: {str(e)}"
```

#### After:

```python
async def generate_response(prompt, system_prompt=None):
    try:
        response = await client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt
        )
        return response.content
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"Error: {str(e)}"
```

### Step 5: Replace Chat Conversation Calls

#### Before:

```python
async def chat_conversation(messages):
    try:
        response = await self.client.messages.create(
            model=self.model,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Error in chat conversation: {e}")
        return f"Error: {str(e)}"
```

#### After:

```python
async def chat_conversation(messages):
    try:
        response = await client.generate_chat_response(messages=messages)
        return response.content
    except Exception as e:
        logger.error(f"Error in chat conversation: {e}")
        return f"Error: {str(e)}"
```

### Step 6: Replace Streaming Implementation

#### Before:

```python
async def stream_response(prompt, callback):
    try:
        with self.client.messages.stream(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                await callback(text)
    except Exception as e:
        logger.error(f"Error streaming response: {e}")
        await callback(f"Error: {str(e)}")
```

#### After:

```python
async def stream_response(prompt, callback):
    try:
        async for chunk in client.generate_text(
            prompt=prompt,
            streaming=True
        ):
            await callback(chunk.chunk)
            
            if chunk.error:
                logger.error(f"Streaming error: {chunk.error}")
                break
    except Exception as e:
        logger.error(f"Error streaming response: {e}")
        await callback(f"Error: {str(e)}")
```

### Step 7: Replace WebSocket Implementation

If your component uses WebSocket directly:

#### Before:

```python
async def connect_websocket(url):
    self.ws = await websockets.connect(url)
    
    # Send message
    await self.ws.send(json.dumps({
        "type": "GENERATE",
        "prompt": "Hello, world!"
    }))
    
    # Receive response
    async for message in self.ws:
        data = json.loads(message)
        # Process data
```

#### After:

```python
from tekton_llm_client import TektonLLMWebSocketClient

# Initialize the WebSocket client
ws_client = TektonLLMWebSocketClient(
    component_id="your-component-name",
    on_message=lambda msg: print(f"Message received: {msg}"),
    on_error=lambda err: print(f"Error: {err}"),
    on_close=lambda: print("Connection closed")
)

# Connect and use the client
await ws_client.connect()

# Generate with WebSocket
request_id = await ws_client.generate(
    prompt="Hello, world!",
    callback=lambda chunk: process_chunk(chunk)
)
```

### Step 8: Update Error Handling

Take advantage of the specific exception types:

```python
from tekton_llm_client.exceptions import (
    TektonLLMError, ConnectionError, TimeoutError, 
    AuthenticationError, ServiceUnavailableError
)

async def generate_with_error_handling(prompt):
    try:
        return await client.generate_text(prompt)
    except ConnectionError:
        logger.error("Failed to connect to LLM service")
        return {"error": "Connection error"}
    except TimeoutError:
        logger.error("Request timed out")
        return {"error": "Timeout"}
    except ServiceUnavailableError:
        logger.error("LLM service unavailable")
        return {"error": "Service unavailable"}
    except TektonLLMError as e:
        logger.error(f"LLM error: {str(e)}")
        return {"error": str(e)}
```

### Step 9: Update Frontend Components

For frontend components using JavaScript, replace custom implementations with the `tekton-llm-client.js` client:

```html
<script src="/static/js/tekton-llm-client.js"></script>
<script>
  // Initialize the client
  const client = new TektonLLMClient({
    componentId: 'my-ui-component',
    rhetorUrl: '/api/llm'
  });
  
  // Generate text
  async function generateResponse() {
    const prompt = document.getElementById('prompt').value;
    try {
      const response = await client.generateText(prompt);
      document.getElementById('response').textContent = response.content;
    } catch (error) {
      console.error("Error:", error);
      document.getElementById('response').textContent = "Error: " + error.message;
    }
  }
  
  // Stream a response
  function streamResponse() {
    const prompt = document.getElementById('prompt').value;
    const responseEl = document.getElementById('response');
    responseEl.textContent = '';
    
    client.streamText(
      prompt,
      (chunk) => {
        responseEl.textContent += chunk.chunk;
      }
    );
  }
</script>
```

### Step 10: Update Environment Configuration

Update your component's environment configuration to use the standardized variables:

```bash
# .env file example
RHETOR_URL=http://localhost:8003
RHETOR_DEFAULT_PROVIDER=anthropic
RHETOR_DEFAULT_MODEL=claude-3-haiku-20240307
RHETOR_AUTH_TOKEN=your_auth_token  # if needed
```

## Component-Specific Migration Notes

### LLMAdapter Component

The LLMAdapter component should be phased out entirely in favor of using the Rhetor component directly. During transition, it can be modified to redirect requests to Rhetor.

### Terma Component

Replace `terma/core/llm_adapter.py` with the `TektonLLMClient` and update the terminal chat interface to use the streaming capabilities.

### Hermes Component

Replace `hermes/core/llm_adapter.py` with `TektonLLMClient` and update service registration to use Rhetor for LLM capabilities.

### Engram Component

Replace custom LLM integration with `TektonLLMClient` and update memory augmentation to use Rhetor's context management.

### Telos Component

Replace `telos/core/llm_adapter.py` with `TektonLLMClient` and update requirement analysis functions to use Rhetor.

## Common Patterns

### Handling Streaming Responses

```python
import asyncio
from tekton_llm_client import TektonLLMClient
from tekton_llm_client.utils import StreamProcessor

async def streaming_example():
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Using a StreamProcessor to collect chunks
    processor = StreamProcessor()
    
    async for chunk in client.generate_text(
        prompt="Write a short story about AI.", 
        streaming=True
    ):
        processor.process_chunk(chunk)
        print(chunk.chunk, end="", flush=True)
    
    # Get the complete text
    complete_text = processor.get_result()
    print(f"\nComplete text ({len(complete_text)} chars)")
    
    await client.shutdown()
```

### Graceful Degradation

```python
client = TektonLLMClient(
    component_id="my-component",
    use_fallback=True,  # Enable fallback
    provider_id="anthropic",
    model_id="claude-3-opus-20240229",
)

# With fallback options
response = await client.generate_text(
    prompt="Complex reasoning task",
    options={
        "fallback_provider": "openai",
        "fallback_model": "gpt-4o",
    }
)

# Check if fallback was used
if response.fallback:
    logger.info(f"Used fallback provider: {response.provider}")
```

### Token Management

```python
from tekton_llm_client.utils import (
    count_tokens, optimize_messages_for_token_limit
)

# Count tokens
text = "Long document to analyze..."
token_count = count_tokens(text, model="claude-3-sonnet-20240229")

# If too long, truncate or optimize
if token_count > 100000:
    # Optimize messages to fit within limits
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": text}
    ]
    
    optimized_messages = optimize_messages_for_token_limit(
        messages=messages,
        max_tokens=100000,
        model="claude-3-sonnet-20240229",
        keep_system_prompt=True
    )
```

## Need Help?

If you encounter issues during migration, please:

1. Check the `tekton-llm-client` documentation
2. Review the API reference
3. Contact the Tekton team for assistance