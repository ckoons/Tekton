#!/usr/bin/env python3
"""
Basic functional tests for aish commands
"""

from .test_runner import AishTest, TestSuite


class TestHelp(AishTest):
    """Test aish help command"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish")
        
        # Check that help is displayed
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Check for expected content
        expected = ["aish - AI Shell", "Usage:", "Quick Start:"]
        for text in expected:
            if text not in stdout:
                self.error_message = f"Expected '{text}' in output"
                return False
        
        return True


class TestListCommands(AishTest):
    """Test aish list commands"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish list commands")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Check for major command sections
        expected_sections = ["CORE COMMANDS:", "FORWARDING:", "PURPOSE:", "PROJECTS:"]
        for section in expected_sections:
            if section not in stdout:
                self.error_message = f"Missing section: {section}"
                return False
        
        return True


class TestList(AishTest):
    """Test aish list"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish list")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Check for AI components
        if "Available AI Components:" not in stdout:
            self.error_message = "Missing AI components header"
            return False
        
        # Check for some known AIs
        expected_ais = ["numa", "apollo", "athena"]
        for ai in expected_ais:
            if ai not in stdout.lower():
                self.error_message = f"Missing AI: {ai}"
                return False
        
        return True


class TestWhoami(AishTest):
    """Test aish whoami"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish whoami")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Should return terminal name or "Not in terma"
        output = stdout.strip()
        if not output:
            self.error_message = "No output from whoami"
            return False
        
        return True


class TestStatus(AishTest):
    """Test aish status"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish status")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Check for expected sections
        expected = ["aish Status Report", "Active AI Forwards:", "AI Components:"]
        for text in expected:
            if text not in stdout:
                self.error_message = f"Missing section: {text}"
                return False
        
        return True


class TestStatusJson(AishTest):
    """Test aish status json"""
    
    def test(self) -> bool:
        exit_code, stdout, stderr = self.run_command("aish status json")
        
        if exit_code != 0:
            self.error_message = f"Exit code {exit_code}, expected 0"
            return False
        
        # Check that output is valid JSON
        try:
            import json
            data = json.loads(stdout)
            
            # Check for expected keys
            expected_keys = ["ai_forwards", "project_forwards", "ai_status"]
            for key in expected_keys:
                if key not in data:
                    self.error_message = f"Missing JSON key: {key}"
                    return False
            
        except json.JSONDecodeError as e:
            self.error_message = f"Invalid JSON output: {e}"
            return False
        
        return True


def create_suite() -> TestSuite:
    """Create the basic test suite"""
    suite = TestSuite("Basic Commands")
    
    suite.add_test(TestHelp("test_help", "Test aish help display"))
    suite.add_test(TestListCommands("test_list_commands", "Test command listing"))
    suite.add_test(TestList("test_list", "Test AI component listing"))
    suite.add_test(TestWhoami("test_whoami", "Test terminal identification"))
    suite.add_test(TestStatus("test_status", "Test status display"))
    suite.add_test(TestStatusJson("test_status_json", "Test JSON status output"))
    
    return suite