# CleanRequirements Implementation Plan

## Overview

This document provides detailed implementation instructions for the CleanRequirements Development Sprint, focusing on systematic dependency optimization across all Tekton components. The plan addresses critical version conflicts, eliminates dependency duplication, and establishes sustainable dependency management practices.

## Phase 1: Critical Conflict Resolution

### Objective
Resolve immediate system-breaking version conflicts that prevent reliable component operation.

### 1.1 Pydantic Version Standardization

**Problem**: Pydantic versions range from 1.9.0 to 2.10.6 causing inter-component communication failures.

**Files to Modify**:
- `tekton-llm-client/requirements.txt`: Currently `pydantic>=1.9.0`
- `Terma/requirements.txt`: Currently `pydantic>=1.10.7`
- All other components: Various `pydantic>=2.x.x` specifications

**Implementation Steps**:
1. **Standardize on Pydantic 2.5.0** across all components
2. **Update tekton-llm-client** to use Pydantic 2.x APIs
3. **Update Terma** to use Pydantic 2.x APIs
4. **Test all component communication** to ensure compatibility

**Standard Version Specification**:
```txt
pydantic>=2.5.0,<3.0.0
```

**API Migration Notes**:
- `BaseModel.dict()` → `BaseModel.model_dump()`
- `BaseModel.parse_obj()` → `BaseModel.model_validate()`
- Field validation syntax updates where needed

### 1.2 Anthropic API Version Standardization

**Problem**: Anthropic versions range from 0.5.0 to 0.10.0 with significant API differences.

**Files to Modify**:
- Components using older Anthropic versions
- LLM adapter implementations

**Implementation Steps**:
1. **Standardize on Anthropic 0.10.0** for consistent API
2. **Update API calls** to use latest Anthropic SDK patterns
3. **Test LLM connectivity** across all components

**Standard Version Specification**:
```txt
anthropic>=0.10.0,<1.0.0
```

### 1.3 WebSocket Version Standardization

**Problem**: WebSocket versions range from 10.3 to 11.0.3 with compatibility issues.

**Implementation Steps**:
1. **Standardize on WebSockets 11.0.3**
2. **Update WebSocket connection logic** if needed
3. **Test real-time communication** between components

**Standard Version Specification**:
```txt
websockets>=11.0.0,<12.0.0
```

### 1.4 Remove Obvious Redundancies

**Engram Flask-Bootstrap Duplication**:
- Remove `flask-bootstrap>=3.3.7.1`
- Keep `bootstrap-flask>=2.3.0`

### 1.5 Phase 1 Testing
- Run `tekton-launch --launch-all` to verify no version conflicts
- Test component communication endpoints
- Verify WebSocket connections work properly

## Phase 2: Dependency Consolidation

### Objective
Create shared dependency packages and eliminate massive duplication across components.

### 2.1 Create Shared Requirements Structure

**Directory Structure**:
```
/shared/requirements/
├── web-common.txt          # FastAPI, uvicorn, websockets, etc.
├── llm-common.txt          # Anthropic, OpenAI, tiktoken, etc.
├── vector-common.txt       # faiss-cpu, sentence-transformers, torch
├── data-common.txt         # pandas, numpy (where needed)
├── testing-common.txt      # pytest, testing utilities
└── development-common.txt  # Development tools
```

### 2.2 Web Framework Consolidation

**Create `/shared/requirements/web-common.txt`**:
```txt
# Web Framework Stack - Standardized Versions
fastapi>=0.105.0,<1.0.0
uvicorn>=0.24.0,<1.0.0
pydantic>=2.5.0,<3.0.0
websockets>=11.0.0,<12.0.0
python-dotenv>=1.0.0,<2.0.0
aiohttp>=3.9.0,<4.0.0
httpx>=0.25.0,<1.0.0
```

**Components to Update** (15+ components):
- Apollo, Athena, Budget, Engram, Ergon, Harmonia, Hermes, etc.
- Replace individual web dependencies with: `-r ../shared/requirements/web-common.txt`

### 2.3 LLM Integration Consolidation

**Create `/shared/requirements/llm-common.txt`**:
```txt
# LLM Integration Stack - Standardized Versions
anthropic>=0.10.0,<1.0.0
openai>=1.1.0,<2.0.0
tiktoken>=0.4.0,<1.0.0
litellm>=1.0.0,<2.0.0
```

**Components to Update**:
- Components using LLM APIs: Apollo, Budget, Ergon, Hermes, LLMAdapter, Terma, etc.

### 2.4 Vector Processing Consolidation

**Problem**: Vector stack (`faiss-cpu`, `sentence-transformers`, `torch`) duplicated across 3+ components.

**Option A: Extend tekton-core**
Add vector processing to `tekton-core/requirements.txt`:
```txt
# Vector Processing Stack
faiss-cpu>=1.7.4,<2.0.0
sentence-transformers>=2.2.2,<3.0.0
torch>=1.10.0,<2.0.0
```

**Option B: Create vector-common.txt**
```txt
# Vector Processing Stack
faiss-cpu>=1.7.4,<2.0.0
sentence-transformers>=2.2.2,<3.0.0
torch>=1.10.0,<2.0.0
numpy>=1.20.0,<2.0.0  # Required by vector libraries
```

**Components to Update**:
- Engram, Hermes, tekton-core
- Remove individual vector dependencies
- Add single reference to consolidated package

### 2.5 Component Requirements Updates

**Template for Updated Component requirements.txt**:
```txt
# Component Name Requirements

# Core Tekton Dependencies
tekton-core>=0.1.0
tekton-llm-client>=0.1.0

# Shared Dependencies
-r ../shared/requirements/web-common.txt
-r ../shared/requirements/llm-common.txt

# Component-Specific Dependencies
[component-specific packages only]
```

### 2.6 Data Science Stack Optimization

**Components with pandas/scipy**:
- Consider if full pandas is needed or if lighter alternatives work
- Consolidate where genuine need exists
- Remove where unused

**Create `/shared/requirements/data-common.txt`**:
```txt
# Data Science Stack (use sparingly)
pandas>=2.0.0,<3.0.0
numpy>=1.20.0,<2.0.0
scipy>=1.10.0,<2.0.0
matplotlib>=3.5.0,<4.0.0
```

## Phase 3: Architecture Optimization

### Objective
Implement sustainable dependency management patterns with optional dependencies and clear separation.

### 3.1 Production/Development Separation

**Create requirements-dev.txt for each component**:
```txt
# Development Dependencies
-r requirements.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
```

**Move to requirements-dev.txt**:
- Testing frameworks (`pytest`, `pytest-asyncio`)
- Code formatting tools (`black`, `isort`)
- Type checking (`mypy`)
- Development utilities

### 3.2 Optional Heavy Dependencies

**Pattern for Optional Dependencies**:
```python
# In component code
try:
    import faiss
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    
def search_vectors(query, vectors):
    if VECTOR_SEARCH_AVAILABLE:
        return _faiss_search(query, vectors)
    else:
        return _python_cosine_search(query, vectors)
```

**Requirements with Optional Sections**:
```txt
# Core Requirements
tekton-core>=0.1.0

# Optional: Vector Processing
# Uncomment for full vector capabilities
# faiss-cpu>=1.7.4,<2.0.0
# sentence-transformers>=2.2.2,<3.0.0
```

### 3.3 Dependency Injection Patterns

**Service Pattern for Heavy Dependencies**:
```python
class EmbeddingService:
    def __init__(self, use_transformers=True):
        if use_transformers:
            self.encoder = SentenceTransformersEncoder()
        else:
            self.encoder = SimpleEmbeddingEncoder()
```

### 3.4 Version Constraint Standards

**Establish Version Constraint Patterns**:
- **Major version pinning**: `>=X.Y.0,<(X+1).0.0`
- **Security updates allowed**: Patch version flexibility
- **Breaking change protection**: Major version boundaries

**Documentation in `/shared/requirements/README.md`**:
- Version constraint rationale
- Upgrade procedures
- Conflict resolution guidelines

## Phase 4: Testing and Validation

### Objective
Comprehensive testing and performance validation of optimized dependency structure.

### 4.1 Functionality Testing

**Component Launch Testing**:
```bash
# Test individual component launches
./scripts/tekton-launch apollo
./scripts/tekton-launch ergon
./scripts/tekton-launch engram

# Test full system launch
./scripts/tekton-launch --launch-all
```

**Inter-Component Communication Testing**:
- Test API endpoints between components
- Verify WebSocket connections
- Test LLM adapter functionality

### 4.2 Performance Benchmarking

**Install Time Measurement**:
```bash
# Before optimization
time pip install -r requirements.txt

# After optimization  
time pip install -r requirements.txt
```

**Disk Usage Measurement**:
```bash
# Measure site-packages size before/after
du -sh venv/lib/python*/site-packages/
```

**Memory Usage Testing**:
- Component startup memory footprint
- Runtime memory usage patterns

### 4.3 Regression Testing

**Functionality Preservation**:
- All existing API endpoints work
- All component features function properly
- No performance degradation in core operations

### 4.4 Documentation Updates

**Update Component Documentation**:
- Installation instructions with new requirements structure
- Development setup with requirements-dev.txt
- Dependency management guidelines

**Create Dependency Management Guide**:
- How to add new dependencies
- Version constraint guidelines
- Conflict resolution procedures

## Implementation Guidelines

### Code Quality Standards
- All changes maintain existing functionality
- Proper error handling for optional dependencies
- Clear documentation for new patterns

### Testing Requirements
- Component functionality tests pass
- Integration tests with other components
- Performance benchmarks show improvement

### Documentation Standards
- Update all affected README files
- Document new dependency patterns
- Create migration guides for developers

## Expected Outcomes

### Quantitative Results
- **60-70% reduction** in total dependency footprint
- **40-50% faster** installation times
- **4-6GB savings** in disk usage
- **Zero version conflicts** across components

### Qualitative Improvements
- **Consistent dependency management** across all components
- **Easier maintenance** through centralized requirements
- **Better developer experience** with clear dependency patterns
- **Future-proof architecture** for sustainable growth

## Rollback Strategy

### Backup Plan
- Maintain backup of all original requirements.txt files
- Document all changes for easy reversal
- Test rollback procedures before major changes

### Risk Mitigation
- Incremental implementation with testing at each step
- Ability to revert individual components if issues arise
- Clear separation between phases for isolated rollback