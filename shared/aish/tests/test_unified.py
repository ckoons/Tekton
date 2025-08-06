#!/usr/bin/env python3
"""
Functional tests for unified CI registry and messaging
"""

from .test_runner import AishTest, TestSuite


class UnifiedListTest(AishTest):
    """Test basic aish list command"""
    
    def test(self) -> bool:
        """Run the test"""
        # Get the aish path - we're in the tests directory when running
        import os
        aish_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aish')
        code, stdout, stderr = self.run_command(f"{aish_path} list")
        
        if code != 0:
            self.error_message = f"Command failed with code {code}: {stderr}"
            return False
        
        if "Greek Chorus CIs:" not in stdout:
            self.error_message = "Output missing Greek Chorus section"
            return False
        
        if "Terminal CIs:" not in stdout:
            self.error_message = "Output missing Terminal CIs section"
            return False
        
        return True


class UnifiedListTypeTest(AishTest):
    """Test aish list with type filter"""
    
    def test(self) -> bool:
        """Run the test"""
        # Test greek filter
        import os
        aish_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aish')
        code, stdout, stderr = self.run_command(f"{aish_path} list type greek")
        
        if code != 0:
            self.error_message = f"Command failed with code {code}: {stderr}"
            return False
        
        # Count Greek Chorus entries
        greek_count = stdout.count("http://localhost:")
        if greek_count < 10:
            self.error_message = f"Expected at least 10 Greek Chorus CIs, found {greek_count}"
            return False
        
        # Test terminal filter
        code, stdout, stderr = self.run_command(f"{aish_path} list type terminal")
        
        if code != 0:
            self.error_message = f"Terminal filter failed with code {code}: {stderr}"
            return False
        
        return True


class UnifiedListJsonTest(AishTest):
    """Test JSON output"""
    
    def test(self) -> bool:
        """Run the test"""
        import json
        
        # Test basic JSON
        import os
        aish_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aish')
        code, stdout, stderr = self.run_command(f"{aish_path} list json")
        
        if code != 0:
            self.error_message = f"Command failed with code {code}: {stderr}"
            return False
        
        try:
            data = json.loads(stdout)
            if not isinstance(data, dict):
                self.error_message = "JSON output is not a dict"
                return False
            
            # Check for message configuration
            numa = data.get('numa')
            if not numa:
                self.error_message = "numa not found in JSON output"
                return False
            
            if 'message_format' not in numa:
                self.error_message = "message_format field missing from numa"
                return False
            
            if numa['message_format'] != 'json_simple':
                self.error_message = f"Expected json_simple format, got {numa['message_format']}"
                return False
            
        except json.JSONDecodeError as e:
            self.error_message = f"Invalid JSON output: {e}"
            return False
        
        return True


class UnifiedListJsonFilterTest(AishTest):
    """Test JSON output with filter"""
    
    def test(self) -> bool:
        """Run the test"""
        import json
        
        import os
        aish_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aish')
        code, stdout, stderr = self.run_command(f"{aish_path} list json terminal")
        
        if code != 0:
            self.error_message = f"Command failed with code {code}: {stderr}"
            return False
        
        try:
            data = json.loads(stdout)
            
            # Check all entries are terminals
            for ci in data:
                if ci.get('type') != 'terminal':
                    self.error_message = f"Non-terminal CI in filtered output: {ci.get('name')}"
                    return False
                
                if ci.get('message_format') != 'terma_route':
                    self.error_message = f"Terminal {ci.get('name')} missing terma_route format"
                    return False
            
        except json.JSONDecodeError as e:
            self.error_message = f"Invalid JSON output: {e}"
            return False
        
        return True


class UnifiedMessagingTest(AishTest):
    """Test unified messaging to different CI types"""
    
    def test(self) -> bool:
        """Run the test"""
        # Test Greek Chorus messaging
        import os
        aish_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aish')
        code, stdout, stderr = self.run_command(f'{aish_path} numa "test unified message"')
        
        if code != 0:
            self.error_message = f"Failed to send to numa: {stderr}"
            return False
        
        # Should get some response
        if not stdout.strip():
            self.error_message = "No response from numa"
            return False
        
        return True


def create_suite() -> TestSuite:
    """Create the unified test suite"""
    suite = TestSuite("unified")
    
    # Add tests
    suite.add_test(UnifiedListTest(
        "list_all",
        "Test basic aish list command"
    ))
    
    suite.add_test(UnifiedListTypeTest(
        "list_type",
        "Test aish list with type filters"
    ))
    
    suite.add_test(UnifiedListJsonTest(
        "list_json",
        "Test JSON output with message configuration"
    ))
    
    suite.add_test(UnifiedListJsonFilterTest(
        "list_json_filter",
        "Test JSON output with type filter"
    ))
    
    suite.add_test(UnifiedMessagingTest(
        "unified_messaging",
        "Test sending messages through unified system"
    ))
    
    return suite