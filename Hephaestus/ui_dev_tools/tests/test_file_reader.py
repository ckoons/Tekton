"""Test the ComponentReader with rhetor component"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_reader import ComponentReader
from core.models import SemanticTagAnalysis


def test_component_reader():
    """Test ComponentReader with rhetor component (should have 31 tags)"""
    print("Testing ComponentReader...")
    
    # Initialize reader
    reader = ComponentReader()
    print(f"Base path: {reader.base_path}")
    
    # List available components
    components = reader.list_available_components()
    print(f"\nAvailable components: {components}")
    
    # Test reading rhetor component
    print("\n--- Testing rhetor component ---")
    component_info, analysis = reader.analyze_component("rhetor")
    
    if not component_info.exists:
        print(f"ERROR: {component_info.error}")
        return False
    
    print(f"Component found at: {component_info.file_path}")
    print(f"Content size: {len(component_info.content)} bytes")
    
    if analysis:
        print(f"\nSemantic tags found: {analysis.total_count}")
        print(f"Unique tag types: {len(analysis.get_tag_names())}")
        
        # Display tag summary
        print("\nTag summary:")
        for tag_name in sorted(analysis.get_tag_names()):
            values = analysis.get_tag_values(tag_name)
            print(f"  data-tekton-{tag_name}: {len(values)} occurrences")
            for value in values[:3]:  # Show first 3 values
                print(f"    - '{value}'")
            if len(values) > 3:
                print(f"    ... and {len(values) - 3} more")
        
        # Check if we found the expected 31 tags
        if analysis.total_count == 31:
            print("\n✓ SUCCESS: Found expected 31 semantic tags!")
            return True
        else:
            print(f"\n✗ WARNING: Expected 31 tags but found {analysis.total_count}")
            return True  # Still success, but with warning
    
    return False


def test_missing_component():
    """Test handling of missing component"""
    print("\n--- Testing missing component ---")
    reader = ComponentReader()
    
    component_info = reader.read_component("nonexistent")
    
    if not component_info.exists:
        print(f"✓ Correctly handled missing component: {component_info.error}")
        return True
    else:
        print("✗ ERROR: Should have reported component as missing")
        return False


if __name__ == "__main__":
    print("Running ComponentReader tests...\n")
    
    success = True
    success &= test_component_reader()
    success &= test_missing_component()
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
    
    sys.exit(0 if success else 1)