# Sprint: aish alias - CI Pattern Building

## Overview
Enable CIs (Contextual Intelligences) to create and manage their own command patterns through an alias system that adapts Unix conventions for the aish environment, allowing natural vocabulary building and reusable command patterns.

## Goals
1. **CI Empowerment**: Allow CIs to dynamically create their own command patterns and vocabulary
2. **Unix Familiarity**: Follow established alias conventions adapted for aish's intelligent shell
3. **Pattern Reusability**: Enable both simple aliases and complex command pipelines with parameter substitution

## Phase 1: Foundation & Storage [0% Complete]

### Tasks
- [ ] Design alias storage format (JSON/YAML in .tekton/aliases/)
- [ ] Create `alias.py` command module with subcommands
- [ ] Implement alias data structures and validation
- [ ] Add alias storage/retrieval with file locking
- [ ] Create alias expansion logic in shell.py
- [ ] Add parameter substitution support ($1, $2, $*, $@)

### Success Criteria
- [ ] Aliases stored persistently in .tekton/aliases/
- [ ] Basic create/list/show/delete operations work
- [ ] Parameter substitution functions correctly
- [ ] Aliases survive shell restarts

### Blocked On
- [ ] Nothing currently blocking

## Phase 2: Integration & Execution [0% Complete]

### Tasks
- [ ] Integrate alias expansion into aish command pipeline
- [ ] Add alias precedence rules (alias before built-in commands)
- [ ] Implement recursive alias expansion with cycle detection
- [ ] Add context preservation for CI-created aliases
- [ ] Create alias export/import functionality
- [ ] Add alias categories/namespaces for organization

### Success Criteria
- [ ] Aliases execute seamlessly in command flow
- [ ] Complex pipelines work with parameter substitution
- [ ] No infinite recursion on circular aliases
- [ ] CI context preserved in alias metadata

### Blocked On
- [ ] Waiting for Phase 1 completion

## Phase 3: CI Experience & Polish [0% Complete]

### Tasks
- [ ] Add natural language alias creation ("save last command as...")
- [ ] Implement alias suggestions based on command history
- [ ] Create alias sharing mechanism between CIs
- [ ] Add alias documentation/help system
- [ ] Implement alias versioning for updates
- [ ] Create comprehensive test suite

### Success Criteria
- [ ] CIs can create aliases conversationally
- [ ] Alias discovery is intuitive
- [ ] Shared aliases work across CI instances
- [ ] All edge cases handled gracefully

### Blocked On
- [ ] Waiting for Phase 2 completion

## Technical Decisions

### Storage Format
```json
{
  "name": "deploy-prod",
  "command": "git push origin main && ssh prod 'cd /app && git pull && docker-compose up -d'",
  "description": "Deploy current branch to production",
  "parameters": ["branch_name"],
  "created_by": "CI-instance-id",
  "created_at": "2025-01-24T10:00:00Z",
  "context": {
    "project": "tekton",
    "purpose": "deployment automation"
  }
}
```

### Command Structure
```bash
# Create alias
aish alias create deploy-prod "git push && ssh prod deploy"
aish alias create greet "echo Hello, $1!"

# List aliases
aish alias list
aish alias list --category deployment

# Show specific alias
aish alias show deploy-prod

# Delete alias
aish alias delete deploy-prod

# Execute alias
aish deploy-prod
aish greet "Casey"
```

### Design Principles
1. **Simple by default**: Basic string replacement works immediately
2. **Powerful when needed**: Full parameter substitution and pipelines
3. **CI-aware**: Aliases remember their creation context
4. **Hard to screw up**: Validate syntax, prevent dangerous patterns

## Out of Scope
- Shell function syntax (use simple command strings)
- Environment variable manipulation within aliases
- Conditional logic in aliases (keep it simple)
- Global system-wide aliases (user-specific only)
- Complex scripting features (that's what scripts are for)

## Files to Update
```
/Users/cskoons/projects/github/Coder-C/shared/aish/src/commands/alias.py (new)
/Users/cskoons/projects/github/Coder-C/shared/aish/src/core/shell.py
/Users/cskoons/projects/github/Coder-C/shared/aish/src/parser/pipeline.py
/Users/cskoons/projects/github/Coder-C/shared/aish/src/utils/alias_manager.py (new)
/Users/cskoons/projects/github/Coder-C/shared/aish/tests/test_alias.py (new)
~/.tekton/aliases/ (new directory structure)
```

## Implementation Notes

### Alias Expansion Order
1. Check if command is an alias
2. Expand alias with parameter substitution
3. Check for recursive aliases (with cycle detection)
4. Pass expanded command to normal pipeline

### Parameter Substitution
- `$1, $2, ...` - Positional parameters
- `$*` - All parameters as single string
- `$@` - All parameters as separate words
- `$$` - Literal $ character

### CI Integration Points
- Aliases can store CI context for later reference
- CIs can query and modify aliases programmatically
- Natural language creation through conversation
- Pattern learning from command history

### Security Considerations
- Validate alias names (no path traversal)
- Sanitize commands (no arbitrary code execution)
- Limit alias file sizes
- Implement rate limiting for creation

## Success Metrics
1. CIs successfully create and use custom vocabulary
2. Users find alias system intuitive and Unix-like
3. Complex workflows simplified through reusable patterns
4. No security vulnerabilities or command injection
5. Performance impact negligible (<10ms per command)