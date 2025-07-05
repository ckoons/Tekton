#!/usr/bin/env python3
"""
Simple integration test to verify Tekton and aish use the new unified service.
This tests the "one queue, one socket, one AI" architecture.
"""

import sys
sys.path.insert(0, '/Users/cskoons/projects/github/Tekton')

def test_imports():
    """Test that all imports work correctly"""
    test_name = "test_imports"
    try:
        # Test simple_ai imports
        from shared.ai.simple_ai import ai_send_sync, ai_send
        
        # Test service imports  
        from shared.ai.ai_service_simple import get_service
        
        # Test that socket registry uses simple service
        from shared.aish.src.registry.socket_registry import SocketRegistry
        
        print(f"✓ {test_name}")
        return True
    except Exception as e:
        print(f"✗ {test_name}: {e}")
        return False

def test_service_creation():
    """Test that we can create the service"""
    test_name = "test_service_creation"
    try:
        from shared.ai.ai_service_simple import get_service
        
        service = get_service()
        
        # Check basic service structure
        assert hasattr(service, 'queues')
        assert hasattr(service, 'sockets') 
        assert hasattr(service, 'send_request')
        assert hasattr(service, 'send_message_sync')
        
        print(f"✓ {test_name}")
        return True
    except Exception as e:
        print(f"✗ {test_name}: {e}")
        return False

def test_simple_ai_mock():
    """Test simple_ai with mock connection"""
    test_name = "test_simple_ai_mock"
    try:
        from shared.ai.simple_ai import ai_send_sync
        
        # This should fail with connection error (expected)
        try:
            response = ai_send_sync("non-existent-ai", "hello", "localhost", 99999)
            print(f"✗ {test_name}: Should have failed")
            return False
        except Exception as e:
            # Expected to fail - AI not running
            if "Could not connect" in str(e) or "AI non-existent-ai not registered" in str(e):
                print(f"✓ {test_name}")
                return True
            else:
                print(f"✗ {test_name}: Wrong error: {e}")
                return False
            
    except Exception as e:
        print(f"✗ {test_name}: {e}")
        return False

def test_socket_registry_simple():
    """Test socket registry uses simple service"""
    test_name = "test_socket_registry_simple"
    try:
        from shared.aish.src.registry.socket_registry import SocketRegistry
        
        # Create registry
        registry = SocketRegistry(debug=True)
        
        # Check it can discover AIs (will be empty but shouldn't crash)
        ais = registry.discover_ais()
        assert isinstance(ais, dict)
        
        print(f"✓ {test_name}")
        return True
    except Exception as e:
        print(f"✗ {test_name}: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("Simple Integration Test Suite")
    print("Testing: Unified AI Communication")
    print("-" * 50)
    
    tests = [
        test_imports,
        test_service_creation,
        test_simple_ai_mock,
        test_socket_registry_simple
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("-" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)