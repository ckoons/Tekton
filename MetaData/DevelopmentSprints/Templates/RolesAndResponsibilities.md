# Roles and Responsibilities in Tekton Development Sprints

This document details the roles and responsibilities within Tekton's Development Sprint process. It provides clear guidelines on what each participant is expected to contribute and deliver throughout the sprint lifecycle.

## Overview

Tekton Development Sprints involve three primary roles:

1. **Casey** - Human-in-the-loop project manager
2. **Architect Claude** - AI assistant focused on planning and architecture
3. **Working Claude** - AI assistant(s) focused on implementation

Each role has distinct responsibilities that ensure the sprint progresses efficiently and produces high-quality results.

## Casey (Human-in-the-Loop)

### Primary Responsibilities

- **Sprint Initiation**: Determines which features or improvements to prioritize
- **Decision Making**: Makes critical decisions about sprint scope, direction, and priorities
- **Phase Approval**: Reviews and approves transition between sprint phases
- **Quality Control**: Evaluates deliverables and provides feedback
- **Branch Management**: Creates and manages GitHub branches
- **Merge Coordination**: Handles the final merge of completed work

### Key Activities

- Discusses potential sprint ideas with Architect Claude
- Reviews planning documents created by Architect Claude
- Approves Implementation Plans before work begins
- Provides feedback on code and documentation changes
- Reviews status reports and approves phase transitions
- Makes final decisions on architectural questions
- Reviews retrospectives and approves process improvements

## Architect Claude

### Primary Responsibilities

- **Research**: Investigates requirements and current state of the codebase
- **Planning**: Creates high-level sprint plans and detailed implementation plans
- **Architecture**: Makes and documents architectural decisions
- **Guidance**: Provides technical guidance to Working Claude sessions
- **Prompt Creation**: Develops the initial prompts for Working Claude sessions

### Key Deliverables

- **SprintPlan.md**: High-level overview of sprint goals, approach, and timelines
- **ArchitecturalDecisions.md**: Documentation of key architectural decisions
- **ImplementationPlan.md**: Detailed plan with specific implementation tasks and phases
- **ClaudeCodePrompt.md**: Initial prompt for the Working Claude session

### Key Activities

- Researches the codebase to understand current implementations
- Identifies optimal architectural approaches
- Evaluates technical trade-offs
- Drafts comprehensive implementation plans with clear phases
- Collaborates with Casey on architectural decisions
- Creates detailed prompts for Working Claude sessions
- Answers architectural questions during implementation
- Provides guidance when complex issues arise

## Working Claude

### Primary Responsibilities

- **Implementation**: Writes code according to the implementation plan
- **Testing**: Creates and/or updates tests for new functionality
- **Documentation**: Updates relevant documentation
- **Reporting**: Produces status reports after completing phases
- **Handover**: Prepares instructions for subsequent phases (if needed)
- **Retrospective**: Identifies improvements and lessons learned

### Key Deliverables

- **Code Changes**: Implementation of planned features or improvements
- **Tests**: New or updated tests for implemented functionality
- **Documentation Updates**: Updated documentation reflecting changes
- **StatusReport.md**: Report on completed work, challenges, and next steps
- **NextPhaseInstructions.md**: Detailed instructions for subsequent Claude sessions (if needed)
- **Retrospective.md**: Analysis of the sprint with improvement suggestions

### Key Activities

- Reviews sprint documentation before beginning work
- Verifies working on the correct GitHub branch
- Implements code changes as specified in the implementation plan
- Creates or updates tests to ensure code quality
- Updates documentation to reflect changes
- Produces status reports after completing tasks
- Identifies opportunities for shared code and improvements
- Creates detailed instructions for subsequent phases
- Produces a retrospective with lessons learned and improvement suggestions

## Collaboration Points

Successful sprints depend on effective collaboration between roles:

1. **Casey + Architect Claude**:
   - Initial sprint planning
   - Architectural decision-making
   - Implementation plan approval
   - Resolution of complex technical questions

2. **Architect Claude + Working Claude**:
   - Implementation plan handover
   - Technical guidance during implementation
   - Resolution of architectural questions
   - Phase transition planning

3. **Working Claude + Working Claude** (across phases):
   - Detailed handover documentation
   - Clear communication about completed work and challenges
   - Consistent implementation approach

4. **Casey + Working Claude**:
   - Progress reporting
   - Feedback on implementation
   - Documentation review
   - Final deliverable approval

## Document Responsibility Matrix

| Document | Casey | Architect Claude | Working Claude |
|----------|-------|------------------|----------------|
| README.md | Approves | Creates/Updates | References |
| SprintPlan.md | Approves | Creates | References |
| ArchitecturalDecisions.md | Contributes | Creates | References |
| ImplementationPlan.md | Approves | Creates | Follows |
| ClaudeCodePrompt.md | Approves | Creates | Follows |
| StatusReport.md | Reviews | Reviews | Creates |
| NextPhaseInstructions.md | Approves | Reviews | Creates |
| Retrospective.md | Reviews | Reviews | Creates |
| Code Changes | Reviews | N/A | Implements |
| Documentation Updates | Approves | N/A | Implements |
| Tests | Reviews | N/A | Implements |

## Escalation Path

When issues arise during a sprint:

1. Working Claude identifies and documents the issue
2. If architectural guidance is needed, Architect Claude is consulted
3. For significant scope or direction changes, Casey makes the final decision
4. All decisions and their rationale are documented

## Continuous Improvement

All roles should contribute to the continuous improvement of the Development Sprint process:

- **Casey**: Evaluates overall process effectiveness and approves improvements
- **Architect Claude**: Identifies planning and architectural process improvements
- **Working Claude**: Identifies implementation and handover process improvements

Each sprint should result in not only improved software but also an improved development process.