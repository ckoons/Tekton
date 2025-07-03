# aish Help System Development Sprint

## Overview

This sprint implements a minimal help system for the aish command that provides documentation paths for both AI Training and User Guides.

## Sprint Status

**Status:** Planning Phase  
**Created:** 2025-01-03  
**Scope:** Minimal - single file change to aish command

## Key Design Decision

Help commands return paths to documentation rather than help content:

```
$ aish help
Usage: aish [options] [ai] [message]
AI Training: /Users/.../MetaData/TektonDocumentation/AITraining/aish/
User Guides: /Users/.../MetaData/TektonDocumentation/UserGuides/aish/

$ aish terma help
Usage: aish terma [command] [args]
AI Training: /Users/.../MetaData/TektonDocumentation/AITraining/Terma/
User Guides: /Users/.../MetaData/TektonDocumentation/UserGuides/Terma/
```

## Implementation

All changes are contained within `/Users/cskoons/projects/github/Tekton/shared/aish/aish`.

## Documentation

- [Sprint Plan](./SprintPlan.md) - Detailed planning document
- [Architectural Decisions](./ArchitecturalDecisions.md) - Key design decisions and rationale

## Why This Matters

This tiny sprint establishes a pattern that will serve Tekton for years:
- Equal treatment for humans and Companion Intelligences
- Documentation can evolve without code changes
- Simple, discoverable, and scalable