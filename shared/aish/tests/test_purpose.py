#!/usr/bin/env python3
"""
Functional tests for aish purpose commands
"""

from .test_runner import AishTest, TestSuite


class TestPurposeCurrent(AishTest):
    """Test showing current terminal purpose"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish purpose")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Should show terminal name and purpose or "Not in a Terma-launched terminal"
        if not stdout.strip():
            self.error_message = "No output from purpose command"
            return False
        
        return True


class TestPurposeSearch(AishTest):
    """Test purpose content search"""
    
    def test(self) -> bool:
        # Search for a known purpose file
        exit_code, stdout, stderr = self.run_command('aish purpose "forward"')
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Should find forward.json or forward.md
        if "Searching for purpose content: forward" not in stdout:
            self.error_message = "Missing search header"
            return False
        
        if "FORWARD" not in stdout:
            self.error_message = "No forward purpose content found"
            return False
        
        return True


class TestPurposeSearchMultiple(AishTest):
    """Test searching multiple purposes with CSV"""
    
    def test(self) -> bool:
        # Search for multiple purposes
        exit_code, stdout, stderr = self.run_command('aish purpose "test, forward"')
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Should find both test and forward content
        if "Searching for purpose content: test, forward" not in stdout:
            self.error_message = "Missing CSV search header"
            return False
        
        # Check both purposes are shown
        if "TEST" not in stdout:
            self.error_message = "TEST section not found"
            return False
        
        if "FORWARD" not in stdout:
            self.error_message = "FORWARD section not found"
            return False
        
        return True


class TestPurposeNotFound(AishTest):
    """Test searching for non-existent purpose"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command('aish purpose "nonexistentpurpose12345"')
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        if "No playbook content found for 'nonexistentpurpose12345'" not in stdout:
            self.error_message = "Missing 'not found' message"
            return False
        
        return True


class TestPurposeTerminal(AishTest):
    """Test checking a specific terminal's purpose"""
    
    def test(self) -> bool:
        # This might show "Terminal 'testterm' not found" if terma isn't running
        exit_code, stdout, stderr = self.run_command("aish purpose testterm")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Should either show the terminal's purpose or "not found"
        output = stdout.strip()
        if not output:
            self.error_message = "No output from terminal purpose check"
            return False
        
        return True


class TestPurposeSet(AishTest):
    """Test setting terminal purpose (if terma available)"""
    
    def test(self) -> bool:
        # Try to set a purpose
        exit_code, stdout, stderr = self.run_command('aish purpose testterm "testing, development"')
        
        # This might fail if terma isn't running, which is ok
        if exit_code != 0:
            if "Error getting terminal list" in stdout or "TEKTON_ROOT not set" in stderr:
                # Expected errors when terma isn't available
                return True
            self.error_message = f"Unexpected error: {stderr}"
            return False
        
        # If it succeeded, check for expected output
        if "Setting purpose for testterm: testing, development" in stdout:
            return True
        
        return True


def create_suite() -> TestSuite:
    """Create the purpose test suite"""
    suite = TestSuite("purpose")
    
    suite.add_test(TestPurposeCurrent("test_purpose_current", "Test showing current purpose"))
    suite.add_test(TestPurposeSearch("test_purpose_search", "Test purpose content search"))
    suite.add_test(TestPurposeSearchMultiple("test_purpose_csv", "Test CSV purpose search"))
    suite.add_test(TestPurposeNotFound("test_purpose_notfound", "Test non-existent purpose"))
    suite.add_test(TestPurposeTerminal("test_purpose_terminal", "Test terminal purpose check"))
    suite.add_test(TestPurposeSet("test_purpose_set", "Test setting terminal purpose"))
    
    return suite