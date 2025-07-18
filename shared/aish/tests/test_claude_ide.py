#!/usr/bin/env python3
"""
Test suite for Claude Code IDE functionality.

Tests the introspect, context, and explain commands.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.introspect import TektonInspector, IntrospectionCache
from src.commands.introspect import introspect_command
from src.commands.context import context_command
from src.commands.explain import explain_command


class TestIntrospection(unittest.TestCase):
    """Test the introspection engine."""
    
    def setUp(self):
        self.inspector = TektonInspector()
    
    def test_introspect_aiShell(self):
        """Test introspecting AIShell class."""
        info = self.inspector.get_class_info('AIShell')
        
        self.assertFalse(info.get('error'), f"Error: {info.get('message')}")
        self.assertEqual(info['name'], 'AIShell')
        self.assertIn('methods', info)
        
        # Check for expected methods
        methods = info['methods']
        self.assertIn('broadcast_message', methods)
        self.assertIn('send_to_ai', methods)
        self.assertIn('execute_command', methods)
    
    def test_introspect_messageHandler(self):
        """Test introspecting MessageHandler class."""
        info = self.inspector.get_class_info('MessageHandler')
        
        self.assertFalse(info.get('error'))
        self.assertEqual(info['name'], 'MessageHandler')
        
        # Check for expected methods
        methods = info['methods']
        self.assertIn('send', methods)
        self.assertIn('broadcast', methods)
        self.assertIn('read', methods)
        self.assertIn('write', methods)
    
    def test_introspect_nonexistent_class(self):
        """Test introspecting a class that doesn't exist."""
        info = self.inspector.get_class_info('NonExistentClass')
        
        self.assertTrue(info.get('error'))
        self.assertIn('not found', info['message'])
        self.assertIn('suggestions', info)
    
    def test_method_signatures(self):
        """Test that method signatures are extracted correctly."""
        info = self.inspector.get_class_info('MessageHandler')
        
        send_method = info['methods'].get('send')
        self.assertIsNotNone(send_method)
        
        # Check parameters
        params = send_method['parameters']
        param_names = [p['name'] for p in params if p['name'] != 'self']
        self.assertIn('ai_name', param_names)
        self.assertIn('message', param_names)
        
        # Check return type
        self.assertEqual(send_method['return_type'], 'str')


class TestCommands(unittest.TestCase):
    """Test the CLI commands."""
    
    def test_introspect_command(self):
        """Test the introspect command."""
        result = introspect_command(['AIShell'])
        
        self.assertIn('AIShell class', result)
        self.assertIn('broadcast_message', result)
        self.assertIn('Methods:', result)
    
    def test_introspect_command_help(self):
        """Test introspect command help."""
        result = introspect_command(['--help'])
        
        self.assertIn('Usage:', result)
        self.assertIn('aish introspect', result)
        self.assertIn('Examples:', result)
    
    def test_context_command_with_file(self):
        """Test context command with a test file."""
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
from src.core.shell import AIShell
import os

class TestClass:
    def test_method(self):
        pass

def test_function():
    pass
''')
            test_file = f.name
        
        try:
            result = context_command([test_file])
            
            self.assertIn('Context for:', result)
            self.assertIn('Imported:', result)
            self.assertIn('AIShell', result)
            self.assertIn('Local Classes:', result)
            self.assertIn('TestClass', result)
            self.assertIn('Local Functions:', result)
            self.assertIn('test_function', result)
        finally:
            os.unlink(test_file)
    
    def test_explain_command_attributeError(self):
        """Test explain command with AttributeError."""
        error = "AttributeError: 'AIShell' object has no attribute 'broadcast'"
        result = explain_command([error])
        
        self.assertIn('Error Type: AttributeError', result)
        self.assertIn('Suggestions:', result)
        self.assertIn('broadcast_message', result)
    
    def test_explain_command_no_error(self):
        """Test explain command with no recognizable error."""
        result = explain_command(['random text'])
        
        self.assertIn('Unable to analyze this error', result)
        self.assertIn('aish introspect', result)


class TestCache(unittest.TestCase):
    """Test the caching functionality."""
    
    def setUp(self):
        self.cache = IntrospectionCache(cache_dir='/tmp/test_aish_cache')
    
    def tearDown(self):
        self.cache.clear()
    
    def test_cache_operations(self):
        """Test basic cache operations."""
        test_data = {'name': 'TestClass', 'methods': {}}
        
        # Test set and get
        self.cache.set('TestClass', test_data)
        cached = self.cache.get('TestClass')
        self.assertEqual(cached['name'], 'TestClass')
        
        # Test invalidation
        self.cache.invalidate('TestClass')
        cached = self.cache.get('TestClass')
        self.assertIsNone(cached)
    
    def test_cache_file_modification(self):
        """Test cache invalidation on file modification."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_file = f.name
        
        try:
            test_data = {'name': 'TestClass', 'methods': {}}
            self.cache.set('TestClass', test_data, test_file)
            
            # Should get cached data
            cached = self.cache.get('TestClass', test_file)
            self.assertIsNotNone(cached)
            
            # Modify file
            import time
            time.sleep(0.1)  # Ensure mtime changes
            with open(test_file, 'w') as f:
                f.write('modified')
            
            # Cache should be invalid now
            cached = self.cache.get('TestClass', test_file)
            self.assertIsNone(cached)
        finally:
            os.unlink(test_file)


class TestErrorAnalysis(unittest.TestCase):
    """Test error analysis functionality."""
    
    def setUp(self):
        self.inspector = TektonInspector()
    
    def test_explain_attributeError(self):
        """Test explaining AttributeError."""
        error = "AttributeError: 'AIShell' object has no attribute 'send_broadcast'"
        analysis = self.inspector.explain_error(error)
        
        self.assertEqual(analysis['error_type'], 'AttributeError')
        self.assertEqual(analysis['object_name'], 'AIShell')
        self.assertEqual(analysis['attribute_name'], 'send_broadcast')
        self.assertTrue(len(analysis['suggestions']) > 0)
    
    def test_find_similar_methods(self):
        """Test finding similar method names."""
        info = self.inspector.get_class_info('AIShell')
        methods = info['methods']
        
        similar = self.inspector._find_similar_methods('broadcast', methods)
        self.assertIn('broadcast_message', similar)
        
        similar = self.inspector._find_similar_methods('send', methods)
        self.assertIn('send_to_ai', similar)


if __name__ == '__main__':
    unittest.main()