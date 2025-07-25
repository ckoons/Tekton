#!/usr/bin/env python3
"""
Test suite for unified CI registry and messaging.
Tests the new configuration-driven approach to CI communication.
"""

import unittest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from registry.ci_registry import CIRegistry, get_registry
from core.unified_sender import send_to_ci


class TestUnifiedCIRegistry(unittest.TestCase):
    """Test the unified CI registry functionality."""
    
    def setUp(self):
        """Set up test registry."""
        self.registry = CIRegistry()
    
    def test_greek_chorus_loading(self):
        """Test that Greek Chorus CIs are loaded with proper configuration."""
        numa = self.registry.get_by_name('numa')
        self.assertIsNotNone(numa)
        self.assertEqual(numa['type'], 'greek')
        self.assertEqual(numa['port'], 8316)
        self.assertEqual(numa['message_format'], 'rhetor_socket')
        self.assertEqual(numa['message_endpoint'], '/rhetor/socket')
    
    def test_registry_get_by_type(self):
        """Test filtering CIs by type."""
        greek_cis = self.registry.get_by_type('greek')
        self.assertTrue(len(greek_cis) > 0)
        self.assertTrue(all(ci['type'] == 'greek' for ci in greek_cis))
    
    def test_registry_get_all(self):
        """Test getting all CIs."""
        all_cis = self.registry.get_all()
        self.assertTrue(len(all_cis) > 0)
        # Should have at least the Greek Chorus CIs
        ci_names = [ci['name'] for ci in all_cis]
        self.assertIn('numa', ci_names)
        self.assertIn('apollo', ci_names)
    
    def test_json_output(self):
        """Test JSON serialization of registry."""
        json_str = self.registry.to_json()
        data = json.loads(json_str)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
    
    def test_text_formatting(self):
        """Test text output formatting."""
        output = self.registry.format_text_output()
        self.assertIn('Greek Chorus AIs:', output)
        self.assertIn('numa', output)
        self.assertIn('(port 8316', output)


class TestUnifiedSender(unittest.TestCase):
    """Test the unified message sender."""
    
    @patch('core.unified_sender.get_registry')
    def test_ci_not_found(self, mock_get_registry):
        """Test sending to non-existent CI."""
        mock_registry = MagicMock()
        mock_registry.get_by_name.return_value = None
        mock_get_registry.return_value = mock_registry
        
        result = send_to_ci('nonexistent', 'test message')
        self.assertFalse(result)
    
    @patch('core.unified_sender.get_registry')
    @patch('urllib.request.urlopen')
    def test_terma_route_format(self, mock_urlopen, mock_get_registry):
        """Test sending with terma_route format."""
        # Mock registry response
        mock_registry = MagicMock()
        mock_registry.get_by_name.return_value = {
            'name': 'sandi',
            'type': 'terminal',
            'endpoint': 'http://localhost:8304',
            'message_endpoint': '/api/mcp/v2/terminals/route-message',
            'message_format': 'terma_route'
        }
        mock_get_registry.return_value = mock_registry
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'success': True,
            'delivered_to': ['sandi']
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = send_to_ci('sandi', 'test message')
        self.assertTrue(result)
    
    @patch('core.unified_sender.get_registry')
    @patch('urllib.request.urlopen')
    def test_json_simple_format(self, mock_urlopen, mock_get_registry):
        """Test sending with json_simple format."""
        # Mock registry response
        mock_registry = MagicMock()
        mock_registry.get_by_name.return_value = {
            'name': 'external-ci',
            'type': 'external',
            'endpoint': 'http://external.com',
            'message_endpoint': '/api/message',
            'message_format': 'json_simple'
        }
        mock_get_registry.return_value = mock_registry
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'response': 'Message received'
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = send_to_ci('external-ci', 'test message')
        self.assertTrue(result)
    
    @patch('core.unified_sender.get_registry')
    def test_unknown_format(self, mock_get_registry):
        """Test sending with unknown format."""
        # Mock registry response
        mock_registry = MagicMock()
        mock_registry.get_by_name.return_value = {
            'name': 'weird-ci',
            'type': 'unknown',
            'message_format': 'unknown_format'
        }
        mock_get_registry.return_value = mock_registry
        
        result = send_to_ci('weird-ci', 'test message')
        self.assertFalse(result)


class TestListCommand(unittest.TestCase):
    """Test the aish list command variations."""
    
    def test_list_command_import(self):
        """Test that list command can be imported."""
        try:
            from commands.list import handle_list_command
            self.assertTrue(callable(handle_list_command))
        except ImportError as e:
            self.fail(f"Failed to import list command: {e}")
    
    @patch('commands.list.get_registry')
    def test_list_all(self, mock_get_registry):
        """Test listing all CIs."""
        from commands.list import handle_list_command
        
        mock_registry = MagicMock()
        mock_registry.format_text_output.return_value = "Test output"
        mock_get_registry.return_value = mock_registry
        
        # Capture output
        with patch('builtins.print') as mock_print:
            handle_list_command([])
            mock_print.assert_called_with("Test output")
    
    @patch('commands.list.get_registry')
    def test_list_json(self, mock_get_registry):
        """Test JSON output."""
        from commands.list import handle_list_command
        
        mock_registry = MagicMock()
        mock_registry.get_all.return_value = [{'name': 'test', 'type': 'test'}]
        mock_get_registry.return_value = mock_registry
        
        # Capture output
        with patch('builtins.print') as mock_print:
            handle_list_command(['json'])
            # Should print JSON
            args = mock_print.call_args[0][0]
            data = json.loads(args)
            self.assertIsInstance(data, list)


if __name__ == '__main__':
    unittest.main()