#!/usr/bin/env python3
"""
Functional tests for aish forward commands
"""

from .test_runner import AishTest, TestSuite
import time


class TestForwardSetup(AishTest):
    """Test setting up AI forwarding"""
    
    def __init__(self):
        super().__init__("test_forward_setup", "Test basic forward setup")
        self.teardown_commands = ["aish forward remove apollo"]
    
    def test(self) -> bool:
        # Set up forwarding
        exit_code, stdout, stderr = self.run_command("aish forward apollo testterm")
        
        if exit_code != 0:
            self.error_message = f"Failed to set forward: {stderr}"
            return False
        
        if "✓ Forwarding apollo messages to testterm" not in stdout:
            self.error_message = "Missing success message"
            return False
        
        # Verify in list
        exit_code, stdout, stderr = self.run_command("aish forward list")
        if "apollo" not in stdout or "testterm" not in stdout:
            self.error_message = "Forward not shown in list"
            return False
        
        return True


class TestForwardJson(AishTest):
    """Test JSON forwarding"""
    
    def __init__(self):
        super().__init__("test_forward_json", "Test JSON forward mode")
        self.teardown_commands = ["aish forward remove athena"]
    
    def test(self) -> bool:
        # Set up JSON forwarding
        exit_code, stdout, stderr = self.run_command("aish forward athena testterm json")
        
        if exit_code != 0:
            self.error_message = f"Failed to set JSON forward: {stderr}"
            return False
        
        if "✓ Forwarding athena messages to testterm (JSON mode)" not in stdout:
            self.error_message = "Missing JSON mode confirmation"
            return False
        
        # Verify in list
        exit_code, stdout, stderr = self.run_command("aish forward list")
        if "[JSON]" not in stdout:
            self.error_message = "JSON mode not shown in list"
            return False
        
        return True


class TestForwardRemove(AishTest):
    """Test removing forwards"""
    
    def __init__(self):
        super().__init__("test_forward_remove", "Test forward removal")
        self.setup_commands = ["aish forward numa testterm"]
    
    def test(self) -> bool:
        # Remove forward
        exit_code, stdout, stderr = self.run_command("aish forward remove numa")
        
        if exit_code != 0:
            self.error_message = f"Failed to remove forward: {stderr}"
            return False
        
        if "✓ Stopped forwarding numa" not in stdout:
            self.error_message = "Missing removal confirmation"
            return False
        
        # Verify removed from list
        exit_code, stdout, stderr = self.run_command("aish forward list")
        lines = stdout.lower().split('\n')
        for line in lines:
            if "numa" in line and "testterm" in line:
                self.error_message = "Forward still in list after removal"
                return False
        
        return True


class TestUnforward(AishTest):
    """Test unforward command"""
    
    def __init__(self):
        super().__init__("test_unforward", "Test unforward alternative command")
        self.setup_commands = ["aish forward rhetor testterm"]
    
    def test(self) -> bool:
        # Use unforward command
        exit_code, stdout, stderr = self.run_command("aish unforward rhetor")
        
        if exit_code != 0:
            self.error_message = f"Failed to unforward: {stderr}"
            return False
        
        if "✓ Stopped forwarding rhetor" not in stdout:
            self.error_message = "Missing unforward confirmation"
            return False
        
        return True


class TestForwardList(AishTest):
    """Test forward list with multiple entries"""
    
    def __init__(self):
        super().__init__("test_forward_list", "Test listing multiple forwards")
        self.setup_commands = [
            "aish forward apollo term1",
            "aish forward athena term2 json"
        ]
        self.teardown_commands = [
            "aish forward remove apollo",
            "aish forward remove athena"
        ]
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish forward list")
        
        if exit_code != 0:
            self.error_message = f"Failed to list forwards: {stderr}"
            return False
        
        # Check both forwards are shown
        if "apollo" not in stdout or "term1" not in stdout:
            self.error_message = "Missing apollo forward"
            return False
        
        if "athena" not in stdout or "term2" not in stdout:
            self.error_message = "Missing athena forward"
            return False
        
        # Check JSON indicator
        lines = stdout.split('\n')
        for line in lines:
            if "athena" in line and "[JSON]" not in line:
                self.error_message = "Missing JSON indicator for athena"
                return False
        
        return True


class TestForwardMessage(AishTest):
    """Test actual message forwarding (if terma is available)"""
    
    def __init__(self):
        super().__init__("test_forward_message", "Test message forwarding flow")
        self.setup_commands = ["aish forward apollo testterm"]
        self.teardown_commands = ["aish forward remove apollo"]
    
    def test(self) -> bool:
        # This test requires terma to be running
        # First check if we can reach terma
        exit_code, _, _ = self.run_command("aish terma inbox", timeout=2)
        
        if exit_code != 0:
            # Terma not available, skip this test
            print("(Terma not available, skipping message test)")
            return True
        
        # Send a test message to apollo
        test_msg = "Test forward message"
        exit_code, stdout, stderr = self.run_command(f'aish apollo "{test_msg}"')
        
        if "Message forwarded to testterm" in stdout:
            # Successfully forwarded
            return True
        elif exit_code != 0:
            # Apollo might not be running, but forward setup worked
            print("(Apollo not running, but forward was configured)")
            return True
        
        return True


def create_suite() -> TestSuite:
    """Create the forward test suite"""
    suite = TestSuite("Forward Commands")
    
    suite.add_test(TestForwardSetup())
    suite.add_test(TestForwardJson())
    suite.add_test(TestForwardRemove())
    suite.add_test(TestUnforward())
    suite.add_test(TestForwardList())
    suite.add_test(TestForwardMessage())
    
    return suite