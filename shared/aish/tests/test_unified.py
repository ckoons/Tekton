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
        
        # Check for new terminal sections
        if "Terminals (terma):" not in stdout and "CI Terminals" not in stdout:
            self.error_message = "Output missing Terminal sections"
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
            
            # Check all entries are terminals (either terma terminals or ci_terminal type)
            # Handle both list and dict formats
            if isinstance(data, list):
                items = data
            else:
                items = data.values()
                
            for ci in items:
                ci_type = ci.get('type')
                name = ci.get('name', 'unknown')
                if ci_type not in ['terminal', 'ci_terminal', 'terma_terminal']:
                    self.error_message = f"Non-terminal CI in filtered output: {name} (type: {ci_type})"
                    return False
                
                # Only terma terminals should have terma_route format
                if ci_type in ['terminal', 'terma_terminal']:
                    if ci.get('message_format') != 'terma_route':
                        self.error_message = f"Terminal {name} missing terma_route format"
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


class CITypeSectionsTest(AishTest):
    """Test that new CI type sections appear correctly"""
    
    def test(self) -> bool:
        """Run the test"""
        import os
        aish_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aish')
        code, stdout, stderr = self.run_command(f"{aish_path} list")
        
        if code != 0:
            self.error_message = f"Command failed with code {code}: {stderr}"
            return False
        
        # Check for proper ordering and sections
        sections = ["Greek Chorus CIs:", "CI Tools:", "CI Terminals", "Terminals (terma):", "Project CIs:"]
        last_pos = -1
        
        for section in sections:
            # Some sections might not exist if no items
            if section in stdout:
                pos = stdout.find(section)
                if pos <= last_pos:
                    self.error_message = f"Section {section} is out of order"
                    return False
                last_pos = pos
        
        return True


class CIToolTypeTest(AishTest):
    """Test filtering for ci_tool type"""
    
    def test(self) -> bool:
        """Run the test"""
        import json
        import os
        
        aish_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aish')
        
        # First check if any ci_tools exist
        code, stdout, stderr = self.run_command(f"{aish_path} list json")
        if code != 0:
            self.error_message = f"Command failed: {stderr}"
            return False
        
        try:
            data = json.loads(stdout)
            # Check for any ci_tool or wrapped_ci entries
            has_tools = any(ci.get('type') in ['ci_tool', 'wrapped_ci'] for ci in data.values())
            
            if has_tools:
                # Verify they appear in the right section
                code, stdout, stderr = self.run_command(f"{aish_path} list")
                if "CI Tools:" in stdout or "CI Tools (wrapped processes):" in stdout:
                    return True
                else:
                    self.error_message = "CI tools exist but not shown in CI Tools section"
                    return False
            
            # No tools exist, which is okay
            return True
            
        except json.JSONDecodeError as e:
            self.error_message = f"Invalid JSON: {e}"
            return False


class RegistrationTest(AishTest):
    """Test CI registration and unregistration"""
    
    def test(self) -> bool:
        """Run the test"""
        import tempfile
        import os
        import sys
        
        # Create a test script that uses the registry
        test_script = '''
import sys
import os
# Add the Coder-C root to path
sys.path.insert(0, "/Users/cskoons/projects/github/Coder-C")
from shared.aish.src.registry.ci_registry import get_registry

registry = get_registry()

# Test registration
test_ci = {
    "name": "test-ci-reg",
    "type": "ci_tool",
    "socket": "/tmp/ci_msg_test-ci-reg.sock",
    "working_directory": "/tmp",
    "capabilities": ["messaging"]
}

# Register
if not registry.register_wrapped_ci(test_ci):
    print("Registration failed")
    sys.exit(1)

# Check it exists
if not registry.get_by_name("test-ci-reg"):
    print("CI not found after registration")
    sys.exit(1)

# Unregister
if not registry.unregister_wrapped_ci("test-ci-reg"):
    print("Unregistration failed")
    sys.exit(1)

# Check it's gone
if registry.get_by_name("test-ci-reg"):
    print("CI still exists after unregistration")
    sys.exit(1)

print("Registration test passed")
'''
        
        # Write and run test script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            temp_file = f.name
        
        try:
            code, stdout, stderr = self.run_command(f"python3 {temp_file}")
            
            if code != 0:
                self.error_message = f"Registration test failed: {stdout} {stderr}"
                return False
            
            if "Registration test passed" not in stdout:
                self.error_message = "Registration test didn't complete"
                return False
            
            return True
            
        finally:
            os.unlink(temp_file)


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
    
    suite.add_test(CITypeSectionsTest(
        "ci_type_sections",
        "Test new CI type sections appear in correct order"
    ))
    
    suite.add_test(CIToolTypeTest(
        "ci_tool_type",
        "Test CI tool type filtering and display"
    ))
    
    suite.add_test(RegistrationTest(
        "registration",
        "Test CI registration and unregistration"
    ))
    
    return suite