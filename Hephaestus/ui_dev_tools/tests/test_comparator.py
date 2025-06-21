"""Test the Comparator tool"""
import asyncio
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui_dev_tools.tools.comparator import Comparator
from ui_dev_tools.core.models import ToolStatus


async def test_compare_component():
    """Test full component comparison"""
    print("Testing Comparator.compare_component()...")
    print("-" * 50)
    
    comparator = Comparator()
    result = await comparator.compare_component("rhetor")
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        data = result.data
        summary = data['summary']
        
        print(f"\nSummary:")
        print(f"  Code tags: {summary['code_tags']}")
        print(f"  Browser tags: {summary['browser_tags']}")
        print(f"  Static tags preserved: {summary['static_tags_preserved']}")
        print(f"  Dynamic tags added: {summary['dynamic_tags_added']}")
        print(f"  Missing from DOM: {summary['missing_from_dom']}")
        
        print(f"\nDynamic Tag Categories:")
        categories = data['dynamic_tag_categories']
        for category, tags in categories.items():
            if tags:
                print(f"  {category}: {tags}")
        
        print(f"\nInsights:")
        for insight in data['insights']:
            print(f"  {insight}")
    
    return result.status == ToolStatus.SUCCESS


async def test_diagnose_missing_tags():
    """Test diagnosing missing tags"""
    print("\n\nTesting Comparator.diagnose_missing_tags()...")
    print("-" * 50)
    
    comparator = Comparator()
    result = await comparator.diagnose_missing_tags("rhetor")
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        diagnosis = result.data['diagnosis']
        
        if isinstance(diagnosis, str):
            print(f"Diagnosis: {diagnosis}")
        else:
            print(f"Missing tags: {diagnosis.get('missing_count', 0)}")
            if diagnosis.get('missing_tags'):
                print(f"Missing: {diagnosis['missing_tags']}")
            if diagnosis.get('possible_causes'):
                print("Possible causes:")
                for cause in diagnosis['possible_causes']:
                    print(f"  - {cause}")
    
    return result.status == ToolStatus.SUCCESS


async def test_suggest_fixes():
    """Test suggesting fixes"""
    print("\n\nTesting Comparator.suggest_fixes()...")
    print("-" * 50)
    
    comparator = Comparator()
    result = await comparator.suggest_fixes("rhetor")
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        suggestions = result.data['suggestions']
        
        print(f"Found {len(suggestions)} suggestions:")
        for suggestion in suggestions:
            print(f"\n  [{suggestion['type'].upper()}] {suggestion['message']}")
            print(f"  Action: {suggestion['action']}")
            if 'details' in suggestion:
                print(f"  Details: {suggestion['details']}")
    
    return result.status == ToolStatus.SUCCESS


async def test_component_lifecycle():
    """Test understanding of static vs dynamic tags"""
    print("\n\nTesting Component Lifecycle Understanding...")
    print("-" * 50)
    
    comparator = Comparator()
    result = await comparator.compare_component("rhetor")
    
    if result.status == ToolStatus.SUCCESS:
        comparison = result.data['comparison']
        
        print("Static vs Dynamic Tag Analysis:")
        print(f"  Tag types in source only: {len(comparison['code_only_tags'])}")
        print(f"  Tag types added dynamically: {len(comparison['dom_only_tags'])}")
        print(f"  Tag types in both: {len(comparison['in_both'])}")
        
        if comparison['dom_only_tags']:
            print(f"\nDynamic tags added at runtime:")
            for tag in comparison['dom_only_tags'][:10]:  # Show first 10
                print(f"    - data-tekton-{tag}")
            if len(comparison['dom_only_tags']) > 10:
                print(f"    ... and {len(comparison['dom_only_tags']) - 10} more")
    
    return result.status == ToolStatus.SUCCESS


async def main():
    """Run all tests"""
    print("Running Comparator tests...")
    print("NOTE: This requires Hephaestus to be running on localhost:8080\n")
    
    tests = [
        test_compare_component,
        test_diagnose_missing_tags,
        test_suggest_fixes,
        test_component_lifecycle
    ]
    
    passed = 0
    for test in tests:
        try:
            if await test():
                passed += 1
                print(f"\n✓ {test.__name__} passed")
            else:
                print(f"\n✗ {test.__name__} failed")
        except Exception as e:
            print(f"\n✗ {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n\nTest Summary: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")


if __name__ == "__main__":
    # Enable some logging
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    asyncio.run(main())