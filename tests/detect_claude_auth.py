#!/usr/bin/env python3
"""
Detect Claude authentication method and billing type
"""

import os
from shared.env import TektonEnviron
import subprocess
import json
import sys
from pathlib import Path

def detect_claude_auth():
    """Detect how Claude is authenticated"""
    
    results = {
        "api_key_present": False,
        "api_key_source": None,
        "auth_method": "unknown",
        "billing_type": "unknown",
        "details": {}
    }
    
    # 1. Check environment variable
    api_key = TektonEnviron.get('ANTHROPIC_API_KEY')
    if api_key:
        results["api_key_present"] = True
        results["api_key_source"] = "environment"
        results["auth_method"] = "api_key"
        results["billing_type"] = "api"
        results["details"]["api_key_prefix"] = api_key[:20] + "..." if len(api_key) > 20 else "HIDDEN"
    
    # 2. Check for Claude stored credentials (web auth tokens)
    home = Path.home()
    
    # Potential token storage locations
    token_locations = [
        home / ".claude" / "auth.json",
        home / ".claude" / "config.json",
        home / ".config" / "claude" / "auth.json",
        home / "Library" / "Application Support" / "@anthropic-ai" / "claude-code" / "auth.json",
        home / ".local" / "share" / "@anthropic-ai" / "claude-code" / "auth.json",
    ]
    
    for location in token_locations:
        if location.exists():
            results["details"]["token_file"] = str(location)
            try:
                with open(location, 'r') as f:
                    data = json.load(f)
                    if 'token' in data or 'access_token' in data:
                        if not results["api_key_present"]:
                            results["auth_method"] = "web_auth"
                            results["billing_type"] = "claude_max"
                        results["details"]["has_stored_tokens"] = True
            except:
                pass
    
    # 3. Try to detect from Claude's runtime behavior
    try:
        # Run a test command with minimal output
        env = os.environ.copy()
        
        # Test without API key
        if api_key:
            del env['ANTHROPIC_API_KEY']
            test_no_key = subprocess.run(
                ['node', '-e', 'console.log(process.env.ANTHROPIC_API_KEY || "NO_KEY")'],
                env=env,
                capture_output=True,
                text=True,
                timeout=2
            )
            results["details"]["without_key_test"] = test_no_key.stdout.strip()
    except:
        pass
    
    # 4. Check Claude's internal state (if accessible)
    try:
        # Try to get Claude's config
        claude_test = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        results["details"]["claude_version"] = claude_test.stdout.strip()
    except:
        pass
    
    # 5. Final determination
    if results["api_key_present"]:
        print("🔑 Authentication: API Key")
        print("💰 Billing: API Usage (pay per token)")
        print(f"📍 Source: {results['api_key_source']}")
        print(f"🔐 Key prefix: {results['details'].get('api_key_prefix', 'N/A')}")
    elif results["auth_method"] == "web_auth":
        print("🌐 Authentication: Web Auth (browser login)")
        print("💎 Billing: Claude Max Subscription")
        print(f"📁 Token location: {results['details'].get('token_file', 'N/A')}")
    else:
        print("❓ Authentication: Unknown/Not configured")
        print("⚠️  Claude may prompt for login on first use")
    
    return results

def test_claude_billing():
    """Test actual Claude behavior to determine billing"""
    
    print("\n" + "="*50)
    print("Testing Claude's actual behavior...")
    print("="*50)
    
    # Check if we can make a request
    test_prompt = "Say 'API' if using API key, 'MAX' if using Claude Max"
    
    try:
        # Try with current environment
        result = subprocess.run(
            ['claude', '--print', test_prompt],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Claude responded successfully")
            # Note: The actual response won't tell us billing directly,
            # but successful response with API key means API billing
            if TektonEnviron.get('ANTHROPIC_API_KEY'):
                print("📊 Using API billing (ANTHROPIC_API_KEY is set)")
            else:
                print("📊 Likely using Claude Max (no API key in environment)")
        else:
            print("❌ Claude command failed")
            print(f"Error: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print("⏱️ Claude command timed out")
    except Exception as e:
        print(f"❌ Error testing Claude: {e}")

def suggest_changes():
    """Suggest how to switch between auth methods"""
    
    print("\n" + "="*50)
    print("How to switch authentication methods:")
    print("="*50)
    
    if TektonEnviron.get('ANTHROPIC_API_KEY'):
        print("\n📌 Currently using API Key")
        print("\nTo switch to Claude Max:")
        print("1. unset ANTHROPIC_API_KEY")
        print("2. claude --print 'test'  # This should open browser for login")
        print("3. Log in with your Claude Max account")
        print("\nTo verify: The browser login indicates Claude Max billing")
    else:
        print("\n📌 Currently NOT using API Key")
        print("\nTo use API billing:")
        print("1. export ANTHROPIC_API_KEY='your-api-key-here'")
        print("2. claude --print 'test'  # Will use API key")
        print("\nTo use Claude Max:")
        print("1. Make sure ANTHROPIC_API_KEY is not set")
        print("2. claude --print 'test'  # Should use stored web auth")

if __name__ == "__main__":
    print("🔍 Claude Authentication & Billing Detector")
    print("="*50)
    
    auth_info = detect_claude_auth()
    test_claude_billing()
    suggest_changes()
    
    print("\n" + "="*50)
    print("Full detection results:")
    print(json.dumps(auth_info, indent=2))