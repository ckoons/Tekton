#!/usr/bin/env python3
"""
Example: Turn-Based CI with New Memory Architecture

Shows how a CI operates with the new turn-based memory system.
No persistent memory, just context provided at turn start.
"""

from typing import Dict, Any, List, Optional
from shared.turn.context_manager import start_ci_turn, end_ci_turn
from shared.knowledge.graph_markers import (
    knowledge_node,
    memory_point,
    insight_trigger,
    context_aware
)


@knowledge_node(node_type="example_ci", tags=["demo", "turn-based"], importance=0.5)
class TurnBasedCI:
    """
    Example CI using turn-based memory architecture.
    
    Key points:
    - No internal memory storage
    - Receives context at turn start
    - Returns memories to store at turn end
    - Completely stateless between turns
    """
    
    def __init__(self, name: str = "example_ci"):
        self.name = name
        self.ci_type = "specialist"
        # NO memory system, NO storage, just the CI's core logic
    
    @context_aware(context_type="turn", requires=["prompt", "digest"])
    def execute_turn(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single turn.
        
        Args:
            task: Task specification
            
        Returns:
            Results and memories to store
        """
        # Start turn - receive context (prompt + digest)
        context = start_ci_turn(
            ci_name=self.name,
            task=task,
            ci_type=self.ci_type
        )
        
        print(f"\n=== Starting turn for {self.name} ===")
        print(f"Context size: {len(context)/1024:.1f}KB")
        print("\nReceived context:")
        print("-" * 40)
        print(context[:500] + "..." if len(context) > 500 else context)
        print("-" * 40)
        
        # Process the task with the provided context
        result = self._process_task(task, context)
        
        # Decide what to remember from this turn
        memories = self._select_memories(task, result)
        
        # End turn - store selected memories
        end_ci_turn(self.name, memories)
        
        print(f"\n=== Turn complete for {self.name} ===")
        print(f"Storing {len(memories)} memories")
        
        return result
    
    @memory_point(memory_type="task_execution", retention="normal")
    def _process_task(self, task: Dict[str, Any], context: str) -> Dict[str, Any]:
        """
        Process the task using provided context.
        
        This is where the CI's actual work happens.
        The context contains all needed memory/history.
        """
        result = {
            'status': 'completed',
            'task_type': task.get('type', 'unknown'),
            'objective': task.get('objective', 'none')
        }
        
        # Example: Use context to make decisions
        if "Previous:" in context:
            print("  → Found previous turn information in context")
            result['continued'] = True
        
        if "Domain Knowledge:" in context:
            print("  → Found domain knowledge in context")
            result['informed'] = True
        
        # Simulate task processing
        if task.get('type') == 'analysis':
            result['analysis'] = self._perform_analysis(task, context)
        elif task.get('type') == 'conversation':
            result['response'] = self._generate_response(task, context)
        else:
            result['output'] = f"Processed {task.get('objective', 'task')}"
        
        return result
    
    def _perform_analysis(self, task: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Perform analysis task."""
        return {
            'findings': ['Finding 1', 'Finding 2'],
            'confidence': 0.8,
            'based_on_context': "Context" in context
        }
    
    def _generate_response(self, task: Dict[str, Any], context: str) -> str:
        """Generate conversational response."""
        return f"Based on the context, I understand that {task.get('objective', 'you need help')}."
    
    @insight_trigger(trigger_type="task_completion", confidence_threshold=0.7)
    def _select_memories(self, task: Dict[str, Any], result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select what to remember from this turn.
        
        The CI decides what's worth remembering.
        These memories will be stored in Engram for future turns.
        """
        memories = []
        
        # Remember the task completion
        memories.append({
            'type': 'task_completion',
            'action': f"Completed {task.get('type', 'task')}",
            'result': result.get('status', 'unknown'),
            'objective': task.get('objective', ''),
            'timestamp': self._get_timestamp()
        })
        
        # Remember any insights
        if result.get('analysis'):
            analysis = result['analysis']
            if analysis.get('findings'):
                memories.append({
                    'type': 'insight',
                    'content': f"Found {len(analysis['findings'])} patterns",
                    'confidence': analysis.get('confidence', 0),
                    'tags': ['analysis', 'findings']
                })
        
        # Remember key decisions
        if result.get('continued'):
            memories.append({
                'type': 'continuation',
                'content': 'Continued from previous turn',
                'key_point': True
            })
        
        return memories
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


def demo_turn_based_system():
    """Demonstrate the turn-based system."""
    print("=" * 60)
    print("TURN-BASED CI DEMONSTRATION")
    print("=" * 60)
    
    # Create a CI
    ci = TurnBasedCI("demo_ci")
    
    # Turn 1: Initial task
    print("\n--- TURN 1 ---")
    task1 = {
        'type': 'analysis',
        'objective': 'Analyze system performance',
        'context': 'First analysis of the day'
    }
    result1 = ci.execute_turn(task1)
    print(f"Result: {result1}")
    
    # Turn 2: Follow-up task (will have context from Turn 1)
    print("\n--- TURN 2 ---")
    task2 = {
        'type': 'conversation',
        'objective': 'Explain the analysis results',
        'context': 'User wants clarification'
    }
    result2 = ci.execute_turn(task2)
    print(f"Result: {result2}")
    
    # Show the architecture benefits
    print("\n" + "=" * 60)
    print("ARCHITECTURE BENEFITS:")
    print("=" * 60)
    print("✓ No memory overhead in CI")
    print("✓ Context provided at turn start (~128KB max)")
    print("✓ CI decides what to remember")
    print("✓ Completely stateless between turns")
    print("✓ Fresh context each turn")
    print("✓ No memory accumulation")
    print("=" * 60)


if __name__ == "__main__":
    demo_turn_based_system()