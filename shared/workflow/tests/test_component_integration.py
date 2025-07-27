#!/usr/bin/env python3
"""
Integration tests for component workflow handoffs.

Tests the complete workflow from one component to another.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_handler import WorkflowHandler, WorkflowMessage
from shared.env import TektonEnviron


class MetisHandler(WorkflowHandler):
    """Mock Metis component handler."""
    
    async def process_sprint(self, payload):
        """Process sprint and create task breakdown."""
        sprint_name = payload.get("sprint_name")
        
        # Simulate task breakdown
        task_data = {
            "tasks": [
                {"id": "t1", "name": "Update UI", "complexity": 3},
                {"id": "t2", "name": "Add tests", "complexity": 2}
            ],
            "phases": [{"name": "Phase 1", "tasks": ["t1", "t2"]}],
            "total_complexity": 5
        }
        
        # Export data
        export_result = await self.export_data({
            "sprint_name": sprint_name,
            "data": task_data
        })
        
        if export_result["status"] == "success":
            # Notify Harmonia
            await self.notify_next_component(
                "harmonia",
                sprint_name,
                "Ready-2:Harmonia",
                task_data,
                export_result["workflow_id"]
            )
        
        return {"status": "success", "tasks_created": 2}


class HarmoniaHandler(WorkflowHandler):
    """Mock Harmonia component handler."""
    
    async def process_sprint(self, payload):
        """Process task breakdown into workflows."""
        sprint_name = payload.get("sprint_name")
        from_component = payload.get("from_component")
        
        # Import data from previous component
        import_result = await self.import_data(payload)
        
        if import_result["status"] != "success":
            return import_result
        
        task_data = import_result["data"]
        
        # Create workflows from tasks
        workflow_data = {
            "workflows": [
                {
                    "id": "wf1",
                    "name": "UI Update Workflow",
                    "tasks": task_data.get("tasks", [])
                }
            ],
            "execution_plan": {
                "order": ["wf1"],
                "parallel": False
            }
        }
        
        return {
            "status": "success",
            "workflows_created": 1,
            "source_tasks": len(task_data.get("tasks", []))
        }


class TestComponentIntegration:
    """Test component workflow integration."""
    
    @pytest.fixture
    def temp_env(self):
        """Set up temporary environment."""
        temp_dir = tempfile.mkdtemp()
        old_root = TektonEnviron.get('TEKTON_ROOT')
        os.environ['TEKTON_ROOT'] = temp_dir
        
        # Create sprint directory
        sprint_dir = os.path.join(
            temp_dir,
            'MetaData',
            'DevelopmentSprints',
            'Integration_Test_Sprint'
        )
        os.makedirs(sprint_dir)
        
        # Create DAILY_LOG
        with open(os.path.join(sprint_dir, 'DAILY_LOG.md'), 'w') as f:
            f.write("# Integration Test Sprint\n\n## Sprint Status: Ready-1:Metis\n")
        
        yield temp_dir
        
        # Cleanup
        if old_root:
            os.environ['TEKTON_ROOT'] = old_root
        else:
            if 'TEKTON_ROOT' in os.environ:
                del os.environ['TEKTON_ROOT']
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def metis(self):
        """Create Metis handler."""
        return MetisHandler('metis')
    
    @pytest.fixture
    def harmonia(self):
        """Create Harmonia handler."""
        return HarmoniaHandler('harmonia')
    
    @pytest.mark.asyncio
    async def test_metis_to_harmonia_handoff(self, metis, harmonia, temp_env):
        """Test complete handoff from Metis to Harmonia."""
        sprint_name = "Integration_Test"
        
        # Mock the HTTP call to Harmonia
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "received"}
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            # Process sprint in Metis
            metis_result = await metis.process_sprint({
                "sprint_name": sprint_name,
                "status": "Ready-1:Metis"
            })
            
            assert metis_result["status"] == "success"
            assert metis_result["tasks_created"] == 2
        
        # Verify workflow data was saved
        workflow_dir = os.path.join(temp_env, '.tekton', 'workflows', 'data')
        assert os.path.exists(workflow_dir)
        
        # Find the workflow file
        workflow_files = os.listdir(workflow_dir)
        assert len(workflow_files) == 1
        workflow_id = workflow_files[0].replace('.json', '')
        
        # Load and verify workflow data
        with open(os.path.join(workflow_dir, workflow_files[0]), 'r') as f:
            workflow_data = json.load(f)
        
        assert workflow_data["sprint_name"] == sprint_name
        assert "metis" in workflow_data
        assert len(workflow_data["metis"]["tasks"]) == 2
        
        # Verify backward compatibility
        sprint_output = os.path.join(
            temp_env,
            'MetaData',
            'DevelopmentSprints',
            f'{sprint_name}_Sprint',
            'metis_output.json'
        )
        assert os.path.exists(sprint_output)
    
    @pytest.mark.asyncio
    async def test_embedded_data_flow(self, metis, harmonia, temp_env):
        """Test workflow with embedded data (small payload)."""
        # Create small task data
        small_data = {"tasks": [{"id": "t1", "name": "Simple task"}]}
        
        # Prepare message for Harmonia
        message = WorkflowMessage(
            purpose={"harmonia": "Process small data"},
            dest="harmonia",
            payload={
                "action": "process_sprint",
                "sprint_name": "Small_Test",
                "from_component": "metis",
                "data": {
                    "type": "embedded",
                    "content": small_data
                }
            }
        )
        
        # Process in Harmonia
        result = await harmonia.handle_workflow(message)
        assert result["status"] == "success"
        assert result["source_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_reference_data_flow(self, metis, harmonia, temp_env):
        """Test workflow with reference data (large payload)."""
        sprint_name = "Large_Test"
        workflow_id = metis.generate_workflow_id(sprint_name)
        
        # Create large task data
        large_data = {
            "tasks": [{"id": f"t{i}", "name": f"Task {i}", "data": "x" * 1000} 
                     for i in range(50)]
        }
        
        # Save as Metis would
        workflow_data = {
            "workflow_id": workflow_id,
            "sprint_name": sprint_name,
            "metis": large_data
        }
        metis.save_workflow_data(workflow_id, workflow_data)
        
        # Prepare reference message
        message = WorkflowMessage(
            purpose={"harmonia": "Process large data"},
            dest="harmonia",
            payload={
                "action": "process_sprint",
                "sprint_name": sprint_name,
                "from_component": "metis",
                "data": {
                    "type": "reference",
                    "workflow_id": workflow_id
                }
            }
        )
        
        # Process in Harmonia
        result = await harmonia.handle_workflow(message)
        assert result["status"] == "success"
        assert result["source_tasks"] == 50
    
    @pytest.mark.asyncio
    async def test_status_updates_during_handoff(self, metis, temp_env):
        """Test that status is properly updated during handoffs."""
        sprint_name = "Integration_Test"
        
        # Check initial status
        daily_log_path = os.path.join(
            temp_env,
            'MetaData',
            'DevelopmentSprints',
            f'{sprint_name}_Sprint',
            'DAILY_LOG.md'
        )
        
        with open(daily_log_path, 'r') as f:
            initial_content = f.read()
        assert "Ready-1:Metis" in initial_content
        
        # Mock the notify call
        with patch.object(metis, 'send_workflow_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"status": "success"}
            
            # Process sprint
            await metis.process_sprint({
                "sprint_name": sprint_name,
                "status": "Ready-1:Metis"
            })
        
        # Check status was updated
        with open(daily_log_path, 'r') as f:
            updated_content = f.read()
        assert "Ready-2:Harmonia" in updated_content
        assert "Previous Status:" in updated_content
    
    @pytest.mark.asyncio
    async def test_error_handling_missing_data(self, harmonia):
        """Test error handling when data is missing."""
        message = WorkflowMessage(
            purpose={"harmonia": "Process without data"},
            dest="harmonia",
            payload={
                "action": "process_sprint",
                "sprint_name": "Error_Test"
            }
        )
        
        result = await harmonia.handle_workflow(message)
        assert result["status"] == "error"
        assert "no data provided" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_error_handling_missing_workflow(self, harmonia):
        """Test error handling when workflow file doesn't exist."""
        message = WorkflowMessage(
            purpose={"harmonia": "Process missing workflow"},
            dest="harmonia",
            payload={
                "action": "process_sprint",
                "sprint_name": "Missing_Test",
                "data": {
                    "type": "reference",
                    "workflow_id": "nonexistent_workflow_123"
                }
            }
        )
        
        result = await harmonia.handle_workflow(message)
        assert result["status"] == "error"
        assert "not found" in result["reason"]


class TestWorkflowEndToEnd:
    """Test complete workflow from proposal to validation."""
    
    @pytest.fixture
    def temp_env(self):
        """Set up temporary environment."""
        temp_dir = tempfile.mkdtemp()
        old_root = TektonEnviron.get('TEKTON_ROOT')
        os.environ['TEKTON_ROOT'] = temp_dir
        yield temp_dir
        # Cleanup
        if old_root:
            os.environ['TEKTON_ROOT'] = old_root
        else:
            if 'TEKTON_ROOT' in os.environ:
                del os.environ['TEKTON_ROOT']
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_full_planning_pipeline(self, temp_env):
        """Test the complete planning team workflow pipeline."""
        # This would test:
        # 1. Telos creates proposal → sprint
        # 2. Prometheus marks as Ready
        # 3. Metis breaks down tasks
        # 4. Harmonia creates workflows
        # 5. Synthesis validates
        
        # For now, just verify the workflow structure is correct
        components = ['telos', 'prometheus', 'metis', 'harmonia', 'synthesis']
        
        for i, component in enumerate(components[:-1]):
            handler = WorkflowHandler(component)
            next_component = components[i + 1]
            
            # Verify can generate workflow ID
            workflow_id = handler.generate_workflow_id("Test_Sprint")
            assert workflow_id.startswith("test_sprint_")
            
            # Verify can prepare data
            data = {"stage": component, "index": i}
            payload = handler.prepare_data_payload(data)
            assert payload["type"] == "embedded"  # Small data
            assert payload["content"] == data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])