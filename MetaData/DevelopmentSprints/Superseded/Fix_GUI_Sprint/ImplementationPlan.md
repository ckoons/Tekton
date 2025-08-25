# Fix GUI Sprint - Revised Implementation Plan

## Overview
This document outlines the revised implementation plan for the Fix GUI Sprint, using a direct HTML injection approach for component rendering. This methodical, component-by-component approach will ensure more reliable component integration with clear checkpoints for approval.

Tekton is an intelligent orchestration system that coordinates multiple CI models and resources to efficiently solve complex software engineering problems. This Implementation Plan focuses on simplifying and standardizing the Hephaestus UI architecture to create a more reliable component integration system.

## Key Architectural Change: Direct HTML Injection

We're adopting a **Direct HTML Injection** approach to component rendering, which:
- Eliminates issues with loading full HTML documents with DOCTYPE, html, head tags
- Avoids complex Shadow DOM encapsulation challenges
- Provides direct control over component rendering
- Simplifies debugging and maintenance

## Implementation Phases

### Phase 1: Core Architecture and Athena Component

#### Task 1.1: Create Template Component Loader
**Description:** Implement the direct HTML injection strategy in UI Manager with a template pattern for component loading.

**Steps:**
1. Create a generic component loader function in `ui-manager.js` that uses direct HTML injection
2. Create individual component loader functions following this pattern
3. Implement the first component loader for Athena as proof of concept
4. Obtain approval for the approach

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`

**Dependencies:**
- None

**Acceptance Criteria:**
- Component loader successfully injects HTML directly into the right panel
- The approach is reviewed and approved
- HTML is correctly rendered without duplicating the entire page

#### Task 1.2: Fix WebSocket Connection Handling
**Description:** Resolve the WebSocket connection issues by properly implementing the Single Port Architecture pattern.

**Steps:**
1. Update `server.py` to properly handle WebSocket protocol upgrade
2. Implement correct Sec-WebSocket-Accept key calculation
3. Modify `websocket.js` to use the correct URL path and connection parameters
4. Test WebSocket connections with visual feedback indicators

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/server.py`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/websocket.js`

**Dependencies:**
- Server restart capability

**Acceptance Criteria:**
- WebSocket connections establish without "invalid Connection header" errors
- Connection status is visually indicated to users
- Connection errors are properly handled and reported
- Obtain approval for the implementation

#### Task 1.3: Create Dedicated Athena Loader
**Description:** Implement a dedicated Athena component loader using direct HTML injection.

**Steps:**
1. Analyze existing Athena component structure and needed functionality
2. Extract HTML content from existing component files (removing document structure tags)
3. Create `loadAthenaComponent()` function with direct HTML injection
4. Implement proper tab handling and event listeners
5. Test and obtain approval

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html` (for reference)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/athena/athena-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/athena/athena-service.js`

**Dependencies:**
- Task 1.1: Create Template Component Loader

**Acceptance Criteria:**
- Athena component loads and renders correctly in the right panel
- Tab switching functionality works properly
- No duplicate content or nested HTML documents
- Obtain approval for implementation

#### Task 1.4: Update Component Registry for Athena
**Description:** Update the component registry for Athena to reflect the new direct HTML injection approach.

**Steps:**
1. Update Athena entry in `component_registry.json`
2. Modify the entry to use HTML mode and specify correct script paths
3. Remove any unnecessary parameters related to HTML loading
4. Test with the new component loader

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/component_registry.json`

**Dependencies:**
- Task 1.3: Create Dedicated Athena Loader

**Acceptance Criteria:**
- Component registry entry is updated correctly
- Athena registration includes required scripts and styles
- No unnecessary parameters are present
- Obtain approval for component registry changes

### Phase 2: Additional Component Migration (One-by-One)

#### Task 2.1: Ergon Component Analysis and Implementation
**Description:** Analyze and implement the Ergon component using direct HTML injection.

**Steps:**
1. Analyze current Ergon component implementation and tab structure
2. Create migration plan for Ergon (documenting tabs, functionality, etc.)
3. Get approval for component-specific approach
4. Implement direct HTML injection loader for Ergon
5. Test and refine
6. Get final approval before moving to next component

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/ergon/ergon-component.html` (for reference)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ergon/ergon-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/component_registry.json`

**Dependencies:**
- Task 1.1: Create Template Component Loader
- Task 1.3: Create Dedicated Athena Loader (as reference implementation)

**Acceptance Criteria:**
- Complete analysis document with tabs and functionality required
- Ergon component loads and renders correctly using direct HTML injection
- All Ergon functionality works as expected
- Component registry is updated
- Get approval before moving to next component

#### Task 2.2: Terma Component Analysis and Implementation
**Description:** Analyze and implement the Terma component using direct HTML injection.

**Steps:**
1. Analyze current Terma component implementation and special requirements
2. Create migration plan for Terma (considering its terminal functionality)
3. Get approval for component-specific approach
4. Implement direct HTML injection loader for Terma
5. Test and refine
6. Get final approval before moving to next component

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/terma/terma-component.html` (for reference)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/terma/terma-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/component_registry.json`

**Dependencies:**
- Task 1.1: Create Template Component Loader
- Task 2.1: Ergon Component Analysis and Implementation (for approach consistency)

**Acceptance Criteria:**
- Complete analysis document with terminal functionality required
- Terma component loads and renders correctly using direct HTML injection
- Terminal functionality works as expected
- Component registry is updated
- Get approval before moving to next component

#### Task 2.3: Rhetor Component Analysis and Implementation
**Description:** Analyze and implement the Rhetor component using direct HTML injection.

**Steps:**
1. Analyze current Rhetor component implementation and special requirements
2. Create migration plan for Rhetor 
3. Get approval for component-specific approach
4. Implement direct HTML injection loader for Rhetor
5. Test and refine
6. Get final approval before moving to next component

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/rhetor/rhetor-component.html` (for reference)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/rhetor/rhetor-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/component_registry.json`

**Dependencies:**
- Task 1.1: Create Template Component Loader
- Previous component implementations (for approach consistency)

**Acceptance Criteria:**
- Complete analysis document with tabs and functionality required
- Rhetor component loads and renders correctly using direct HTML injection
- All Rhetor functionality works as expected
- Component registry is updated
- Get approval before moving to next component

### Phase 3: Shared Utilities and Chat Interface

#### Task 3.1: Create Common Tab Handling Utility
**Description:** Develop shared tab handling functionality for all components.

**Steps:**
1. Extract common tab switching functionality from component implementations
2. Create a shared utility function for tab handling
3. Update existing component loaders to use the shared utility
4. Test with multiple components
5. Get approval for shared utility approach

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/component-utils.js` (new or existing)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`

**Dependencies:**
- Multiple component implementations from Phase 2

**Acceptance Criteria:**
- Shared tab utility successfully handles tab switching for multiple components
- Code is DRY (Don't Repeat Yourself) with common functionality extracted
- All components using tabs work correctly with the utility
- Get approval for shared utility approach

#### Task 3.2: Create Chat Interface Template
**Description:** Create a standardized chat interface template that can be injected into components.

**Steps:**
1. Design chat interface HTML structure
2. Create CSS for chat interface styling
3. Develop JavaScript for chat interactions
4. Test basic chat functionality
5. Get approval for chat interface design

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/shared/chat-interface.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/shared/chat-interface.css`

**Dependencies:**
- Task 3.1: Create Common Tab Handling Utility

**Acceptance Criteria:**
- Chat interface template is created with clean, maintainable code
- Chat styling is consistent with Hephaestus UI
- Basic message display and input functionality works
- Get approval for chat interface template

#### Task 3.3: Integrate Chat Interface with LLM Adapter
**Description:** Connect the chat interface with the Tekton LLM Adapter.

**Steps:**
1. Update or create `llm_adapter_client.js` 
2. Implement message sending and receiving
3. Add provider selection and connection management
4. Test with actual LLM responses
5. Get approval for LLM integration

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/shared/llm_adapter_client.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/shared/chat-interface.js`

**Dependencies:**
- Task 3.2: Create Chat Interface Template

**Acceptance Criteria:**
- Chat interface successfully connects to Tekton LLM Adapter
- Messages are properly sent and received
- Provider selection works correctly
- Get approval for LLM integration

#### Task 3.4: Add Chat Interface to Selected Components
**Description:** Integrate the chat interface with selected components (prioritizing Athena).

**Steps:**
1. Add chat interface to Athena component loader
2. Create component-specific chat handlers for Athena
3. Test Athena-specific chat functionality
4. Get approval for chat integration with Athena
5. Plan for additional component chat integration

**Required Files:**
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js` (Athena loader)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/athena/athena-component.js`

**Dependencies:**
- Task 1.3: Create Dedicated Athena Loader
- Task 3.3: Integrate Chat Interface with LLM Adapter

**Acceptance Criteria:**
- Chat interface is properly integrated with Athena component
- Athena-specific interactions work through chat
- User experience is intuitive and responsive
- Get approval for chat integration with Athena

## Testing Requirements

### Component-by-Component Testing
- Test each component individually after implementation
- Visual inspection of rendering in the right panel
- Functional testing of all component features
- Get approval before moving to the next component

### WebSocket Testing
- Test WebSocket connection with visual indicators
- Verify error handling and reconnection
- Ensure proper protocol handling

### Integration Testing
- Test interactions between components (once multiple are implemented)
- Verify shared utilities work across components
- Test chat interface with multiple components
- Ensure all JavaScript functionality continues to work

### User Acceptance Testing
- Verify components render correctly in the right panel
- Test navigation between components using the left panel
- Verify tab switching and other component-specific functionality
- For chat-enabled components, test chat interactions

## Documentation Updates

### Component Analysis Documents
For each component, create a detailed analysis document:
1. **Athena Component Analysis**
   - Tab structure and content
   - Required functionality
   - Integration points
   - Implementation approach

2. **Ergon Component Analysis**
   - Tab structure and content
   - Required functionality
   - Integration points
   - Implementation approach

3. **Additional Component Analyses**
   - One analysis document per component

### Implementation Guidelines
1. **Direct HTML Injection Pattern**
   - Template for component loaders
   - Best practices for HTML structure
   - Event handling approach
   - State management

2. **Chat Interface Integration Guide**
   - How to add chat interface to components
   - Component-specific handling
   - LLM adapter integration

## Implementation Roadmap

| Phase | Component | Checkpoint |
|-------|-----------|------------|
| Phase 1 | Core Architecture & Athena | Review & approval of approach |
| Phase 2 | Ergon Component | Review & approval |
| Phase 2 | Terma Component | Review & approval |
| Phase 2 | Rhetor Component | Review & approval |
| Phase 3 | Shared Utilities | Review & approval |
| Phase 3 | Chat Interface | Final review & approval |

## Component Migration Strategy

### For Each Component
1. **Component Analysis** - One day
   - Analyze existing implementation
   - Document tab structure and required functionality
   - Get approach approval

2. **Implementation** - One to two days
   - Create dedicated loader
   - Extract HTML content
   - Implement tab functionality
   - Test and refine

3. **Review & Approval** - Half day
   - Demonstrate working component
   - Document any issues or special requirements
   - Get approval before proceeding to next component

This component-by-component approach ensures steady progress with clear checkpoints for validation.