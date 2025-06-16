# Tekton Launch Testing Plan

## Overview

This document outlines the strategy for testing the Tekton component launch system, including the key scripts `tekton-status`, `tekton-kill`, and `tekton-launch`. The testing process focuses on methodically verifying and fixing each component's launch process, addressing issues as they arise, and documenting findings for future development sprints.

## Testing Workflow

### Phase 1: Core Infrastructure Testing

1. **Script Evaluation**
   - ✅ `tekton-status`: Verified working with minor adjustments to process detection
   - ✅ `tekton-kill`: Fixed to exclude Claude processes and improved process termination
   - 🔄 `tekton-launch`: Being tested component by component

2. **Core Component Testing**
   - ✅ Hermes: Fixed async method issues and database MCP server integration
   - ✅ Engram: Successfully launches and provides memory services
   - 🔄 Rhetor: Debugging component_dir issue in launch script

### Phase 2: Component Integration Testing

1. **Mid-Level Components**
   - Ergon
   - Prometheus
   - Harmonia

2. **Higher-Level Components**
   - Athena
   - Sophia
   - Telos
   - Synthesis
   - Terma

3. **User Interface**
   - Hephaestus UI

### Phase 3: Full System Launch

1. **All-Component Launch**
   - Using `--launch-all` flag for comprehensive system test
   - Verify component interactions through Hermes registration
   - Test auto-detection and launching of dependencies

## Testing Guidelines

1. **Methodical, Sequential Testing**
   - Test components sequentially, starting with core infrastructure
   - Address and document issues before progressing to next component
   - Regularly check status using `tekton-status` after each launch/kill cycle

2. **Documentation Requirements**
   - Document all issues found during testing
   - Note workarounds implemented and permanent fixes required
   - Create detailed issue reports for the FastMCP sprint

3. **Collaborative Process**
   - Work interactively with project stakeholders
   - Obtain explicit approval before proceeding to next component
   - Leverage stakeholder knowledge of system design and history

## Testing Environment

- MacOS system with bash 3.2 (requirement: handle backward compatibility)
- Testing directory: `/Users/cskoons/projects/github/Tekton`
- Log directory: `$HOME/.tekton/logs`
- Component-specific data directories: `$HOME/.tekton/data`

## Known Issues and Considerations

### tekton-kill Script

1. **Claude Process Protection**
   - Modified to exclude Claude/Anthropic processes from termination
   - Uses pattern matching and PID filtering instead of direct pkill
   - Added safety checks to prevent accidental termination of claude sessions

### tekton-launch Script

1. **Single Port Architecture**
   - Ports 8000-8010 assigned to components in `tekton-ports.sh`
   - Port conflicts must be handled gracefully with proper error messages
   - Component lifecycle management is handled via Hermes

2. **Component Directory Structure**
   - Requires proper handling of component paths
   - Fixed issue with `component_dir` in launch scripts

3. **Process Detection**
   - Enhanced patterns for detecting running processes
   - Added additional detection methods in `tekton-status`

### Hermes Service

1. **MessageBus Implementation**
   - Added missing async methods (`create_channel`, `subscribe`, `publish`)
   - Fixed error handling in registration and event publishing

2. **Database MCP Server**
   - Created temporary stub script for database MCP server
   - Will be replaced during FastMCP sprint

### Rhetor Service

1. **Port Configuration**
   - Port mismatch (8003 vs 8300) needs standardization
   - Component launch needs to handle port mapping properly

## Approval Checkpoints

1. **Core Infrastructure**
   - [x] Scripts initial assessment
   - [x] Hermes service launch
   - [x] Engram service launch
   - [ ] Rhetor service launch

2. **Component Testing**
   - [ ] All mid-level components
   - [ ] All higher-level components
   - [ ] UI component

3. **System Integration**
   - [ ] Full system launch
   - [ ] System stability verification
   - [ ] Shutdown and restart cycle

## Additional Information Sources

- Component design documents in MetaData/ComponentDocumentation
- Development sprint documentation in MetaData/DevelopmentSprints
- Single Port Architecture documentation in config/port_assignments.md