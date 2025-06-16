"""
Utility functions for retrying operations.
"""

import asyncio
import logging
import time
import random
from typing import TypeVar, Callable, Awaitable, Optional, List, Dict, Any, Generic

from ..exceptions import (
    TektonLLMError, ConnectionError, TimeoutError, 
    AuthenticationError, ServiceUnavailableError, 
    RateLimitError, InvalidRequestError
)

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryConfig:
    """Configuration for retry logic."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: int = 1000,  # milliseconds
        max_delay: int = 30000,  # milliseconds
        jitter: bool = True,
        retry_on: Optional[List[type]] = None
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in milliseconds
            max_delay: Maximum delay between retries in milliseconds
            jitter: Whether to add random jitter to the delay
            retry_on: List of exception types to retry on (defaults to connection errors)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        
        # Default exceptions to retry on
        if retry_on is None:
            self.retry_on = [ConnectionError, TimeoutError, ServiceUnavailableError]
        else:
            self.retry_on = retry_on
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if a retry should be attempted.
        
        Args:
            exception: The exception that was raised
            attempt: Current attempt number (zero-based)
            
        Returns:
            True if a retry should be attempted, False otherwise
        """
        # Check if we've exceeded max retries
        if attempt >= self.max_retries:
            return False
            
        # Check if this exception type should be retried
        for exc_type in self.retry_on:
            if isinstance(exception, exc_type):
                return True
                
        # Special handling for rate limit errors
        if isinstance(exception, RateLimitError):
            return True
                
        return False
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate the delay before the next retry attempt.
        
        Args:
            attempt: Current attempt number (zero-based)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay_ms = min(
            self.base_delay * (2 ** attempt),
            self.max_delay
        )
        
        # Add jitter if enabled (±15%)
        if self.jitter:
            jitter_factor = 1.0 + random.uniform(-0.15, 0.15)
            delay_ms = delay_ms * jitter_factor
            
        # Special handling for rate limit errors
        if isinstance(self.last_exception, RateLimitError):
            # Use a longer delay for rate limit errors
            delay_ms = max(delay_ms, 5000)  # At least 5 seconds
            
        # Convert to seconds
        return delay_ms / 1000.0


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    config: Optional[RetryConfig] = None
) -> T:
    """
    Retry an asynchronous operation with exponential backoff.
    
    Args:
        operation: Async function to retry
        config: Retry configuration
        
    Returns:
        Result of the operation
        
    Raises:
        The last exception encountered if all retries fail
    """
    if config is None:
        config = RetryConfig()
        
    attempt = 0
    last_exception = None
    
    while True:
        try:
            return await operation()
        except Exception as e:
            last_exception = e
            
            if config.should_retry(e, attempt):
                # Calculate delay
                delay = config.get_delay(attempt)
                
                logger.warning(
                    f"Retry attempt {attempt + 1}/{config.max_retries} "
                    f"after {delay:.2f}s delay. Error: {str(e)}"
                )
                
                # Wait before retry
                await asyncio.sleep(delay)
                
                attempt += 1
            else:
                # Either max retries exceeded or exception not retryable
                logger.error(
                    f"Operation failed after {attempt + 1} attempts: {str(e)}"
                )
                raise
    
    # This should never be reached
    raise last_exception or TektonLLMError("Unknown error in retry logic")