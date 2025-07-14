# Architectural Decisions - Single Environment Read Sprint

## Core Principle

**Environment configuration must be read ONCE at program start, then remain immutable.**

## REVISED After Failed Attempt

### What We Learned

1. **Python subprocess reality**: Subprocesses get fresh Python interpreter state. Class variables don't transfer.
2. **Only os.environ transfers**: Between processes, only os.environ is inherited, not Python object state.
3. **Module-level execution kills you**: Python runs module-level code at import time, before you can control anything.
4. **Clever is the enemy**: Every "clever" optimization (singletons, caching, state management) breaks at process boundaries.

## Revised Key Decisions

### 1. No Singleton Caching

**Decision**: Remove all singleton patterns for configuration objects.

**Rationale**: 
- Singletons capture state at unpredictable times
- Once created, they never update even if environment changes
- Import order determines behavior (race condition)
- "Clever" optimization that costs more than it saves

**Implementation**:
```python
# OLD (Broken)
_component_config = None
def get_component_config():
    global _component_config
    if _component_config is None:
        _component_config = ComponentConfig()  # Frozen forever
    return _component_config

# NEW (Simple)
def get_component_config():
    return ComponentConfig()  # Fresh read every time
```

### 2. TektonEnviron as SIMPLE Wrapper

**Decision**: TektonEnviron is just a thin wrapper around os.environ with NO state.

**Rationale**:
- Subprocesses can't inherit Python state, only os.environ
- No caching means no stale data
- No loading logic means no timing issues
- Dead simple means no bugs

**Implementation**:
```python
class TektonEnviron:
    @classmethod
    def get(cls, key: str, default: str = None) -> str:
        return os.environ.get(key, default)
```

That's it. No state. No loading. No cleverness.

### 3. Explicit Load Order

**Decision**: Environment loading follows explicit sequence:
1. Parse command line arguments
2. Set TEKTON_ROOT based on arguments
3. Load environment from that root
4. Freeze to os.environ for subprocesses
5. Execute command

**Rationale**:
- Predictable behavior
- Command line overrides everything
- Subprocesses inherit correct environment
- No surprises from import order

### 4. No Premature Optimization

**Decision**: Read configuration when needed, don't cache.

**Rationale**:
- Configuration reads are fast (microseconds)
- Caching adds complexity and bugs
- Debugging cached state is painful
- Optimize only after profiling shows need

### 5. Main Script Owns Environment Setup

**Decision**: ONLY the main entry point (tekton script) loads and configures environment.

**Rationale**:
- Single place to debug environment issues
- Subprocesses inherit correctly configured os.environ
- No race conditions or import-order dependencies
- Clear, predictable flow

**Implementation**:
- tekton script loads .env files and updates os.environ
- ALL other code just reads from os.environ (via TektonEnviron wrapper)
- NO other module tries to load or configure environment

## Anti-Patterns to Eliminate

1. **Module-Level Reads**
   ```python
   # BAD
   PORT = int(os.environ.get('PORT', 8000))  # Runs at import
   ```

2. **Singleton Configuration**
   ```python
   # BAD
   _config = None
   def get_config():
       global _config
       if not _config:
           _config = load_config()  # Frozen forever
   ```

3. **Constructor Reads**
   ```python
   # BAD
   class Component:
       def __init__(self):
           self.port = os.environ.get('PORT')  # Too early
   ```

4. **Scattered Defaults**
   ```python
   # BAD
   port = os.environ.get('PORT', 8000)  # Default in 100 places
   ```

## Benefits

1. **Predictable Behavior**: Environment read once, behavior determined at startup
2. **Multi-Environment Support**: --coder option works reliably
3. **Remote Support**: Can point to non-localhost instances
4. **Easier Debugging**: One place to set breakpoints
5. **Cleaner Code**: No clever tricks, just simple functions

## Trade-offs

1. **Slight Performance Cost**: Reading config multiple times vs caching
   - Mitigation: Profile first, optimize only if needed
   
2. **More Function Calls**: get_component_config() called more often
   - Mitigation: Still microseconds, not a real issue
   
3. **Breaking Change**: Existing code expects singletons
   - Mitigation: Phased approach, backward compatibility

## Conclusion

By eliminating "clever" patterns and returning to simple, predictable code, we gain reliability, maintainability, and the ability to support multiple environments. The performance cost is negligible compared to the debugging time saved.