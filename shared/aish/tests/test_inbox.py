#!/usr/bin/env python3
"""
Inbox system functional tests for aish
Tests the unified inbox message management system
"""

import json
import tempfile
import shutil
from pathlib import Path
from .test_runner import AishTest, TestSuite


class TestInboxHelp(AishTest):
    """Test aish inbox help command"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish inbox help")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Check for expected help sections
        expected = [
            "aish inbox commands:",
            "Basic Usage:",
            "Inbox Types:",
            "prompt - Urgent messages",
            "new    - Regular incoming", 
            "keep   - Saved/archived",
            "Filtering:",
            "from <ci-name>"
        ]
        
        for text in expected:
            if text not in stdout:
                self.error_message = f"Missing help text: '{text}'"
                return False
        
        return True


class TestInboxTraining(AishTest):
    """Test aish inbox training command"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish inbox training")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Check for training content
        expected = [
            "INBOX TRAINING FOR CIs",
            "BATCH PROCESSING",
            "MESSAGE STRUCTURE",
            "SENDING MESSAGES",
            "COMMON PATTERNS",
            "aish inbox get prompt"
        ]
        
        for text in expected:
            if text not in stdout:
                self.error_message = f"Missing training content: '{text}'"
                return False
        
        return True


class TestInboxCount(AishTest):
    """Test inbox count commands"""
    
    def test(self) -> bool:
        # Test count for each inbox type
        for inbox_type in ['prompt', 'new', 'keep']:
            exit_code, stdout, stderr = self.run_command(f"aish inbox count {inbox_type}")
            
            if exit_code != 0:
                self.error_message = f"Exit code {exit_code} for count {inbox_type}, expected 0"
                return False
            
            # Should return a number
            try:
                count = int(stdout.strip())
                if count < 0:
                    self.error_message = f"Invalid count {count} for {inbox_type}"
                    return False
            except ValueError:
                self.error_message = f"Non-numeric count output for {inbox_type}: '{stdout.strip()}'"
                return False
        
        return True


class TestInboxDefault(AishTest):
    """Test default inbox command (shows counts)"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish inbox")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Should show format like "prompt:0  new:1  keep:2"
        output = stdout.strip()
        
        # Check for expected format
        expected_parts = ["prompt:", "new:", "keep:"]
        for part in expected_parts:
            if part not in output:
                self.error_message = f"Missing inbox type in output: '{part}'"
                return False
        
        return True


class TestInboxSendShow(AishTest):
    """Test sending and showing messages"""
    
    def setup(self):
        """Clean up any test messages first"""
        for inbox_type in ['prompt', 'new', 'keep']:
            self.run_command(f"aish inbox clear {inbox_type}")
    
    def test(self) -> bool:
        test_message = "Test message from inbox test suite"
        test_ci = "test-ci"
        
        # Test sending to each inbox type
        for inbox_type in ['prompt', 'new', 'keep']:
            # Send a message
            exit_code, stdout, stderr = self.run_command(
                f'aish inbox send {inbox_type} {test_ci} "{test_message}"'
            )
            
            if exit_code != 0:
                self.error_message = f"Failed to send to {inbox_type}: {stderr}"
                return False
            
            # Should return message ID
            message_id = stdout.strip()
            if not message_id:
                self.error_message = f"No message ID returned for {inbox_type}"
                return False
            
            # Verify count increased
            exit_code, stdout, stderr = self.run_command(f"aish inbox count {inbox_type}")
            if exit_code != 0:
                self.error_message = f"Failed to count {inbox_type} after send"
                return False
            
            count = int(stdout.strip())
            if count == 0:
                self.error_message = f"Count still 0 after sending to {inbox_type}"
                return False
            
            # Test showing messages
            exit_code, stdout, stderr = self.run_command(f"aish inbox show {inbox_type}")
            if exit_code != 0:
                self.error_message = f"Failed to show {inbox_type} messages"
                return False
            
            if test_message not in stdout:
                self.error_message = f"Test message not found in {inbox_type} show output"
                return False
        
        return True
    
    def teardown(self):
        """Clean up test messages"""
        for inbox_type in ['prompt', 'new', 'keep']:
            self.run_command(f"aish inbox clear {inbox_type}")


class TestInboxJson(AishTest):
    """Test JSON output formats"""
    
    def setup(self):
        """Set up test messages"""
        for inbox_type in ['prompt', 'new', 'keep']:
            self.run_command(f"aish inbox clear {inbox_type}")
        
        # Send test messages
        self.run_command('aish inbox send new test-sender "JSON test message"')
    
    def test(self) -> bool:
        # Test JSON output
        exit_code, stdout, stderr = self.run_command("aish inbox json new")
        
        if exit_code != 0:
            self.error_message = f"Failed to get JSON output: {stderr}"
            return False
        
        # Validate JSON format
        try:
            messages = json.loads(stdout)
            
            if not isinstance(messages, list):
                self.error_message = "JSON output should be a list"
                return False
            
            if len(messages) > 0:
                msg = messages[0]
                required_fields = ['id', 'from', 'to', 'timestamp', 'purpose', 'message']
                
                for field in required_fields:
                    if field not in msg:
                        self.error_message = f"Missing required field in JSON: {field}"
                        return False
                
                if "JSON test message" not in msg['message']:
                    self.error_message = "Test message not found in JSON output"
                    return False
        
        except json.JSONDecodeError as e:
            self.error_message = f"Invalid JSON output: {e}"
            return False
        
        return True
    
    def teardown(self):
        """Clean up test messages"""
        self.run_command("aish inbox clear new")


class TestInboxGet(AishTest):
    """Test get command (retrieve and remove)"""
    
    def setup(self):
        """Set up test messages"""
        self.run_command("aish inbox clear new")
        self.run_command('aish inbox send new test-ci "Message for get test"')
    
    def test(self) -> bool:
        # Verify message exists
        exit_code, stdout, stderr = self.run_command("aish inbox count new")
        if exit_code != 0 or stdout.strip() == "0":
            self.error_message = "Test message not found in setup"
            return False
        
        # Get messages (should remove them)
        exit_code, stdout, stderr = self.run_command("aish inbox get new")
        
        if exit_code != 0:
            self.error_message = f"Failed to get messages: {stderr}"
            return False
        
        # Validate JSON output
        try:
            messages = json.loads(stdout)
            if not messages:
                self.error_message = "No messages returned by get command"
                return False
            
            if "Message for get test" not in messages[0]['message']:
                self.error_message = "Test message not found in get output"
                return False
        
        except json.JSONDecodeError as e:
            self.error_message = f"Invalid JSON from get command: {e}"
            return False
        
        # Verify messages were removed
        exit_code, stdout, stderr = self.run_command("aish inbox count new")
        if exit_code != 0:
            self.error_message = "Failed to check count after get"
            return False
        
        if stdout.strip() != "0":
            self.error_message = f"Messages not removed by get command, count: {stdout.strip()}"
            return False
        
        return True


class TestInboxFiltering(AishTest):
    """Test 'from <ci>' filtering"""
    
    def setup(self):
        """Set up test messages from different senders"""
        self.run_command("aish inbox clear new")
        self.run_command('aish inbox send new test-receiver "Message from sender1" ')
        # We can't easily change the sender in tests, but we can test the syntax
    
    def test(self) -> bool:
        # Test that from filter syntax is accepted
        exit_code, stdout, stderr = self.run_command("aish inbox count new from nonexistent")
        
        # Should not error, just return 0 for no matches
        if exit_code != 0:
            self.error_message = f"From filter failed: {stderr}"
            return False
        
        # Should return 0 since no messages from 'nonexistent'
        count = stdout.strip()
        if count != "0":
            self.error_message = f"Expected 0 messages from nonexistent sender, got: {count}"
            return False
        
        # Test show with from filter
        exit_code, stdout, stderr = self.run_command("aish inbox show new from nonexistent")
        
        if exit_code != 0:
            self.error_message = f"Show with from filter failed: {stderr}"
            return False
        
        if "No messages in new inbox" not in stdout:
            self.error_message = "Expected 'No messages' for filtered show"
            return False
        
        return True
    
    def teardown(self):
        """Clean up test messages"""
        self.run_command("aish inbox clear new")


class TestInboxClear(AishTest):
    """Test clear command"""
    
    def setup(self):
        """Set up test messages"""
        self.run_command('aish inbox send keep test-ci "Message to clear"')
    
    def test(self) -> bool:
        # Verify message exists
        exit_code, stdout, stderr = self.run_command("aish inbox count keep")
        if exit_code != 0 or stdout.strip() == "0":
            self.error_message = "Test message not found in setup"
            return False
        
        # Clear messages (silent operation)
        exit_code, stdout, stderr = self.run_command("aish inbox clear keep")
        
        if exit_code != 0:
            self.error_message = f"Clear command failed: {stderr}"
            return False
        
        # Should be silent (no output)
        if stdout.strip():
            self.error_message = f"Clear command should be silent, got: '{stdout}'"
            return False
        
        # Verify messages were cleared
        exit_code, stdout, stderr = self.run_command("aish inbox count keep")
        if exit_code != 0:
            self.error_message = "Failed to check count after clear"
            return False
        
        if stdout.strip() != "0":
            self.error_message = f"Messages not cleared, count: {stdout.strip()}"
            return False
        
        return True


class TestInboxErrorHandling(AishTest):
    """Test error handling for invalid commands"""
    
    def test(self) -> bool:
        # Test invalid inbox type
        exit_code, stdout, stderr = self.run_command("aish inbox count invalid")
        
        if exit_code == 0:
            self.error_message = "Should have failed with invalid inbox type"
            return False
        
        if "Invalid inbox type" not in stderr and "Invalid inbox type" not in stdout:
            self.error_message = "Should show invalid inbox type error"
            return False
        
        # Test missing arguments
        exit_code, stdout, stderr = self.run_command("aish inbox send")
        
        if exit_code == 0:
            self.error_message = "Should have failed with missing arguments"
            return False
        
        # Test show with missing type
        exit_code, stdout, stderr = self.run_command("aish inbox show")
        
        if exit_code == 0:
            self.error_message = "Should have failed with missing inbox type"
            return False
        
        return True


def create_suite() -> TestSuite:
    """Create the inbox test suite"""
    suite = TestSuite("Inbox System")
    
    suite.add_test(TestInboxHelp("test_inbox_help", "Test inbox help command"))
    suite.add_test(TestInboxTraining("test_inbox_training", "Test inbox training command"))
    suite.add_test(TestInboxCount("test_inbox_count", "Test inbox count commands"))
    suite.add_test(TestInboxDefault("test_inbox_default", "Test default inbox display"))
    suite.add_test(TestInboxSendShow("test_inbox_send_show", "Test sending and showing messages"))
    suite.add_test(TestInboxJson("test_inbox_json", "Test JSON message format"))
    suite.add_test(TestInboxGet("test_inbox_get", "Test get command (retrieve and remove)"))
    suite.add_test(TestInboxFiltering("test_inbox_filtering", "Test message filtering"))
    suite.add_test(TestInboxClear("test_inbox_clear", "Test clear command"))
    suite.add_test(TestInboxErrorHandling("test_inbox_errors", "Test error handling"))
    
    return suite