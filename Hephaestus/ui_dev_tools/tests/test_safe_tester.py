"""Test the SafeTester tool"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui_dev_tools.tools.safe_tester import SafeTester
from ui_dev_tools.core.models import ToolStatus


async def test_preview_change():
    """Test previewing changes"""
    print("Testing SafeTester.preview_change()...")
    print("-" * 50)
    
    tester = SafeTester()
    
    # Define some test changes
    changes = [
        {
            "type": "text",
            "selector": "[data-tekton-action='send-message']",
            "content": "Send Test Message"
        },
        {
            "type": "attribute",
            "selector": "[data-tekton-component='rhetor']",
            "name": "data-tekton-test",
            "value": "true"
        }
    ]
    
    result = await tester.preview_change("rhetor", changes)
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        data = result.data
        print(f"Preview mode: {data['preview_mode']}")
        print(f"Changes to preview: {data['changes']}")
        print(f"Would break: {data['would_break']}")
        
        print("\nPreview results:")
        for i, preview in enumerate(data['preview_results'], 1):
            print(f"  Change {i}: {preview['change_type']} on {preview['selector']}")
            print(f"    Description: {preview['description']}")
            print(f"    Impact: {preview['impact']}")
            if preview.get('elements_affected'):
                print(f"    Elements affected: {preview['elements_affected']}")
    
    return result.status == ToolStatus.SUCCESS


async def test_validate_change():
    """Test validating changes"""
    print("\n\nTesting SafeTester.validate_change()...")
    print("-" * 50)
    
    tester = SafeTester()
    
    # Test both safe and unsafe changes
    changes = [
        # Safe change
        {
            "type": "text",
            "selector": ".button-text",
            "content": "New Text"
        },
        # Potentially unsafe change
        {
            "type": "element",
            "selector": "[data-tekton-component]",
            "action": "remove"
        },
        # Medium risk change
        {
            "type": "attribute",
            "selector": "[data-tekton-area]",
            "name": "data-tekton-area",
            "value": "modified"
        }
    ]
    
    result = await tester.validate_change("rhetor", changes)
    
    print(f"Status: {result.status.value}")
    
    if result.status in [ToolStatus.SUCCESS, ToolStatus.WARNING]:
        data = result.data
        print(f"Changes validated: {data['changes_validated']}")
        print(f"All safe: {data['all_safe']}")
        print(f"Critical issues: {data['critical_issues']}")
        print(f"Recommendation: {data['recommendation']}")
        
        print("\nValidation details:")
        for i, validation in enumerate(data['validations'], 1):
            print(f"  Change {i}: {validation['change_type']}")
            print(f"    Safe: {validation['safe']}")
            print(f"    Severity: {validation['severity']}")
            if validation['issues']:
                print(f"    Issues: {', '.join(validation['issues'])}")
    
    return result.status in [ToolStatus.SUCCESS, ToolStatus.WARNING]


async def test_sandbox():
    """Test changes in sandbox"""
    print("\n\nTesting SafeTester.test_in_sandbox()...")
    print("-" * 50)
    
    tester = SafeTester()
    
    # Simple safe changes for sandbox testing
    changes = [
        {
            "type": "text",
            "selector": "[data-tekton-action]",
            "content": "Sandbox Test"
        }
    ]
    
    result = await tester.test_in_sandbox("rhetor", changes)
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        data = result.data
        print(f"Sandbox mode: {data['sandbox_mode']}")
        print(f"Changes applied: {data['changes_applied']}/{data['changes_requested']}")
        print(f"Changes failed: {data['changes_failed']}")
        
        if data['validation']:
            print(f"Validation: Safe={data['validation']['safe']}")
            if data['validation']['issues']:
                print(f"Issues: {data['validation']['issues']}")
    
    return result.status == ToolStatus.SUCCESS


async def test_rollback():
    """Test rollback functionality"""
    print("\n\nTesting SafeTester.rollback_changes()...")
    print("-" * 50)
    
    tester = SafeTester()
    
    # First try rollback with no changes
    result = await tester.rollback_changes("rhetor")
    
    print(f"Status: {result.status.value}")
    if result.warnings:
        print(f"Warnings: {result.warnings}")
    
    return result.status in [ToolStatus.SUCCESS, ToolStatus.WARNING]


async def test_dangerous_changes():
    """Test detection of dangerous changes"""
    print("\n\nTesting dangerous change detection...")
    print("-" * 50)
    
    tester = SafeTester()
    
    # Dangerous changes that should be caught
    dangerous_changes = [
        {
            "type": "element",
            "selector": "*",  # Too broad
            "action": "remove"
        },
        {
            "type": "attribute",
            "selector": "body",  # Affects entire page
            "name": "class",
            "value": ""
        }
    ]
    
    result = await tester.validate_change("rhetor", dangerous_changes)
    
    print(f"Status: {result.status.value}")
    
    if result.data:
        print(f"All safe: {result.data['all_safe']}")
        print(f"Critical issues: {result.data['critical_issues']}")
        print(f"Recommendation: {result.data['recommendation']}")
    
    # Should NOT be safe
    return result.data and not result.data['all_safe']


async def main():
    """Run all tests"""
    print("Running SafeTester tests...")
    print("NOTE: This requires Hephaestus to be running on localhost:8080\n")
    
    tests = [
        test_preview_change,
        test_validate_change,
        test_sandbox,
        test_rollback,
        test_dangerous_changes
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