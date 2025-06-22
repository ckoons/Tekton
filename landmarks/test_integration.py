#!/usr/bin/env python3
"""
Test that landmarks are properly integrated into shared utilities
"""

import sys
from pathlib import Path

# Add Tekton root to path
tekton_root = Path(__file__).parent.parent
sys.path.insert(0, str(tekton_root))

# Import the landmarked modules to trigger registration
print("🔄 Importing landmarked modules...\n")

try:
    # Import global_config with landmarks
    print("1. Importing global_config...")
    from shared.utils.global_config import GlobalConfig
    print("   ✅ GlobalConfig imported successfully")
    
    # Import graceful_shutdown with landmarks  
    print("2. Importing graceful_shutdown...")
    from shared.utils.graceful_shutdown import GracefulShutdown
    print("   ✅ GracefulShutdown imported successfully")
    
    # Import standard_component with landmarks
    print("3. Importing standard_component...")
    from shared.utils.standard_component import StandardComponentBase
    print("   ✅ StandardComponentBase imported successfully")
    
    # Import mcp_helpers with landmarks
    print("4. Importing mcp_helpers...")
    from shared.utils.mcp_helpers import create_mcp_server
    print("   ✅ mcp_helpers imported successfully")
    
except Exception as e:
    print(f"   ❌ Error importing: {e}")
    sys.exit(1)

# Now check if landmarks were registered
print("\n📊 Checking landmark registration...\n")

from landmarks import LandmarkRegistry

stats = LandmarkRegistry.stats()
print(f"Total landmarks registered: {stats['total_landmarks']}")

# List landmarks in shared component
shared_landmarks = LandmarkRegistry.list(component='shared')
print(f"\nLandmarks in 'shared' component: {len(shared_landmarks)}")

for lm in shared_landmarks:
    print(f"\n[{lm.type}] {lm.title}")
    print(f"  File: {Path(lm.file_path).name}:{lm.line_number}")
    if lm.metadata.get('rationale'):
        print(f"  Rationale: {lm.metadata['rationale'][:80]}...")

# Test that decorated functions still work
print("\n🧪 Testing that decorated functions still work...\n")

# Test GlobalConfig singleton
config1 = GlobalConfig()
config2 = GlobalConfig()
print(f"1. GlobalConfig singleton test: {'✅ PASS' if config1 is config2 else '❌ FAIL'}")

# Test GracefulShutdown initialization
shutdown = GracefulShutdown("test_component", 8000)
print(f"2. GracefulShutdown creation: ✅ PASS")

# Test that functions have landmark attributes
if hasattr(GlobalConfig, '_landmark'):
    print(f"3. GlobalConfig has landmark: ✅ PASS")
else:
    print(f"3. GlobalConfig has landmark: ❌ FAIL")

print("\n✨ Integration test complete!")