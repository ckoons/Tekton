"""
A2A Protocol Error Definitions

Implements JSON-RPC 2.0 error codes and custom A2A error extensions.
"""

from typing import Any, Dict, Optional


class A2AError(Exception):
    """Base class for all A2A protocol errors"""
    
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"[{code}] {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to JSON-RPC error format"""
        error = {
            "code": self.code,
            "message": self.message
        }
        if self.data is not None:
            error["data"] = self.data
        return error


# JSON-RPC 2.0 Standard Error Codes
class ParseError(A2AError):
    """Invalid JSON was received by the server (-32700)"""
    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32700, "Parse error", data)


class InvalidRequestError(A2AError):
    """The JSON sent is not a valid Request object (-32600)"""
    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32600, "Invalid Request", data)


class MethodNotFoundError(A2AError):
    """The method does not exist / is not available (-32601)"""
    def __init__(self, method: str, data: Optional[Any] = None):
        super().__init__(-32601, f"Method '{method}' not found", data)


class InvalidParamsError(A2AError):
    """Invalid method parameter(s) (-32602)"""
    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32602, "Invalid params", data)


class InternalError(A2AError):
    """Internal JSON-RPC error (-32603)"""
    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32603, "Internal error", data)


# A2A Protocol Custom Error Codes (-32000 to -32099)
class AgentNotFoundError(A2AError):
    """The specified agent does not exist (-32000)"""
    def __init__(self, agent_id: str, data: Optional[Any] = None):
        super().__init__(-32000, f"Agent '{agent_id}' not found", data)


class TaskNotFoundError(A2AError):
    """The specified task does not exist (-32001)"""
    def __init__(self, task_id: str, data: Optional[Any] = None):
        super().__init__(-32001, f"Task '{task_id}' not found", data)


class UnauthorizedError(A2AError):
    """The request lacks valid authentication credentials (-32002)"""
    def __init__(self, message: Optional[str] = None, data: Optional[Any] = None):
        super().__init__(-32002, message or "Unauthorized", data)


class CapabilityNotSupportedError(A2AError):
    """The agent does not support the requested capability (-32003)"""
    def __init__(self, capability: str, data: Optional[Any] = None):
        super().__init__(-32003, f"Capability '{capability}' not supported", data)


class TaskStateError(A2AError):
    """Invalid task state transition (-32004)"""
    def __init__(self, current_state: str, requested_state: str, data: Optional[Any] = None):
        super().__init__(
            -32004, 
            f"Cannot transition from '{current_state}' to '{requested_state}'", 
            data
        )


class RateLimitError(A2AError):
    """Rate limit exceeded (-32005)"""
    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32005, "Rate limit exceeded", data)


class TimeoutError(A2AError):
    """Operation timed out (-32006)"""
    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32006, "Operation timed out", data)


class ConversationNotFoundError(A2AError):
    """The specified conversation does not exist (-32007)"""
    def __init__(self, conversation_id: str, data: Optional[Any] = None):
        super().__init__(-32007, f"Conversation '{conversation_id}' not found", data)