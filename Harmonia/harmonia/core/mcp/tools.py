"""
FastMCP tool definitions for Harmonia.

This module defines FastMCP tools for Harmonia's workflow orchestration functionality:
- Workflow definition management tools
- Workflow execution and monitoring tools
- Template management tools
- Component integration tools
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from uuid import UUID

from tekton.mcp.fastmcp import mcp_tool, mcp_capability
from tekton.mcp.fastmcp.utils import register_tools as register_tools_util

# We'll use forward references for Harmonia types to avoid circular imports
from ..engine import WorkflowEngine

logger = logging.getLogger(__name__)

# =====================
# Workflow Definition Management Tools
# =====================

@mcp_capability(
    name="workflow_definition_management",
    description="Create, update, and manage workflow definitions",
    modality="orchestration"
)
@mcp_tool(
    name="CreateWorkflowDefinition",
    description="Create a new workflow definition",
    tags=["workflow", "definition", "creation"],
    category="workflow_management"
)
async def create_workflow_definition(
    name: str,
    description: str,
    tasks: Dict[str, Dict[str, Any]],
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    version: str = "1.0",
    metadata: Optional[Dict[str, Any]] = None,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Create a new workflow definition.
    
    Args:
        name: Name of the workflow
        description: Description of the workflow
        tasks: Dictionary of task definitions
        input_schema: Optional input schema
        output_schema: Optional output schema
        version: Version of the workflow
        metadata: Optional metadata
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Created workflow definition information
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        from ..state import StateManager
        from ...models.workflow import WorkflowDefinition, TaskDefinition
        
        # Convert task definitions
        task_defs = {}
        for task_id, task_data in tasks.items():
            task_defs[task_id] = TaskDefinition(**task_data)
        
        # Create workflow definition
        workflow_def = WorkflowDefinition(
            name=name,
            description=description,
            tasks=task_defs,
            input=input_schema or {},
            output=output_schema or {},
            version=version,
            metadata=metadata or {}
        )
        
        # Save to state manager
        await workflow_engine.state_manager.save_workflow_definition(workflow_def)
        
        return {
            "workflow_id": str(workflow_def.id),
            "name": workflow_def.name,
            "description": workflow_def.description,
            "version": workflow_def.version,
            "status": "created"
        }
    
    except Exception as e:
        logger.error(f"Error creating workflow definition: {e}")
        return {"error": f"Error creating workflow definition: {str(e)}"}


@mcp_capability(
    name="workflow_definition_management",
    description="Create, update, and manage workflow definitions",
    modality="orchestration"
)
@mcp_tool(
    name="UpdateWorkflowDefinition",
    description="Update an existing workflow definition",
    tags=["workflow", "definition", "update"],
    category="workflow_management"
)
async def update_workflow_definition(
    workflow_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tasks: Optional[Dict[str, Dict[str, Any]]] = None,
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Update an existing workflow definition.
    
    Args:
        workflow_id: ID of the workflow to update
        name: Updated name of the workflow
        description: Updated description of the workflow
        tasks: Updated dictionary of task definitions
        input_schema: Updated input schema
        output_schema: Updated output schema
        version: Updated version of the workflow
        metadata: Updated metadata
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Updated workflow definition information
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        from ...models.workflow import TaskDefinition
        
        # Load existing workflow
        workflow_def = await workflow_engine.state_manager.load_workflow_definition(UUID(workflow_id))
        
        if not workflow_def:
            return {"error": f"Workflow definition {workflow_id} not found"}
        
        # Update fields
        if name:
            workflow_def.name = name
        if description:
            workflow_def.description = description
        if tasks:
            task_defs = {}
            for task_id, task_data in tasks.items():
                task_defs[task_id] = TaskDefinition(**task_data)
            workflow_def.tasks = task_defs
        if input_schema:
            workflow_def.input = input_schema
        if output_schema:
            workflow_def.output = output_schema
        if version:
            workflow_def.version = version
        if metadata:
            workflow_def.metadata = {**workflow_def.metadata, **metadata}
        
        # Save updated definition
        await workflow_engine.state_manager.save_workflow_definition(workflow_def)
        
        return {
            "workflow_id": str(workflow_def.id),
            "name": workflow_def.name,
            "description": workflow_def.description,
            "version": workflow_def.version,
            "status": "updated"
        }
    
    except Exception as e:
        logger.error(f"Error updating workflow definition: {e}")
        return {"error": f"Error updating workflow definition: {str(e)}"}


@mcp_capability(
    name="workflow_definition_management",
    description="Create, update, and manage workflow definitions",
    modality="orchestration"
)
@mcp_tool(
    name="DeleteWorkflowDefinition",
    description="Delete a workflow definition",
    tags=["workflow", "definition", "delete"],
    category="workflow_management"
)
async def delete_workflow_definition(
    workflow_id: str,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Delete a workflow definition.
    
    Args:
        workflow_id: ID of the workflow to delete
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Deletion status
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Check if workflow exists
        workflow_def = await workflow_engine.state_manager.load_workflow_definition(UUID(workflow_id))
        
        if not workflow_def:
            return {"error": f"Workflow definition {workflow_id} not found"}
        
        # Delete workflow definition
        await workflow_engine.state_manager.delete_workflow_definition(UUID(workflow_id))
        
        return {
            "workflow_id": workflow_id,
            "status": "deleted"
        }
    
    except Exception as e:
        logger.error(f"Error deleting workflow definition: {e}")
        return {"error": f"Error deleting workflow definition: {str(e)}"}


@mcp_capability(
    name="workflow_definition_management",
    description="Create, update, and manage workflow definitions",
    modality="orchestration"
)
@mcp_tool(
    name="GetWorkflowDefinition",
    description="Get a workflow definition by ID",
    tags=["workflow", "definition", "query"],
    category="workflow_management"
)
async def get_workflow_definition(
    workflow_id: str,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Get a workflow definition by ID.
    
    Args:
        workflow_id: ID of the workflow to retrieve
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Workflow definition information
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Load workflow definition
        workflow_def = await workflow_engine.state_manager.load_workflow_definition(UUID(workflow_id))
        
        if not workflow_def:
            return {"error": f"Workflow definition {workflow_id} not found"}
        
        return {
            "workflow_id": str(workflow_def.id),
            "name": workflow_def.name,
            "description": workflow_def.description,
            "tasks": {task_id: task.dict() for task_id, task in workflow_def.tasks.items()},
            "input_schema": workflow_def.input,
            "output_schema": workflow_def.output,
            "version": workflow_def.version,
            "metadata": workflow_def.metadata,
            "created_at": workflow_def.created_at.isoformat() if workflow_def.created_at else None,
            "updated_at": workflow_def.updated_at.isoformat() if workflow_def.updated_at else None
        }
    
    except Exception as e:
        logger.error(f"Error getting workflow definition: {e}")
        return {"error": f"Error getting workflow definition: {str(e)}"}


@mcp_capability(
    name="workflow_definition_management",
    description="Create, update, and manage workflow definitions",
    modality="orchestration"
)
@mcp_tool(
    name="ListWorkflowDefinitions",
    description="List all workflow definitions",
    tags=["workflow", "definition", "query"],
    category="workflow_management"
)
async def list_workflow_definitions(
    limit: int = 100,
    offset: int = 0,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    List all workflow definitions.
    
    Args:
        limit: Maximum number of results to return
        offset: Number of results to skip
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        List of workflow definitions
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Get workflow definitions
        workflows = await workflow_engine.state_manager.list_workflow_definitions(limit, offset)
        
        return {
            "workflows": [
                {
                    "workflow_id": str(w.id),
                    "name": w.name,
                    "description": w.description,
                    "version": w.version,
                    "created_at": w.created_at.isoformat() if w.created_at else None,
                    "updated_at": w.updated_at.isoformat() if w.updated_at else None
                }
                for w in workflows
            ],
            "count": len(workflows),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        logger.error(f"Error listing workflow definitions: {e}")
        return {"error": f"Error listing workflow definitions: {str(e)}"}


# =====================
# Workflow Execution Tools
# =====================

@mcp_capability(
    name="workflow_execution",
    description="Execute and monitor workflows",
    modality="orchestration"
)
@mcp_tool(
    name="ExecuteWorkflow",
    description="Execute a workflow with input data",
    tags=["workflow", "execution"],
    category="workflow_execution"
)
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Execute a workflow with input data.
    
    Args:
        workflow_id: ID of the workflow to execute
        input_data: Input data for the workflow
        metadata: Optional execution metadata
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Workflow execution information
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Load workflow definition
        workflow_def = await workflow_engine.state_manager.load_workflow_definition(UUID(workflow_id))
        
        if not workflow_def:
            return {"error": f"Workflow definition {workflow_id} not found"}
        
        # Execute workflow
        execution = await workflow_engine.execute_workflow(
            workflow_def=workflow_def,
            input_data=input_data,
            metadata=metadata or {}
        )
        
        return {
            "execution_id": str(execution.id),
            "workflow_id": str(execution.workflow_id),
            "status": execution.status.value,
            "started_at": execution.started_at.isoformat() if execution.started_at else None
        }
    
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return {"error": f"Error executing workflow: {str(e)}"}


@mcp_capability(
    name="workflow_execution",
    description="Execute and monitor workflows",
    modality="orchestration"
)
@mcp_tool(
    name="CancelWorkflowExecution",
    description="Cancel a running workflow execution",
    tags=["workflow", "execution", "cancel"],
    category="workflow_execution"
)
async def cancel_workflow_execution(
    execution_id: str,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Cancel a running workflow execution.
    
    Args:
        execution_id: ID of the execution to cancel
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Cancellation status
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Cancel workflow
        cancelled = await workflow_engine.cancel_workflow(UUID(execution_id))
        
        if not cancelled:
            return {"error": f"Workflow execution {execution_id} not found or not running"}
        
        return {
            "execution_id": execution_id,
            "status": "cancelled"
        }
    
    except Exception as e:
        logger.error(f"Error cancelling workflow execution: {e}")
        return {"error": f"Error cancelling workflow execution: {str(e)}"}


@mcp_capability(
    name="workflow_execution",
    description="Execute and monitor workflows",
    modality="orchestration"
)
@mcp_tool(
    name="PauseWorkflowExecution",
    description="Pause a running workflow execution",
    tags=["workflow", "execution", "pause"],
    category="workflow_execution"
)
async def pause_workflow_execution(
    execution_id: str,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Pause a running workflow execution.
    
    Args:
        execution_id: ID of the execution to pause
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Pause status
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Pause workflow
        paused = await workflow_engine.pause_workflow(UUID(execution_id))
        
        if not paused:
            return {"error": f"Workflow execution {execution_id} not found or not running"}
        
        return {
            "execution_id": execution_id,
            "status": "paused"
        }
    
    except Exception as e:
        logger.error(f"Error pausing workflow execution: {e}")
        return {"error": f"Error pausing workflow execution: {str(e)}"}


@mcp_capability(
    name="workflow_execution",
    description="Execute and monitor workflows",
    modality="orchestration"
)
@mcp_tool(
    name="ResumeWorkflowExecution",
    description="Resume a paused workflow execution",
    tags=["workflow", "execution", "resume"],
    category="workflow_execution"
)
async def resume_workflow_execution(
    execution_id: str,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Resume a paused workflow execution.
    
    Args:
        execution_id: ID of the execution to resume
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Resume status
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Resume workflow
        resumed = await workflow_engine.resume_workflow(UUID(execution_id))
        
        if not resumed:
            return {"error": f"Workflow execution {execution_id} not found or not paused"}
        
        return {
            "execution_id": execution_id,
            "status": "running"
        }
    
    except Exception as e:
        logger.error(f"Error resuming workflow execution: {e}")
        return {"error": f"Error resuming workflow execution: {str(e)}"}


@mcp_capability(
    name="workflow_execution",
    description="Execute and monitor workflows",
    modality="orchestration"
)
@mcp_tool(
    name="GetWorkflowExecutionStatus",
    description="Get the status of a workflow execution",
    tags=["workflow", "execution", "status"],
    category="workflow_execution"
)
async def get_workflow_execution_status(
    execution_id: str,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Get the status of a workflow execution.
    
    Args:
        execution_id: ID of the execution
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Execution status information
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Get execution status
        execution_summary = await workflow_engine.get_workflow_status(UUID(execution_id))
        
        if not execution_summary:
            return {"error": f"Workflow execution {execution_id} not found"}
        
        return {
            "execution_id": str(execution_summary.execution_id),
            "workflow_id": str(execution_summary.workflow_id),
            "status": execution_summary.status.value,
            "progress": execution_summary.progress,
            "started_at": execution_summary.started_at.isoformat() if execution_summary.started_at else None,
            "completed_at": execution_summary.completed_at.isoformat() if execution_summary.completed_at else None,
            "task_statuses": {
                task_id: status.value for task_id, status in execution_summary.task_statuses.items()
            },
            "error_message": execution_summary.error_message
        }
    
    except Exception as e:
        logger.error(f"Error getting workflow execution status: {e}")
        return {"error": f"Error getting workflow execution status: {str(e)}"}


@mcp_capability(
    name="workflow_execution",
    description="Execute and monitor workflows",
    modality="orchestration"
)
@mcp_tool(
    name="ListWorkflowExecutions",
    description="List workflow executions with optional filtering",
    tags=["workflow", "execution", "query"],
    category="workflow_execution"
)
async def list_workflow_executions(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    List workflow executions with optional filtering.
    
    Args:
        workflow_id: Optional workflow ID filter
        status: Optional status filter
        limit: Maximum number of results to return
        offset: Number of results to skip
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        List of workflow executions
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        from ...models.workflow import WorkflowStatus
        
        # Convert status string to enum if provided
        workflow_status = None
        if status:
            try:
                workflow_status = WorkflowStatus(status)
            except ValueError:
                return {"error": f"Invalid status: {status}"}
        
        # Get executions
        executions = await workflow_engine.state_manager.list_workflow_executions(
            limit, offset, workflow_status
        )
        
        # Filter by workflow_id if provided
        if workflow_id:
            executions = [e for e in executions if str(e.workflow_id) == workflow_id]
        
        return {
            "executions": [
                {
                    "execution_id": str(e.id),
                    "workflow_id": str(e.workflow_id),
                    "status": e.status.value,
                    "started_at": e.started_at.isoformat() if e.started_at else None,
                    "completed_at": e.completed_at.isoformat() if e.completed_at else None
                }
                for e in executions
            ],
            "count": len(executions),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        logger.error(f"Error listing workflow executions: {e}")
        return {"error": f"Error listing workflow executions: {str(e)}"}


# =====================
# Template Management Tools
# =====================

@mcp_capability(
    name="template_management",
    description="Create and manage workflow templates",
    modality="orchestration"
)
@mcp_tool(
    name="CreateTemplate",
    description="Create a workflow template",
    tags=["template", "creation"],
    category="template_management"
)
async def create_template(
    name: str,
    description: str,
    workflow_definition_id: str,
    parameters: Optional[Dict[str, Dict[str, Any]]] = None,
    category_ids: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    is_public: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Create a workflow template.
    
    Args:
        name: Name of the template
        description: Description of the template
        workflow_definition_id: ID of the workflow definition to template
        parameters: Template parameters
        category_ids: Optional category IDs
        tags: Optional tags
        is_public: Whether the template is public
        metadata: Optional metadata
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Created template information
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Get workflow definition
        workflow_def = await workflow_engine.state_manager.load_workflow_definition(UUID(workflow_definition_id))
        
        if not workflow_def:
            return {"error": f"Workflow definition {workflow_definition_id} not found"}
        
        # Get template manager
        template_manager = workflow_engine.template_manager
        if not template_manager:
            return {"error": "Template manager not initialized"}
        
        # Create template
        template = template_manager.create_template(
            name=name,
            description=description,
            workflow_definition=workflow_def,
            parameters=parameters or {},
            category_ids=[UUID(c) for c in (category_ids or [])],
            tags=tags or [],
            is_public=is_public,
            metadata=metadata or {}
        )
        
        return {
            "template_id": str(template.id),
            "name": template.name,
            "description": template.description,
            "is_public": template.is_public,
            "status": "created"
        }
    
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return {"error": f"Error creating template: {str(e)}"}


@mcp_capability(
    name="template_management",
    description="Create and manage workflow templates",
    modality="orchestration"
)
@mcp_tool(
    name="InstantiateTemplate",
    description="Instantiate a workflow template with parameters",
    tags=["template", "instantiation"],
    category="template_management"
)
async def instantiate_template(
    template_id: str,
    parameter_values: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Instantiate a workflow template with parameters.
    
    Args:
        template_id: ID of the template to instantiate
        parameter_values: Values for template parameters
        metadata: Optional metadata
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Instantiation result with workflow definition
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Get template manager
        template_manager = workflow_engine.template_manager
        if not template_manager:
            return {"error": "Template manager not initialized"}
        
        # Instantiate template
        result = await template_manager.instantiate_template(
            template_id=UUID(template_id),
            parameter_values=parameter_values
        )
        
        if not result:
            return {"error": f"Template {template_id} not found"}
        
        instantiation, workflow_def = result
        
        return {
            "instantiation_id": str(instantiation.id),
            "workflow_definition_id": str(workflow_def.id),
            "workflow_name": workflow_def.name,
            "status": "instantiated"
        }
    
    except Exception as e:
        logger.error(f"Error instantiating template: {e}")
        return {"error": f"Error instantiating template: {str(e)}"}


@mcp_capability(
    name="template_management",
    description="Create and manage workflow templates",
    modality="orchestration"
)
@mcp_tool(
    name="ListTemplates",
    description="List available workflow templates",
    tags=["template", "query"],
    category="template_management"
)
async def list_templates(
    category_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    List available workflow templates.
    
    Args:
        category_id: Optional category ID filter
        tags: Optional tags filter
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        List of templates
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Get template manager
        template_manager = workflow_engine.template_manager
        if not template_manager:
            return {"error": "Template manager not initialized"}
        
        # Get templates
        templates = template_manager.get_templates(
            category_id=UUID(category_id) if category_id else None,
            tags=tags or []
        )
        
        return {
            "templates": [
                {
                    "template_id": str(t.id),
                    "name": t.name,
                    "description": t.description,
                    "is_public": t.is_public,
                    "tags": t.tags,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in templates
            ],
            "count": len(templates)
        }
    
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return {"error": f"Error listing templates: {str(e)}"}


# =====================
# Component Integration Tools
# =====================

@mcp_capability(
    name="component_integration",
    description="Integrate with Tekton components",
    modality="integration"
)
@mcp_tool(
    name="ListComponents",
    description="List available Tekton components",
    tags=["component", "query"],
    category="component_integration"
)
async def list_components(
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    List available Tekton components.
    
    Args:
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        List of available components
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Get components from component registry
        components = workflow_engine.component_registry.get_components()
        
        return {
            "components": components,
            "count": len(components)
        }
    
    except Exception as e:
        logger.error(f"Error listing components: {e}")
        return {"error": f"Error listing components: {str(e)}"}


@mcp_capability(
    name="component_integration",
    description="Integrate with Tekton components",
    modality="integration"
)
@mcp_tool(
    name="GetComponentActions",
    description="Get available actions for a component",
    tags=["component", "actions"],
    category="component_integration"
)
async def get_component_actions(
    component_name: str,
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Get available actions for a component.
    
    Args:
        component_name: Name of the component
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        List of available actions
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Check if component exists
        if not workflow_engine.component_registry.has_component(component_name):
            return {"error": f"Component {component_name} not found"}
        
        component = workflow_engine.component_registry.get_component(component_name)
        
        # Get actions
        actions = await component.get_actions()
        
        return {
            "component_name": component_name,
            "actions": actions,
            "count": len(actions)
        }
    
    except Exception as e:
        logger.error(f"Error getting component actions: {e}")
        return {"error": f"Error getting component actions: {str(e)}"}


@mcp_capability(
    name="component_integration",
    description="Integrate with Tekton components",
    modality="integration"
)
@mcp_tool(
    name="ExecuteComponentAction",
    description="Execute an action on a component",
    tags=["component", "action", "execution"],
    category="component_integration"
)
async def execute_component_action(
    component_name: str,
    action: str,
    parameters: Dict[str, Any],
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    """
    Execute an action on a component.
    
    Args:
        component_name: Name of the component
        action: Name of the action to execute
        parameters: Parameters for the action
        workflow_engine: Workflow engine instance (injected)
        
    Returns:
        Action execution result
    """
    if not workflow_engine:
        logger.error("Workflow engine not provided")
        return {"error": "Workflow engine not provided"}
    
    try:
        # Execute action using component registry
        result = await workflow_engine.component_registry.execute_action(
            component_name=component_name,
            action=action,
            params=parameters
        )
        
        return {
            "component_name": component_name,
            "action": action,
            "result": result,
            "status": "executed"
        }
    
    except Exception as e:
        logger.error(f"Error executing component action: {e}")
        return {"error": f"Error executing component action: {str(e)}"}


# =====================
# Tool Registration
# =====================

async def register_tools(
    workflow_engine: Optional[WorkflowEngine] = None,
    skip_tools: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Register all tools with the MCP service.
    
    Args:
        workflow_engine: Workflow engine to use for registration
        skip_tools: List of tool names to skip
        
    Returns:
        Registration results
    """
    # Get all tools defined in this module
    tools = [
        create_workflow_definition, update_workflow_definition, delete_workflow_definition,
        get_workflow_definition, list_workflow_definitions,
        execute_workflow, cancel_workflow_execution, pause_workflow_execution,
        resume_workflow_execution, get_workflow_execution_status, list_workflow_executions,
        create_template, instantiate_template, list_templates,
        list_components, get_component_actions, execute_component_action
    ]
    
    # Filter tools to skip if provided
    if skip_tools:
        tools = [tool for tool in tools if tool.__name__ not in skip_tools]
    
    # Create dependencies dict for injecting into tool handlers
    deps = {}
    if workflow_engine:
        deps["workflow_engine"] = workflow_engine
    
    # Register tools with dependencies
    # TODO: Fix FastMCP integration - register_tools_util expects different signature
    # The tekton.mcp.fastmcp.utils.register_tools expects (registry, tools, component_manager)
    # but this code is calling it with (tools, deps)
    logger.warning("FastMCP tool registration skipped - signature mismatch")
    return {
        "registered": 0,
        "failed": 0,
        "results": [],
        "message": "Tool registration skipped due to signature mismatch"
    }


def get_all_tools(workflow_engine=None):
    """Get all Harmonia MCP tools."""
    from tekton.mcp.fastmcp.schema import MCPTool
    
    tools = []
    
    # Get all workflow tools defined in this module
    all_tools = [
        create_workflow_definition, update_workflow_definition, delete_workflow_definition,
        get_workflow_definition, list_workflow_definitions,
        execute_workflow, cancel_workflow_execution, pause_workflow_execution,
        resume_workflow_execution, get_workflow_execution_status, list_workflow_executions,
        create_template, instantiate_template, list_templates,
        list_components, get_component_actions, execute_component_action
    ]
    
    # Convert tools to dict format
    for tool_func in all_tools:
        if hasattr(tool_func, '_mcp_tool_meta'):
            tools.append(tool_func._mcp_tool_meta.to_dict())
    
    logger.info(f"get_all_tools returning {len(tools)} Harmonia workflow tools")
    return tools