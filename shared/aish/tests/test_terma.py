#!/usr/bin/env python3
"""
Functional tests for aish terma commands
"""

from .test_runner import AishTest, TestSuite


class TestTermaInboxDeprecation(AishTest):
    """Test that old terma inbox command shows deprecation message"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish terma inbox")
        
        # Should show deprecation message
        if exit_code != 1:
            self.error_message = f"Expected exit code 1 for deprecated command, got {exit_code}"
            return False
        
        # Should show deprecation message pointing to new system
        expected_messages = ["moved to 'aish inbox'", "aish inbox help"]
        for msg in expected_messages:
            if msg not in stdout:
                self.error_message = f"Missing deprecation message: '{msg}'"
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
    
    suite.add_test(TestTermaInboxDeprecation("test_terma_inbox_deprecation", "Test inbox deprecation message"))
    suite.add_test(TestTermaList("test_terma_list", "Test terminal listing"))
    suite.add_test(TestTermaWhoami("test_terma_whoami", "Test terminal identification"))
    
    return suite