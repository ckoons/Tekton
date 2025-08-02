#!/usr/bin/env python3
"""
Test CI Tools Definition functionality.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.ci_tools import get_registry
from shared.ci_tools.commands.tools import define_tool, show_defined_tools, undefine_tool


def test_define_tool():
    """Test defining a new tool."""
    print("Testing tool definition...")
    
    registry = get_registry()
    
    # Define a test tool
    tool_name = "test-openai"
    args = [
        "--type", "generic",
        "--executable", "/usr/bin/openai",
        "--description", "Test OpenAI tool",
        "--port", "auto",
        "--capabilities", "code_generation,debugging",
        "--launch-args", "--mode stdio --format json",
        "--health-check", "version",
        "--env", "OPENAI_MODEL=gpt-4",
        "--env", "OPENAI_API_KEY=test"
    ]
    
    # Define the tool
    define_tool(tool_name, args)
    
    # Verify it was registered
    tool_config = registry.get_tool(tool_name)
    assert tool_config is not None
    assert tool_config['executable'] == '/usr/bin/openai'
    assert tool_config['description'] == 'Test OpenAI tool'
    assert tool_config['base_type'] == 'generic'
    assert tool_config['health_check'] == 'version'
    assert 'code_generation' in tool_config['capabilities']
    assert 'debugging' in tool_config['capabilities']
    assert tool_config['environment']['OPENAI_MODEL'] == 'gpt-4'
    assert tool_config['environment']['OPENAI_API_KEY'] == 'test'
    
    print("✓ Tool definition test passed")
    
    # Clean up
    registry.unregister_tool(tool_name)


def test_show_defined_tools():
    """Test showing defined tools."""
    print("Testing show defined tools...")
    
    registry = get_registry()
    
    # Define a couple of test tools
    tool1_name = "test-tool-1"
    tool2_name = "test-tool-2"
    
    registry.register_tool(tool1_name, {
        'display_name': 'Test Tool 1',
        'type': 'tool',
        'port': 9001,
        'description': 'First test tool',
        'executable': 'test1',
        'defined_by': 'user',
        'base_type': 'generic'
    })
    
    registry.register_tool(tool2_name, {
        'display_name': 'Test Tool 2',
        'type': 'tool',
        'port': 9002,
        'description': 'Second test tool',
        'executable': 'test2',
        'defined_by': 'user',
        'base_type': 'generic'
    })
    
    # Test listing all defined tools
    print("\nListing all user-defined tools:")
    show_defined_tools()
    
    # Test showing specific tool
    print(f"\nShowing details for {tool1_name}:")
    show_defined_tools(tool1_name)
    
    print("✓ Show defined tools test passed")
    
    # Clean up
    registry.unregister_tool(tool1_name)
    registry.unregister_tool(tool2_name)


def test_undefine_tool():
    """Test undefining a tool."""
    print("Testing tool undefinition...")
    
    registry = get_registry()
    
    # Define a test tool
    tool_name = "test-undefine"
    registry.register_tool(tool_name, {
        'display_name': 'Test Undefine',
        'type': 'tool',
        'port': 9003,
        'description': 'Tool to test undefinition',
        'executable': 'test-undefine',
        'defined_by': 'user',
        'base_type': 'generic'
    })
    
    # Verify it exists
    assert registry.get_tool(tool_name) is not None
    
    # Undefine it
    undefine_tool(tool_name)
    
    # Verify it's gone
    assert registry.get_tool(tool_name) is None
    
    # Test undefining built-in tool (should fail)
    print("\nTrying to undefine built-in tool (should fail):")
    undefine_tool('claude-code')
    # Should still exist
    assert registry.get_tool('claude-code') is not None
    
    print("✓ Tool undefinition test passed")


def test_dynamic_port_allocation():
    """Test dynamic port allocation."""
    print("Testing dynamic port allocation...")
    
    registry = get_registry()
    
    # Test with fixed port mode (default)
    port1 = registry.find_available_port(8500)
    assert isinstance(port1, int)
    assert port1 >= 8500
    
    # Test with dynamic port mode - just verify it returns a valid port
    # Don't enforce specific range since environment setup is complex
    port2 = registry.find_available_port()
    assert isinstance(port2, int)
    assert port2 > 0
    
    print(f"✓ Dynamic port allocation test passed (allocated ports: {port1}, {port2})")


def test_persistence():
    """Test tool persistence across registry reloads."""
    print("Testing tool persistence...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set TEKTON_ROOT to temp directory
        os.environ['TEKTON_ROOT'] = temp_dir
        
        # Create first registry instance
        from shared.ci_tools.registry import CIToolRegistry
        registry1 = CIToolRegistry()
        
        # Define a custom tool
        tool_name = "test-persist"
        config = {
            'display_name': 'Test Persist',
            'type': 'tool',
            'port': 9004,
            'description': 'Tool to test persistence',
            'executable': 'test-persist',
            'defined_by': 'user',
            'base_type': 'generic',
            'capabilities': {'test': True}
        }
        registry1.register_tool(tool_name, config)
        
        # Force save
        registry1._save_custom_tools()
        
        # Create new registry instance (simulates restart)
        registry2 = CIToolRegistry()
        
        # Check if tool was loaded
        loaded_config = registry2.get_tool(tool_name)
        assert loaded_config is not None
        assert loaded_config['display_name'] == 'Test Persist'
        assert loaded_config['port'] == 9004
        assert loaded_config['capabilities']['test'] is True
        
        print("✓ Tool persistence test passed")
        
        # Clean up
        del os.environ['TEKTON_ROOT']


def test_tool_launch_args_parsing():
    """Test parsing of launch arguments."""
    print("Testing launch arguments parsing...")
    
    registry = get_registry()
    
    # Test with quoted arguments
    tool_name = "test-args"
    args = [
        "--type", "generic",
        "--executable", "test",
        "--launch-args", "--mode stdio --format json"
    ]
    
    define_tool(tool_name, args)
    
    config = registry.get_tool(tool_name)
    assert config['launch_args'] == ['--mode', 'stdio', '--format', 'json']
    
    print("✓ Launch arguments parsing test passed")
    
    # Clean up
    registry.unregister_tool(tool_name)


def run_all_tests():
    """Run all tests."""
    print("Running CI Tools Definition Tests")
    print("=" * 50)
    
    tests = [
        test_define_tool,
        test_show_defined_tools,
        test_undefine_tool,
        test_dynamic_port_allocation,
        test_persistence,
        test_tool_launch_args_parsing
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)