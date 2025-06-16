"""
Unit tests for the Protocol Enforcer module.
"""

import os
import json
import tempfile
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta

import pytest

from apollo.core.protocol_enforcer import (
    ProtocolEnforcer,
    MessageFormatValidator,
    RequestFlowValidator,
    ResponseFormatValidator,
    EventSequenceValidator
)
from apollo.models.protocol import (
    ProtocolDefinition,
    ProtocolViolation,
    ProtocolStats,
    ProtocolType,
    ProtocolSeverity,
    ProtocolScope,
    EnforcementMode,
    MessageFormatRule,
    RequestFlowRule
)


class TestProtocolEnforcer(unittest.TestCase):
    """Test cases for the ProtocolEnforcer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create a protocol enforcer without loading defaults
        self.enforcer = ProtocolEnforcer(
            protocols_dir=os.path.join(self.test_dir, "protocols"),
            load_defaults=False,
            data_dir=self.test_dir
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(self.test_dir)
    
    async def test_add_protocol(self):
        """Test adding a protocol definition."""
        # Create a protocol definition
        protocol = ProtocolDefinition(
            protocol_id="test.protocol.1",
            name="Test Protocol",
            description="A test protocol",
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
                }
            ).dict()
        )
        
        # Add protocol
        success = self.enforcer.add_protocol(protocol)
        
        # Should succeed
        assert success is True
        
        # Protocol should be in the enforcer
        assert "test.protocol.1" in self.enforcer.protocols
        
        # Protocol stats should be initialized
        assert "test.protocol.1" in self.enforcer.protocol_stats
        
        # Check protocol directory
        protocol_files = os.listdir(os.path.join(self.test_dir, "protocols"))
        assert len(protocol_files) == 1
    
    async def test_update_protocol(self):
        """Test updating a protocol definition."""
        # Create and add a protocol
        protocol = ProtocolDefinition(
            protocol_id="test.protocol.update",
            name="Test Protocol",
            description="A test protocol",
            type=ProtocolType.MESSAGE_FORMAT,
            scope=ProtocolScope.GLOBAL,
            enforcement_mode=EnforcementMode.WARN,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            rules=MessageFormatRule(
                required_fields=["message_id", "timestamp", "source", "type"]
            ).dict()
        )
        
        self.enforcer.add_protocol(protocol)
        
        # Update protocol
        updated_protocol = ProtocolDefinition(
            protocol_id="test.protocol.update",
            name="Updated Protocol",
            description="An updated test protocol",
            type=ProtocolType.MESSAGE_FORMAT,
            scope=ProtocolScope.GLOBAL,
            enforcement_mode=EnforcementMode.ENFORCE,  # Changed
            severity=ProtocolSeverity.ERROR,  # Changed
            applicable_components=["*"],
            rules=MessageFormatRule(
                required_fields=["message_id", "timestamp", "source", "type", "payload"]  # Added field
            ).dict()
        )
        
        success = self.enforcer.update_protocol(updated_protocol)
        
        # Should succeed
        assert success is True
        
        # Protocol should be updated
        assert self.enforcer.protocols["test.protocol.update"].name == "Updated Protocol"
        assert self.enforcer.protocols["test.protocol.update"].enforcement_mode == EnforcementMode.ENFORCE
        assert self.enforcer.protocols["test.protocol.update"].severity == ProtocolSeverity.ERROR
        
        # Rules should be updated
        rule_dict = self.enforcer.protocols["test.protocol.update"].rules
        rule = MessageFormatRule(**rule_dict)
        assert "payload" in rule.required_fields
    
    async def test_remove_protocol(self):
        """Test removing a protocol definition."""
        # Create and add a protocol
        protocol = ProtocolDefinition(
            protocol_id="test.protocol.remove",
            name="Test Protocol",
            description="A test protocol",
            type=ProtocolType.MESSAGE_FORMAT,
            scope=ProtocolScope.GLOBAL,
            enforcement_mode=EnforcementMode.WARN,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            rules=MessageFormatRule(
                required_fields=["message_id", "timestamp", "source", "type"]
            ).dict()
        )
        
        self.enforcer.add_protocol(protocol)
        
        # Verify protocol was added
        assert "test.protocol.remove" in self.enforcer.protocols
        
        # Remove protocol
        success = self.enforcer.remove_protocol("test.protocol.remove")
        
        # Should succeed
        assert success is True
        
        # Protocol should be removed
        assert "test.protocol.remove" not in self.enforcer.protocols
        assert "test.protocol.remove" not in self.enforcer.protocol_stats
    
    async def test_get_applicable_protocols(self):
        """Test getting applicable protocols."""
        # Add several protocols with different scopes
        protocols = [
            # Global protocol
            ProtocolDefinition(
                protocol_id="test.protocol.global",
                name="Global Protocol",
                type=ProtocolType.MESSAGE_FORMAT,
                scope=ProtocolScope.GLOBAL,
                enforcement_mode=EnforcementMode.WARN,
                severity=ProtocolSeverity.WARNING,
                applicable_components=["*"],
                rules={}
            ),
            # Component-specific protocol
            ProtocolDefinition(
                protocol_id="test.protocol.component",
                name="Component Protocol",
                type=ProtocolType.MESSAGE_FORMAT,
                scope=ProtocolScope.COMPONENT,
                enforcement_mode=EnforcementMode.WARN,
                severity=ProtocolSeverity.WARNING,
                applicable_components=["test-component"],
                rules={}
            ),
            # Endpoint-specific protocol
            ProtocolDefinition(
                protocol_id="test.protocol.endpoint",
                name="Endpoint Protocol",
                type=ProtocolType.REQUEST_FLOW,
                scope=ProtocolScope.ENDPOINT,
                enforcement_mode=EnforcementMode.WARN,
                severity=ProtocolSeverity.WARNING,
                applicable_components=["*"],
                applicable_endpoints=["/api/test", "/api/other*"],
                rules={}
            ),
            # Message type-specific protocol
            ProtocolDefinition(
                protocol_id="test.protocol.message",
                name="Message Protocol",
                type=ProtocolType.MESSAGE_FORMAT,
                scope=ProtocolScope.MESSAGE_TYPE,
                enforcement_mode=EnforcementMode.WARN,
                severity=ProtocolSeverity.WARNING,
                applicable_components=["*"],
                applicable_message_types=["test.message", "other.*"],
                rules={}
            ),
            # Disabled protocol
            ProtocolDefinition(
                protocol_id="test.protocol.disabled",
                name="Disabled Protocol",
                type=ProtocolType.MESSAGE_FORMAT,
                scope=ProtocolScope.GLOBAL,
                enforcement_mode=EnforcementMode.WARN,
                severity=ProtocolSeverity.WARNING,
                applicable_components=["*"],
                rules={},
                enabled=False
            )
        ]
        
        # Add protocols
        for protocol in protocols:
            self.enforcer.add_protocol(protocol)
        
        # Test getting applicable protocols
        
        # Test 1: Global and component protocols
        applicable = self.enforcer.get_applicable_protocols(
            component="test-component"
        )
        
        assert len(applicable) == 2
        assert "test.protocol.global" in [p.protocol_id for p in applicable]
        assert "test.protocol.component" in [p.protocol_id for p in applicable]
        
        # Test 2: Global and endpoint protocols
        applicable = self.enforcer.get_applicable_protocols(
            component="other-component",
            endpoint="/api/test"
        )
        
        assert len(applicable) == 2
        assert "test.protocol.global" in [p.protocol_id for p in applicable]
        assert "test.protocol.endpoint" in [p.protocol_id for p in applicable]
        
        # Test 3: Global and message type protocols
        applicable = self.enforcer.get_applicable_protocols(
            component="other-component",
            message_type="other.message"
        )
        
        assert len(applicable) == 2
        assert "test.protocol.global" in [p.protocol_id for p in applicable]
        assert "test.protocol.message" in [p.protocol_id for p in applicable]
        
        # Test 4: All applicable protocols
        applicable = self.enforcer.get_applicable_protocols(
            component="test-component",
            endpoint="/api/test",
            message_type="test.message"
        )
        
        assert len(applicable) == 4
        protocol_ids = [p.protocol_id for p in applicable]
        assert "test.protocol.global" in protocol_ids
        assert "test.protocol.component" in protocol_ids
        assert "test.protocol.endpoint" in protocol_ids
        assert "test.protocol.message" in protocol_ids
        
        # Disabled protocol should not be included
        assert "test.protocol.disabled" not in protocol_ids
    
    async def test_message_format_validator(self):
        """Test MessageFormatValidator."""
        # Create protocol
        protocol = ProtocolDefinition(
            protocol_id="test.validator.format",
            name="Format Validator Protocol",
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
                }
            ).dict()
        )
        
        # Create validator
        validator = MessageFormatValidator(protocol)
        
        # Test valid message
        valid_message = {
            "message_id": "test-message",
            "timestamp": "2023-01-01T00:00:00Z",
            "source": "test-component",
            "type": "test.message",
            "payload": {"test": "data"}
        }
        
        context = {
            "component": "test-component"
        }
        
        # Validate
        violation = await validator.validate(valid_message, context)
        
        # Should be valid
        assert violation is None
        
        # Test invalid message (missing required field)
        invalid_message = {
            "message_id": "test-message",
            # Missing timestamp
            "source": "test-component",
            "type": "test.message"
        }
        
        # Validate
        violation = await validator.validate(invalid_message, context)
        
        # Should be invalid
        assert violation is not None
        assert violation.protocol_id == "test.validator.format"
        assert violation.component == "test-component"
        assert "timestamp" in violation.message
        
        # Test invalid message (forbidden field)
        forbidden_message = {
            "message_id": "test-message",
            "timestamp": "2023-01-01T00:00:00Z",
            "source": "test-component",
            "type": "test.message",
            "__private": "secret"  # Forbidden
        }
        
        # Validate
        violation = await validator.validate(forbidden_message, context)
        
        # Should be invalid
        assert violation is not None
        assert "__private" in violation.message
        
        # Test invalid message (wrong type)
        wrong_type_message = {
            "message_id": "test-message",
            "timestamp": "2023-01-01T00:00:00Z",
            "source": "test-component",
            "type": "test.message",
            "payload": "not an object"  # Should be object
        }
        
        # Validate
        violation = await validator.validate(wrong_type_message, context)
        
        # Should be invalid
        assert violation is not None
        assert "payload" in violation.message
        assert "object" in violation.message
    
    async def test_request_flow_validator(self):
        """Test RequestFlowValidator."""
        # Create protocol
        protocol = ProtocolDefinition(
            protocol_id="test.validator.flow",
            name="Flow Validator Protocol",
            type=ProtocolType.REQUEST_FLOW,
            scope=ProtocolScope.ENDPOINT,
            enforcement_mode=EnforcementMode.WARN,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            applicable_endpoints=["/api/test"],
            rules=RequestFlowRule(
                required_headers={
                    "Content-Type": "application/json",
                    "X-Tekton-Component": ""
                },
                allowed_methods=["GET", "POST"],
                rate_limit=60,
                required_auth=True,
                sequence_requirements=["init->query"]
            ).dict()
        )
        
        # Create validator
        validator = RequestFlowValidator(protocol)
        
        # Test valid request
        valid_request = {
            "method": "GET",
            "endpoint": "/api/test"
        }
        
        context = {
            "component": "test-component",
            "endpoint": "/api/test",
            "method": "GET",
            "headers": {
                "Content-Type": "application/json",
                "X-Tekton-Component": "test-component"
            },
            "authenticated": True,
            "request_rate": 10,
            "operation": "query",
            "previous_operations": ["init"]
        }
        
        # Validate
        violation = await validator.validate(valid_request, context)
        
        # Should be valid
        assert violation is None
        
        # Test invalid request (missing header)
        invalid_context = context.copy()
        invalid_context["headers"] = {
            "Content-Type": "application/json"
            # Missing X-Tekton-Component
        }
        
        # Validate
        violation = await validator.validate(valid_request, invalid_context)
        
        # Should be invalid
        assert violation is not None
        assert "X-Tekton-Component" in violation.message
        
        # Test invalid request (wrong method)
        invalid_context = context.copy()
        invalid_context["method"] = "DELETE"  # Not allowed
        
        # Validate
        violation = await validator.validate(valid_request, invalid_context)
        
        # Should be invalid
        assert violation is not None
        assert "DELETE" in violation.message
        
        # Test invalid request (not authenticated)
        invalid_context = context.copy()
        invalid_context["authenticated"] = False
        
        # Validate
        violation = await validator.validate(valid_request, invalid_context)
        
        # Should be invalid
        assert violation is not None
        assert "Authentication" in violation.message
        
        # Test invalid request (rate limit exceeded)
        invalid_context = context.copy()
        invalid_context["request_rate"] = 100  # Exceeds limit
        
        # Validate
        violation = await validator.validate(valid_request, invalid_context)
        
        # Should be invalid
        assert violation is not None
        assert "Rate limit" in violation.message
        
        # Test invalid request (sequence violation)
        invalid_context = context.copy()
        invalid_context["operation"] = "query"
        invalid_context["previous_operations"] = []  # Missing init
        
        # Validate
        violation = await validator.validate(valid_request, invalid_context)
        
        # Should be invalid
        assert violation is not None
        assert "Operation" in violation.message
        assert "init" in violation.message
    
    async def test_validate_message(self):
        """Test validating a message against applicable protocols."""
        # Add protocols
        format_protocol = ProtocolDefinition(
            protocol_id="test.validate.format",
            name="Format Protocol",
            type=ProtocolType.MESSAGE_FORMAT,
            scope=ProtocolScope.GLOBAL,
            enforcement_mode=EnforcementMode.WARN,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            rules=MessageFormatRule(
                required_fields=["message_id", "source", "type"]
            ).dict()
        )
        
        flow_protocol = ProtocolDefinition(
            protocol_id="test.validate.flow",
            name="Flow Protocol",
            type=ProtocolType.REQUEST_FLOW,
            scope=ProtocolScope.ENDPOINT,
            enforcement_mode=EnforcementMode.WARN,
            severity=ProtocolSeverity.ERROR,
            applicable_components=["*"],
            applicable_endpoints=["/api/test"],
            rules=RequestFlowRule(
                required_headers={
                    "Content-Type": "application/json"
                },
                allowed_methods=["GET"]
            ).dict()
        )
        
        self.enforcer.add_protocol(format_protocol)
        self.enforcer.add_protocol(flow_protocol)
        
        # Test valid message
        valid_message = {
            "message_id": "test-message",
            "source": "test-component",
            "type": "test.message"
        }
        
        context = {
            "component": "test-component",
            "endpoint": "/api/test",
            "method": "GET",
            "message_type": "test.message",
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
        # Validate
        violations = await self.enforcer.validate_message(valid_message, context)
        
        # Should be valid
        assert len(violations) == 0
        
        # Test invalid message (missing required field)
        invalid_message = {
            # Missing message_id
            "source": "test-component",
            "type": "test.message"
        }
        
        # Validate
        violations = await self.enforcer.validate_message(invalid_message, context)
        
        # Should have one violation
        assert len(violations) == 1
        assert violations[0].protocol_id == "test.validate.format"
        assert "message_id" in violations[0].message
        
        # Test invalid context (wrong method)
        invalid_context = context.copy()
        invalid_context["method"] = "POST"  # Not allowed
        
        # Validate
        violations = await self.enforcer.validate_message(valid_message, invalid_context)
        
        # Should have one violation
        assert len(violations) == 1
        assert violations[0].protocol_id == "test.validate.flow"
        assert "POST" in violations[0].message
        
        # Test multiple violations
        invalid_message = {
            # Missing message_id
            "source": "test-component",
            "type": "test.message"
        }
        
        invalid_context = context.copy()
        invalid_context["method"] = "POST"  # Not allowed
        
        # Validate
        violations = await self.enforcer.validate_message(invalid_message, invalid_context)
        
        # Should have two violations
        assert len(violations) == 2
        
        # Check violation statistics
        format_stats = self.enforcer.protocol_stats["test.validate.format"]
        flow_stats = self.enforcer.protocol_stats["test.validate.flow"]
        
        assert format_stats.total_evaluations > 0
        assert format_stats.total_violations > 0
        assert flow_stats.total_evaluations > 0
        assert flow_stats.total_violations > 0
        
        # Check violation history
        assert len(self.enforcer.violation_history) > 0
    
    async def test_handle_message(self):
        """Test handling a message according to protocol enforcement."""
        # Add protocols with different enforcement modes
        monitor_protocol = ProtocolDefinition(
            protocol_id="test.handle.monitor",
            name="Monitor Protocol",
            type=ProtocolType.MESSAGE_FORMAT,
            scope=ProtocolScope.GLOBAL,
            enforcement_mode=EnforcementMode.MONITOR,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            rules=MessageFormatRule(
                required_fields=["field1"]
            ).dict()
        )
        
        warn_protocol = ProtocolDefinition(
            protocol_id="test.handle.warn",
            name="Warn Protocol",
            type=ProtocolType.MESSAGE_FORMAT,
            scope=ProtocolScope.GLOBAL,
            enforcement_mode=EnforcementMode.WARN,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            rules=MessageFormatRule(
                required_fields=["field2"]
            ).dict()
        )
        
        enforce_protocol = ProtocolDefinition(
            protocol_id="test.handle.enforce",
            name="Enforce Protocol",
            type=ProtocolType.MESSAGE_FORMAT,
            scope=ProtocolScope.GLOBAL,
            enforcement_mode=EnforcementMode.ENFORCE,
            severity=ProtocolSeverity.ERROR,
            applicable_components=["*"],
            rules=MessageFormatRule(
                required_fields=["field3"]
            ).dict()
        )
        
        adapt_protocol = ProtocolDefinition(
            protocol_id="test.handle.adapt",
            name="Adapt Protocol",
            type=ProtocolType.MESSAGE_FORMAT,
            scope=ProtocolScope.GLOBAL,
            enforcement_mode=EnforcementMode.ADAPT,
            severity=ProtocolSeverity.WARNING,
            applicable_components=["*"],
            rules=MessageFormatRule(
                required_fields=["field4"],
                field_types={"field4": "string"}
            ).dict()
        )
        
        self.enforcer.add_protocol(monitor_protocol)
        self.enforcer.add_protocol(warn_protocol)
        self.enforcer.add_protocol(enforce_protocol)
        self.enforcer.add_protocol(adapt_protocol)
        
        # Test 1: Valid message
        valid_message = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
            "field4": "value4"
        }
        
        context = {
            "component": "test-component"
        }
        
        # Handle
        result = await self.enforcer.handle_message(valid_message, context)
        
        # Should return original message unchanged
        assert result == valid_message
        
        # Test 2: Message with MONITOR violation (should pass through)
        monitor_message = {
            # Missing field1 (MONITOR)
            "field2": "value2",
            "field3": "value3",
            "field4": "value4"
        }
        
        # Handle
        result = await self.enforcer.handle_message(monitor_message, context)
        
        # Should return original message unchanged
        assert result == monitor_message
        
        # Test 3: Message with WARN violation (should pass through)
        warn_message = {
            "field1": "value1",
            # Missing field2 (WARN)
            "field3": "value3",
            "field4": "value4"
        }
        
        # Handle
        result = await self.enforcer.handle_message(warn_message, context)
        
        # Should return original message unchanged
        assert result == warn_message
        
        # Test 4: Message with ENFORCE violation (should block)
        enforce_message = {
            "field1": "value1",
            "field2": "value2",
            # Missing field3 (ENFORCE)
            "field4": "value4"
        }
        
        # Handle
        result = await self.enforcer.handle_message(enforce_message, context)
        
        # Should return empty object (blocked)
        assert result == {}
        
        # Test 5: Message with ADAPT violation (should correct)
        adapt_message = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
            # Missing field4 (ADAPT)
        }
        
        # Handle
        result = await self.enforcer.handle_message(adapt_message, context)
        
        # Should add missing field
        assert result != adapt_message
        assert "field4" in result
        assert result["field1"] == "value1"
        assert result["field2"] == "value2"
        assert result["field3"] == "value3"


# Run tests using pytest
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])