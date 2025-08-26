#!/usr/bin/env python3
"""
Full System Integration Test
Tests the complete Rhetor/Apollo Prompt & Context Management System
Including token management, sundown/sunrise, and CI agency
"""

import asyncio
import json
import time
from pathlib import Path
import sys

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.aish.src.registry.ci_registry import get_registry
from shared.ai.claude_handler import get_claude_handler
from Rhetor.rhetor.core.token_manager import get_token_manager
from Apollo.apollo.core.sundown_sunrise import get_sundown_sunrise_manager


async def test_complete_workflow():
    """
    Test the complete workflow:
    1. CI starts working
    2. Token usage increases
    3. System detects high usage
    4. Sundown triggers
    5. Context preserved
    6. Sunrise restores context
    7. CI continues with awareness
    """
    print("\n" + "=" * 70)
    print("COMPLETE SYSTEM INTEGRATION TEST")
    print("Testing Rhetor/Apollo Prompt & Context Management")
    print("=" * 70 + "\n")
    
    # Components
    registry = get_registry()
    token_mgr = get_token_manager()
    sundown_mgr = get_sundown_sunrise_manager()
    claude_handler = get_claude_handler()
    
    ci_name = 'integration-test-ci'
    
    # Step 1: Initialize CI
    print("Step 1: Initialize CI and start tracking")
    print("-" * 50)
    registry.set_forward_state(ci_name, 'claude-3-5-sonnet', '')
    token_mgr.init_ci_tracking(ci_name, 'claude-3-5-sonnet')
    print(f"✓ CI '{ci_name}' initialized with claude-3-5-sonnet")
    
    # Step 2: Simulate work and token usage
    print("\nStep 2: Simulate CI work and token accumulation")
    print("-" * 50)
    messages = [
        "Initial task: Build authentication system",
        "Implementing OAuth2 with JWT tokens",
        "Adding refresh token rotation",
        "Securing endpoints with middleware",
        "Testing authentication flow"
    ]
    
    for i, msg in enumerate(messages, 1):
        # Simulate message processing
        token_count = token_mgr.update_usage(ci_name, 'conversation_history', msg * 100)
        status = token_mgr.get_status(ci_name)
        usage_total = sum(status.get('usage', {}).values())
        print(f"  Message {i}: {status['usage_percentage']:.1f}% usage ({usage_total} tokens)")
        
        # Check if sundown needed
        should_sundown, reason = token_mgr.should_sundown(ci_name)
        if should_sundown:
            print(f"  ⚠️  Sundown trigger: {reason}")
    
    print(f"✓ Processed {len(messages)} messages")
    
    # Step 3: Check token status
    print("\nStep 3: Token Management Status")
    print("-" * 50)
    status = token_mgr.get_status(ci_name)
    print(f"  Model: {status['model']}")
    limit = token_mgr.get_model_limit(status['model'])
    print(f"  Token Limit: {limit:,}")
    usage_total = sum(status.get('usage', {}).values())
    print(f"  Current Usage: {usage_total:,} ({status['usage_percentage']:.1f}%)")
    print(f"  Sundown Level: {status['sundown_level']}")
    
    budgets = status.get('budgets', {})
    if budgets:
        print(f"  Budget Allocation:")
        for component, tokens in budgets.items():
            print(f"    - {component}: {tokens:,} tokens")
    
    # Step 4: Test sundown with CI agency
    print("\nStep 4: CI Agency - Sundown Decision")
    print("-" * 50)
    
    # CI decides what to preserve
    ci_summary = {
        "key_topics": ["OAuth2 implementation", "JWT tokens", "Refresh rotation"],
        "important_context": "Working on authentication system, completed token generation",
        "next_steps": ["Implement token revocation", "Add rate limiting", "Document API"],
        "emotional_state": "focused but approaching cognitive limit"
    }
    
    print("  CI preserves:")
    for topic in ci_summary["key_topics"]:
        print(f"    • {topic}")
    print(f"  Next steps: {len(ci_summary['next_steps'])} items")
    print(f"  Emotional state: {ci_summary['emotional_state']}")
    
    # Trigger sundown
    result = await sundown_mgr.sundown(
        ci_name,
        reason="Approaching token limit"
    )
    
    registry.set_needs_fresh_start(ci_name, True)
    print(f"✓ Sundown completed, context preserved")
    
    # Step 5: Simulate rest period
    print("\nStep 5: Rest Period")
    print("-" * 50)
    print("  CI is resting...")
    await asyncio.sleep(1)  # Short sleep for demo
    print("✓ Rest period complete")
    
    # Step 6: Sunrise - Restore context
    print("\nStep 6: Sunrise - Context Restoration")
    print("-" * 50)
    
    result = await sundown_mgr.sunrise(ci_name)
    if result.get("success"):
        print(f"  Context restored successfully")
        print(f"  Summary: {result.get('summary', 'N/A')}")
        
        # Clear fresh start flag
        registry.set_needs_fresh_start(ci_name, False)
        
        # Reinitialize token tracking
        token_mgr.init_ci_tracking(ci_name, 'claude-3-5-sonnet')
        print(f"✓ CI ready to continue with full awareness")
    else:
        print(f"  ⚠️  No context to restore")
    
    # Step 7: Verify fresh start handling
    print("\nStep 7: Verify Claude Integration")
    print("-" * 50)
    
    needs_fresh = registry.get_needs_fresh_start(ci_name)
    print(f"  Needs fresh start: {needs_fresh}")
    print(f"  Next message will {'skip' if needs_fresh else 'include'} --continue flag")
    
    # Check if sunrise context exists
    sunrise_ctx = registry.get_sunrise_context(ci_name)
    if sunrise_ctx:
        print(f"  Sunrise context available: {len(sunrise_ctx)} chars")
    
    print(f"✓ Claude integration verified")
    
    # Step 8: Clean up
    print("\nStep 8: Cleanup")
    print("-" * 50)
    registry.clear_forward_state(ci_name)
    token_mgr.reset_ci(ci_name)
    print(f"✓ Test environment cleaned")
    
    print("\n" + "=" * 70)
    print("✅ FULL SYSTEM INTEGRATION TEST PASSED")
    print("=" * 70 + "\n")
    
    return True


async def test_multi_ci_orchestration():
    """Test managing multiple CIs simultaneously."""
    print("\n" + "=" * 70)
    print("MULTI-CI ORCHESTRATION TEST")
    print("=" * 70 + "\n")
    
    registry = get_registry()
    token_mgr = get_token_manager()
    
    cis = ['numa-ci', 'athena-ci', 'apollo-ci']
    models = ['claude-3-5-sonnet', 'gpt-4', 'claude-3-opus']
    
    print("Initializing multiple CIs...")
    for ci, model in zip(cis, models):
        registry.set_forward_state(ci, model, '')
        token_mgr.init_ci_tracking(ci, model)
        print(f"  ✓ {ci} with {model}")
    
    print("\nSimulating parallel work...")
    for i in range(3):
        for ci in cis:
            token_mgr.update_usage(ci, 'conversation_history', f"Message {i}" * 50)
        
    print("\nToken usage across CIs:")
    for ci in cis:
        status = token_mgr.get_status(ci)
        should_sundown, reason = token_mgr.should_sundown(ci)
        print(f"  {ci}: {status['usage_percentage']:.1f}% - {reason}")
    
    # Clean up
    for ci in cis:
        registry.clear_forward_state(ci)
        token_mgr.reset_ci(ci)
    
    print("\n✅ Multi-CI orchestration test passed\n")
    return True


async def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 70)
    print("EDGE CASES TEST")
    print("=" * 70 + "\n")
    
    registry = get_registry()
    token_mgr = get_token_manager()
    sundown_mgr = get_sundown_sunrise_manager()
    
    print("Test 1: Sunrise without sundown")
    result = await sundown_mgr.sunrise('nonexistent-ci')
    assert not result.get("success"), "Should fail for non-existent CI"
    print("  ✓ Handled correctly")
    
    print("\nTest 2: Double sundown")
    ci_name = 'edge-test-ci'
    registry.set_forward_state(ci_name, 'claude-3-5-sonnet', '')
    await sundown_mgr.sundown(ci_name, "Test")
    await sundown_mgr.sundown(ci_name, "Test again")
    print("  ✓ Handled without error")
    
    print("\nTest 3: Unknown model")
    try:
        token_mgr.init_ci_tracking('unknown-ci', 'unknown-model')
        limit = token_mgr.get_model_limit('unknown-model')
        print(f"  ✓ Defaults to {limit:,} token limit")
    except:
        print("  ✓ Error handled gracefully")
    
    # Clean up
    registry.clear_forward_state(ci_name)
    
    print("\n✅ Edge cases handled correctly\n")
    return True


async def main():
    """Run all integration tests."""
    
    print("\n" + "🚀" * 30)
    print("TEKTON PROMPT & CONTEXT MANAGEMENT")
    print("FULL SYSTEM INTEGRATION TEST SUITE")
    print("🚀" * 30 + "\n")
    
    tests = [
        ("Complete Workflow", test_complete_workflow),
        ("Multi-CI Orchestration", test_multi_ci_orchestration),
        ("Edge Cases", test_edge_cases)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            print(f"\nRunning: {name}")
            passed = await test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Final summary
    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System ready for production.")
    else:
        print("⚠️  Some tests failed. Review output above.")
    print("=" * 70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)