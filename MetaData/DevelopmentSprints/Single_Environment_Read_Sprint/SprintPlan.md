# Single Environment Read Sprint Plan

## Sprint Duration
Estimated: 2-3 days
Actual: Failed - Overcomplicated the solution

## Problem Statement

Tekton's environment configuration is read from multiple places at unpredictable times:
- 714+ direct calls to os.environ
- Module-level initialization reads environment during imports
- Singleton patterns freeze configuration at first access
- No control over when environment is read

This prevents:
- Multi-environment support (Coder-A/B/C)
- Remote Tekton instances
- Consistent configuration across components
- Predictable behavior

## LESSONS LEARNED

### What Went Wrong
1. **Overcomplicated TektonEnviron**: Added complex state management, singleton patterns, and "clever" subprocess detection
2. **Fought Python's Nature**: Tried to maintain state across process boundaries when only os.environ is inherited
3. **Serial Coding**: Made changes without thinking through the full solution
4. **Module-Level Execution**: Didn't properly handle Python's import-time code execution

### Root Cause
- Python subprocesses get fresh interpreter state (all class variables reset)
- Only os.environ is inherited from parent
- TektonEnviron's `_loaded` flag and `_data` dict don't transfer to subprocesses
- Any "clever" caching or state management fails at process boundaries

## CORRECT APPROACH

### Simplified Solution

1. **Keep TektonEnviron SIMPLE**:
   ```python
   class TektonEnviron:
       """Simple wrapper around os.environ after main script sets it up"""
       
       @classmethod
       def get(cls, key: str, default: str = None) -> str:
           """Get from os.environ - no caching, no state"""
           return os.environ.get(key, default)
       
       @classmethod
       def get_int(cls, key: str, default: int = 0) -> int:
           """Get int from os.environ"""
           try:
               return int(os.environ.get(key, str(default)))
           except ValueError:
               return default
   ```

2. **Main script (tekton) does ALL setup**:
   - Parse arguments
   - Set TEKTON_ROOT based on --coder
   - Load .env files in correct order
   - Set os.environ directly
   - Launch subprocesses

3. **Everything else is read-only**:
   - Import TektonEnviron
   - Call get() methods
   - No loading, no state, no caching

4. **Fix module-level imports**:
   - Remove ALL os.environ access at module level
   - Move environment reads to function/method level
   - Or use lazy initialization patterns

### Correct Phase Approach

### Phase 1: Simple TektonEnviron
- Create shared/env.py as a SIMPLE wrapper around os.environ
- NO state management, NO loading logic
- Just typed accessors that read os.environ

### Phase 2: Main Script Setup
- tekton script handles ALL environment loading
- Parse args → Set ROOT → Load envs → Update os.environ
- Then launch subprocesses with correct environment

### Phase 3: Remove Module-Level Reads
- Find all module-level os.environ access
- Move to function-level or lazy init
- Especially in component_config.py, env_config.py

### Phase 4: Gradual Migration
- Replace os.environ.get() with TektonEnviron.get()
- One module at a time
- Test each change

## Technical Decisions

1. **No Caching**: Configuration is read when needed, not cached
2. **Explicit Loading**: Environment loaded explicitly, not at import
3. **Backward Compatible**: freeze_to_environ() maintains os.environ compatibility
4. **Type Safety**: Typed accessors prevent string/int confusion
5. **Single Import**: Only TektonEnviron knows about os.environ

## Risk Mitigation

1. **Gradual Migration**: Phase approach allows incremental changes
2. **Backward Compatibility**: Existing code continues working
3. **Testing**: Each phase can be tested independently
4. **Reversion**: Changes can be reverted if issues arise

## Key Implementation Rules

1. **NO module-level environment access** - Python executes module code at import time
2. **NO state in TektonEnviron** - Just a thin wrapper around os.environ
3. **NO clever subprocess detection** - Subprocesses inherit os.environ, that's enough
4. **NO singletons or caching** - They don't work across process boundaries
5. **Main script sets up EVERYTHING** - All other code just reads

## Definition of Done

- [ ] Simple TektonEnviron wrapper implemented (no state, no loading)
- [ ] tekton script properly loads all .env files and sets os.environ
- [ ] All module-level os.environ access removed
- [ ] Configuration modules use lazy initialization
- [ ] Multi-environment support (--coder) works reliably
- [ ] No complex state management or caching
- [ ] Tests pass with multiple environments