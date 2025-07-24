#!/usr/bin/env python3
"""
Functional tests for aish route commands
"""

from .test_runner import AishTest, TestSuite
import json


class TestRouteCreate(AishTest):
    """Test creating a route"""
    
    def __init__(self):
        super().__init__("test_route_create", "Test route creation")
        self.teardown_commands = ['aish route remove "testreview"']
    
    def test(self) -> bool:
        # Create a route
        cmd = 'aish route name "testreview" numa purpose "prepare" apollo purpose "analyze" testterm'
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code != 0:
            self.error_message = f"Failed to create route: {stderr}"
            return False
        
        if "Route 'testreview' created:" not in stdout:
            self.error_message = "Missing route creation confirmation"
            return False
        
        # Verify route shows numa → apollo → testterm
        if "numa → apollo → testterm" not in stdout:
            self.error_message = "Route path not shown correctly"
            return False
        
        return True


class TestRouteList(AishTest):
    """Test listing routes"""
    
    def __init__(self):
        super().__init__("test_route_list", "Test route listing")
        self.setup_commands = [
            'aish route name "test1" numa apollo term1',
            'aish route name "test2" athena rhetor term2'
        ]
        self.teardown_commands = [
            'aish route remove "test1"',
            'aish route remove "test2"'
        ]
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish route list")
        
        if exit_code != 0:
            self.error_message = f"Failed to list routes: {stderr}"
            return False
        
        # Check both routes are shown
        if "test1" not in stdout or "test2" not in stdout:
            self.error_message = "Routes not shown in list"
            return False
        
        return True


class TestRouteShow(AishTest):
    """Test showing specific route"""
    
    def __init__(self):
        super().__init__("test_route_show", "Test showing route details")
        self.setup_commands = ['aish route name "testshow" numa purpose "think" apollo testdest']
        self.teardown_commands = ['aish route remove "testshow"']
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command('aish route show "testshow"')
        
        if exit_code != 0:
            self.error_message = f"Failed to show route: {stderr}"
            return False
        
        # Should show route details
        if "numa" not in stdout or "apollo" not in stdout:
            self.error_message = "Route details not shown"
            return False
        
        return True


class TestRouteRemove(AishTest):
    """Test removing a route"""
    
    def __init__(self):
        super().__init__("test_route_remove", "Test route removal")
        self.setup_commands = ['aish route name "testremove" numa apollo term']
    
    def test(self) -> bool:
        # Remove the route
        exit_code, stdout, stderr = self.run_command('aish route remove "testremove"')
        
        if exit_code != 0:
            self.error_message = f"Failed to remove route: {stderr}"
            return False
        
        if "Route 'testremove' removed" not in stdout:
            self.error_message = "Missing removal confirmation"
            return False
        
        # Verify it's gone
        exit_code, stdout, stderr = self.run_command("aish route list")
        if "testremove" in stdout:
            self.error_message = "Route still exists after removal"
            return False
        
        return True


class TestRouteSend(AishTest):
    """Test sending message through route"""
    
    def __init__(self):
        super().__init__("test_route_send", "Test route message sending")
        self.setup_commands = ['aish route name "testsend" numa apollo dest']
        self.teardown_commands = ['aish route remove "testsend"']
    
    def test(self) -> bool:
        # Send a message through the route
        exit_code, stdout, stderr = self.run_command('aish route dest "Test message"')
        
        if exit_code != 0:
            self.error_message = f"Failed to send through route: {stderr}"
            return False
        
        # Output should be JSON
        try:
            data = json.loads(stdout)
            
            # Check JSON structure
            if "message" not in data or data["message"] != "Test message":
                self.error_message = "Message not in JSON output"
                return False
            
            if "dest" not in data or data["dest"] != "dest":
                self.error_message = "Destination not in JSON output"
                return False
            
            # Route info is optional when sending directly to destination
            # The important part is that the message was formatted as JSON
            
        except json.JSONDecodeError:
            self.error_message = "Output is not valid JSON"
            return False
        
        return True


def create_suite() -> TestSuite:
    """Create the route test suite"""
    suite = TestSuite("Route Commands")
    
    suite.add_test(TestRouteCreate())
    suite.add_test(TestRouteList())
    suite.add_test(TestRouteShow())
    suite.add_test(TestRouteRemove())
    suite.add_test(TestRouteSend())
    
    return suite