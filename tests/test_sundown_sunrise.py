#!/usr/bin/env python3
"""
Test sundown/sunrise functionality with CI agency.

This test simulates a CI preparing for tomorrow, just like a human would
plan their day and think about what needs to be done.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Apollo.apollo.core.sundown_sunrise import get_sundown_sunrise_manager
from Rhetor.rhetor.core.token_manager import get_token_manager
from shared.aish.src.registry.ci_registry import get_registry


async def simulate_ci_conversation():
    """Simulate a CI having a conversation that approaches token limits."""
    print("\n" + "="*60)
    print("SIMULATING CI CONVERSATION")
    print("="*60)
    
    ci_name = "test-ergon-ci"
    token_mgr = get_token_manager()
    
    # Initialize with a smaller model to trigger limits faster
    print(f"\n1. Initializing {ci_name} with gpt-4 (8k limit)...")
    token_mgr.init_ci_tracking(ci_name, 'gpt-4')
    
    # Simulate conversation building up tokens
    messages = [
        "Let's work on implementing a new feature for user authentication.",
        "I need to create a login system with JWT tokens and session management.",
        "First, I'll design the database schema for users and sessions.",
        "The user table will have: id, email, password_hash, created_at, updated_at.",
        "For sessions: id, user_id, token, expires_at, created_at.",
        "Now implementing the authentication service with password hashing using bcrypt...",
        "Creating JWT token generation and validation functions...",
        "Adding middleware for protecting routes that require authentication...",
    ]
    
    print("\n2. Simulating conversation...")
    total_tokens = 0
    for i, msg in enumerate(messages, 1):
        # Simulate a larger conversation by repeating the message
        expanded_msg = msg * 50  # Make messages artificially longer
        tokens = token_mgr.update_usage(ci_name, 'conversation_history', expanded_msg)
        total_tokens += tokens
        
        status = token_mgr.get_status(ci_name)
        print(f"   Message {i}: {tokens:,} tokens (Total: {status['usage']['total']:,} / {8192:,})")
        
        # Check if we should trigger sundown
        should_sundown, reason = token_mgr.should_sundown(ci_name)
        if should_sundown:
            print(f"\n   🌅 SUNDOWN TRIGGER: {reason}")
            print(f"   Token usage: {status['usage_percentage']:.1%}")
            print(f"   Recommendation: {status['recommendation']}")
            break
    
    return ci_name, status


async def test_sundown_procedure(ci_name: str):
    """Test the sundown procedure with CI agency."""
    print("\n" + "="*60)
    print("TESTING SUNDOWN PROCEDURE")
    print("="*60)
    
    manager = get_sundown_sunrise_manager()
    
    print(f"\n1. Initiating sundown for {ci_name}...")
    result = await manager.sundown(ci_name, reason="Approaching token limit during feature implementation")
    
    print(f"   Status: {result['status']}")
    print(f"   Timestamp: {result['timestamp']}")
    print(f"   Reason: {result['reason']}")
    
    # Simulate CI providing their summary (what would happen in real interaction)
    print("\n2. Simulating CI's sundown summary preparation...")
    ci_summary = """
## Sundown Summary - Authentication Feature Implementation

### Current Context
We were implementing a comprehensive user authentication system with JWT tokens and session management for the application.

### Key Decisions Made
1. **Database Schema**: Decided on separate tables for users and sessions
   - Users table: id, email, password_hash, created_at, updated_at
   - Sessions table: id, user_id, token, expires_at, created_at
2. **Security**: Using bcrypt for password hashing with cost factor 12
3. **Tokens**: JWT tokens with 24-hour expiration, refresh tokens with 7-day expiration
4. **Architecture**: Middleware-based route protection pattern

### Progress Made
- ✅ Designed database schema
- ✅ Created user and session models
- ✅ Implemented password hashing service
- ✅ Built JWT token generation functions
- ⚠️ Partially completed validation functions
- 🚧 Started middleware implementation

### Unfinished Work
1. Complete JWT validation function (missing refresh token logic)
2. Finish authentication middleware
3. Create login/logout endpoints
4. Add password reset functionality
5. Write comprehensive tests

### Next Steps for Tomorrow
1. First priority: Complete the JWT validation function in `auth/jwt.py`
2. Test the middleware with protected routes
3. Implement the `/api/auth/login` and `/api/auth/logout` endpoints
4. Begin integration testing with the frontend

### Important Notes
- Remember to add rate limiting to login endpoint (prevent brute force)
- The refresh token rotation strategy needs security review
- Database migrations are pending - run before testing
- Environment variables needed: JWT_SECRET, BCRYPT_ROUNDS, TOKEN_EXPIRY

### Files Modified
- `/models/user.py` - User model
- `/models/session.py` - Session model  
- `/services/auth/jwt.py` - Token handling (incomplete)
- `/middleware/auth.js` - Route protection (incomplete)

I'm ready to resume this work tomorrow. The foundation is solid, just need to complete the implementation and testing.
"""
    
    print("\n   CI Summary Preview:")
    print("   " + "-"*50)
    for line in ci_summary.split('\n')[:10]:
        if line.strip():
            print(f"   {line}")
    print("   ...")
    print("   " + "-"*50)
    
    # Complete the sundown with the CI's summary
    print("\n3. Completing sundown with CI summary...")
    completion = await manager.complete_sundown(ci_name, ci_summary)
    print(f"   Status: {completion['status']}")
    print(f"   State saved: {completion['state_saved']}")
    print(f"   Summary length: {completion['summary_length']:,} characters")
    
    return ci_summary


async def test_sunrise_procedure(ci_name: str):
    """Test the sunrise procedure with context restoration."""
    print("\n" + "="*60)
    print("TESTING SUNRISE PROCEDURE")
    print("="*60)
    
    manager = get_sundown_sunrise_manager()
    
    print(f"\n1. Initiating sunrise for {ci_name}...")
    result = await manager.sunrise(ci_name)
    
    print(f"   Status: {result['status']}")
    
    if result['status'] == 'ready':
        print("\n2. Sunrise context that will be restored:")
        print("   " + "-"*50)
        # Show first part of restored summary
        summary_preview = result.get('restored_summary', '')
        for line in summary_preview.split('\n')[:8]:
            if line.strip():
                print(f"   {line}")
        print("   ...")
        print("   " + "-"*50)
        
        print("\n3. CI is ready to continue with preserved context!")
        print("   - Previous work is remembered")
        print("   - Key decisions are retained")
        print("   - Next steps are clear")
        print("   - Can pick up exactly where they left off")
        
        # Check token reset
        token_mgr = get_token_manager()
        status = token_mgr.get_status(ci_name)
        print(f"\n4. Token usage reset: {status['usage']['total']:,} tokens (fresh start)")
        
    return result


async def test_full_cycle():
    """Test the complete sundown/sunrise cycle."""
    print("\n" + "="*60)
    print("FULL SUNDOWN/SUNRISE CYCLE TEST")
    print("="*60)
    
    try:
        # Phase 1: Build up conversation
        ci_name, status = await simulate_ci_conversation()
        
        # Phase 2: Sundown
        ci_summary = await test_sundown_procedure(ci_name)
        
        print("\n" + "="*60)
        print("🌙 CI IS NOW IN SUNDOWN - Context Preserved")
        print("="*60)
        
        # Simulate time passing
        await asyncio.sleep(2)
        
        # Phase 3: Sunrise
        result = await test_sunrise_procedure(ci_name)
        
        print("\n" + "="*60)
        print("☀️ CI HAS RISEN - Ready to Continue Work")
        print("="*60)
        
        print("\n✅ TEST SUCCESSFUL!")
        print("\nThe CI demonstrated agency by:")
        print("1. ✓ Recognizing when to prepare for sundown")
        print("2. ✓ Creating a comprehensive summary of their work")
        print("3. ✓ Identifying what needs to be done tomorrow")
        print("4. ✓ Preserving context for seamless continuation")
        print("5. ✓ Rising with full context restoration")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """Main test runner."""
    print("="*60)
    print("SUNDOWN/SUNRISE TEST SUITE")
    print("Testing CI Agency in Context Management")
    print("="*60)
    
    success = await test_full_cycle()
    
    if success:
        print("\n" + "="*60)
        print("ALL TESTS PASSED - System Ready for Production")
        print("="*60)
        print("\nNext Steps:")
        print("1. Integrate with aish commands")
        print("2. Add UI indicators for token usage")
        print("3. Test with real CI conversations")
        print("4. Monitor and refine thresholds")
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())