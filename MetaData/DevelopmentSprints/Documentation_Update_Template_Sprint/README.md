# Documentation Update Sprint Template

## Purpose
This template is used after completing any development sprint to update the documentation with what was actually built. The same Claude Code that did the implementation should handle the documentation updates for best context.

## When to Use
- After completing any feature sprint
- After component renovation sprints  
- After architectural changes
- When documentation drift is noticed

## How to Use

1. **Copy this template** to a new directory:
   ```bash
   cp -r Documentation_Update_Template_Sprint/ Documentation_Update_[SprintName]_Sprint/
   ```

2. **Replace placeholders** in all files:
   - [PREVIOUS_SPRINT_NAME] → Actual sprint name
   - [Date] → Current date
   - [sprint start date] → When coding sprint began
   - [start_commit] → Git commit where sprint started

3. **Start with Phase 1** - Analyze what actually changed
4. **Update only affected docs** - Don't update everything
5. **Focus on accuracy** - Document what IS, not what WAS PLANNED

## Key Principles

### Do:
- ✓ Document actual implementation
- ✓ Update examples to working code
- ✓ Remove outdated information
- ✓ Create release notes
- ✓ Focus on developer/CI needs

### Don't:
- ✗ Document planned features that weren't built
- ✗ Update unrelated documentation  
- ✗ Rewrite working documentation
- ✗ Create extensive prose
- ✗ Update docs before code

## Documentation Priority

1. **Breaking Changes** - Must document immediately
2. **New Patterns** - Developers need to know
3. **API Changes** - Affects integration
4. **New Features** - How to use them
5. **Bug Fixes** - Only if behavior changed

## Success Metrics

- Developers can use new features without asking questions
- Examples compile and run correctly
- No references to old patterns remain
- CI training is updated for new capabilities

## Time Estimate

- Small sprint (1-2 components): 1 day
- Medium sprint (3-5 components): 2 days  
- Large sprint (architecture changes): 3-4 days

Remember: Good documentation follows good code. Update what matters, delete what doesn't.