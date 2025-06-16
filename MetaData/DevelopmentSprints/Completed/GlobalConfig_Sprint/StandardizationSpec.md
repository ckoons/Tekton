# Standardization Specification - GlobalConfig Sprint

## Expanded Scope

This sprint now encompasses two major standardization efforts:

### 1. Global Configuration Management

**Goal**: Create a single source of truth for all configuration values across Tekton.

**Implementation**:
```python
# shared/utils/global_config.py
class GlobalConfig:
    """Singleton configuration manager for all Tekton components."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._load_configuration()
            self._initialized = True
    
    def _load_configuration(self):
        """Load all configuration from env_config once."""
        config = get_component_config()
        
        # Ports
        self.ports = {
            'hermes': config.hermes.port if hasattr(config, 'hermes') else int(os.environ.get('HERMES_PORT', 8001)),
            'rhetor': config.rhetor.port if hasattr(config, 'rhetor') else int(os.environ.get('RHETOR_PORT', 8003)),
            'apollo': config.apollo.port if hasattr(config, 'apollo') else int(os.environ.get('APOLLO_PORT', 8012)),
            # ... all other components
        }
        
        # URLs
        self.urls = {
            'hermes': f"http://localhost:{self.ports['hermes']}",
            'rhetor': f"http://localhost:{self.ports['rhetor']}",
            # ... all other components
        }
        
        # Other configuration
        self.timeouts = {...}
        self.limits = {...}
        self.features = {...}

# Global instance
GLOBAL_CONFIG = GlobalConfig()
```

### 2. Standardized Component Initialization

**Goal**: Extract common initialization patterns into a reusable base.

**Implementation**:
```python
# shared/utils/standard_component.py
class StandardComponentBase:
    """Base class for all Tekton components."""
    
    def __init__(self, component_name: str, version: str, description: str):
        self.component_name = component_name
        self.version = version
        self.description = description
        self.logger = setup_component_logging(component_name)
        self.config = GLOBAL_CONFIG
        self.port = self.config.ports[component_name]
        
        # Standard state
        self.is_registered_with_hermes = False
        self.start_time = None
        self.hermes_registration = None
        self.heartbeat_task = None
        
    async def startup(self):
        """Standard startup sequence."""
        self.start_time = time.time()
        
        # Register with Hermes
        await self._register_with_hermes()
        
        # Component-specific initialization
        await self.initialize_component()
        
        # Start heartbeat
        if self.is_registered_with_hermes:
            self._start_heartbeat()
    
    async def initialize_component(self):
        """Override in subclass for component-specific init."""
        raise NotImplementedError
    
    def create_app(self) -> FastAPI:
        """Create FastAPI app with standard configuration."""
        app = FastAPI(
            **get_openapi_configuration(
                component_name=self.component_name,
                component_version=self.version,
                component_description=self.description
            ),
            lifespan=self._lifespan
        )
        
        # Add standard middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Create and mount standard routers
        routers = create_standard_routers(self.component_name)
        mount_standard_routers(app, routers, self)
        
        return app
    
    def health_check(self):
        """Standard health check implementation."""
        return create_health_response(
            component_name=self.component_name,
            port=self.port,
            version=self.version,
            status="healthy" if self.is_healthy() else "unhealthy",
            registered=self.is_registered_with_hermes,
            details=self.get_health_details()
        )
    
    def is_healthy(self) -> bool:
        """Override in subclass."""
        return True
    
    def get_health_details(self) -> dict:
        """Override in subclass."""
        return {}
```

## What Changes for Each Component

### Before:
```python
# rhetor/__main__.py
config = get_component_config()
port = config.rhetor.port if hasattr(config, 'rhetor') else int(os.environ.get("RHETOR_PORT"))

# rhetor/api/app.py
COMPONENT_NAME = "rhetor"
COMPONENT_VERSION = "0.1.0"
rhetor_port = None
is_registered_with_hermes = False
# ... many globals

async def lifespan(app: FastAPI):
    # Lots of boilerplate initialization
```

### After:
```python
# rhetor/__main__.py
from shared.utils.standard_component import StandardComponentBase
from shared.utils.global_config import GLOBAL_CONFIG

class Rhetor(StandardComponentBase):
    async def initialize_component(self):
        # Only Rhetor-specific initialization
        self.llm_client = LLMClient()
        await self.llm_client.initialize()
        # ... other Rhetor-specific setup
    
    def is_healthy(self):
        return self.llm_client and self.llm_client.is_initialized
    
    def get_health_details(self):
        return {
            "llm_client": self.llm_client is not None,
            # ... other Rhetor-specific health details
        }

# Main execution
if __name__ == "__main__":
    rhetor = Rhetor("rhetor", "0.1.0", "LLM orchestration service")
    app = rhetor.create_app()
    
    # Run with existing socket server
    run_component_server(
        component_name="rhetor",
        app_module=app,
        default_port=GLOBAL_CONFIG.ports['rhetor'],
        reload=False
    )
```

## Benefits

1. **Configuration**: Single source of truth, no scattered variables
2. **Consistency**: All components follow the same pattern
3. **Maintainability**: Changes to common functionality in one place
4. **Reliability**: Proven patterns reduce bugs
5. **Simplicity**: New components are trivial to create

## Migration Strategy

1. Implement GlobalConfig and StandardComponentBase
2. Start with Rhetor (most complex, known issues)
3. Verify Rhetor works completely
4. Systematically migrate each component
5. Run full integration tests after each
6. Document any exceptions or special cases