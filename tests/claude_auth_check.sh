#!/bin/bash
# Claude Authentication & Billing Detection Script
# This script can be used by Claude itself to determine its auth method

echo "🔍 Checking Claude Authentication Method..."
echo "=========================================="

# Method 1: Check for API key
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ ANTHROPIC_API_KEY is set"
    echo "📊 Billing: API Usage (pay-per-token)"
    echo "💰 You are being charged through API usage"
    KEY_PREFIX="${ANTHROPIC_API_KEY:0:20}..."
    echo "🔑 Key prefix: $KEY_PREFIX"
else
    echo "❌ ANTHROPIC_API_KEY is NOT set"
    echo "📊 Billing: Likely Claude Max (if authenticated)"
    echo "💎 Using subscription-based billing"
fi

echo ""
echo "=========================================="
echo "How to verify your billing:"
echo ""

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "You are currently using API billing because:"
    echo "1. ANTHROPIC_API_KEY environment variable is set"
    echo "2. All requests go through api.anthropic.com"
    echo "3. You're charged per token used"
    echo ""
    echo "To switch to Claude Max:"
    echo "  unset ANTHROPIC_API_KEY"
    echo "  claude --print 'test'  # Will prompt for browser login"
else
    echo "You are likely using Claude Max because:"
    echo "1. No ANTHROPIC_API_KEY in environment"
    echo "2. Claude uses stored web authentication"
    echo "3. Flat monthly subscription fee"
    echo ""
    echo "To verify Claude Max is active:"
    echo "  claude --print 'test'  # Should work without API key"
fi

echo ""
echo "=========================================="
echo "Quick test command:"
echo "  echo 'What is 2+2?' | claude --print"
echo ""
echo "If this works without ANTHROPIC_API_KEY set,"
echo "you're using Claude Max subscription billing."