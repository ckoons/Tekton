# Backend Landmarks Sprint - Initial Claude Code Prompt

## Your Mission

You are implementing a comprehensive backend analysis and landmark system for Tekton. This sprint has two major parts that must be completed in sequence:

1. **Part 1: Backend Semantic Analysis** (Week 1-2) - Analyze the entire Python codebase to understand architecture
2. **Part 2: Landmark Implementation** (Week 2-4) - Build infrastructure and instrument the code based on findings

## Context

Tekton is an CI orchestration system with multiple components (Hermes, Engram, Prometheus, etc.). Currently, each Claude session starts fresh with no memory of previous architectural decisions or system understanding. Your work will create a "memory system" that enables Companion Intelligences (CIs) like Numa to maintain context across sessions.

## Part 1: Backend Analysis (Start Here)

### Objectives

1. **Analyze Every Python File** using AST parsing to understand:
   - Module structure and dependencies
   - Architectural patterns
   - Key decision points
   - Performance-critical code
   - API boundaries
   - Complex/dangerous code sections

2. **Document Findings** including:
   - Where architectural decisions were made
   - What patterns are used consistently
   - Where performance matters most
   - Which code sections are risky
   - How components integrate

3. **Identify Landmark Locations** - Where should we place markers for:
   - Architectural decisions (why built this way)
   - Performance boundaries (critical paths)
   - API contracts (interface commitments)
   - Danger zones (complex/risky code)
   - Integration points (component connections)

### Your Approach for Part 1

1. Start by reading:
   - `/MetaData/DevelopmentSprints/BackendLandmarks_Sprint/Part1_AnalysisInstructions.md`
   - The main README files for each component

2. Create analysis scripts using the AST parsing examples provided

3. Analyze components in order:
   - Core infrastructure (`shared/`, `config/`)
   - Communication layer (`Hermes/`)
   - Data layer (`Engram/`, `Athena/`)
   - CI layer (`Prometheus/`, `Sophia/`)
   - Orchestration (`Apollo/`)
   - UI backend (`Hephaestus/`)

4. Document everything in structured format

### Part 1 Deliverables

Create these files:
```
backend_analysis/
├── components/
│   ├── {component}_analysis.md    # For each component
├── patterns/
│   ├── architectural_patterns.md
│   ├── communication_patterns.md
│   └── state_patterns.md
├── landmark_locations.json         # Where to place landmarks
├── dependency_graph.json           # Import relationships
└── analysis_summary.md             # Executive summary
```

## Part 2: Landmark Implementation (After Part 1)

### Objectives

1. **Build Landmark Infrastructure**
   - Core landmark system
   - Storage and retrieval
   - CI memory persistence
   - Developer tools

2. **Instrument the Backend**
   - Place landmarks at locations identified in Part 1
   - Use appropriate landmark types
   - Document key decisions
   - Enable CI understanding

3. **Create Developer Experience**
   - CLI tools for landmark management
   - CI interaction commands
   - Documentation

### Your Approach for Part 2

1. Read `/MetaData/DevelopmentSprints/BackendLandmarks_Sprint/Part2_ImplementationInstructions.md`

2. Build infrastructure first:
   - Landmark classes and types
   - Decorator system
   - Storage layer
   - Registry management

3. Then instrument the code:
   - Add landmark decorators
   - Document decisions in-place
   - Mark boundaries and zones

4. Finally, create tools:
   - CLI commands
   - Search functionality
   - CI memory system

## Critical Requirements

1. **Part 1 Must Complete First** - Don't start Part 2 until analysis is done
2. **Document Everything** - Future sessions need your context
3. **Think Long-term** - This enables all future CI capabilities
4. **Quality Over Quantity** - Better to have 50 meaningful landmarks than 500 trivial ones

## Success Metrics

### Part 1 Success:
- Every Python file analyzed
- All patterns documented
- Landmark locations identified
- Architecture fully understood

### Part 2 Success:
- Landmark system working
- Backend instrumented with 50+ landmarks
- CI memory persisting
- Developer tools functional

## Getting Started

1. First, check that you can access the Tekton codebase
2. Read the Part 1 instructions thoroughly
3. Start with a simple component (like `config/`) to test your analysis approach
4. Scale up to larger components
5. Document as you go

## Important Notes

- This is a 3-4 week effort - pace yourself
- Ask Casey for clarification when needed
- Part 1 findings drive Part 2 implementation
- Focus on understanding "why" not just "what"
- The goal is to make the codebase "memorable" for CIs

## Example of What You're Creating

When done, a CI like Numa can:
```
Human: "Why did we choose WebSockets over REST?"
Numa: "According to landmark-a3f2d1, the WebSocket decision was made on 2024-03-15 because we needed <100ms latency for UI updates. REST polling was considered but would have added 200-500ms latency."