#!/usr/bin/env python3
"""
Compare Code (Truth) vs Browser (Reality) for rhetor component
This demonstrates the core philosophy of the new UI DevTools
"""
import asyncio
import sys
from pathlib import Path

# Add ui_dev_tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui_dev_tools.tools.code_reader import CodeReader
from ui_dev_tools.tools.browser_verifier import BrowserVerifier
from ui_dev_tools.core.models import ToolStatus


async def main():
    """Compare source code truth vs browser reality"""
    print("=== UI DevTools: Code (Truth) vs Browser (Reality) ===\n")
    
    component_name = "rhetor"
    
    # 1. Read the source code (TRUTH)
    print("STEP 1: Reading Source Code (The Truth)")
    print("-" * 50)
    
    code_reader = CodeReader()
    code_result = code_reader.list_semantic_tags(component_name)
    
    if code_result.status == ToolStatus.SUCCESS:
        code_tags = code_result.data['semantic_tags']
        code_summary = code_result.data['summary']
        
        print(f"Component: {component_name}")
        print(f"Source file: ui/components/{component_name}/{component_name}-component.html")
        print(f"Total semantic tags in code: {code_summary['total_tags']}")
        print(f"Unique tag types: {code_summary['unique_tag_types']}")
        print(f"\nTag types: {', '.join(sorted(code_summary['tag_types']))}")
        
        # Show top 5 tag types by count
        print("\nTop tag types by count:")
        tag_counts = [(name, len(values)) for name, values in code_tags['by_name'].items()]
        tag_counts.sort(key=lambda x: x[1], reverse=True)
        for name, count in tag_counts[:5]:
            print(f"  - data-tekton-{name}: {count}")
    else:
        print(f"Error reading code: {code_result.error}")
        return
    
    print("\n" + "="*70 + "\n")
    
    # 2. Check the browser (REALITY)
    print("STEP 2: Checking Browser DOM (The Reality)")
    print("-" * 50)
    
    browser_verifier = BrowserVerifier()
    
    try:
        # First verify component loads
        verify_result = await browser_verifier.verify_component_loaded(component_name)
        if verify_result.status != ToolStatus.SUCCESS:
            print(f"Component not loaded in browser: {verify_result.error or verify_result.warnings}")
            return
        
        # Get DOM semantic tags
        browser_result = await browser_verifier.get_dom_semantic_tags(component_name)
        
        if browser_result.status == ToolStatus.SUCCESS:
            browser_tags = browser_result.data['semantic_tags']
            
            print(f"Component loaded: Yes")
            print(f"Total semantic tags in DOM: {browser_tags['total_count']}")
            print(f"Unique tag types in DOM: {len(browser_tags['found'])}")
            print(f"\nTag types found: {', '.join(sorted(browser_tags['found']))}")
            
            # Show top 5 tag types by count
            print("\nTop tag types by count:")
            tag_counts = [(name, count) for name, count in browser_tags['count_by_type'].items()]
            tag_counts.sort(key=lambda x: x[1], reverse=True)
            for name, count in tag_counts[:5]:
                print(f"  - data-tekton-{name}: {count}")
        else:
            print(f"Error checking browser: {browser_result.error}")
            return
            
    finally:
        await browser_verifier.cleanup()
    
    print("\n" + "="*70 + "\n")
    
    # 3. ANALYSIS: Compare Truth vs Reality
    print("STEP 3: Analysis - Truth vs Reality")
    print("-" * 50)
    
    code_tag_names = set(code_summary['tag_types'])
    browser_tag_names = set(browser_tags['found'])
    
    print(f"\nTag Count Comparison:")
    print(f"  Source code: {code_summary['total_tags']} tags")
    print(f"  Browser DOM: {browser_tags['total_count']} tags")
    print(f"  Difference: {browser_tags['total_count'] - code_summary['total_tags']} tags")
    
    print(f"\nTag Type Comparison:")
    print(f"  Source code: {len(code_tag_names)} unique types")
    print(f"  Browser DOM: {len(browser_tag_names)} unique types")
    
    # Find differences
    only_in_code = code_tag_names - browser_tag_names
    only_in_browser = browser_tag_names - code_tag_names
    in_both = code_tag_names & browser_tag_names
    
    if only_in_code:
        print(f"\nTag types ONLY in source code:")
        for tag in sorted(only_in_code):
            print(f"  - data-tekton-{tag}")
    
    if only_in_browser:
        print(f"\nTag types ONLY in browser:")
        for tag in sorted(only_in_browser):
            print(f"  - data-tekton-{tag}")
    
    print(f"\nTag types in BOTH: {len(in_both)}")
    
    # Diagnosis
    print("\n" + "="*70 + "\n")
    print("DIAGNOSIS:")
    
    if browser_tags['total_count'] > code_summary['total_tags']:
        print("✓ Good news: Browser has MORE tags than source!")
        print("  This suggests:")
        print("  - Dynamic tags are being added at runtime")
        print("  - Multiple components may be loaded")
        print("  - The loader is working properly")
    elif browser_tags['total_count'] < code_summary['total_tags']:
        print("✗ Problem: Browser has FEWER tags than source!")
        print("  This suggests:")
        print("  - Some tags are being stripped during loading")
        print("  - Component may not be fully loaded")
        print("  - Sanitization may be removing tags")
    else:
        print("✓ Perfect match: Same number of tags in source and browser")
    
    print("\nThis demonstrates why 'Code is Truth, Browser is Reality' matters!")
    print("The old tools would only check the browser and miss the full picture.")


if __name__ == "__main__":
    # Enable some logging
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    asyncio.run(main())