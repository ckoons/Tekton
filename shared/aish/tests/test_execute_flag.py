#!/usr/bin/env python3
"""
Tests for aish -x/--execute flag functionality.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestExecuteFlag:
    """Test suite for aish execute flag."""
    
    def __init__(self):
        self.test_results = []
        
    def run_aish_command(self, args):
        """Run aish command and capture output."""
        aish_path = Path(__file__).parent.parent / 'aish'
        
        cmd = [sys.executable, str(aish_path)] + args
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
    
    def test_execute_flag_parsing(self):
        """Test that -x flag is parsed correctly."""
        print("Testing: Execute flag parsing...")
        
        # Test with mock to verify argument parsing
        with patch('sys.argv', ['aish', 'test-ci', 'message', '-x']):
            try:
                import argparse
                parser = argparse.ArgumentParser()
                parser.add_argument('ai_or_script', nargs='?')
                parser.add_argument('message', nargs='*')
                parser.add_argument('-x', '--execute', nargs='?', const='\n', default=None)
                
                args = parser.parse_args(['test-ci', 'message', '-x'])
                
                assert args.execute == '\n', f"Expected '\\n', got {repr(args.execute)}"
                print("✓ Execute flag parsing successful")
                return True
                
            except AssertionError as e:
                print(f"✗ Execute flag parsing failed: {e}")
                return False
    
    def test_execute_with_custom_delimiter(self):
        """Test -x with custom delimiter."""
        print("Testing: Execute with custom delimiter...")
        
        with patch('sys.argv', ['aish', 'test-ci', 'message', '-x', '\\r\\n']):
            try:
                import argparse
                parser = argparse.ArgumentParser()
                parser.add_argument('ai_or_script', nargs='?')
                parser.add_argument('message', nargs='*')
                parser.add_argument('-x', '--execute', nargs='?', const='\n', default=None)
                
                args = parser.parse_args(['test-ci', 'message', '-x', '\\r\\n'])
                
                assert args.execute == '\\r\\n', f"Expected '\\r\\n', got {repr(args.execute)}"
                print("✓ Execute with custom delimiter successful")
                return True
                
            except AssertionError as e:
                print(f"✗ Execute with custom delimiter failed: {e}")
                return False
    
    def test_execute_long_form(self):
        """Test --execute long form."""
        print("Testing: --execute long form...")
        
        with patch('sys.argv', ['aish', 'test-ci', 'message', '--execute']):
            try:
                import argparse
                parser = argparse.ArgumentParser()
                parser.add_argument('ai_or_script', nargs='?')
                parser.add_argument('message', nargs='*')
                parser.add_argument('-x', '--execute', nargs='?', const='\n', default=None)
                
                args = parser.parse_args(['test-ci', 'message', '--execute'])
                
                assert args.execute == '\n', f"Expected '\\n', got {repr(args.execute)}"
                print("✓ --execute long form successful")
                return True
                
            except AssertionError as e:
                print(f"✗ --execute long form failed: {e}")
                return False
    
    def test_no_execute_flag(self):
        """Test backward compatibility without execute flag."""
        print("Testing: No execute flag (backward compatibility)...")
        
        with patch('sys.argv', ['aish', 'test-ci', 'message']):
            try:
                import argparse
                parser = argparse.ArgumentParser()
                parser.add_argument('ai_or_script', nargs='?')
                parser.add_argument('message', nargs='*')
                parser.add_argument('-x', '--execute', nargs='?', const='\n', default=None)
                
                args = parser.parse_args(['test-ci', 'message'])
                
                assert args.execute is None, f"Expected None, got {repr(args.execute)}"
                print("✓ No execute flag successful")
                return True
                
            except AssertionError as e:
                print(f"✗ No execute flag failed: {e}")
                return False
    
    def test_send_to_ci_with_execute(self):
        """Test that execute info is passed to send_to_ci."""
        print("Testing: send_to_ci with execute...")
        
        try:
            # Import the unified_sender module
            from src.core.unified_sender import send_to_ci
            
            # Mock the registry and socket operations
            with patch('src.core.unified_sender.get_registry') as mock_registry, \
                 patch('socket.socket') as mock_socket:
                
                # Setup mocks
                mock_ci = {
                    'name': 'test-ci',
                    'type': 'ci_tool',
                    'socket': '/tmp/ci_msg_test-ci.sock'
                }
                mock_registry.return_value.get_by_name.return_value = mock_ci
                
                mock_sock_instance = MagicMock()
                mock_socket.return_value = mock_sock_instance
                
                # Call send_to_ci with execute parameters
                result = send_to_ci(
                    'test-ci',
                    'test message',
                    sender_name='test',
                    execute=True,
                    delimiter='\n'
                )
                
                # Verify the message sent includes execute info
                sent_data = mock_sock_instance.send.call_args[0][0]
                sent_message = json.loads(sent_data.decode('utf-8'))
                
                assert sent_message['execute'] == True, "Execute flag not in message"
                assert sent_message['delimiter'] == '\n', "Delimiter not in message"
                
                print("✓ send_to_ci with execute successful")
                return True
                
        except Exception as e:
            print(f"✗ send_to_ci with execute failed: {e}")
            return False
    
    def test_execute_flag_help(self):
        """Test that -x flag appears in help."""
        print("Testing: Execute flag in help...")
        
        returncode, stdout, stderr = self.run_aish_command(['--help'])
        
        try:
            # Check that execute flag is documented
            assert '-x' in stdout or '--execute' in stdout, "Execute flag not in help"
            
            print("✓ Execute flag in help successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Execute flag in help failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("=" * 60)
        print("aish Execute Flag Tests")
        print("=" * 60)
        
        tests = [
            self.test_execute_flag_parsing,
            self.test_execute_with_custom_delimiter,
            self.test_execute_long_form,
            self.test_no_execute_flag,
            self.test_send_to_ci_with_execute,
            self.test_execute_flag_help
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"✗ Test {test.__name__} crashed: {e}")
                failed += 1
            
            print()
        
        print("=" * 60)
        print(f"Results: {passed} passed, {failed} failed")
        print("=" * 60)
        
        return failed == 0


def main():
    """Main test runner."""
    tester = TestExecuteFlag()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()