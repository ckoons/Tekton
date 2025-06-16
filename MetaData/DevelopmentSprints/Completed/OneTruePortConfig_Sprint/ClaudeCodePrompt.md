# Claude Code Prompt - OneTruePortConfig Sprint

## Sprint Context
You are about to work on the OneTruePortConfig Sprint for the Tekton project. This sprint aims to centralize all port configuration across Tekton components, eliminating hardcoded values and establishing consistent patterns.

## Branch Information
**Branch Name**: sprint/OneTruePortConfig  
**Base Branch**: main

## Critical First Step
Before beginning ANY work, verify you are on the correct branch:
```bash
git branch --show-current
```
This should return: `sprint/OneTruePortConfig`

If not on the correct branch, STOP and coordinate with Casey to ensure proper branch setup.

## Required Reading
Please read the following documents in order:
1. `/MetaData/DevelopmentSprints/OneTruePortConfig_Sprint/SprintPlan.md`
2. `/MetaData/DevelopmentSprints/OneTruePortConfig_Sprint/ArchitecturalDecisions.md`
3. `/MetaData/DevelopmentSprints/OneTruePortConfig_Sprint/ImplementationPlan.md`
4. Current port configuration files:
   - `/shared/utils/env_config.py`
   - `/shared/utils/env_manager.py`
   - `/.env.tekton`

## Your Task
Review the sprint plan and implementation guide, then:

1. **Analyze Current State**
   - Map out where ports are currently defined and used
   - Identify all hardcoded port values across components
   - Document patterns of cross-component communication
   - Note any special cases or exceptions

2. **Propose Implementation Approach**
   - Based on your analysis, refine the implementation plan
   - Suggest specific module structures and APIs
   - Identify any risks or considerations not covered
   - Propose migration order and strategy

3. **Begin Implementation**
   - Start with Phase 1: Core Infrastructure
   - Create central port configuration system
   - Implement with debug instrumentation throughout
   - Ensure backwards compatibility

## Key Constraints
- Must maintain backwards compatibility during migration
- Cannot break existing deployments
- All code must include debug instrumentation
- Changes must be systematic and traceable
- Service discovery must work in local development

## Code Patterns to Follow
- Use env_manager patterns for configuration loading
- Follow Tekton debug instrumentation standards
- Maintain consistent error handling
- Provide clear validation messages
- Document all new utilities and patterns

## Testing Requirements
- Unit tests for all new utilities
- Integration tests for service discovery
- Component startup verification
- No hardcoded ports in test code
- Mock configurations for testing

## Documentation Updates
As you work, update:
- Component README files noting configuration changes
- API documentation for new utilities
- Configuration guide for developers
- Migration notes for existing deployments

## Deliverables for This Session
1. Detailed analysis of current port configuration state
2. Refined implementation proposal with specific APIs
3. Phase 1 implementation (if time permits)
4. Clear notes on migration strategy
5. List of all components requiring updates

## Questions to Consider
- How should components discover each other's ports?
- What validation should occur at startup?
- How to handle port conflicts?
- What's the cleanest API for port access?
- How to minimize migration risk?

## Communication
- Document key decisions and trade-offs
- Note any blockers or concerns
- Identify areas needing Casey's input
- Keep clear progress notes

Remember: The goal is to create a single, maintainable source of truth for all port configuration while ensuring system reliability throughout the transition.