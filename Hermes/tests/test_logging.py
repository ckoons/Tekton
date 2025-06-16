"""
Tests for the Centralized Logging System implementation.
"""

import unittest
import os
import json
import time
import tempfile
import shutil
from typing import Dict, Any, List

from hermes.core.logging import (
    LogLevel, LogEntry, LogManager, Logger,
    init_logging, get_logger
)


class TestLogLevel(unittest.TestCase):
    """Test cases for the LogLevel enum."""
    
    def test_from_string(self):
        """Test converting string to LogLevel."""
        self.assertEqual(LogLevel.from_string("FATAL"), LogLevel.FATAL)
        self.assertEqual(LogLevel.from_string("ERROR"), LogLevel.ERROR)
        self.assertEqual(LogLevel.from_string("WARN"), LogLevel.WARN)
        self.assertEqual(LogLevel.from_string("INFO"), LogLevel.INFO)
        self.assertEqual(LogLevel.from_string("NORMAL"), LogLevel.NORMAL)
        self.assertEqual(LogLevel.from_string("DEBUG"), LogLevel.DEBUG)
        self.assertEqual(LogLevel.from_string("TRACE"), LogLevel.TRACE)
        
        # Case insensitivity
        self.assertEqual(LogLevel.from_string("fatal"), LogLevel.FATAL)
        self.assertEqual(LogLevel.from_string("Fatal"), LogLevel.FATAL)
        
        # Default to INFO for unknown level
        self.assertEqual(LogLevel.from_string("UNKNOWN"), LogLevel.INFO)
    
    def test_to_python_level(self):
        """Test converting LogLevel to Python logging level."""
        import logging
        
        self.assertEqual(LogLevel.to_python_level(LogLevel.FATAL), logging.CRITICAL)
        self.assertEqual(LogLevel.to_python_level(LogLevel.ERROR), logging.ERROR)
        self.assertEqual(LogLevel.to_python_level(LogLevel.WARN), logging.WARNING)
        self.assertEqual(LogLevel.to_python_level(LogLevel.INFO), logging.INFO)
        self.assertEqual(LogLevel.to_python_level(LogLevel.NORMAL), logging.INFO)
        self.assertEqual(LogLevel.to_python_level(LogLevel.DEBUG), logging.DEBUG)
        self.assertEqual(LogLevel.to_python_level(LogLevel.TRACE), logging.DEBUG)


class TestLogEntry(unittest.TestCase):
    """Test cases for the LogEntry class."""
    
    def test_initialization(self):
        """Test initializing a LogEntry."""
        entry = LogEntry(
            component="test.component",
            message="Test message"
        )
        
        self.assertEqual(entry.component, "test.component")
        self.assertEqual(entry.message, "Test message")
        self.assertEqual(entry.level, LogLevel.INFO)
        self.assertIsNotNone(entry.timestamp)
        self.assertEqual(entry.effective_timestamp, entry.timestamp)
        self.assertIsNotNone(entry.correlation_id)
        self.assertEqual(entry.schema_version, "1.0.0")
    
    def test_to_dict(self):
        """Test converting LogEntry to dictionary."""
        entry = LogEntry(
            component="test.component",
            message="Test message",
            level=LogLevel.ERROR,
            code="TEST001",
            context={"key": "value"},
            client_id="client123"
        )
        
        entry_dict = entry.to_dict()
        
        self.assertEqual(entry_dict["component"], "test.component")
        self.assertEqual(entry_dict["message"], "Test message")
        self.assertEqual(entry_dict["level"], "ERROR")
        self.assertEqual(entry_dict["code"], "TEST001")
        self.assertEqual(entry_dict["context"], {"key": "value"})
        self.assertEqual(entry_dict["client_id"], "client123")
    
    def test_to_from_json(self):
        """Test JSON serialization and deserialization."""
        original = LogEntry(
            component="test.component",
            message="Test message",
            level=LogLevel.ERROR,
            code="TEST001",
            context={"key": "value"},
            client_id="client123"
        )
        
        # Convert to JSON
        json_str = original.to_json()
        
        # Convert back to LogEntry
        restored = LogEntry.from_json(json_str)
        
        # Compare
        self.assertEqual(restored.component, original.component)
        self.assertEqual(restored.message, original.message)
        self.assertEqual(restored.level, original.level)
        self.assertEqual(restored.code, original.code)
        self.assertEqual(restored.context, original.context)
        self.assertEqual(restored.client_id, original.client_id)


class TestLogStorage(unittest.TestCase):
    """Test cases for the LogStorage class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for logs
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize storage
        from hermes.core.logging import LogStorage
        self.storage = LogStorage(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_store_retrieve(self):
        """Test storing and retrieving log entries."""
        # Create log entry
        entry = LogEntry(
            component="test.component",
            message="Test message",
            level=LogLevel.INFO,
            code="TEST001"
        )
        
        # Store entry
        self.storage.store(entry)
        
        # Query entries
        entries = self.storage.query(
            components=["test.component"],
            limit=10
        )
        
        # Check results
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].component, "test.component")
        self.assertEqual(entries[0].message, "Test message")
        self.assertEqual(entries[0].level, LogLevel.INFO)
        self.assertEqual(entries[0].code, "TEST001")
    
    def test_query_filtering(self):
        """Test query filtering capabilities."""
        # Create log entries
        components = ["component1", "component2"]
        levels = [LogLevel.ERROR, LogLevel.INFO, LogLevel.DEBUG]
        
        for i in range(10):
            component = components[i % 2]
            level = levels[i % 3]
            
            entry = LogEntry(
                component=component,
                message=f"Message {i}",
                level=level,
                code=f"TEST{i:03d}"
            )
            
            self.storage.store(entry)
        
        # Query by component
        entries = self.storage.query(
            components=["component1"],
            limit=10
        )
        
        self.assertEqual(len(entries), 5)
        for entry in entries:
            self.assertEqual(entry.component, "component1")
        
        # Query by level
        entries = self.storage.query(
            levels=[LogLevel.ERROR],
            limit=10
        )
        
        for entry in entries:
            self.assertEqual(entry.level, LogLevel.ERROR)
        
        # Query by both
        entries = self.storage.query(
            components=["component2"],
            levels=[LogLevel.INFO],
            limit=10
        )
        
        for entry in entries:
            self.assertEqual(entry.component, "component2")
            self.assertEqual(entry.level, LogLevel.INFO)


class TestLogger(unittest.TestCase):
    """Test cases for the Logger class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for logs
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize log manager
        from hermes.core.logging import LogManager
        self.log_manager = LogManager(
            storage_path=self.temp_dir,
            console_output=False  # Disable console output for tests
        )
        
        # Initialize logger
        self.logger = Logger(
            component="test.component",
            log_manager=self.log_manager,
            client_id="test_client",
            default_context={"test": True}
        )
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_log_levels(self):
        """Test logging at different levels."""
        # Log at different levels
        self.logger.fatal("Fatal message", code="FATAL001")
        self.logger.error("Error message", code="ERROR001")
        self.logger.warn("Warning message", code="WARN001")
        self.logger.info("Info message", code="INFO001")
        self.logger.normal("Normal message", code="NORMAL001")
        self.logger.debug("Debug message", code="DEBUG001")
        self.logger.trace("Trace message", code="TRACE001")
        
        # Query logs
        entries = self.log_manager.query(
            components=["test.component"],
            limit=10
        )
        
        # Check results
        self.assertEqual(len(entries), 7)
        
        # Check level distribution
        level_counts = {}
        for entry in entries:
            level = entry.level.name
            level_counts[level] = level_counts.get(level, 0) + 1
        
        self.assertEqual(level_counts["FATAL"], 1)
        self.assertEqual(level_counts["ERROR"], 1)
        self.assertEqual(level_counts["WARN"], 1)
        self.assertEqual(level_counts["INFO"], 1)
        self.assertEqual(level_counts["NORMAL"], 1)
        self.assertEqual(level_counts["DEBUG"], 1)
        self.assertEqual(level_counts["TRACE"], 1)
    
    def test_context_merging(self):
        """Test context merging capabilities."""
        # Log with additional context
        self.logger.info(
            "Message with context",
            code="INFO001",
            context={"additional": "value"}
        )
        
        # Query logs
        entries = self.log_manager.query(
            components=["test.component"],
            limit=1
        )
        
        # Check results
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].context["test"], True)  # Default context
        self.assertEqual(entries[0].context["additional"], "value")  # Added context
    
    def test_with_context(self):
        """Test creating logger with additional context."""
        # Create logger with additional context
        context_logger = self.logger.with_context({
            "context_value": 123
        })
        
        # Log with context logger
        context_logger.info("Message from context logger")
        
        # Query logs
        entries = self.log_manager.query(
            components=["test.component"],
            limit=1
        )
        
        # Check results
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].context["test"], True)  # Original context
        self.assertEqual(entries[0].context["context_value"], 123)  # Added context
    
    def test_with_correlation(self):
        """Test creating logger with correlation ID."""
        # Create logger with correlation ID
        correlation_id = "test-correlation-id"
        correlation_logger = self.logger.with_correlation(correlation_id)
        
        # Log with correlation logger
        correlation_logger.info("Message 1 from correlation logger")
        correlation_logger.info("Message 2 from correlation logger")
        
        # Query logs
        entries = self.log_manager.query(
            components=["test.component"],
            limit=2
        )
        
        # Check results
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].correlation_id, correlation_id)
        self.assertEqual(entries[1].correlation_id, correlation_id)


if __name__ == "__main__":
    unittest.main()