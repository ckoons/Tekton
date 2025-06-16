# CleanRequirements Sprint - Phase 2 Claude Code Prompt

## Overview

This document serves as the Claude Code prompt for **Phase 2** of the CleanRequirements Development Sprint for the Tekton project. Phase 2 focuses on **dependency consolidation** to achieve the target 60-70% reduction in overall dependency footprint while maintaining all functionality.

**IMPORTANT**: This is Phase 2 of an ongoing sprint. Phase 1 (Critical Conflict Resolution) has been completed successfully. All system-breaking version conflicts have been resolved and the system is now stable.

## Phase 1 Completion Summary

### ✅ **What Was Already Completed in Phase 1**
1. **Fixed all critical version conflicts**:
   - Pydantic standardized to 2.5.0 across all components
   - Anthropic standardized to 0.10.0 across components  
   - WebSockets standardized to 11.0.3 across components
   - Removed dependency redundancy (flask-bootstrap conflicts)

2. **Updated 43+ API calls** for Pydantic v2 compatibility
3. **System successfully launches** with `tekton-launch --launch-all`
4. **Zero version conflicts** during startup
5. **All 14 components operational** and communicating properly

**DO NOT** repeat Phase 1 work. The system is now stable and ready for consolidation.

## Phase 2 Objectives

The goal of Phase 2 is to **consolidate redundant dependencies** across Tekton's 17+ components to achieve:

- **60-70% reduction** in total dependency footprint
- **4-6GB disk usage savings**
- **40-50% faster installation times**
- **Maintainable dependency management structure**
- **No functionality regression**

## Current Dependency Landscape

### Components Overview (23+ requirements.txt files):
- **Core Components**: Apollo, Athena, Budget, Codex, Engram, Ergon, Harmonia, Hephaestus, Hermes, LLMAdapter, Metis, Prometheus, Rhetor, Sophia, Synthesis, Telos, Terma
- **Core Packages**: tekton-core, tekton-llm-client
- **Branch**: `sprint/Clean_Slate_051125` (all changes committed)

### Major Consolidation Targets

#### 1. **Vector Processing Stack** (~6GB redundant savings potential)
**Current Duplication**: `faiss-cpu`, `sentence-transformers`, `torch` duplicated in:
- Engram, Hermes, tekton-core, Sophia, Ergon
- **Strategy**: Consolidate into `shared/requirements/vector-common.txt`

#### 2. **Data Science Stack** (~2GB redundant savings potential) 
**Current Duplication**: `numpy`, `pandas`, `scipy` duplicated across:
- Sophia, Engram, Budget, Apollo (4+ components)
- **Strategy**: Evaluate necessity and consolidate legitimate usage

#### 3. **Web Framework Stack** (15+ components affected)
**Current Duplication**: `fastapi`, `uvicorn`, `pydantic`, `websockets` with **consistent versions** across:
- Apollo, Athena, Budget, Ergon, Harmonia, Hermes, LLMAdapter, Metis, Prometheus, Rhetor, Sophia, Synthesis, Telos, Terma, etc.
- **Strategy**: Create `shared/requirements/web-common.txt`

#### 4. **LLM Integration Stack** (4+ components)
**Current Duplication**: `anthropic`, `openai`, `tiktoken`, `litellm` across:
- Rhetor, tekton-llm-client, Ergon, LLMAdapter
- **Strategy**: Create `shared/requirements/llm-common.txt`

## Implementation Strategy for Phase 2

### **Create Shared Requirements Structure**

#### Target Structure:
```
/shared/requirements/
├── web-common.txt          # FastAPI ecosystem (15+ components)
├── llm-common.txt          # LLM integration stack (4+ components)
├── vector-common.txt       # Vector processing stack (5+ components)
├── data-common.txt         # Data science stack (4+ components)
├── testing-common.txt      # Testing utilities
└── development-common.txt  # Development tools
```

#### Implementation Steps:

1. **Create `/shared/requirements/` directory structure**

2. **Analyze and consolidate Web Framework Stack** (`/shared/requirements/web-common.txt`):
   ```txt
   fastapi>=0.105.0,<1.0.0
   uvicorn>=0.24.0,<1.0.0
   pydantic>=2.5.0,<3.0.0
   websockets>=11.0.3,<12.0.0
   python-dotenv>=1.0.0,<2.0.0
   aiohttp>=3.9.0,<4.0.0
   httpx>=0.25.0,<1.0.0
   ```

3. **Consolidate LLM Integration Stack** (`/shared/requirements/llm-common.txt`):
   ```txt
   anthropic>=0.10.0,<1.0.0
   openai>=1.1.0,<2.0.0
   tiktoken>=0.4.0,<1.0.0
   litellm>=1.0.0,<2.0.0
   ```

4. **Consolidate Vector Processing Stack** (`/shared/requirements/vector-common.txt`):
   ```txt
   faiss-cpu>=1.7.4,<2.0.0
   sentence-transformers>=2.2.2,<3.0.0
   torch>=1.10.0,<2.0.0
   numpy>=1.24.0,<2.0.0
   ```

5. **Update Component Requirements** to use shared dependencies:
   ```txt
   # Component Requirements Template
   tekton-core>=0.1.0
   tekton-llm-client>=0.1.0
   
   # Shared Dependencies
   -r ../shared/requirements/web-common.txt
   -r ../shared/requirements/llm-common.txt
   
   # Component-Specific Dependencies
   [only truly unique packages]
   ```

### **Component Update Priority**

#### **High Priority** (Web Framework - Most Components):
- Apollo, Athena, Budget, Ergon, Harmonia, Hermes, LLMAdapter, Metis, Prometheus, Rhetor, Sophia, Synthesis, Telos, Terma

#### **Medium Priority** (Vector Processing - Highest Savings):
- Engram, Hermes, tekton-core, Sophia, Ergon

#### **Lower Priority** (Data Science - Evaluate First):
- Sophia, Engram, Budget, Apollo

#### **Specialized** (Development/Testing):
- Codex, Hephaestus (may need custom handling)

## Safety and Testing Requirements

### **Critical Safety Measures**:
1. **Maintain all existing functionality** - No regression testing
2. **Preserve component isolation** - Components must work independently
3. **Gradual implementation** - Update component groups systematically
4. **Test after each major change** - Verify system launches successfully
5. **Rollback capability** - Keep original requirements as backups

### **Testing Strategy**:
1. **After creating each shared requirements file**: Test affected components individually
2. **After updating component groups**: Run `tekton-launch --launch-all`
3. **Verify functionality**: Test component communication and key features
4. **Monitor for regressions**: Check for any broken functionality

### **Success Validation**:
- [ ] System launches successfully with `tekton-launch --launch-all`
- [ ] All components maintain their existing functionality
- [ ] No new version conflicts introduced
- [ ] Significant reduction in total dependency count
- [ ] Faster installation times (measurable improvement)

## Key Tekton Context

### **Project Structure** (Unchanged from Phase 1):
- **Components**: Apollo, Athena, Budget, Codex, Engram, Ergon, Harmonia, Hephaestus, Hermes, LLMAdapter, Metis, Prometheus, Rhetor, Sophia, Synthesis, Telos, Terma
- **Core Packages**: `tekton-core`, `tekton-llm-client`
- **Branch**: `sprint/Clean_Slate_051125`

### **Current System State**:
- ✅ **Stable and operational** - All components launch successfully
- ✅ **Consistent versions** - Critical conflicts resolved
- ✅ **Ready for consolidation** - No blocking issues

### **Launch Testing**:
- Use `tekton-launch --launch-all` to test full system
- Individual component testing: `tekton-launch <component>`
- Port assignments in `/config/port_assignments.md`

## Development Approach for Phase 2

### **Recommended Order**:
1. **Start with Web Framework Stack** (affects most components, lowest risk)
2. **Move to LLM Integration Stack** (medium complexity, clear boundaries)  
3. **Tackle Vector Processing Stack** (highest savings, medium complexity)
4. **Evaluate Data Science Stack** (may need selective consolidation)
5. **Address Development/Testing dependencies** (create separate dev requirements)

### **Per-Stack Process**:
1. **Analyze current usage** across all components
2. **Create shared requirements file** with verified compatible versions
3. **Update 2-3 components** to use shared requirements (test group)
4. **Test the test group** thoroughly with individual and system launches
5. **Roll out to remaining components** in batches
6. **Validate full system** functionality

### **Quality Assurance**:
- Test individual component launches after each change
- Verify inter-component communication works properly  
- Run full system launch tests regularly
- Document any issues and rollback if necessary
- Follow Tekton coding standards and practices

## Expected Phase 2 Outcomes

### **Immediate Benefits**:
- **60-70% reduction** in redundant dependencies
- **4-6GB disk space savings**
- **40-50% faster installation times**
- **Simplified dependency management**

### **Long-term Benefits**:
- **Sustainable dependency management** practices
- **Easier maintenance and upgrades**
- **Clear patterns** for future component development
- **Reduced complexity** for new developers

## Important Notes

### **What NOT to Change**:
- **Do not modify** component functionality or APIs
- **Do not change** the existing system architecture
- **Do not remove** dependencies that are actually needed
- **Do not break** component isolation

### **Compatibility Requirements**:
- **Preserve all existing functionality**
- **Maintain component communication**
- **Keep all integrations working**
- **Ensure graceful degradation** where applicable

### **Documentation Requirements**:
- **Document** the new shared requirements structure
- **Create guidelines** for future dependency management
- **Update README** files with new dependency installation instructions
- **Record** any compatibility notes or special considerations

## Files to Focus On (Phase 2)

### **New Files to Create**:
- `/shared/requirements/web-common.txt`
- `/shared/requirements/llm-common.txt`
- `/shared/requirements/vector-common.txt`
- `/shared/requirements/data-common.txt`
- `/shared/requirements/testing-common.txt`
- `/shared/requirements/development-common.txt`
- `/shared/requirements/README.md` (documentation)

### **Files to Modify** (Update to use shared requirements):
- **All component `requirements.txt` files** (17+ files)
- **Component README files** (update installation instructions)
- **Root-level documentation** (update dependency management docs)

## Sprint Handoff Information

### **Phase 1 Completion Status**:
- ✅ All Phase 1 objectives achieved
- ✅ System stable and tested
- ✅ Ready for Phase 2 implementation
- ✅ No blocking issues identified

### **Current System Health**:
- **Version conflicts**: None (resolved in Phase 1)
- **System launch**: Successful (all 14 components)
- **Component communication**: Working properly
- **Dependency consistency**: Achieved for critical packages

### **Phase 2 Prerequisites Met**:
- ✅ Stable foundation established
- ✅ Compatible versions standardized
- ✅ Testing framework in place
- ✅ Rollback capability available

---

**Ready to begin Phase 2 dependency consolidation when testing period is complete.**

This sprint will establish Tekton as having best-in-class dependency management with significant performance benefits and long-term maintainability while maintaining 100% functionality.