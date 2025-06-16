"""
Harmonia Client - Client for interacting with the Harmonia workflow component.

This module provides a client for interacting with Harmonia's workflow orchestration capabilities
through the standardized Tekton component client interface.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union

# Try to import from tekton-core first
try:
    from tekton.utils.component_client import (
        ComponentClient,
        ComponentError,
        ComponentNotFoundError,
        CapabilityNotFoundError,
        CapabilityInvocationError,
        ComponentUnavailableError,
        SecurityContext,
        RetryPolicy,
    )
except ImportError:
    # If tekton-core is not available, use a minimal implementation
    from .utils.component_client import (
        ComponentClient,
        ComponentError,
        ComponentNotFoundError,
        CapabilityNotFoundError,
        CapabilityInvocationError,
        ComponentUnavailableError,
        SecurityContext,
        RetryPolicy,
    )

# Configure logger
logger = logging.getLogger(__name__)


class HarmoniaClient(ComponentClient):
    """Client for the Harmonia workflow component."""
    
    def __init__(
        self,
        component_id: str = "harmonia.workflow",
        hermes_url: Optional[str] = None,
        security_context: Optional[SecurityContext] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """
        Initialize the Harmonia client.
        
        Args:
            component_id: ID of the Harmonia component to connect to (default: "harmonia.workflow")
            hermes_url: URL of the Hermes API
            security_context: Security context for authentication/authorization
            retry_policy: Policy for retrying capability invocations
        """
        super().__init__(
            component_id=component_id,
            hermes_url=hermes_url,
            security_context=security_context,
            retry_policy=retry_policy
        )
    
    async def create_workflow(
        self,
        name: str,
        tasks: List[Dict[str, Any]],
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new workflow definition.
        
        Args:
            name: Name of the workflow
            tasks: List of tasks in the workflow
            description: Optional description of the workflow
            input_schema: Optional schema for workflow inputs
            output_schema: Optional schema for workflow outputs
            
        Returns:
            Dictionary with workflow information (including workflow_id)
            
        Raises:
            CapabilityInvocationError: If the workflow creation fails
            ComponentUnavailableError: If the Harmonia component is unavailable
        """
        parameters = {
            "name": name,
            "tasks": tasks
        }
        
        if description:
            parameters["description"] = description
            
        if input_schema:
            parameters["input"] = input_schema
            
        if output_schema:
            parameters["output"] = output_schema
            
        result = await self.invoke_capability("create_workflow", parameters)
        
        if not isinstance(result, dict) or "workflow_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Harmonia",
                result
            )
            
        return result
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            input_data: Optional input data for the workflow
            
        Returns:
            Dictionary with execution information (including execution_id)
            
        Raises:
            CapabilityInvocationError: If the workflow execution fails
            ComponentUnavailableError: If the Harmonia component is unavailable
        """
        parameters = {"workflow_id": workflow_id}
        
        if input_data:
            parameters["input"] = input_data
            
        result = await self.invoke_capability("execute_workflow", parameters)
        
        if not isinstance(result, dict) or "execution_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Harmonia",
                result
            )
            
        return result
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution.
        
        Args:
            execution_id: ID of the workflow execution to get status for
            
        Returns:
            Dictionary with execution status information
            
        Raises:
            CapabilityInvocationError: If the status retrieval fails
            ComponentUnavailableError: If the Harmonia component is unavailable
        """
        parameters = {"execution_id": execution_id}
        
        result = await self.invoke_capability("get_workflow_status", parameters)
        
        if not isinstance(result, dict) or "status" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Harmonia",
                result
            )
            
        return result
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """
        Cancel a workflow execution.
        
        Args:
            execution_id: ID of the workflow execution to cancel
            
        Returns:
            True if the cancellation was successful
            
        Raises:
            CapabilityInvocationError: If the cancellation fails
            ComponentUnavailableError: If the Harmonia component is unavailable
        """
        parameters = {"execution_id": execution_id}
        
        result = await self.invoke_capability("cancel_workflow", parameters)
        
        if not isinstance(result, dict) or "success" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Harmonia",
                result
            )
            
        return result["success"]


class HarmoniaStateClient(ComponentClient):
    """Client for the Harmonia state management component."""
    
    def __init__(
        self,
        component_id: str = "harmonia.state",
        hermes_url: Optional[str] = None,
        security_context: Optional[SecurityContext] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """
        Initialize the Harmonia state client.
        
        Args:
            component_id: ID of the Harmonia state component to connect to (default: "harmonia.state")
            hermes_url: URL of the Hermes API
            security_context: Security context for authentication/authorization
            retry_policy: Policy for retrying capability invocations
        """
        super().__init__(
            component_id=component_id,
            hermes_url=hermes_url,
            security_context=security_context,
            retry_policy=retry_policy
        )
    
    async def save_state(
        self,
        execution_id: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        Save workflow state.
        
        Args:
            execution_id: ID of the workflow execution
            state: State data to save
            
        Returns:
            True if the state was saved successfully
            
        Raises:
            CapabilityInvocationError: If the state saving fails
            ComponentUnavailableError: If the Harmonia state component is unavailable
        """
        parameters = {
            "execution_id": execution_id,
            "state": state
        }
        
        result = await self.invoke_capability("save_state", parameters)
        
        if not isinstance(result, dict) or "success" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Harmonia State",
                result
            )
            
        return result["success"]
    
    async def load_state(self, execution_id: str) -> Dict[str, Any]:
        """
        Load workflow state.
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            Dictionary with state data
            
        Raises:
            CapabilityInvocationError: If the state loading fails
            ComponentUnavailableError: If the Harmonia state component is unavailable
        """
        parameters = {"execution_id": execution_id}
        
        result = await self.invoke_capability("load_state", parameters)
        
        if not isinstance(result, dict) or "state" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Harmonia State",
                result
            )
            
        return result["state"]
    
    async def create_checkpoint(self, execution_id: str) -> Dict[str, Any]:
        """
        Create a checkpoint of workflow state.
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            Dictionary with checkpoint information
            
        Raises:
            CapabilityInvocationError: If the checkpoint creation fails
            ComponentUnavailableError: If the Harmonia state component is unavailable
        """
        parameters = {"execution_id": execution_id}
        
        result = await self.invoke_capability("create_checkpoint", parameters)
        
        if not isinstance(result, dict) or "checkpoint_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Harmonia State",
                result
            )
            
        return result


async def get_harmonia_client(
    component_id: str = "harmonia.workflow",
    hermes_url: Optional[str] = None,
    security_context: Optional[SecurityContext] = None,
    retry_policy: Optional[RetryPolicy] = None
) -> HarmoniaClient:
    """
    Create a client for the Harmonia workflow component.
    
    Args:
        component_id: ID of the Harmonia component to connect to (default: "harmonia.workflow")
        hermes_url: URL of the Hermes API
        security_context: Security context for authentication/authorization
        retry_policy: Policy for retrying capability invocations
        
    Returns:
        HarmoniaClient instance
        
    Raises:
        ComponentNotFoundError: If the Harmonia component is not found
        ComponentUnavailableError: If the Hermes API is unavailable
    """
    # Try to import from tekton-core first
    try:
        from tekton.utils.component_client import discover_component
    except ImportError:
        # If tekton-core is not available, use a minimal implementation
        from .utils.component_client import discover_component
    
    # Check if the component exists
    await discover_component(component_id, hermes_url)
    
    # Create the client
    return HarmoniaClient(
        component_id=component_id,
        hermes_url=hermes_url,
        security_context=security_context,
        retry_policy=retry_policy
    )


async def get_harmonia_state_client(
    component_id: str = "harmonia.state",
    hermes_url: Optional[str] = None,
    security_context: Optional[SecurityContext] = None,
    retry_policy: Optional[RetryPolicy] = None
) -> HarmoniaStateClient:
    """
    Create a client for the Harmonia state management component.
    
    Args:
        component_id: ID of the Harmonia state component to connect to (default: "harmonia.state")
        hermes_url: URL of the Hermes API
        security_context: Security context for authentication/authorization
        retry_policy: Policy for retrying capability invocations
        
    Returns:
        HarmoniaStateClient instance
        
    Raises:
        ComponentNotFoundError: If the Harmonia state component is not found
        ComponentUnavailableError: If the Hermes API is unavailable
    """
    # Try to import from tekton-core first
    try:
        from tekton.utils.component_client import discover_component
    except ImportError:
        # If tekton-core is not available, use a minimal implementation
        from .utils.component_client import discover_component
    
    # Check if the component exists
    await discover_component(component_id, hermes_url)
    
    # Create the client
    return HarmoniaStateClient(
        component_id=component_id,
        hermes_url=hermes_url,
        security_context=security_context,
        retry_policy=retry_policy
    )