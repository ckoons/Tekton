"""
Neo4j Configuration

Configuration utilities for Neo4j connection in Athena.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Neo4jConfig:
    """Configuration for Neo4j connection."""
    
    # Connection settings
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "password"
    
    # Component identification
    component_id: str = "athena.knowledge"
    namespace: str = "athena_knowledge"
    
    # Integration configuration
    use_hermes: bool = True
    hermes_url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'Neo4jConfig':
        """Create configuration from environment variables."""
        return cls(
            uri=os.getenv("ATHENA_NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("ATHENA_NEO4J_USERNAME", "neo4j"),
            password=os.getenv("ATHENA_NEO4J_PASSWORD", "password"),
            component_id=os.getenv("ATHENA_COMPONENT_ID", "athena.knowledge"),
            namespace=os.getenv("ATHENA_NAMESPACE", "athena_knowledge"),
            use_hermes=os.getenv("ATHENA_USE_HERMES", "true").lower() == "true",
            hermes_url=os.getenv("HERMES_URL", None)
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Neo4jConfig':
        """Create configuration from dictionary."""
        return cls(
            uri=config_dict.get("uri", "bolt://localhost:7687"),
            username=config_dict.get("username", "neo4j"),
            password=config_dict.get("password", "password"),
            component_id=config_dict.get("component_id", "athena.knowledge"),
            namespace=config_dict.get("namespace", "athena_knowledge"),
            use_hermes=config_dict.get("use_hermes", True),
            hermes_url=config_dict.get("hermes_url", None)
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "uri": self.uri,
            "username": self.username,
            "password": "********",  # Don't include actual password
            "component_id": self.component_id,
            "namespace": self.namespace,
            "use_hermes": self.use_hermes,
            "hermes_url": self.hermes_url
        }
        
    def get_connection_config(self) -> Dict[str, Any]:
        """Get configuration for Neo4j connection."""
        return {
            "uri": self.uri,
            "username": self.username,
            "password": self.password
        }
        
    def get_hermes_config(self) -> Dict[str, Any]:
        """Get configuration for Hermes integration."""
        return {
            "component_id": self.component_id,
            "namespace": self.namespace,
            "hermes_url": self.hermes_url
        }