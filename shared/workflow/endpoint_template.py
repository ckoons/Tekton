"""
Shared workflow endpoint template for all Tekton components.
Provides standardized /workflow endpoint that handles the unified JSON format.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

# Import landmarks with fallback
try:
    from landmarks import architecture_decision, api_contract, integration_point
except ImportError:
    # No-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func): return func
        return decorator
    def api_contract(**kwargs):
        def decorator(func): return func
        return decorator
    def integration_point(**kwargs):
        def decorator(func): return func
        return decorator

try:
    from .workflow_handler import WorkflowHandler
except ImportError:
    from workflow_handler import WorkflowHandler

@architecture_decision(
    title="Standardized Workflow Endpoint",
    description="All Tekton components share a common /workflow endpoint pattern",
    rationale="Enables unified workflow orchestration and work distribution across all components",
    alternatives_considered=["Component-specific endpoints", "Direct message passing", "Pub/sub"],
    decided_by="Casey",
    decision_date="2025-01-27"
)
def create_workflow_endpoint(component_name: str) -> APIRouter:
    """
    Create a standardized /workflow endpoint for a Tekton component.
    
    Args:
        component_name: Name of the component (e.g., 'telos', 'apollo', 'metis')
        
    Returns:
        FastAPI router with /workflow endpoint
    """
    router = APIRouter()
    workflow_handler = WorkflowHandler(component_name)
    
    @router.post("/workflow")
    @api_contract(
        title="Component Workflow Endpoint",
        description="Standard endpoint for workflow messages on all Tekton components",
        endpoint="/workflow",
        method="POST",
        request_schema={
            "purpose": "string (e.g., 'check_work')",
            "dest": "string (component name)",
            "payload": {
                "component": "string",
                "action": "string (e.g., 'look_for_work')"
            }
        },
        response_schema={
            "status": "string",
            "component": "string",
            "work_available": "boolean",
            "work_count": "number",
            "work_items": "array"
        }
    )
    @integration_point(
        title="Workflow Handler Integration",
        description="Connects workflow endpoint to WorkflowHandler for checking work assignments",
        target_component="WorkflowHandler",
        protocol="internal_api",
        data_flow="Workflow endpoint → WorkflowHandler.check_for_work → scan workflow files → return work items"
    )
    async def workflow_endpoint(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard workflow endpoint for all Tekton components.
        
        Accepts unified JSON format:
        {
            "purpose": "check_work",
            "dest": "component_name", 
            "payload": {
                "component": "component_name",
                "action": "look_for_work"
            }
        }
        """
        try:
            # Validate message structure
            if not isinstance(message, dict):
                raise HTTPException(status_code=400, detail="Message must be a JSON object")
                
            required_fields = ["purpose", "dest", "payload"]
            missing_fields = [field for field in required_fields if field not in message]
            if missing_fields:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required fields: {missing_fields}"
                )
            
            purpose = message["purpose"]
            dest = message["dest"]
            payload = message["payload"]
            
            # Validate destination matches this component
            if dest != component_name:
                return {
                    "status": "error",
                    "message": f"Message dest '{dest}' does not match component '{component_name}'",
                    "component": component_name
                }
            
            # Handle check_work purpose with look_for_work action
            if purpose == "check_work" and payload.get("action") == "look_for_work":
                # Use shared workflow handler to check for work
                work_items = workflow_handler.check_for_work(component_name)
                
                return {
                    "status": "success",
                    "component": component_name,
                    "purpose": purpose,
                    "work_available": len(work_items) > 0,
                    "work_count": len(work_items),
                    "work_items": work_items,
                    "message": f"Checked for work on {component_name}"
                }
            
            # Handle other workflow purposes (future expansion)
            return {
                "status": "not_implemented",
                "component": component_name,
                "purpose": purpose,
                "message": f"Purpose '{purpose}' not yet implemented on {component_name}"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            return {
                "status": "error",
                "component": component_name,
                "message": f"Internal error: {str(e)}"
            }
    
    return router