"""
Utility functions for handling streaming responses.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Callable, Union
from ..models import StreamingChunk

logger = logging.getLogger(__name__)

class StreamProcessor:
    """Helper class for processing streaming responses."""
    
    def __init__(self, callback: Optional[Callable[[StreamingChunk], None]] = None):
        """
        Initialize the stream processor.
        
        Args:
            callback: Optional callback function for each chunk
        """
        self.callback = callback
        self.buffer = ""
        self.chunks = []
        self.is_complete = False
        self.has_error = False
        self.error = None
    
    def process_chunk(self, chunk: StreamingChunk) -> None:
        """
        Process a streaming chunk.
        
        Args:
            chunk: The chunk to process
        """
        # Store the chunk
        self.chunks.append(chunk)
        
        # Add to buffer
        self.buffer += chunk.chunk
        
        # Check for completion
        if chunk.done:
            self.is_complete = True
            
        # Check for error
        if chunk.error:
            self.has_error = True
            self.error = chunk.error
            
        # Call the callback if provided
        if self.callback:
            self.callback(chunk)
    
    def get_result(self) -> str:
        """
        Get the complete result as a string.
        
        Returns:
            The complete text from all chunks
        """
        return self.buffer
    
    def get_chunks(self) -> List[StreamingChunk]:
        """
        Get all received chunks.
        
        Returns:
            List of StreamingChunk objects
        """
        return self.chunks
    
    async def process_stream(
        self, 
        stream: AsyncGenerator[StreamingChunk, None]
    ) -> str:
        """
        Process a stream until completion.
        
        Args:
            stream: AsyncGenerator yielding StreamingChunk objects
            
        Returns:
            The complete text from all chunks
        """
        async for chunk in stream:
            self.process_chunk(chunk)
            
            if chunk.done:
                break
                
        return self.get_result()

class StreamBuffer:
    """
    Buffer for managing streaming responses across different components.
    
    This is useful for cases where multiple components need to process
    the same streaming response.
    """
    
    def __init__(self, capacity: int = 100):
        """
        Initialize the stream buffer.
        
        Args:
            capacity: Maximum number of chunks to store in the buffer
        """
        self.chunks = []
        self.capacity = capacity
        self.lock = asyncio.Lock()
        self.new_chunk_event = asyncio.Event()
        self.done = False
    
    async def add_chunk(self, chunk: StreamingChunk) -> None:
        """
        Add a chunk to the buffer.
        
        Args:
            chunk: The chunk to add
        """
        async with self.lock:
            self.chunks.append(chunk)
            
            # Maintain buffer capacity
            if len(self.chunks) > self.capacity:
                self.chunks = self.chunks[-self.capacity:]
                
            # Mark as done if this is the final chunk
            if chunk.done:
                self.done = True
                
            # Signal that a new chunk is available
            self.new_chunk_event.set()
            self.new_chunk_event.clear()
    
    async def get_chunks(
        self, 
        start_index: int = 0
    ) -> AsyncGenerator[StreamingChunk, None]:
        """
        Get chunks from the buffer starting at a specific index.
        
        Args:
            start_index: Index to start from
            
        Yields:
            StreamingChunk objects
        """
        current_index = start_index
        
        while True:
            # Check if we have chunks to return
            if current_index < len(self.chunks):
                # Return all available chunks
                while current_index < len(self.chunks):
                    yield self.chunks[current_index]
                    current_index += 1
                    
                    # Break if we've reached the end
                    if self.done and current_index >= len(self.chunks):
                        break
            elif self.done:
                # No more chunks and stream is done
                break
            else:
                # Wait for new chunks
                await self.new_chunk_event.wait()
    
    async def get_all_chunks(self) -> List[StreamingChunk]:
        """
        Get all chunks in the buffer.
        
        Returns:
            List of all StreamingChunk objects
        """
        async with self.lock:
            return self.chunks.copy()
    
    def get_combined_text(self) -> str:
        """
        Get the combined text from all chunks.
        
        Returns:
            Combined text as string
        """
        return "".join(chunk.chunk for chunk in self.chunks)
    
    def is_done(self) -> bool:
        """
        Check if the stream is complete.
        
        Returns:
            True if the stream is complete, False otherwise
        """
        return self.done
    
    def has_error(self) -> bool:
        """
        Check if any chunk contains an error.
        
        Returns:
            True if an error was encountered, False otherwise
        """
        return any(chunk.error for chunk in self.chunks)
    
    def get_error(self) -> Optional[str]:
        """
        Get the first error encountered in the stream.
        
        Returns:
            Error message or None if no error
        """
        for chunk in self.chunks:
            if chunk.error:
                return chunk.error
        return None