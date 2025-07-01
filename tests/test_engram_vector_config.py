#!/usr/bin/env python3
"""
Test if Engram correctly picks up vector DB configuration from GlobalConfig.
"""

import sys
import os

# Add Tekton to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# First, set a test value in the config
print("1. Setting TEKTON_VECTOR_DB in .env.tekton...")

from shared.utils.env_manager import TektonEnvManager
env_manager = TektonEnvManager()

# Save chromadb preference to .env.tekton
env_manager.save_tekton_settings({
    'TEKTON_VECTOR_DB': 'chromadb'
})

# Reload environment to pick up the change
env_manager.load_environment()

# Now test if Engram picks it up
print("\n2. Testing Engram configuration loading...")

from shared.utils.global_config import GlobalConfig
config = GlobalConfig.get_instance()

print(f"GlobalConfig vector DB setting: {config.config.vector.vector_db}")

# Test Engram's config module
print("\n3. Testing Engram memory config module...")

from Engram.engram.core.memory import config as engram_config

# Force reload of the module to pick up new config
import importlib
importlib.reload(engram_config)

print(f"Engram PREFERRED_VECTOR_DB: {engram_config.PREFERRED_VECTOR_DB}")
print(f"Engram VECTOR_CPU_ONLY: {engram_config.VECTOR_CPU_ONLY}")
print(f"Engram VECTOR_GPU_ENABLED: {engram_config.VECTOR_GPU_ENABLED}")

# Test initialization
print("\n4. Testing vector DB initialization...")

has_vector, db_info, vector_model = engram_config.initialize_vector_db()

print(f"Initialized with: {db_info.get('name', 'none')}")
print(f"Available: {db_info.get('available', False)}")

# Reset to auto
print("\n5. Resetting to auto mode...")
env_manager.save_tekton_settings({
    'TEKTON_VECTOR_DB': 'auto'
})

print("Done! Check if Engram now uses ChromaDB on restart.")