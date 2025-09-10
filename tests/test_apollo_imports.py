#!/usr/bin/env python3
"""Test Apollo imports and ESR integration."""

import os
import sys

# Set up environment
os.environ['TEKTON_ROOT'] = '/Users/cskoons/projects/github/Coder-A'
sys.path.insert(0, '/Users/cskoons/projects/github/Coder-A')
sys.path.insert(0, '/Users/cskoons/projects/github/Coder-A/Hermes')
sys.path.insert(0, '/Users/cskoons/projects/github/Coder-A/Engram')
sys.path.insert(0, '/Users/cskoons/projects/github/Coder-A/Apollo')

print("Testing Apollo ESR Integration...")
print("=" * 50)

try:
    print("1. Testing Hermes database imports...")
    from hermes.core.database.factory import DatabaseFactory
    print("   ✓ DatabaseFactory imported")
    
    print("\n2. Testing Engram ESR imports...")
    from engram.core.storage.unified_interface import ESRMemorySystem
    print("   ✓ ESRMemorySystem imported")
    
    print("\n3. Testing Cognitive Workflows...")
    from engram.core.storage.cognitive_workflows import CognitiveWorkflows
    print("   ✓ CognitiveWorkflows imported")
    
    print("\n4. Testing Apollo imports...")
    from apollo.core.apollo_manager import ApolloManager
    print("   ✓ ApolloManager imported")
    
    from apollo.core.storage_interface import ApolloStorageInterface
    print("   ✓ ApolloStorageInterface imported")
    
    print("\n5. Testing ESR initialization...")
    esr_system = ESRMemorySystem(cache_size=100)
    print("   ✓ ESR system created")
    
    print("\n6. Checking for encoder...")
    if hasattr(esr_system, 'encoder'):
        print("   ✓ ESR has encoder attribute")
    else:
        print("   ✗ ESR missing encoder attribute")
        
    print("\n7. Testing database adapter creation...")
    from hermes.core.database.database_types import DatabaseType, DatabaseBackend
    
    # Test FAISS fallback
    adapter = DatabaseFactory.create_adapter(DatabaseType.VECTOR, DatabaseBackend.FAISS)
    print(f"   ✓ Vector adapter created: {type(adapter).__name__}")
    
    # Test QDRANT fallback
    adapter = DatabaseFactory.create_adapter(DatabaseType.VECTOR, DatabaseBackend.QDRANT)
    print(f"   ✓ Qdrant fallback: {type(adapter).__name__}")
    
    print("\n✅ All imports successful! Apollo-ESR integration should work.")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()