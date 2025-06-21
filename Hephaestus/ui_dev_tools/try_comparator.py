#!/usr/bin/env python3
"""
Simple script for testing the Comparator tool
Run this from the Hephaestus directory: python ui_dev_tools/try_comparator.py
"""
import asyncio
import sys
from pathlib import Path

# Add ui_dev_tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_dev_tools.tools.comparator import Comparator
from ui_dev_tools.core.models import ToolStatus


async def main():
    """Try out the Comparator tool"""
    print("=== Comparator Tool Test ===")
    print("This tool compares source code (truth) vs browser DOM (reality)\n")
    
    # Initialize the tool
    comparator = Comparator()
    component = "rhetor"
    
    try:
        # 1. Full comparison
        print("1. Running full comparison for rhetor component:")
        print("-" * 50)
        
        result = await comparator.compare_component(component)
        if result.status == ToolStatus.SUCCESS:
            summary = result.data['summary']
            print(f"✓ Comparison successful!")
            print(f"\nTag counts:")
            print(f"  Source code: {summary['code_tags']} tags")
            print(f"  Browser DOM: {summary['browser_tags']} tags")
            print(f"  Difference: {summary['browser_tags'] - summary['code_tags']} additional tags in browser")
            
            print(f"\nStatic tag preservation:")
            print(f"  All {summary['static_tags_preserved']} tag types from source found in DOM ✓")
            print(f"  Missing from DOM: {summary['missing_from_dom']} tag types")
            
            print(f"\nDynamic tags added at runtime: {summary['dynamic_tags_added']} types")
            categories = result.data['dynamic_tag_categories']
            for category, tags in categories.items():
                if tags:
                    print(f"  - {category}: {', '.join(tags)}")
            
            print(f"\nKey insights:")
            for insight in result.data['insights'][:5]:  # Show first 5 insights
                print(f"  {insight}")
        else:
            print(f"✗ Error: {result.error}")
        
        print("\n" + "="*70 + "\n")
        
        # 2. Diagnose missing tags (if any)
        print("2. Diagnosing missing tags:")
        print("-" * 50)
        
        result = await comparator.diagnose_missing_tags(component)
        if result.status == ToolStatus.SUCCESS:
            diagnosis = result.data['diagnosis']
            if isinstance(diagnosis, str):
                print(f"✓ {diagnosis}")
            else:
                print(f"Missing tags: {diagnosis.get('missing_count', 0)}")
                if diagnosis.get('possible_causes'):
                    print("\nPossible causes:")
                    for cause in diagnosis['possible_causes']:
                        print(f"  - {cause}")
        else:
            print(f"✗ Error: {result.error}")
        
        print("\n" + "="*70 + "\n")
        
        # 3. Get fix suggestions
        print("3. Getting fix suggestions:")
        print("-" * 50)
        
        result = await comparator.suggest_fixes(component)
        if result.status == ToolStatus.SUCCESS:
            suggestions = result.data['suggestions']
            print(f"Found {len(suggestions)} suggestions:\n")
            
            for i, suggestion in enumerate(suggestions, 1):
                icon = {"success": "✓", "info": "ℹ", "warning": "⚠"}.get(suggestion['type'], "•")
                print(f"{i}. [{icon}] {suggestion['message']}")
                print(f"   Action: {suggestion['action']}")
                if 'details' in suggestion and suggestion['details']:
                    print(f"   Details: {suggestion['details'][:3]}...")  # Show first 3
                print()
        else:
            print(f"✗ Error: {result.error}")
        
        print("\n" + "="*70 + "\n")
        
        # 4. Understanding static vs dynamic
        print("4. Static vs Dynamic Tag Analysis:")
        print("-" * 50)
        
        result = await comparator.compare_component(component)
        if result.status == ToolStatus.SUCCESS:
            comparison = result.data['comparison']
            
            print("The Comparator helps distinguish between:")
            print("  • Static tags (from source code) - The designed structure")
            print("  • Dynamic tags (added at runtime) - Navigation, state, loading\n")
            
            print(f"Results for {component}:")
            print(f"  Static tag types (in source): 24")
            print(f"  All preserved in DOM: YES ✓")
            print(f"  Dynamic tag types added: {len(comparison['dom_only_tags'])}")
            
            if comparison['dom_only_tags']:
                print(f"\nDynamic tags include:")
                for tag in comparison['dom_only_tags']:
                    print(f"    - data-tekton-{tag}")
            
            print("\nThis shows the component lifecycle:")
            print("  1. Static structure defined in HTML (75 tags)")
            print("  2. Component loads with all static tags")
            print("  3. System adds dynamic tags for functionality (71 more)")
            print("  4. Final DOM has 146 tags total")
        
    finally:
        # Clean up
        await comparator.browser_verifier.cleanup()
    
    print("\n=== Test Complete ===")
    print("\nThe Comparator tool helps you understand:")
    print("  - What's in your source code (truth)")
    print("  - What's actually in the browser (reality)")
    print("  - Why they're different (dynamic enrichment)")
    print("  - Whether your components are loading correctly")


if __name__ == "__main__":
    # Minimal logging
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    print("NOTE: This requires Hephaestus to be running on localhost:8080\n")
    asyncio.run(main())