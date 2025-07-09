# Tekton GitHub Utilities

## Overview

This directory contains utilities and tools for managing GitHub operations for the Tekton project. These utilities simplify branch management, status checking, and verification across multiple Tekton components.

## Installation

You can install these utilities using the provided installation script:

```bash
./scripts/github/install.sh
```

This will create symbolic links in your `~/.local/bin` directory (or another directory of your choice) to make the utilities available system-wide.

## Directory Structure

- `lib/`: Shared library functions used by GitHub utilities
- `templates/`: Template files for GitHub operations (commit messages, PR templates)
- `claude/`: Helper scripts designed for Claude Code sessions
- `examples/`: Example usage of GitHub utilities

## Available Utilities

### Branch Management

#### tekton-branch-create

Creates branches with consistent naming across all components.

```bash
tekton-branch-create [OPTIONS] BRANCH_NAME

Options:
  -h, --help           Display help message and exit
  -v, --verbose        Enable verbose output
  -b, --base BRANCH    Base branch to create new branch from (default: main)
  -p, --push           Push the new branch to remote repositories
  -c, --components     Only create branches in component repositories
  -m, --main-only      Only create branch in the main repository
  -f, --force          Force branch creation even if it already exists
  
Arguments:
  BRANCH_NAME          Name of the branch to create (e.g., sprint/feature-name-YYMMDD)

Examples:
  tekton-branch-create sprint/github-support-250430
    Create a branch named 'sprint/github-support-250430' in all repositories

  tekton-branch-create -b develop -p sprint/feature-name-250430
    Create a branch from 'develop' and push it to remote repositories
```

#### tekton-branch-status

Checks branch status across all Tekton components.

```bash
tekton-branch-status [OPTIONS] [BRANCH_NAME]

Options:
  -h, --help           Display help message and exit
  -v, --verbose        Enable verbose output
  -j, --json           Output in JSON format
  -c, --components     Only check component repositories
  -m, --main-only      Only check main repository
  -r, --remote REMOTE  Remote name to check against (default: origin)
  
Arguments:
  BRANCH_NAME          Name of the branch to check (defaults to current branch)

Examples:
  tekton-branch-status
    Check status of the current branch across all repositories

  tekton-branch-status sprint/github-support-250430
    Check status of the 'sprint/github-support-250430' branch

  tekton-branch-status -j sprint/feature-name-250430
    Check status and output in JSON format
```

#### tekton-branch-verify

Verifies branch correctness for Claude sessions.

```bash
tekton-branch-verify [OPTIONS] [EXPECTED_BRANCH]

Options:
  -h, --help           Display help message and exit
  -v, --verbose        Enable verbose output
  -j, --json           Output in JSON format
  -c, --claude         Format output specifically for Claude sessions
  -s, --strict         Fail if branch doesn't exactly match expected
  
Arguments:
  EXPECTED_BRANCH      Expected branch name to verify against

Examples:
  tekton-branch-verify sprint/github-support-250430
    Verify current branch against 'sprint/github-support-250430'

  tekton-branch-verify -c sprint/feature-name-250430
    Verify and format output for Claude sessions
```

#### tekton-branch-sync

Synchronize changes between branches across multiple Tekton components.

```bash
tekton-branch-sync [OPTIONS] SOURCE_BRANCH TARGET_BRANCH

Options:
  -h, --help           Display help message and exit
  -v, --verbose        Enable verbose output
  -d, --dry-run        Show what would be done without making changes
  -f, --force          Force synchronization even if conflicts are detected
  -c, --components     Only synchronize component repositories
  -m, --main-only      Only synchronize main repository
  -p, --push           Push changes after synchronization
  -s, --strategy STR   Merge strategy to use (merge, rebase, cherry-pick)
  
Arguments:
  SOURCE_BRANCH        Source branch containing changes to synchronize
  TARGET_BRANCH        Target branch to synchronize changes to

Examples:
  tekton-branch-sync sprint/feature-a-250430 sprint/feature-b-250430
    Synchronize changes from feature-a to feature-b across all repositories

  tekton-branch-sync -s rebase -p main sprint/feature-name-250430
    Rebase feature branch on main branch and push changes
```

#### tekton-branch-cleanup

Clean up unused branches across Tekton components.

```bash
tekton-branch-cleanup [OPTIONS] [PATTERN]

Options:
  -h, --help           Display help message and exit
  -v, --verbose        Enable verbose output
  -d, --dry-run        Show what would be done without making changes
  -l, --local          Delete only local branches
  -r, --remote         Delete only remote branches
  -f, --force          Force branch deletion (including unmerged branches)
  -c, --components     Only clean up component repositories
  -m, --main-only      Only clean up main repository
  -a, --all            Include all branches (override protection)
  -o, --older-than N   Only delete branches older than N days
  
Arguments:
  PATTERN              Optional pattern to match branch names (e.g., "sprint/*")

Examples:
  tekton-branch-cleanup --dry-run "sprint/*"
    Show which sprint branches would be deleted

  tekton-branch-cleanup --local --older-than 90 "feature/*"
    Delete local feature branches older than 90 days

  tekton-branch-cleanup --remote --force "bugfix/*"
    Force delete remote bugfix branches
```

#### tekton-branch-merge

Merge branches across Tekton components, with options for creating pull requests or direct merges.

```bash
tekton-branch-merge [OPTIONS] SOURCE_BRANCH [TARGET_BRANCH]

Options:
  -h, --help           Display help message and exit
  -v, --verbose        Enable verbose output
  -d, --dry-run        Show what would be done without making changes
  -p, --push           Push changes after merging
  -r, --pr             Create a pull request instead of direct merge
  -y, --yes            Skip all confirmation prompts (YOLO mode)
  -m, --message TEXT   Custom merge commit message
  -f, --force          Force merge even if conflicts are detected
  -c, --components     Only merge component repositories
  -M, --main-only      Only merge main repository
  
Arguments:
  SOURCE_BRANCH        Source branch containing changes to merge
  TARGET_BRANCH        Target branch to merge changes into (defaults to main)

Examples:
  tekton-branch-merge sprint/feature-name-250430
    Merge sprint branch into main across all repositories

  tekton-branch-merge -p -y sprint/feature-name-250430
    Merge sprint branch into main and push changes, skipping confirmations (YOLO)

  tekton-branch-merge -r sprint/feature-name-250430 main
    Create pull requests from feature branch to main for all components
```

### Commit Management

#### tekton-commit

Generate and apply standardized commit messages.

```bash
tekton-commit [OPTIONS] [COMMIT_TYPE]

Options:
  -h, --help           Display help message and exit
  -v, --verbose        Enable verbose output
  -l, --list           List available commit types and templates
  -p, --preview        Preview the commit message without applying it
  -t, --title TITLE    Commit title (required unless using --preview)
  -m, --message TEXT   Custom message (replaces template bullets)
  -c, --components     Include list of affected components in commit
  -i, --issue NUM      Reference issue number in commit
  -e, --edit           Open commit message in editor before committing
  
Arguments:
  COMMIT_TYPE          Type of commit: feature, fix, docs, refactor, etc.
                       (Defaults to "feature" if not specified)

Examples:
  tekton-commit --title "Add branch management utilities" feature
    Create a feature commit with the given title

  tekton-commit --title "Fix component detection" --issue 123 fix
    Create a bugfix commit that references issue #123

  tekton-commit --preview --title "Update documentation" docs
    Preview a documentation commit message without applying it
```

### Claude Code Helpers

#### branch-validator.sh

Validates branch correctness for Claude Code sessions.

```bash
claude/branch-validator.sh EXPECTED_BRANCH

Examples:
  claude/branch-validator.sh sprint/github-support-250430
    Check if current branch matches expected branch with Claude-friendly output
```

#### prepare-session.sh

Prepares environment for Claude Code sessions by verifying branch, loading project context, and generating structured output.

```bash
claude/prepare-session.sh [OPTIONS] EXPECTED_BRANCH

Options:
  -h, --help           Display help message and exit
  -v, --verbose        Enable verbose output
  -c, --component      Include component-specific context
  -p, --project        Include project-wide context
  -s, --strict         Fail if branch doesn't exactly match expected
  
Arguments:
  EXPECTED_BRANCH      Expected branch name to verify against

Examples:
  claude/prepare-session.sh sprint/github-support-250430
    Prepare session for the 'sprint/github-support-250430' branch

  claude/prepare-session.sh -c -p sprint/feature-name-250430
    Prepare session with component and project context
```

#### generate-commit.sh

Generates a structured commit message template for Claude Code sessions.

```bash
claude/generate-commit.sh COMMIT_TYPE

Examples:
  claude/generate-commit.sh feature
    Generate a feature commit message template

  claude/generate-commit.sh fix
    Generate a bugfix commit message template
```

## Template Files

### Commit Message Templates

Located in `templates/commit-messages/`:

- `feature.txt`: Template for feature commits
- `fix.txt`: Template for bugfix commits
- `docs.txt`: Template for documentation updates
- `refactor.txt`: Template for code refactoring
- `test.txt`: Template for test-related changes
- `chore.txt`: Template for maintenance tasks

These templates include placeholders that will be filled interactively or via command-line arguments.

### PR Description Templates

Located in `templates/pr-templates/`:

- `feature.txt`: Template for feature PRs
- `bugfix.txt`: Template for bugfix PRs
- `documentation.txt`: Template for documentation PRs
- `refactor.txt`: Template for refactoring PRs
- `sprint-completion.txt`: Template for sprint completion PRs

## Common Workflows

### Starting a New Development Sprint

```bash
# Create a new sprint branch across all components
tekton-branch-create sprint/feature-name-YYMMDD

# Verify the branch was created correctly
tekton-branch-status sprint/feature-name-YYMMDD
```

### Working in a Claude Code Session

```bash
# Prepare the Claude session with project context
scripts/github/claude/prepare-session.sh -c -p sprint/feature-name-YYMMDD

# Create a commit with standardized message
scripts/github/tekton-commit --title "Add new feature" feature
```

### Synchronizing with Main Branch

```bash
# Synchronize the current sprint branch with main
tekton-branch-sync main sprint/feature-name-YYMMDD

# Push changes to remote
git push
```

### Completing a Sprint

```bash
# Verify all changes are properly synchronized
tekton-branch-status sprint/feature-name-YYMMDD

# Create final commit summarizing changes
tekton-commit --title "Complete feature implementation" feature

# Push final changes
git push

# Merge the sprint branch into main (interactive mode)
tekton-branch-merge sprint/feature-name-YYMMDD

# Or create pull requests instead of direct merges
tekton-branch-merge --pr sprint/feature-name-YYMMDD

# Clean up after merging and approving PRs
tekton-branch-cleanup sprint/feature-name-YYMMDD
```

## Library Documentation

For detailed documentation of the library functions used by these utilities, see the comments in the library files:

- `lib/github-utils.sh`: Core utility functions for GitHub operations
- `lib/error-utils.sh`: Error handling and reporting utilities
- `lib/component-utils.sh`: Component management utilities

## Examples

See the `examples/` directory for detailed examples of common workflows and use cases.

## Contributing

When adding new functionality to these utilities:

1. Ensure consistent command-line interface and options
2. Update documentation in both script help text and this README
3. Add examples for new features
4. Follow the error handling patterns established in existing utilities

## Troubleshooting

### Branch creation fails

- Ensure you have write access to all repositories
- Check if the branch already exists with `tekton-branch-status`
- Verify network connectivity for remote operations

### Branch verification fails

- Check if you're on the correct branch with `git branch --show-current`
- Verify the expected branch name matches the naming convention
- Check if the branch exists in all component repositories

### Commit creation fails

- Ensure you have staged changes with `git add`
- Verify you have provided a commit title
- Check if you have the necessary permissions

## References

- [Pro Git Book](https://git-scm.com/book/en/v2)
- [GitHub Documentation](https://docs.github.com/en)
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- [Tekton Development Sprint Process](/MetaData/DevelopmentSprints/README.md)
- [Tekton Branch Management Guide](/MetaData/DevelopmentSprints/Templates/BranchManagement.md)