"""
Unit tests for JSON-RPC 2.0 message handling in A2A Protocol v0.2.1
"""

import pytest
import json
from typing import Dict, Any

from tekton.a2a.jsonrpc import (
    JSONRPCRequest, JSONRPCResponse, JSONRPCError, JSONRPCBatch,
    parse_jsonrpc_message, create_error_response, create_success_response
)
from tekton.a2a.errors import (
    ParseError, InvalidRequestError, MethodNotFoundError,
    InvalidParamsError, InternalError
)


class TestJSONRPCRequest:
    """Test JSON-RPC request creation and validation"""
    
    def test_create_request_with_params(self):
        """Test creating a request with parameters"""
        request = JSONRPCRequest(
            method="test.method",
            params={"key": "value"},
            id="test-123"
        )
        
        assert request.jsonrpc == "2.0"
        assert request.method == "test.method"
        assert request.params == {"key": "value"}
        assert request.id == "test-123"
    
    def test_create_request_without_params(self):
        """Test creating a request without parameters"""
        request = JSONRPCRequest(method="test.method", id=1)
        
        assert request.jsonrpc == "2.0"
        assert request.method == "test.method"
        assert request.params is None
        assert request.id == 1
    
    def test_request_to_dict(self):
        """Test converting request to dictionary"""
        request = JSONRPCRequest(
            method="test.method",
            params={"key": "value"},
            id="test-123"
        )
        
        result = request.to_dict()
        assert result == {
            "jsonrpc": "2.0",
            "method": "test.method",
            "params": {"key": "value"},
            "id": "test-123"
        }
    
    def test_request_to_json(self):
        """Test converting request to JSON string"""
        request = JSONRPCRequest(
            method="test.method",
            params={"key": "value"},
            id="test-123"
        )
        
        result = request.to_json()
        parsed = json.loads(result)
        assert parsed["jsonrpc"] == "2.0"
        assert parsed["method"] == "test.method"
        assert parsed["params"] == {"key": "value"}
        assert parsed["id"] == "test-123"
    
    def test_request_from_dict_valid(self):
        """Test creating request from valid dictionary"""
        data = {
            "jsonrpc": "2.0",
            "method": "test.method",
            "params": {"key": "value"},
            "id": "test-123"
        }
        
        request = JSONRPCRequest.from_dict(data)
        assert request.method == "test.method"
        assert request.params == {"key": "value"}
        assert request.id == "test-123"
    
    def test_request_from_dict_missing_jsonrpc(self):
        """Test error when jsonrpc field is missing"""
        data = {
            "method": "test.method",
            "id": "test-123"
        }
        
        with pytest.raises(InvalidRequestError):
            JSONRPCRequest.from_dict(data)
    
    def test_request_from_dict_invalid_jsonrpc(self):
        """Test error when jsonrpc version is invalid"""
        data = {
            "jsonrpc": "1.0",
            "method": "test.method",
            "id": "test-123"
        }
        
        with pytest.raises(InvalidRequestError):
            JSONRPCRequest.from_dict(data)
    
    def test_request_from_dict_missing_method(self):
        """Test error when method is missing"""
        data = {
            "jsonrpc": "2.0",
            "id": "test-123"
        }
        
        with pytest.raises(InvalidRequestError):
            JSONRPCRequest.from_dict(data)
    
    def test_notification_request(self):
        """Test notification request (no ID)"""
        request = JSONRPCRequest(method="notify.method")
        
        assert request.id is None
        result = request.to_dict()
        assert "id" not in result


class TestJSONRPCResponse:
    """Test JSON-RPC response creation and validation"""
    
    def test_create_success_response(self):
        """Test creating a success response"""
        response = JSONRPCResponse(
            id="test-123",
            result={"status": "ok"}
        )
        
        assert response.jsonrpc == "2.0"
        assert response.id == "test-123"
        assert response.result == {"status": "ok"}
        assert response.error is None
        assert not response.is_error
    
    def test_create_error_response(self):
        """Test creating an error response"""
        response = JSONRPCResponse(
            id="test-123",
            error={"code": -32600, "message": "Invalid Request"}
        )
        
        assert response.jsonrpc == "2.0"
        assert response.id == "test-123"
        assert response.result is None
        assert response.error == {"code": -32600, "message": "Invalid Request"}
        assert response.is_error
    
    def test_response_cannot_have_both_result_and_error(self):
        """Test that response cannot have both result and error"""
        with pytest.raises(ValueError):
            JSONRPCResponse(
                id="test-123",
                result={"status": "ok"},
                error={"code": -32600, "message": "Invalid Request"}
            )
    
    def test_response_must_have_result_or_error(self):
        """Test that response must have either result or error"""
        with pytest.raises(ValueError):
            JSONRPCResponse(id="test-123")
    
    def test_response_to_dict(self):
        """Test converting response to dictionary"""
        response = JSONRPCResponse(
            id="test-123",
            result={"status": "ok"}
        )
        
        result = response.to_dict()
        assert result == {
            "jsonrpc": "2.0",
            "id": "test-123",
            "result": {"status": "ok"}
        }


class TestJSONRPCError:
    """Test JSON-RPC error object"""
    
    def test_create_error(self):
        """Test creating an error object"""
        error = JSONRPCError(
            code=-32600,
            message="Invalid Request",
            data="Additional info"
        )
        
        assert error.code == -32600
        assert error.message == "Invalid Request"
        assert error.data == "Additional info"
    
    def test_error_to_dict_with_data(self):
        """Test converting error to dictionary with data"""
        error = JSONRPCError(
            code=-32600,
            message="Invalid Request",
            data={"detail": "Missing field"}
        )
        
        result = error.to_dict()
        assert result == {
            "code": -32600,
            "message": "Invalid Request",
            "data": {"detail": "Missing field"}
        }
    
    def test_error_to_dict_without_data(self):
        """Test converting error to dictionary without data"""
        error = JSONRPCError(
            code=-32600,
            message="Invalid Request"
        )
        
        result = error.to_dict()
        assert result == {
            "code": -32600,
            "message": "Invalid Request"
        }


class TestJSONRPCBatch:
    """Test JSON-RPC batch handling"""
    
    def test_create_batch(self):
        """Test creating a batch of requests"""
        requests = [
            JSONRPCRequest(method="method1", id=1),
            JSONRPCRequest(method="method2", id=2),
            JSONRPCRequest(method="method3", id=3)
        ]
        
        batch = JSONRPCBatch(requests)
        assert len(batch.messages) == 3
    
    def test_batch_cannot_be_empty(self):
        """Test that batch cannot be empty"""
        with pytest.raises(ValueError):
            JSONRPCBatch([])
    
    def test_batch_to_dict(self):
        """Test converting batch to list of dictionaries"""
        requests = [
            JSONRPCRequest(method="method1", id=1),
            JSONRPCRequest(method="method2", id=2)
        ]
        
        batch = JSONRPCBatch(requests)
        result = batch.to_dict()
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["method"] == "method1"
        assert result[1]["method"] == "method2"
    
    def test_batch_to_json(self):
        """Test converting batch to JSON string"""
        requests = [
            JSONRPCRequest(method="method1", id=1),
            JSONRPCRequest(method="method2", id=2)
        ]
        
        batch = JSONRPCBatch(requests)
        result = batch.to_json()
        parsed = json.loads(result)
        
        assert isinstance(parsed, list)
        assert len(parsed) == 2


class TestParseJSONRPCMessage:
    """Test parsing JSON-RPC messages"""
    
    def test_parse_single_request_from_dict(self):
        """Test parsing a single request from dictionary"""
        data = {
            "jsonrpc": "2.0",
            "method": "test.method",
            "params": {"key": "value"},
            "id": "test-123"
        }
        
        result = parse_jsonrpc_message(data)
        assert isinstance(result, JSONRPCRequest)
        assert result.method == "test.method"
        assert result.params == {"key": "value"}
        assert result.id == "test-123"
    
    def test_parse_single_request_from_json(self):
        """Test parsing a single request from JSON string"""
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "test.method",
            "params": {"key": "value"},
            "id": "test-123"
        })
        
        result = parse_jsonrpc_message(data)
        assert isinstance(result, JSONRPCRequest)
        assert result.method == "test.method"
    
    def test_parse_batch_request(self):
        """Test parsing a batch request"""
        data = [
            {
                "jsonrpc": "2.0",
                "method": "method1",
                "id": 1
            },
            {
                "jsonrpc": "2.0",
                "method": "method2",
                "id": 2
            }
        ]
        
        result = parse_jsonrpc_message(data)
        assert isinstance(result, JSONRPCBatch)
        assert len(result.messages) == 2
        assert result.messages[0].method == "method1"
        assert result.messages[1].method == "method2"
    
    def test_parse_empty_batch_error(self):
        """Test error when parsing empty batch"""
        with pytest.raises(InvalidRequestError):
            parse_jsonrpc_message([])
    
    def test_parse_invalid_json_error(self):
        """Test error when parsing invalid JSON"""
        with pytest.raises(ParseError):
            parse_jsonrpc_message("{invalid json")
    
    def test_parse_invalid_type_error(self):
        """Test error when parsing invalid type"""
        with pytest.raises(InvalidRequestError):
            parse_jsonrpc_message(12345)


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_create_error_response(self):
        """Test creating an error response"""
        response = create_error_response(
            id="test-123",
            code=-32600,
            message="Invalid Request",
            data="Additional info"
        )
        
        assert isinstance(response, JSONRPCResponse)
        assert response.id == "test-123"
        assert response.is_error
        assert response.error["code"] == -32600
        assert response.error["message"] == "Invalid Request"
        assert response.error["data"] == "Additional info"
    
    def test_create_success_response(self):
        """Test creating a success response"""
        response = create_success_response(
            id="test-123",
            result={"status": "ok"}
        )
        
        assert isinstance(response, JSONRPCResponse)
        assert response.id == "test-123"
        assert not response.is_error
        assert response.result == {"status": "ok"}