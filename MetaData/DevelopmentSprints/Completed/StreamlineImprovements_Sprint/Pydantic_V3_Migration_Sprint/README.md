# Pydantic V3 Migration Sprint

## Overview

This sprint focuses on migrating all Tekton components from Pydantic v1/v2 to Pydantic v3 (latest stable release). This migration will eliminate field shadowing warnings, improve performance, and provide access to modern validation features.

## Current State

Issues discovered during GoodLaunch debugging:
- Mix of Pydantic v1 and v2 patterns across components
- Persistent warning: "Field name 'schema' shadows an attribute in parent 'BaseModel'"
- Field annotation errors causing startup failures (Terma MCP capabilities)
- Missing type annotations on inherited fields
- NumPy 2.x compatibility breaking transformers imports (Engram)
- Inconsistent model configuration patterns
- Legacy validation decorators

## Goals

1. **Complete Migration**: All components using Pydantic v3
2. **Zero Warnings**: Eliminate all Pydantic-related warnings
3. **Modern Patterns**: Use latest Pydantic features and best practices
4. **Performance**: Leverage v3's performance improvements

## Implementation Plan

### Phase 1: Assessment & Dependency Audit (0.5 sessions)
- Audit all Pydantic usage across components
- **CRITICAL**: Fix NumPy 2.x compatibility issues (`uv pip install "numpy<2"`)
- Identify v1-specific patterns that need updating
- Pin dependency versions to prevent compatibility issues
- Document breaking changes that affect Tekton

### Phase 2: Core Migration (1 session)
- Update tekton-core dependencies to Pydantic v3
- Fix BaseModel field shadowing issues
- Update validation patterns

### Phase 3: Component Updates (2 sessions)
- Migrate each component systematically
- **Fix Terma-style field annotation errors**: Add type annotations to all inherited fields
- Update model configurations to v3 patterns
- Fix validation decorators and field validators
- Ensure MCP capability classes use proper Pydantic patterns

### Phase 4: Testing & Validation (0.5 sessions)
- Comprehensive testing of all components
- Performance benchmarking
- Documentation updates

## Key Changes

### Field Shadowing Fix
```python
# Old (causing warnings)
class ToolSchema(BaseModel):
    schema: Dict[str, Any]  # Shadows BaseModel.schema

# New (Pydantic v3)
class ToolSchema(BaseModel):
    model_config = ConfigDict(
        # Use alias to avoid shadowing
        fields={'tool_schema': {'alias': 'schema'}}
    )
    tool_schema: Dict[str, Any]
```

### Missing Type Annotations (Terma pattern fix)
```python
# Old (causing "Field 'name' defined on a base class was overridden" errors)
class TerminalCapability(MCPCapability):
    name = "terminal_management"
    description = "Terminal management capability"

# New (Pydantic v3 with proper annotations)
class TerminalCapability(MCPCapability):
    name: str = "terminal_management"
    description: str = "Terminal management capability"
```

### Dependency Compatibility
```python
# requirements.txt updates
numpy<2  # Fix transformers compatibility (Engram issue)
pydantic>=3.0.0,<4.0.0
transformers>=4.0.0  # Compatible with numpy<2
```

### Model Configuration
```python
# Old (Pydantic v1/v2)
class MyModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

# New (Pydantic v3)
class MyModel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
```

### Validators
```python
# Old
@validator('field_name')
def validate_field(cls, v):
    return v

# New
@field_validator('field_name')
def validate_field(cls, v):
    return v
```

## Benefits

1. **Performance**: 5-50x faster validation in v3
2. **Type Safety**: Better mypy integration
3. **Features**: Access to new validation patterns
4. **Future Proof**: Alignment with modern Python ecosystem
5. **Cleaner Code**: Simplified patterns and better errors

## Success Criteria

- [ ] All components on Pydantic v3.x
- [ ] Zero Pydantic-related warnings in logs
- [ ] All tests passing with v3
- [ ] Performance metrics show improvement
- [ ] Documentation updated with v3 patterns

## Risk Mitigation

- Incremental migration by component
- Comprehensive test coverage before/after
- Fallback plan for critical issues
- Parallel testing environment

## Timeline

Total effort: 4 sessions
- Assessment: 0.5 sessions
- Core Migration: 1 session
- Component Updates: 2 sessions
- Testing: 0.5 sessions