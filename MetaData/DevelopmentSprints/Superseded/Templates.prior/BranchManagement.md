# Tekton Branch Management Guide

This document outlines the branch management strategy for Tekton Development Sprints. It provides guidelines for creating, managing, and merging branches to ensure that development work is properly isolated and can be integrated smoothly.

## Overview

Tekton employs a branch-based development workflow to ensure that:

- Multiple Development Sprints can proceed in parallel without conflicts
- Changes can be reviewed and tested before integration
- Work is properly isolated to prevent unintended side effects
- History is preserved for future reference

Each Development Sprint must work on a dedicated branch. This isolation is crucial for maintaining the stability of the codebase while enabling parallel development efforts.

## Branch Naming Convention

Branches for Development Sprints should follow this naming convention:

```
sprint/[sprint-name]-[date]
```

Where:
- `[sprint-name]` is a brief, hyphenated name describing the sprint
- `[date]` is the sprint start date in YYMMDD format

Examples:
- `sprint/shared-code-250428`
- `sprint/github-utils-250505`
- `sprint/llm-integration-250512`

## Branch Management Utilities

Tekton provides several utilities to streamline branch management across components:

### tekton-branch-create

Creates branches with consistent naming across all components:

```bash
scripts/github/tekton-branch-create [OPTIONS] BRANCH_NAME

# Options:
#   -b, --base BRANCH    Base branch to create from (default: main)
#   -p, --push           Push new branches to remote repositories
#   -c, --components     Only create in component repositories
#   -m, --main-only      Only create in main repository
#   -f, --force          Force branch creation even if it exists

# Example:
scripts/github/tekton-branch-create -b develop -p sprint/feature-name-250430
```

### tekton-branch-verify

Verifies branch correctness before beginning work:

```bash
scripts/github/tekton-branch-verify [OPTIONS] EXPECTED_BRANCH

# Options:
#   -c, --claude         Format output specifically for Claude sessions
#   -s, --strict         Fail if branch doesn't exactly match expected
#   -j, --json           Output in JSON format

# Example:
scripts/github/tekton-branch-verify sprint/github-support-250430
```

### tekton-branch-status

Checks branch status across all Tekton components:

```bash
scripts/github/tekton-branch-status [OPTIONS] [BRANCH_NAME]

# Options:
#   -j, --json           Output in JSON format
#   -c, --components     Only check component repositories
#   -m, --main-only      Only check main repository
#   -r, --remote REMOTE  Remote name to check against (default: origin)

# Example:
scripts/github/tekton-branch-status -j sprint/feature-name-250430
```

### tekton-branch-sync

Synchronizes changes between branches across components:

```bash
scripts/github/tekton-branch-sync [OPTIONS] SOURCE_BRANCH TARGET_BRANCH

# Options:
#   -d, --dry-run        Show what would be done without making changes
#   -f, --force          Force synchronization even if conflicts are detected
#   -p, --push           Push changes after synchronization
#   -s, --strategy STR   Merge strategy to use (merge, rebase, cherry-pick)

# Example:
scripts/github/tekton-branch-sync -s rebase -p main sprint/feature-name-250430
```

### tekton-branch-cleanup

Safely removes unused branches:

```bash
scripts/github/tekton-branch-cleanup [OPTIONS] [PATTERN]

# Options:
#   -d, --dry-run        Show what would be done without making changes
#   -l, --local          Delete only local branches
#   -r, --remote         Delete only remote branches
#   -f, --force          Force branch deletion (including unmerged branches)
#   -o, --older-than N   Only delete branches older than N days

# Example:
scripts/github/tekton-branch-cleanup --dry-run "sprint/*"
```

## Branch Creation Process

1. **Before creating a branch**:
   - Ensure the main branch is up to date
   - Verify that all submodules are in sync

2. **Branch creation**:
   - Use the `tekton-branch-create` utility to create branches across all components
   - This utility handles the creation of branches in both the main repository and component repositories

### Example

```bash
# Ensure main is up to date
git checkout main
git pull
git submodule update --init --recursive

# Create the sprint branch across all components
scripts/github/tekton-branch-create -p sprint/shared-code-250428
```

## Submodule Management

Since Tekton consists of multiple components that may exist as submodules, special attention is needed for branch management across these components. The `tekton-branch-create` utility handles this automatically, but here's what's happening behind the scenes:

1. **Main Repository Branch**:
   - Create a branch in the main Tekton repository first

2. **Component Repository Branches**:
   - For each component that will be modified, create a corresponding branch
   - Use the same branch naming convention for consistency

3. **Submodule References**:
   - Update submodule references in the main repository to point to the component branches

### Manual Example for Component Branches

If you need to manually manage branches in a component:

```bash
# Navigate to component directory
cd Ergon

# Create corresponding branch
git checkout -b sprint/shared-code-250428
git push -u origin sprint/shared-code-250428

# Return to main repository
cd ..

# Update submodule reference
git add Ergon
git commit -m "Update Ergon submodule reference to sprint/shared-code-250428"
```

## Branch Verification for Claude Sessions

Working Claude sessions must verify they are working on the correct branch before making any changes. This verification should be performed at the start of each session and after any significant operation.

### Automated Branch Verification

Use the `tekton-branch-verify` utility for reliable branch verification:

```bash
# Verify current branch matches expected branch
scripts/github/tekton-branch-verify sprint/shared-code-250428

# For Claude sessions, use the --claude flag for structured output
scripts/github/tekton-branch-verify --claude sprint/shared-code-250428

# For stricter verification, use the --strict flag
scripts/github/tekton-branch-verify --strict sprint/shared-code-250428
```

### Claude-Specific Utilities

For Claude Code sessions, use the specialized helper scripts:

```bash
# Simple branch validation for Claude
scripts/github/claude/branch-validator.sh sprint/shared-code-250428

# Comprehensive session preparation with project context
scripts/github/claude/prepare-session.sh -c -p sprint/shared-code-250428
```

## Handling Changes During a Sprint

1. **Committing Changes**:
   - Make frequent, atomic commits with clear messages
   - Use the `tekton-commit` utility to ensure consistent message format:
     ```bash
     scripts/github/tekton-commit --title "Add branch management utilities" feature
     ```
   - Include the sprint name in commit messages for clarity

2. **Pushing Changes**:
   - Push changes to the remote branch regularly
   - Ensure submodule changes are pushed first, then update references

3. **Keeping Up with Main**:
   - If the sprint runs for an extended period, use `tekton-branch-sync` to stay current:
     ```bash
     scripts/github/tekton-branch-sync main sprint/shared-code-250428
     ```
   - Address any conflicts that arise

## Branch Status Checking

Regularly check the status of branches across components using the `tekton-branch-status` utility:

```bash
# Check status of current branch across all components
scripts/github/tekton-branch-status

# Check status of a specific branch
scripts/github/tekton-branch-status sprint/shared-code-250428

# Get detailed JSON output for automation
scripts/github/tekton-branch-status -j sprint/shared-code-250428
```

This will show which components are ahead, behind, or diverged from their remote branches, helping to identify synchronization issues early.

## Merging Process

When a sprint is completed and ready to be integrated:

1. **Pre-Merge Checks**:
   - Ensure all tests pass
   - Verify documentation has been updated
   - Review the code for quality and adherence to guidelines

2. **Submodule Merges**:
   - Merge component branches into their respective main branches first
   - Update submodule references in the main repository

3. **Main Repository Merge**:
   - Create a pull request from the sprint branch to main
   - Address any review comments
   - Merge the pull request
   - Delete the sprint branch when no longer needed

### Merge Command Example

```bash
# For each component
cd Ergon
git checkout main
git pull
git merge --no-ff sprint/shared-code-250428
git push

# Return to main repository
cd ..
git add Ergon  # Update submodule reference
git commit -m "Update Ergon submodule reference to main"

# Now create PR for main repository or merge directly
git checkout main
git pull
git merge --no-ff sprint/shared-code-250428
git push
```

## Branch Cleanup

After a sprint is successfully completed and merged, use the `tekton-branch-cleanup` utility:

```bash
# Preview which branches would be deleted (dry run)
scripts/github/tekton-branch-cleanup --dry-run "sprint/shared-code-*"

# Delete local and remote branches matching pattern
scripts/github/tekton-branch-cleanup "sprint/shared-code-*"

# Only delete branches older than 30 days
scripts/github/tekton-branch-cleanup --older-than 30 "sprint/*"
```

For manual cleanup:

1. **Delete Remote Branches**:
   ```bash
   git push origin --delete sprint/shared-code-250428
   ```

2. **Delete Local Branches**:
   ```bash
   git branch -d sprint/shared-code-250428
   ```

3. **Clean up Component Branches**:
   - Follow the same process for each component repository

## Handling Merge Conflicts

If merge conflicts occur during synchronization:

1. Use the `--dry-run` option with `tekton-branch-sync` to preview changes:
   ```bash
   scripts/github/tekton-branch-sync --dry-run main sprint/feature-name
   ```

2. For complex conflicts, you may need to resolve them manually:
   - Identify the conflicting files
   - Resolve conflicts with careful attention to both sets of changes
   - Test thoroughly after resolution
   - Document any significant conflict resolution decisions

3. After resolving conflicts, complete the synchronization:
   ```bash
   scripts/github/tekton-branch-sync main sprint/feature-name
   ```

## Branch Protection Guidelines

For critical components or the main repository, consider these branch protection rules:

1. Require pull request reviews before merging
2. Require status checks to pass before merging
3. Require branches to be up to date before merging
4. Prevent force pushes on protected branches
5. Restrict who can push to matching branches

## Troubleshooting

### Incorrect Branch

If a Working Claude session discovers it's working on the wrong branch:

1. Check the current branch status:
   ```bash
   scripts/github/tekton-branch-verify sprint/expected-branch-name
   ```

2. If needed, stash any uncommitted changes:
   ```bash
   git stash
   ```

3. Switch to the correct branch:
   ```bash
   git checkout sprint/shared-code-250428
   ```

4. Apply stashed changes if appropriate:
   ```bash
   git stash apply
   ```

5. Verify the changes make sense in the new context before committing

### Submodule Issues

If submodules are not tracking the correct branches, use the branch status utility to check:

```bash
scripts/github/tekton-branch-status
```

This will show which components are on different branches or have diverged from the expected state.

## References

For more detailed Git information, consult:

- [Pro Git Book](https://git-scm.com/book/en/v2)
- [GitHub Documentation](https://docs.github.com/en)
- Tekton's GitHub utilities documentation in `scripts/github/README.md`
- Tekton's CLAUDE.md for project-specific guidelines