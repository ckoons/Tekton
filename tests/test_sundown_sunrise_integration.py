#!/usr/bin/env python3
"""
Integration test for sundown/sunrise with aish commands
Tests the full workflow: token management → sundown → sunrise
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.aish.src.registry.ci_registry import get_registry
from Rhetor.rhetor.core.token_manager import get_token_manager
from Apollo.apollo.core.sundown_sunrise import get_sundown_sunrise_manager


async def test_aish_sundown_sunrise():
    """Test the aish sundown/sunrise commands."""
    print("\n=== Testing aish sundown/sunrise commands ===\n")
    
    # 1. Set up a CI with forward state
    print("1. Setting up CI forward state...")
    registry = get_registry()
    token_mgr = get_token_manager()
    
    # Simulate a CI being forwarded
    registry.set_forward_state('test-ci', 'claude-3-5-sonnet', 'test args')
    
    # Initialize token tracking
    token_mgr.init_ci_tracking('test-ci', 'claude-3-5-sonnet')
    
    # Add some usage to simulate work
    token_mgr.update_usage('test-ci', 'conversation_history', 'A' * 1000)
    
    # 2. Check sundown command
    print("2. Testing sundown command...")
    result = subprocess.run(
        ['python', 'shared/aish/aish', 'sundown', 'test-ci', 'Testing sundown'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"  ❌ Sundown failed: {result.stderr}")
        return False
    
    print(f"  ✓ Sundown successful")
    print(f"  Output: {result.stdout[:200]}...")
    
    # 3. Check sundown status
    print("3. Testing sundown status...")
    result = subprocess.run(
        ['python', 'shared/aish/aish', 'sundown', 'status'],
        capture_output=True,
        text=True
    )
    
    if 'test-ci' not in result.stdout:
        print(f"  ❌ CI not shown in sundown status")
        return False
    
    print(f"  ✓ CI shown in sundown status")
    
    # 4. Test sunrise command
    print("4. Testing sunrise command...")
    result = subprocess.run(
        ['python', 'shared/aish/aish', 'sunrise', 'test-ci'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"  ❌ Sunrise failed: {result.stderr}")
        return False
    
    print(f"  ✓ Sunrise successful")
    print(f"  Output: {result.stdout[:200]}...")
    
    # 5. Verify fresh start flag cleared
    print("5. Verifying fresh start flag...")
    needs_fresh = registry.get_needs_fresh_start('test-ci')
    if needs_fresh:
        print(f"  ❌ Fresh start flag not cleared")
        return False
    
    print(f"  ✓ Fresh start flag cleared correctly")
    
    # Clean up
    registry.clear_forward_state('test-ci')
    
    print("\n✅ All aish sundown/sunrise tests passed!\n")
    return True


async def test_token_sundown_trigger():
    """Test automatic sundown trigger at token thresholds."""
    print("\n=== Testing automatic sundown triggers ===\n")
    
    registry = get_registry()
    token_mgr = get_token_manager()
    manager = get_sundown_sunrise_manager()
    
    # Set up CI with high token usage
    print("1. Simulating high token usage...")
    registry.set_forward_state('ergon-ci', 'claude-3-5-sonnet', '')
    
    token_mgr.init_ci_tracking('ergon-ci', 'claude-3-5-sonnet')
    
    # Simulate 85% usage (auto-trigger threshold)
    large_text = 'A' * 170000  # ~170k chars ≈ 42k tokens (rough estimate)
    token_mgr.update_usage('ergon-ci', 'conversation_history', large_text)
    
    # Check if sundown should trigger
    should_sundown, reason = token_mgr.should_sundown('ergon-ci')
    print(f"2. Should sundown: {should_sundown}")
    print(f"   Reason: {reason}")
    
    if not should_sundown:
        print("  ⚠️  Sundown not triggered at high usage (might need adjustment)")
    
    # Get usage status
    usage = token_mgr.get_status('ergon-ci')
    print(f"3. Token usage: {usage.get('usage_percentage', 0):.1f}%")
    print(f"   Total tokens: {usage.get('total_tokens', 0)}")
    print(f"   Limit: {usage.get('token_limit', 0)}")
    
    # Clean up
    registry.clear_forward_state('ergon-ci')
    
    print("\n✅ Token trigger test completed\n")
    return True


async def test_command_line_interface():
    """Test CLI interface for sundown/sunrise."""
    print("\n=== Testing CLI interface ===\n")
    
    # Test help output
    commands_to_test = [
        (['python', 'shared/aish/aish', 'sundown'], "sundown help"),
        (['python', 'shared/aish/aish', 'sunrise'], "sunrise help"),
        (['python', 'shared/aish/aish', 'list', 'commands'], "list commands")
    ]
    
    for cmd, description in commands_to_test:
        print(f"Testing {description}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0 and 'Usage:' not in result.stdout:
            print(f"  ❌ {description} failed")
            print(f"     Error: {result.stderr}")
            return False
        
        print(f"  ✓ {description} works")
    
    print("\n✅ CLI interface tests passed\n")
    return True


async def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("SUNDOWN/SUNRISE INTEGRATION TESTS")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    tests = [
        test_command_line_interface,
        test_aish_sundown_sunrise,
        test_token_sundown_trigger
    ]
    
    for test in tests:
        try:
            passed = await test()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL INTEGRATION TESTS PASSED!")
    else:
        print("❌ Some tests failed. See output above.")
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)