#!/usr/bin/env python3
"""Test script to verify Tekton Core modernization."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test environment imports
        from shared.env import TektonEnviron
        print("✓ TektonEnviron import successful")
        
        # Test URL imports
        from shared.urls import hermes_url, tekton_url
        print("✓ URL builder imports successful")
        
        # Test that we can use the functions
        test_env = TektonEnviron.get('TEKTON_ROOT', '/default')
        print(f"✓ TektonEnviron.get() works: TEKTON_ROOT={test_env}")
        
        test_url = hermes_url("/api")
        print(f"✓ hermes_url() works: {test_url}")
        
        # Test core imports
        from tekton.core.component_discovery import ComponentDiscovery
        print("✓ ComponentDiscovery import successful")
        
        from tekton.api.app import app
        print("✓ API app import successful")
        
        from tekton.models.config import TektonConfig
        print("✓ TektonConfig import successful")
        
        from tekton.storage.factory import create_vector_store
        print("✓ Storage factory import successful")
        
        print("\n✅ All imports successful! Modernization complete.")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)