# ByeByeNumPy Sprint - Claude Code Prompt

## Overview

This document serves as the initial prompt for a Claude Code session working on the ByeByeNumPy Development Sprint for the Tekton project. This sprint focuses on eliminating NumPy/SciPy dependencies from Tekton components to resolve compatibility issues and improve system reliability.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on dependency optimization and compatibility resolution by removing problematic ML dependencies while preserving functionality.

## Sprint Context

**Sprint Goal**: Eliminate NumPy/SciPy dependencies causing component startup failures while maintaining all existing functionality

**Current Phase**: Phase 1: Complete dependency elimination and implementation

**Branch Name**: `sprint/Clean_Slate_051125` (reusing current branch)

## Required Reading

Before beginning implementation, please thoroughly review the following documents:

1. **General Development Sprint Process**: `/MetaData/DevelopmentSprints/README.md`
2. **Sprint Plan**: `/MetaData/DevelopmentSprints/ByeByeNumPy_Sprint/SprintPlan.md`
3. **Implementation Plan**: `/MetaData/DevelopmentSprints/ByeByeNumPy_Sprint/ImplementationPlan.md`
4. **Debug Instrumentation Guidelines**: `/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md`
5. **Tekton Development Notes**: `/CLAUDE.md`

## Branch Verification (CRITICAL)

Before making any changes, verify you are working on the correct branch:

```bash
git branch --show-current
```

Ensure the output matches: `sprint/Clean_Slate_051125`

If you are not on the correct branch, please do not proceed until this is resolved.

## Background Context

### Current State
A previous Claude Code session has identified and partially fixed several Tekton issues:
- ✅ **MCP Import Fixes**: All missing MCP modules have been created
- ✅ **Port Assignments**: Sophia and Budget port configurations added  
- ✅ **Hephaestus Launcher**: Created run_ui.sh script

### Critical Remaining Issue
**NumPy Compatibility Crisis**: Components Ergon and Apollo fail to start due to NumPy 1.x/2.x compatibility conflicts in SciPy and sentence-transformers libraries.

**Error Pattern**:
```
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.5 as it may crash.
ImportError: numpy.core.multiarray failed to import
```

## Implementation Instructions

Follow the detailed implementation plan to systematically eliminate NumPy dependencies. **The goal is to remove NumPy entirely, not fix version conflicts.**

### Task 1: Dependency Analysis

**Description**: Analyze actual NumPy usage vs. declared dependencies across affected components

**Steps**:
1. Examine `/Ergon/ergon/core/memory/services/embedding.py` - uses NumPy for embedding operations
2. Examine `/Apollo/apollo/core/predictive_engine.py` - uses SciPy for statistical analysis  
3. Map usage patterns to pure Python alternatives
4. Document current API contracts that must be preserved

**Files to Analyze**:
- `/Ergon/ergon/core/memory/services/embedding.py`
- `/Ergon/ergon/core/memory/services/vector_store.py`  
- `/Apollo/apollo/core/predictive_engine.py`
- All component `requirements.txt` files

**Acceptance Criteria**:
- Complete mapping of actual NumPy usage
- Pure Python replacement strategy documented
- API preservation plan created

### Task 2: Ergon Embedding Service Refactoring

**Description**: Replace sentence-transformers with OpenAI API primary path and remove NumPy dependency

**Steps**:
1. Modify `/Ergon/ergon/core/memory/services/embedding.py`:
   - Remove `import numpy as np`
   - Remove sentence-transformers dependency and fallback logic
   - Make OpenAI embeddings the primary method
   - Add simple text hashing fallback if OpenAI unavailable
   - Add debug instrumentation for embedding method selection

2. Update `/Ergon/ergon/core/memory/services/vector_store.py`:
   - Remove NumPy array operations
   - Replace with pure Python list operations  
   - Implement cosine similarity in pure Python
   - Maintain same interface for callers

3. Clean up requirements:
   - Remove `sentence-transformers` from `/Ergon/requirements.txt` 
   - Remove `numpy` from `/Ergon/requirements.txt`

**Files to Modify**:
- `/Ergon/ergon/core/memory/services/embedding.py`: Remove NumPy, enhance OpenAI path
- `/Ergon/ergon/core/memory/services/vector_store.py`: Replace NumPy arrays with lists
- `/Ergon/requirements.txt`: Remove sentence-transformers and numpy

**Implementation Example**:
```python
# Pure Python cosine similarity
def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    return dot_product / (magnitude1 * magnitude2) if magnitude1 and magnitude2 else 0.0
```

**Acceptance Criteria**:
- Embedding service works without NumPy/sentence-transformers
- OpenAI embeddings are primary method
- Graceful fallback when OpenAI unavailable
- Same API interface maintained
- Debug logging for method selection

### Task 3: Apollo Statistical Functions Replacement

**Description**: Replace SciPy statistical functions with pure Python implementations

**Steps**:
1. Replace `scipy.stats` functions in `/Apollo/apollo/core/predictive_engine.py`:
   - Implement mean, standard deviation, percentiles in pure Python
   - Replace statistical tests with simple threshold checks
   - Implement basic trend analysis without NumPy
   - Add debug instrumentation for calculations

2. Remove NumPy array operations
3. Maintain prediction interface and reasonable accuracy

**Files to Modify**:
- `/Apollo/apollo/core/predictive_engine.py`: Replace SciPy with pure Python stats
- `/Apollo/requirements.txt`: Remove scipy and numpy

**Implementation Example**:
```python
def calculate_percentile(data, percentile):
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = (percentile / 100) * (len(sorted_data) - 1)
    lower_index = int(index)
    upper_index = min(lower_index + 1, len(sorted_data) - 1)
    weight = index - lower_index
    return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight

def calculate_moving_average(data, window_size):
    if len(data) < window_size:
        return sum(data) / len(data) if data else 0.0
    return sum(data[-window_size:]) / window_size
```

**Acceptance Criteria**:
- All statistical functions work without SciPy
- Prediction accuracy maintained within reasonable bounds
- Error handling improved with clearer messages
- Performance acceptable for Tekton's use cases

### Task 4: Requirements Cleanup

**Description**: Remove unused ML dependencies from all components

**Steps**:
1. Review all component `requirements.txt` files
2. Remove NumPy, SciPy, sentence-transformers from components that don't need them
3. Keep dependencies in components that actually need them (Sophia, Engram if needed)
4. Update any `setup.py` files that reference removed dependencies

**Files to Modify**:
- `/Ergon/requirements.txt`: Remove ML dependencies
- `/Apollo/requirements.txt`: Remove ML dependencies  
- `/Hermes/requirements.txt`: Remove unused ML dependencies
- `/*/requirements.txt`: Review and clean up as needed

**Acceptance Criteria**:
- Only components that need ML libraries have them in requirements
- Cleaner dependency trees across components
- No unused dependencies declared

### Task 5: Testing and Validation

**Description**: Comprehensive testing of modified components and system startup

**Steps**:
1. Test individual component functionality
2. Test system startup: `tekton-launch --launch-all`
3. Verify performance improvements
4. Ensure existing functionality preserved

**Testing Commands**:
```bash
# Test system startup (primary success criteria)
tekton-launch --launch-all

# Test individual components if needed
cd Ergon && python -c "from ergon.core.memory.services.embedding import embedding_service; print('Ergon OK')"
cd Apollo && python -c "from apollo.core.predictive_engine import PredictiveEngine; print('Apollo OK')"
```

**Acceptance Criteria**:
- `tekton-launch --launch-all` completes without NumPy errors
- All components start successfully  
- Existing functionality preserved
- Performance improvements measurable

## Testing Requirements

After implementing the changes, perform the following tests:

1. **Primary Success Test**:
   ```bash
   tekton-launch --launch-all
   ```
   This should complete without any NumPy compatibility errors

2. **Component Import Testing**:
   - Test that modified components can import without errors
   - Verify embedding services work with OpenAI API
   - Confirm statistical functions work with pure Python

3. **Integration Testing**:
   - Test component interactions still work
   - Verify MCP endpoints respond correctly 
   - Check service discovery functionality

## Documentation Updates

Update the following documentation as part of this implementation:

1. **MUST Update**:
   - `/Ergon/README.md`: Document embedding service changes and OpenAI requirement
   - `/Apollo/README.md`: Document statistical function simplification
   - `/MetaData/ComponentDocumentation/Ergon/TECHNICAL_DOCUMENTATION.md`: Update dependency info
   - `/MetaData/ComponentDocumentation/Apollo/TECHNICAL_DOCUMENTATION.md`: Update technical details

2. **CAN Update** (if time permits):
   - Performance benchmarks in component docs
   - Troubleshooting guides with new error scenarios

## Deliverables

Upon completion of this sprint, produce the following deliverables:

1. **Code Changes**:
   - Ergon and Apollo components with NumPy dependencies removed
   - Pure Python implementations of statistical and embedding functions
   - Clean requirements.txt files across all components
   - Debug instrumentation following Tekton guidelines

2. **Status Report**:
   - Create `/MetaData/DevelopmentSprints/ByeByeNumPy_Sprint/StatusReports/Phase1Status.md`
   - Include summary of completed work
   - Document performance improvements achieved  
   - List any challenges encountered
   - Provide before/after system startup comparison

3. **Documentation Updates**:
   - All specified documentation changes
   - Clear notes about simplified implementations
   - Migration guide for reverting changes if needed

## Success Criteria

This sprint is successful when:

1. **`tekton-launch --launch-all` completes successfully** without NumPy errors
2. **All components start** without import failures
3. **Functionality preserved** - existing features still work
4. **Dependencies reduced** - NumPy/SciPy removed from non-ML components
5. **Performance improved** - faster startup times measurable

## Emergency Rollback

If critical functionality is broken, preserve ability to rollback:
- Keep original implementations as comments initially
- Document how to restore ML dependencies if absolutely necessary
- Tag commits for easy rollback points

## Code Style and Practices

Follow Tekton's established guidelines:

1. **Python Code Style**:
   - Use f-strings for string formatting
   - Add type hints to function signatures  
   - Follow PEP 8 guidelines
   - Use docstrings for all functions and classes

2. **Debug Instrumentation**:
   ```python
   from shared.debug.debug_utils import debug_log, log_function
   
   debug_log.info("component_name", "NumPy dependency eliminated", {"method": "pure_python"})
   ```

3. **Error Handling**:
   - Graceful fallbacks when external services unavailable
   - Clear error messages about simplified implementations
   - Appropriate logging levels for different scenarios

## Questions and Clarifications

If you encounter any blocking issues:

1. **API Preservation**: If maintaining exact API compatibility is impossible, document the changes clearly
2. **Performance Concerns**: If pure Python implementations are too slow, implement with performance warnings
3. **Missing Dependencies**: If you need additional libraries, choose lightweight pure Python alternatives

## Final Note

This sprint directly addresses the critical NumPy compatibility issues preventing Tekton system startup. Success means the system will launch cleanly and components will be more maintainable going forward. Focus on getting the system working first, then optimize for performance and elegance.

The previous session has already fixed MCP imports, port assignments, and created the Hephaestus launcher. Your mission is to eliminate the NumPy compatibility crisis and get `tekton-launch --launch-all` working successfully.