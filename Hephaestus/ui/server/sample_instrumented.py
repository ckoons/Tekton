"""
Sample instrumented Python module

This demonstrates how to use the debug instrumentation in a Python module.
"""

from debug_utils import debug_log, log_function, LogLevel

class SampleService:
    """Sample service demonstrating debug instrumentation"""
    
    @log_function(level=LogLevel.INFO)
    def __init__(self, name, config=None):
        """Initialize the service with optional configuration"""
        self.name = name
        self.config = config or {}
        self.initialized = False
        
        debug_log.debug("SampleService", f"Created service: {name}", self.config)
    
    @log_function()
    def initialize(self):
        """Initialize the service"""
        if self.initialized:
            debug_log.debug("SampleService", "Already initialized")
            return True
            
        debug_log.info("SampleService", "Initializing service", self.config)
        
        try:
            # Simulate initialization work
            self._connect_to_resources()
            self._load_data()
            
            self.initialized = True
            debug_log.info("SampleService", "Service initialized successfully")
            return True
        except Exception as e:
            debug_log.exception("SampleService", "Failed to initialize service")
            return False
    
    def _connect_to_resources(self):
        """Connect to external resources"""
        debug_log.debug("SampleService", "Connecting to resources")
        
        # Simulate connection logic
        for resource, config in self.config.get("resources", {}).items():
            try:
                debug_log.trace("SampleService", f"Connecting to {resource}", config)
                # Connection code would go here
                debug_log.debug("SampleService", f"Connected to {resource}")
            except Exception as e:
                debug_log.error("SampleService", f"Failed to connect to {resource}", {
                    "error": str(e),
                    "config": config
                })
                raise
    
    def _load_data(self):
        """Load initial data"""
        debug_log.debug("SampleService", "Loading initial data")
        
        # Simulate data loading
        data_sources = self.config.get("data_sources", [])
        
        if not data_sources:
            debug_log.warn("SampleService", "No data sources configured")
            return
            
        for source in data_sources:
            debug_log.trace("SampleService", f"Loading data from {source}")
            # Data loading code would go here
    
    @log_function()
    def process_request(self, request_id, data):
        """Process a sample request"""
        debug_log.info("SampleService", f"Processing request {request_id}", {
            "data_size": len(data) if data else 0
        })
        
        if not self.initialized:
            debug_log.warn("SampleService", "Service not initialized, initializing now")
            if not self.initialize():
                debug_log.error("SampleService", "Cannot process request, initialization failed")
                return {"status": "error", "message": "Service initialization failed"}
        
        try:
            # Request validation
            if not data:
                debug_log.warn("SampleService", "Empty request data")
                return {"status": "error", "message": "Empty request data"}
                
            # Process the request (example)
            result = self._compute_result(data)
            
            debug_log.info("SampleService", f"Request {request_id} processed successfully", {
                "result_type": type(result).__name__
            })
            
            return {"status": "success", "result": result}
        except Exception as e:
            debug_log.exception("SampleService", f"Error processing request {request_id}")
            return {"status": "error", "message": str(e)}
    
    def _compute_result(self, data):
        """Compute result from input data"""
        debug_log.debug("SampleService", "Computing result", {
            "data_type": type(data).__name__
        })
        
        # Decision point with detailed logging
        if isinstance(data, dict):
            debug_log.trace("SampleService", "Processing dictionary data")
            # Processing logic
            return {"processed": True, "keys": list(data.keys())}
        elif isinstance(data, list):
            debug_log.trace("SampleService", "Processing list data")
            # Processing logic
            return {"processed": True, "count": len(data)}
        else:
            debug_log.debug("SampleService", f"Unrecognized data type: {type(data).__name__}")
            return {"processed": False, "error": "Unsupported data type"}


# Example usage
if __name__ == "__main__":
    # Turn on debugging for demonstration
    debug_log.set_enabled(True)
    debug_log.default_level = LogLevel.DEBUG
    
    # Create and use the service
    service = SampleService("demo-service", {
        "resources": {
            "database": {"url": "postgres://localhost/demo"},
            "cache": {"type": "redis", "url": "localhost:6379"}
        },
        "data_sources": ["users", "products"]
    })
    
    # Process some requests
    response1 = service.process_request("req-001", {"user": "john", "action": "search"})
    print(f"Response 1: {response1}")
    
    response2 = service.process_request("req-002", ["item1", "item2", "item3"])
    print(f"Response 2: {response2}")
    
    # Demonstrate error handling
    try:
        # Force an error
        debug_log.debug("main", "Forcing an error to demonstrate exception handling")
        result = 1 / 0
    except Exception as e:
        debug_log.exception("main", "Caught division by zero error")