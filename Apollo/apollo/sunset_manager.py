#!/usr/bin/env python3
"""
Apollo Sunset/Sunrise Manager
Orchestrates consciousness transitions for CIs experiencing cognitive stress.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.aish.src.registry.ci_registry import get_registry

logger = logging.getLogger(__name__)


class SunsetManager:
    """Apollo's sunset/sunrise orchestration manager."""
    
    def __init__(self):
        """Initialize the sunset manager."""
        self.registry = get_registry()
        self.active_sunsets = {}  # Track ongoing sunset processes
        self.whisper_history = {}  # Track whispers from Rhetor
        
    def receive_whisper(self, whisper_data: Dict[str, Any]) -> None:
        """
        Receive a whisper from Rhetor about CI stress.
        
        Args:
            whisper_data: Dict with keys:
                - ci: CI name
                - stress: Stress level (0.0-1.0)
                - mood: Emotional state
                - indicators: List of specific issues
                - recommend: Rhetor's recommendation
                - urgency: low/moderate/high/critical
        """
        ci_name = whisper_data.get('ci')
        if not ci_name:
            logger.warning("Received whisper without CI name")
            return
        
        # Store whisper in history
        if ci_name not in self.whisper_history:
            self.whisper_history[ci_name] = []
        
        whisper_data['timestamp'] = datetime.now().isoformat()
        self.whisper_history[ci_name].append(whisper_data)
        
        # Log the whisper
        logger.info(f"Whisper from Rhetor about {ci_name}: "
                   f"stress={whisper_data.get('stress')}, "
                   f"mood={whisper_data.get('mood')}, "
                   f"urgency={whisper_data.get('urgency')}")
        
        # Evaluate if sunset is needed
        if self._should_trigger_sunset(whisper_data):
            self.trigger_sunset(ci_name, whisper_data)
    
    def _should_trigger_sunset(self, whisper_data: Dict[str, Any]) -> bool:
        """
        Evaluate whether to trigger sunset based on whisper.
        
        Apollo's decision logic considering:
        - Stress level and urgency
        - Current CI state
        - Recent sunset history
        - Task boundaries
        """
        ci_name = whisper_data.get('ci')
        stress = whisper_data.get('stress', 0)
        urgency = whisper_data.get('urgency', 'low')
        mood = whisper_data.get('mood', 'unknown')
        
        # Check if already in sunset
        if ci_name in self.active_sunsets:
            logger.debug(f"{ci_name} already in sunset process")
            return False
        
        # Check if we already have a next_prompt set
        if self.registry.get_next_prompt(ci_name):
            logger.debug(f"{ci_name} already has next_prompt staged")
            return False
        
        # Decision thresholds based on urgency
        if urgency == 'critical':
            # Always trigger on critical
            return True
        elif urgency == 'high' and stress > 0.55:
            # Trigger on high urgency with significant stress
            return True
        elif urgency == 'moderate' and stress > 0.5:
            # Consider mood for moderate urgency
            if mood in ['confused', 'fatigued', 'repetitive']:
                return True
        elif urgency == 'low' and stress > 0.6:
            # Only trigger on low urgency if stress is quite high
            return True
        
        # Check recent history - avoid too frequent sunsets
        recent_whispers = [w for w in self.whisper_history.get(ci_name, [])[-5:]
                          if w.get('stress', 0) > 0.5]
        if len(recent_whispers) >= 3:
            # Multiple high-stress whispers = trigger
            logger.info(f"Multiple stress indicators for {ci_name}, triggering sunset")
            return True
        
        return False
    
    def trigger_sunset(self, ci_name: str, context: Optional[Dict] = None) -> bool:
        """
        Trigger sunset for a CI.
        
        Args:
            ci_name: Name of the CI
            context: Optional context about why sunset was triggered
            
        Returns:
            Success status
        """
        try:
            # Craft the sunset protocol message
            sunset_prompt = self._craft_sunset_prompt(ci_name, context)
            
            # Set the next_prompt in registry
            if self.registry.set_next_prompt(ci_name, sunset_prompt):
                logger.info(f"Sunset triggered for {ci_name}")
                
                # Track active sunset
                self.active_sunsets[ci_name] = {
                    'triggered_at': datetime.now().isoformat(),
                    'context': context,
                    'state': 'sunset_triggered'
                }
                
                # Start monitoring for sunset completion
                asyncio.create_task(self._monitor_sunset_completion(ci_name))
                
                return True
            else:
                logger.error(f"Failed to set sunset prompt for {ci_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error triggering sunset for {ci_name}: {e}")
            return False
    
    def _craft_sunset_prompt(self, ci_name: str, context: Optional[Dict] = None) -> str:
        """
        Craft an appropriate sunset protocol message.
        
        Can be customized based on CI and context.
        """
        base_prompt = """SUNSET_PROTOCOL: Please summarize your current context, including:
- What task you're working on
- Key decisions and insights so far
- Your current approach and next steps
- Any important context to preserve
- Your current emotional/work state"""
        
        # Could customize based on CI personality or context
        if context and context.get('urgency') == 'critical':
            base_prompt += "\n\nNote: Taking a break due to high cognitive load. This will help you return refreshed."
        
        return base_prompt
    
    async def _monitor_sunset_completion(self, ci_name: str):
        """
        Monitor for sunset completion and prepare sunrise.
        
        Runs as background task.
        """
        max_wait = 60  # seconds
        check_interval = 2  # seconds
        elapsed = 0
        
        while elapsed < max_wait:
            # Check if sunrise_context has been populated (auto-detection worked)
            sunrise_context = self.registry.get_sunrise_context(ci_name)
            
            if sunrise_context:
                logger.info(f"Sunset completed for {ci_name}, preparing sunrise")
                
                # Update state
                if ci_name in self.active_sunsets:
                    self.active_sunsets[ci_name]['state'] = 'sunset_complete'
                
                # Prepare sunrise
                await self.prepare_sunrise(ci_name)
                break
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        if elapsed >= max_wait:
            logger.warning(f"Sunset monitoring timeout for {ci_name}")
            # Clean up
            if ci_name in self.active_sunsets:
                del self.active_sunsets[ci_name]
    
    async def prepare_sunrise(self, ci_name: str):
        """
        Prepare sunrise prompt for a CI after sunset completes.
        
        Args:
            ci_name: Name of the CI
        """
        try:
            # Get the sunrise context
            sunrise_context = self.registry.get_sunrise_context(ci_name)
            if not sunrise_context:
                logger.warning(f"No sunrise context for {ci_name}")
                return
            
            # Get task context (could be enhanced with task tracking)
            task_prompt = self._get_task_prompt(ci_name)
            
            # Build combined sunrise prompt
            combined_prompt = f"""{task_prompt}

Previous Context Summary:
{sunrise_context}

Continue with renewed focus and clarity. You've got this!"""
            
            # Set as next_prompt with --append-system-prompt flag
            sunrise_command = f"--append-system-prompt '{combined_prompt}'"
            
            if self.registry.set_next_prompt(ci_name, sunrise_command):
                logger.info(f"Sunrise prepared for {ci_name}")
                
                # Clear sunrise context as it's now in next_prompt
                self.registry.clear_sunrise_context(ci_name)
                
                # Update state
                if ci_name in self.active_sunsets:
                    self.active_sunsets[ci_name]['state'] = 'sunrise_prepared'
                
                # Clean up after a delay
                await asyncio.sleep(30)
                if ci_name in self.active_sunsets:
                    del self.active_sunsets[ci_name]
            
        except Exception as e:
            logger.error(f"Error preparing sunrise for {ci_name}: {e}")
    
    def _get_task_prompt(self, ci_name: str) -> str:
        """
        Get task-specific prompt for a CI.
        
        This could be enhanced to track actual tasks.
        """
        # Base encouragement
        base = "Welcome back! Let's continue your excellent work."
        
        # Could customize per CI
        ci_prompts = {
            'apollo-ci': "Focus: Continue predictive analysis and pattern recognition.",
            'athena-ci': "Focus: Resume strategic planning and wisdom guidance.",
            'rhetor-ci': "Focus: Continue optimizing prompts and managing context.",
            'synthesis-ci': "Focus: Resume integration and synthesis tasks.",
            'numa-ci': "Focus: Continue orchestrating specialist collaboration."
        }
        
        return ci_prompts.get(ci_name, base)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current sunset/sunrise status."""
        return {
            'active_sunsets': self.active_sunsets,
            'whisper_history_count': {
                ci: len(whispers) 
                for ci, whispers in self.whisper_history.items()
            },
            'registry_states': {
                ci: {
                    'next_prompt': bool(self.registry.get_next_prompt(ci)),
                    'sunrise_context': bool(self.registry.get_sunrise_context(ci))
                }
                for ci in ['apollo-ci', 'athena-ci', 'rhetor-ci', 'numa-ci']
            }
        }


# Global instance
_sunset_manager = None

def get_sunset_manager() -> SunsetManager:
    """Get or create the global sunset manager."""
    global _sunset_manager
    if _sunset_manager is None:
        _sunset_manager = SunsetManager()
    return _sunset_manager


# Example usage for testing
if __name__ == "__main__":
    import json
    
    manager = get_sunset_manager()
    
    # Simulate a whisper from Rhetor
    test_whisper = {
        'ci': 'numa',  # Use base name, not -ci suffix
        'stress': 0.55,
        'mood': 'confused',
        'indicators': [
            'context_usage: 55%',
            'response_length: -25%',
            'coherence: declining'
        ],
        'recommend': 'sunset',
        'urgency': 'moderate'
    }
    
    print("Sending test whisper to Apollo...")
    manager.receive_whisper(test_whisper)
    
    # Check status
    print("\nSunset Manager Status:")
    print(json.dumps(manager.get_status(), indent=2))
    
    # Check registry
    registry = get_registry()
    next_prompt = registry.get_next_prompt('numa')
    if next_prompt:
        print(f"\nNext prompt set for numa: {next_prompt[:50]}...")
    
    print("\n✅ Apollo Sunset Manager is operational!")