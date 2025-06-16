"""
Protocol data models for Apollo.

This module defines the data models used for protocol enforcement and monitoring.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Set
from enum import Enum
from pydantic import Field
from tekton.models import TektonBaseModel


class ProtocolType(str, Enum):
    """Types of protocols that can be enforced."""
    MESSAGE_FORMAT = "message_format"
    REQUEST_FLOW = "request_flow"
    RESPONSE_FORMAT = "response_format"
    AUTHENTICATION = "authentication"
    RATE_LIMITING = "rate_limiting"
    DATA_VALIDATION = "data_validation"
    ERROR_HANDLING = "error_handling"
    EVENT_SEQUENCING = "event_sequencing"


class ProtocolSeverity(str, Enum):
    """Severity levels for protocol violations."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ProtocolScope(str, Enum):
    """Scope of protocol application."""
    GLOBAL = "global"
    COMPONENT = "component"
    ENDPOINT = "endpoint"
    MESSAGE_TYPE = "message_type"


class EnforcementMode(str, Enum):
    """How protocol violations should be handled."""
    MONITOR = "monitor"  # Just log and report violations
    WARN = "warn"  # Log, report, and send warnings
    ENFORCE = "enforce"  # Actively block or correct violations
    ADAPT = "adapt"  # Correct and adapt to violations where possible


class ProtocolDefinition(TektonBaseModel):
    """Definition of a protocol to be enforced."""
    protocol_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: ProtocolType
    scope: ProtocolScope
    enforcement_mode: EnforcementMode
    severity: ProtocolSeverity
    version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Where the protocol applies
    applicable_components: List[str] = Field(default_factory=list)
    applicable_endpoints: List[str] = Field(default_factory=list)
    applicable_message_types: List[str] = Field(default_factory=list)
    
    # Protocol-specific rules
    rules: Dict[str, Any] = Field(default_factory=dict)
    protocol_schema: Optional[Dict[str, Any]] = Field(default=None, alias="schema")
    
    # Runtime configuration
    enabled: bool = True
    priority: int = 5  # 1-10, higher is more important


class ProtocolViolation(TektonBaseModel):
    """Record of a protocol violation."""
    violation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    protocol_id: str
    component: str
    endpoint: Optional[str] = None
    message_type: Optional[str] = None
    severity: ProtocolSeverity
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    context_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    corrective_action_taken: Optional[str] = None


class ProtocolStats(TektonBaseModel):
    """Statistics for protocol enforcement."""
    protocol_id: str
    total_evaluations: int = 0
    total_violations: int = 0
    violations_by_severity: Dict[ProtocolSeverity, int] = Field(default_factory=lambda: {
        severity: 0 for severity in ProtocolSeverity
    })
    violations_by_component: Dict[str, int] = Field(default_factory=dict)
    last_violation: Optional[datetime] = None
    last_evaluation: Optional[datetime] = None


class MessageFormatRule(TektonBaseModel):
    """Rules for message format protocols."""
    required_fields: List[str] = Field(default_factory=list)
    forbidden_fields: List[str] = Field(default_factory=list)
    field_types: Dict[str, str] = Field(default_factory=dict)
    max_size_bytes: Optional[int] = None
    serialization_format: Optional[str] = None  # json, msgpack, etc.


class RequestFlowRule(TektonBaseModel):
    """Rules for request flow protocols."""
    required_headers: Dict[str, str] = Field(default_factory=dict)
    allowed_methods: List[str] = Field(default_factory=list)
    rate_limit: Optional[int] = None  # requests per minute
    required_auth: bool = False
    sequence_requirements: List[str] = Field(default_factory=list)
    prerequisite_requests: List[str] = Field(default_factory=list)


class ResponseFormatRule(TektonBaseModel):
    """Rules for response format protocols."""
    status_codes: List[int] = Field(default_factory=list)
    required_headers: Dict[str, str] = Field(default_factory=dict)
    required_fields: List[str] = Field(default_factory=list)
    max_response_time_ms: Optional[int] = None


class EventSequenceRule(TektonBaseModel):
    """Rules for event sequencing protocols."""
    sequence_order: List[str] = Field(default_factory=list)
    max_interval_ms: Optional[int] = None
    required_correlation_id: bool = False
    allowed_parallel_events: Optional[List[str]] = None