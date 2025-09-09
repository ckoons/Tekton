# Handoff Document: Till Lifecycle Manager and Federation System

## Current Status
**Phase**: Planning/Architecture Complete, Ready for C Implementation  
**Progress**: 0% Implementation (100% Design)  
**Last Updated**: 2024-08-31

## What Was Just Completed
- Redefined Till as comprehensive Tekton lifecycle manager (not just federation)
- Specified C implementation with single header configuration file
- Designed complete installation flow for solo/observer/member modes
- Created registration via ephemeral GitHub branches
- Defined Till command structure and host management
- Established Till as separate repository from Tekton

## What Needs To Be Done Next
1. **IMMEDIATE**: Create Till C project with Makefile and till_config.h
2. **NEXT**: Implement core till.c with basic command parsing
3. **THEN**: Add JSON handling (cJSON or jq integration)
4. **AFTER**: Build menu-of-the-day fetching from GitHub
5. **FINALLY**: Implement registration branch creation for federation

## Current Blockers
- [x] ~~Need Casey's decision on implementation language~~ → C confirmed
- [ ] Need to finalize menu-of-the-day JSON structure
- [ ] Need GitHub organization name for future migration from ckoons

## Important Context

### Till Scope Expansion
- **Primary Role**: Tekton lifecycle manager (installation, updates, federation)
- **Implementation**: C program with no external dependencies except git/gh
- **Configuration**: Single header file (till_config.h) for all paths/URLs
- **Solo Support**: Even solo installations use Till for component updates

### Installation Modes
1. **Solo**: No federation, just installation and updates
2. **Observer**: Generates keypair, registers via branch, read-only federation
3. **Member**: Full federation with bidirectional trust

### Registration Process
- Create branch: `registration-[fqn]-[mode]`
- Push minimal info (or encode in branch name)
- GitHub action processes and updates registry
- Local Till deletes branch after push (never persistent)

### Key Design Principles
- **No hardcoded paths/URLs**: Everything in till_config.h
- **Terminal only**: No UI beyond command line
- **Portable C**: Must compile on Mac/Linux with standard toolchain
- **Git/gh commands**: Use system() calls, let user handle auth

### Relationship Types
1. **Solo**: Invisible, can pull but not seen by others
2. **Observer**: Visible in status, cannot modify others
3. **Member**: Full bidirectional sync and configuration sharing

## Test Status
- Unit tests: Not started
- Integration tests: Not started
- Design validation: Complete through discussion

## Files Being Modified
```
# These files need to be created:
/till/                          # New directory for Till system
/till/till.py                   # Main Till implementation
/till/branch_manager.py         # GitHub branch operations
/till/federation.py             # Federation protocol
/till/cli.py                    # Command-line interface

# These need updates:
/Hermes/hermes.py              # Add federation endpoints
/scripts/tekton                # Integrate till commands
```

## Commands to Run on Startup
```bash
# Get to the right state
cd $TEKTON_ROOT
git status

# Check if sprint directory exists
ls -la MetaData/DevelopmentSprints/Federation_till_Sprint/

# Review the design documents
cat MetaData/DevelopmentSprints/Federation_till_Sprint/SPRINT_PLAN.md
cat MetaData/DevelopmentSprints/Federation_till_Sprint/DAILY_LOG.md
```

## Questions Needing Answers
1. Should Till be implemented in Python (integrate easily) or C (standalone, faster)?
2. What should default TTLs be? (suggested: public-face=3d, component=24h, handshake=15m)
3. Do we need encryption for federation data or rely on HTTPS?
4. Should branch cleanup be logged to federation branch for audit?
5. How should we handle federation version mismatches?

## Do NOT Touch
- Main branch - all work in ephemeral branches initially
- Existing Hermes functionality - add federation as new endpoints
- Current Tekton start/stop/status - integrate, don't replace

## Notes for Next Session
- Review Casey's answers to questions above
- Start with Till core before federation protocol
- Consider creating mock GitHub repo for testing branch operations
- Remember: "till sync" is the primary operation everything else supports

## Key Design Principles to Remember
1. **Loosely Coupled**: Tektons coordinate but remain independent
2. **Trust-Based**: Relationships define permissions
3. **Natural Growth**: Communities form organically
4. **Public/Private Split**: Share what you choose
5. **Automatic Lifecycle**: Active content stays, inactive expires

## Example Configurations for Reference

### Public Till Example
```json
{
  "format": "till-federation-v1",
  "version": "1.0.0",
  "identity": {
    "name": "Kant-Tekton",
    "uuid": "kant-uuid-12345",
    "endpoint": "https://kant.example.com:8101",
    "capabilities": ["numa", "rhetor", "apollo"]
  }
}
```

### Private Till Example
```json
{
  "format": "till-federation-v1",
  "version": "1.0.0",
  "relationships": {
    "hume-uuid-67890": {
      "name": "Hume-Tekton",
      "role": "member",
      "accept_prs": true,
      "trust_level": "high"
    }
  }
}
```

### Branch Registry Example
```json
{
  "ephemeral": {
    "kant-tekton-3d": {
      "owner": "kant-uuid-12345",
      "expires": "2024-01-04T00:00:00Z",
      "ttl_hours": 72,
      "purpose": "public-face"
    }
  }
}
```