"""Test the CodeReader tool"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui_dev_tools.tools.code_reader import CodeReader
from ui_dev_tools.core.models import ToolStatus


def test_read_component():
    """Test reading a component"""
    print("Testing CodeReader.read_component()...")
    
    reader = CodeReader()
    result = reader.read_component("rhetor")
    
    print(f"Status: {result.status.value}")
    print(f"Component: {result.component}")
    
    if result.status == ToolStatus.SUCCESS:
        print(f"File exists: {result.data['exists']}")
        print(f"Content size: {result.data['content_size']} bytes")
        if result.data.get('semantic_tags'):
            print(f"Semantic tags found: {result.data['semantic_tags']['total_count']}")
    else:
        print(f"Error: {result.error}")
    
    return result.status == ToolStatus.SUCCESS


def test_list_semantic_tags():
    """Test listing semantic tags"""
    print("\n\nTesting CodeReader.list_semantic_tags()...")
    
    reader = CodeReader()
    result = reader.list_semantic_tags("rhetor")
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        summary = result.data['summary']
        print(f"Total tags: {summary['total_tags']}")
        print(f"Unique tag types: {summary['unique_tag_types']}")
        print(f"Tag types: {', '.join(summary['tag_types'][:5])}...")
    
    return result.status == ToolStatus.SUCCESS


def test_get_component_structure():
    """Test getting component structure"""
    print("\n\nTesting CodeReader.get_component_structure()...")
    
    reader = CodeReader()
    result = reader.get_component_structure("rhetor")
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        print(f"Has component root: {result.data['has_component_root']}")
        structure = result.data['structure']
        print(f"Root tag: {structure.get('tag', 'N/A')}")
        if 'attributes' in structure:
            print(f"Root attributes: {list(structure['attributes'].keys())}")
    
    return result.status == ToolStatus.SUCCESS


def test_list_components():
    """Test listing all components"""
    print("\n\nTesting CodeReader.list_components()...")
    
    reader = CodeReader()
    result = reader.list_components()
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        print(f"Components found: {result.data['count']}")
        print(f"Components: {', '.join(result.data['components'][:5])}...")
    
    return result.status == ToolStatus.SUCCESS


def test_missing_component():
    """Test handling missing component"""
    print("\n\nTesting missing component handling...")
    
    reader = CodeReader()
    result = reader.read_component("nonexistent")
    
    print(f"Status: {result.status.value}")
    print(f"Error: {result.error}")
    
    return result.status == ToolStatus.ERROR


def test_result_serialization():
    """Test that results can be serialized to JSON"""
    print("\n\nTesting result serialization...")
    
    reader = CodeReader()
    result = reader.list_semantic_tags("rhetor")
    
    try:
        json_str = json.dumps(result.to_dict(), indent=2)
        print("✓ Result successfully serialized to JSON")
        print(f"JSON size: {len(json_str)} bytes")
        return True
    except Exception as e:
        print(f"✗ Failed to serialize: {e}")
        return False


if __name__ == "__main__":
    print("Running CodeReader tests...\n")
    
    tests = [
        test_read_component,
        test_list_semantic_tags,
        test_get_component_structure,
        test_list_components,
        test_missing_component,
        test_result_serialization
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✓ {test.__name__} passed")
            else:
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            print(f"✗ {test.__name__} crashed: {e}")
    
    print(f"\n\nTest Summary: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")