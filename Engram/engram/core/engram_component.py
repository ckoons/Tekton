"""Engram component implementation using StandardComponentBase."""
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from shared.utils.standard_component import StandardComponentBase

logger = logging.getLogger(__name__)

class EngramComponent(StandardComponentBase):
    """Engram memory management component with flexible storage backends."""
    
    def __init__(self):
        super().__init__(component_name="engram", version="0.1.0")
        # Component-specific attributes
        self.memory_manager = None
        self.hermes_adapter = None
        self.mcp_bridge = None
        self.data_dir = None
        self.default_client_id = None
        self.use_fallback = False
        self.use_hermes = False
        self.debug_mode = False
        
    async def _component_specific_init(self):
        """Initialize Engram-specific services with flexible storage backends."""
        # Get component configuration
        engram_config = self.global_config.get_component_config("engram")
        
        # Configure modes from config or environment
        self.debug_mode = getattr(engram_config, "debug", 
            os.environ.get('ENGRAM_DEBUG', '').lower() in ('1', 'true', 'yes'))
        self.use_fallback = getattr(engram_config, "use_fallback", 
            os.environ.get('ENGRAM_USE_FALLBACK', '').lower() in ('1', 'true', 'yes'))
        self.use_hermes = getattr(engram_config, "hermes_mode", 
            os.environ.get('ENGRAM_MODE', '').lower() == 'hermes')
        
        # Set up logging level
        if self.debug_mode:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
        
        # Log storage configuration
        logger.info(f"Storage mode: {'fallback (file-based)' if self.use_fallback else 'vector (FAISS)'}")
        logger.info(f"Hermes integration: {'enabled' if self.use_hermes else 'disabled'}")
        
        # Set up data directory structure
        self.data_dir = Path(self.global_config.get_data_dir("engram"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different storage types
        vector_dir = self.data_dir / "vectors"
        fallback_dir = self.data_dir / "fallback"
        vector_dir.mkdir(exist_ok=True)
        fallback_dir.mkdir(exist_ok=True)
        
        logger.info(f"Data directory initialized at: {self.data_dir}")
        
        # Get client ID from config or environment
        self.default_client_id = getattr(engram_config, "default_client_id",
            os.environ.get("ENGRAM_CLIENT_ID", "default"))
        
        # Initialize memory manager based on storage mode
        try:
            from engram.core.memory_manager import MemoryManager
            
            # Pass appropriate data directory based on mode
            storage_dir = str(fallback_dir if self.use_fallback else vector_dir)
            self.memory_manager = MemoryManager(data_dir=storage_dir)
            
            logger.info(f"Memory manager initialized with storage at: {storage_dir}")
            logger.info(f"Default client ID: {self.default_client_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            # Try fallback initialization if vector fails
            if not self.use_fallback:
                logger.warning("Attempting fallback storage mode due to initialization error")
                try:
                    self.use_fallback = True
                    self.memory_manager = MemoryManager(data_dir=str(fallback_dir))
                    logger.info("Successfully initialized with fallback storage")
                except Exception as fallback_error:
                    logger.error(f"Failed to initialize even with fallback: {fallback_error}")
                    raise
            else:
                raise
        
        # Initialize Hermes integration if enabled
        if self.use_hermes:
            await self._init_hermes_integration()
        
        # Initialize MCP bridge
        await self._init_mcp_bridge()
        
        logger.info("Engram component initialization completed")
    
    async def _init_hermes_integration(self):
        """Initialize optional Hermes integration."""
        try:
            from engram.integrations.hermes.memory_adapter import HermesMemoryAdapter
            
            self.hermes_adapter = HermesMemoryAdapter(self.memory_manager)
            await self.hermes_adapter.initialize()
            logger.info("Hermes memory adapter initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Hermes integration not available: {e}")
            logger.info("Continuing without Hermes integration")
            self.use_hermes = False
            
        except Exception as e:
            logger.error(f"Failed to initialize Hermes integration: {e}")
            logger.warning("Continuing without Hermes integration")
            self.use_hermes = False
    
    async def _init_mcp_bridge(self):
        """Initialize MCP bridge for tool access."""
        try:
            from engram.core.mcp.hermes_bridge import EngramMCPBridge
            
            self.mcp_bridge = EngramMCPBridge(self.memory_manager)
            await self.mcp_bridge.initialize()
            logger.info("MCP Bridge initialized for tool access")
            
        except Exception as e:
            logger.warning(f"Failed to initialize MCP Bridge: {e}")
            logger.info("MCP tools will not be available")
    
    async def _component_specific_cleanup(self):
        """Cleanup Engram-specific resources with proper lifecycle management."""
        # Cleanup MCP bridge first
        if self.mcp_bridge:
            try:
                await self.mcp_bridge.shutdown()
                logger.info("MCP Bridge cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up MCP Bridge: {e}")
        
        # Cleanup Hermes adapter
        if self.hermes_adapter:
            try:
                await self.hermes_adapter.close()
                logger.info("Hermes adapter closed")
            except Exception as e:
                logger.warning(f"Error closing Hermes adapter: {e}")
        
        # Cleanup memory manager last (most critical)
        if self.memory_manager:
            try:
                await self.memory_manager.shutdown()
                logger.info("Memory manager shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down memory manager: {e}")
                # Log but don't re-raise to allow other cleanup to continue
        
        logger.info("Engram cleanup completed")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities based on current configuration."""
        capabilities = [
            "memory_storage",
            "memory_retrieval",
            "conversation_memory"
        ]
        
        if not self.use_fallback:
            capabilities.extend([
                "vector_search",
                "semantic_similarity"
            ])
        
        if self.use_hermes:
            capabilities.append("hermes_integration")
            
        if self.mcp_bridge:
            capabilities.append("mcp_tools")
        
        return capabilities
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata including storage configuration."""
        metadata = {
            "description": "Memory management system with vector search and semantic similarity",
            "data_directory": str(self.data_dir) if self.data_dir else None,
            "storage_type": "fallback" if self.use_fallback else "vector",
            "vector_support": not self.use_fallback,
            "hermes_integration": self.use_hermes,
            "debug_mode": self.debug_mode,
            "default_client_id": self.default_client_id,
            "memory_manager_initialized": bool(self.memory_manager),
            "mcp_bridge_available": bool(self.mcp_bridge)
        }
        
        # Add storage-specific metadata
        if self.data_dir:
            vector_dir = self.data_dir / "vectors"
            fallback_dir = self.data_dir / "fallback"
            metadata["storage_paths"] = {
                "vector": str(vector_dir) if vector_dir.exists() else None,
                "fallback": str(fallback_dir) if fallback_dir.exists() else None
            }
        
        return metadata