# ByeByeNumPy Sprint - Implementation Plan

## Overview

This document outlines the detailed implementation plan for the ByeByeNumPy Development Sprint. It breaks down the high-level goals into specific implementation tasks, defines the phasing, specifies testing requirements, and identifies documentation that must be updated.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Implementation Plan focuses on eliminating NumPy/SciPy dependencies while preserving functionality.

## Debug Instrumentation Requirements

All code produced in this sprint **MUST** follow the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md).

### Python Components

The following Python components must be instrumented during modification:

| Component | Log Level | Notes |
|-----------|-----------|-------|
| Ergon Embedding Service | INFO | Log embedding method selection and performance |
| Apollo Predictive Engine | DEBUG | Log statistical calculations and predictions |
| Hermes Vector Engine | INFO | Log dependency cleanup and fallback usage |
| Requirements Files | INFO | Log dependency changes during cleanup |

All instrumentation must use the `debug_log` utility:

```python
from shared.debug.debug_utils import debug_log, log_function

debug_log.info("component_name", "NumPy dependency eliminated", {"method": "openai_api"})
```

Key methods should use the `@log_function` decorator for performance tracking:

```python
@log_function()
def pure_python_statistical_function(data):
    # Implementation
```

## Implementation Tasks

### Phase 1: Analysis and Preparation

#### Task 1.1: Dependency Analysis
**Description**: Comprehensive analysis of actual NumPy usage vs. declared dependencies

**Steps**:
1. Scan all Python files for actual `numpy`, `scipy`, `sentence_transformers` imports
2. Identify which components declare but don't use ML dependencies
3. Map actual usage patterns to replacement strategies
4. Document current API contracts that must be preserved

**Files to Analyze**:
- `/Ergon/ergon/core/memory/services/embedding.py`
- `/Ergon/ergon/core/memory/services/vector_store.py`
- `/Apollo/apollo/core/predictive_engine.py`
- `/Hermes/hermes/core/vector_engine.py`
- All `requirements.txt` files

**Acceptance Criteria**:
- Complete mapping of NumPy usage by component
- List of pure Python replacement strategies
- API preservation plan documented

#### Task 1.2: Test Coverage Assessment
**Description**: Identify existing test coverage for functionality to be modified

**Steps**:
1. Review existing tests for embedding services
2. Review existing tests for statistical functions
3. Identify gaps in test coverage
4. Plan new tests for replacement implementations

**Files to Review**:
- `/Ergon/tests/core/memory/`
- `/Apollo/tests/core/`
- `/Hermes/tests/core/`

**Acceptance Criteria**:
- Test coverage assessment complete
- Plan for maintaining test coverage with new implementations
- Identification of additional tests needed

### Phase 2: Ergon Refactoring

#### Task 2.1: Embedding Service Refactoring
**Description**: Replace sentence-transformers with OpenAI API and remove NumPy dependency

**Steps**:
1. Modify `/Ergon/ergon/core/memory/services/embedding.py`:
   - Remove `import numpy as np` 
   - Remove sentence-transformers fallback logic
   - Enhance OpenAI embedding path to be primary
   - Add fallback to simple text hashing if OpenAI unavailable
2. Update `/Ergon/ergon/core/memory/services/vector_store.py`:
   - Remove NumPy array operations
   - Replace with pure Python list operations
   - Maintain same interface for callers

**Files to Modify**:
- `/Ergon/ergon/core/memory/services/embedding.py`: Remove NumPy, enhance OpenAI path
- `/Ergon/ergon/core/memory/services/vector_store.py`: Replace NumPy arrays with lists
- `/Ergon/requirements.txt`: Remove sentence-transformers and numpy

**Acceptance Criteria**:
- Embedding service works without NumPy/sentence-transformers
- OpenAI embeddings are primary method
- Graceful fallback when OpenAI unavailable
- Same API interface maintained
- All existing tests pass

#### Task 2.2: Vector Store Simplification
**Description**: Replace FAISS-based vector operations with simple similarity search

**Steps**:
1. Implement cosine similarity in pure Python
2. Replace vector store with simple in-memory storage
3. Maintain search interface but use linear search
4. Add performance warnings for large datasets

**Files to Modify**:
- `/Ergon/ergon/core/vector_store/faiss_store.py`: Simplify to pure Python
- `/Ergon/ergon/core/memory/services/vector_store.py`: Update vector operations

**Acceptance Criteria**:
- Vector operations work without FAISS
- Search functionality preserved (with performance notes)
- Memory usage reduced
- Startup time improved

### Phase 3: Apollo Refactoring

#### Task 3.1: Statistical Functions Replacement
**Description**: Replace SciPy statistical functions with pure Python implementations

**Steps**:
1. Replace `scipy.stats` functions in `/Apollo/apollo/core/predictive_engine.py`:
   - Implement mean, standard deviation, percentiles in pure Python
   - Replace statistical tests with simple threshold checks
   - Implement basic trend analysis without NumPy
2. Remove NumPy array operations
3. Maintain prediction interface and accuracy

**Files to Modify**:
- `/Apollo/apollo/core/predictive_engine.py`: Replace SciPy with pure Python stats
- `/Apollo/requirements.txt`: Remove scipy and numpy

**Implementation Details**:
```python
# Replace scipy.stats.norm with pure Python
def calculate_percentile(data, percentile):
    sorted_data = sorted(data)
    index = (percentile / 100) * (len(sorted_data) - 1)
    # Implementation details...

def calculate_moving_average(data, window_size):
    # Pure Python moving average
    # Implementation details...
```

**Acceptance Criteria**:
- All statistical functions work without SciPy
- Prediction accuracy maintained within reasonable bounds
- Error handling improved with clearer messages
- Performance acceptable for Tekton's use cases

#### Task 3.2: Prediction Model Simplification
**Description**: Simplify prediction models to use basic statistical methods

**Steps**:
1. Replace complex statistical models with:
   - Simple moving averages
   - Basic trend detection
   - Threshold-based alerts
2. Maintain prediction interface
3. Add clear documentation about simplified approach

**Files to Modify**:
- `/Apollo/apollo/core/predictive_engine.py`: Simplify models
- `/Apollo/apollo/models/prediction.py`: Update prediction schemas if needed

**Acceptance Criteria**:
- Prediction models work without NumPy/SciPy
- Basic functionality preserved
- Clear documentation of limitations
- Performance improved

### Phase 4: Hermes and Cleanup

#### Task 4.1: Hermes Dependency Cleanup
**Description**: Remove unused ML dependencies from Hermes

**Steps**:
1. Remove sentence-transformers from Hermes requirements
2. Update any import statements that reference unused libraries
3. Simplify vector engine if it exists

**Files to Modify**:
- `/Hermes/requirements.txt`: Remove unused ML dependencies
- `/Hermes/hermes/core/vector_engine.py`: Simplify or remove if unused

**Acceptance Criteria**:
- Hermes starts without ML dependencies
- Functionality preserved
- Cleaner dependency tree

#### Task 4.2: Global Requirements Cleanup
**Description**: Clean up ML dependencies from all component requirements files

**Steps**:
1. Review all `requirements.txt` files for unnecessary ML libraries
2. Remove NumPy, SciPy, sentence-transformers from components that don't need them
3. Keep dependencies in components that actually need them (Sophia, etc.)
4. Update any setup.py files that reference removed dependencies

**Files to Modify**:
- `/*/requirements.txt`: Remove unused ML dependencies
- `/*/setup.py`: Update dependency lists

**Acceptance Criteria**:
- Only components that need ML libraries have them in requirements
- Sophia and Engram retain their ML capabilities
- All other components have cleaner dependencies

### Phase 5: Testing and Validation

#### Task 5.1: Component Testing
**Description**: Comprehensive testing of modified components

**Steps**:
1. Run existing unit tests for all modified components
2. Run integration tests between components
3. Test the full system startup with `tekton-launch --launch-all`
4. Verify performance improvements

**Testing Commands**:
```bash
# Test individual components
cd Ergon && python -m pytest tests/
cd Apollo && python -m pytest tests/
cd Hermes && python -m pytest tests/

# Test system startup
tekton-launch --launch-all

# Performance testing
time tekton-launch --components ergon
time tekton-launch --components apollo
```

**Acceptance Criteria**:
- All existing tests pass
- System startup succeeds without NumPy errors
- Performance metrics show improvement
- Functionality verification complete

#### Task 5.2: Integration Testing
**Description**: Test inter-component communication with new implementations

**Steps**:
1. Test Ergon memory operations with other components
2. Test Apollo predictions integration
3. Verify MCP endpoints still work
4. Test component discovery and registration

**Acceptance Criteria**:
- All component interactions work as before
- MCP integration preserved
- Service discovery functional
- Error handling improved

## Testing Requirements

### Unit Testing
- Run all existing unit tests and ensure they pass
- Add new unit tests for pure Python implementations
- Test error handling and fallback scenarios

### Integration Testing
- Test component startup sequence
- Verify inter-component communication
- Test system behavior when external services (OpenAI) unavailable

### Performance Testing
- Measure startup time improvements
- Verify memory usage reduction
- Document any performance trade-offs

## Documentation Updates

### MUST Update
- `/Ergon/README.md`: Document embedding service changes
- `/Apollo/README.md`: Document statistical function changes
- `/MetaData/ComponentDocumentation/Ergon/TECHNICAL_DOCUMENTATION.md`: Update dependency info
- `/MetaData/ComponentDocumentation/Apollo/TECHNICAL_DOCUMENTATION.md`: Update technical details

### CAN Update
- Component API documentation if interfaces change
- Performance benchmarks in component docs
- Troubleshooting guides with new error scenarios

## Risk Mitigation

### Implementation Risks
1. **API Breaking Changes**: Maintain existing interfaces as much as possible
2. **Performance Regression**: Benchmark critical paths before and after
3. **Functionality Loss**: Test existing feature coverage extensively

### Rollback Plan
- Keep original implementation as comments initially
- Tag commit before major changes
- Document how to re-enable ML dependencies if needed

## Success Metrics

1. **System Startup**: `tekton-launch --launch-all` completes successfully
2. **Dependency Reduction**: 50%+ reduction in ML dependencies across components
3. **Performance**: 25%+ improvement in component startup times
4. **Memory Usage**: Reduced memory footprint for non-ML components
5. **Error Rate**: Zero NumPy compatibility errors in logs

## Deliverables

1. **Modified Components**: Ergon, Apollo, Hermes with NumPy dependencies removed
2. **Updated Requirements**: Clean requirements.txt files across all components
3. **Test Coverage**: All existing tests passing plus new tests for changes
4. **Documentation**: Updated technical documentation
5. **Performance Report**: Before/after performance comparison
6. **Migration Guide**: Instructions for reverting changes if needed