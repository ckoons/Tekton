"""
Key-Value Database Adapters - Implementations for key-value stores.

This package contains concrete implementations of the KeyValueDatabaseAdapter interface
for various key-value database backends.
"""

# INTEGRATION TEST NOTE:
# During full Tekton stack integration testing, verify the following key-value database
# implementations and their dependencies:
#
# 1. Redis Adapter (redis_adapter.py)
#    - Requires: pip install redis
#    - Configuration: Redis server URL, port, authentication
#    - Used for fast caching, session state, and simple structured data
#
# 2. Potential additional adapters to implement:
#    - LevelDB (leveldb_adapter.py) - For local storage without a server
#    - RocksDB (rocksdb_adapter.py) - For high-performance local storage
#    - DynamoDB or other cloud key-value stores for distributed deployments
#
# Key-value stores are used throughout the Tekton system for configuration, 
# state management, and lightweight data storage, making them critical for
# proper system integration.

# Re-export adapters for simplified imports
from .redis_adapter import RedisKeyValueAdapter

__all__ = ["RedisKeyValueAdapter"]