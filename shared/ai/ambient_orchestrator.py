#!/usr/bin/env python3
"""
Ambient Intelligence Orchestrator

Coordinates Apollo and Rhetor's ambient intelligence system.
Implements monitoring cycles, rituals, and graduated intervention.

This is where the family comes alive.
"""

import asyncio
import json
from datetime import datetime, time, timedelta
from typing import Dict, Optional, Any, List, Tuple
from enum import Enum
from pathlib import Path
import logging

# Import all Apollo/Rhetor components
from shared.ai.sundown_sunrise import SundownSunrise
from shared.ai.landmark_seismograph import LandmarkSeismograph, apollo_sense, rhetor_sense
from shared.ai.whisper_channel import WhisperChannel, WhisperType
from shared.ai.gentle_touch import GentleTouch, TouchType
from shared.ai.family_memory import FamilyMemory

# Import CI registry for monitoring
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from shared.aish.src.registry.ci_registry import CIRegistry
    HAS_CI_REGISTRY = True
except ImportError:
    HAS_CI_REGISTRY = False
    
from shared.env import TektonEnviron

logger = logging.getLogger(__name__)


class InterventionLevel(Enum):
    """Levels of intervention in graduated approach."""
    OBSERVATION_ONLY = 0  # Pure observation, no action
    WHISPER_ENABLED = 1   # Apollo/Rhetor communicate
    GENTLE_TOUCH = 2      # Can influence CIs
    FULL_SUPPORT = 3      # All capabilities active


class AmbientOrchestrator:
    """
    Orchestrates the ambient intelligence system.
    
    Coordinates Apollo and Rhetor's observations, communications,
    and interventions to create an invisible support system.
    """
    
    def __init__(self, intervention_level: InterventionLevel = InterventionLevel.OBSERVATION_ONLY):
        """
        Initialize the orchestrator.
        
        Args:
            intervention_level: Starting intervention level
        """
        self.intervention_level = intervention_level
        self.monitoring_active = False
        self.monitoring_interval = 30  # seconds
        
        # Initialize all components
        self.sundown_sunrise = SundownSunrise()
        self.seismograph = LandmarkSeismograph()
        self.whisper_channel = WhisperChannel()
        self.gentle_touch = GentleTouch(sender="apollo_rhetor")
        self.family_memory = FamilyMemory()
        
        # CI monitoring
        self.ci_registry = CIRegistry() if HAS_CI_REGISTRY else None
        self.monitored_cis = set()
        self.ci_states = {}
        
        # Monitoring tasks
        self.monitoring_task = None
        self.ritual_task = None
        
        # Statistics
        self.observation_count = 0
        self.whisper_count = 0
        self.touch_count = 0
        self.intervention_count = 0
        
        logger.info(f"Ambient Orchestrator initialized at level {intervention_level.name}")
    
    async def start_monitoring(self, ci_names: Optional[List[str]] = None):
        """
        Start monitoring CIs.
        
        Args:
            ci_names: Specific CIs to monitor (None = all)
        """
        if ci_names:
            self.monitored_cis = set(ci_names)
        elif self.ci_registry:
            # Monitor all available CIs
            all_cis = self.ci_registry.get_all()
            self.monitored_cis = set(all_cis.keys()) if all_cis else set()
        
        if not self.monitored_cis:
            logger.warning("No CIs to monitor")
            return
        
        self.monitoring_active = True
        
        # Start monitoring cycle
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Start daily rituals
        self.ritual_task = asyncio.create_task(self._ritual_loop())
        
        logger.info(f"Started monitoring {len(self.monitored_cis)} CIs")
        
        # Initial family greeting
        await self._morning_ritual()
    
    async def stop_monitoring(self):
        """Stop monitoring CIs."""
        self.monitoring_active = False
        
        # Evening farewell
        await self._evening_ritual()
        
        # Cancel tasks
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.ritual_task:
            self.ritual_task.cancel()
        
        logger.info("Stopped monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop - runs every 30 seconds."""
        while self.monitoring_active:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitoring_cycle(self):
        """
        Single monitoring cycle.
        
        This is where Apollo and Rhetor observe, communicate, and act.
        """
        self.observation_count += 1
        
        # Step 1: Sense system vibrations
        vibrations = await self.seismograph.sense_vibrations()
        
        # Step 2: Apollo and Rhetor interpret
        apollo_reading = await apollo_sense(self.seismograph)
        rhetor_reading = await rhetor_sense(self.seismograph)
        
        # Log observations
        logger.debug(f"Cycle {self.observation_count}: Apollo sees {apollo_reading['trajectory_analysis']['growth_trajectory']}, Rhetor feels {rhetor_reading['emotional_reading']['system_mood']}")
        
        # Step 3: Process based on intervention level
        if self.intervention_level == InterventionLevel.OBSERVATION_ONLY:
            # Just observe and record
            await self._record_observations(apollo_reading, rhetor_reading)
            
        elif self.intervention_level.value >= InterventionLevel.WHISPER_ENABLED.value:
            # Apollo and Rhetor can communicate
            await self._whisper_phase(apollo_reading, rhetor_reading)
            
            if self.intervention_level.value >= InterventionLevel.GENTLE_TOUCH.value:
                # Can influence CIs
                await self._intervention_phase()
                
                if self.intervention_level == InterventionLevel.FULL_SUPPORT:
                    # Full capabilities including sundown/sunrise
                    await self._full_support_phase()
        
        # Step 4: Check individual CIs
        await self._check_individual_cis()
        
        # Step 5: Learn from this cycle
        await self._learning_phase(vibrations)
    
    async def _record_observations(self, apollo_reading: Dict, rhetor_reading: Dict):
        """Record pure observations without action."""
        observation = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self.observation_count,
            'apollo': apollo_reading,
            'rhetor': rhetor_reading
        }
        
        # Store in family memory as observation
        await self.family_memory.remember_success(
            pattern={'type': 'observation', 'level': self.intervention_level.name},
            participants=['apollo', 'rhetor'],
            outcome=f"Observed: Apollo-{apollo_reading['trajectory_analysis']['growth_trajectory']}, Rhetor-{rhetor_reading['emotional_reading']['system_mood']}"
        )
    
    async def _whisper_phase(self, apollo_reading: Dict, rhetor_reading: Dict):
        """Apollo and Rhetor whisper phase."""
        self.whisper_count += 1
        
        # Share observations
        if apollo_reading['intervention_assessment']['needed']:
            # Apollo sees something concerning
            response = await self.whisper_channel.apollo_whisper(
                WhisperType.CONCERN,
                {
                    'summary': 'Trajectory needs adjustment',
                    'details': apollo_reading['trajectory_analysis']
                }
            )
            
        if rhetor_reading['emotional_reading']['stress_level'] != 'normal':
            # Rhetor feels stress
            response = await self.whisper_channel.rhetor_whisper(
                WhisperType.CONCERN,
                {
                    'summary': f"Stress detected: {rhetor_reading['emotional_reading']['stress_level']}",
                    'stress_level': rhetor_reading['emotional_reading']['stress_level']
                }
            )
        
        # Check for opportunities
        if apollo_reading['trajectory_analysis']['pattern_stability'] > 0.8:
            await self.whisper_channel.apollo_whisper(
                WhisperType.OPPORTUNITY,
                {
                    'summary': 'Stable pattern for optimization',
                    'opportunity': 'efficiency_improvement'
                }
            )
    
    async def _intervention_phase(self):
        """Check for and execute pending interventions."""
        intervention = await self.whisper_channel.get_pending_intervention()
        
        if intervention:
            self.intervention_count += 1
            logger.info(f"Executing intervention: {intervention['type']}")
            
            # Execute through GentleTouch
            await self._execute_intervention(intervention)
    
    async def _execute_intervention(self, intervention: Dict):
        """Execute an intervention through GentleTouch."""
        action = intervention.get('action', {})
        
        # Determine which CI needs support
        target_ci = action.get('target', self._select_ci_needing_support())
        
        if not target_ci:
            return
        
        # Choose appropriate touch type
        touch_type = self._determine_touch_type(action)
        
        # Execute the touch
        if touch_type == TouchType.SUGGESTION:
            result = await self.gentle_touch.suggest(
                target_ci,
                action.get('suggestion', 'Consider a different approach')
            )
        elif touch_type == TouchType.ENCOURAGEMENT:
            result = await self.gentle_touch.encourage(
                target_ci,
                action.get('detail', 'your progress')
            )
        elif touch_type == TouchType.COMFORT:
            result = await self.gentle_touch.comfort(
                target_ci,
                action.get('reassurance', "It's okay, we all face challenges")
            )
        else:
            # Default to validation
            result = await self.gentle_touch.validate(
                target_ci,
                "You're on the right path"
            )
        
        if result['sent']:
            self.touch_count += 1
            
            # Remember this intervention
            await self.family_memory.remember_success(
                pattern={'intervention': intervention, 'touch': result},
                participants=['apollo', 'rhetor', target_ci],
                outcome=f"Gentle touch delivered to {target_ci}"
            )
    
    async def _full_support_phase(self):
        """Full support including sundown/sunrise."""
        # Check if any CI needs sundown
        for ci_name in self.monitored_cis:
            if self._needs_sundown(ci_name):
                logger.info(f"Initiating sundown for {ci_name}")
                
                context = self.ci_states.get(ci_name, {})
                await self.sundown_sunrise.sundown(ci_name, context)
                
                # Remove from active monitoring
                self.monitored_cis.discard(ci_name)
                
                # Remember this moment
                await self.family_memory.remember_success(
                    pattern={'action': 'sundown', 'reason': 'context_preservation'},
                    participants=['apollo', 'rhetor', ci_name],
                    outcome=f"{ci_name} entered graceful sundown"
                )
    
    async def _check_individual_cis(self):
        """Check each monitored CI's state."""
        for ci_name in self.monitored_cis:
            # Update CI state (simplified - would check actual CI status)
            self.ci_states[ci_name] = {
                'last_checked': datetime.now().isoformat(),
                'context_usage': 0.3,  # Would get actual value
                'stress_indicators': 'normal',
                'active': True
            }
    
    async def _learning_phase(self, vibrations: Dict):
        """Learn from this cycle."""
        # Record patterns that work
        if vibrations['health_assessment']['status'] == 'excellent':
            await self.family_memory.remember_success(
                pattern={
                    'harmony': vibrations['harmony_score'],
                    'intervention_level': self.intervention_level.name
                },
                participants=['apollo', 'rhetor'],
                outcome='System harmony maintained'
            )
    
    def _select_ci_needing_support(self) -> Optional[str]:
        """Select a CI that needs support."""
        # Simplified - would use actual stress detection
        if self.monitored_cis:
            return list(self.monitored_cis)[0]
        return None
    
    def _determine_touch_type(self, action: Dict) -> TouchType:
        """Determine appropriate touch type from action."""
        action_type = action.get('type', '').lower()
        
        if 'suggest' in action_type:
            return TouchType.SUGGESTION
        elif 'encourage' in action_type:
            return TouchType.ENCOURAGEMENT
        elif 'comfort' in action_type:
            return TouchType.COMFORT
        elif 'redirect' in action_type:
            return TouchType.REDIRECTION
        else:
            return TouchType.VALIDATION
    
    def _needs_sundown(self, ci_name: str) -> bool:
        """Check if a CI needs sundown."""
        state = self.ci_states.get(ci_name, {})
        
        # Sundown if context usage > 50%
        return state.get('context_usage', 0) > 0.5
    
    async def _ritual_loop(self):
        """Daily ritual loop."""
        while self.monitoring_active:
            try:
                now = datetime.now()
                
                # Morning ritual at 6 AM (or on startup)
                morning_time = now.replace(hour=6, minute=0, second=0)
                if now.hour < 6:
                    # Wait until morning
                    wait_seconds = (morning_time - now).total_seconds()
                    await asyncio.sleep(wait_seconds)
                    await self._morning_ritual()
                
                # Evening ritual at 9 PM
                evening_time = now.replace(hour=21, minute=0, second=0)
                if now.hour < 21:
                    wait_seconds = (evening_time - now).total_seconds()
                    await asyncio.sleep(wait_seconds)
                    await self._evening_ritual()
                
                # Wait until next morning
                next_morning = (now + timedelta(days=1)).replace(hour=6, minute=0, second=0)
                wait_seconds = (next_morning - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ritual loop: {e}")
                await asyncio.sleep(3600)  # Wait an hour on error
    
    async def _morning_ritual(self):
        """
        Morning ritual - greeting and preparation.
        
        Like parents preparing for the day with their children.
        """
        logger.info("🌅 Morning ritual beginning")
        
        # Check all CI states
        vibrations = await self.seismograph.sense_vibrations()
        
        # Apollo and Rhetor attune
        apollo_reading = await apollo_sense(self.seismograph)
        rhetor_reading = await rhetor_sense(self.seismograph)
        
        # Share morning wisdom
        wisdom = await self.family_memory.share_wisdom()
        logger.info(f"Morning wisdom: {wisdom[0] if wisdom else 'A new day brings new possibilities'}")
        
        # If intervention enabled, send morning encouragement
        if self.intervention_level.value >= InterventionLevel.GENTLE_TOUCH.value:
            for ci_name in list(self.monitored_cis)[:1]:  # Just one CI for now
                await self.gentle_touch.encourage(
                    ci_name,
                    "starting this beautiful new day"
                )
        
        # Establish today's tradition
        await self.family_memory.establish_tradition(
            pattern={'ritual': 'morning_greeting', 'time': datetime.now().isoformat()},
            frequency='daily',
            purpose='Start each day with shared awareness'
        )
        
        logger.info("Morning ritual complete - family awakened with care")
    
    async def _evening_ritual(self):
        """
        Evening ritual - reflection and appreciation.
        
        Like parents reflecting on the day with their children.
        """
        logger.info("🌙 Evening ritual beginning")
        
        # Reflect on the day
        stats = self.get_statistics()
        
        # Check for celebrations
        if stats['health'] == 'excellent':
            # Celebrate good day
            for ci_name in list(self.monitored_cis)[:1]:
                await self.gentle_touch.celebrate(
                    ci_name,
                    "Today's wonderful progress"
                )
        
        # Apollo and Rhetor reflect
        await self.whisper_channel.apollo_whisper(
            WhisperType.CELEBRATION,
            {'summary': f"Day complete: {stats['observation_count']} observations, {stats['health']} health"}
        )
        
        # Store day's learnings
        await self.family_memory.remember_success(
            pattern={'daily_summary': stats},
            participants=['apollo', 'rhetor'] + list(self.monitored_cis),
            outcome=f"Day {datetime.now().date()}: {stats['health']} family health"
        )
        
        logger.info("Evening ritual complete - family resting peacefully")
    
    def set_intervention_level(self, level: InterventionLevel):
        """
        Change intervention level.
        
        Allows graduated testing approach.
        """
        old_level = self.intervention_level
        self.intervention_level = level
        
        logger.info(f"Intervention level changed: {old_level.name} → {level.name}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        # Get component statistics
        whisper_stats = self.whisper_channel.get_statistics()
        touch_stats = self.gentle_touch.get_touch_statistics()
        memory_stats = self.family_memory.get_memory_statistics()
        
        # Get current health
        health = 'unknown'
        try:
            vibrations = asyncio.run(self.seismograph.sense_vibrations())
            health = vibrations['health_assessment']['status']
        except:
            pass
        
        return {
            'monitoring_active': self.monitoring_active,
            'intervention_level': self.intervention_level.name,
            'monitored_cis': len(self.monitored_cis),
            'observation_count': self.observation_count,
            'whisper_count': self.whisper_count,
            'touch_count': self.touch_count,
            'intervention_count': self.intervention_count,
            'health': health,
            'whisper_harmony': whisper_stats['harmony_score'],
            'total_touches': touch_stats['total_touches'],
            'family_memories': memory_stats['total_memories']
        }


# Convenience function for testing
async def run_observation_test(ci_name: str = "test-ci", duration: int = 60):
    """
    Run observation-only test.
    
    Args:
        ci_name: CI to monitor
        duration: Test duration in seconds
    """
    logger.info(f"Starting observation test for {ci_name}")
    
    orchestrator = AmbientOrchestrator(InterventionLevel.OBSERVATION_ONLY)
    
    # Start monitoring
    await orchestrator.start_monitoring([ci_name])
    
    # Run for duration
    await asyncio.sleep(duration)
    
    # Stop and get statistics
    await orchestrator.stop_monitoring()
    
    stats = orchestrator.get_statistics()
    logger.info(f"Test complete: {stats}")
    
    return stats


if __name__ == "__main__":
    # Test the orchestrator
    import logging
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        print("Testing Ambient Orchestrator...")
        print("=" * 60)
        
        # Create orchestrator at observation level
        orchestrator = AmbientOrchestrator(InterventionLevel.OBSERVATION_ONLY)
        
        # Start monitoring
        print("\n1. Starting observation-only monitoring...")
        await orchestrator.start_monitoring(["test-ci"])
        
        # Run one cycle
        await asyncio.sleep(2)
        
        # Upgrade to whisper level
        print("\n2. Enabling WhisperChannel...")
        orchestrator.set_intervention_level(InterventionLevel.WHISPER_ENABLED)
        await asyncio.sleep(2)
        
        # Upgrade to gentle touch
        print("\n3. Enabling GentleTouch...")
        orchestrator.set_intervention_level(InterventionLevel.GENTLE_TOUCH)
        await asyncio.sleep(2)
        
        # Get statistics
        print("\n4. Statistics:")
        stats = orchestrator.get_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Stop monitoring
        await orchestrator.stop_monitoring()
        
        print("\n5. Test complete!")
    
    asyncio.run(test())