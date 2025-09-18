#!/usr/bin/env python3
"""
Example demonstrating the enhanced sundown/sunrise flow with:
- Memory requests for targeted retrieval
- Question encouragement
- Feedback-based tuning
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.ci_tools.sundown_enhanced import (
    EnhancedCISundown,
    QuestionEncourager,
    FeedbackCollector,
    prepare_enhanced_sundown
)


def simulate_turn_1():
    """Turn 1: CI starts eagerly without questions."""
    print("\n" + "="*70)
    print("TURN 1: CI STARTS EAGERLY (NO QUESTIONS)")
    print("="*70)

    ci_output = """
I'll implement the Apollo digest system right away. Let me start coding...

[Starts implementing without understanding requirements]
"""
    print(ci_output)

    # Question encourager notices lack of questions
    encourager = QuestionEncourager("Amy")
    questions = encourager.check_output_for_questions(ci_output)
    encouragement = encourager.generate_encouragement(len(questions) > 0, 1)

    if encouragement:
        print("\n[System Encouragement]:")
        print(encouragement)

    return ci_output


def simulate_turn_2():
    """Turn 2: CI learns to ask questions."""
    print("\n" + "="*70)
    print("TURN 2: CI ASKS QUESTIONS")
    print("="*70)

    ci_output = """
Actually, let me pause and ask some questions first:

1. What memory types does Engram currently store?
2. How should relevance be calculated - any existing patterns?
3. What's the maximum memory volume we typically handle?
4. Are there examples of prioritization algorithms in the codebase?

These answers would help me design a better solution.
"""
    print(ci_output)

    # Prepare sundown with memory requests
    sundown = prepare_enhanced_sundown(
        todo_list=[
            {"task": "Analyzed Apollo digest requirements", "status": "completed"},
            {"task": "Identified key questions", "status": "completed"},
            {"task": "Design relevance algorithm", "status": "pending"},
            {"task": "Implement digest generation", "status": "pending"}
        ],
        context_notes="""Paused to gather context before implementation.
Need to understand existing patterns and constraints.
Will design algorithm after getting answers.""",
        memory_requests=[
            "Show examples of: existing prioritization or scoring code",
            "Need context about: Engram memory types and volumes",
            "Search for: relevance, scoring, or ranking implementations",
            "Find discussions about: memory management decisions"
        ],
        open_questions=[
            "Should relevance decay over time?",
            "How to handle conflicting relevance signals?",
            "What's the performance budget for scoring?"
        ],
        feedback={
            'apollo_digest': 'too little',  # Wants more context
            'rhetor_prompt': 'just right',
            'overall_context': 'need more'
        },
        ci_name="Amy"
    )

    full_output = ci_output + "\n" + sundown
    print("\n[Sundown with Memory Requests]:")
    print(sundown)

    return full_output


def simulate_apollo_response():
    """Apollo provides targeted memories based on requests."""
    print("\n" + "="*70)
    print("APOLLO TARGETED RESPONSE (BASED ON MEMORY REQUESTS)")
    print("="*70)

    # Apollo uses memory requests to prioritize
    digest = """# APOLLO MEMORY DIGEST
## Requested Information (85% relevance weight)

### Existing Prioritization Examples
- /Apollo/apollo/core/attention.py:45 - frequency-based scoring
- /Sophia/sophia/ranking.py:120 - semantic similarity ranking
- Pattern: Most use weighted combination of signals

### Engram Memory Types
- Landmarks: Code waypoints (~10K entries)
- Sessions: CI conversations (~100MB/day)
- Decisions: Architectural choices (~500 entries)
- Patterns: Recurring solutions (~200 entries)

### Relevance Discussions
- "Use 85% relevance, 15% recency" - Casey, 2024-09-17
- "Catastrophe theory for sudden importance shifts" - Design doc
- "Explicit requests should override algorithmic ranking" - Amy feedback

### Performance Constraints
- Scoring must complete in <100ms for 10K items
- Cache scores for 5 minutes
- Use inverted index for keyword matching

## Recent Context (15% recency weight)
- Just started Apollo implementation
- Memory overflow issue being addressed
- Sundown/sunrise protocol active

[Size: 45KB of 57KB budget (adjusted from feedback)]"""

    print(digest)
    return digest


def simulate_turn_3():
    """Turn 3: CI works effectively with targeted information."""
    print("\n" + "="*70)
    print("TURN 3: INFORMED IMPLEMENTATION")
    print("="*70)

    ci_output = """
Perfect! With this context, I can design an effective relevance algorithm:

Based on the examples and Casey's guidance, I'll implement:
1. 85% relevance score from task/keyword matching
2. 15% recency with exponential decay
3. Override for explicit memory requests
4. Catastrophe detection for sudden importance

The implementation will follow the pattern in attention.py but with
the weighting Casey specified. I'll ensure <100ms performance using
the inverted index approach from sophia/ranking.py.

Let me implement this now with confidence!

[Implements with understanding of requirements and patterns]
"""
    print(ci_output)

    # Positive feedback - system worked well
    sundown = prepare_enhanced_sundown(
        todo_list=[
            {"task": "Designed relevance algorithm", "status": "completed"},
            {"task": "Implemented scoring with 85/15 split", "status": "completed"},
            {"task": "Added memory request override", "status": "completed"},
            {"task": "Test performance (<100ms)", "status": "pending"},
            {"task": "Integrate with Rhetor", "status": "pending"}
        ],
        context_notes="""Successfully implemented relevance algorithm.
Used existing patterns and Casey's specifications.
Ready for performance testing and integration.""",
        memory_requests=[
            "Need: performance testing utilities",
            "Need: Rhetor integration points",
            "Show: any existing Apollo-Rhetor connections"
        ],
        feedback={
            'apollo_digest': 'just right',  # Perfect amount
            'rhetor_prompt': 'just right',
            'overall_context': 'adequate'
        },
        ci_name="Amy"
    )

    print("\n[Feedback: Information was just right!]")
    print("✓ Questions led to targeted, useful information")
    print("✓ Implementation proceeded with confidence")
    print("✓ System learns from positive feedback")

    return ci_output + "\n" + sundown


def show_tuning_evolution():
    """Show how the system tunes itself based on feedback."""
    print("\n" + "="*70)
    print("SYSTEM TUNING BASED ON FEEDBACK")
    print("="*70)

    collector = FeedbackCollector()

    # Simulate feedback over multiple turns
    feedback_sequence = [
        {'apollo_digest': 'too little', 'rhetor_prompt': 'just right'},
        {'apollo_digest': 'too little', 'rhetor_prompt': 'just right'},
        {'apollo_digest': 'just right', 'rhetor_prompt': 'just right'},
        {'apollo_digest': 'just right', 'rhetor_prompt': 'too much'},
        {'apollo_digest': 'just right', 'rhetor_prompt': 'just right'},
    ]

    print("Feedback over 5 turns:")
    for i, feedback in enumerate(feedback_sequence, 1):
        collector.process_feedback(feedback)
        targets = collector.get_size_targets()
        print(f"\nTurn {i}: {feedback}")
        print(f"  → Apollo target: {targets['apollo_digest_kb']}KB")
        print(f"  → Rhetor target: {targets['rhetor_prompt_kb']}KB")
        print(f"  → Relevance threshold: {targets['relevance_threshold']:.2f}")

    print("\n" + collector.generate_tuning_report())


def main():
    """Run the complete enhanced flow demonstration."""
    print("\n" + "="*80)
    print(" ENHANCED SUNDOWN/SUNRISE WITH QUESTIONS & FEEDBACK")
    print("="*80)

    # Turn 1: Eager start without questions
    turn1 = simulate_turn_1()

    # Turn 2: CI learns to ask questions
    turn2 = simulate_turn_2()

    # Apollo provides targeted response
    apollo_digest = simulate_apollo_response()

    # Turn 3: Effective work with good context
    turn3 = simulate_turn_3()

    # Show system tuning
    show_tuning_evolution()

    print("\n" + "="*80)
    print("KEY BENEFITS DEMONSTRATED:")
    print("="*80)
    print("""
1. QUESTIONS IMPROVE OUTCOMES
   - Turn 1: No questions → working blind
   - Turn 2: Good questions → targeted information
   - Turn 3: Informed work → better results

2. MEMORY REQUESTS DRIVE RELEVANCE
   - CI explicitly states what's needed
   - Apollo prioritizes requested information
   - Less noise, more signal

3. FEEDBACK TUNES THE SYSTEM
   - "Too little" → increases budget
   - "Too much" → reduces budget, raises threshold
   - System adapts to CI preferences

4. VALIDATION HELPS CIS LEARN
   - First failure: Template provided
   - Second failure: Request for feedback
   - CIs understand requirements better

5. ENCOURAGEMENT CHANGES BEHAVIOR
   - Gentle nudges toward asking questions
   - Positive reinforcement when questions asked
   - CIs become less eager, more thoughtful
""")


if __name__ == "__main__":
    main()