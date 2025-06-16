# Sprint Insights Addendum - Additional Recommendations

## CleanRequirements_Sprint Phase 2 Enhancement Ideas

### Shared Requirements Structure
Consider a tiered approach:
1. **Core Requirements** (`requirements-core.txt`) - Used by all components
   - pydantic>=2.0
   - fastapi
   - uvicorn
   - Basic shared utilities

2. **Feature Requirements** (`requirements-features.txt`) - Optional features
   - Vector stores (faiss, chromadb)
   - LLM providers (anthropic, openai)
   - Specialized libraries

3. **Component Overrides** - Only for specific needs
   - Component-specific versions if absolutely necessary
   - Should be minimal and well-documented

### Benefits
- Single source of truth for versions
- Easier Pydantic v2/v3 migration
- Reduced conflicts between components
- Simplified dependency management

## MCP_External_Integration_Sprint Enhancement Ideas

### Centralized Registration Pattern
```python
# In Ergon or a shared module
class MCPRegistry:
    """Central registry for all MCP tools and capabilities."""
    
    @classmethod
    def register_tool(cls, tool_func, **kwargs):
        """Validate and register a tool with consistent pattern."""
        # Validate function signature
        # Create MCPTool with proper schema structure
        # Handle registration errors gracefully
        
    @classmethod
    def register_capability(cls, capability_class):
        """Register capability with validation."""
        # Ensure it's a class
        # Create instance with proper initialization
        # Add to capability registry
```

### Registration Validation
- Check for duplicate names
- Validate schema structure
- Ensure proper parameter types
- Provide clear error messages

## Future Sprint: Consistent Error Handling

### Standardized Error Classes
```python
# In shared module
class TektonError(Exception):
    """Base error for all Tekton components."""
    component: str
    error_code: str
    
class StartupError(TektonError):
    """Component failed to start."""
    
class RegistrationError(TektonError):
    """Failed to register with Hermes."""
```

### Error Propagation Pattern
- Log locally with component context
- Report to Hermes for system-wide visibility
- Provide actionable error messages
- Include troubleshooting hints

## Future Sprint: Debugging Infrastructure

### Startup Diagnostics
1. **Pre-flight Checks**
   - Verify all dependencies importable
   - Check required services available
   - Validate configuration
   
2. **Health Check Standardization**
   - Every component implements `/health`
   - Returns structured status info
   - Includes dependency status

3. **Timeout Investigation**
   - Add startup progress logging
   - Report what step is hanging
   - Configurable timeout with clear messaging

### Debug Mode
- Environment variable `TEKTON_DEBUG=1`
- Verbose logging during startup
- Step-by-step initialization reporting
- Performance timing for each startup phase

## Integration Recommendations

These sprints work together:
1. **Clean Requirements** makes version management consistent
2. **MCP Integration** standardizes component interfaces  
3. **Error Handling** makes failures diagnosable
4. **Debug Infrastructure** prevents "silent" timeouts

The combination would dramatically improve the launch reliability we're working toward in GoodLaunch Sprint.