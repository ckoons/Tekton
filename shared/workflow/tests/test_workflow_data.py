#!/usr/bin/env python3
"""
Test workflow data management functionality.

Tests the centralized workflow data storage in .tekton/workflows/data/
"""

import os
import json
import tempfile
import shutil
from datetime import datetime
import pytest
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_handler import WorkflowHandler, WorkflowMessage


class TestComponent(WorkflowHandler):
    """Test implementation of workflow handler."""
    
    async def look_for_work(self):
        return {"status": "success", "found": 0}
    
    async def process_sprint(self, payload):
        return {"status": "success", "processed": True}


class TestWorkflowData:
    """Test workflow data management."""
    
    @pytest.fixture
    def temp_tekton_root(self):
        """Create temporary TEKTON_ROOT for testing."""
        temp_dir = tempfile.mkdtemp()
        old_root = os.environ.get('TEKTON_ROOT')
        os.environ['TEKTON_ROOT'] = temp_dir
        yield temp_dir
        # Cleanup
        if old_root:
            os.environ['TEKTON_ROOT'] = old_root
        else:
            del os.environ['TEKTON_ROOT']
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def handler(self):
        """Create test handler instance."""
        return TestComponent('test_component')
    
    def test_workflow_id_generation(self, handler):
        """Test workflow ID generation."""
        sprint_name = "Test_Sprint"
        workflow_id = handler.generate_workflow_id(sprint_name)
        
        # Check format
        assert workflow_id.startswith("test_")  # _Sprint is removed
        assert len(workflow_id.split('_')) >= 7  # name + date parts
        
        # Test with _Sprint suffix removal
        workflow_id2 = handler.generate_workflow_id("Another_Sprint")
        assert workflow_id2.startswith("another_")
    
    def test_workflow_directory_creation(self, handler, temp_tekton_root):
        """Test workflow directory is created."""
        workflow_dir = handler._get_workflow_dir()
        expected = os.path.join(temp_tekton_root, '.tekton', 'workflows', 'data')
        assert workflow_dir == expected
        
        # Save data should create directory
        workflow_id = "test_workflow_123"
        data = {"test": "data"}
        handler.save_workflow_data(workflow_id, data)
        
        assert os.path.exists(workflow_dir)
    
    def test_save_and_load_workflow_data(self, handler, temp_tekton_root):
        """Test saving and loading workflow data."""
        workflow_id = "test_workflow_123"
        test_data = {
            "sprint_name": "Test_Sprint",
            "tasks": [
                {"id": "t1", "name": "Task 1"},
                {"id": "t2", "name": "Task 2"}
            ]
        }
        
        # Save data
        path = handler.save_workflow_data(workflow_id, test_data)
        assert os.path.exists(path)
        
        # Load data
        loaded_data = handler.load_workflow_data(workflow_id)
        assert loaded_data["sprint_name"] == "Test_Sprint"
        assert len(loaded_data["tasks"]) == 2
        assert "metadata" in loaded_data
        assert loaded_data["metadata"]["updated_by"] == "test_component"
    
    def test_workflow_data_update(self, handler, temp_tekton_root):
        """Test updating existing workflow data."""
        workflow_id = "test_workflow_456"
        
        # Initial save
        initial_data = {"stage1": {"status": "complete"}}
        handler.save_workflow_data(workflow_id, initial_data)
        
        # Update with new data
        update_data = {"stage2": {"status": "in_progress"}}
        handler.save_workflow_data(workflow_id, update_data)
        
        # Load and verify merge
        loaded = handler.load_workflow_data(workflow_id)
        assert "stage1" in loaded
        assert "stage2" in loaded
        assert loaded["stage1"]["status"] == "complete"
        assert loaded["stage2"]["status"] == "in_progress"
    
    def test_prepare_data_payload_embedded(self, handler):
        """Test data payload preparation for small data."""
        small_data = {"key": "value", "count": 123}
        payload = handler.prepare_data_payload(small_data)
        
        assert payload["type"] == "embedded"
        assert payload["content"] == small_data
    
    def test_prepare_data_payload_reference(self, handler):
        """Test data payload preparation for large data."""
        # Create data larger than 10KB
        large_data = {"items": [{"id": i, "data": "x" * 100} for i in range(200)]}
        payload = handler.prepare_data_payload(large_data)
        
        assert payload["type"] == "reference"
        assert "size_bytes" in payload
        assert payload["size_bytes"] > 10 * 1024
    
    def test_load_nonexistent_workflow(self, handler, temp_tekton_root):
        """Test loading non-existent workflow raises error."""
        with pytest.raises(FileNotFoundError):
            handler.load_workflow_data("nonexistent_workflow")
    
    def test_backward_compatibility(self, handler, temp_tekton_root):
        """Test backward compatibility with sprint directories."""
        sprint_name = "Test_Sprint"
        sprint_dir = os.path.join(
            temp_tekton_root,
            'MetaData',
            'DevelopmentSprints',
            f'{sprint_name}_Sprint'
        )
        os.makedirs(sprint_dir)
        
        # Update sprint directory
        test_data = {"compatibility": "test"}
        handler._update_sprint_directory(sprint_name, test_data)
        
        # Check file was created
        output_file = os.path.join(sprint_dir, 'test_component_output.json')
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
        assert saved_data["compatibility"] == "test"


@pytest.mark.asyncio
class TestWorkflowDataAsync:
    """Test async workflow data operations."""
    
    @pytest.fixture
    def temp_tekton_root(self):
        """Create temporary TEKTON_ROOT for testing."""
        temp_dir = tempfile.mkdtemp()
        old_root = os.environ.get('TEKTON_ROOT')
        os.environ['TEKTON_ROOT'] = temp_dir
        
        # Create sprint directory with DAILY_LOG
        sprint_dir = os.path.join(
            temp_dir,
            'MetaData',
            'DevelopmentSprints',
            'Test_Sprint_Sprint'
        )
        os.makedirs(sprint_dir)
        
        with open(os.path.join(sprint_dir, 'DAILY_LOG.md'), 'w') as f:
            f.write("# Test Sprint Daily Log\n\n## Sprint Status: Created\n")
        
        yield temp_dir
        
        # Cleanup
        if old_root:
            os.environ['TEKTON_ROOT'] = old_root
        else:
            del os.environ['TEKTON_ROOT']
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def handler(self):
        """Create test handler instance."""
        return TestComponent('test_component')
    
    async def test_export_data(self, handler, temp_tekton_root):
        """Test export_data functionality."""
        result = await handler.export_data({
            "sprint_name": "Test_Sprint",
            "data": {"exported": "data"}
        })
        
        assert result["status"] == "success"
        assert "workflow_id" in result
        assert "workflow_path" in result
        
        # Verify data was saved
        workflow_data = handler.load_workflow_data(result["workflow_id"])
        assert workflow_data["test_component"]["exported"] == "data"
    
    async def test_import_embedded_data(self, handler):
        """Test importing embedded data."""
        result = await handler.import_data({
            "data": {
                "type": "embedded",
                "content": {"test": "data"}
            }
        })
        
        assert result["status"] == "success"
        assert result["data"]["test"] == "data"
    
    async def test_import_reference_data(self, handler, temp_tekton_root):
        """Test importing reference data."""
        # First save some data
        workflow_id = "test_import_123"
        test_data = {
            "other_component": {"source": "data"},
            "test_component": {"target": "data"}
        }
        handler.save_workflow_data(workflow_id, test_data)
        
        # Import with reference
        result = await handler.import_data({
            "from_component": "other_component",
            "data": {
                "type": "reference",
                "workflow_id": workflow_id
            }
        })
        
        assert result["status"] == "success"
        assert result["data"]["source"] == "data"
        assert "workflow_data" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])