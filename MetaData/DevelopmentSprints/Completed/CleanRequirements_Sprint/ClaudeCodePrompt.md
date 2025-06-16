# CleanRequirements Sprint - Claude Code Prompt

## Overview

This document serves as the initial prompt for a Claude Code session working on the CleanRequirements Development Sprint for the Tekton project. This sprint focuses on comprehensive dependency optimization to resolve critical version conflicts, eliminate massive dependency duplication, and establish sustainable dependency management practices.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on dependency optimization that will reduce the overall dependency footprint by 60-70% while resolving system-breaking compatibility issues.

## Sprint Context

You are taking over a CleanRequirements Development Sprint that addresses critical dependency management issues discovered through comprehensive analysis of all 23+ requirements.txt files across the Tekton project. The analysis revealed severe version conflicts, massive dependency duplication, and unsustainable dependency management practices that are preventing reliable system operation.

## Critical Issues to Address

### 1. System-Breaking Version Conflicts

**Pydantic Version Conflicts (Critical)**:
- Range: 1.9.0 → 2.10.6 across components
- Impact: Inter-component communication failures
- Files: `tekton-llm-client/requirements.txt` (1.9.0), `Terma/requirements.txt` (1.10.7), others (2.x)
- Solution: Standardize on Pydantic 2.5.0 across all components

**Anthropic API Version Conflicts**:
- Range: 0.5.0 → 0.10.0 with significant API differences
- Impact: LLM integration inconsistencies
- Solution: Standardize on Anthropic 0.10.0

**WebSocket Version Conflicts**:
- Range: 10.3 → 11.0.3 with compatibility issues
- Impact: Real-time communication problems
- Solution: Standardize on WebSockets 11.0.3

### 2. Massive Dependency Duplication

**Vector Processing Stack** (~6GB redundant):
- `faiss-cpu`, `sentence-transformers`, `torch` duplicated in Engram, Hermes, tekton-core
- Strategy: Consolidate into shared requirements or enhance tekton-core

**Data Science Stack** (~2GB redundant):
- `numpy`, `pandas`, `scipy` duplicated across 4+ components
- Strategy: Evaluate necessity and consolidate where legitimate

**Web Framework Stack**:
- `fastapi`, `uvicorn`, `pydantic`, `websockets` with different versions across 15+ components
- Strategy: Create shared web-common.txt requirements

### 3. Dependency Management Issues

**Immediate Cleanup Opportunities**:
- Engram has both `flask-bootstrap>=3.3.7.1` AND `bootstrap-flask>=2.3.0` (redundant)
- Development dependencies mixed with production requirements
- Missing version pinning causing unpredictable behavior
- Loose version constraints (`>=`) leading to conflicts

## Implementation Strategy

### Phase 1: Critical Conflict Resolution (Current Priority)

**Immediate Actions**:
1. **Fix Pydantic conflicts** - Standardize all components to `pydantic>=2.5.0,<3.0.0`
2. **Update API usage** in tekton-llm-client and Terma for Pydantic 2.x compatibility
3. **Standardize Anthropic** to `anthropic>=0.10.0,<1.0.0` across components
4. **Standardize WebSockets** to `websockets>=11.0.0,<12.0.0`
5. **Remove Engram redundancy** - Remove `flask-bootstrap>=3.3.7.1`, keep `bootstrap-flask>=2.3.0`

**Pydantic 2.x Migration Notes**:
- `BaseModel.dict()` → `BaseModel.model_dump()`
- `BaseModel.parse_obj()` → `BaseModel.model_validate()`
- Update field validation syntax as needed

**Testing After Phase 1**:
- Run `tekton-launch --launch-all` to verify no version conflicts
- Test component communication to ensure Pydantic compatibility
- Verify WebSocket connections work properly

### Phase 2: Dependency Consolidation

**Create Shared Requirements Structure**:
```
/shared/requirements/
├── web-common.txt          # FastAPI ecosystem
├── llm-common.txt          # LLM integration stack  
├── vector-common.txt       # Vector processing stack
├── data-common.txt         # Data science stack
├── testing-common.txt      # Testing utilities
└── development-common.txt  # Development tools
```

**Consolidation Targets**:

1. **Web Framework Stack** (`/shared/requirements/web-common.txt`):
```txt
fastapi>=0.105.0,<1.0.0
uvicorn>=0.24.0,<1.0.0
pydantic>=2.5.0,<3.0.0
websockets>=11.0.0,<12.0.0
python-dotenv>=1.0.0,<2.0.0
aiohttp>=3.9.0,<4.0.0
httpx>=0.25.0,<1.0.0
```

2. **LLM Integration Stack** (`/shared/requirements/llm-common.txt`):
```txt
anthropic>=0.10.0,<1.0.0
openai>=1.1.0,<2.0.0
tiktoken>=0.4.0,<1.0.0
litellm>=1.0.0,<2.0.0
```

3. **Vector Processing Stack** (`/shared/requirements/vector-common.txt`):
```txt
faiss-cpu>=1.7.4,<2.0.0
sentence-transformers>=2.2.2,<3.0.0
torch>=1.10.0,<2.0.0
```

**Component Updates**:
Update component requirements.txt files to use shared dependencies:
```txt
# Component Requirements
tekton-core>=0.1.0
tekton-llm-client>=0.1.0

# Shared Dependencies
-r ../shared/requirements/web-common.txt
-r ../shared/requirements/llm-common.txt

# Component-Specific Dependencies
[only truly unique packages]
```

### Phase 3: Architecture Optimization

**Production/Development Separation**:
- Create `requirements-dev.txt` files for development dependencies
- Move testing, formatting, and development tools out of production requirements

**Optional Dependency Patterns**:
- Implement graceful degradation for heavy dependencies
- Create dependency injection patterns for better modularity

## Files to Modify

### High Priority (Phase 1):
- `tekton-llm-client/requirements.txt` - Pydantic 1.9.0 → 2.5.0
- `Terma/requirements.txt` - Pydantic 1.10.7 → 2.5.0  
- `Engram/requirements.txt` - Remove flask-bootstrap redundancy
- All components using Anthropic - Standardize to 0.10.0
- All components using WebSockets - Standardize to 11.0.3

### Medium Priority (Phase 2):
- All 23+ component requirements.txt files
- Create `/shared/requirements/` directory and files
- Update component requirements to reference shared files

### Component-Specific API Updates:
- **tekton-llm-client**: Update Pydantic 1.x API calls to 2.x
- **Terma**: Update Pydantic 1.x API calls to 2.x
- **Components using Anthropic**: Update to 0.10.0 API patterns

## Success Criteria

### Phase 1 Success:
- [ ] Zero version conflicts when running `tekton-launch --launch-all`
- [ ] All components use Pydantic 2.5.0+ with working API calls
- [ ] Consistent Anthropic and WebSocket versions across components
- [ ] Successful component communication and WebSocket connections

### Phase 2 Success:
- [ ] Shared requirements structure created and implemented
- [ ] 60-70% reduction in total dependency footprint
- [ ] All components load shared dependencies successfully
- [ ] No functionality regression in any component

### Overall Success:
- [ ] Faster installation times (40-50% improvement)
- [ ] Significant disk usage reduction (4-6GB savings)
- [ ] Maintainable dependency management structure
- [ ] Documentation for ongoing dependency management

## Key Tekton Context

### Project Structure:
- **Components**: Apollo, Athena, Budget, Codex, Engram, Ergon, Harmonia, Hephaestus, Hermes, LLMAdapter, Metis, Prometheus, Rhetor, Sophia, Synthesis, Telos, Terma
- **Core Packages**: `tekton-core`, `tekton-llm-client`
- **Branch**: `sprint/Clean_Slate_051125`

### Launch System:
- Use `tekton-launch --launch-all` to test full system
- Individual component testing: `tekton-launch <component>`
- Port assignments in `/config/port_assignments.md`

### Dependency Patterns:
- Most components use FastAPI + uvicorn for web services
- Many components integrate with LLM APIs (Anthropic, OpenAI)
- Vector processing components use faiss-cpu + sentence-transformers
- Inter-component communication relies on consistent Pydantic models

## Development Approach

### Recommended Order:
1. **Start with Phase 1** - Fix critical version conflicts first
2. **Test thoroughly** after each major change
3. **Create shared requirements** incrementally
4. **Update components systematically** to use shared dependencies
5. **Document changes** for future maintenance

### Testing Strategy:
- Test individual component launches after dependency changes
- Verify inter-component communication works properly
- Run full system launch tests regularly
- Check for functionality regressions

### Code Quality:
- Maintain all existing functionality
- Use proper version constraints (avoid loose `>=` specifications)
- Document any API changes required for version compatibility
- Follow Tekton coding standards and practices

## Expected Outcomes

### Immediate Benefits:
- System stability through elimination of version conflicts
- Faster development through consistent dependency versions
- Reduced installation and disk usage

### Long-term Benefits:
- Sustainable dependency management practices
- Easier maintenance and upgrades
- Better performance and resource utilization
- Clear patterns for future component development

## Important Notes

### Compatibility:
- Ensure all existing functionality is preserved
- Test component communication thoroughly after Pydantic updates
- Verify WebSocket and LLM integrations work properly

### Performance:
- Shared dependencies should improve install times
- Monitor for any performance regressions
- Benchmark before and after optimization

### Maintenance:
- Document new dependency management patterns
- Create guidelines for adding future dependencies
- Establish version upgrade procedures

This sprint will establish Tekton as having best-in-class dependency management with significant performance benefits and long-term maintainability. Focus on incremental implementation with thorough testing at each phase.