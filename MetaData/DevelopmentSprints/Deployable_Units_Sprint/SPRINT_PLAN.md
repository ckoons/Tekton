# Sprint: Ergon Container Management

## Overview
Transform Ergon into a comprehensive container management platform with JSON-based registry, build system, and deployment capabilities using the Casey Method principles: simple, works, hard to screw up.

## Goals
1. **Phase 0**: Clean up Ergon by moving Analyzer to TektonCore
2. **Phase 1**: Build robust JSON registry for all deployable units  
3. **Phase 2**: Implement Build system for container creation and testing

## Phase 0: Infrastructure Cleanup [0% Complete]

### Tasks
- [ ] Move Analyzer functionality from Ergon to TektonCore
- [ ] Remove Analyzer tab from Ergon UI
- [ ] Update TektonCore to include Analyzer with Create Project integration
- [ ] Test Analyzer functionality in TektonCore
- [ ] Clean up Ergon navigation to prepare for Container focus
- [ ] Update inter-component APIs for Analyzer handoff

### Success Criteria
- [ ] Analyzer fully functional in TektonCore
- [ ] No Analyzer references remaining in Ergon
- [ ] Ergon UI cleaned up and ready for container features
- [ ] All existing functionality preserved

### Blocked On
- [ ] Nothing currently blocking

## Phase 1: Build the Registry [0% Complete]

### Core Registry Foundation
- [ ] Design universal JSON schema for deployable units
- [ ] Implement SQLite-based registry storage
- [ ] Create core registry operations (store, retrieve, search, delete)
- [ ] Build REST API endpoints (`/api/ergon/registry/*`)
- [ ] Add JSON validation for base schema
- [ ] Implement basic search and filtering

### Registry Schema
```json
{
  "id": "uuid_or_hash",
  "type": "container|solution|tool|config",
  "version": "semver",
  "name": "human_readable_name", 
  "created": "iso_timestamp",
  "updated": "iso_timestamp",
  "content": {
    // type-specific JSON structure
  }
}
```

### Core Operations
- [ ] `store(json_object)` → returns ID
- [ ] `retrieve(id)` → returns JSON object  
- [ ] `search(type, name, filters)` → returns list
- [ ] `list_types()` → returns available types
- [ ] `delete(id)` → removes object

### UI Integration
- [ ] Create Registry tab in Ergon
- [ ] Browse all stored objects by type
- [ ] Basic JSON editor with validation
- [ ] Search and filter interface

### Success Criteria
- [ ] Store and retrieve any JSON structure
- [ ] Fast O(1) lookup by ID
- [ ] Search by type, name, and content fields
- [ ] UI shows stored objects clearly
- [ ] Schema validation enforced
- [ ] Foundation ready for container definitions

### Blocked On
- [ ] Waiting for Phase 0 completion

## Phase 2: Build the Build System [0% Complete]

### Build Tab Implementation
- [ ] Create Build tab in Ergon UI
- [ ] Component selection panel (browse Registry)
- [ ] Build workspace (configure selected components)
- [ ] Actions panel (sandbox, publish, export)

### Component Selection Panel
- [ ] Registry browser interface
- [ ] Search and filter components
- [ ] Component cards with details
- [ ] "Add to Build" functionality

### Build Workspace  
- [ ] Selected components list
- [ ] Configuration panel for each component
- [ ] Environment variables editor
- [ ] Port mapping interface
- [ ] Dependency ordering system
- [ ] CI assignment dropdown

### Build Settings
- [ ] Deployable unit naming
- [ ] Description editor
- [ ] Container type selection
- [ ] Tags and metadata

### Sandbox Testing
- [ ] Local testing environment
- [ ] Resolve GitHub file references
- [ ] Component startup orchestration
- [ ] Log streaming to UI
- [ ] Test endpoint provision

### Publishing System
- [ ] Generate deployable unit JSON
- [ ] GitHub repository creation
- [ ] Solution upload to GitHub
- [ ] Registry entry with GitHub URL
- [ ] Export to Docker format

### Success Criteria
- [ ] Complete build workflow functional
- [ ] Sandbox testing works reliably
- [ ] Publishing to GitHub successful
- [ ] Registry integration seamless
- [ ] Export capabilities working

### Blocked On
- [ ] Waiting for Phase 1 completion

## Technical Decisions

### Registry Storage
- **SQLite database** for simplicity and reliability
- **File-based fallback** for development
- **JSON schema validation** at storage time
- **UUID-based IDs** for global uniqueness

### Build System Architecture  
- **Component composition** over monolithic builds
- **GitHub as source of truth** for shared components
- **Local sandbox** for safe testing
- **JSON-centric** configuration

### Casey Method Principles
- **Simple**: Clear operations, obvious workflows
- **Works**: Reliable storage, predictable behavior  
- **Hard to screw up**: Validation, safe defaults, clear errors

## Out of Scope
- Complex orchestration systems
- Production deployment automation  
- Advanced container networking
- Kubernetes integration (future sprint)

## Files to Create/Update

### Phase 0
```
/tekton-core/tekton/analyzer/ (moved from Ergon)
/Hephaestus/ui/components/tekton/analyzer-integration.html
/Hephaestus/ui/components/ergon/ergon-component.html (remove analyzer)
```

### Phase 1  
```
/Ergon/ergon/registry/ (new directory)
/Ergon/ergon/registry/storage.py
/Ergon/ergon/registry/schema.py
/Ergon/ergon/api/registry.py
/Hephaestus/ui/components/ergon/registry-tab.html
```

### Phase 2
```
/Hephaestus/ui/components/ergon/build-tab.html
/Ergon/ergon/build/ (new directory)
/Ergon/ergon/build/workspace.py
/Ergon/ergon/build/sandbox.py
/Ergon/ergon/build/publisher.py
```

## Success Metrics
- [ ] Ergon focused purely on container/deployment management
- [ ] Registry stores and retrieves JSON reliably
- [ ] Build system creates testable deployable units
- [ ] Publishing workflow generates GitHub repositories
- [ ] All components follow Casey Method principles

## Future Integration
This sprint sets the foundation for:
- **Container CIs** from our Docker sprint
- **Federated Tekton** registry synchronization
- **Casey Method cookbooks** integration
- **Multi-AI deployment** coordination