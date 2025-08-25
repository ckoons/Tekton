# Terma Implementation Plan

## Phase 1: aish Shell Wrapper (Week 1)

### Goals
Transform aish into a true shell wrapper that can intercept CI commands while passing through normal shell operations transparently.

### Tasks

#### 1.1 Analyze Current aish Implementation
- [ ] Review existing aish code and architecture
- [ ] Identify integration points with Rhetor
- [ ] Document current limitations
- [ ] Plan refactoring approach

#### 1.2 Implement Core Shell Wrapper
- [ ] Create Python-based REPL loop
- [ ] Implement transparent command passthrough
- [ ] Handle subprocess execution properly
- [ ] Preserve environment and working directory
- [ ] Support command history

#### 1.3 Add CI Command Detection
- [ ] Define natural language patterns
- [ ] Implement pattern matching logic
- [ ] Route CI commands to Rhetor
- [ ] Return translated commands for confirmation
- [ ] Execute approved commands

#### 1.4 Test Shell Compatibility
- [ ] Test with common tools (git, npm, python)
- [ ] Verify pipe and redirection support
- [ ] Test background processes
- [ ] Ensure signal handling works
- [ ] Validate exit codes

### Deliverables
- Refactored `scripts/aish` 
- Test suite for shell operations
- Documentation for CI command patterns

## Phase 2: Terminal Launch Service (Week 2)

### Goals
Build the Terma service that launches and manages native terminal applications across platforms.

### Tasks

#### 2.1 Create Terma Service Structure
- [ ] Set up FastAPI application
- [ ] Define API endpoints
- [ ] Create terminal manager class
- [ ] Implement PID registry
- [ ] Add configuration system

#### 2.2 Implement macOS Terminal Launching
- [ ] Terminal.app launcher with AppleScript
- [ ] iTerm2 integration
- [ ] Warp.app support
- [ ] Claude Code detection and launch
- [ ] Test on macOS

#### 2.3 Implement Linux Terminal Launching
- [ ] GNOME Terminal support
- [ ] Konsole support
- [ ] xterm fallback
- [ ] Terminal detection logic
- [ ] Test on Ubuntu/Debian

#### 2.4 Build PID Management System
- [ ] Process tracking and validation
- [ ] Terminal status monitoring
- [ ] Show/hide terminal operations
- [ ] Clean termination handling
- [ ] Registry persistence

#### 2.5 Create Configuration Templates
- [ ] Define template schema
- [ ] Implement default templates
- [ ] Template CRUD operations
- [ ] Environment variable expansion
- [ ] User customization support

### Deliverables
- `Terma/terma_service.py` - Main service
- `Terma/terminal_manager.py` - Terminal lifecycle
- `Terma/templates/` - Default configurations
- API documentation

## Phase 3: Terma UI Implementation (Week 3)

### Goals
Create the Hephaestus UI component following Numa/Noesis patterns with four-tab interface.

### Tasks

#### 3.1 Copy Numa/Noesis UI Structure
- [ ] Duplicate Numa component as starting point
- [ ] Update to Terma branding and colors
- [ ] Modify component registration
- [ ] Update semantic tags for Terma

#### 3.2 Implement Dashboard Tab
- [ ] Terminal list display
- [ ] Real-time status updates
- [ ] Show/Terminate buttons
- [ ] Launch configuration summary
- [ ] PID and runtime information

#### 3.3 Implement Launch Terminal Tab
- [ ] Terminal type selector
- [ ] Configuration template dropdown
- [ ] Working directory picker
- [ ] Environment variable editor
- [ ] Context/purpose text area
- [ ] Prompt editor (like Rhetor)
- [ ] Launch button with validation

#### 3.4 Implement Terminal Chat Tab
- [ ] Terminal selector dropdown
- [ ] Direct aish communication
- [ ] Command history display
- [ ] CI translation preview
- [ ] Context-aware suggestions

#### 3.5 Implement Team Chat Tab
- [ ] Connect to Rhetor team chat
- [ ] Terminal context sharing
- [ ] Collaborative debugging
- [ ] Shared command history

#### 3.6 Wire Up API Integration
- [ ] Connect all UI to Terma service
- [ ] Real-time updates via polling
- [ ] Error handling and retries
- [ ] Loading states

### Deliverables
- `Hephaestus/ui/components/terma.html`
- `Hephaestus/ui/css/components/terma.css`
- `Hephaestus/ui/js/terma.js`
- Updated `index.html` with Terma

## Phase 4: Integration & Polish (Week 4)

### Goals
Complete integration, add CI terminal requests, test thoroughly, and document.

### Tasks

#### 4.1 CI Terminal Request API
- [ ] Define request schema
- [ ] Implement endpoint
- [ ] Add context injection
- [ ] Test with Tekton CIs
- [ ] Document API usage

#### 4.2 Enhanced aish Features
- [ ] Rhetor integration improvements
- [ ] Context persistence between sessions
- [ ] Command pattern learning
- [ ] Engram storage integration

#### 4.3 Cross-Platform Testing
- [ ] Test all terminal types on macOS
- [ ] Test Linux terminals
- [ ] Verify aish compatibility
- [ ] Performance testing
- [ ] Edge case handling

#### 4.4 Documentation
- [ ] User guide for Terma UI
- [ ] aish command reference
- [ ] API documentation
- [ ] Configuration guide
- [ ] Troubleshooting guide

#### 4.5 Integration Testing
- [ ] Test with other Tekton components
- [ ] CI collaboration scenarios
- [ ] Multi-terminal workflows
- [ ] Stress testing

### Deliverables
- Complete Terma system
- Comprehensive documentation
- Test suite
- Example configurations

## Development Checklist

### Before Starting
- [ ] Review Numa/Noesis implementations
- [ ] Set up development environment
- [ ] Verify terminal applications available
- [ ] Review UI DevTools documentation

### During Development
- [ ] Follow CSS-first architecture
- [ ] Use semantic tags throughout
- [ ] Test on both macOS and Linux
- [ ] Keep API responses consistent
- [ ] Document as you build

### Before Completion
- [ ] All tests passing
- [ ] Documentation complete
- [ ] UI follows Tekton patterns
- [ ] Performance acceptable
- [ ] Security review done

## Risk Mitigation

1. **Terminal Compatibility**: Test early with various terminals
2. **aish Complexity**: Start simple, add features incrementally
3. **Platform Differences**: Abstract platform-specific code
4. **PID Management**: Handle edge cases robustly
5. **UI Consistency**: Strictly follow Numa/Noesis patterns

## Success Metrics

- Launch any terminal in < 2 seconds
- Zero crashes in PID management
- aish works with 95%+ of commands
- UI matches Numa/Noesis quality
- Both users and CIs can launch terminals