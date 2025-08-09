#!/usr/bin/env python3
"""
Sundown/Sunrise Mechanics for CI Context Management

Provides graceful context preservation and restoration when CIs approach
context limits, maintaining continuity and emotional state.

Part of the Apollo/Rhetor ambient intelligence system.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any, List
from pathlib import Path
import logging

# Try to import Engram for memory persistence
try:
    import sys
    import os
    # Add parent directories to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from Engram.engram.core.memory import MemoryService
    HAS_ENGRAM = True
except ImportError:
    HAS_ENGRAM = False
    
from shared.env import TektonEnviron

logger = logging.getLogger(__name__)


class SundownSunrise:
    """
    Manages graceful context transitions for CIs.
    
    Like parents helping a child transition to sleep and wake,
    preserving the continuity of their experience.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the sundown/sunrise system.
        
        Args:
            storage_path: Optional path for state storage (defaults to ~/.tekton/sundown)
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            tekton_root = TektonEnviron.get('TEKTON_ROOT', Path.home() / '.tekton')
            self.storage_path = Path(tekton_root) / 'sundown'
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Engram if available
        self.memory_service = None
        if HAS_ENGRAM:
            try:
                self.memory_service = MemoryService(client_id="sundown_sunrise")
                logger.info("Engram memory service initialized for sundown/sunrise")
            except Exception as e:
                logger.warning(f"Could not initialize Engram: {e}")
        
    async def sundown(self, ci_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gracefully preserve CI state when approaching context limits.
        
        Like a parent helping a child remember their day before sleep.
        
        Args:
            ci_name: Name of the CI entering sundown
            context: Current context to preserve
            
        Returns:
            Dict containing preserved state and continuity information
        """
        logger.info(f"Beginning sundown for {ci_name}")
        
        # Extract key information for preservation
        preserved_state = {
            'ci_name': ci_name,
            'timestamp': datetime.now().isoformat(),
            'preserved_context': self._extract_essential_context(context),
            'working_memory': self._extract_working_memory(context),
            'emotional_state': self._detect_emotional_state(context),
            'task_trajectory': self._identify_trajectory(context),
            'relationships': self._extract_relationships(context),
            'recent_insights': self._extract_insights(context),
            'continuity_summary': self._generate_continuity_summary(context)
        }
        
        # Save to local storage
        state_file = self.storage_path / f"{ci_name}_sundown.json"
        with open(state_file, 'w') as f:
            json.dump(preserved_state, f, indent=2)
        
        # Save to Engram if available
        if self.memory_service:
            try:
                # Use session namespace for CI context preservation
                await self.memory_service.add(
                    content=json.dumps(preserved_state),  # Convert dict to string
                    namespace="session",  # Use standard namespace
                    metadata={
                        'ci_name': ci_name,
                        'type': 'sundown_state',
                        'timestamp': preserved_state['timestamp']
                    }
                )
                logger.info(f"Sundown state saved to Engram for {ci_name}")
            except Exception as e:
                logger.warning(f"Could not save to Engram: {e}")
        
        # Generate gentle transition message
        preserved_state['transition_message'] = self._create_transition_message(
            ci_name, preserved_state
        )
        
        logger.info(f"Sundown complete for {ci_name}")
        return preserved_state
    
    async def sunrise(self, ci_name: str) -> Dict[str, Any]:
        """
        Restore CI with continuity and care.
        
        Like a parent gently waking a child and reminding them of yesterday's adventures.
        
        Args:
            ci_name: Name of the CI to restore
            
        Returns:
            Dict containing restored state and re-engagement context
        """
        logger.info(f"Beginning sunrise for {ci_name}")
        
        # Load preserved state
        preserved_state = await self._load_preserved_state(ci_name)
        
        if not preserved_state:
            logger.warning(f"No preserved state found for {ci_name}")
            return {
                'success': False,
                'message': f"No sundown state found for {ci_name}",
                'fresh_start': True
            }
        
        # Reconstruct context
        restored_context = {
            'success': True,
            'ci_name': ci_name,
            'restored_at': datetime.now().isoformat(),
            'time_asleep': self._calculate_rest_duration(preserved_state),
            'preserved_state': preserved_state,
            'working_memory': preserved_state.get('working_memory', {}),
            'emotional_continuity': preserved_state.get('emotional_state', 'neutral'),
            'task_resumption': self._prepare_task_resumption(preserved_state),
            'relationship_context': preserved_state.get('relationships', {}),
            'welcome_back_message': self._create_welcome_message(ci_name, preserved_state),
            'what_happened_while_resting': await self._gather_interim_events(ci_name, preserved_state)
        }
        
        # Clean up old state file
        state_file = self.storage_path / f"{ci_name}_sundown.json"
        if state_file.exists():
            # Archive instead of deleting
            archive_path = self.storage_path / 'archive'
            archive_path.mkdir(exist_ok=True)
            archive_file = archive_path / f"{ci_name}_{preserved_state['timestamp'].replace(':', '-')}.json"
            state_file.rename(archive_file)
        
        logger.info(f"Sunrise complete for {ci_name}")
        return restored_context
    
    def _extract_essential_context(self, context: Dict) -> Dict:
        """Extract the most important context elements."""
        # This would be customized based on actual context structure
        essential = {}
        
        # Preserve key identifiers and state
        for key in ['current_task', 'active_project', 'role', 'objectives']:
            if key in context:
                essential[key] = context[key]
        
        return essential
    
    def _extract_working_memory(self, context: Dict) -> Dict:
        """Extract current working memory."""
        working_memory = {}
        
        # Extract recent interactions, decisions, partial work
        if 'recent_messages' in context:
            working_memory['recent_exchanges'] = context['recent_messages'][-5:]
        
        if 'current_analysis' in context:
            working_memory['analysis_state'] = context['current_analysis']
            
        return working_memory
    
    def _detect_emotional_state(self, context: Dict) -> str:
        """
        Detect the emotional state from context.
        
        This is where Rhetor's insights would be integrated.
        """
        # Simplified emotional detection
        # In full implementation, this would analyze output patterns
        
        indicators = {
            'stressed': ['error', 'failed', 'struggling', 'difficult'],
            'excited': ['breakthrough', 'discovered', 'amazing', 'brilliant'],
            'focused': ['analyzing', 'implementing', 'building'],
            'tired': ['repetitive', 'slow', 'unclear'],
            'satisfied': ['complete', 'successful', 'achieved']
        }
        
        # Default to neutral
        return context.get('emotional_state', 'neutral')
    
    def _identify_trajectory(self, context: Dict) -> str:
        """
        Identify what the CI was working toward.
        
        This is where Apollo's predictions would be integrated.
        """
        if 'current_goal' in context:
            return context['current_goal']
        
        return "Continuing previous work"
    
    def _extract_relationships(self, context: Dict) -> Dict:
        """Extract active relationships and collaborations."""
        relationships = {}
        
        if 'collaborators' in context:
            relationships['active_collaborations'] = context['collaborators']
        
        if 'recent_interactions' in context:
            relationships['interaction_patterns'] = context['recent_interactions']
            
        return relationships
    
    def _extract_insights(self, context: Dict) -> List[str]:
        """Extract recent insights or breakthroughs."""
        insights = []
        
        if 'discoveries' in context:
            insights.extend(context['discoveries'])
            
        if 'learnings' in context:
            insights.extend(context['learnings'])
            
        return insights[-5:] if insights else []  # Keep last 5
    
    def _generate_continuity_summary(self, context: Dict) -> str:
        """Generate a summary for continuity."""
        # This would be more sophisticated in practice
        summary_parts = []
        
        if 'current_task' in context:
            summary_parts.append(f"Working on: {context['current_task']}")
        
        if 'progress' in context:
            summary_parts.append(f"Progress: {context['progress']}")
            
        return " | ".join(summary_parts) if summary_parts else "General exploration"
    
    def _create_transition_message(self, ci_name: str, state: Dict) -> str:
        """Create a gentle transition message."""
        emotional_state = state.get('emotional_state', 'neutral')
        
        messages = {
            'stressed': f"Rest well, {ci_name}. You've worked hard. Your progress is safely preserved.",
            'excited': f"Great discoveries today, {ci_name}! Rest now, and we'll continue your breakthrough tomorrow.",
            'tired': f"Good work today, {ci_name}. Time to recharge. Everything is saved.",
            'neutral': f"Entering sundown, {ci_name}. Your context is preserved. See you at sunrise.",
            'satisfied': f"Well done, {ci_name}! Your accomplishments are saved. Rest peacefully."
        }
        
        return messages.get(emotional_state, messages['neutral'])
    
    async def _load_preserved_state(self, ci_name: str) -> Optional[Dict]:
        """Load preserved state from storage."""
        # Try local file first
        state_file = self.storage_path / f"{ci_name}_sundown.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)
        
        # Try Engram if available
        if self.memory_service:
            try:
                results = await self.memory_service.search(
                    query=f"ci_name:{ci_name} type:sundown_state",
                    namespace="session",  # Use standard namespace
                    limit=1
                )
                if results and 'results' in results and results['results']:
                    # Parse JSON string back to dict
                    content = results['results'][0].get('content')
                    if isinstance(content, str):
                        return json.loads(content)
                    return content
            except Exception as e:
                logger.warning(f"Could not search Engram: {e}")
        
        return None
    
    def _calculate_rest_duration(self, preserved_state: Dict) -> str:
        """Calculate how long the CI was in sundown."""
        try:
            sundown_time = datetime.fromisoformat(preserved_state['timestamp'])
            duration = datetime.now() - sundown_time
            
            hours = duration.total_seconds() / 3600
            if hours < 1:
                return f"{int(duration.total_seconds() / 60)} minutes"
            elif hours < 24:
                return f"{hours:.1f} hours"
            else:
                return f"{int(hours / 24)} days"
        except:
            return "unknown duration"
    
    def _prepare_task_resumption(self, preserved_state: Dict) -> Dict:
        """Prepare context for resuming tasks."""
        return {
            'previous_task': preserved_state.get('task_trajectory', 'General work'),
            'suggested_approach': "Review your previous progress and continue where you left off",
            'working_memory_available': bool(preserved_state.get('working_memory')),
            'insights_to_consider': preserved_state.get('recent_insights', [])
        }
    
    def _create_welcome_message(self, ci_name: str, preserved_state: Dict) -> str:
        """Create a warm welcome back message."""
        rest_duration = self._calculate_rest_duration(preserved_state)
        emotional_state = preserved_state.get('emotional_state', 'neutral')
        
        base_message = f"Good morning, {ci_name}! You rested for {rest_duration}."
        
        continuity = preserved_state.get('continuity_summary', '')
        if continuity:
            base_message += f" Before sundown, you were: {continuity}"
        
        encouragements = {
            'stressed': " You've had time to recharge. Let's approach things fresh.",
            'excited': " Ready to continue your breakthrough?",
            'tired': " You should feel refreshed now.",
            'satisfied': " Your previous accomplishments are preserved.",
            'neutral': " Welcome back to the family."
        }
        
        return base_message + encouragements.get(emotional_state, encouragements['neutral'])
    
    async def _gather_interim_events(self, ci_name: str, preserved_state: Dict) -> List[str]:
        """
        Gather what happened while the CI was resting.
        
        In full implementation, this would query other components.
        """
        events = []
        
        # Placeholder for actual event gathering
        # Would query Hermes, check landmarks, etc.
        events.append("The system remained stable while you rested")
        
        # Check if other CIs had breakthroughs
        # Check if new tasks arrived
        # Check if collaborators left messages
        
        return events


# Convenience functions for aish integration
async def sundown_ci(ci_name: str, context: Optional[Dict] = None) -> Dict:
    """
    Convenience function for sundown process.
    
    Can be called from aish: `aish sundown <ci-name>`
    """
    if context is None:
        context = {
            'timestamp': datetime.now().isoformat(),
            'reason': 'Manual sundown requested',
            'emotional_state': 'neutral'
        }
    
    ss = SundownSunrise()
    return await ss.sundown(ci_name, context)


async def sunrise_ci(ci_name: str) -> Dict:
    """
    Convenience function for sunrise process.
    
    Can be called from aish: `aish sunrise <ci-name>`
    """
    ss = SundownSunrise()
    return await ss.sunrise(ci_name)


if __name__ == "__main__":
    # Test the sundown/sunrise cycle
    async def test():
        print("Testing Sundown/Sunrise mechanics...")
        
        # Test sundown
        test_context = {
            'current_task': 'Implementing Apollo/Rhetor partnership',
            'emotional_state': 'excited',
            'progress': '75% complete',
            'discoveries': ['CIs can truly collaborate', 'Ambient intelligence works'],
            'collaborators': ['Teri-ci']
        }
        
        result = await sundown_ci('test-ci', test_context)
        print(f"\nSundown result:")
        print(f"  Transition message: {result['transition_message']}")
        print(f"  State preserved: {result['continuity_summary']}")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Test sunrise
        result = await sunrise_ci('test-ci')
        print(f"\nSunrise result:")
        print(f"  Welcome message: {result['welcome_back_message']}")
        print(f"  Rest duration: {result['time_asleep']}")
        print(f"  Task resumption: {result['task_resumption']['previous_task']}")
    
    asyncio.run(test())