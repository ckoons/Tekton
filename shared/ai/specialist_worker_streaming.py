"""
Enhanced CI Specialist Worker with native streaming support.

This extends the base specialist worker to support native Ollama streaming
for real-time progressive responses.
"""
import os
import sys
import json
import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, AsyncIterator
from abc import ABC, abstractmethod

# Import the base worker
from .specialist_worker import CISpecialistWorker

# Import landmarks
try:
    from landmarks import (
        architecture_decision,
        performance_boundary,
        integration_point,
        state_checkpoint
    )
except ImportError:
    # If landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Native Streaming Support for Greek Chorus AIs",
    rationale="Enable real-time progressive responses with metadata for monitoring line of criticality",
    alternatives_considered=["Simulated chunking", "Batch responses", "WebSockets"],
    impacts=["latency", "user_experience", "observability"],
    decided_by="Casey"
)
@integration_point(
    title="Ollama Streaming Integration",
    target_component="Ollama API",
    protocol="HTTP streaming",
    data_flow="Prompt → Ollama stream=True → Chunks → Socket stream"
)
class StreamingAISpecialistWorker(CISpecialistWorker):
    """Enhanced CI Specialist Worker with streaming support."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Streaming configuration
        self.supports_streaming = True
        self.streaming_chunk_size = 50  # Characters per chunk for pacing
        
        # Add streaming handlers
        self.handlers['chat'] = self._handle_chat_with_streaming
        
        # Track active streams
        self.active_streams: Dict[str, Dict[str, Any]] = {}
    
    async def _handle_chat_with_streaming(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat message with optional streaming support."""
        if message.get('stream', False) and self.supports_streaming:
            # Note: For streaming, we need to handle this differently
            # The response will be sent as multiple messages over the socket
            request_id = message.get('request_id', str(uuid.uuid4()))
            asyncio.create_task(self._stream_chat_response(message, request_id))
            
            # Return acknowledgment
            return {
                'type': 'stream_start',
                'request_id': request_id,
                'ai_id': self.ai_id
            }
        else:
            # Fall back to non-streaming behavior
            return await super()._handle_chat(message)
    
    async def _stream_chat_response(self, message: Dict[str, Any], request_id: str):
        """Stream chat response over the socket connection."""
        writer = message.get('_writer')  # Socket writer passed from handle_client
        if not writer:
            logger.error("No writer available for streaming")
            return
        
        try:
            prompt = message.get('content', '')
            chunk_index = 0
            total_tokens = 0
            start_time = time.time()
            
            # Stream from Ollama
            if self.model_provider == 'ollama':
                async for chunk_content in self._stream_ollama(prompt):
                    # Estimate tokens
                    chunk_tokens = len(chunk_content) // 4
                    total_tokens += chunk_tokens
                    
                    # Calculate metadata
                    elapsed = time.time() - start_time
                    perplexity = 0.85 + (chunk_index * 0.01)  # Simulated for now
                    reasoning_depth = min(3, chunk_index // 10)  # Increases with length
                    
                    # Send chunk
                    chunk_message = {
                        'type': 'stream_chunk',
                        'request_id': request_id,
                        'content': chunk_content,
                        'chunk_index': chunk_index,
                        'metadata': {
                            'tokens_so_far': total_tokens,
                            'perplexity': perplexity,
                            'reasoning_depth': reasoning_depth,
                            'elapsed_time': elapsed,
                            'ai_id': self.ai_id
                        }
                    }
                    
                    writer.write(json.dumps(chunk_message).encode() + b'\n')
                    await writer.drain()
                    
                    chunk_index += 1
                    
                    # Small delay for backpressure handling
                    await asyncio.sleep(0.01)
            
            # Send completion message
            completion_message = {
                'type': 'stream_end',
                'request_id': request_id,
                'metadata': {
                    'total_chunks': chunk_index,
                    'total_tokens': total_tokens,
                    'total_time': time.time() - start_time,
                    'ai_id': self.ai_id,
                    'model': self.model_name
                }
            }
            
            writer.write(json.dumps(completion_message).encode() + b'\n')
            await writer.drain()
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            # Send error message
            error_message = {
                'type': 'stream_error',
                'request_id': request_id,
                'error': str(e),
                'ai_id': self.ai_id
            }
            try:
                writer.write(json.dumps(error_message).encode() + b'\n')
                await writer.drain()
            except:
                pass
    
    @performance_boundary(
        title="Ollama Streaming Handler",
        sla="<100ms first token",
        optimization_notes="Direct streaming without buffering",
        metrics={"chunk_size": "variable", "backpressure": "0.01s"}
    )
    async def _stream_ollama(self, prompt: str) -> AsyncIterator[str]:
        """Stream response from Ollama API."""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                # Send streaming request
                async with client.stream(
                    'POST',
                    'http://localhost:11434/api/generate',
                    json={
                        'model': self.model_name,
                        'prompt': f"{self.get_system_prompt()}\n\nUser: {prompt}\n\nAssistant:",
                        'stream': True
                    },
                    timeout=60.0
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if 'response' in data:
                                    yield data['response']
                                
                                # Check if done
                                if data.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse Ollama response: {line}")
                                continue
                                
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            yield f"[Streaming error: {e}]"
    
    async def handle_client(self, reader: asyncio.StreamReader, 
                          writer: asyncio.StreamWriter):
        """Enhanced client handler that supports streaming."""
        client_addr = writer.get_extra_info('peername')
        self.logger.info(f"Client connected: {client_addr}")
        self.clients.append(writer)
        
        try:
            while True:
                # Read message
                data = await reader.readline()
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    msg_type = message.get('type', 'unknown')
                    
                    # Add writer reference for streaming
                    message['_writer'] = writer
                    
                    # Get handler
                    handler = self.handlers.get(msg_type, self.process_message)
                    
                    # Process message
                    self.logger.debug(f"Processing message type: {msg_type}")
                    response = await handler(message)
                    
                    # Only send response if not streaming
                    if response and response.get('type') != 'stream_start':
                        writer.write(json.dumps(response).encode() + b'\n')
                        await writer.drain()
                    
                except json.JSONDecodeError:
                    error_response = {'type': 'error', 'error': 'Invalid JSON'}
                    writer.write(json.dumps(error_response).encode() + b'\n')
                    await writer.drain()
                    
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.logger.error(f"Client error: {e}")
        finally:
            self.clients.remove(writer)
            writer.close()
            await writer.wait_closed()
            self.logger.info(f"Client disconnected: {client_addr}")