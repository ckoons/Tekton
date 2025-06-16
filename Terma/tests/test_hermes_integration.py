"""
Tests for Hermes integration
"""

import unittest
from unittest.mock import MagicMock, patch
import json
import os
import sys
import tempfile

class TestHermesIntegration(unittest.TestCase):
    """Test Hermes integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        # This is a placeholder since the implementation will be in Phase 3
        # We're just testing the registration script functionality
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Tear down test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    @patch('requests.post')
    def test_registration(self, mock_post):
        """Test Hermes registration"""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        
        # Import the registration script
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        import register_with_hermes
        
        # Call the registration function with the temp file
        result = register_with_hermes.register_with_hermes(
            "http://localhost:8000", 
            self.temp_file.name
        )
        
        # Check that the registration was successful
        self.assertTrue(result)
        
        # Check that the registration file was created
        self.assertTrue(os.path.exists(self.temp_file.name))
        
        # Check that the registration file has the correct content
        with open(self.temp_file.name, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["name"], "Terma")
            self.assertEqual(len(data["capabilities"]), 4)
            self.assertIn("terminal.create", [c["name"] for c in data["capabilities"]])
        
        # Check that the registration request was made
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_registration_failure(self, mock_post):
        """Test Hermes registration failure"""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        # Import the registration script
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        import register_with_hermes
        
        # Call the registration function with the temp file
        result = register_with_hermes.register_with_hermes(
            "http://localhost:8000", 
            self.temp_file.name
        )
        
        # Check that the registration failed
        self.assertFalse(result)
        
        # Check that the registration file was still created
        self.assertTrue(os.path.exists(self.temp_file.name))

if __name__ == "__main__":
    unittest.main()