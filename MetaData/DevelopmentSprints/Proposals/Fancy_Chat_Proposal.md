# Fancy Chat - Enhanced Command Features Proposal

## Overview
This proposal outlines potential enhancements to the Tekton chat command system that uses `[]` syntax for inline command execution. These features would build upon the basic command execution and output routing already implemented.

## Current State (August 2025)
- Basic command execution with `[command]` syntax
- Output routing modes: `>` (AI only), `>>` (user + AI context)
- Blacklist-based safety checking
- 25K character output truncation
- Multiple commands per message supported

## Fundamental Limitations
- **No shell state persistence**: Each command runs in a new subprocess, so `cd` commands don't affect subsequent commands
- **No background processes**: Commands run synchronously with 10-second timeout
- **No interactive commands**: Can't run vim, less, or other interactive tools

## Proposed Features

### Quick Wins (High Value, Low Complexity)

#### 1. Command Aliases
User-definable shortcuts for common commands.
```
[g status] → [git status]
[ll] → [ls -la]
[test] → [npm test]
```
Implementation: Simple string replacement before parsing.

#### 2. Command Annotations  
Comments for context that get passed to AI.
```
[ls -la] # checking for config files
[git diff] # looking at recent changes
```
The comment after `#` would be included in context to AI.

### Intermediate Features

#### 3. Command Templates/Macros
Save and replay command sequences.
```
[macro: deploy] → Expands to:
  [git pull]
  [npm install]
  [npm test]
  [npm run build]
```

#### 4. Conditional Execution
Basic shell conditionals.
```
[[ -f package.json ]] && [npm install]
[[ -d .git ]] || [git init]
```

#### 5. Save/Replay Sessions
Export chat sessions with commands as runbooks.
- Save successful command sequences
- Share workflows with team
- Replay for automation

### Advanced Features

#### 6. Pipe to AI Tools
Special AI-aware commands in pipes.
```
[git diff | explain >]  # Sends diff to AI with "explain this" prompt
[ls -la | summarize >]  # AI summarizes file list
[cat error.log | debug >]  # AI analyzes error log
```

#### 7. Multi-AI Routing
Direct commands to specific AI specialists.
```
[apollo: git status >]  # Send to Apollo
[athena: SELECT * FROM users | analyze >]  # Athena analyzes query
```

#### 8. Smart Context Management
Commands that automatically set context.
```
[cd ~/projects/tekton]  # AI knows we're working on Tekton
[git checkout feature-x]  # AI knows we're on feature-x branch
[source venv/bin/activate]  # AI knows Python environment
```

#### 9. Progress Tracking
Task-oriented command grouping.
```
[task: setup environment]
[python -m venv venv]
[source venv/bin/activate]
[pip install -r requirements.txt]
[task: complete]
```
Shows progress bar, tracks time, logs to history.

#### 10. Inline Previews
Hover interactions without execution.
- Hover over `[cat large_file.json]` to preview first 50 lines
- Hover over file paths to see file info
- Hover over git commands to see current branch/status

#### 11. Side-by-Side Diffs
When commands modify files, show inline diffs.
```
[sed -i 's/old/new/g' config.txt]
# Shows before/after diff in chat
```

#### 12. Smart Defaults
Context-aware command suggestions based on:
- Current directory contents
- Recent commands
- Common patterns
- File types present

### UI/UX Enhancements

#### 13. Breadcrumbs Bar
Persistent status bar showing:
- Current directory
- Git branch
- Virtual environment
- Last command status
- Container/SSH context if applicable

#### 14. Command Palette
- Cmd/Ctrl+K to open command palette
- Search through command history
- Browse available macros/templates
- Quick access to common commands

#### 15. Rich Output Rendering
- Tables for structured data
- Syntax highlighting for code files
- Image previews for image files
- JSON/YAML folding
- CSV as tables

## Implementation Priority

### Phase 1 (Current Sprint)
✅ Basic command execution
✅ Output routing (>, >>)
✅ Safety blacklist
- Command history (up arrow)
- Tab completion
- Syntax highlighting (success/failure colors)
- Edit in place (left/right arrows)
- Clear command

### Phase 2 (Next Sprint)
- Command aliases
- Command annotations
- Basic templates

### Phase 3 (Future)
- Conditional execution
- Session save/replay
- AI tool pipes
- Multi-AI routing

## Questions for Discussion

1. **Shell State**: Should we implement a persistent shell session per component? This would enable `cd` and environment variables but adds complexity.

2. **Security**: Should the blacklist be configurable per-user? Should we add a whitelist mode for production?

3. **Storage**: Where should command history, aliases, and macros be stored? Component-specific or global?

4. **Syntax**: Should we support bash-style history expansion (`!!`, `!$`, etc.)?

5. **Integration**: Should commands be able to trigger Tekton workflows or interact with other components?

## Notes

The goal is to keep the command syntax "just like unix/linux" so users don't need to learn new patterns. Features should be discoverable through normal terminal muscle memory (up arrow, tab, etc.) rather than requiring documentation.

The beauty of the `[]` syntax is its simplicity - we should resist the urge to make it too complex. Each feature should feel natural and optional.