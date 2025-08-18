"""
Workflow Handler Base Class

Implements the Workflow Endpoint Standard for Tekton components.
All components should extend this class to handle workflow messages.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import os
import json
import httpx
import logging

# Import landmarks with fallback
try:
    from landmarks import architecture_decision, state_checkpoint, integration_point
except ImportError:
    # No-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func): return func
        return decorator
    def state_checkpoint(**kwargs):
        def decorator(func): return func
        return decorator
    def integration_point(**kwargs):
        def decorator(func): return func
        return decorator
try:
    from shared.env import TektonEnviron
    from shared.urls import tekton_url
except ImportError:
    # For testing, create minimal mock classes
    class TektonEnviron:
        @staticmethod
        def get(key, default=None):
            return default
    
    # Define port mapping for fallback
    _COMPONENT_PORTS = {
        'engram': 8000,
        'hermes': 8001,
        'ergon': 8002,
        'rhetor': 8003,
        'terma': 8004,
        'athena': 8005,
        'prometheus': 8006,
        'harmonia': 8007,
        'telos': 8008,
        'synthesis': 8009,
        'tekton-core': 8010,
        'metis': 8011,
        'apollo': 8012,
        'budget': 8013,
        'penia': 8013,
        'sophia': 8014,
        'noesis': 8015,
        'numa': 8016,
        'aish': 8017,
        'hephaestus': 8080
    }
    
    def tekton_url(component, path=""):
        port = _COMPONENT_PORTS.get(component, 8000)
        return f"http://localhost:{port}{path}"

logger = logging.getLogger(__name__)


class WorkflowMessage(BaseModel):
    """Standard workflow message structure."""
    purpose: Dict[str, str]
    dest: str
    payload: Dict[str, Any]


@architecture_decision(
    title="Workflow Handler Base Class",
    description="Common workflow handling logic for all Tekton components",
    rationale="Centralizes workflow file management and message routing to avoid duplication across components",
    alternatives_considered=["Component-specific handlers", "Direct file access", "Database storage"],
    decided_by="Casey",
    decision_date="2025-01-27"
)
class WorkflowHandler:
    """
    Base workflow handler for Tekton components.
    
    Each component should extend this class and implement the
    action methods (look_for_work, process_sprint, etc.)
    """
    
    def __init__(self, component_name: str):
        """
        Initialize workflow handler.
        
        Args:
            component_name: Name of this component (e.g., 'telos', 'metis')
        """
        self.component_name = component_name
        self.router = APIRouter()
        self.router.post("/workflow")(self.handle_workflow)
        
        # Get component ports from environment
        self.ports = self._load_port_config()
    
    def _load_port_config(self) -> Dict[str, int]:
        """Load component port configuration."""
        return {
            'telos': int(TektonEnviron.get('TELOS_PORT', '8011')),
            'prometheus': int(TektonEnviron.get('PROMETHEUS_PORT', '8012')),
            'metis': int(TektonEnviron.get('METIS_PORT', '8013')),
            'harmonia': int(TektonEnviron.get('HARMONIA_PORT', '8014')),
            'synthesis': int(TektonEnviron.get('SYNTHESIS_PORT', '8015')),
            'tekton': int(TektonEnviron.get('TEKTONCORE_PORT', '8080')),
            'hermes': int(TektonEnviron.get('HERMES_PORT', '8000'))
        }
    
    def _get_workflow_dir(self) -> str:
        """Get the workflow data directory path."""
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '.')
        return os.path.join(tekton_root, '.tekton', 'workflows', 'data')
    
    def generate_workflow_id(self, sprint_name: str) -> str:
        """
        Generate a workflow ID for a sprint.
        
        Format: sprint_name_YYYY_MM_DD_HHMMSS
        """
        timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
        # Clean sprint name (remove _Sprint suffix if present)
        clean_name = sprint_name.replace('_Sprint', '').lower().replace(' ', '_')
        return f"{clean_name}_{timestamp}"
    
    def save_workflow_data(self, workflow_id: str, data: Dict[str, Any]) -> str:
        """
        Save workflow data to centralized location.
        
        Args:
            workflow_id: Unique workflow identifier
            data: Workflow data to save
            
        Returns:
            Path to saved workflow file
        """
        workflow_dir = self._get_workflow_dir()
        os.makedirs(workflow_dir, exist_ok=True)
        
        workflow_file = os.path.join(workflow_dir, f"{workflow_id}.json")
        
        # Load existing data if file exists (for updates)
        existing_data = {}
        if os.path.exists(workflow_file):
            with open(workflow_file, 'r') as f:
                existing_data = json.load(f)
        
        # Update with new data
        existing_data.update(data)
        
        # Add metadata
        if 'metadata' not in existing_data:
            existing_data['metadata'] = {}
        
        existing_data['metadata'].update({
            'last_updated': datetime.now().isoformat(),
            'updated_by': self.component_name
        })
        
        # Save updated data
        with open(workflow_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        logger.info(f"Saved workflow data to {workflow_file}")
        return workflow_file
    
    def load_workflow_data(self, workflow_id: str) -> Dict[str, Any]:
        """
        Load workflow data from centralized location.
        
        Args:
            workflow_id: Unique workflow identifier
            
        Returns:
            Workflow data
            
        Raises:
            FileNotFoundError: If workflow file doesn't exist
        """
        workflow_file = os.path.join(self._get_workflow_dir(), f"{workflow_id}.json")
        
        if not os.path.exists(workflow_file):
            raise FileNotFoundError(f"Workflow file not found: {workflow_id}")
        
        with open(workflow_file, 'r') as f:
            return json.load(f)
    
    def prepare_data_payload(self, data: Any) -> Dict[str, Any]:
        """
        Prepare data for payload based on size threshold.
        
        Uses 10KB threshold:
        - < 10KB: Embed data directly
        - >= 10KB: Save and reference
        
        Args:
            data: Data to include in payload
            
        Returns:
            Formatted data payload
        """
        # Convert to JSON to check size
        data_json = json.dumps(data)
        size_bytes = len(data_json.encode('utf-8'))
        
        # 10KB threshold
        if size_bytes < 10 * 1024:
            return {
                "type": "embedded",
                "content": data
            }
        else:
            # For references, the workflow_id should be provided by caller
            return {
                "type": "reference",
                "size_bytes": size_bytes,
                "content": data  # Caller will save and update with reference
            }
    
    async def handle_workflow(self, message: WorkflowMessage) -> Dict[str, Any]:
        """
        Main workflow message handler.
        
        Routes incoming workflow messages to appropriate action handlers.
        """
        try:
            # Ignore if not for this component
            if message.dest != self.component_name:
                logger.debug(f"Ignoring message for {message.dest}")
                return {"status": "ignored", "reason": "wrong destination"}
            
            # Get purpose for this component
            purpose = message.purpose.get(self.component_name)
            if not purpose:
                return {"status": "error", "reason": "no purpose defined"}
            
            logger.info(f"Processing workflow: {purpose}")
            
            # Route to appropriate handler
            action = message.payload.get("action")
            
            if action == "look_for_work":
                return await self.look_for_work()
            elif action == "process_sprint":
                return await self.process_sprint(message.payload)
            elif action == "update_status":
                return await self.update_status(message.payload)
            elif action == "import_data":
                return await self.import_data(message.payload)
            elif action == "export_data":
                return await self.export_data(message.payload)
            else:
                return {"status": "error", "reason": f"unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            return {"status": "error", "reason": str(e)}
    
    @state_checkpoint(
        title="Workflow Work Queue",
        description="Scans workflow directory for pending work assignments",
        state_type="file_system",
        persistence=True,
        consistency_requirements="Must check all workflow JSON files in directory",
        recovery_strategy="Returns empty list if directory doesn't exist"
    )
    @integration_point(
        title="Workflow Directory Scanner",
        description="Reads workflow files from .tekton/workflows/data/ to find component work",
        target_component="Filesystem",
        protocol="file_operations",
        data_flow="scan directory → read JSON files → filter by component → return work items"
    )
    def check_for_work(self, component_name: str) -> List[Dict[str, Any]]:
        """
        Check .tekton/workflows/data/ directory for work assigned to this component.
        
        Args:
            component_name: Name of the component to check work for
            
        Returns:
            List of available work items for the component
        """
        work_items = []
        
        try:
            workflow_dir = self._get_workflow_dir()
            
            if not os.path.exists(workflow_dir):
                return work_items
            
            # Scan all workflow files
            for filename in os.listdir(workflow_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(workflow_dir, filename)
                    
                    try:
                        with open(filepath, 'r') as f:
                            workflow_data = json.load(f)
                        
                        # Check if this workflow has work for the component
                        if self._has_work_for_component(workflow_data, component_name):
                            work_items.append({
                                "workflow_id": filename.replace('.json', ''),
                                "workflow_file": filename,
                                "status": workflow_data.get("status", "unknown"),
                                "created": workflow_data.get("created", "unknown"),
                                "component_tasks": self._extract_component_tasks(workflow_data, component_name)
                            })
                            
                    except (json.JSONDecodeError, IOError) as e:
                        logger.warning(f"Could not read workflow file {filename}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error checking for work: {e}")
            
        return work_items
    
    def _has_work_for_component(self, workflow_data: Dict[str, Any], component_name: str) -> bool:
        """Check if workflow data contains work for the specified component."""
        # Check if component is mentioned in tasks, assignments, or destinations
        data_str = json.dumps(workflow_data).lower()
        component_lower = component_name.lower()
        
        # Look for component name in various contexts
        return (
            component_lower in data_str or
            f'"{component_name}"' in json.dumps(workflow_data) or
            workflow_data.get("dest") == component_name or
            any(task.get("component") == component_name 
                for task in workflow_data.get("tasks", []) 
                if isinstance(task, dict))
        )
    
    def _extract_component_tasks(self, workflow_data: Dict[str, Any], component_name: str) -> List[Dict[str, Any]]:
        """Extract tasks specifically assigned to the component."""
        component_tasks = []
        
        # Look in tasks array
        for task in workflow_data.get("tasks", []):
            if isinstance(task, dict) and task.get("component") == component_name:
                component_tasks.append(task)
        
        # Look in payload for component-specific data
        payload = workflow_data.get("payload", {})
        if payload.get("component") == component_name:
            component_tasks.append({
                "type": "payload_task",
                "action": payload.get("action", "unknown"),
                "data": payload
            })
            
        return component_tasks

    async def look_for_work(self) -> Dict[str, Any]:
        """
        Check for pending work for this component.
        
        Override in component implementation.
        """
        raise NotImplementedError(f"{self.component_name} must implement look_for_work")
    
    async def process_sprint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a sprint at this component's workflow stage.
        
        Override in component implementation.
        """
        raise NotImplementedError(f"{self.component_name} must implement process_sprint")
    
    async def update_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update sprint status in DAILY_LOG.md.
        
        Can be overridden if component needs custom status handling.
        """
        sprint_name = payload.get("sprint_name")
        old_status = payload.get("old_status", "Unknown")
        new_status = payload.get("new_status")
        
        if not sprint_name or not new_status:
            return {"status": "error", "reason": "missing sprint_name or new_status"}
        
        try:
            self._update_daily_log(sprint_name, old_status, new_status)
            return {"status": "success", "updated": new_status}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    async def import_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import data from previous component in workflow.
        
        Default implementation handles both embedded and reference data.
        Components can override for custom behavior.
        """
        data_info = payload.get("data", {})
        
        if not data_info:
            return {"status": "error", "reason": "no data provided"}
        
        # Handle embedded vs reference data
        if data_info.get("type") == "embedded":
            return {
                "status": "success",
                "data": data_info.get("content", {})
            }
        elif data_info.get("type") == "reference":
            workflow_id = data_info.get("workflow_id")
            if not workflow_id:
                return {"status": "error", "reason": "no workflow_id in reference"}
            
            try:
                workflow_data = self.load_workflow_data(workflow_id)
                # Extract component-specific data if available
                component_data = workflow_data.get(self.component_name, {})
                from_component = payload.get("from_component")
                if from_component and from_component in workflow_data:
                    # Also include data from the sending component
                    return {
                        "status": "success",
                        "data": workflow_data[from_component],
                        "workflow_data": workflow_data
                    }
                return {
                    "status": "success", 
                    "data": component_data,
                    "workflow_data": workflow_data
                }
            except FileNotFoundError as e:
                return {"status": "error", "reason": str(e)}
        else:
            return {"status": "error", "reason": "unknown data type"}
    
    async def export_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export data to next component in workflow.
        
        Default implementation saves data and returns reference.
        Components can override for custom behavior.
        """
        sprint_name = payload.get("sprint_name")
        workflow_id = payload.get("workflow_id")
        export_data = payload.get("data", {})
        
        if not sprint_name:
            return {"status": "error", "reason": "missing sprint_name"}
        
        # Generate workflow_id if not provided
        if not workflow_id:
            workflow_id = self.generate_workflow_id(sprint_name)
        
        # Prepare workflow data structure
        workflow_data = {
            "workflow_id": workflow_id,
            "sprint_name": sprint_name,
            "current_stage": self.component_name,
            self.component_name: export_data
        }
        
        try:
            # Save workflow data
            workflow_path = self.save_workflow_data(workflow_id, workflow_data)
            
            # Also update sprint directory for backward compatibility
            self._update_sprint_directory(sprint_name, export_data)
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "workflow_path": workflow_path
            }
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return {"status": "error", "reason": str(e)}
    
    def _update_daily_log(self, sprint_name: str, old_status: str, new_status: str):
        """Update sprint status in DAILY_LOG.md."""
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '.')
        sprint_path = os.path.join(
            tekton_root, 
            'MetaData', 
            'DevelopmentSprints', 
            f'{sprint_name}_Sprint'
        )
        daily_log = os.path.join(sprint_path, 'DAILY_LOG.md')
        
        if not os.path.exists(daily_log):
            raise FileNotFoundError(f"DAILY_LOG.md not found for {sprint_name}")
        
        # Append status update
        with open(daily_log, 'a') as f:
            f.write(f"\n## Sprint Status: {new_status}\n")
            f.write(f"**Updated**: {datetime.now().isoformat()}Z\n")
            f.write(f"**Updated By**: {self.component_name}\n")
            f.write(f"\nPrevious Status: {old_status} → {new_status}\n")
    
    def _update_sprint_directory(self, sprint_name: str, data: Dict[str, Any]):
        """
        Update sprint directory with component output for backward compatibility.
        
        Args:
            sprint_name: Name of the sprint
            data: Component output data
        """
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '.')
        sprint_path = os.path.join(
            tekton_root,
            'MetaData',
            'DevelopmentSprints',
            f'{sprint_name}_Sprint'
        )
        
        if os.path.exists(sprint_path):
            output_file = os.path.join(sprint_path, f'{self.component_name}_output.json')
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Updated sprint directory: {output_file}")
    
    async def send_workflow_message(
        self, 
        dest: str, 
        purpose: Dict[str, str], 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send workflow message to another component.
        
        Args:
            dest: Target component name
            purpose: Purpose object with instructions for components
            payload: Action payload
            
        Returns:
            Response from target component
        """
        message = WorkflowMessage(
            purpose=purpose,
            dest=dest,
            payload=payload
        )
        
        # Use tekton_url for proper URL construction
        url = tekton_url(dest, "/workflow")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=message.model_dump(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error sending to {dest}: {str(e)}")
                raise
    
    async def notify_next_component(
        self,
        next_component: str,
        sprint_name: str,
        new_status: str,
        data: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Notify next component in workflow pipeline.
        
        Handles data storage and creates proper data payload based on size.
        
        Args:
            next_component: Target component name
            sprint_name: Sprint being processed
            new_status: New status for the sprint
            data: Data to pass to next component
            workflow_id: Optional workflow ID (generated if not provided)
        """
        # Generate workflow_id if not provided
        if not workflow_id:
            workflow_id = self.generate_workflow_id(sprint_name)
        
        # Prepare data payload
        data_payload = self.prepare_data_payload(data)
        
        # If data needs to be referenced, save it first
        if data_payload["type"] == "reference":
            # Save the workflow data
            workflow_data = {
                "workflow_id": workflow_id,
                "sprint_name": sprint_name,
                "current_stage": self.component_name,
                "next_stage": next_component,
                self.component_name: data
            }
            workflow_path = self.save_workflow_data(workflow_id, workflow_data)
            
            # Update data payload with reference
            data_payload = {
                "type": "reference",
                "workflow_id": workflow_id,
                "path": f"{self.component_name}_output"
            }
            
            # Also update sprint directory for backward compatibility
            self._update_sprint_directory(sprint_name, data)
        
        # Update sprint status
        await self.update_status({
            "sprint_name": sprint_name,
            "old_status": f"Processing:{self.component_name}",
            "new_status": new_status
        })
        
        # Create purpose with clear instruction
        purpose = {
            next_component: f"Process {self.component_name} output for {sprint_name}"
        }
        
        # Build payload
        payload = {
            "action": "process_sprint",
            "sprint_name": sprint_name,
            "status": new_status,
            "from_component": self.component_name,
            "workflow_id": workflow_id,
            "data": data_payload
        }
        
        return await self.send_workflow_message(next_component, purpose, payload)
    
    def find_sprints_by_status(self, status_pattern: str) -> list:
        """
        Find all sprints matching a status pattern.
        
        Args:
            status_pattern: Status to match (e.g., "Ready-1:Metis")
            
        Returns:
            List of sprint names matching the status
        """
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '.')
        sprints_dir = os.path.join(tekton_root, 'MetaData', 'DevelopmentSprints')
        matching_sprints = []
        
        if not os.path.exists(sprints_dir):
            return matching_sprints
        
        # Check each *_Sprint directory
        for item in os.listdir(sprints_dir):
            if item.endswith('_Sprint') and os.path.isdir(os.path.join(sprints_dir, item)):
                daily_log = os.path.join(sprints_dir, item, 'DAILY_LOG.md')
                if os.path.exists(daily_log):
                    with open(daily_log, 'r') as f:
                        content = f.read()
                        # Look for most recent status
                        if f"Sprint Status: {status_pattern}" in content:
                            sprint_name = item.replace('_Sprint', '')
                            matching_sprints.append(sprint_name)
        
        return matching_sprints