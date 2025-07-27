#!/usr/bin/env python3
"""
Test core workflow handler functionality.

Tests the base WorkflowHandler class and message routing.
"""

import os
import sys
import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_handler import WorkflowHandler, WorkflowMessage


class MockComponent(WorkflowHandler):
    """Mock component for testing."""
    
    def __init__(self, component_name: str):
        super().__init__(component_name)
        self.look_for_work_called = False
        self.process_sprint_called = False
        self.last_payload = None
    
    async def look_for_work(self):
        self.look_for_work_called = True
        return {"status": "success", "found": 2, "items": ["sprint1", "sprint2"]}
    
    async def process_sprint(self, payload):
        self.process_sprint_called = True
        self.last_payload = payload
        return {"status": "success", "processed": payload.get("sprint_name")}


class TestWorkflowHandler:
    """Test the base WorkflowHandler class."""
    
    @pytest.fixture
    def handler(self):
        """Create mock handler instance."""
        return MockComponent('test_component')
    
    def test_initialization(self, handler):
        """Test handler initialization."""
        assert handler.component_name == 'test_component'
        assert handler.router is not None
        assert isinstance(handler.ports, dict)
        # Port should match environment or default
        expected_port = int(os.getenv('TELOS_PORT', '8011'))
        assert handler.ports['telos'] == expected_port
    
    def test_port_configuration(self):
        """Test port configuration loading."""
        handler = MockComponent('test')
        # Ports should come from environment or defaults
        expected_ports = {
            'telos': int(os.getenv('TELOS_PORT', '8011')),
            'prometheus': int(os.getenv('PROMETHEUS_PORT', '8012')),
            'metis': int(os.getenv('METIS_PORT', '8013')),
            'harmonia': int(os.getenv('HARMONIA_PORT', '8014')),
            'synthesis': int(os.getenv('SYNTHESIS_PORT', '8015')),
            'tekton': int(os.getenv('TEKTONCORE_PORT', '8080')),
            'hermes': int(os.getenv('HERMES_PORT', '8000'))
        }
        assert handler.ports == expected_ports
    
    @pytest.mark.asyncio
    async def test_handle_workflow_wrong_dest(self, handler):
        """Test handling message for wrong destination."""
        message = WorkflowMessage(
            purpose={"other": "do something"},
            dest="other_component",
            payload={"action": "test"}
        )
        
        result = await handler.handle_workflow(message)
        assert result["status"] == "ignored"
        assert result["reason"] == "wrong destination"
    
    @pytest.mark.asyncio
    async def test_handle_workflow_no_purpose(self, handler):
        """Test handling message with no purpose defined."""
        message = WorkflowMessage(
            purpose={"other": "do something"},
            dest="test_component",
            payload={"action": "test"}
        )
        
        result = await handler.handle_workflow(message)
        assert result["status"] == "error"
        assert result["reason"] == "no purpose defined"
    
    @pytest.mark.asyncio
    async def test_handle_workflow_look_for_work(self, handler):
        """Test look_for_work action routing."""
        message = WorkflowMessage(
            purpose={"test_component": "check for work"},
            dest="test_component",
            payload={"action": "look_for_work"}
        )
        
        result = await handler.handle_workflow(message)
        assert result["status"] == "success"
        assert result["found"] == 2
        assert handler.look_for_work_called
    
    @pytest.mark.asyncio
    async def test_handle_workflow_process_sprint(self, handler):
        """Test process_sprint action routing."""
        message = WorkflowMessage(
            purpose={"test_component": "process sprint"},
            dest="test_component",
            payload={
                "action": "process_sprint",
                "sprint_name": "Test_Sprint",
                "status": "Ready"
            }
        )
        
        result = await handler.handle_workflow(message)
        assert result["status"] == "success"
        assert result["processed"] == "Test_Sprint"
        assert handler.process_sprint_called
        assert handler.last_payload["sprint_name"] == "Test_Sprint"
    
    @pytest.mark.asyncio
    async def test_handle_workflow_unknown_action(self, handler):
        """Test handling unknown action."""
        message = WorkflowMessage(
            purpose={"test_component": "do something"},
            dest="test_component",
            payload={"action": "unknown_action"}
        )
        
        result = await handler.handle_workflow(message)
        assert result["status"] == "error"
        assert "unknown action" in result["reason"]
    
    def test_find_sprints_by_status(self, handler, tmp_path):
        """Test finding sprints by status."""
        # Set up test environment
        os.environ['TEKTON_ROOT'] = str(tmp_path)
        
        # Create test sprint directories
        sprints_dir = tmp_path / "MetaData" / "DevelopmentSprints"
        sprints_dir.mkdir(parents=True)
        
        # Sprint 1 - matches
        sprint1_dir = sprints_dir / "Sprint1_Sprint"
        sprint1_dir.mkdir()
        (sprint1_dir / "DAILY_LOG.md").write_text(
            "# Sprint 1\n\n## Sprint Status: Ready-1:Metis\n"
        )
        
        # Sprint 2 - doesn't match
        sprint2_dir = sprints_dir / "Sprint2_Sprint"
        sprint2_dir.mkdir()
        (sprint2_dir / "DAILY_LOG.md").write_text(
            "# Sprint 2\n\n## Sprint Status: Planning\n"
        )
        
        # Sprint 3 - matches
        sprint3_dir = sprints_dir / "Sprint3_Sprint"
        sprint3_dir.mkdir()
        (sprint3_dir / "DAILY_LOG.md").write_text(
            "# Sprint 3\n\n## Sprint Status: Ready-1:Metis\n"
        )
        
        # Find sprints
        matches = handler.find_sprints_by_status("Ready-1:Metis")
        assert len(matches) == 2
        assert "Sprint1" in matches
        assert "Sprint3" in matches
        assert "Sprint2" not in matches


class TestWorkflowMessage:
    """Test WorkflowMessage model."""
    
    def test_message_creation(self):
        """Test creating workflow message."""
        message = WorkflowMessage(
            purpose={"telos": "create proposal"},
            dest="telos",
            payload={"action": "create", "name": "test"}
        )
        
        assert message.purpose == {"telos": "create proposal"}
        assert message.dest == "telos"
        assert message.payload["action"] == "create"
    
    def test_message_serialization(self):
        """Test message serialization."""
        message = WorkflowMessage(
            purpose={"metis": "break down tasks"},
            dest="metis",
            payload={
                "action": "process_sprint",
                "sprint_name": "Test",
                "data": {"tasks": [1, 2, 3]}
            }
        )
        
        # Convert to dict
        msg_dict = message.dict()
        assert msg_dict["dest"] == "metis"
        assert "tasks" in msg_dict["payload"]["data"]
        
        # Convert to JSON
        msg_json = message.json()
        parsed = json.loads(msg_json)
        assert parsed["dest"] == "metis"


@pytest.mark.asyncio
class TestAsyncMethods:
    """Test async workflow methods."""
    
    @pytest.fixture
    def handler(self):
        """Create mock handler with mocked HTTP client."""
        return MockComponent('test_component')
    
    async def test_send_workflow_message(self, handler):
        """Test sending workflow message."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "received"}
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            result = await handler.send_workflow_message(
                "telos",
                {"telos": "test message"},
                {"action": "test"}
            )
            
            assert result["status"] == "received"
    
    async def test_update_status_missing_params(self, handler):
        """Test update_status with missing parameters."""
        result = await handler.update_status({})
        assert result["status"] == "error"
        assert "missing sprint_name" in result["reason"]
    
    async def test_update_status_success(self, handler, tmp_path):
        """Test successful status update."""
        os.environ['TEKTON_ROOT'] = str(tmp_path)
        
        # Create sprint directory with DAILY_LOG
        sprint_dir = tmp_path / "MetaData" / "DevelopmentSprints" / "Test_Sprint"
        sprint_dir.mkdir(parents=True)
        daily_log = sprint_dir / "DAILY_LOG.md"
        daily_log.write_text("# Test Sprint\n\n## Sprint Status: Created\n")
        
        # Update status
        result = await handler.update_status({
            "sprint_name": "Test",
            "old_status": "Created",
            "new_status": "Planning"
        })
        
        assert result["status"] == "success"
        assert result["updated"] == "Planning"
        
        # Verify file was updated
        content = daily_log.read_text()
        assert "Sprint Status: Planning" in content
        assert "Previous Status: Created → Planning" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])