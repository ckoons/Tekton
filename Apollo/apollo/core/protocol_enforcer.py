"""
Protocol Enforcer Module for Apollo.

This module is responsible for enforcing communication protocols between
Tekton components. It defines, validates, and monitors compliance with
established protocols for data formats, message flows, and interaction patterns.
"""

import os
import json
import logging
import asyncio
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set, Callable
import uuid
import jsonschema

from apollo.models.protocol import (
    ProtocolDefinition,
    ProtocolViolation,
    ProtocolStats,
    ProtocolType,
    ProtocolSeverity,
    ProtocolScope,
    EnforcementMode,
    MessageFormatRule,
    RequestFlowRule,
    ResponseFormatRule,
    EventSequenceRule
)

# Configure logging
logger = logging.getLogger(__name__)


class ProtocolValidator:
    """Base class for protocol validators."""
    
    def __init__(self, protocol: ProtocolDefinition):
        """
        Initialize the protocol validator.
        
        Args:
            protocol: Protocol definition
        """
        self.protocol = protocol
    
    async def validate(
        self, 
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[ProtocolViolation]:
        """
        Validate a message against the protocol.
        
        Args:
            message: Message to validate
            context: Additional context for validation
            
        Returns:
            ProtocolViolation if validation fails, None otherwise
        """
        raise NotImplementedError("Protocol validators must implement validate method")


class MessageFormatValidator(ProtocolValidator):
    """Validator for message format protocols."""
    
    async def validate(
        self, 
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[ProtocolViolation]:
        """Validate message format."""
        # Extract rules
        rules = MessageFormatRule(**self.protocol.rules)
        violations = []
        
        # Check required fields
        for field in rules.required_fields:
            if field not in message:
                violations.append(f"Missing required field: {field}")
                
        # Check forbidden fields
        for field in rules.forbidden_fields:
            if field in message:
                violations.append(f"Forbidden field present: {field}")
                
        # Check field types
        for field, expected_type in rules.field_types.items():
            if field in message:
                # Extract actual value and check type
                value = message[field]
                if expected_type == "string" and not isinstance(value, str):
                    violations.append(f"Field {field} should be string, got {type(value).__name__}")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    violations.append(f"Field {field} should be number, got {type(value).__name__}")
                elif expected_type == "integer" and not isinstance(value, int):
                    violations.append(f"Field {field} should be integer, got {type(value).__name__}")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    violations.append(f"Field {field} should be boolean, got {type(value).__name__}")
                elif expected_type == "array" and not isinstance(value, list):
                    violations.append(f"Field {field} should be array, got {type(value).__name__}")
                elif expected_type == "object" and not isinstance(value, dict):
                    violations.append(f"Field {field} should be object, got {type(value).__name__}")
                    
        # Check message size
        if rules.max_size_bytes:
            # Approximate size by converting to JSON
            size = len(json.dumps(message).encode('utf-8'))
            if size > rules.max_size_bytes:
                violations.append(f"Message size ({size} bytes) exceeds maximum ({rules.max_size_bytes} bytes)")
        
        # If JSON schema is provided, validate against it
        if self.protocol.schema:
            try:
                jsonschema.validate(instance=message, schema=self.protocol.schema)
            except jsonschema.exceptions.ValidationError as e:
                violations.append(f"Schema validation error: {e.message}")
        
        # Create violation if any issues were found
        if violations:
            return ProtocolViolation(
                protocol_id=self.protocol.protocol_id,
                component=context.get("component", "unknown"),
                endpoint=context.get("endpoint"),
                message_type=context.get("message_type"),
                severity=self.protocol.severity,
                message="; ".join(violations),
                details={
                    "violations": violations,
                    "message": message
                },
                context_id=context.get("context_id")
            )
        
        return None


class RequestFlowValidator(ProtocolValidator):
    """Validator for request flow protocols."""
    
    async def validate(
        self, 
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[ProtocolViolation]:
        """Validate request flow."""
        # Extract rules
        rules = RequestFlowRule(**self.protocol.rules)
        violations = []
        
        # Check headers
        headers = context.get("headers", {})
        for header, required_value in rules.required_headers.items():
            if header not in headers:
                violations.append(f"Missing required header: {header}")
            elif required_value and headers[header] != required_value:
                violations.append(f"Header {header} has incorrect value: {headers[header]} (expected {required_value})")
                
        # Check HTTP method
        method = context.get("method")
        if method and rules.allowed_methods and method not in rules.allowed_methods:
            violations.append(f"Method {method} not allowed (allowed: {', '.join(rules.allowed_methods)})")
            
        # Check rate limit
        if rules.rate_limit:
            # Rate limiting would require tracking previous requests
            # This is a simplified check based on context info
            rate = context.get("request_rate", 0)
            if rate > rules.rate_limit:
                violations.append(f"Rate limit exceeded: {rate} requests/min (limit: {rules.rate_limit})")
                
        # Check authentication
        if rules.required_auth and not context.get("authenticated", False):
            violations.append("Authentication required but not provided")
            
        # Check sequence requirements
        if rules.sequence_requirements and "previous_operations" in context:
            prev_ops = context["previous_operations"]
            for req in rules.sequence_requirements:
                # Format: "A->B" means A must come before B
                if "->" in req:
                    parts = req.split("->")
                    if len(parts) == 2:
                        op_a, op_b = parts
                        # Current operation is B
                        if context.get("operation") == op_b:
                            # Check if A was in previous operations
                            if op_a not in prev_ops:
                                violations.append(f"Operation {op_b} requires {op_a} to be called first")
        
        # Create violation if any issues were found
        if violations:
            return ProtocolViolation(
                protocol_id=self.protocol.protocol_id,
                component=context.get("component", "unknown"),
                endpoint=context.get("endpoint"),
                message_type=context.get("message_type"),
                severity=self.protocol.severity,
                message="; ".join(violations),
                details={
                    "violations": violations,
                    "context": context
                },
                context_id=context.get("context_id")
            )
        
        return None


class ResponseFormatValidator(ProtocolValidator):
    """Validator for response format protocols."""
    
    async def validate(
        self, 
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[ProtocolViolation]:
        """Validate response format."""
        # Extract rules
        rules = ResponseFormatRule(**self.protocol.rules)
        violations = []
        
        # Check status code
        status_code = context.get("status_code")
        if status_code and rules.status_codes and status_code not in rules.status_codes:
            violations.append(f"Status code {status_code} not allowed (allowed: {', '.join(map(str, rules.status_codes))})")
            
        # Check headers
        headers = context.get("headers", {})
        for header, required_value in rules.required_headers.items():
            if header not in headers:
                violations.append(f"Missing required header: {header}")
            elif required_value and headers[header] != required_value:
                violations.append(f"Header {header} has incorrect value: {headers[header]} (expected {required_value})")
                
        # Check required fields in response body
        for field in rules.required_fields:
            if field not in message:
                violations.append(f"Missing required field in response: {field}")
                
        # Check response time
        response_time = context.get("response_time_ms")
        if response_time and rules.max_response_time_ms and response_time > rules.max_response_time_ms:
            violations.append(f"Response time ({response_time}ms) exceeds maximum ({rules.max_response_time_ms}ms)")
        
        # Create violation if any issues were found
        if violations:
            return ProtocolViolation(
                protocol_id=self.protocol.protocol_id,
                component=context.get("component", "unknown"),
                endpoint=context.get("endpoint"),
                message_type=context.get("message_type"),
                severity=self.protocol.severity,
                message="; ".join(violations),
                details={
                    "violations": violations,
                    "response": message
                },
                context_id=context.get("context_id")
            )
        
        return None


class EventSequenceValidator(ProtocolValidator):
    """Validator for event sequencing protocols."""
    
    async def validate(
        self, 
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[ProtocolViolation]:
        """Validate event sequencing."""
        # Extract rules
        rules = EventSequenceRule(**self.protocol.rules)
        violations = []
        
        # Check sequence order
        if rules.sequence_order and "event_type" in context:
            event_type = context["event_type"]
            sequence_position = context.get("sequence_position")
            
            if sequence_position is not None:
                # Check if this event is in the expected position
                if 0 <= sequence_position < len(rules.sequence_order):
                    expected_event = rules.sequence_order[sequence_position]
                    if event_type != expected_event:
                        violations.append(f"Unexpected event in sequence: got {event_type}, expected {expected_event}")
                else:
                    violations.append(f"Event sequence position out of range: {sequence_position}")
        
        # Check time interval if provided
        if rules.max_interval_ms and "prev_event_time" in context:
            prev_time = context["prev_event_time"]
            current_time = context.get("current_time", datetime.now())
            
            # Convert to timestamp if datetime objects
            if isinstance(prev_time, datetime):
                prev_time = prev_time.timestamp() * 1000
            if isinstance(current_time, datetime):
                current_time = current_time.timestamp() * 1000
                
            interval = current_time - prev_time
            if interval > rules.max_interval_ms:
                violations.append(f"Event interval ({interval}ms) exceeds maximum ({rules.max_interval_ms}ms)")
                
        # Check correlation ID if required
        if rules.required_correlation_id and "correlation_id" not in message:
            violations.append("Missing required correlation ID")
            
        # Check parallel events
        if (rules.allowed_parallel_events is not None and 
            "parallel_events" in context and 
            "event_type" in context):
            
            event_type = context["event_type"]
            parallel_events = context["parallel_events"]
            
            for parallel_event in parallel_events:
                if (parallel_event != event_type and 
                    parallel_event not in rules.allowed_parallel_events):
                    violations.append(f"Event {parallel_event} not allowed in parallel with {event_type}")
        
        # Create violation if any issues were found
        if violations:
            return ProtocolViolation(
                protocol_id=self.protocol.protocol_id,
                component=context.get("component", "unknown"),
                endpoint=context.get("endpoint"),
                message_type=context.get("message_type"),
                severity=self.protocol.severity,
                message="; ".join(violations),
                details={
                    "violations": violations,
                    "event": message
                },
                context_id=context.get("context_id")
            )
        
        return None


class ProtocolEnforcer:
    """
    Protocol enforcer for Apollo that ensures communication standards.
    
    This class manages protocol definitions, validates messages against them,
    and tracks compliance with established protocols across Tekton components.
    """
    
    def __init__(
        self,
        protocols_dir: Optional[str] = None,
        load_defaults: bool = True,
        violation_history_limit: int = 1000,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the Protocol Enforcer.
        
        Args:
            protocols_dir: Directory with protocol definitions
            load_defaults: Whether to load default protocols
            violation_history_limit: Maximum violations to keep in history
            data_dir: Directory for storing protocol data
        """
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            # Use $TEKTON_DATA_DIR/apollo/protocol_data by default
            default_data_dir = os.path.join(
                os.environ.get('TEKTON_DATA_DIR', 
                              os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'apollo', 'protocol_data'
            )
            self.data_dir = default_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Set protocols directory
        self.protocols_dir = protocols_dir or os.path.join(self.data_dir, "definitions")
        os.makedirs(self.protocols_dir, exist_ok=True)
        
        # Initialize protocol definitions
        self.protocols: Dict[str, ProtocolDefinition] = {}
        
        # Initialize protocol validators
        self.validators: Dict[ProtocolType, type] = {
            ProtocolType.MESSAGE_FORMAT: MessageFormatValidator,
            ProtocolType.REQUEST_FLOW: RequestFlowValidator,
            ProtocolType.RESPONSE_FORMAT: ResponseFormatValidator,
            ProtocolType.EVENT_SEQUENCING: EventSequenceValidator
        }
        
        # Violation history
        self.violation_history: List[ProtocolViolation] = []
        self.violation_history_limit = violation_history_limit
        
        # Protocol statistics
        self.protocol_stats: Dict[str, ProtocolStats] = {}
        
        # Sequence state for event sequencing protocols
        self.sequence_state: Dict[str, Dict[str, Any]] = {}
        
        # For callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "on_violation": [],
            "on_validation": []
        }
        
        # Load protocols
        if load_defaults:
            self._load_default_protocols()
            
        self._load_protocols_from_dir()
    
    def _load_default_protocols(self):
        """Load default protocol definitions."""
        # Standard message format protocol
        standard_message = ProtocolDefinition(
            protocol_id="tekton.standard.message_format.v1",
            name="Tekton Standard Message Format",
            description="Standard format for messages between Tekton components",
            type=ProtocolType.MESSAGE_FORMAT,
            scope=ProtocolScope.GLOBAL,
            enforcement_mode=EnforcementMode.WARN,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            rules=MessageFormatRule(
                required_fields=["message_id", "timestamp", "source", "type"],
                forbidden_fields=["__private", "__internal"],
                field_types={
                    "message_id": "string",
                    "timestamp": "string",
                    "source": "string",
                    "type": "string",
                    "payload": "object"
                },
                max_size_bytes=1024 * 1024  # 1MB
            ).model_dump()
        )
        self.protocols[standard_message.protocol_id] = standard_message
        
        # Standard request flow protocol
        standard_request = ProtocolDefinition(
            protocol_id="tekton.standard.request_flow.v1",
            name="Tekton Standard Request Flow",
            description="Standard flow for API requests between Tekton components",
            type=ProtocolType.REQUEST_FLOW,
            scope=ProtocolScope.ENDPOINT,
            enforcement_mode=EnforcementMode.WARN,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            applicable_endpoints=["/api/*"],
            rules=RequestFlowRule(
                required_headers={
                    "Content-Type": "application/json",
                    "X-Tekton-Component": ""
                },
                allowed_methods=["GET", "POST", "PUT", "DELETE"],
                rate_limit=60,  # 60 requests per minute
                required_auth=False
            ).model_dump()
        )
        self.protocols[standard_request.protocol_id] = standard_request
        
        # Standard response format protocol
        standard_response = ProtocolDefinition(
            protocol_id="tekton.standard.response_format.v1",
            name="Tekton Standard Response Format",
            description="Standard format for API responses from Tekton components",
            type=ProtocolType.RESPONSE_FORMAT,
            scope=ProtocolScope.ENDPOINT,
            enforcement_mode=EnforcementMode.WARN,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            applicable_endpoints=["/api/*"],
            rules=ResponseFormatRule(
                status_codes=[200, 201, 400, 401, 403, 404, 500],
                required_headers={
                    "Content-Type": "application/json"
                },
                required_fields=["success", "data"],
                max_response_time_ms=5000  # 5 seconds
            ).model_dump()
        )
        self.protocols[standard_response.protocol_id] = standard_response
        
        # Standard event sequence protocol
        standard_event_sequence = ProtocolDefinition(
            protocol_id="tekton.standard.event_sequence.v1",
            name="Tekton Standard Event Sequence",
            description="Standard sequencing for events in Tekton workflows",
            type=ProtocolType.EVENT_SEQUENCING,
            scope=ProtocolScope.MESSAGE_TYPE,
            enforcement_mode=EnforcementMode.MONITOR,
            severity=ProtocolSeverity.INFO,
            applicable_components=["*"],
            applicable_message_types=["event.*"],
            rules=EventSequenceRule(
                required_correlation_id=True,
                max_interval_ms=60000  # 1 minute
            ).model_dump()
        )
        self.protocols[standard_event_sequence.protocol_id] = standard_event_sequence
        
        # Initialize stats for default protocols
        for protocol in self.protocols.values():
            self.protocol_stats[protocol.protocol_id] = ProtocolStats(
                protocol_id=protocol.protocol_id
            )
            
        logger.info(f"Loaded {len(self.protocols)} default protocols")
    
    def _load_protocols_from_dir(self):
        """Load protocol definitions from directory."""
        try:
            # List all JSON files in the protocols directory
            protocol_files = [f for f in os.listdir(self.protocols_dir) 
                             if f.endswith('.json')]
            
            protocols_loaded = 0
            for filename in protocol_files:
                try:
                    file_path = os.path.join(self.protocols_dir, filename)
                    with open(file_path, 'r') as f:
                        protocol_data = json.load(f)
                        
                    # Create protocol definition from data
                    protocol = ProtocolDefinition(**protocol_data)
                    
                    # Add to protocols dict
                    self.protocols[protocol.protocol_id] = protocol
                    
                    # Initialize stats
                    if protocol.protocol_id not in self.protocol_stats:
                        self.protocol_stats[protocol.protocol_id] = ProtocolStats(
                            protocol_id=protocol.protocol_id
                        )
                        
                    protocols_loaded += 1
                    
                except Exception as e:
                    logger.error(f"Error loading protocol from {filename}: {e}")
                    
            if protocols_loaded > 0:
                logger.info(f"Loaded {protocols_loaded} protocols from {self.protocols_dir}")
                
        except Exception as e:
            logger.error(f"Error loading protocols from directory: {e}")
    
    def add_protocol(self, protocol: ProtocolDefinition) -> bool:
        """
        Add a new protocol definition.
        
        Args:
            protocol: Protocol definition to add
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Validate protocol definition
            if not protocol.protocol_id:
                logger.error("Protocol ID is required")
                return False
                
            # Add to protocols dict
            self.protocols[protocol.protocol_id] = protocol
            
            # Initialize stats
            if protocol.protocol_id not in self.protocol_stats:
                self.protocol_stats[protocol.protocol_id] = ProtocolStats(
                    protocol_id=protocol.protocol_id
                )
                
            # Save to file
            self._save_protocol(protocol)
            
            logger.info(f"Added protocol {protocol.protocol_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding protocol: {e}")
            return False
    
    def update_protocol(self, protocol: ProtocolDefinition) -> bool:
        """
        Update an existing protocol definition.
        
        Args:
            protocol: Updated protocol definition
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Check if protocol exists
            if protocol.protocol_id not in self.protocols:
                logger.error(f"Protocol {protocol.protocol_id} not found")
                return False
                
            # Update protocol
            protocol.updated_at = datetime.now()
            self.protocols[protocol.protocol_id] = protocol
            
            # Save to file
            self._save_protocol(protocol)
            
            logger.info(f"Updated protocol {protocol.protocol_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating protocol: {e}")
            return False
    
    def _save_protocol(self, protocol: ProtocolDefinition):
        """
        Save protocol definition to file.
        
        Args:
            protocol: Protocol definition to save
        """
        try:
            # Create filename from protocol ID
            safe_id = protocol.protocol_id.replace(".", "_").replace(":", "_")
            filename = os.path.join(self.protocols_dir, f"{safe_id}.json")
            
            # Save to file
            with open(filename, "w") as f:
                json.dump(protocol.model_dump(), f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving protocol to file: {e}")
    
    def remove_protocol(self, protocol_id: str) -> bool:
        """
        Remove a protocol definition.
        
        Args:
            protocol_id: ID of protocol to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            # Check if protocol exists
            if protocol_id not in self.protocols:
                logger.error(f"Protocol {protocol_id} not found")
                return False
                
            # Remove from protocols dict
            del self.protocols[protocol_id]
            
            # Remove stats
            if protocol_id in self.protocol_stats:
                del self.protocol_stats[protocol_id]
                
            # Remove file if exists
            safe_id = protocol_id.replace(".", "_").replace(":", "_")
            filename = os.path.join(self.protocols_dir, f"{safe_id}.json")
            if os.path.exists(filename):
                os.remove(filename)
                
            logger.info(f"Removed protocol {protocol_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing protocol: {e}")
            return False
    
    def get_protocol(self, protocol_id: str) -> Optional[ProtocolDefinition]:
        """
        Get a protocol definition by ID.
        
        Args:
            protocol_id: Protocol identifier
            
        Returns:
            Protocol definition or None if not found
        """
        return self.protocols.get(protocol_id)
    
    def get_all_protocols(self) -> List[ProtocolDefinition]:
        """
        Get all protocol definitions.
        
        Returns:
            List of all protocol definitions
        """
        return list(self.protocols.values())
    
    def get_applicable_protocols(
        self,
        component: str,
        endpoint: Optional[str] = None,
        message_type: Optional[str] = None
    ) -> List[ProtocolDefinition]:
        """
        Get protocols applicable to a component, endpoint, or message type.
        
        Args:
            component: Component name
            endpoint: Optional endpoint path
            message_type: Optional message type
            
        Returns:
            List of applicable protocol definitions
        """
        applicable = []
        
        for protocol in self.protocols.values():
            # Skip disabled protocols
            if not protocol.enabled:
                continue
                
            # Check component applicability
            component_match = (
                "*" in protocol.applicable_components or
                component in protocol.applicable_components
            )
            
            if not component_match:
                continue
                
            # For global scope, only component match is needed
            if protocol.scope == ProtocolScope.GLOBAL:
                applicable.append(protocol)
                continue
                
            # For component scope, only component match is needed
            if protocol.scope == ProtocolScope.COMPONENT:
                applicable.append(protocol)
                continue
                
            # For endpoint scope, check endpoint
            if protocol.scope == ProtocolScope.ENDPOINT and endpoint:
                endpoint_match = False
                
                for pattern in protocol.applicable_endpoints:
                    # Convert glob pattern to regex
                    regex_pattern = pattern.replace("*", ".*")
                    if re.match(regex_pattern, endpoint):
                        endpoint_match = True
                        break
                        
                if endpoint_match:
                    applicable.append(protocol)
                    continue
                    
            # For message type scope, check message type
            if protocol.scope == ProtocolScope.MESSAGE_TYPE and message_type:
                message_match = False
                
                for pattern in protocol.applicable_message_types:
                    # Convert glob pattern to regex
                    regex_pattern = pattern.replace("*", ".*")
                    if re.match(regex_pattern, message_type):
                        message_match = True
                        break
                        
                if message_match:
                    applicable.append(protocol)
                    continue
        
        return applicable
    
    async def validate_message(
        self,
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ProtocolViolation]:
        """
        Validate a message against applicable protocols.
        
        Args:
            message: Message to validate
            context: Additional context for validation
            
        Returns:
            List of protocol violations
        """
        # Extract context information
        component = context.get("component", "unknown")
        endpoint = context.get("endpoint")
        message_type = context.get("message_type")
        
        # Get applicable protocols
        applicable_protocols = self.get_applicable_protocols(
            component=component,
            endpoint=endpoint,
            message_type=message_type
        )
        
        violations = []
        
        # Apply each protocol
        for protocol in applicable_protocols:
            try:
                # Get appropriate validator
                validator_class = self.validators.get(protocol.type)
                if not validator_class:
                    logger.warning(f"No validator found for protocol type {protocol.type}")
                    continue
                    
                # Create validator
                validator = validator_class(protocol)
                
                # Validate message
                violation = await validator.validate(message, context)
                
                # Update stats
                if protocol.protocol_id in self.protocol_stats:
                    stats = self.protocol_stats[protocol.protocol_id]
                    stats.total_evaluations += 1
                    stats.last_evaluation = datetime.now()
                    
                    # Trigger validation callback
                    await self._trigger_callbacks(
                        "on_validation", 
                        protocol, 
                        message, 
                        context,
                        violation
                    )
                    
                # If violation found
                if violation:
                    # Add to violations list
                    violations.append(violation)
                    
                    # Add to history
                    self.violation_history.append(violation)
                    
                    # Limit history size
                    if len(self.violation_history) > self.violation_history_limit:
                        self.violation_history = self.violation_history[-self.violation_history_limit:]
                    
                    # Update stats
                    if protocol.protocol_id in self.protocol_stats:
                        stats = self.protocol_stats[protocol.protocol_id]
                        stats.total_violations += 1
                        stats.last_violation = datetime.now()
                        
                        # Update severity counts
                        stats.violations_by_severity[violation.severity] += 1
                        
                        # Update component counts
                        if component not in stats.violations_by_component:
                            stats.violations_by_component[component] = 0
                        stats.violations_by_component[component] += 1
                    
                    # Trigger violation callback
                    await self._trigger_callbacks("on_violation", violation)
                    
                    # Log violation
                    log_method = logger.info
                    if violation.severity == ProtocolSeverity.WARNING:
                        log_method = logger.warning
                    elif violation.severity == ProtocolSeverity.ERROR:
                        log_method = logger.error
                    elif violation.severity == ProtocolSeverity.CRITICAL:
                        log_method = logger.critical
                        
                    log_method(f"Protocol violation: {violation.message} (Protocol: {protocol.name}, Severity: {violation.severity})")
                
            except Exception as e:
                logger.error(f"Error validating message against protocol {protocol.protocol_id}: {e}")
        
        return violations
    
    async def apply_corrections(
        self,
        message: Dict[str, Any],
        violations: List[ProtocolViolation]
    ) -> Dict[str, Any]:
        """
        Apply automatic corrections to a message based on violations.
        
        Only called for protocols with ADAPT enforcement mode.
        
        Args:
            message: Original message
            violations: Protocol violations
            
        Returns:
            Corrected message
        """
        # Make a copy of the message to modify
        corrected = message.copy()
        
        for violation in violations:
            # Get protocol
            protocol = self.get_protocol(violation.protocol_id)
            if not protocol:
                continue
                
            # Skip if not in ADAPT mode
            if protocol.enforcement_mode != EnforcementMode.ADAPT:
                continue
                
            # Apply corrections based on protocol type
            if protocol.type == ProtocolType.MESSAGE_FORMAT:
                # Add missing required fields with default values
                rules = MessageFormatRule(**protocol.rules)
                
                for field in rules.required_fields:
                    if field not in corrected:
                        # Add default value based on field type
                        field_type = rules.field_types.get(field)
                        if field_type == "string":
                            corrected[field] = ""
                        elif field_type == "array":
                            corrected[field] = []
                        elif field_type == "object":
                            corrected[field] = {}
                        elif field_type == "number":
                            corrected[field] = 0
                        elif field_type == "boolean":
                            corrected[field] = False
                        else:
                            corrected[field] = None
                
                # Remove forbidden fields
                for field in rules.forbidden_fields:
                    if field in corrected:
                        del corrected[field]
            
            # Update correction action taken
            violation.corrective_action_taken = "Applied automatic corrections"
        
        return corrected
    
    async def handle_message(
        self,
        message: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a message and handle it according to protocol enforcement.
        
        This method validates the message, applies corrections if needed,
        and blocks messages that violate ENFORCE protocols.
        
        Args:
            message: Message to validate and handle
            context: Additional context for validation
            
        Returns:
            Handled message (possibly corrected) or empty dict if blocked
        """
        # Validate the message
        violations = await self.validate_message(message, context)
        
        # If no violations, return original message
        if not violations:
            return message
            
        # Check for ENFORCE violations
        enforce_violations = []
        adapt_violations = []
        
        for violation in violations:
            # Get protocol
            protocol = self.get_protocol(violation.protocol_id)
            if not protocol:
                continue
                
            # Check enforcement mode
            if protocol.enforcement_mode == EnforcementMode.ENFORCE:
                enforce_violations.append(violation)
            elif protocol.enforcement_mode == EnforcementMode.ADAPT:
                adapt_violations.append(violation)
        
        # If ENFORCE violations, block the message
        if enforce_violations:
            logger.warning(f"Blocking message due to {len(enforce_violations)} ENFORCE protocol violations")
            return {}
            
        # If ADAPT violations, try to correct the message
        if adapt_violations:
            return await self.apply_corrections(message, adapt_violations)
            
        # Otherwise, just return the original message
        return message
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback for a specific event type.
        
        Args:
            event_type: Type of event to register for
            callback: Callback function
        """
        if event_type not in self.callbacks:
            logger.warning(f"Unknown event type: {event_type}")
            return
            
        self.callbacks[event_type].append(callback)
        logger.debug(f"Registered callback for {event_type}")
    
    async def _trigger_callbacks(self, event_type: str, *args, **kwargs):
        """
        Trigger registered callbacks for an event.
        
        Args:
            event_type: Type of event
            *args: Arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        if event_type not in self.callbacks:
            return
            
        for callback in self.callbacks[event_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {event_type} callback: {e}")
    
    def get_violations(
        self,
        component: Optional[str] = None,
        protocol_id: Optional[str] = None,
        severity: Optional[ProtocolSeverity] = None,
        limit: int = 100
    ) -> List[ProtocolViolation]:
        """
        Get protocol violations filtered by criteria.
        
        Args:
            component: Optional component filter
            protocol_id: Optional protocol ID filter
            severity: Optional severity filter
            limit: Maximum number of violations to return
            
        Returns:
            List of protocol violations matching criteria
        """
        # Filter violations
        filtered = self.violation_history
        
        if component:
            filtered = [v for v in filtered if v.component == component]
            
        if protocol_id:
            filtered = [v for v in filtered if v.protocol_id == protocol_id]
            
        if severity:
            filtered = [v for v in filtered if v.severity == severity]
            
        # Sort by timestamp (newest first)
        filtered.sort(key=lambda v: v.timestamp, reverse=True)
        
        # Limit results
        return filtered[:limit]
    
    def get_protocol_stats(self, protocol_id: str) -> Optional[ProtocolStats]:
        """
        Get statistics for a specific protocol.
        
        Args:
            protocol_id: Protocol identifier
            
        Returns:
            Protocol statistics or None if not found
        """
        return self.protocol_stats.get(protocol_id)
    
    def get_all_stats(self) -> Dict[str, ProtocolStats]:
        """
        Get statistics for all protocols.
        
        Returns:
            Dictionary mapping protocol IDs to their statistics
        """
        return self.protocol_stats
    
    def get_violation_summary(self) -> Dict[str, int]:
        """
        Get summary of violations by severity.
        
        Returns:
            Dictionary mapping severity to count
        """
        summary = {severity.value: 0 for severity in ProtocolSeverity}
        
        for violation in self.violation_history:
            summary[violation.severity.value] += 1
            
        return summary
    
    def clear_violation_history(self):
        """Clear the violation history."""
        self.violation_history = []
        logger.info("Cleared violation history")
    
    def reset_stats(self):
        """Reset all protocol statistics."""
        for stats in self.protocol_stats.values():
            stats.total_evaluations = 0
            stats.total_violations = 0
            stats.violations_by_severity = {severity: 0 for severity in ProtocolSeverity}
            stats.violations_by_component = {}
            stats.last_violation = None
            stats.last_evaluation = None
            
        logger.info("Reset protocol statistics")
    
    def save_violation_history(self):
        """Save violation history to disk."""
        try:
            # Create filename
            filename = os.path.join(self.data_dir, f"violations_{int(time.time())}.json")
            
            # Convert to dict
            violations_data = [v.model_dump() for v in self.violation_history]
            
            # Save to file
            with open(filename, "w") as f:
                json.dump(violations_data, f, indent=2, default=str)
                
            logger.info(f"Saved violation history to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving violation history: {e}")
    
    def load_violation_history(self, filename: str):
        """
        Load violation history from disk.
        
        Args:
            filename: Path to violation history file
        """
        try:
            # Load from file
            with open(filename, "r") as f:
                violations_data = json.load(f)
                
            # Convert to objects
            violations = [ProtocolViolation(**v) for v in violations_data]
            
            # Set as history
            self.violation_history = violations
            
            logger.info(f"Loaded {len(violations)} violations from {filename}")
            
        except Exception as e:
            logger.error(f"Error loading violation history: {e}")
    
    def save_stats(self):
        """Save protocol statistics to disk."""
        try:
            # Create filename
            filename = os.path.join(self.data_dir, "protocol_stats.json")
            
            # Convert to dict
            stats_data = {
                protocol_id: stats.model_dump()
                for protocol_id, stats in self.protocol_stats.items()
            }
            
            # Save to file
            with open(filename, "w") as f:
                json.dump(stats_data, f, indent=2, default=str)
                
            logger.info(f"Saved protocol statistics to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving protocol statistics: {e}")
    
    def load_stats(self):
        """Load protocol statistics from disk."""
        try:
            # Check if file exists
            filename = os.path.join(self.data_dir, "protocol_stats.json")
            if not os.path.exists(filename):
                logger.info("No protocol statistics file found")
                return
                
            # Load from file
            with open(filename, "r") as f:
                stats_data = json.load(f)
                
            # Convert to objects
            stats = {
                protocol_id: ProtocolStats(**data)
                for protocol_id, data in stats_data.items()
            }
            
            # Set as stats
            self.protocol_stats = stats
            
            logger.info(f"Loaded statistics for {len(stats)} protocols")
            
        except Exception as e:
            logger.error(f"Error loading protocol statistics: {e}")