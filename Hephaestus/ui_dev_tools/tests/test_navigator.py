"""Test the Navigator tool"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui_dev_tools.tools.navigator import Navigator
from ui_dev_tools.core.models import ToolStatus


async def test_navigate_to_component():
    """Test navigating to a component"""
    print("Testing Navigator.navigate_to_component()...")
    print("-" * 50)
    
    navigator = Navigator()
    
    # Test navigating to rhetor
    result = await navigator.navigate_to_component("rhetor", wait_for_ready=True)
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        data = result.data
        print(f"Component exists in code: {data['component_exists']}")
        print(f"Navigation successful: {data['navigation_success']}")
        print(f"Component ready: {data['component_ready']}")
        print(f"Load method: {data['load_method']}")
        print(f"Current URL: {data['current_url']}")
    else:
        print(f"Error: {result.error}")
    
    return result.status == ToolStatus.SUCCESS


async def test_get_current_component():
    """Test getting current component"""
    print("\n\nTesting Navigator.get_current_component()...")
    print("-" * 50)
    
    navigator = Navigator()
    
    # First navigate to rhetor
    await navigator.navigate_to_component("rhetor")
    
    # Now check current component
    result = await navigator.get_current_component()
    
    print(f"Status: {result.status.value}")
    
    if result.status in [ToolStatus.SUCCESS, ToolStatus.WARNING]:
        data = result.data
        print(f"Current component: {data.get('current_component', 'None')}")
        print(f"Loaded components: {data.get('loaded_components', [])}")
        print(f"Current URL: {data.get('current_url', 'N/A')}")
    
    return result.status in [ToolStatus.SUCCESS, ToolStatus.WARNING]


async def test_list_navigable_components():
    """Test listing navigable components"""
    print("\n\nTesting Navigator.list_navigable_components()...")
    print("-" * 50)
    
    navigator = Navigator()
    
    result = await navigator.list_navigable_components()
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        data = result.data
        print(f"Components in code: {data['total_components']}")
        print(f"Available: {', '.join(data['available_in_code'][:5])}...")
        
        if data.get('available_in_nav'):
            print(f"In navigation UI: {len(data['available_in_nav'])} components")
        
        if 'discrepancies' in data:
            disc = data['discrepancies']
            if disc.get('in_code_only'):
                print(f"In code but not nav: {disc['in_code_only']}")
            if disc.get('in_nav_only'):
                print(f"In nav but not code: {disc['in_nav_only']}")
    
    return result.status == ToolStatus.SUCCESS


async def test_navigate_to_missing_component():
    """Test navigating to non-existent component"""
    print("\n\nTesting navigation to missing component...")
    print("-" * 50)
    
    navigator = Navigator()
    
    result = await navigator.navigate_to_component("nonexistent")
    
    print(f"Status: {result.status.value}")
    print(f"Error: {result.error}")
    print(f"Component exists: {result.data.get('component_exists', False)}")
    
    return result.status == ToolStatus.ERROR  # Should error for missing component


async def test_navigation_sequence():
    """Test navigating between multiple components"""
    print("\n\nTesting navigation sequence...")
    print("-" * 50)
    
    navigator = Navigator()
    components_to_test = ["rhetor", "athena", "hermes"]
    success_count = 0
    
    for component in components_to_test:
        print(f"\nNavigating to {component}...")
        result = await navigator.navigate_to_component(component, wait_for_ready=True)
        
        if result.status == ToolStatus.SUCCESS:
            print(f"  ✓ Successfully loaded {component}")
            success_count += 1
            
            # Check if it's the current component
            current_result = await navigator.get_current_component()
            if current_result.status == ToolStatus.SUCCESS:
                current = current_result.data.get('current_component')
                if current == component:
                    print(f"  ✓ Confirmed as current component")
                else:
                    print(f"  ⚠ Current component mismatch: expected {component}, got {current}")
        else:
            print(f"  ✗ Failed to load {component}: {result.error}")
    
    print(f"\nSuccessfully navigated to {success_count}/{len(components_to_test)} components")
    return success_count > 0


async def main():
    """Run all tests"""
    print("Running Navigator tests...")
    print("NOTE: This requires Hephaestus to be running on localhost:8080\n")
    
    navigator = None
    try:
        tests = [
            test_navigate_to_component,
            test_get_current_component,
            test_list_navigable_components,
            test_navigate_to_missing_component,
            test_navigation_sequence
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
            
    finally:
        # Clean up
        if navigator:
            await navigator.cleanup()


if __name__ == "__main__":
    # Enable some logging
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    asyncio.run(main())