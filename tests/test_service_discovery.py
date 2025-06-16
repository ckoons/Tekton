#!/usr/bin/env python3
"""
Test script for GlobalConfig service discovery feature.

This script verifies that:
1. GlobalConfig can query Hermes for service URLs
2. Service URLs are cached after first load
3. Fallback to localhost works when Hermes is unavailable
"""

import sys
import os
import time
import json
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.utils.global_config import GlobalConfig


def test_service_discovery_with_hermes():
    """Test service discovery when Hermes is available."""
    print("\n=== Testing Service Discovery with Hermes ===")
    
    # Mock Hermes response
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "components": [
            {
                "name": "rhetor",
                "endpoint": "http://docker-rhetor:8003",
                "status": "healthy"
            },
            {
                "name": "engram", 
                "endpoint": "http://k8s-engram.namespace.svc.cluster.local:8000",
                "status": "healthy"
            },
            {
                "name": "apollo",
                "endpoint": "http://remote-host.example.com:8012",
                "status": "healthy"
            }
        ]
    }
    
    # Clear any existing state
    config = GlobalConfig.get_instance()
    config.clear_runtime_state()
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        # First call should query Hermes
        rhetor_url = config.get_service_url("rhetor")
        print(f"✓ Rhetor URL from Hermes: {rhetor_url}")
        assert rhetor_url == "http://docker-rhetor:8003"
        
        # Verify Hermes was called
        mock_get.assert_called_once_with("http://localhost:8001/components", timeout=2.0)
        
        # Second call should use cache (no additional Hermes call)
        engram_url = config.get_service_url("engram")
        print(f"✓ Engram URL from cache: {engram_url}")
        assert engram_url == "http://k8s-engram.namespace.svc.cluster.local:8000"
        assert mock_get.call_count == 1  # Still only one call
        
        # Test remote host URL
        apollo_url = config.get_service_url("apollo")
        print(f"✓ Apollo URL from cache: {apollo_url}")
        assert apollo_url == "http://remote-host.example.com:8012"
        
    print("✓ Service discovery with Hermes: PASSED")


def test_fallback_when_hermes_unavailable():
    """Test fallback to localhost when Hermes is not available."""
    print("\n=== Testing Fallback when Hermes Unavailable ===")
    
    # Clear any existing state
    config = GlobalConfig.get_instance()
    config.clear_runtime_state()
    
    # Mock failed request
    with patch('requests.get', side_effect=Exception("Connection refused")):
        # Should fallback to localhost
        rhetor_url = config.get_service_url("rhetor")
        print(f"✓ Rhetor URL fallback: {rhetor_url}")
        assert rhetor_url == "http://localhost:8003"
        
        # Different component
        hermes_url = config.get_service_url("hermes")
        print(f"✓ Hermes URL fallback: {hermes_url}")
        assert hermes_url == "http://localhost:8001"
        
    print("✓ Fallback mechanism: PASSED")


def test_component_not_in_hermes():
    """Test fallback for components not registered in Hermes."""
    print("\n=== Testing Component Not in Hermes ===")
    
    # Mock Hermes response with limited components
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "components": [
            {
                "name": "rhetor",
                "endpoint": "http://custom-host:8003",
                "status": "healthy"
            }
        ]
    }
    
    # Clear any existing state
    config = GlobalConfig.get_instance()
    config.clear_runtime_state()
    
    with patch('requests.get', return_value=mock_response):
        # Component in Hermes
        rhetor_url = config.get_service_url("rhetor")
        print(f"✓ Rhetor URL from Hermes: {rhetor_url}")
        assert rhetor_url == "http://custom-host:8003"
        
        # Component NOT in Hermes - should fallback
        sophia_url = config.get_service_url("sophia")
        print(f"✓ Sophia URL fallback: {sophia_url}")
        assert sophia_url == "http://localhost:8014"
        
    print("✓ Mixed discovery/fallback: PASSED")


def test_real_hermes_if_running():
    """Test against real Hermes if it's running."""
    print("\n=== Testing with Real Hermes (if available) ===")
    
    import requests
    
    # Clear any existing state
    config = GlobalConfig.get_instance()
    config.clear_runtime_state()
    
    try:
        # Check if Hermes is actually running
        response = requests.get("http://localhost:8001/health", timeout=0.5)
        if response.ok:
            print("✓ Hermes is running, testing real service discovery...")
            
            # Get service URL through GlobalConfig
            rhetor_url = config.get_service_url("rhetor")
            print(f"  Retrieved Rhetor URL: {rhetor_url}")
            
            # Verify cache was populated
            if config._service_urls:
                print(f"  Cached services: {list(config._service_urls.keys())}")
            else:
                print("  No services cached (Hermes might not have any registered)")
                
    except:
        print("  Hermes not running - skipping real test")
    
    print("✓ Real Hermes test: COMPLETED")


def main():
    """Run all tests."""
    print("Testing GlobalConfig Service Discovery")
    print("=" * 50)
    
    try:
        test_service_discovery_with_hermes()
        test_fallback_when_hermes_unavailable()
        test_component_not_in_hermes()
        test_real_hermes_if_running()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())