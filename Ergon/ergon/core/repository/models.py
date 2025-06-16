"""
Tool, Agent, and Workflow Repository Models.

This module defines the database models for storing and retrieving tools, agents,
and workflows in the Ergon repository.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union

from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship

from ergon.core.database.engine import Base


class ComponentType(str, Enum):
    """Types of components in the repository."""
    TOOL = "tool"
    AGENT = "agent"
    WORKFLOW = "workflow"


class Component(Base):
    """Base model for all components in the repository."""
    __tablename__ = "components"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(String(50), nullable=False, default="0.1.0")
    is_active = Column(Boolean, default=True)
    
    # Relationships
    capabilities = relationship("Capability", back_populates="component")
    parameters = relationship("Parameter", back_populates="component")
    meta_items = relationship("Metadata", back_populates="component")
    files = relationship("ComponentFile", back_populates="component")
    
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'component'
    }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version,
            "is_active": self.is_active,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "parameters": [p.to_dict() for p in self.parameters],
            "metadata": {m.key: m.value for m in self.meta_items},
            "files": [f.to_dict() for f in self.files]
        }


class Tool(Component):
    """Model for tools in the repository."""
    __tablename__ = "tools"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, ForeignKey("components.id"), primary_key=True)
    implementation_type = Column(String(50), nullable=False, default="python")
    entry_point = Column(String(255), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'tool'
    }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation."""
        result = super().to_dict()
        result.update({
            "implementation_type": self.implementation_type,
            "entry_point": self.entry_point
        })
        return result


class AgentComponent(Component):
    """Model for agents in the repository."""
    __tablename__ = "repo_agents"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, ForeignKey("components.id"), primary_key=True)
    model = Column(String(255), nullable=False)
    system_prompt = Column(Text, nullable=False)
    tools = Column(JSON, nullable=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'agent_component'
    }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        result = super().to_dict()
        result.update({
            "model": self.model,
            "system_prompt": self.system_prompt,
            "tools": self.tools
        })
        return result


class Workflow(Component):
    """Model for workflows in the repository."""
    __tablename__ = "workflows"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, ForeignKey("components.id"), primary_key=True)
    definition = Column(JSON, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'workflow'
    }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        result = super().to_dict()
        result.update({
            "definition": self.definition
        })
        return result


class Capability(Base):
    """Model for component capabilities."""
    __tablename__ = "capabilities"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Relationships
    component = relationship("Component", back_populates="capabilities")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert capability to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class Parameter(Base):
    """Model for component parameters."""
    __tablename__ = "parameters"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    required = Column(Boolean, default=False)
    default_value = Column(Text, nullable=True)
    
    # Relationships
    component = relationship("Component", back_populates="parameters")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameter to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "required": self.required,
            "default_value": self.default_value
        }


class Metadata(Base):
    """Model for component metadata."""
    __tablename__ = "metadata"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    
    # Relationships
    component = relationship("Component", back_populates="meta_items")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary representation."""
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value
        }


class ComponentFile(Base):
    """Model for files associated with components."""
    __tablename__ = "component_files"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    path = Column(String(512), nullable=False)
    content_type = Column(String(100), nullable=False)
    
    # Relationships
    component = relationship("Component", back_populates="files")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert file to dictionary representation."""
        return {
            "id": self.id,
            "filename": self.filename,
            "path": self.path,
            "content_type": self.content_type
        }