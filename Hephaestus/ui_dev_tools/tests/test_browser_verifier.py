"""Test the BrowserVerifier tool"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui_dev_tools.tools.browser_verifier import BrowserVerifier
from ui_dev_tools.core.models import ToolStatus


async def test_verify_component_loaded():
    """Test verifying if component is loaded"""
    print("Testing BrowserVerifier.verify_component_loaded()...")
    
    verifier = BrowserVerifier()
    
    # Test with rhetor component
    result = await verifier.verify_component_loaded("rhetor")
    
    print(f"Status: {result.status.value}")
    print(f"Component loaded: {result.data.get('loaded', False)}")
    print(f"URL: {result.data.get('url', 'N/A')}")
    
    if result.data.get('component_info'):
        info = result.data['component_info']
        print(f"Component tag: <{info['tagName']}>")
        print(f"Has children: {info['hasChildren']}")
    
    return result.status in [ToolStatus.SUCCESS, ToolStatus.WARNING]


async def test_get_dom_semantic_tags():
    """Test extracting semantic tags from DOM"""
    print("\n\nTesting BrowserVerifier.get_dom_semantic_tags()...")
    
    verifier = BrowserVerifier()
    
    # Test with rhetor component
    result = await verifier.get_dom_semantic_tags("rhetor")
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        data = result.data
        if data.get('semantic_tags'):
            tags = data['semantic_tags']
            print(f"Total tags in DOM: {tags['total_count']}")
            print(f"Unique tag types: {len(tags['found'])}")
            print(f"Tag types found: {', '.join(tags['found'][:5])}...")
            
            # Compare with expected 75 from source
            print(f"\nCOMPARISON: Source has 75 tags, DOM has {tags['total_count']} tags")
            print(f"Missing tags: {75 - tags['total_count']} ({100 * (75 - tags['total_count']) / 75:.1f}% loss)")
    
    if result.warnings:
        print(f"Warnings: {result.warnings}")
    
    return result.status in [ToolStatus.SUCCESS, ToolStatus.WARNING]


async def test_capture_dom_state():
    """Test capturing DOM structure"""
    print("\n\nTesting BrowserVerifier.capture_dom_state()...")
    
    verifier = BrowserVerifier()
    
    # Test with rhetor component
    result = await verifier.capture_dom_state("rhetor")
    
    print(f"Status: {result.status.value}")
    
    if result.status == ToolStatus.SUCCESS:
        data = result.data
        print(f"DOM captured: {data.get('captured', False)}")
        print(f"Total elements in component: {data.get('element_count', 0)}")
        
        if data.get('dom_structure'):
            structure = data['dom_structure']
            print(f"Root element: <{structure['tag']}>")
            if 'attributes' in structure:
                semantic_attrs = [k for k in structure['attributes'] if k.startswith('data-tekton-')]
                print(f"Root semantic attributes: {semantic_attrs}")
    
    return result.status == ToolStatus.SUCCESS


async def test_missing_component():
    """Test handling of missing component"""
    print("\n\nTesting missing component handling...")
    
    verifier = BrowserVerifier()
    
    result = await verifier.verify_component_loaded("nonexistent")
    
    print(f"Status: {result.status.value}")
    print(f"Component loaded: {result.data.get('loaded', False)}")
    
    if result.warnings:
        print(f"Warnings: {result.warnings}")
    
    return True  # Expected to handle gracefully


async def main():
    """Run all tests"""
    print("Running BrowserVerifier tests...")
    print("NOTE: This requires Hephaestus to be running on localhost:8080\n")
    
    verifier = None
    try:
        tests = [
            test_verify_component_loaded,
            test_get_dom_semantic_tags,
            test_capture_dom_state,
            test_missing_component
        ]
        
        passed = 0
        for test in tests:
            try:
                if await test():
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
            
    finally:
        # Clean up browser
        if verifier:
            await verifier.cleanup()


if __name__ == "__main__":
    # Enable logging to see what's happening
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())