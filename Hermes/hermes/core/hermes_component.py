"""Hermes component implementation using StandardComponentBase."""
import logging
import os
import subprocess
import asyncio
import sys
import atexit
from pathlib import Path
from typing import List, Dict, Any, Optional

from shared.env import TektonEnviron
from shared.utils.standard_component import StandardComponentBase
from shared.utils.env_manager import TektonEnvManager
from shared.urls import tekton_url

logger = logging.getLogger(__name__)


class HermesComponent(StandardComponentBase):
    """Hermes central registration and messaging component."""
    
    def __init__(self):
        super().__init__(component_name="hermes", version="0.1.0")
        self.service_registry = None
        self.message_bus = None
        self.registration_manager = None
        self.database_manager = None
        self.a2a_service = None
        self.mcp_service = None
        self.self_bridge = None
        self.database_mcp_process = None
        self.env_manager = None
        self.initialized = False
        
    async def _pre_init(self):
        """Pre-initialization hook for Hermes."""
        # Load Tekton environment
        self.env_manager = TektonEnvManager()
        self.env_manager.load_environment()
    
    async def _register_with_hermes(self, capabilities: List[str], metadata: Optional[Dict[str, Any]]):
        """Override to skip registration - Hermes doesn't register with itself."""
        self.logger.info("Skipping Hermes self-registration")
        self.global_config.is_registered_with_hermes = False
        
    async def _component_specific_init(self):
        """Initialize Hermes-specific services."""
        # Import here to avoid circular imports
        from hermes.core.service_discovery import ServiceRegistry
        from hermes.core.message_bus import MessageBus
        from hermes.core.registration import RegistrationManager
        from hermes.core.database.manager import DatabaseManager
        from hermes.core.a2a_service import A2AService
        from hermes.core.mcp_service import MCPService
        
        try:
            # Create service registry and message bus instances
            self.service_registry = ServiceRegistry()
            self.message_bus = MessageBus()
            
            # Create registration manager
            self.registration_manager = RegistrationManager(
                service_registry=self.service_registry,
                message_bus=self.message_bus,
                secret_key="tekton-secret-key",
            )
            
            # Create database manager
            self.database_manager = DatabaseManager(
                base_path=os.path.join(TektonEnviron.get('TEKTON_ROOT'), '.tekton', 'data')
            )
            
            # Check environment variable for disabling A2A security
            enable_a2a_security = self.env_manager.get_bool("TEKTON_A2A_ENABLE_SECURITY", True)
            
            # Create A2A service
            self.a2a_service = A2AService(
                service_registry=self.service_registry,
                message_bus=self.message_bus,
                registration_manager=self.registration_manager,
                enable_security=enable_a2a_security
            )
            
            # Create MCP service
            self.mcp_service = MCPService(
                service_registry=self.service_registry,
                message_bus=self.message_bus,
                registration_manager=self.registration_manager,
                database_manager=self.database_manager
            )
            
            # Start service registry health check monitoring
            self.service_registry.start()
            
            # Initialize A2A and MCP services
            await self.a2a_service.initialize()
            await self.mcp_service.initialize()
            
            # Initialize Hermes self-registration bridge
            try:
                from hermes.core.mcp.hermes_self_bridge import HermesSelfBridge
                self.self_bridge = HermesSelfBridge(
                    service_registry=self.service_registry,
                    message_bus=self.message_bus,
                    registration_manager=self.registration_manager,
                    database_manager=self.database_manager
                )
                await self.self_bridge.initialize()
                logger.info("Initialized Hermes self-registration bridge")
            except Exception as e:
                logger.warning(f"Failed to initialize self-registration bridge: {e}")
            
            # Start database MCP server in a separate process
            await self.start_database_mcp_server()
            
            # Register Hermes components with the registration manager
            await self.register_hermes_components()
            
            # Mark as initialized
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing Hermes services: {e}")
            raise
    
    async def register_hermes_components(self):
        """Register all Hermes components with the registration manager."""
        # Register the API server itself
        component_id = "hermes-api"
        success, _ = self.registration_manager.register_component(
            component_id=component_id,
            name="Hermes API Server",
            version="0.1.0",
            component_type="hermes",
            endpoint=tekton_url("hermes", "/api"),
            capabilities=[
                "registration", 
                "service_discovery", 
                "message_bus", 
                "database", 
                "a2a", 
                "mcp"
            ],
            metadata={
                "description": "Central registration and messaging service for Tekton ecosystem"
            }
        )
        
        if success:
            logger.info(f"Hermes API server registered with ID: {component_id}")
        else:
            logger.warning("Failed to register Hermes API server")
        
        # Register the database MCP server
        db_component_id = "hermes-database-mcp"
        db_port = self.config.db_mcp_port if hasattr(self.config, 'db_mcp_port') else int(TektonEnviron.get("DB_MCP_PORT"))
        
        success, _ = self.registration_manager.register_component(
            component_id=db_component_id,
            name="Hermes Database MCP Server",
            version="0.1.0",
            component_type="hermes",
            endpoint=f"http://localhost:{db_port}",
            capabilities=["database", "mcp"],
            metadata={
                "description": "Database services provider for Tekton ecosystem",
                "supported_databases": ["vector", "graph", "key_value", "document", "cache", "relation"]
            }
        )
        
        if success:
            logger.info(f"Database MCP server registered with ID: {db_component_id}")
        else:
            logger.warning("Failed to register Database MCP server")
        
        # Register the A2A service
        a2a_component_id = "hermes-a2a-service"
        
        success, _ = self.registration_manager.register_component(
            component_id=a2a_component_id,
            name="Hermes A2A Service",
            version="0.1.0",
            component_type="hermes",
            endpoint=tekton_url("hermes", "/api/a2a"),
            capabilities=["a2a", "agent_registry", "task_management", "conversation_management"],
            metadata={
                "description": "Agent-to-Agent communication service for Tekton ecosystem"
            }
        )
        
        if success:
            logger.info(f"A2A service registered with ID: {a2a_component_id}")
        else:
            logger.warning("Failed to register A2A service")
        
        # Register the MCP service
        mcp_component_id = "hermes-mcp-service"
        
        success, _ = self.registration_manager.register_component(
            component_id=mcp_component_id,
            name="Hermes MCP Service",
            version="0.1.0",
            component_type="hermes",
            endpoint=tekton_url("hermes", "/api/mcp/v2"),
            capabilities=["mcp", "tool_registry", "message_processing", "context_management"],
            metadata={
                "description": "Multimodal Cognitive Protocol service for Tekton ecosystem"
            }
        )
        
        if success:
            logger.info(f"MCP service registered with ID: {mcp_component_id}")
        else:
            logger.warning("Failed to register MCP service")
    
    async def start_database_mcp_server(self):
        """Start the Database MCP server as a separate process."""
        # Get configuration from environment
        db_mcp_port = self.config.db_mcp_port if hasattr(self.config, 'db_mcp_port') else int(TektonEnviron.get("DB_MCP_PORT"))
        db_mcp_host = TektonEnviron.get("DB_MCP_HOST", "127.0.0.1")
        debug_mode = TektonEnviron.get("DEBUG", "False").lower() == "true"
        
        # Find the script path
        project_root = Path(__file__).parent.parent.parent.parent
        script_path = project_root / "scripts" / "run_database_mcp.py"
        
        if not script_path.exists():
            logger.error(f"Database MCP server script not found at {script_path}")
            return False
        
        # Build command arguments
        cmd = [
            sys.executable,
            str(script_path),
            "--port", str(db_mcp_port),
            "--host", str(db_mcp_host)
        ]
        
        if debug_mode:
            cmd.append("--debug")
        
        try:
            # Start the process
            logger.info(f"Starting Database MCP server: {' '.join(cmd)}")
            self.database_mcp_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Register cleanup function
            atexit.register(self.stop_database_mcp_server)
            
            # Wait a bit for the server to start
            await asyncio.sleep(2)
            
            # Check if the process is still running
            if self.database_mcp_process.poll() is None:
                logger.info("Database MCP server started successfully")
                return True
            else:
                # Process has terminated
                stdout, stderr = self.database_mcp_process.communicate()
                logger.error(f"Database MCP server failed to start: {stderr}")
                return False
        except Exception as e:
            logger.error(f"Error starting Database MCP server: {e}")
            return False
    
    def stop_database_mcp_server(self):
        """Stop the Database MCP server process."""
        if self.database_mcp_process:
            logger.info("Stopping Database MCP server")
            
            try:
                # Send SIGTERM signal
                self.database_mcp_process.terminate()
                
                # Wait for graceful shutdown (max 5 seconds)
                try:
                    self.database_mcp_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if not responding
                    self.database_mcp_process.kill()
                
                logger.info("Database MCP server stopped")
            except Exception as e:
                logger.error(f"Error stopping Database MCP server: {e}")
            
            self.database_mcp_process = None
    
    async def _component_specific_cleanup(self):
        """Cleanup Hermes-specific resources."""
        # Clean up self-registration bridge
        if self.self_bridge:
            try:
                await self.self_bridge.shutdown()
                logger.info("Self-registration bridge cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up self-registration bridge: {e}")
        
        # Stop service registry monitoring
        if self.service_registry:
            self.service_registry.stop()
        
        # Close all database connections
        if self.database_manager:
            await self.database_manager.close_all_connections()
        
        # Stop the database MCP server
        self.stop_database_mcp_server()
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        return [
            "registration",
            "service_discovery",
            "message_bus",
            "database",
            "a2a",
            "mcp",
            "llm"
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        return {
            "description": "Central registration and messaging service for Tekton ecosystem",
            "category": "infrastructure",
            "database_types": ["vector", "graph", "key_value", "document", "cache", "relation"]
        }
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get detailed component status."""
        status = {
            "service_registry": self.service_registry is not None,
            "message_bus": self.message_bus is not None,
            "registration_manager": self.registration_manager is not None,
            "database_manager": self.database_manager is not None,
            "a2a_service": self.a2a_service is not None,
            "mcp_service": self.mcp_service is not None,
            "self_bridge": self.self_bridge is not None,
            "database_mcp_server": self.database_mcp_process is not None and self.database_mcp_process.poll() is None
        }
        
        # Add service counts if available
        if self.service_registry:
            status["registered_services"] = len(self.service_registry.services)
        
        return status
