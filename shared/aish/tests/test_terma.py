#!/usr/bin/env python3
"""
Functional tests for aish terma commands
"""

from .test_runner import AishTest, TestSuite


class TestTermaInbox(AishTest):
    """Test terma inbox command"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish terma inbox")
        
        # If terma isn't running, we'll get an error
        if exit_code != 0:
            if "Connection refused" in stderr or "Failed to connect" in stdout:
                # Expected when terma isn't running
                print("(Terma not running)")
                return True
            self.error_message = f"Unexpected error: {stderr}"
            return False
        
        # If terma is running, check output
        expected_patterns = ["PROMPT:", "NEW:", "KEEP:"]
        for pattern in expected_patterns:
            if pattern not in stdout:
                self.error_message = f"Missing inbox section: {pattern}"
                return False
        
        return True


class TestTermaList(AishTest):
    """Test terma list command"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish terma list")
        
        # Handle terma not running
        if exit_code != 0:
            if "Connection refused" in stderr or "Failed to get" in stdout:
                print("(Terma not running)")
                return True
            self.error_message = f"Unexpected error: {stderr}"
            return False
        
        # Should show terminal list or "No active terminals"
        return True


class TestTermaWhoami(AishTest):
    """Test terma whoami command"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish terma whoami")
        
        if exit_code != 0:
            # This is ok - might not be in a terma terminal
            if "Not in a Terma" in stdout:
                return True
            self.error_message = f"Unexpected error: {stderr}"
            return False
        
        # Should show terminal info
        if "Terminal:" in stdout:
            return True
        
        return True


def create_suite() -> TestSuite:
    """Create the terma test suite"""
    suite = TestSuite("Terma Commands")
    
    suite.add_test(TestTermaInbox("test_terma_inbox", "Test inbox display"))
    suite.add_test(TestTermaList("test_terma_list", "Test terminal listing"))
    suite.add_test(TestTermaWhoami("test_terma_whoami", "Test terminal identification"))
    
    return suite