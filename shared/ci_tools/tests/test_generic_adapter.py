#!/usr/bin/env python3
"""
Test Generic CI Tool Adapter.
"""

import json
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.ci_tools.adapters.generic_adapter import GenericAdapter


def test_json_translation():
    """Test JSON input/output translation."""
    print("Testing JSON translation...")
    
    config = {
        'display_name': 'Test Tool',
        'executable': 'test',
        'port': 8500,
        'input_format': 'json',
        'output_format': 'json'
    }
    
    adapter = GenericAdapter('test-tool', config)
    
    # Test input translation
    message = {
        'content': 'Hello, world!',
        'type': 'user',
        'session': 'test-session',
        'context': {'key': 'value'}
    }
    
    translated = adapter.translate_to_tool(message)
    parsed = json.loads(translated.strip())
    
    assert parsed['message'] == 'Hello, world!'
    assert parsed['type'] == 'user'
    assert parsed['session'] == 'test-session'
    assert parsed['context']['key'] == 'value'
    
    # Test output translation - dict response
    tool_output = json.dumps({
        'response': 'Hi there!',
        'type': 'assistant',
        'metadata': {'model': 'test'}
    })
    
    response = adapter.translate_from_tool(tool_output)
    assert response['content'] == 'Hi there!'
    assert response['type'] == 'assistant'
    # The metadata contains the full original data structure
    assert 'metadata' in response['metadata']  # Original structure has 'metadata' field
    assert response['metadata']['metadata']['model'] == 'test'
    
    # Test output translation - alternate field names
    tool_output2 = json.dumps({
        'content': 'Content field',
        'extra': 'data'
    })
    
    response2 = adapter.translate_from_tool(tool_output2)
    assert response2['content'] == 'Content field'
    
    print("✓ JSON translation test passed")


def test_text_translation():
    """Test plain text input/output translation."""
    print("Testing text translation...")
    
    config = {
        'display_name': 'Text Tool',
        'executable': 'test',
        'port': 8501,
        'input_format': 'text',
        'output_format': 'text'
    }
    
    adapter = GenericAdapter('text-tool', config)
    
    # Test input translation
    message = {
        'content': 'Plain text message',
        'type': 'user'
    }
    
    translated = adapter.translate_to_tool(message)
    assert translated == 'Plain text message\n'
    
    # Test output translation
    tool_output = 'Plain text response'
    response = adapter.translate_from_tool(tool_output)
    
    assert response['content'] == 'Plain text response'
    assert response['type'] == 'response'
    assert response['tool'] == 'text-tool'
    
    print("✓ Text translation test passed")


def test_mixed_format_handling():
    """Test handling mixed formats."""
    print("Testing mixed format handling...")
    
    config = {
        'display_name': 'Mixed Tool',
        'executable': 'test',
        'port': 8502,
        'input_format': 'json',
        'output_format': 'json'
    }
    
    adapter = GenericAdapter('mixed-tool', config)
    
    # Test JSON parser receiving plain text
    plain_output = 'This is not JSON'
    response = adapter.translate_from_tool(plain_output)
    
    # Should fall back to plain text
    assert response['content'] == 'This is not JSON'
    assert response['type'] == 'response'
    
    # Test empty output
    empty_response = adapter.translate_from_tool('')
    assert empty_response is None
    
    # Test whitespace-only output
    whitespace_response = adapter.translate_from_tool('   \n\t  ')
    assert whitespace_response is None
    
    print("✓ Mixed format handling test passed")


def test_health_check_commands():
    """Test health check command generation."""
    print("Testing health check commands...")
    
    # Test predefined health checks
    configs = [
        ('version', '--version'),
        ('help', '--help'),
        ('ping', 'ping'),
        ('status', 'status'),
        ('health', 'health'),
        ('custom-check', 'custom-check')  # Custom command
    ]
    
    for check_type, expected_cmd in configs:
        config = {
            'display_name': f'Test {check_type}',
            'executable': 'test',
            'port': 8503,
            'health_check': check_type
        }
        
        adapter = GenericAdapter(f'test-{check_type}', config)
        cmd = adapter.get_health_check_command()
        assert cmd == expected_cmd, f"Expected {expected_cmd}, got {cmd}"
    
    # Test no health check
    config_no_check = {
        'display_name': 'No Check',
        'executable': 'test',
        'port': 8504
    }
    
    adapter_no_check = GenericAdapter('test-no-check', config_no_check)
    assert adapter_no_check.get_health_check_command() is None
    
    print("✓ Health check commands test passed")


def test_response_validation():
    """Test response validation."""
    print("Testing response validation...")
    
    config = {
        'display_name': 'Validation Test',
        'executable': 'test',
        'port': 8505
    }
    
    adapter = GenericAdapter('validation-test', config)
    
    # Valid responses
    valid_responses = [
        {'content': 'Hello'},
        {'content': 'World', 'type': 'response'},
        {'content': '123', 'metadata': {}}
    ]
    
    for response in valid_responses:
        assert adapter.validate_response(response) is True
    
    # Invalid responses
    invalid_responses = [
        None,
        {},
        {'type': 'response'},  # No content
        {'content': ''},  # Empty content
        {'content': None}  # None content
    ]
    
    for response in invalid_responses:
        assert adapter.validate_response(response) is False
    
    print("✓ Response validation test passed")


def test_complex_json_structures():
    """Test handling of complex JSON structures."""
    print("Testing complex JSON structures...")
    
    config = {
        'display_name': 'Complex JSON',
        'executable': 'test',
        'port': 8506,
        'output_format': 'json'
    }
    
    adapter = GenericAdapter('complex-json', config)
    
    # Test nested JSON response
    complex_output = json.dumps({
        'result': {
            'analysis': 'Complete',
            'data': [1, 2, 3],
            'nested': {
                'key': 'value'
            }
        }
    })
    
    response = adapter.translate_from_tool(complex_output)
    # Should return the full JSON as content
    assert '"result"' in response['content']
    assert response['metadata']['result']['analysis'] == 'Complete'
    
    # Test JSON array response
    array_output = json.dumps([1, 2, 3, 4, 5])
    array_response = adapter.translate_from_tool(array_output)
    assert array_response['content'] == '[1, 2, 3, 4, 5]'
    
    print("✓ Complex JSON structures test passed")


def run_all_tests():
    """Run all tests."""
    print("Running Generic Adapter Tests")
    print("=" * 50)
    
    tests = [
        test_json_translation,
        test_text_translation,
        test_mixed_format_handling,
        test_health_check_commands,
        test_response_validation,
        test_complex_json_structures
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