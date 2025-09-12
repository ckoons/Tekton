# Sprint: Till Federation - Local and Global Synchronization

## Overview
Implement bidirectional synchronization for Till instances in local networks (hosts-local.json) and global federation via GitHub gists, establishing Till as the single authority for all component communication.

## Goals
1. **Local Network Sync**: Automatic propagation of host changes across all Till instances in a LAN
2. **GitHub Federation**: Till manages all GitHub communication for installed components via gists
3. **Unified Authority**: Establish Till as the single point of federation and external communication

## Phase 1: Local Network Synchronization [100% Complete] ✅

### Tasks
- [x] Add `actual_hostname` field to host structure in till_host.c
- [x] Capture hostname during `till host add` installation
- [x] Store `local_hostname` in hosts-local.json at Till init
- [x] Implement host update propagation after add/remove
- [x] Add merge logic to handle incoming host updates
- [x] Implement self-detection to prevent circular updates
- [x] Add soft delete with timestamps for removed hosts
- [x] Create `till host sync` command for manual reconciliation
- [x] Add opportunistic sync during host operations
- [x] Implement stale host cleanup (30-day retention logic added)

### Success Criteria
- [x] Hosts automatically share knowledge after add/remove
- [x] No duplicate entries or circular updates
- [x] Graceful handling of network partitions
- [x] Removed hosts marked but not deleted immediately
- [x] All hosts in LAN have consistent view (eventually)

### Blocked On
- [ ] Nothing currently blocking

## Phase 2: GitHub Federation Infrastructure [0% Complete]

### Tasks
- [ ] Create till_github.c for GitHub/gist operations
- [ ] Implement `gh` CLI integration for authentication
- [ ] Add fallback to personal access token if gh unavailable
- [ ] Create secure token storage (600 permissions)
- [ ] Implement gist creation for host status
- [ ] Add gist update mechanism with retry logic
- [ ] Create menu-of-the-day download from hub repo
- [ ] Implement role-based command execution (solo/observer/member)
- [ ] Add component status collection interface
- [ ] Create aggregated status gist structure

### Success Criteria
- [ ] Till can authenticate with GitHub via gh or token
- [ ] Host gist created and updated successfully
- [ ] Menu downloaded and parsed correctly
- [ ] Components report status through Till only
- [ ] No component has direct GitHub access

### Blocked On
- [ ] Waiting for Phase 1 completion

## Phase 3: Federation Commands and Sync [0% Complete]

### Tasks
- [ ] Implement `till register --hub <repo>` command
- [ ] Create `till sync` command for manual federation sync
- [ ] Add automatic sync via cron integration
- [ ] Implement queue for offline operation
- [ ] Add `till federate status` to show federation state
- [ ] Create `till component-status` interface for components
- [ ] Implement menu command delegation to components
- [ ] Add federation role management (solo/observer/member)
- [ ] Create hub registration via gist URL submission
- [ ] Add telemetry aggregation from all components

### Success Criteria
- [ ] Single `till sync` updates everything
- [ ] Components never touch network directly
- [ ] Offline operations queue properly
- [ ] Role-based execution works correctly
- [ ] Hub has visibility into all registered hosts

### Blocked On
- [ ] Waiting for Phase 2 completion

## Technical Decisions

### Architecture Principles
1. **Till as Single Authority**: All external communication flows through Till
2. **Eventual Consistency**: LAN uses gossip-style eventual consistency, not strict sync
3. **Soft Deletes**: Hosts marked as removed, not immediately deleted (30-day retention)
4. **GitHub via HTTPS**: All GitHub operations use HTTPS, not SSH (firewall friendly)
5. **Component Isolation**: Components report to Till, never communicate externally

### Data Structures

**Enhanced hosts-local.json**:
```json
{
  "local_hostname": "M4",
  "hosts": {
    "m2": {
      "user": "cskoons",
      "host": "m2.local",
      "port": 22,
      "actual_hostname": "m2",
      "state": "active",
      "last_seen": "2025-01-10T12:00:00Z",
      "version": 5
    }
  }
}
```

**Host Gist Structure**:
```json
{
  "host": "M4",
  "updated": "2025-01-10T12:00:00Z",
  "federation": {
    "role": "member",
    "last_sync": "2025-01-10T11:00:00Z"
  },
  "components": {
    "primary.tekton": {
      "status": "running",
      "version": "0.1.0"
    }
  }
}
```

### Implementation Order
1. Local sync first (simpler, no external dependencies)
2. GitHub infrastructure second (authentication, gists)
3. Federation commands last (builds on both)

## Out of Scope
- Component-level GitHub access
- Real-time synchronization (eventual consistency is sufficient)
- Complex conflict resolution (last-write-wins is acceptable)
- Peer-to-peer gist sharing (hub-and-spoke model only)
- Encrypted communication (HTTPS/SSH is sufficient)

## Files to Update
```
# Phase 1 - Local Sync
/Users/cskoons/projects/github/till/src/till_host.c
/Users/cskoons/projects/github/till/src/till_config.h
/Users/cskoons/projects/github/till/src/till_common.c
/Users/cskoons/projects/github/till/src/till.c

# Phase 2 - GitHub Federation
/Users/cskoons/projects/github/till/src/till_github.c (new)
/Users/cskoons/projects/github/till/src/till_github.h (new)
/Users/cskoons/projects/github/till/src/till_federate.c (new)
/Users/cskoons/projects/github/till/src/till_federate.h (new)

# Phase 3 - Commands
/Users/cskoons/projects/github/till/src/till.c
/Users/cskoons/projects/github/till/src/till_sync.c (new)
/Users/cskoons/projects/github/till/Makefile
```

## Daily Progress Tracking

### Session 1 - Planning and Architecture
- Created sprint document
- Defined three-phase approach
- Established architecture principles
- Designed data structures

### Session 2 - Phase 1 Implementation
- Added `actual_hostname` field to host structure
- Implemented hostname capture via SSH during `till host add`
- Added `local_hostname` to hosts-local.json for self-identification
- Implemented automatic host propagation after add/remove
- Created merge logic with version-based conflict resolution
- Added self-detection to prevent circular updates
- Implemented soft delete with timestamps (hosts marked as "removed")
- Created `till host sync` command for manual reconciliation
- Added opportunistic sync during add/remove operations
- Successfully compiled and tested

### Next Steps
1. Test Phase 1 with actual remote hosts
2. Review and refine Phase 2 (GitHub Federation) design
3. Begin Phase 2 implementation if testing successful

## Handoff Notes
**For next session**: Start with Phase 1, Task 1 - adding the `actual_hostname` field to the host structure in till_host.c. The field should be captured during `till host add` by running `hostname` on the remote system via SSH. Store both the local hostname and remote hostnames to enable self-detection and prevent circular updates.