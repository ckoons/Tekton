"""Database models for Ergon v2 with evolutionary JSONB schema."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum as PyEnum
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean, 
    DateTime, ForeignKey, Table, JSON, ARRAY, Enum,
    Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class SolutionType(str, PyEnum):
    """Types of solutions that can be cataloged."""
    TOOL = "tool"
    AGENT = "agent"
    MCP_SERVER = "mcp_server"
    LIBRARY = "library"
    FRAMEWORK = "framework"
    SERVICE = "service"
    WORKFLOW = "workflow"
    TEMPLATE = "template"


class AutonomyLevel(str, PyEnum):
    """Levels of autonomy for build sessions."""
    ADVISORY = "advisory"
    ASSISTED = "assisted"
    GUIDED = "guided"
    AUTONOMOUS = "autonomous"


class BuildOutcome(str, PyEnum):
    """Outcomes of build sessions."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(str, PyEnum):
    """Types of workflow steps."""
    ANALYSIS = "analysis"
    CONFIGURATION = "configuration"
    EXECUTION = "execution"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    DECISION = "decision"


class WorkflowStatus(str, PyEnum):
    """Status of workflows."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


# Many-to-many association tables
solution_capabilities = Table(
    'solution_capabilities',
    Base.metadata,
    Column('solution_id', String(36), ForeignKey('solutions.id')),
    Column('capability_id', String(36), ForeignKey('capabilities.id'))
)

solution_dependencies = Table(
    'solution_dependencies',
    Base.metadata,
    Column('solution_id', String(36), ForeignKey('solutions.id')),
    Column('dependency_id', String(36), ForeignKey('solutions.id'))
)


class Solution(Base):
    """Catalog of reusable solutions (tools, agents, MCP servers, etc.)."""
    __tablename__ = 'solutions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Flexible metadata using JSON for evolution (SQLite compatible)
    extra_metadata = Column(JSON, default={})
    
    # Source information
    source_url = Column(String(1024))
    source_type = Column(String(50))  # github, npm, pypi, local, etc.
    
    # Technical details stored as JSON for flexibility
    technical_details = Column(JSON, default={})
    # Can include: language, framework, dependencies, requirements, etc.
    
    # Usage and quality metrics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_integration_time = Column(Float)  # in minutes
    quality_score = Column(Float)  # calculated metric
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)
    
    # Relationships
    capabilities = relationship("Capability", secondary=solution_capabilities, back_populates="solutions")
    dependencies = relationship("Solution", secondary=solution_dependencies,
                              primaryjoin=id==solution_dependencies.c.solution_id,
                              secondaryjoin=id==solution_dependencies.c.dependency_id)
    integrations = relationship("Integration", back_populates="solution")
    analyses = relationship("Analysis", back_populates="solution")
    configurations = relationship("Configuration", back_populates="solution")


class Capability(Base):
    """Hierarchical taxonomy of capabilities."""
    __tablename__ = 'capabilities'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100))
    parent_id = Column(String(36), ForeignKey('capabilities.id'))
    description = Column(Text)
    
    # Hierarchical relationship
    parent = relationship("Capability", remote_side=[id])
    children = relationship("Capability")
    
    # Solutions with this capability
    solutions = relationship("Solution", secondary=solution_capabilities, back_populates="capabilities")
    
    # Metadata for future extensions
    extra_metadata = Column(JSON, default={})


class Workflow(Base):
    """Captured development workflows for pattern learning."""
    __tablename__ = 'workflows'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Workflow definition as JSON for flexibility
    pattern = Column(JSON, nullable=False)
    # Includes: steps, decisions, conditions, loops, etc.
    
    # Performance metrics
    avg_duration = Column(Float)  # minutes
    success_rate = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    
    # Learning metrics
    improvement_score = Column(Float)  # how much this workflow improves over time
    adaptability_score = Column(Float)  # how well it adapts to different contexts
    
    # Who created it
    created_by = Column(String(100))  # 'human', 'ergon', specific user, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)
    
    # Relationships
    steps = relationship("WorkflowStep", back_populates="workflow", order_by="WorkflowStep.order")
    build_sessions = relationship("BuildSession", back_populates="workflow")
    
    # Metadata for extensions
    extra_metadata = Column(JSON, default={})


class WorkflowStep(Base):
    """Individual steps within workflows."""
    __tablename__ = 'workflow_steps'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workflow_id = Column(String(36), ForeignKey('workflows.id'), nullable=False)
    order = Column(Integer, nullable=False)
    
    type = Column(Enum(StepType), nullable=False)
    action = Column(String(255), nullable=False)
    parameters = Column(JSON, default={})
    expected_result = Column(JSON, default={})
    validation_rules = Column(JSON, default={})
    
    # Execution tracking
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    avg_duration = Column(Float)  # seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")
    
    # Metadata for extensions
    extra_metadata = Column(JSON, default={})


class BuildSession(Base):
    """Records of autonomous build sessions for learning and audit."""
    __tablename__ = 'build_sessions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Workflow used
    workflow_id = Column(String(36), ForeignKey('workflows.id'))
    workflow = relationship("Workflow", back_populates="build_sessions")
    
    # Autonomy level for this session
    autonomy_level = Column(String(50), nullable=False)
    
    # Decision tracking as JSON (SQLite compatible)
    decisions = Column(JSON, default=[])
    # Each decision includes: timestamp, type, rationale, options, selected, approval_required, etc.
    
    # Performance metrics
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_minutes = Column(Float)
    
    # Outcomes
    outcome = Column(String(50))
    outcome_details = Column(JSON, default={})
    
    # Metrics for learning
    metrics = Column(JSON, default={})
    # Includes: lines_of_code, test_coverage, performance_score, quality_metrics, etc.
    
    # User feedback
    user_satisfaction = Column(Integer)  # 1-5 scale
    user_feedback = Column(Text)
    
    # Sprint integration
    sprint_id = Column(String(255))  # Reference to Dev Sprint if created
    
    # Metadata
    extra_metadata = Column(JSON, default={})


class Analysis(Base):
    """GitHub repository analysis results."""
    __tablename__ = 'analyses'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    repository_url = Column(String(1024), nullable=False)
    
    # Analysis results as JSON
    analysis_results = Column(JSON, nullable=False)
    # Includes: architecture, patterns, components, dependencies, quality_metrics, etc.
    
    # Reusability assessment
    reusability_score = Column(Float)
    identified_components = Column(JSON, default=[])
    adaptation_strategies = Column(JSON, default=[])
    
    # Solution if this analysis led to a registry entry
    solution_id = Column(String(36), ForeignKey('solutions.id'))
    solution = relationship("Solution", back_populates="analyses")
    
    # Caching
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    cache_expires_at = Column(DateTime)
    
    # Metadata
    extra_metadata = Column(JSON, default={})


class Configuration(Base):
    """Generated configurations and wrappers."""
    __tablename__ = 'configurations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(String(100))  # fastapi_wrapper, mcp_adapter, docker_config, etc.
    
    # Solution this configures
    solution_id = Column(String(36), ForeignKey('solutions.id'))
    solution = relationship("Solution", back_populates="configurations")
    
    # Template used
    template_id = Column(String(36), ForeignKey('templates.id'))
    template = relationship("Template")
    
    # Generated configuration
    configuration = Column(JSON, nullable=False)
    generated_code = Column(Text)
    
    # Validation status
    validated = Column(Boolean, default=False)
    validation_results = Column(JSON, default={})
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, default={})


class Template(Base):
    """Configuration templates for different wrapper types."""
    __tablename__ = 'templates'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(100), nullable=False)
    version = Column(String(50))
    
    # Template definition
    template_content = Column(Text, nullable=False)
    variables = Column(JSON, default={})  # Required variables and their types
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, default={})


class Integration(Base):
    """Track solution integrations and their outcomes."""
    __tablename__ = 'integrations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Solution being integrated
    solution_id = Column(String(36), ForeignKey('solutions.id'))
    solution = relationship("Solution", back_populates="integrations")
    
    # Integration context
    project_name = Column(String(255))
    integration_type = Column(String(100))  # direct, wrapped, adapted, etc.
    
    # Configuration used
    configuration_id = Column(String(36), ForeignKey('configurations.id'))
    configuration = relationship("Configuration")
    
    # Integration details
    integration_details = Column(JSON, default={})
    
    # Outcome tracking
    success = Column(Boolean)
    integration_time = Column(Float)  # minutes
    issues_encountered = Column(JSON, default=[])
    
    # Timestamps
    integrated_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, default={})


class ChatSession(Base):
    """Tool Chat interaction history for learning."""
    __tablename__ = 'chat_sessions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String(255), nullable=False)
    
    # Chat type
    chat_type = Column(String(50))  # tool_chat, team_chat
    
    # Messages as JSON array
    messages = Column(JSON, default=[])
    
    # Outcomes
    resulted_in_solution = Column(Boolean, default=False)
    solution_id = Column(String(36), ForeignKey('solutions.id'))
    
    resulted_in_build = Column(Boolean, default=False)
    build_session_id = Column(String(36), ForeignKey('build_sessions.id'))
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Metadata
    extra_metadata = Column(JSON, default={})