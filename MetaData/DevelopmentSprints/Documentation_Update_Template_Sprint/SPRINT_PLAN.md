# Sprint: Documentation Update - [PREVIOUS_SPRINT_NAME]

## Overview
Update Tekton documentation to reflect changes made during [PREVIOUS_SPRINT_NAME]. Focus on documenting what was actually built, not what was planned.

## Goals
1. **Capture Changes**: Document what actually changed in the code
2. **Update Guides**: Ensure guides reflect new patterns/features
3. **Fix Examples**: Update code examples to match current implementation

## Phase 1: Change Analysis [0% Complete]

### Tasks
- [ ] Review git commits from [PREVIOUS_SPRINT_NAME]
- [ ] List all files modified/added/removed
- [ ] Identify which components were affected
- [ ] Note any new patterns or conventions introduced
- [ ] Check for breaking changes

### Success Criteria
- [ ] Complete list of changes documented
- [ ] Know which docs need updates
- [ ] No code changes made

### Commands
```bash
# Review changes from sprint
cd $TEKTON_ROOT
git log --oneline --since="[sprint start date]"
git diff [start_commit]..HEAD --name-status

# Check which components were touched
git diff [start_commit]..HEAD --name-only | grep -E "^(numa|apollo|athena|rhetor|aish|terma)/"
```

## Phase 2: Documentation Updates [0% Complete]

### Tasks
#### Architecture Updates
- [ ] Update Architecture docs if patterns changed
- [ ] Document any new architectural decisions
- [ ] Update component interaction diagrams

#### Standards Updates  
- [ ] Update Standards if new conventions introduced
- [ ] Document any new error patterns
- [ ] Update API standards if endpoints changed

#### Component Guide Updates
- [ ] Update ComponentGuides if build process changed
- [ ] Document new instrumentation patterns
- [ ] Update testing approaches

#### AI Training Updates
- [ ] Update training docs for modified AIs
- [ ] Document new capabilities added
- [ ] Update command references

#### Developer Guide Updates
- [ ] Update debugging guides for new features
- [ ] Document new troubleshooting steps
- [ ] Update instrumentation examples

### Success Criteria
- [ ] All affected docs updated
- [ ] Examples work with current code
- [ ] No outdated information remains

## Phase 3: Quick Reference Updates [0% Complete]

### Tasks
- [ ] Update QuickStart guides if setup changed
- [ ] Update MCP docs if tools added/changed
- [ ] Create/update command reference sheets
- [ ] Update any cheat sheets

### Success Criteria
- [ ] New users can follow guides successfully
- [ ] Quick references are accurate
- [ ] Common tasks documented

## Phase 4: Release Documentation [0% Complete]

### Tasks
- [ ] Create release notes for the sprint
- [ ] Document any migration steps needed
- [ ] List known issues or limitations
- [ ] Update test documentation

### Release Note Template
```markdown
# [PREVIOUS_SPRINT_NAME] Release Notes

## What Changed
- [Feature/Fix]: [Description]
- [Feature/Fix]: [Description]

## Breaking Changes
- [If any]

## Migration Steps
1. [If needed]

## Known Issues
- [If any]

## Testing
- Run: `[test command]`
```

## Technical Decisions
- Document after code, not before
- Focus on what developers/CIs actually need
- Remove outdated information rather than updating it
- Use examples from actual code

## Out of Scope
- Creating new documentation categories
- Rewriting unchanged documentation
- Updating all documentation (only what changed)

## Files to Update
```
# Will be determined in Phase 1
MetaData/Documentation/[affected docs]
```