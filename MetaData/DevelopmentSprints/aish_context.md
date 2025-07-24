# aish Context Save/Restore Development Sprint

## Sprint Overview

Create a context save/restore feature for aish that captures and restores complete CI working state. This allows CIs to suspend work, switch contexts, and resume exactly where they left off - including directory, environment, active forwards/routes, and notes.

**Philosophy**: Simple, works, hard to screw up. Unix-like composability.

## Core Design

### Context Structure (JSON)

```json
{
  "version": "1.0",
  "name": "auth-refactor",
  "created": "2025-07-24T10:30:00Z",
  "updated": "2025-07-24T11:45:00Z",
  "purpose": "Refactoring authentication module to support OAuth2",
  "working_directory": "/home/user/projects/webapp/auth",
  "environment": {
    "OAUTH_CLIENT_ID": "abc123",
    "API_ENDPOINT": "https://api.dev.example.com",
    "DEBUG": "true"
  },
  "forwards": [
    {
      "port": 8080,
      "target": "localhost:3000",
      "name": "webapp"
    },
    {
      "port": 5432,
      "target": "db.internal:5432",
      "name": "postgres"
    }
  ],
  "routes": [
    {
      "pattern": "/api/*",
      "destination": "backend:8000"
    }
  ],
  "notes": [
    "TODO: Update tests after OAuth implementation",
    "Check with security team about token expiry",
    "Migration script needed for existing users"
  ],
  "shell_history": [
    "npm test auth.spec.js",
    "git diff auth/",
    "curl -X POST localhost:8080/oauth/token"
  ]
}
```

### Storage Location

```
~/.tekton/contexts/
├── auth-refactor.json
├── bug-fix-123.json
├── feature-payments.json
└── .active -> auth-refactor.json  # symlink to active context
```

## Command Interface

### Save Context

```bash
# Save current state
aish context save auth-refactor

# Save with explicit purpose
aish context save auth-refactor --purpose "Refactoring auth module"

# Update existing context
aish context save auth-refactor --update

# Quick save to active context
aish context save
```

### Restore Context

```bash
# Restore named context
aish context restore auth-refactor

# Restore and set as active
aish context restore auth-refactor --activate

# Preview what would be restored
aish context restore auth-refactor --dry-run
```

### List and Manage

```bash
# List all contexts
aish context list

# Show detailed info
aish context show auth-refactor

# Show active context
aish context active

# Delete context
aish context delete auth-refactor

# Clean up old contexts (>30 days)
aish context clean --older-than 30d
```

### Update Context

```bash
# Add note to active context
aish context note "Check security review feedback"

# Update purpose
aish context purpose "OAuth2 implementation with PKCE"

# Capture current forwards/routes
aish context capture-network
```

## Implementation Plan

### Phase 1: Core Save/Restore

1. Create `src/commands/context_save.py`:
   - Capture current directory
   - Save environment variables (filtered)
   - Store purpose from `.purpose` file
   - Write JSON to `~/.tekton/contexts/`

2. Create `src/commands/context_restore.py`:
   - Read JSON context
   - Change to saved directory
   - Export environment variables
   - Restore purpose
   - Display notes

### Phase 2: Network State

3. Integrate with forward command:
   - Capture active forwards from registry
   - Store in context
   - Restore on context load

4. Integrate with route command:
   - Capture active routes
   - Store and restore

### Phase 3: Shell Integration

5. Shell history capture:
   - Last N commands from current session
   - Optional: full history export

6. Auto-save on exit:
   - Hook into shell exit
   - Save if context is "dirty"

### Phase 4: Advanced Features

7. Context switching:
   - Quick switch between contexts
   - Maintain context stack

8. Context templates:
   - Pre-defined contexts for common tasks
   - Share contexts between team members

## Technical Considerations

### Environment Variable Filtering

```python
# Sensitive patterns to exclude
EXCLUDE_PATTERNS = [
    '*_KEY', '*_SECRET', '*_TOKEN', '*_PASSWORD',
    'AWS_*', 'GITHUB_*', 'SSH_*'
]

# Always include
INCLUDE_PATTERNS = [
    'TEKTON_*', 'AISH_*', 'DEBUG', 'ENV'
]
```

### Atomic Operations

- Use temporary files + rename for saves
- Validate JSON before overwriting
- Keep backups of last N versions

### Integration Points

1. **aish purpose**: Auto-capture on save
2. **aish forward**: Registry integration
3. **aish route**: Route table export
4. **aish terma**: Terminal state awareness

## Usage Examples

### CI Workflow Integration

```bash
# Start new task
aish purpose "Fix authentication bug #123"
cd ~/projects/webapp
aish context save bug-123

# Work on the bug...
npm test
aish forward 8080 localhost:3000

# Need to switch to urgent issue
aish context save  # Updates current
aish context save urgent-fix --purpose "Production outage"

# Return to original work
aish context restore bug-123
# Automatically restores directory, env, forwards, shows notes
```

### Team Collaboration

```bash
# Share context
aish context export auth-refactor > auth-context.json
# Send to teammate

# Import shared context
aish context import < auth-context.json
aish context restore auth-refactor
```

## Success Metrics

1. **Adoption**: CIs use contexts naturally without training
2. **Reliability**: Zero data loss, clean error handling
3. **Speed**: Save/restore < 100ms
4. **Integration**: Works seamlessly with existing aish commands

## Edge Cases

1. **Directory deleted**: Graceful fallback to parent
2. **Port conflicts**: Warn but continue restore
3. **Large contexts**: Compress if > 1MB
4. **Corrupted JSON**: Keep backup, report error
5. **Permission issues**: Clear error messages

## Future Enhancements

- Git branch association
- Docker container state
- tmux session integration
- Context sharing via Rhetor
- Auto-context based on directory
- Context history/undo

## Implementation Notes

- Start simple: just directory and environment
- Add features based on CI feedback
- Keep JSON human-readable
- Follow Unix philosophy: do one thing well
- Make it hard to lose work

---

Sprint Duration: 2 weeks
Priority: High
Dependencies: None (can build incrementally)