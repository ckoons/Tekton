"""
JSON-RPC 2.0 Protocol Implementation for A2A

Handles JSON-RPC message creation, parsing, and validation according to the
JSON-RPC 2.0 specification.
"""

import json
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from .errors import ParseError, InvalidRequestError


class JSONRPCMessage:
    """Base class for JSON-RPC messages"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        raise NotImplementedError
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())


class JSONRPCRequest(JSONRPCMessage):
    """JSON-RPC 2.0 Request"""
    
    def __init__(
        self, 
        method: str, 
        params: Optional[Union[Dict[str, Any], List[Any]]] = None,
        id: Optional[Union[str, int]] = None
    ):
        self.jsonrpc = "2.0"
        self.method = method
        self.params = params
        self.id = id
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "jsonrpc": self.jsonrpc,
            "method": self.method
        }
        if self.params is not None:
            result["params"] = self.params
        if self.id is not None:
            result["id"] = self.id
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JSONRPCRequest':
        """Create request from dictionary"""
        if "jsonrpc" not in data or data["jsonrpc"] != "2.0":
            raise InvalidRequestError("Missing or invalid jsonrpc version")
        
        if "method" not in data:
            raise InvalidRequestError("Missing method")
        
        return cls(
            method=data["method"],
            params=data.get("params"),
            id=data.get("id")
        )


class JSONRPCResponse(JSONRPCMessage):
    """JSON-RPC 2.0 Response"""
    
    def __init__(
        self,
        id: Union[str, int, None],
        result: Optional[Any] = None,
        error: Optional[Dict[str, Any]] = None
    ):
        if result is not None and error is not None:
            raise ValueError("Response cannot have both result and error")
        
        if result is None and error is None:
            raise ValueError("Response must have either result or error")
        
        self.jsonrpc = "2.0"
        self.id = id
        self.result = result
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        
        if self.result is not None:
            result["result"] = self.result
        elif self.error is not None:
            result["error"] = self.error
        
        return result
    
    @property
    def is_error(self) -> bool:
        """Check if response is an error"""
        return self.error is not None


class JSONRPCError(JSONRPCMessage):
    """JSON-RPC 2.0 Error object"""
    
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "code": self.code,
            "message": self.message
        }
        if self.data is not None:
            result["data"] = self.data
        return result


class JSONRPCBatch:
    """JSON-RPC 2.0 Batch Request/Response"""
    
    def __init__(self, messages: List[Union[JSONRPCRequest, JSONRPCResponse]]):
        if not messages:
            raise ValueError("Batch cannot be empty")
        self.messages = messages
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert batch to list of dictionaries"""
        return [msg.to_dict() for msg in self.messages]
    
    def to_json(self) -> str:
        """Convert batch to JSON string"""
        return json.dumps(self.to_dict())


def parse_jsonrpc_message(data: Union[str, Dict, List]) -> Union[JSONRPCRequest, JSONRPCBatch, None]:
    """Parse JSON-RPC message from various input formats"""
    
    # Parse JSON string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ParseError(str(e))
    
    # Handle batch requests
    if isinstance(data, list):
        if not data:
            raise InvalidRequestError("Batch cannot be empty")
        
        requests = []
        for item in data:
            if not isinstance(item, dict):
                raise InvalidRequestError("Invalid batch item")
            requests.append(JSONRPCRequest.from_dict(item))
        
        return JSONRPCBatch(requests)
    
    # Handle single request
    elif isinstance(data, dict):
        return JSONRPCRequest.from_dict(data)
    
    else:
        raise InvalidRequestError("Invalid request type")


def create_error_response(
    id: Union[str, int, None],
    code: int,
    message: str,
    data: Optional[Any] = None
) -> JSONRPCResponse:
    """Create a JSON-RPC error response"""
    error = JSONRPCError(code, message, data)
    return JSONRPCResponse(id=id, error=error.to_dict())


def create_success_response(
    id: Union[str, int],
    result: Any
) -> JSONRPCResponse:
    """Create a JSON-RPC success response"""
    return JSONRPCResponse(id=id, result=result)