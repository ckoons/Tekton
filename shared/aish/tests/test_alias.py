"""
Test suite for aish alias functionality
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_runner import AishTest, main

class AliasTests(AishTest):
    """Test alias creation, execution, and management"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        # Create a temporary TEKTON_ROOT for testing
        self.test_tekton_root = tempfile.mkdtemp()
        self.original_tekton_root = os.environ.get('TEKTON_ROOT')
        os.environ['TEKTON_ROOT'] = self.test_tekton_root
        
        # Ensure alias directory exists
        self.alias_dir = Path(self.test_tekton_root) / '.tekton' / 'aliases'
        self.alias_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore original TEKTON_ROOT
        if self.original_tekton_root:
            os.environ['TEKTON_ROOT'] = self.original_tekton_root
        else:
            del os.environ['TEKTON_ROOT']
        
        # Remove temporary directory
        shutil.rmtree(self.test_tekton_root, ignore_errors=True)
        super().tearDown()
    
    def test_alias_create_simple(self):
        """Test creating a simple alias"""
        exit_code, stdout, stderr = self.run_command('aish alias create hello "echo Hello World"')
        self.assertEqual(exit_code, 0)
        self.assertIn("Created alias 'hello'", stdout)
        
        # Verify alias file was created
        alias_file = self.alias_dir / 'hello.json'
        self.assertTrue(alias_file.exists())
        
        # Verify alias content
        with open(alias_file, 'r') as f:
            alias_data = json.load(f)
        self.assertEqual(alias_data['name'], 'hello')
        self.assertEqual(alias_data['command'], 'echo Hello World')
    
    def test_alias_create_with_description(self):
        """Test creating an alias with description"""
        exit_code, stdout, stderr = self.run_command('aish alias create greet "echo Hello $1" "Greet someone by name"')
        self.assertEqual(exit_code, 0)
        self.assertIn("Created alias 'greet'", stdout)
        
        # Verify description was saved
        alias_file = self.alias_dir / 'greet.json'
        with open(alias_file, 'r') as f:
            alias_data = json.load(f)
        self.assertEqual(alias_data['description'], 'Greet someone by name')
    
    def test_alias_already_exists(self):
        """Test error when creating duplicate alias"""
        # Create first alias
        self.run_command('aish alias create test "echo test"')
        
        # Try to create again
        exit_code, stdout, stderr = self.run_command('aish alias create test "echo test2"')
        self.assertNotEqual(exit_code, 0)
        self.assertIn("already defined", stdout + stderr)
        self.assertIn("aish alias delete test", stdout + stderr)
    
    def test_alias_delete(self):
        """Test deleting an alias"""
        # Create alias first
        self.run_command('aish alias create temp "echo temporary"')
        
        # Delete it
        exit_code, stdout, stderr = self.run_command('aish alias delete temp')
        self.assertEqual(exit_code, 0)
        self.assertIn("Deleted alias 'temp'", stdout)
        
        # Verify file was removed
        alias_file = self.alias_dir / 'temp.json'
        self.assertFalse(alias_file.exists())
    
    def test_alias_delete_nonexistent(self):
        """Test deleting non-existent alias"""
        exit_code, stdout, stderr = self.run_command('aish alias delete nonexistent')
        self.assertNotEqual(exit_code, 0)
        self.assertIn("not found", stdout + stderr)
    
    def test_alias_list_empty(self):
        """Test listing aliases when none exist"""
        exit_code, stdout, stderr = self.run_command('aish alias list')
        self.assertEqual(exit_code, 0)
        self.assertIn("No aliases defined", stdout)
    
    def test_alias_list_with_aliases(self):
        """Test listing multiple aliases"""
        # Create some aliases
        self.run_command('aish alias create hello "echo Hello"')
        self.run_command('aish alias create greet "echo Hi $1" "Greet someone"')
        
        exit_code, stdout, stderr = self.run_command('aish alias list')
        self.assertEqual(exit_code, 0)
        self.assertIn("hello", stdout)
        self.assertIn("echo Hello", stdout)
        self.assertIn("greet", stdout)
        self.assertIn("echo Hi $1", stdout)
        self.assertIn("Greet someone", stdout)
    
    def test_alias_show(self):
        """Test showing alias details"""
        # Create alias
        self.run_command('aish alias create deploy "git push && ssh prod deploy" "Deploy to production"')
        
        exit_code, stdout, stderr = self.run_command('aish alias show deploy')
        self.assertEqual(exit_code, 0)
        self.assertIn("Alias: deploy", stdout)
        self.assertIn("Command: git push && ssh prod deploy", stdout)
        self.assertIn("Description: Deploy to production", stdout)
        self.assertIn("Created:", stdout)
        self.assertIn("Usage count: 0", stdout)
    
    def test_alias_show_nonexistent(self):
        """Test showing non-existent alias"""
        exit_code, stdout, stderr = self.run_command('aish alias show nonexistent')
        self.assertNotEqual(exit_code, 0)
        self.assertIn("not found", stdout + stderr)
    
    def test_alias_recursive_validation(self):
        """Test that recursive aliases are prevented"""
        # Create first alias
        self.run_command('aish alias create hello "echo Hello"')
        
        # Try to create alias that uses another alias
        exit_code, stdout, stderr = self.run_command('aish alias create greet "hello World"')
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Cannot use alias", stdout + stderr)
        
        # Try with 'aish alias' pattern
        exit_code, stdout, stderr = self.run_command('aish alias create greet2 "aish hello World"')
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Cannot use alias", stdout + stderr)
    
    def test_alias_execution(self):
        """Test executing an alias"""
        # Create simple alias
        self.run_command('aish alias create hello "echo Hello from alias"')
        
        # Execute it
        exit_code, stdout, stderr = self.run_command('aish hello')
        self.assertEqual(exit_code, 0)
        self.assertIn("Hello from alias", stdout)
    
    def test_alias_parameter_substitution(self):
        """Test parameter substitution in aliases"""
        # Create alias with parameters
        self.run_command('aish alias create greet "echo Hello $1, welcome to $2"')
        
        # Execute with parameters
        exit_code, stdout, stderr = self.run_command('aish greet Casey Tekton')
        self.assertEqual(exit_code, 0)
        self.assertIn("Hello Casey, welcome to Tekton", stdout)
    
    def test_alias_all_parameters(self):
        """Test $* parameter substitution"""
        # Create alias using $*
        self.run_command('aish alias create echo_all "echo All args: $*"')
        
        # Execute with multiple args
        exit_code, stdout, stderr = self.run_command('aish echo_all one two three')
        self.assertEqual(exit_code, 0)
        self.assertIn("All args: one two three", stdout)
    
    def test_alias_usage_tracking(self):
        """Test that alias usage is tracked"""
        # Create and execute alias
        self.run_command('aish alias create test "echo test"')
        self.run_command('aish test')
        
        # Check usage count
        exit_code, stdout, stderr = self.run_command('aish alias show test')
        self.assertEqual(exit_code, 0)
        self.assertIn("Usage count: 1", stdout)
        self.assertIn("Last used:", stdout)

if __name__ == '__main__':
    main(AliasTests)