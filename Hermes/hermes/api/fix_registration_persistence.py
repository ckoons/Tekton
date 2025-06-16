"""
Fix for Hermes registration persistence issue.

The problem: get_registration_manager() creates a new instance on every request,
so registrations disappear immediately.

The solution: Use FastAPI's app.state to maintain a singleton instance.
"""

# Here's what needs to change in endpoints.py:

# OLD CODE (creates new instance each time):
"""
def get_registration_manager():
    service_registry = ServiceRegistry()
    message_bus = MessageBus()
    service_registry.start()
    return RegistrationManager(
        service_registry=service_registry,
        message_bus=message_bus,
        secret_key="tekton-secret-key"
    )
"""

# NEW CODE (singleton pattern):
"""
# At module level, create singleton instances
_service_registry = None
_message_bus = None
_registration_manager = None

def get_registration_manager():
    global _service_registry, _message_bus, _registration_manager
    
    if _registration_manager is None:
        # Create singleton instances
        _service_registry = ServiceRegistry()
        _message_bus = MessageBus()
        
        # Start health check monitoring
        _service_registry.start()
        
        _registration_manager = RegistrationManager(
            service_registry=_service_registry,
            message_bus=_message_bus,
            secret_key="tekton-secret-key"
        )
        
        logger.info("Created singleton RegistrationManager")
    
    return _registration_manager
"""

# ALTERNATIVE SOLUTION using FastAPI's app.state:
"""
@app.on_event("startup")
async def startup_event():
    # Create singleton instances at startup
    app.state.service_registry = ServiceRegistry()
    app.state.message_bus = MessageBus()
    app.state.service_registry.start()
    
    app.state.registration_manager = RegistrationManager(
        service_registry=app.state.service_registry,
        message_bus=app.state.message_bus,
        secret_key="tekton-secret-key"
    )
    
    logger.info("Hermes registration system initialized")

def get_registration_manager(request: Request):
    return request.app.state.registration_manager
"""