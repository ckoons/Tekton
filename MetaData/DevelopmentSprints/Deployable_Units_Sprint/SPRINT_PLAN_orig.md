# Deployable_Units Sprint Plan

## Overview
**Sprint Name**: Deployable_Units_Sprint  
**Created**: 2025-08-14  
**Status**: Active  

## Proposal Details
{
  "name": "Deployable_Units",
  "title": "\n                            Deployable Units\n                        ",
  "description": "\n                        Ergon automates development, maintains a database of solutions, and should also manage and configure containers\n                    ",
  "status": "sprint"
}

## Sprint Checklist

### Phase 1: Planning
- [ ] Review proposal requirements
- [ ] Identify technical approach
- [ ] Break down into tasks

### Phase 2: Implementation
- [ ] Core functionality
- [ ] Integration points
- [ ] Error handling

### Phase 3: Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] User acceptance

### Phase 4: Documentation
- [ ] Update component docs
- [ ] API documentation
- [ ] User guide

## Success Criteria
- All checklist items completed
- Tests passing
- Documentation updated
Here's the complete updated SPRINT_PLAN.md content:

``markdown

Deployable Units Sprint Plan

Sprint Overview
Sprint Goal: Build JSON-centric container management in Ergon - store, search, and manage deployable unit definitions

Duration: Phased approach Components: Ergon (Registry enhancement, Container management) Sprint Type: Feature Sprint Status: Active Created: 2025-08-14 Updated: 2025-08-19

Background
Ergon manages JSON structures that define deployable units. Containers are one type of deployable unit that includes:

Multi-app stacks with configuration
CI assignment for intelligence
Build instructions for deployment
Core Principle: Simple, works, hard to screw up
Architecture Approach
JSON-Centric Design
Ergon Role: Manage JSON definitions, not actual containers
Container Format: Tekton-native with --export docker capability
Registry: Universal JSON store for all deployable unit types
Federation Ready: JSON structures can sync between Tekton instances
Base JSON Schema
`json { "id": "uuid_or_hash", "type": "container|solution|tool|config", "version": "semver", "name": "human_readable_name", "created": "iso_timestamp", "updated": "iso_timestamp", "content": { / type-specific JSON structure / } } `
Sprint Phases
Phase 0: Infrastructure Prep
Move Analyzer to TektonCore - Clean up Ergon UI for Containers tab
[ ] Move analyzer functionality to TektonCore
[ ] Remove analyzer tab from Ergon
[ ] Prepare UI space for Containers tab
Phase 1: Registry Foundation - CORE FOCUS
Registry Specification
Purpose: Simple JSON object store with ID-based retrieval and basic search
Core Operations:
store(json_object) → returns ID
retrieve(id) → returns JSON object
search(type=None, name=None, filters) → returns list of objects
list_types() → returns available types
delete(id) → removes object
Implementation Deliverables:
[ ] Registry database schema/structure (SQLite or file-based)
[ ] Core storage operations (store, retrieve, search, delete)
[ ] REST API endpoints (/api/ergon/registry/*)
[ ] Basic UI integration (Registry tab shows all types)
[ ] JSON validation for base schema
Success Criteria:
Store and retrieve any JSON structure
Search by type and name
UI can browse stored objects
Foundation ready for container/solution/tool types
Phase 2: Container JSON Definitions
Define container-type JSON schema and management
[ ] Container JSON schema design
[ ] CI assignment mechanism
[ ] Multi-app stack definition
Phase 3: Apps/Tools/Config Management
Define other deployable unit types and their relationships
[ ] Solution type definitions
[ ] Tool type definitions
[ ] Config type definitions
Phase 4: UI Integration
Container tab with JSON editing/building capabilities
[ ] Containers tab implementation
[ ] JSON editor with validation
[ ] Container creation workflow
Future Phases:
Phase 5: Sandbox testing
Phase 6: Export capabilities (Docker format)
Phase 7: Refactor/Refine capabilities
Technical Requirements
- No hardcoded ports/URLs (use TektonEnviron)
Proper error handling and logging
JSON validation and schema versioning
Debug instrumentation following guidelines
Simple database approach (optimize later)
Success Criteria
Phase 1 Registry Success:
1. Store any JSON: Registry accepts and stores arbitrary JSON structures 2. Fast retrieval: O(1) lookup by ID 3. Basic search: Filter by type, name, and content fields 4. UI integration: Registry tab shows stored objects 5. Schema validation: Base schema enforced on all objects
---
Updated 2025-08-19 with refined scope focusing on JSON-centric registry foundation ```
Ergon Build Tab Workflow Specification

Overview
The Build tab enables users to create deployable units by combining components from the Registry, configuring them, testing locally, and publishing to GitHub.

Build Tab UI Structure
Component Selection Panel (Left)
Registry Browser: Browse available components from Registry
Search/Filter: Find components by type, name, tags
Component Cards: Show name, description, type, GitHub source
Add Button: Add selected component to build workspace
Build Workspace (Center)
Selected Components: List of components added to current build
Configuration Panel: Configure each component (environment, ports, dependencies)
Build Settings:
- Deployable unit name - Description - CI assignment (optional) - Container type selection
Actions Panel (Right)
Sandbox Button: Test deployable unit locally
Sandbox Output: Terminal/logs from testing
Publish Button: Create GitHub repo and update Registry
Export Options: Docker format, Tekton format
User Workflow
1. Component Selection
`` User browses Registry → Finds useful components → Adds to build workspace `
Actions:
Browse Registry tab components
Search by type: container|solution|app|config
Filter by tags, author, update date
Click "Add to Build" on component cards
Result: Components appear in build workspace with default configuration
2. Configuration
` User configures each component → Sets environment variables → Defines dependencies `
Configuration Options:
Environment Variables: Key-value pairs for each component
Port Mapping: Internal/external port assignments
File Paths: Where component files are placed in container
Dependencies: Startup order and inter-component connections
CI Assignment: Which CI will manage this deployable unit
3. Testing with Sandbox
` User clicks Sandbox → Deployable unit runs locally → User verifies functionality `
Sandbox Process:
Resolve all GitHub file references to local files
Create isolated test environment
Start components in dependency order
Stream logs/output to Sandbox Output panel
Provide test endpoints/interfaces
4. Publishing to GitHub
` User clicks Publish → Creates GitHub repo → Updates local Registry → Makes solution discoverable ``
Publish Process:

Generate deployable unit JSON structure
Create GitHub repository (if needed)
Upload complete solution definition
Add entry to local Registry with GitHub URL
This transforms Ergon into a powerful solution development environment focused on composition, testing, and sharing.
