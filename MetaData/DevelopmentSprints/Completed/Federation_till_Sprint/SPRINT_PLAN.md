# Sprint: Till Lifecycle Manager and Federation System

## Overview
Implement Till as a lightweight C program that manages Tekton installations, handles component updates, and enables federation between Tekton instances. Till serves as the universal installer and manager for all Tekton deployments, supporting solo, observer, and member federation modes.

## Goals
1. **Till Core**: Build lightweight C program for Tekton lifecycle management
2. **Installation Management**: Enable automated Tekton installation and updates from GitHub
3. **Federation System**: Implement trust-based federation for observer/member instances
4. **Component Tracking**: Manage independent component versions with hold capabilities

## Phase 1: Till Core Implementation [0% Complete]

### Tasks
- [ ] Create Till C program with single header configuration (till_config.h)
- [ ] Implement JSON parsing using cJSON or jq integration
- [ ] Build core commands: till, till sync, till watch, till install, till uninstall
- [ ] Create menu-of-the-day fetching from GitHub
- [ ] Implement component version tracking in .till/tekton/installed/
- [ ] Add hold mechanism for preventing unwanted updates
- [ ] Build host management: till host add/remove/list
- [ ] Implement watch daemon with configurable frequency (default 24h)
- [ ] Add dry-run mode (till with no parameters)

### Success Criteria
- [ ] Till can create and manage ephemeral branches
- [ ] Branch registry tracks all active branches with expiration
- [ ] Automatic cleanup removes expired branches
- [ ] Till sync successfully pulls and processes GitHub data
- [ ] HOLD mechanism prevents unwanted updates with expiration

### Blocked On
- [ ] Nothing currently blocking

## Phase 2: Federation Implementation [0% Complete]

### Tasks
- [ ] Generate keypairs for observer/member installations
- [ ] Implement registration branch creation (registration-[fqn])
- [ ] Build deregistration process (till federate leave)
- [ ] Create relationship types (solo, observer, member)
- [ ] Store credentials in .till/ directory structure
- [ ] Implement branch-name-only registration (no file upload)
- [ ] Add federation status integration for tekton command
- [ ] Build trust-based permission system
- [ ] Create asymmetric relationship support

### Success Criteria
- [ ] Tektons can establish solo/observer/member relationships
- [ ] Asymmetric relationships work correctly
- [ ] Members can accept configuration additions from trusted sources
- [ ] Observers appear in tekton status but cannot modify
- [ ] Solo instances remain invisible to federation

### Blocked On
- [ ] Waiting for Phase 1 completion

## Phase 3: Integration and Testing [0% Complete]

### Tasks
- [ ] Integrate with tekton --system/-s flag for multi-host support
- [ ] Ensure till-private.json readable by tekton script
- [ ] Test solo installation workflow
- [ ] Test observer/member registration via branches
- [ ] Verify component update mechanism
- [ ] Test hold and release functionality
- [ ] Validate cross-platform compilation (Mac/Linux)
- [ ] Test Git authentication error handling

### Success Criteria
- [ ] Federation works across multiple Tekton instances
- [ ] Till sync properly manages relationship-based updates
- [ ] Handshake protocol successfully onboards new members
- [ ] Tests cover solo, observer, and member scenarios
- [ ] Documentation complete for federation setup

### Blocked On
- [ ] Waiting for Phase 2 completion

## Technical Decisions

### Core Design Principles
- **Decision**: "Working code wins" - no gatekeepers, no approval committees
  - **Why**: Learned from decades of better solutions being blocked
  - **Impact**: Implementation determines standard, not committees

### Protocol Design
- **Decision**: Fixed 4-byte aligned fields, no variable-length parsing
  - **Why**: Learned from TCP/IP header parsing nightmares
  - **Impact**: Clean, fast parsing with room for future growth

### Naming and Identity
- **Decision**: Flexible FQN system (name.category.geography) with crypto verification
  - **Why**: First-come naming rights, cryptographic proof of identity
  - **Impact**: No identity spoofing, natural namespace management

### Data Structure Design
- **Decision**: Use JSON for Till configuration with format/version header
  - **Why**: Human-readable, Git-friendly, supports nested objects
  - **Impact**: All Till operations parse/generate JSON

### Branch Management
- **Decision**: Use ephemeral branches with TTL instead of permanent branches
  - **Why**: Prevents repository clutter, natural lifecycle for federation data
  - **Impact**: Need branch registry and cleanup mechanism

### Trust Model
- **Decision**: Individual sovereignty - each Tekton manages its own relationships
  - **Why**: No central authority needed, natural growth of communities
  - **Impact**: Asymmetric relationships must be supported

### GitHub Integration
- **Decision**: Use single till-public repo with branch-based separation
  - **Why**: Simpler than submodules, leverages Git's branch management
  - **Impact**: Till must manage branch lifecycle carefully

## Out of Scope
- Centralized authentication/authorization system
- Automated conflict resolution between federated Tektons
- Real-time synchronization (using periodic till sync instead)
- Federation across different Tekton versions
- Encrypted communication between Tektons (future sprint)

## Files to Create
```
# Till repository structure (separate from Tekton)
/till/
├── src/
│   ├── till.c                 # Main program
│   ├── till_config.h          # All configuration
│   ├── cJSON.c                # JSON library (embedded)
│   └── cJSON.h
├── Makefile                    # Cross-platform build
├── README.md                   # Installation instructions
└── .till/                      # Local config (not in Git)
    ├── config/                 # Till configuration
    └── tekton/
        ├── federation/
        │   ├── till-private.json
        │   ├── till-registry.json
        │   └── till-hosts.json
        └── installed/          # Component tracking

# Modifications to Tekton
/scripts/tekton                 # Add --system/-s flag support
```

## Configuration Schema Examples

### Public Till (GitHub)
```json
{
  "format": "till-federation-v1",
  "version": "1.0.0",
  "identity": {
    "fqn": "kant.philosophy.us.princeton",
    "name": "Kant-Tekton",
    "uuid": "kant-uuid-12345",
    "public_key": "ssh-rsa AAAAB3NzaC1yc2EA...",
    "endpoint": "https://kant.example.com:8101",
    "capabilities": ["numa", "rhetor", "apollo"],
    "attributes": {
      "category": "philosophy",
      "geography": "us-east",
      "topics": ["ethics", "epistemology"],
      "organization": "princeton"
    }
  },
  "menu": {
    "components": {},
    "solutions": {}
  },
  "signature": "BASE64_SIGNATURE_OF_CONTENT"
}
```

### Till Private Configuration (.till/tekton/federation/till-private.json)
```json
{
  "format": "till-private-v1",
  "version": "1.0.0",
  "mode": "observer",
  "identity": {
    "fqn": "kant.philosophy.us.princeton",
    "private_key_path": ".till/credentials/private.key",
    "public_key": "ssh-rsa AAAAB3NzaC1yc2EA..."
  },
  "hosts": {
    "laptop": {
      "address": "localhost",
      "tekton_root": "/Users/casey/Tekton"
    },
    "desktop": {
      "address": "192.168.1.100",
      "tekton_root": "/home/casey/Tekton"
    }
  },
  "installed": {
    "tekton-core": {
      "version": "2.1.0",
      "installed": "2024-01-01T00:00:00Z",
      "hold": false
    },
    "aish": {
      "version": "1.4.0",
      "available": "1.5.0",
      "hold": true,
      "hold_reason": "Testing current version"
    }
  }
}
```

## Key Commands
```bash
# Basic Till operations
till                            # Dry-run, shows what sync would do
till -h | --help               # Show usage
till sync                      # Run synchronization now
till watch [frequency]         # Set watch daemon (default 24h)

# Installation
till install                   # Install Tekton with defaults
till install --mode solo       # Solo installation (no federation)
till install --mode observer --name kant.philosophy.us
till uninstall <component>    # Remove component

# Component management  
till hold <component>          # Prevent updates
till release <component>       # Allow updates
till update check             # Check for updates
till update apply             # Apply all updates

# Host management
till host add laptop localhost /Users/casey/Tekton
till host remove laptop
till host list

# Federation
till federate init --mode observer --name kant.philosophy.us
till federate leave           # Deregister from federation
till federate status          # Show federation status

# Tekton integration
tekton --system laptop start
tekton -s desktop status  
tekton --system cloud stop
```