# Single Environment Read Sprint

## Overview

This sprint addresses a fundamental architectural flaw in Tekton: environment configuration is read from multiple places at unpredictable times, creating inconsistent state and preventing proper multi-environment support (Coder-A/B/C, remote instances).

The core principle: **Environment must be read ONCE at program start, then frozen**.

## The Problem

Currently, Tekton has ~714 calls to `os.environ` scattered throughout the codebase. Configuration is read:
- At module import time (unpredictable)
- In class constructors (too early)
- In singleton initialization (frozen forever)
- Throughout execution (inconsistent)

This creates a "birdhouse without a hole" - we cannot control when or how the environment is read.

## The Solution: TektonEnviron

A single environment manager that:
1. Loads configuration once at startup
2. Provides typed access methods
3. Can be frozen to os.environ for backward compatibility
4. Supports multiple environments (Coder-A/B/C, remote)

## Sprint Goals

1. Implement TektonEnviron as the single source of truth
2. Update all entry points to load environment properly
3. Remove/replace scattered os.environ calls
4. Eliminate singleton caching of configuration
5. Enable reliable multi-environment support

## Success Criteria

- `tekton --coder a status` shows Coder-A's ports (7000 range)
- `tekton --coder b status` shows Coder-B's ports (6000 range)
- No module-level environment reads
- All configuration flows through TektonEnviron
- Remote Tekton instances can be supported

## Key Documents

- [SprintPlan.md](SprintPlan.md) - Detailed sprint planning
- [ArchitecturalDecisions.md](ArchitecturalDecisions.md) - Key design choices
- [ImplementationPlan.md](ImplementationPlan.md) - Four-phase implementation plan
- [ClaudeCodePrompt.md](ClaudeCodePrompt.md) - Initial prompt for implementation

## Current Status

Phase 1 (TektonEnviron implementation) is complete. The remaining phases will systematically eliminate the scattered environment reads and singleton patterns that prevent proper environment control.