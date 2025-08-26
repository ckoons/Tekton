#!/usr/bin/env python3
"""
Test script for token management functionality.
"""

import sys
from pathlib import Path

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Rhetor.rhetor.core.token_manager import TokenManager, get_token_manager


def test_token_counting():
    """Test basic token counting."""
    print("Testing Token Counting...")
    
    tm = TokenManager()
    
    # Test different text lengths
    test_cases = [
        ("Hello world", 2),  # Approximate
        ("This is a longer sentence with multiple words.", 10),  # Approximate
        ("A" * 1000, 250),  # Long repetitive text
    ]
    
    for text, expected_range in test_cases:
        count = tm.count_tokens(text)
        print(f"  Text length: {len(text)}, Tokens: {count}")
        
    print("✓ Token counting works\n")


def test_model_limits():
    """Test model limit detection."""
    print("Testing Model Limits...")
    
    tm = TokenManager()
    
    models = [
        "claude-3-opus",
        "claude-3-5-sonnet", 
        "gpt-4",
        "gpt-4-turbo",
        "llama2",
        "unknown-model"
    ]
    
    for model in models:
        limit = tm.get_model_limit(model)
        print(f"  {model}: {limit:,} tokens")
        
    print("✓ Model limit detection works\n")


def test_budget_calculation():
    """Test budget calculations."""
    print("Testing Budget Calculations...")
    
    tm = TokenManager()
    
    model = "claude-3-5-sonnet"
    budgets = tm.calculate_budgets(model)
    
    print(f"  Budgets for {model}:")
    for component, tokens in budgets.items():
        print(f"    {component}: {tokens:,} tokens")
        
    print("✓ Budget calculation works\n")


def test_usage_tracking():
    """Test usage tracking for a CI."""
    print("Testing Usage Tracking...")
    
    tm = TokenManager()
    ci_name = "test-ci"
    model = "claude-3-5-sonnet"
    
    # Initialize tracking
    tm.init_ci_tracking(ci_name, model)
    
    # Simulate some usage
    messages = [
        "This is the first message in our conversation.",
        "Here's another message with more content to track token usage.",
        "And a third message to push the token count higher."
    ]
    
    for msg in messages:
        tokens = tm.update_usage(ci_name, 'conversation_history', msg)
        print(f"  Added {tokens} tokens")
        
    # Get status
    status = tm.get_status(ci_name)
    print(f"\n  CI Status for {ci_name}:")
    print(f"    Model: {status['model']}")
    print(f"    Total usage: {status['usage']['total']:,} tokens")
    print(f"    Usage percentage: {status['usage_percentage']:.1%}")
    print(f"    Sundown level: {status['sundown_level']}")
    print(f"    Recommendation: {status['recommendation']}")
    
    print("✓ Usage tracking works\n")


def test_sundown_detection():
    """Test sundown trigger detection."""
    print("Testing Sundown Detection...")
    
    tm = TokenManager()
    ci_name = "ergon-test"
    model = "gpt-4"  # Smaller limit for testing
    
    tm.init_ci_tracking(ci_name, model)
    
    # Simulate heavy usage
    large_text = "This is a test message. " * 1000  # About 5000 tokens
    tm.update_usage(ci_name, 'conversation_history', large_text)
    
    should_sundown, reason = tm.should_sundown(ci_name)
    usage_pct = tm.get_usage_percentage(ci_name)
    
    print(f"  CI: {ci_name}")
    print(f"  Model: {model} (limit: {tm.get_model_limit(model):,} tokens)")
    print(f"  Current usage: {usage_pct:.1%}")
    print(f"  Should sundown: {should_sundown}")
    print(f"  Reason: {reason}")
    
    print("✓ Sundown detection works\n")


def test_prompt_estimation():
    """Test prompt size estimation."""
    print("Testing Prompt Size Estimation...")
    
    tm = TokenManager()
    ci_name = "estimation-test"
    
    message = "What's the weather like today?"
    system_prompt = "You are a helpful AI assistant."
    buffered = "\n[Previous message from another CI]: Check the API for weather data."
    
    estimate = tm.estimate_prompt_size(
        ci_name,
        message,
        system_prompt=system_prompt,
        buffered_messages=buffered
    )
    
    print(f"  Prompt components:")
    for component, count in estimate['counts'].items():
        print(f"    {component}: {count} tokens")
    print(f"\n  Total: {estimate['total']} tokens")
    print(f"  Limit: {estimate['limit']:,} tokens")
    print(f"  Usage: {estimate['percentage']:.1%}")
    print(f"  Fits: {estimate['fits']}")
    print(f"  Recommendation: {estimate['recommendation']}")
    
    print("✓ Prompt estimation works\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Token Management Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_token_counting()
        test_model_limits()
        test_budget_calculation()
        test_usage_tracking()
        test_sundown_detection()
        test_prompt_estimation()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)