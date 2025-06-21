#!/usr/bin/env python3
"""
Simple script for testing the CodeReader tool
Run this from the Hephaestus directory: python ui_dev_tools/try_code_reader.py
"""
import sys
from pathlib import Path

# Add ui_dev_tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_dev_tools.tools.code_reader import CodeReader
from ui_dev_tools.core.models import ToolStatus


def main():
    """Try out the CodeReader tool"""
    print("=== CodeReader Tool Test ===\n")
    
    # Initialize the tool
    reader = CodeReader()
    
    # 1. List available components
    print("1. Listing all available components:")
    result = reader.list_components()
    if result.status == ToolStatus.SUCCESS:
        components = result.data['components']
        print(f"   Found {len(components)} components: {', '.join(components[:5])}...")
    else:
        print(f"   Error: {result.error}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. Read the rhetor component
    print("2. Reading rhetor component:")
    result = reader.read_component("rhetor")
    if result.status == ToolStatus.SUCCESS:
        data = result.data
        print(f"   File: {data['file_path']}")
        print(f"   Size: {data['content_size']} bytes")
        print(f"   Semantic tags: {data['semantic_tags']['total_count']}")
    else:
        print(f"   Error: {result.error}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. Get detailed semantic tag analysis
    print("3. Analyzing semantic tags in rhetor:")
    result = reader.list_semantic_tags("rhetor")
    if result.status == ToolStatus.SUCCESS:
        summary = result.data['summary']
        print(f"   Total tags: {summary['total_tags']}")
        print(f"   Unique tag types: {summary['unique_tag_types']}")
        print("\n   Tag breakdown:")
        
        # Show tag counts
        tags = result.data['semantic_tags']['by_name']
        for tag_name, occurrences in sorted(tags.items()):
            print(f"     data-tekton-{tag_name}: {len(occurrences)} occurrences")
            # Show first value as example
            if occurrences:
                print(f"       Example: '{occurrences[0]['value']}'")
    else:
        print(f"   Error: {result.error}")
    
    print("\n" + "="*50 + "\n")
    
    # 4. Get component structure
    print("4. Getting rhetor component structure:")
    result = reader.get_component_structure("rhetor")
    if result.status == ToolStatus.SUCCESS:
        data = result.data
        print(f"   Has component root: {data['has_component_root']}")
        structure = data['structure']
        if 'attributes' in structure:
            print(f"   Root element: <{structure['tag']}>")
            print("   Root semantic attributes:")
            for attr, value in structure['attributes'].items():
                if attr.startswith('data-tekton-'):
                    print(f"     {attr}='{value}'")
    else:
        print(f"   Error: {result.error}")
    
    print("\n" + "="*50 + "\n")
    
    # 5. Try a non-existent component
    print("5. Testing error handling with non-existent component:")
    result = reader.read_component("does-not-exist")
    print(f"   Status: {result.status.value}")
    print(f"   Error: {result.error}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()