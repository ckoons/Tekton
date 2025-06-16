"""
Repository Service for Ergon.

This module provides services for accessing and managing the repository of
tools, agents, and workflows.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ergon.core.database.engine import get_db
from ergon.core.repository.models import (
    Component, Tool, AgentComponent, Workflow, Capability,
    Parameter, Metadata, ComponentFile, ComponentType
)
from ergon.core.vector_store.faiss_store import FAISSDocumentStore

# Setup logging
logger = logging.getLogger(__name__)


class RepositoryService:
    """Service for managing the repository of tools, agents, and workflows."""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize the repository service.
        
        Args:
            db: Database session. If None, a new session will be created.
        """
        self.db = db or next(get_db())
        self.vector_store = FAISSDocumentStore()
        
    def create_tool(self, 
                   name: str, 
                   description: str, 
                   entry_point: str,
                   implementation_type: str = "python",
                   capabilities: List[Dict[str, str]] = None,
                   parameters: List[Dict[str, Any]] = None,
                   metadata: Dict[str, str] = None,
                   files: List[Dict[str, str]] = None,
                   version: str = "0.1.0") -> Tool:
        """Create a new tool in the repository.
        
        Args:
            name: Name of the tool
            description: Description of the tool
            entry_point: Entry point for the tool (e.g. function name)
            implementation_type: Type of implementation (e.g. python, js)
            capabilities: List of capabilities for the tool
            parameters: List of parameters for the tool
            metadata: Additional metadata for the tool
            files: List of files associated with the tool
            version: Tool version
            
        Returns:
            The created tool
        """
        # Create the tool
        tool = Tool(
            name=name,
            description=description,
            entry_point=entry_point,
            implementation_type=implementation_type,
            version=version
        )
        
        self.db.add(tool)
        self.db.flush()  # Get the ID without committing
        
        # Add capabilities
        if capabilities:
            for cap in capabilities:
                capability = Capability(
                    component_id=tool.id,
                    name=cap["name"],
                    description=cap.get("description", "")
                )
                self.db.add(capability)
        
        # Add parameters
        if parameters:
            for param in parameters:
                parameter = Parameter(
                    component_id=tool.id,
                    name=param["name"],
                    description=param.get("description", ""),
                    type=param.get("type", "string"),
                    required=param.get("required", False),
                    default_value=param.get("default_value")
                )
                self.db.add(parameter)
        
        # Add metadata
        if metadata:
            for key, value in metadata.items():
                meta = Metadata(
                    component_id=tool.id,
                    key=key,
                    value=value
                )
                self.db.add(meta)
        
        # Add files
        if files:
            for file_info in files:
                component_file = ComponentFile(
                    component_id=tool.id,
                    filename=file_info["filename"],
                    path=file_info["path"],
                    content_type=file_info.get("content_type", "text/plain")
                )
                self.db.add(component_file)
        
        self.db.commit()
        
        # Add to vector store
        self._add_to_vector_store(tool)
        
        return tool
    
    def create_agent(self,
                    name: str,
                    description: str,
                    model: str,
                    system_prompt: str,
                    tools: Optional[List[Dict[str, Any]]] = None,
                    capabilities: Optional[List[Dict[str, str]]] = None,
                    parameters: Optional[List[Dict[str, Any]]] = None,
                    metadata: Optional[Dict[str, str]] = None,
                    files: Optional[List[Dict[str, str]]] = None,
                    version: str = "0.1.0") -> AgentComponent:
        """Create a new agent in the repository.
        
        Args:
            name: Name of the agent
            description: Description of the agent
            model: Model used by the agent
            system_prompt: System prompt for the agent
            tools: List of tools used by the agent
            capabilities: List of capabilities for the agent
            parameters: List of parameters for the agent
            metadata: Additional metadata for the agent
            files: List of files associated with the agent
            version: Agent version
            
        Returns:
            The created agent
        """
        # Create the agent
        agent = AgentComponent(
            name=name,
            description=description,
            model=model,
            system_prompt=system_prompt,
            tools=tools or [],
            version=version
        )
        
        self.db.add(agent)
        self.db.flush()  # Get the ID without committing
        
        # Add capabilities
        if capabilities:
            for cap in capabilities:
                capability = Capability(
                    component_id=agent.id,
                    name=cap["name"],
                    description=cap.get("description", "")
                )
                self.db.add(capability)
        
        # Add parameters
        if parameters:
            for param in parameters:
                parameter = Parameter(
                    component_id=agent.id,
                    name=param["name"],
                    description=param.get("description", ""),
                    type=param.get("type", "string"),
                    required=param.get("required", False),
                    default_value=param.get("default_value")
                )
                self.db.add(parameter)
        
        # Add metadata
        if metadata:
            for key, value in metadata.items():
                meta = Metadata(
                    component_id=agent.id,
                    key=key,
                    value=value
                )
                self.db.add(meta)
        
        # Add files
        if files:
            for file_info in files:
                component_file = ComponentFile(
                    component_id=agent.id,
                    filename=file_info["filename"],
                    path=file_info["path"],
                    content_type=file_info.get("content_type", "text/plain")
                )
                self.db.add(component_file)
        
        self.db.commit()
        
        # Add to vector store
        self._add_to_vector_store(agent)
        
        return agent
    
    def create_workflow(self,
                       name: str,
                       description: str,
                       definition: Dict[str, Any],
                       capabilities: Optional[List[Dict[str, str]]] = None,
                       parameters: Optional[List[Dict[str, Any]]] = None,
                       metadata: Optional[Dict[str, str]] = None,
                       files: Optional[List[Dict[str, str]]] = None,
                       version: str = "0.1.0") -> Workflow:
        """Create a new workflow in the repository.
        
        Args:
            name: Name of the workflow
            description: Description of the workflow
            definition: Workflow definition
            capabilities: List of capabilities for the workflow
            parameters: List of parameters for the workflow
            metadata: Additional metadata for the workflow
            files: List of files associated with the workflow
            version: Workflow version
            
        Returns:
            The created workflow
        """
        # Create the workflow
        workflow = Workflow(
            name=name,
            description=description,
            definition=definition,
            version=version
        )
        
        self.db.add(workflow)
        self.db.flush()  # Get the ID without committing
        
        # Add capabilities
        if capabilities:
            for cap in capabilities:
                capability = Capability(
                    component_id=workflow.id,
                    name=cap["name"],
                    description=cap.get("description", "")
                )
                self.db.add(capability)
        
        # Add parameters
        if parameters:
            for param in parameters:
                parameter = Parameter(
                    component_id=workflow.id,
                    name=param["name"],
                    description=param.get("description", ""),
                    type=param.get("type", "string"),
                    required=param.get("required", False),
                    default_value=param.get("default_value")
                )
                self.db.add(parameter)
        
        # Add metadata
        if metadata:
            for key, value in metadata.items():
                meta = Metadata(
                    component_id=workflow.id,
                    key=key,
                    value=value
                )
                self.db.add(meta)
        
        # Add files
        if files:
            for file_info in files:
                component_file = ComponentFile(
                    component_id=workflow.id,
                    filename=file_info["filename"],
                    path=file_info["path"],
                    content_type=file_info.get("content_type", "text/plain")
                )
                self.db.add(component_file)
        
        self.db.commit()
        
        # Add to vector store
        self._add_to_vector_store(workflow)
        
        return workflow
    
    def get_component(self, component_id: int) -> Optional[Component]:
        """Get a component by ID.
        
        Args:
            component_id: ID of the component
            
        Returns:
            The component or None if not found
        """
        return self.db.query(Component).filter(Component.id == component_id).first()
    
    def get_component_by_name(self, name: str) -> Optional[Component]:
        """Get a component by name.
        
        Args:
            name: Name of the component
            
        Returns:
            The component or None if not found
        """
        return self.db.query(Component).filter(Component.name == name).first()
    
    def list_components(self, 
                       component_type: Optional[ComponentType] = None,
                       active_only: bool = True) -> List[Component]:
        """List components in the repository.
        
        Args:
            component_type: Filter by component type
            active_only: Only include active components
            
        Returns:
            List of components
        """
        query = self.db.query(Component)
        
        if component_type:
            query = query.filter(Component.type == component_type)
        
        if active_only:
            query = query.filter(Component.is_active == True)
        
        return query.all()
    
    def search_components(self, 
                         query: str, 
                         component_type: Optional[ComponentType] = None,
                         limit: int = 10) -> List[Tuple[Component, float]]:
        """Search for components using vector similarity search.
        
        Args:
            query: Search query
            component_type: Filter by component type
            limit: Maximum number of results
            
        Returns:
            List of (component, score) tuples
        """
        # First, search in vector store
        component_ids, scores = self.vector_store.search(query, limit=limit * 2)  # Get more results for filtering
        
        # Fetch components
        components = []
        if component_ids:
            query = self.db.query(Component).filter(Component.id.in_(component_ids))
            
            if component_type:
                query = query.filter(Component.type == component_type)
            
            query = query.filter(Component.is_active == True)
            
            db_components = query.all()
            
            # Map components to scores
            component_dict = {comp.id: comp for comp in db_components}
            
            for i, component_id in enumerate(component_ids):
                if component_id in component_dict:
                    components.append((component_dict[component_id], scores[i]))
                    
                    if len(components) >= limit:
                        break
        
        return components
    
    def update_component(self, 
                        component_id: int, 
                        updates: Dict[str, Any]) -> Optional[Component]:
        """Update a component in the repository.
        
        Args:
            component_id: ID of the component
            updates: Dictionary of fields to update
            
        Returns:
            The updated component or None if not found
        """
        component = self.get_component(component_id)
        if not component:
            return None
        
        for key, value in updates.items():
            if hasattr(component, key):
                setattr(component, key, value)
        
        component.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Update vector store
        self._add_to_vector_store(component, update=True)
        
        return component
    
    def delete_component(self, component_id: int) -> bool:
        """Delete a component from the repository.
        
        Args:
            component_id: ID of the component
            
        Returns:
            True if deleted, False if not found
        """
        component = self.get_component(component_id)
        if not component:
            return False
        
        # Mark as inactive instead of deleting
        component.is_active = False
        component.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def _add_to_vector_store(self, component: Component, update: bool = False) -> None:
        """Add a component to the vector store.
        
        Args:
            component: Component to add
            update: Whether this is an update
        """
        # Create a text representation of the component for embedding
        text = f"{component.name}\n{component.description}\n"
        
        # Add capabilities
        for capability in component.capabilities:
            text += f"Capability: {capability.name} - {capability.description}\n"
        
        # Add parameters
        for parameter in component.parameters:
            text += f"Parameter: {parameter.name} - {parameter.description}\n"
        
        # Add the component to the vector store
        if update:
            self.vector_store.update(component.id, text)
        else:
            self.vector_store.add(component.id, text)