"""
Unit tests for the standardized workflow endpoint template.
"""

import sys
import os
import json
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from endpoint_template import create_workflow_endpoint


class TestWorkflowEndpoint:
    """Test the standardized workflow endpoint functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a test FastAPI app with the workflow endpoint
        self.app = FastAPI()
        self.component_name = "test_component"
        
        # Add the workflow endpoint
        workflow_router = create_workflow_endpoint(self.component_name)
        self.app.include_router(workflow_router)
        
        # Create test client
        self.client = TestClient(self.app)
    
    def test_valid_check_work_message(self):
        """Test a valid check_work message."""
        message = {
            "purpose": "check_work",
            "dest": self.component_name,
            "payload": {
                "component": self.component_name,
                "action": "look_for_work"
            }
        }
        
        with patch('shared.workflow.endpoint_template.WorkflowHandler') as mock_handler_class:
            # Mock the workflow handler
            mock_handler = Mock()
            mock_handler.check_for_work.return_value = []
            mock_handler_class.return_value = mock_handler
            
            response = self.client.post("/workflow", json=message)
            
            assert response.status_code == 200
            result = response.json()
            
            assert result["status"] == "success"
            assert result["component"] == self.component_name
            assert result["work_available"] == False
            assert result["work_count"] == 0
            assert result["work_items"] == []
            
            # Verify the handler was called correctly
            mock_handler.check_for_work.assert_called_once_with(self.component_name)
    
    def test_valid_check_work_with_work_available(self):
        """Test check_work when work is available."""
        message = {
            "purpose": "check_work",
            "dest": self.component_name,
            "payload": {
                "component": self.component_name,
                "action": "look_for_work"
            }
        }
        
        # Mock work items
        mock_work_items = [
            {
                "workflow_id": "test_workflow_2025_01_27_123456",
                "workflow_file": "test_workflow_2025_01_27_123456.json",
                "status": "pending",
                "component_tasks": [{"action": "process", "data": {}}]
            }
        ]
        
        with patch('shared.workflow.endpoint_template.WorkflowHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler.check_for_work.return_value = mock_work_items
            mock_handler_class.return_value = mock_handler
            
            response = self.client.post("/workflow", json=message)
            
            assert response.status_code == 200
            result = response.json()
            
            assert result["status"] == "success"
            assert result["work_available"] == True
            assert result["work_count"] == 1
            assert result["work_items"] == mock_work_items
    
    def test_invalid_destination(self):
        """Test message with wrong destination."""
        message = {
            "purpose": "check_work",
            "dest": "wrong_component",
            "payload": {
                "component": "wrong_component",
                "action": "look_for_work"
            }
        }
        
        response = self.client.post("/workflow", json=message)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["status"] == "error"
        assert "does not match component" in result["message"]
        assert result["component"] == self.component_name
    
    def test_missing_required_fields(self):
        """Test message missing required fields."""
        message = {
            "purpose": "check_work"
            # Missing "dest" and "payload"
        }
        
        response = self.client.post("/workflow", json=message)
        
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "Missing required fields" in detail
        assert "dest" in detail
        assert "payload" in detail
    
    def test_invalid_json(self):
        """Test invalid JSON input."""
        response = self.client.post("/workflow", json="not a dict")
        
        assert response.status_code == 400
        assert "Message must be a JSON object" in response.json()["detail"]
    
    def test_unimplemented_purpose(self):
        """Test message with unimplemented purpose."""
        message = {
            "purpose": "unknown_purpose",
            "dest": self.component_name,
            "payload": {
                "component": self.component_name,
                "action": "unknown_action"
            }
        }
        
        response = self.client.post("/workflow", json=message)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["status"] == "not_implemented"
        assert result["purpose"] == "unknown_purpose"
        assert result["component"] == self.component_name
        assert "not yet implemented" in result["message"]
    
    def test_workflow_handler_exception(self):
        """Test handling of WorkflowHandler exceptions."""
        message = {
            "purpose": "check_work",
            "dest": self.component_name,
            "payload": {
                "component": self.component_name,
                "action": "look_for_work"
            }
        }
        
        with patch('shared.workflow.endpoint_template.WorkflowHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler.check_for_work.side_effect = Exception("Test error")
            mock_handler_class.return_value = mock_handler
            
            response = self.client.post("/workflow", json=message)
            
            assert response.status_code == 200
            result = response.json()
            
            assert result["status"] == "error"
            assert "Internal error" in result["message"]
            assert "Test error" in result["message"]
            assert result["component"] == self.component_name


def test_create_workflow_endpoint():
    """Test the create_workflow_endpoint function."""
    router = create_workflow_endpoint("apollo")
    
    # Check that the router was created
    assert router is not None
    
    # Check that it has the expected route
    route_paths = [route.path for route in router.routes]
    assert "/workflow" in route_paths