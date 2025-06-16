"""
Telos Client - Client for interacting with the Telos requirements management component.

This module provides a client for interacting with Telos's requirements management capabilities
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


class TelosClient(ComponentClient):
    """Client for the Telos requirements management component."""
    
    def __init__(
        self,
        component_id: str = "telos.requirements",
        hermes_url: Optional[str] = None,
        security_context: Optional[SecurityContext] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """
        Initialize the Telos client.
        
        Args:
            component_id: ID of the Telos component to connect to (default: "telos.requirements")
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
    
    async def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new requirements project.
        
        Args:
            name: Name of the project
            description: Optional description of the project
            metadata: Optional additional metadata for the project
            
        Returns:
            Dictionary with project information (including project_id)
            
        Raises:
            CapabilityInvocationError: If the project creation fails
            ComponentUnavailableError: If the Telos component is unavailable
        """
        parameters = {"name": name}
        
        if description:
            parameters["description"] = description
            
        if metadata:
            parameters["metadata"] = metadata
            
        result = await self.invoke_capability("create_project", parameters)
        
        if not isinstance(result, dict) or "project_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Telos",
                result
            )
            
        return result
    
    async def create_requirement(
        self,
        project_id: str,
        title: str,
        description: str,
        priority: Optional[str] = None,
        requirement_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new requirement within a project.
        
        Args:
            project_id: ID of the project to add the requirement to
            title: Title of the requirement
            description: Description of the requirement
            priority: Optional priority level (e.g., "high", "medium", "low")
            requirement_type: Optional type of requirement (e.g., "functional", "performance")
            metadata: Optional additional metadata for the requirement
            
        Returns:
            Dictionary with requirement information (including requirement_id)
            
        Raises:
            CapabilityInvocationError: If the requirement creation fails
            ComponentUnavailableError: If the Telos component is unavailable
        """
        parameters = {
            "project_id": project_id,
            "title": title,
            "description": description
        }
        
        if priority:
            parameters["priority"] = priority
            
        if requirement_type:
            parameters["type"] = requirement_type
            
        if metadata:
            parameters["metadata"] = metadata
            
        result = await self.invoke_capability("create_requirement", parameters)
        
        if not isinstance(result, dict) or "requirement_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Telos",
                result
            )
            
        return result
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get information about a project.
        
        Args:
            project_id: ID of the project to get
            
        Returns:
            Dictionary with project information
            
        Raises:
            CapabilityInvocationError: If the project retrieval fails
            ComponentUnavailableError: If the Telos component is unavailable
        """
        parameters = {"project_id": project_id}
        
        result = await self.invoke_capability("get_project", parameters)
        
        if not isinstance(result, dict) or "name" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Telos",
                result
            )
            
        return result
    
    async def get_requirements(
        self,
        project_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get requirements for a project.
        
        Args:
            project_id: ID of the project to get requirements for
            filters: Optional filters to apply (e.g., priority, type)
            
        Returns:
            List of dictionaries with requirement information
            
        Raises:
            CapabilityInvocationError: If the requirements retrieval fails
            ComponentUnavailableError: If the Telos component is unavailable
        """
        parameters = {"project_id": project_id}
        
        if filters:
            parameters["filter"] = filters
            
        result = await self.invoke_capability("get_requirements", parameters)
        
        if not isinstance(result, dict) or "requirements" not in result or not isinstance(result["requirements"], list):
            raise CapabilityInvocationError(
                "Unexpected response format from Telos",
                result
            )
            
        return result["requirements"]
    
    async def analyze_requirements(
        self,
        project_id: str,
        analysis_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze requirements for a project.
        
        Args:
            project_id: ID of the project to analyze
            analysis_type: Optional type of analysis to perform
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            CapabilityInvocationError: If the requirements analysis fails
            ComponentUnavailableError: If the Telos component is unavailable
        """
        parameters = {"project_id": project_id}
        
        if analysis_type:
            parameters["analysis_type"] = analysis_type
            
        result = await self.invoke_capability("analyze_requirements", parameters)
        
        if not isinstance(result, dict) or "analysis" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Telos",
                result
            )
            
        return result
    
    async def refine_requirement(
        self,
        requirement_id: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Refine a requirement based on feedback.
        
        Args:
            requirement_id: ID of the requirement to refine
            feedback: Optional feedback to incorporate
            
        Returns:
            Dictionary with the refined requirement
            
        Raises:
            CapabilityInvocationError: If the requirement refinement fails
            ComponentUnavailableError: If the Telos component is unavailable
        """
        parameters = {"requirement_id": requirement_id}
        
        if feedback:
            parameters["feedback"] = feedback
            
        result = await self.invoke_capability("refine_requirement", parameters)
        
        if not isinstance(result, dict) or "requirement" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Telos",
                result
            )
            
        return result["requirement"]
            
    async def llm_analyze_requirement(
        self,
        requirement_text: str,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a requirement using LLM capabilities.
        
        Args:
            requirement_text: The text of the requirement to analyze
            context: Optional additional context about the project
            model: Optional model to use for analysis
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            CapabilityInvocationError: If the requirement analysis fails
            ComponentUnavailableError: If the Telos component is unavailable
        """
        parameters = {"requirement_text": requirement_text}
        
        if context:
            parameters["context"] = context
            
        if model:
            parameters["model"] = model
            
        result = await self.invoke_capability("llm_analyze_requirement", parameters)
        
        if not isinstance(result, dict):
            raise CapabilityInvocationError(
                "Unexpected response format from Telos",
                result
            )
            
        return result
    
    async def llm_generate_traces(
        self,
        requirements: str,
        artifacts: str,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate traceability links between requirements and implementation artifacts.
        
        Args:
            requirements: The requirements text or representation
            artifacts: The implementation artifacts text or representation
            context: Optional additional context
            model: Optional model to use for trace generation
            
        Returns:
            Dictionary with traceability results
            
        Raises:
            CapabilityInvocationError: If the trace generation fails
            ComponentUnavailableError: If the Telos component is unavailable
        """
        parameters = {
            "requirements": requirements,
            "artifacts": artifacts
        }
        
        if context:
            parameters["context"] = context
            
        if model:
            parameters["model"] = model
            
        result = await self.invoke_capability("llm_generate_traces", parameters)
        
        if not isinstance(result, dict):
            raise CapabilityInvocationError(
                "Unexpected response format from Telos",
                result
            )
            
        return result
    
    async def llm_initialize_project(
        self,
        project_name: str,
        project_description: Optional[str] = None,
        project_domain: Optional[str] = None,
        stakeholders: Optional[str] = None,
        constraints: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initialize a new requirements project with LLM-generated recommendations.
        
        Args:
            project_name: Name of the project
            project_description: Optional description of the project
            project_domain: Optional domain/industry of the project
            stakeholders: Optional key stakeholders information
            constraints: Optional project constraints
            model: Optional model to use for initialization
            
        Returns:
            Dictionary with project initialization recommendations
            
        Raises:
            CapabilityInvocationError: If the project initialization fails
            ComponentUnavailableError: If the Telos component is unavailable
        """
        parameters = {"project_name": project_name}
        
        if project_description:
            parameters["project_description"] = project_description
            
        if project_domain:
            parameters["project_domain"] = project_domain
            
        if stakeholders:
            parameters["stakeholders"] = stakeholders
            
        if constraints:
            parameters["constraints"] = constraints
            
        if model:
            parameters["model"] = model
            
        result = await self.invoke_capability("llm_initialize_project", parameters)
        
        if not isinstance(result, dict):
            raise CapabilityInvocationError(
                "Unexpected response format from Telos",
                result
            )
            
        return result


class TelosUIClient(ComponentClient):
    """Client for the Telos UI component."""
    
    def __init__(
        self,
        component_id: str = "telos.ui",
        hermes_url: Optional[str] = None,
        security_context: Optional[SecurityContext] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """
        Initialize the Telos UI client.
        
        Args:
            component_id: ID of the Telos UI component to connect to (default: "telos.ui")
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
    
    async def interactive_refine(
        self,
        project_id: str,
        requirement_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start an interactive refinement session.
        
        Args:
            project_id: ID of the project
            requirement_id: Optional ID of a specific requirement to refine
            
        Returns:
            Dictionary with session information
            
        Raises:
            CapabilityInvocationError: If the interactive refinement fails
            ComponentUnavailableError: If the Telos UI component is unavailable
        """
        parameters = {"project_id": project_id}
        
        if requirement_id:
            parameters["requirement_id"] = requirement_id
            
        result = await self.invoke_capability("interactive_refine", parameters)
        
        if not isinstance(result, dict) or "session_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Telos UI",
                result
            )
            
        return result
    
    async def visualize_project(
        self,
        project_id: str,
        visualization_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a visualization for a project.
        
        Args:
            project_id: ID of the project to visualize
            visualization_type: Optional type of visualization
            
        Returns:
            Dictionary with visualization information
            
        Raises:
            CapabilityInvocationError: If the visualization fails
            ComponentUnavailableError: If the Telos UI component is unavailable
        """
        parameters = {"project_id": project_id}
        
        if visualization_type:
            parameters["visualization_type"] = visualization_type
            
        result = await self.invoke_capability("visualize_project", parameters)
        
        if not isinstance(result, dict) or "visualization" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Telos UI",
                result
            )
            
        return result


async def get_telos_client(
    component_id: str = "telos.requirements",
    hermes_url: Optional[str] = None,
    security_context: Optional[SecurityContext] = None,
    retry_policy: Optional[RetryPolicy] = None
) -> TelosClient:
    """
    Create a client for the Telos requirements management component.
    
    Args:
        component_id: ID of the Telos component to connect to (default: "telos.requirements")
        hermes_url: URL of the Hermes API
        security_context: Security context for authentication/authorization
        retry_policy: Policy for retrying capability invocations
        
    Returns:
        TelosClient instance
        
    Raises:
        ComponentNotFoundError: If the Telos component is not found
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
    return TelosClient(
        component_id=component_id,
        hermes_url=hermes_url,
        security_context=security_context,
        retry_policy=retry_policy
    )


async def get_telos_ui_client(
    component_id: str = "telos.ui",
    hermes_url: Optional[str] = None,
    security_context: Optional[SecurityContext] = None,
    retry_policy: Optional[RetryPolicy] = None
) -> TelosUIClient:
    """
    Create a client for the Telos UI component.
    
    Args:
        component_id: ID of the Telos UI component to connect to (default: "telos.ui")
        hermes_url: URL of the Hermes API
        security_context: Security context for authentication/authorization
        retry_policy: Policy for retrying capability invocations
        
    Returns:
        TelosUIClient instance
        
    Raises:
        ComponentNotFoundError: If the Telos UI component is not found
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
    return TelosUIClient(
        component_id=component_id,
        hermes_url=hermes_url,
        security_context=security_context,
        retry_policy=retry_policy
    )