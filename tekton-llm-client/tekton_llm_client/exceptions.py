"""
Exception classes for the Tekton LLM Client.
"""

class TektonLLMError(Exception):
    """Base exception for all Tekton LLM Client errors."""
    pass

class ConnectionError(TektonLLMError):
    """Raised when a connection to the LLM service cannot be established."""
    pass

class TimeoutError(TektonLLMError):
    """Raised when an operation times out."""
    pass

class AuthenticationError(TektonLLMError):
    """Raised when authentication with the LLM service fails."""
    pass

class ServiceUnavailableError(TektonLLMError):
    """Raised when the LLM service is unavailable."""
    pass

class RateLimitError(TektonLLMError):
    """Raised when the LLM service rate limit is exceeded."""
    pass

class InvalidRequestError(TektonLLMError):
    """Raised when the request to the LLM service is invalid."""
    pass

class AdapterError(TektonLLMError):
    """Raised when there is an error with a specific LLM adapter."""
    
    def __init__(self, adapter_id, message):
        self.adapter_id = adapter_id
        super().__init__(f"Adapter '{adapter_id}' error: {message}")
        
class FallbackError(TektonLLMError):
    """Raised when all fallback options have been exhausted and failed."""
    pass