# Rhetor Integration Guide

## Overview

This guide explains how to integrate your Tekton component with Rhetor for LLM capabilities. Rhetor provides a unified interface for working with large language models, handling model selection, prompt management, and budget optimization.

## Prerequisites

- A Tekton component that needs LLM capabilities
- Rhetor installed and running (typically on port 8005)
- Python 3.10 or higher
- Rhetor client library

## Integration Steps

### 1. Install the Rhetor Client

Add the Rhetor client to your component's dependencies:

```bash
pip install tekton-rhetor-client
```

Or, if working within the Tekton repository:

```bash
# From your component directory
pip install -e ../Rhetor
```

### 2. Configure Environment Variables

Set up the environment variables for Rhetor connection:

```bash
# .env file
RHETOR_HOST=localhost
RHETOR_PORT=8005
RHETOR_API_KEY=your_api_key_here
```

In your component, load these variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

rhetor_config = {
    "host": os.getenv("RHETOR_HOST", "localhost"),
    "port": int(os.getenv("RHETOR_PORT", 8005)),
    "api_key": os.getenv("RHETOR_API_KEY", "")
}
```

### 3. Create a Rhetor Client

Initialize the Rhetor client in your component:

```python
from rhetor.client import RhetorClient

class MyComponent:
    def __init__(self):
        self.rhetor = RhetorClient(
            host=rhetor_config["host"],
            port=rhetor_config["port"],
            api_key=rhetor_config["api_key"]
        )
        # Other initialization code...
```

### 4. Basic Text Generation

Generate text completions:

```python
async def generate_text(self, prompt, temperature=0.7):
    """Generate text from a prompt."""
    try:
        response = await self.rhetor.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=500
        )
        
        return response.text
    except Exception as e:
        print(f"Text generation error: {str(e)}")
        return f"Error generating text: {str(e)}"
```

### 5. Streaming Text Generation

Stream text completions in real-time:

```python
async def generate_text_stream(self, prompt, callback, temperature=0.7):
    """Generate text with streaming response."""
    try:
        # Initialize accumulator for the full response
        full_response = ""
        
        # Stream the response
        async for chunk in self.rhetor.generate_stream(
            prompt=prompt,
            temperature=temperature,
            max_tokens=1000
        ):
            # Append to the full response
            full_response += chunk
            
            # Call the callback with the chunk
            await callback(chunk)
        
        return full_response
    except Exception as e:
        print(f"Streaming text generation error: {str(e)}")
        error_message = f"Error generating text: {str(e)}"
        await callback(error_message)
        return error_message
```

### 6. Chat Interface

Implement a chat interface:

```python
class ChatSession:
    def __init__(self, rhetor_client, system_prompt="You are a helpful assistant."):
        self.rhetor = rhetor_client
        self.messages = [{"role": "system", "content": system_prompt}]
        self.session_id = self._generate_session_id()
    
    def _generate_session_id(self):
        """Generate a unique session ID."""
        import uuid
        return f"sess-{uuid.uuid4()}"
    
    async def send_message(self, message, stream=False):
        """Send a message to the chat session."""
        # Add the user message to the conversation
        self.messages.append({"role": "user", "content": message})
        
        try:
            if stream:
                # For streaming response
                full_response = ""
                
                async for chunk in self.rhetor.chat_stream(
                    messages=self.messages,
                    temperature=0.7
                ):
                    full_response += chunk
                    yield chunk
                
                # Add the assistant response to the conversation
                self.messages.append({"role": "assistant", "content": full_response})
                
            else:
                # For non-streaming response
                response = await self.rhetor.chat(
                    messages=self.messages,
                    temperature=0.7
                )
                
                # Add the assistant response to the conversation
                self.messages.append({"role": "assistant", "content": response.message.content})
                
                return response.message.content
                
        except Exception as e:
            error_message = f"Error in chat: {str(e)}"
            print(error_message)
            return error_message
```

### 7. Working with Templates

Create and use prompt templates:

```python
# Creating a template
async def create_template(self):
    """Create a reusable prompt template."""
    try:
        template_id = await self.rhetor.create_template(
            name="bug_report_analysis",
            content="""Analyze the following bug report and provide insights:

Bug Description:
{bug_description}

Steps to Reproduce:
{reproduction_steps}

Expected Behavior:
{expected_behavior}

Actual Behavior:
{actual_behavior}

Environment:
{environment}

Please provide:
1. A root cause analysis
2. Potential solutions
3. Severity assessment (low, medium, high, critical)
4. Estimated effort to fix (hours)""",
            metadata={
                "description": "Template for analyzing software bug reports",
                "required_parameters": [
                    "bug_description", 
                    "reproduction_steps", 
                    "expected_behavior", 
                    "actual_behavior"
                ],
                "optional_parameters": ["environment"]
            }
        )
        
        return template_id
    except Exception as e:
        print(f"Template creation error: {str(e)}")
        return None

# Using a template
async def analyze_bug_report(self, 
                            bug_description, 
                            reproduction_steps, 
                            expected_behavior, 
                            actual_behavior, 
                            environment="Not specified"):
    """Analyze a bug report using the template."""
    try:
        response = await self.rhetor.generate_from_template(
            template_name="bug_report_analysis",
            parameters={
                "bug_description": bug_description,
                "reproduction_steps": reproduction_steps,
                "expected_behavior": expected_behavior,
                "actual_behavior": actual_behavior,
                "environment": environment
            },
            temperature=0.3  # Lower temperature for analytical tasks
        )
        
        return response.text
    except Exception as e:
        print(f"Bug report analysis error: {str(e)}")
        return f"Error analyzing bug report: {str(e)}"
```

### 8. Model Selection and Routing

Use Rhetor's model routing capabilities:

```python
async def generate_with_routing(self, prompt, task_type, complexity):
    """Generate text using automatic model routing."""
    try:
        response = await self.rhetor.generate(
            prompt=prompt,
            routing_parameters={
                "task_type": task_type,  # e.g., "creative", "analytical", "coding"
                "complexity": complexity,  # e.g., "low", "medium", "high"
                "required_capabilities": self._get_capabilities_for_task(task_type),
                "max_cost": self._get_cost_limit_for_task(task_type, complexity)
            }
        )
        
        return {
            "text": response.text,
            "model": response.model,
            "provider": response.provider,
            "routing_explanation": response.routing_explanation
        }
    except Exception as e:
        print(f"Text generation with routing error: {str(e)}")
        return {"error": str(e)}
    
def _get_capabilities_for_task(self, task_type):
    """Get required capabilities for a task type."""
    capabilities_map = {
        "creative": ["creative_writing", "storytelling"],
        "analytical": ["reasoning", "analysis"],
        "coding": ["code_generation", "debugging"],
        "educational": ["explanation", "teaching"]
    }
    
    return capabilities_map.get(task_type, ["general"])

def _get_cost_limit_for_task(self, task_type, complexity):
    """Get cost limit based on task type and complexity."""
    # Base cost limits
    base_limits = {
        "creative": 0.05,
        "analytical": 0.08,
        "coding": 0.10,
        "educational": 0.06
    }
    
    # Complexity multipliers
    multipliers = {
        "low": 0.5,
        "medium": 1.0,
        "high": 2.0
    }
    
    base_limit = base_limits.get(task_type, 0.05)
    multiplier = multipliers.get(complexity, 1.0)
    
    return base_limit * multiplier
```

### 9. Budget Management

Implement budget-aware LLM usage:

```python
async def check_budget_before_generation(self, prompt, model=None):
    """Check budget before generating text."""
    try:
        # Estimate cost
        estimate = await self.rhetor.estimate_cost(
            prompt=prompt,
            model=model,
            max_tokens=1000
        )
        
        print(f"Estimated cost: ${estimate['estimated_cost']}")
        print(f"Estimated tokens: {estimate['estimated_tokens']['total_tokens']}")
        
        # Check if under budget
        if estimate["under_budget"]:
            # Proceed with generation
            response = await self.rhetor.generate(
                prompt=prompt,
                model=model,
                max_tokens=1000
            )
            
            return response.text
        else:
            # Budget exceeded, try a cheaper alternative
            return await self._generate_with_cheaper_alternative(prompt)
    
    except Exception as e:
        print(f"Budget check error: {str(e)}")
        return f"Error checking budget: {str(e)}"

async def _generate_with_cheaper_alternative(self, prompt):
    """Generate text using a cheaper model."""
    try:
        # Try with a cheaper model
        response = await self.rhetor.generate(
            prompt=prompt,
            model="gpt-3.5-turbo",  # Cheaper than GPT-4 or Claude
            max_tokens=500  # Reduced max tokens
        )
        
        return response.text + "\n\n[Note: Generated with a more economical model due to budget constraints]"
    except Exception as e:
        print(f"Cheaper alternative generation error: {str(e)}")
        return "Unable to generate response due to budget constraints."
```

### 10. Evaluation and Quality Assurance

Implement quality checks for LLM outputs:

```python
async def generate_with_evaluation(self, prompt, criteria=None):
    """Generate text and evaluate its quality."""
    if criteria is None:
        criteria = ["accuracy", "clarity", "relevance"]
    
    try:
        # Generate the response
        response = await self.rhetor.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Evaluate the response
        evaluation = await self.rhetor.evaluate(
            prompt=prompt,
            response=response.text,
            criteria=criteria
        )
        
        # Check if quality meets threshold
        overall_score = evaluation["evaluation"]["overall_score"]
        
        result = {
            "text": response.text,
            "evaluation": evaluation["evaluation"],
            "meets_quality_standard": overall_score >= 7.0
        }
        
        # If quality is poor, regenerate with improvements
        if overall_score < 7.0:
            improved_response = await self._regenerate_with_improvements(
                prompt, 
                response.text, 
                evaluation["evaluation"]["feedback"]
            )
            
            result["improved_text"] = improved_response
        
        return result
    
    except Exception as e:
        print(f"Evaluation error: {str(e)}")
        return {"error": str(e)}

async def _regenerate_with_improvements(self, original_prompt, original_response, feedback):
    """Regenerate the response with improvements based on feedback."""
    improvement_prompt = f"""I need to improve the following response to the prompt:

Original Prompt: {original_prompt}

Original Response: {original_response}

Feedback on the original response: {feedback}

Please provide an improved response that addresses the feedback.
"""
    
    try:
        # Generate improved response
        improved = await self.rhetor.generate(
            prompt=improvement_prompt,
            temperature=0.5,  # Lower temperature for more focused improvements
            max_tokens=1200  # Allow slightly more tokens for improvements
        )
        
        return improved.text
    except Exception as e:
        print(f"Regeneration error: {str(e)}")
        return "Error generating improved response."
```

### 11. WebSocket Communication

Connect to Rhetor WebSocket for real-time streaming:

```python
import asyncio
import websockets
import json
import uuid

class RhetorWebSocketClient:
    def __init__(self, host="localhost", port=8005, api_key=None):
        self.host = host
        self.port = port
        self.api_key = api_key
        self.ws = None
    
    async def connect(self):
        """Connect to the Rhetor WebSocket."""
        uri = f"ws://{self.host}:{self.port}/ws/rhetor/streaming?api_key={self.api_key}"
        
        try:
            self.ws = await websockets.connect(uri)
            return True
        except Exception as e:
            print(f"WebSocket connection error: {str(e)}")
            return False
    
    async def generate_stream(self, prompt, model=None, temperature=0.7):
        """Generate text with streaming via WebSocket."""
        if not self.ws:
            if not await self.connect():
                raise Exception("Failed to connect to WebSocket")
        
        # Create request
        request = {
            "prompt": prompt,
            "temperature": temperature,
            "stream": True
        }
        
        if model:
            request["model"] = model
        
        # Send request
        await self.ws.send(json.dumps(request))
        
        # Get streaming response
        full_text = ""
        while True:
            try:
                response = json.loads(await self.ws.recv())
                
                if response["type"] == "content_chunk":
                    chunk = response["text"]
                    full_text += chunk
                    yield chunk
                elif response["type"] == "content_complete":
                    break
                elif response["type"] == "error":
                    raise Exception(response["error"])
            except websockets.exceptions.ConnectionClosed:
                raise Exception("WebSocket connection closed")
        
        return full_text
    
    async def close(self):
        """Close the WebSocket connection."""
        if self.ws:
            await self.ws.close()
```

### 12. Create a Helper Module for Rhetor Integration

To simplify Rhetor integration across your codebase, create a helper module:

```python
# rhetor_helper.py
from rhetor.client import RhetorClient
import os
import asyncio
import json

class RhetorHelper:
    """Helper class for Rhetor integration."""
    
    def __init__(self, component_id=None, host=None, port=None, api_key=None):
        """Initialize the Rhetor helper."""
        self.component_id = component_id or "unknown_component"
        self.host = host or os.getenv("RHETOR_HOST", "localhost")
        self.port = int(port or os.getenv("RHETOR_PORT", 8005))
        self.api_key = api_key or os.getenv("RHETOR_API_KEY", "")
        
        self.client = RhetorClient(
            host=self.host,
            port=self.port,
            api_key=self.api_key
        )
        
        self.session_contexts = {}
    
    async def generate(self, prompt, **kwargs):
        """Generate text with default settings for the component."""
        # Set component-specific metadata
        metadata = kwargs.pop("metadata", {})
        metadata.update({
            "component": self.component_id,
            "request_id": f"req-{uuid.uuid4()}"
        })
        
        try:
            response = await self.client.generate(
                prompt=prompt,
                metadata=metadata,
                **kwargs
            )
            
            return response.text
        except Exception as e:
            print(f"Generation error: {str(e)}")
            return self._get_fallback_response(str(e))
    
    async def generate_stream(self, prompt, callback, **kwargs):
        """Generate streaming text with a callback."""
        # Set component-specific metadata
        metadata = kwargs.pop("metadata", {})
        metadata.update({
            "component": self.component_id,
            "request_id": f"req-{uuid.uuid4()}"
        })
        
        try:
            full_text = ""
            async for chunk in self.client.generate_stream(
                prompt=prompt,
                metadata=metadata,
                **kwargs
            ):
                full_text += chunk
                await callback(chunk)
            
            return full_text
        except Exception as e:
            error_message = f"Streaming error: {str(e)}"
            print(error_message)
            await callback(self._get_fallback_response(str(e)))
            return self._get_fallback_response(str(e))
    
    async def create_chat_session(self, session_id=None, system_prompt=None):
        """Create a new chat session."""
        session_id = session_id or f"sess-{uuid.uuid4()}"
        system_prompt = system_prompt or "You are a helpful assistant."
        
        self.session_contexts[session_id] = {
            "messages": [{"role": "system", "content": system_prompt}]
        }
        
        return session_id
    
    async def chat_send_message(self, session_id, message, stream=False, callback=None, **kwargs):
        """Send a message in a chat session."""
        if session_id not in self.session_contexts:
            await self.create_chat_session(session_id)
        
        # Add the user message
        self.session_contexts[session_id]["messages"].append({
            "role": "user", 
            "content": message
        })
        
        # Set component-specific metadata
        metadata = kwargs.pop("metadata", {})
        metadata.update({
            "component": self.component_id,
            "session_id": session_id,
            "request_id": f"req-{uuid.uuid4()}"
        })
        
        try:
            if stream and callback:
                full_response = ""
                async for chunk in self.client.chat_stream(
                    messages=self.session_contexts[session_id]["messages"],
                    metadata=metadata,
                    **kwargs
                ):
                    full_response += chunk
                    await callback(chunk)
                
                # Add the assistant response
                self.session_contexts[session_id]["messages"].append({
                    "role": "assistant", 
                    "content": full_response
                })
                
                return full_response
            else:
                response = await self.client.chat(
                    messages=self.session_contexts[session_id]["messages"],
                    metadata=metadata,
                    **kwargs
                )
                
                # Add the assistant response
                self.session_contexts[session_id]["messages"].append({
                    "role": "assistant", 
                    "content": response.message.content
                })
                
                return response.message.content
        except Exception as e:
            error_message = f"Chat error: {str(e)}"
            print(error_message)
            return self._get_fallback_response(str(e))
    
    async def use_template(self, template_name, parameters, **kwargs):
        """Generate text using a template."""
        try:
            response = await self.client.generate_from_template(
                template_name=template_name,
                parameters=parameters,
                **kwargs
            )
            
            return response.text
        except Exception as e:
            print(f"Template error: {str(e)}")
            return self._get_fallback_response(str(e))
    
    def _get_fallback_response(self, error):
        """Get a fallback response when an error occurs."""
        return f"I'm sorry, but I encountered an issue processing your request. Please try again later. (Error: {error})"
```

### 13. Use the Helper in Your Component

Integrate the helper in your component:

```python
from my_component.utils.rhetor_helper import RhetorHelper

class MyComponent:
    def __init__(self):
        # Create Rhetor helper
        self.rhetor = RhetorHelper(component_id="my_component")
        
        # Other initialization...
    
    async def process_user_query(self, query, stream=False):
        """Process a user query using LLM."""
        if stream:
            chunks = []
            
            async def collect_chunks(chunk):
                chunks.append(chunk)
                # Also send to frontend or other output
                await self.send_to_frontend(chunk)
            
            result = await self.rhetor.generate_stream(
                prompt=query,
                callback=collect_chunks,
                temperature=0.7
            )
            
            return result
        else:
            return await self.rhetor.generate(
                prompt=query,
                temperature=0.7
            )
    
    async def handle_chat_session(self, session_id, message):
        """Handle a message in a chat session."""
        return await self.rhetor.chat_send_message(
            session_id=session_id,
            message=message,
            temperature=0.7
        )
    
    async def analyze_code(self, code, language):
        """Analyze code using a template."""
        return await self.rhetor.use_template(
            template_name="code_analysis",
            parameters={
                "code": code,
                "language": language
            },
            temperature=0.3  # Lower temperature for code analysis
        )
```

## Common Integration Patterns

### Fallback Chain

Implement a fallback chain for model availability:

```python
async def generate_with_fallbacks(self, prompt, max_retries=3):
    """Generate text with automatic fallbacks."""
    models = [
        {"name": "claude-3-opus-20240229", "provider": "anthropic"},
        {"name": "claude-3-sonnet-20240229", "provider": "anthropic"},
        {"name": "gpt-4", "provider": "openai"},
        {"name": "gpt-3.5-turbo", "provider": "openai"}
    ]
    
    for attempt, model_info in enumerate(models):
        try:
            if attempt > 0:
                print(f"Falling back to {model_info['name']} (attempt {attempt+1})")
            
            response = await self.rhetor.generate(
                prompt=prompt,
                model=model_info["name"],
                provider=model_info["provider"],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.text
        except Exception as e:
            print(f"Error with {model_info['name']}: {str(e)}")
            
            # If we've tried all models, give up
            if attempt == len(models) - 1:
                return "I'm sorry, but I'm unable to generate a response at this time. Please try again later."
```

### Context Management

Maintain conversation context efficiently:

```python
class ContextManager:
    def __init__(self, rhetor_client, max_tokens=4000):
        self.rhetor = rhetor_client
        self.max_tokens = max_tokens
        self.conversations = {}
    
    async def add_message(self, conversation_id, role, content):
        """Add a message to the conversation context."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append({
            "role": role,
            "content": content
        })
        
        # Check if we need to trim the context
        await self._trim_context_if_needed(conversation_id)
    
    async def get_context(self, conversation_id):
        """Get the current conversation context."""
        return self.conversations.get(conversation_id, [])
    
    async def generate_response(self, conversation_id, user_message):
        """Generate a response in the conversation context."""
        # Add user message
        await self.add_message(conversation_id, "user", user_message)
        
        # Get the current context
        context = await self.get_context(conversation_id)
        
        # Generate response
        response = await self.rhetor.chat(
            messages=context,
            temperature=0.7
        )
        
        # Add assistant response to the context
        await self.add_message(conversation_id, "assistant", response.message.content)
        
        return response.message.content
    
    async def _trim_context_if_needed(self, conversation_id):
        """Trim the context if it's too long."""
        context = self.conversations[conversation_id]
        
        if len(context) < 3:
            return  # Need at least system + user + assistant messages
        
        # Count tokens (simplified - you'd use a real token counter)
        total_tokens = sum(len(msg["content"].split()) * 1.3 for msg in context)
        
        if total_tokens > self.max_tokens:
            # Keep system message
            system_message = next((msg for msg in context if msg["role"] == "system"), None)
            
            # Summarize the conversation
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
            summary_prompt = f"Summarize the following conversation concisely while preserving key information:\n\n{conversation_text}"
            
            summary = await self.rhetor.generate(
                prompt=summary_prompt,
                temperature=0.3,
                max_tokens=400
            )
            
            # Create new context with system message, summary, and last few messages
            new_context = []
            if system_message:
                new_context.append(system_message)
            
            new_context.append({
                "role": "system",
                "content": f"Previous conversation summary: {summary.text}"
            })
            
            # Add the most recent messages
            new_context.extend(context[-4:])
            
            # Update the conversation
            self.conversations[conversation_id] = new_context
```

### Multi-model Collaboration

Use multiple models for different aspects of a task:

```python
async def analyze_document_with_multiple_models(self, document):
    """Analyze a document using multiple specialized models."""
    tasks = {
        "summarization": {
            "prompt": f"Summarize the following document concisely:\n\n{document}",
            "model": "claude-3-haiku-20240307",
            "temperature": 0.3
        },
        "key_points": {
            "prompt": f"Extract the 5 most important points from this document:\n\n{document}",
            "model": "gpt-3.5-turbo",
            "temperature": 0.2
        },
        "sentiment": {
            "prompt": f"Analyze the sentiment of this document (positive, negative, or neutral) and explain why:\n\n{document}",
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.1
        },
        "action_items": {
            "prompt": f"Identify all action items or next steps mentioned in this document:\n\n{document}",
            "model": "gpt-4",
            "temperature": 0.2
        }
    }
    
    results = {}
    
    # Process tasks in parallel
    async def process_task(task_name, task_info):
        try:
            response = await self.rhetor.generate(
                prompt=task_info["prompt"],
                model=task_info.get("model"),
                temperature=task_info.get("temperature", 0.7)
            )
            results[task_name] = {
                "result": response.text,
                "model": response.model
            }
        except Exception as e:
            results[task_name] = {
                "error": str(e)
            }
    
    # Run all tasks concurrently
    await asyncio.gather(*[
        process_task(task_name, task_info) 
        for task_name, task_info in tasks.items()
    ])
    
    # Synthesize the results with another model
    synthesis_prompt = f"""Synthesize the following analyses of a document into a comprehensive report:

Summary: {results.get('summarization', {}).get('result', 'No summary available')}

Key Points: {results.get('key_points', {}).get('result', 'No key points available')}

Sentiment: {results.get('sentiment', {}).get('result', 'No sentiment analysis available')}

Action Items: {results.get('action_items', {}).get('result', 'No action items available')}

Provide an integrated report that brings all these analyses together.
"""
    
    synthesis = await self.rhetor.generate(
        prompt=synthesis_prompt,
        model="claude-3-opus-20240229",
        temperature=0.4
    )
    
    results["synthesis"] = {
        "result": synthesis.text,
        "model": synthesis.model
    }
    
    return results
```

## Testing Rhetor Integration

### Unit Testing with Mocks

Create mocks for testing Rhetor integration:

```python
# test_rhetor_integration.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

class MockRhetorResponse:
    def __init__(self, text, model="test-model", provider="test"):
        self.text = text
        self.model = model
        self.provider = provider
        self.message = MagicMock()
        self.message.content = text

@pytest.fixture
def mock_rhetor_client():
    """Create a mock Rhetor client."""
    mock = AsyncMock()
    mock.generate = AsyncMock(return_value=MockRhetorResponse("Generated text"))
    mock.chat = AsyncMock(return_value=MockRhetorResponse("Chat response"))
    mock.generate_from_template = AsyncMock(return_value=MockRhetorResponse("Template response"))
    
    # Setup streaming mock
    async def mock_stream(*args, **kwargs):
        chunks = ["This ", "is ", "a ", "streamed ", "response"]
        for chunk in chunks:
            yield chunk
    
    mock.generate_stream = mock_stream
    
    return mock

@pytest.mark.asyncio
async def test_text_generation(mock_rhetor_client):
    """Test basic text generation."""
    with patch('my_component.utils.rhetor_helper.RhetorClient', return_value=mock_rhetor_client):
        from my_component.utils.rhetor_helper import RhetorHelper
        helper = RhetorHelper("test_component")
        
        result = await helper.generate("Test prompt")
        
        assert result == "Generated text"
        mock_rhetor_client.generate.assert_called_once()
        
        # Check call arguments
        call_args = mock_rhetor_client.generate.call_args[1]
        assert call_args["prompt"] == "Test prompt"
        assert call_args["metadata"]["component"] == "test_component"
```

### Integration Testing with Rhetor

Create integration tests with a real Rhetor instance:

```python
# integration_test_rhetor.py
import pytest
import os
import asyncio
from my_component.utils.rhetor_helper import RhetorHelper

@pytest.mark.integration
@pytest.mark.asyncio
async def test_rhetor_integration():
    """Test integration with a real Rhetor instance."""
    # Ensure Rhetor is running
    rhetor_host = os.getenv("TEST_RHETOR_HOST", "localhost")
    rhetor_port = int(os.getenv("TEST_RHETOR_PORT", 8005))
    
    helper = RhetorHelper(
        component_id="test_integration",
        host=rhetor_host,
        port=rhetor_port
    )
    
    # Test text generation
    response = await helper.generate(
        prompt="Write a haiku about testing",
        temperature=0.7
    )
    
    assert response and len(response) > 0
    print(f"Generated haiku: {response}")
    
    # Test chat
    session_id = await helper.create_chat_session(
        system_prompt="You are a helpful test assistant that responds very briefly."
    )
    
    chat_response = await helper.chat_send_message(
        session_id=session_id,
        message="What is the purpose of testing software?"
    )
    
    assert chat_response and len(chat_response) > 0
    print(f"Chat response: {chat_response}")
```

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Ensure Rhetor is running at the specified host and port
   - Check firewall settings

2. **Authentication Failure**:
   - Verify the API key is correct
   - Check if API keys are properly configured in Rhetor

3. **Model Not Available**:
   - Verify that the requested model is available in your Rhetor configuration
   - Check if the provider API keys are configured

4. **Budget Exceeded**:
   - Check budget limits in Rhetor
   - Use model routing or fallbacks to less expensive models

5. **Context Too Long**:
   - Implement context summarization or truncation
   - Break long messages into smaller chunks

### Debugging Tools

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger('rhetor').setLevel(logging.DEBUG)
   ```

2. **Test Direct Requests**:
   ```bash
   curl -X POST http://localhost:8005/api/rhetor/completions \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_api_key" \
     -d '{"prompt": "Hello, world!", "temperature": 0.7}'
   ```

3. **Check Rhetor Logs**:
   Examine the Rhetor logs for errors or warnings related to your requests.

4. **Monitor Usage and Costs**:
   Check the Rhetor budget API to monitor usage and costs:
   ```bash
   curl http://localhost:8005/api/rhetor/budget/usage \
     -H "X-API-Key: your_api_key"
   ```

## Best Practices

1. **Use Templates for Common Tasks**:
   Create and use templates for repetitive prompt patterns to ensure consistency.

2. **Implement Fallback Mechanisms**:
   Always include fallbacks for when preferred models are unavailable.

3. **Be Budget-Conscious**:
   Check costs before sending requests and use appropriate models for the task.

4. **Manage Context Efficiently**:
   Implement context windowing or summarization for long conversations.

5. **Stream Responses when Appropriate**:
   Use streaming for better user experience with longer responses.

6. **Cache Common Responses**:
   Implement caching for frequently requested information.

7. **Use Model Routing**:
   Let Rhetor select the most appropriate model based on the task.

8. **Handle Errors Gracefully**:
   Provide helpful fallback responses when errors occur.

9. **Evaluate Response Quality**:
   Use Rhetor's evaluation capabilities to ensure high-quality outputs.

10. **Monitor Usage and Performance**:
    Regularly check usage statistics and adjust settings as needed.

## Resources

- [Rhetor API Reference](./API_REFERENCE.md)
- [Rhetor Client Documentation](https://docs.example.com/rhetor-client)
- [LLM Integration Guide](../../TektonDocumentation/Architecture/LLMIntegrationPlan.md)