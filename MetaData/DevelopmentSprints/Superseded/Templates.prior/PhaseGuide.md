# Tekton Development Sprint Phase Guide

This document provides detailed guidance for each phase of a Tekton Development Sprint, including objectives, activities, deliverables, and transition criteria. It serves as a reference for all participants to understand the expectations and outcomes of each sprint phase.

## Overview of Sprint Phases

A Tekton Development Sprint typically progresses through the following phases:

1. **Inception**: Initial idea discussion and feasibility assessment
2. **Planning and Architecture**: Detailed planning and architectural design
3. **Implementation**: Coding, testing, and documentation (may involve multiple phases)
4. **Continuation and Handoff**: Transitioning between implementation phases (if needed)
5. **Completion and Retrospective**: Finalizing deliverables and reflecting on the sprint
6. **Merge and Integration**: Integrating changes into the main codebase

Each phase has specific objectives, required activities, and deliverables that must be completed before moving to the next phase.

## 1. Inception Phase

### Objectives
- Identify a potential improvement or feature for Tekton
- Evaluate technical feasibility and value
- Decide whether to proceed with detailed planning

### Participants
- Casey (human-in-the-loop)
- Architect Claude

### Activities
- Casey discusses a potential sprint idea with Architect Claude
- Architect Claude provides initial feedback on technical feasibility
- They discuss potential approaches and value
- Casey decides whether to proceed with planning

### Deliverables
- Initial discussion record/notes
- Decision to proceed or table the idea

### Transition Criteria
- Casey's approval to proceed with Planning and Architecture phase
- Clear understanding of the general scope and objectives

## 2. Planning and Architecture Phase

### Objectives
- Create a detailed plan for the sprint
- Make and document key architectural decisions
- Establish clear implementation phases and tasks

### Participants
- Architect Claude (primary)
- Casey (review and approval)

### Activities
- Architect Claude researches the requirements and current state
- Architect Claude analyzes the codebase to understand current implementation
- Architect Claude identifies optimal architectural approaches
- Architect Claude documents key architectural decisions
- Architect Claude creates a high-level plan document
- Architect Claude produces a detailed implementation plan
- Casey reviews and provides feedback
- Architect Claude creates the initial prompt for the Working Claude session

### Deliverables
- **SprintPlan.md**: High-level overview of the sprint goals, approach, and timeline
- **ArchitecturalDecisions.md**: Documentation of key architectural decisions
- **ImplementationPlan.md**: Detailed plan with specific tasks and phases
- **ClaudeCodePrompt.md**: Initial prompt for the Working Claude session

### Transition Criteria
- All planning documents completed
- Casey's approval of the implementation plan
- Initial prompt for Working Claude prepared
- Branch created for implementation

## 3. Implementation Phase

### Objectives
- Implement code changes according to the implementation plan
- Create or update tests
- Update documentation
- Produce a status report

### Participants
- Working Claude (primary)
- Casey (review and feedback)
- Architect Claude (technical guidance when needed)

### Activities
- Working Claude reviews all sprint documentation
- Working Claude verifies working on the correct GitHub branch
- Working Claude asks any questions before beginning implementation
- Working Claude implements code according to the plan
- Working Claude creates or updates tests
- Working Claude updates documentation
- Working Claude produces a status report

### Deliverables
- Code changes on the branch
- New or updated tests
- Updated documentation
- **StatusReport.md**: Report on completed work, challenges, and next steps

### Transition Criteria
- Implementation tasks for the phase completed
- Tests passing
- Documentation updated
- Status report completed and reviewed by Casey
- Casey's approval to proceed to next phase or completion

## 4. Continuation and Handoff Phase

### Objectives
- Ensure smooth transition between implementation phases
- Provide clear instructions for the next Working Claude session
- Document progress, challenges, and next steps

### Participants
- Current Working Claude
- Casey (review and approval)
- Next Working Claude (recipient of handoff)

### Activities
- Current Working Claude prepares detailed instructions for the next phase
- Current Working Claude documents the current state of the implementation
- Current Working Claude identifies remaining work and potential challenges
- Casey reviews the status and handoff documentation
- Next Working Claude reviews documentation and asks clarifying questions

### Deliverables
- **NextPhaseInstructions.md**: Detailed instructions for the next phase
- Updated status report with current progress
- Documentation of any challenges or open questions

### Transition Criteria
- Handoff documentation completed
- Casey's approval to move to the next phase
- Next Working Claude has clear understanding of the work to be done

## 5. Completion and Retrospective Phase

### Objectives
- Finalize all code changes
- Ensure all tests pass
- Complete all documentation updates
- Reflect on the sprint process and identify improvements

### Participants
- Working Claude (primary)
- Casey (review and approval)
- Architect Claude (if needed for technical questions)

### Activities
- Working Claude finalizes all code changes
- Working Claude ensures all tests pass
- Working Claude completes all documentation updates
- Working Claude prepares a final status report
- Working Claude creates a retrospective document
- Working Claude identifies opportunities for shared code and further enhancements
- Casey reviews the final deliverables

### Deliverables
- Completed code changes
- Passing tests
- Complete documentation updates
- **FinalStatusReport.md**: Final report on all completed work
- **Retrospective.md**: Analysis of the sprint with lessons learned and improvement suggestions

### Transition Criteria
- All planned code changes implemented
- All tests passing
- All documentation updated
- Final status report and retrospective completed
- Casey's approval of the final deliverables

## 6. Merge and Integration Phase

### Objectives
- Integrate the sprint changes into the main codebase
- Ensure the changes work correctly in the integrated environment
- Update release documentation if needed

### Participants
- Casey (primary)
- Architect Claude (if needed for technical guidance)

### Activities
- Casey reviews the final changes once more
- Casey creates a pull request or directly merges the changes
- Casey verifies the changes work correctly in the integrated environment
- Casey updates release documentation if needed

### Deliverables
- Merged changes in main branch
- Updated release documentation (if applicable)

### Transition Criteria
- Changes successfully merged
- No integration issues
- Sprint officially completed

## Documentation Requirements by Phase

Each phase requires specific documentation to be created or updated:

### Inception
- Initial discussion notes (informal)

### Planning and Architecture
- **SprintPlan.md** (MUST create)
- **ArchitecturalDecisions.md** (MUST create)
- **ImplementationPlan.md** (MUST create)
- **ClaudeCodePrompt.md** (MUST create)

### Implementation
- Code with appropriate comments (MUST update)
- Tests (MUST update)
- Component-specific documentation (MUST update)
- API references for changed APIs (MUST update)
- **StatusReport.md** (MUST create)
- Development guides (CAN update)
- Examples and tutorials (CAN update)

### Continuation and Handoff
- **NextPhaseInstructions.md** (MUST create)
- Updated status report (MUST update)

### Completion and Retrospective
- Final code clean-up (MUST update)
- User guides for new features (MUST update)
- **FinalStatusReport.md** (MUST create)
- **Retrospective.md** (MUST create)

### Merge and Integration
- Release notes (MUST update if applicable)
- Project roadmap (CAN update with approval)

## Phase Transition Checklist

When transitioning between phases, use this checklist:

- All required deliverables for the current phase are complete
- Required documentation has been created or updated
- All specified tests are passing
- Casey has reviewed and approved the transition
- Any open questions or issues have been addressed or documented
- The next phase has clear objectives and tasks defined
- If handoff is involved, detailed handoff documentation is prepared

## Dealing with Blockers

If a blocker is encountered during any phase:

1. Document the issue clearly
2. Identify potential solutions or workarounds
3. Consult with Architect Claude if it's an architectural issue
4. Escalate to Casey for decision-making if needed
5. Update the implementation plan if significant changes are required
6. Document the resolution for future reference

## Communication Guidelines

Effective communication is essential for successful phase transitions:

- Be explicit about the current state of the implementation
- Clearly document any deviations from the implementation plan
- Highlight areas that need attention in the next phase
- Document assumptions and design decisions
- Provide context for code changes
- Link documentation updates to code changes
- Create comprehensive handoff documentation for multi-phase sprints