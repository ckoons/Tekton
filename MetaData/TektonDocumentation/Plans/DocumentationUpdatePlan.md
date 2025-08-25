# Tekton Documentation Update Plan

*Created: January 2025*

## Overview

This document outlines the comprehensive plan to update Tekton documentation to reflect current architecture, new features, and deprecated components.

## Priority Levels

- 🔴 **HIGH**: Critical updates blocking user understanding or containing incorrect information
- 🟡 **MEDIUM**: Important updates for consistency and completeness
- 🟢 **LOW**: Enhancements and nice-to-have improvements

## 🔴 HIGH PRIORITY Updates

### 1. Fix Deprecated Component References

**Issue**: Main README.md references "Agenteer" instead of "Ergon"
**Files**: 
- `/README.md` (line 20)
**Action**: 
- Replace "Agenteer" with "Ergon"
- Update any related references in other files

### 2. Document New Core Features

#### 2.1 Landmarks System
**Current State**: Basic README exists but lacks integration guide
**Action Items**:
- Create `/MetaData/TektonDocumentation/Guides/LandmarksIntegrationGuide.md`
- Add examples of landmark usage in components
- Document landmark types and their purposes
- Include code examples for adding landmarks to new components

#### 2.2 CI Specialists
**Current State**: Feature is implemented but poorly documented
**Action Items**:
- Create `/MetaData/TektonDocumentation/Guides/AISpecialistsGuide.md`
- Document configuration options (models, providers, ports)
- Include examples of CI specialist usage
- Add troubleshooting section for common issues

#### 2.3 aish (CI Shell)
**Current State**: Has README but not integrated into main documentation
**Action Items**:
- Add aish to main README.md component list
- Create user guide for aish commands
- Document integration with Terma
- Add examples of common workflows

### 3. Update Main README.md

**Specific Changes**:
- Line 20: Change "Agenteer" to "Ergon"
- Add to Integration section:
  - **aish**: AI-enhanced shell for terminal interactions
  - **Landmarks**: Code annotation and knowledge graph system
- Enhance CI Specialists section with:
  - Configuration examples
  - Port allocation explanation
  - Model selection guide

## 🟡 MEDIUM PRIORITY Updates

### 4. Standardize Component Documentation

**Template for all component READMEs**:
```markdown
# [Component Name]

## Overview
Brief description of component purpose

## Key Features
- Feature 1
- Feature 2

## Quick Start
```bash
# Installation
# Basic usage
```

## Configuration
Environment variables and settings

## API Reference
Link to detailed API docs

## Integration Points
How this component connects with others

## Troubleshooting
Common issues and solutions
```

**Components needing standardization**:
- Apollo
- Budget
- Harmonia
- Metis
- Prometheus
- Sophia
- Telos

### 5. Update UI Documentation

**Hephaestus Updates**:
- Document UI DevTools V2 comprehensively
- Update component instrumentation guide
- Clarify Shadow DOM isolation strategy
- Add semantic tagging guide

**Files to update**:
- `/Hephaestus/README.md`
- `/MetaData/TektonDocumentation/Guides/UIDevToolsV2/README.md`

### 6. Create Integration Guides

**New Guides Needed**:
1. **MCP Tool Registration Guide**
   - How to register tools
   - Tool schema definition
   - Examples of tool usage
   
2. **Component Integration Patterns**
   - Standard integration patterns
   - Event communication
   - Shared services usage

## 🟢 LOW PRIORITY Updates

### 7. API Documentation Enhancement

**Updates Needed**:
- Document MCP endpoints in detail
- Add CI registry API documentation
- Update shared utilities documentation
- Include request/response examples

### 8. Installation and Setup Improvements

**Enhancements**:
- Add troubleshooting section for common setup issues
- Document all environment variables
- Create setup verification checklist
- Add performance tuning guide

## Implementation Timeline

### Week 1: High Priority Items
- Fix Agenteer → Ergon references
- Create Landmarks integration guide
- Create CI Specialists guide
- Update main README.md

### Week 2: Medium Priority Items
- Standardize 3-4 component READMEs
- Update Hephaestus documentation
- Create MCP tool registration guide

### Week 3: Medium Priority Completion
- Standardize remaining component READMEs
- Create component integration patterns guide
- Update UI documentation

### Week 4: Low Priority Items
- Enhance API documentation
- Improve installation guides
- Add troubleshooting sections

## Success Criteria

- [ ] No references to deprecated components
- [ ] All new features have comprehensive documentation
- [ ] All component READMEs follow standard template
- [ ] Integration guides cover common use cases
- [ ] Documentation is searchable and well-linked

## Documentation Standards

### Every Document Should Include:
1. **Clear Purpose**: What is this component/feature for?
2. **Prerequisites**: What needs to be set up first?
3. **Examples**: Working code examples
4. **Configuration**: All available options
5. **Troubleshooting**: Common issues and solutions
6. **Related Links**: Links to other relevant docs

### Code Examples Should:
- Be complete and runnable
- Include necessary imports
- Show expected output
- Handle errors appropriately

### Diagrams Should:
- Use consistent styling
- Be generated from text (Mermaid preferred)
- Include a text description

## Maintenance Plan

1. **Regular Reviews**: Monthly documentation review
2. **Update Triggers**: Document updates with code changes
3. **User Feedback**: Incorporate user-reported issues
4. **Version Tracking**: Document which Tekton version docs apply to

## Notes

- Priority on user-facing documentation
- Technical implementation details in MetaData
- Keep examples practical and relevant
- Ensure consistency across all documentation