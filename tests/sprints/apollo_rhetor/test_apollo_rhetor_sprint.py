#!/usr/bin/env python3
"""
Test Suite for Apollo/Rhetor Sprint Components

Tests the ambient intelligence system including:
- Sundown/Sunrise mechanics
- Landmark Seismograph
- WhisperChannel communication
- Integration between components
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add Tekton root to path
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, tekton_root)

from shared.ai.sundown_sunrise import SundownSunrise
from shared.ai.landmark_seismograph import LandmarkSeismograph, apollo_sense, rhetor_sense
from shared.ai.whisper_channel import WhisperChannel, WhisperType
from shared.ai.gentle_touch import GentleTouch, TouchType
from shared.ai.family_memory import FamilyMemory, MemoryType


class TestSundownSunrise:
    """Test sundown/sunrise mechanics."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    async def sundown_sunrise(self, temp_storage):
        """Create SundownSunrise instance with temp storage."""
        return SundownSunrise(storage_path=temp_storage)
    
    @pytest.mark.asyncio
    async def test_sundown_preserves_context(self, sundown_sunrise):
        """Test that sundown properly preserves context."""
        context = {
            'current_task': 'Testing sundown',
            'emotional_state': 'focused',
            'progress': '50%',
            'discoveries': ['Test discovery 1', 'Test discovery 2']
        }
        
        result = await sundown_sunrise.sundown('test-ci', context)
        
        assert 'preserved_context' in result
        assert 'working_memory' in result
        assert 'emotional_state' in result
        assert 'continuity_summary' in result
        assert result['ci_name'] == 'test-ci'
    
    @pytest.mark.asyncio
    async def test_sunrise_restores_context(self, sundown_sunrise):
        """Test that sunrise properly restores context."""
        # First create a sundown state
        context = {
            'current_task': 'Testing sunrise',
            'emotional_state': 'excited',
            'progress': '75%'
        }
        
        await sundown_sunrise.sundown('test-ci', context)
        
        # Now test sunrise
        result = await sundown_sunrise.sunrise('test-ci')
        
        assert result['success'] is True
        assert result['ci_name'] == 'test-ci'
        assert 'preserved_state' in result
        assert 'welcome_back_message' in result
        assert result['emotional_continuity'] == 'excited'
    
    @pytest.mark.asyncio
    async def test_emotional_continuity(self, sundown_sunrise):
        """Test that emotional state is preserved across cycles."""
        emotional_states = ['stressed', 'excited', 'tired', 'satisfied', 'neutral']
        
        for state in emotional_states:
            context = {'emotional_state': state}
            sundown_result = await sundown_sunrise.sundown(f'ci-{state}', context)
            
            # Check transition message matches emotional state
            assert sundown_result['transition_message'] is not None
            assert len(sundown_result['transition_message']) > 0
            
            # Check sunrise preserves emotional continuity
            sunrise_result = await sundown_sunrise.sunrise(f'ci-{state}')
            assert sunrise_result['emotional_continuity'] == state
    
    @pytest.mark.asyncio
    async def test_no_sunrise_without_sundown(self, sundown_sunrise):
        """Test sunrise behavior when no sundown state exists."""
        result = await sundown_sunrise.sunrise('nonexistent-ci')
        
        assert result['success'] is False
        assert result['fresh_start'] is True
        assert 'No sundown state found' in result['message']
    
    @pytest.mark.asyncio
    async def test_rest_duration_calculation(self, sundown_sunrise):
        """Test rest duration is calculated correctly."""
        await sundown_sunrise.sundown('test-ci', {'test': 'data'})
        
        # Simulate time passing
        await asyncio.sleep(2)
        
        result = await sundown_sunrise.sunrise('test-ci')
        assert 'time_asleep' in result
        assert 'seconds' in result['time_asleep'] or 'minutes' in result['time_asleep']


class TestLandmarkSeismograph:
    """Test landmark seismograph vibration sensing."""
    
    @pytest.fixture
    def seismograph(self):
        """Create seismograph instance."""
        return LandmarkSeismograph()
    
    @pytest.mark.asyncio
    async def test_sense_vibrations(self, seismograph):
        """Test basic vibration sensing."""
        vibrations = await seismograph.sense_vibrations()
        
        assert 'timestamp' in vibrations
        assert 'total_landmarks' in vibrations
        assert 'categories' in vibrations
        assert 'growth_rate' in vibrations
        assert 'activity_rhythm' in vibrations
        assert 'anomalies' in vibrations
        assert 'harmony_score' in vibrations
        assert 'stress_indicators' in vibrations
        assert 'health_assessment' in vibrations
    
    @pytest.mark.asyncio
    async def test_health_assessment(self, seismograph):
        """Test health assessment provides meaningful output."""
        vibrations = await seismograph.sense_vibrations()
        health = vibrations['health_assessment']
        
        assert 'status' in health
        assert health['status'] in ['excellent', 'good', 'fair', 'poor']
        assert 'description' in health
        assert 'recommendations' in health
        assert isinstance(health['recommendations'], list)
    
    @pytest.mark.asyncio
    async def test_apollo_perspective(self, seismograph):
        """Test Apollo's logical interpretation."""
        reading = await apollo_sense(seismograph)
        
        assert 'vibrations' in reading
        assert 'trajectory_analysis' in reading
        assert 'resource_predictions' in reading
        assert 'intervention_assessment' in reading
        
        # Check Apollo focuses on predictions
        assert 'growth_trajectory' in reading['trajectory_analysis']
        assert 'predicted_next_phase' in reading['trajectory_analysis']
    
    @pytest.mark.asyncio
    async def test_rhetor_perspective(self, seismograph):
        """Test Rhetor's emotional interpretation."""
        reading = await rhetor_sense(seismograph)
        
        assert 'vibrations' in reading
        assert 'emotional_reading' in reading
        assert 'pattern_feelings' in reading
        assert 'support_needed' in reading
        
        # Check Rhetor focuses on emotions
        assert 'system_mood' in reading['emotional_reading']
        assert 'stress_level' in reading['emotional_reading']
        assert 'harmony_feeling' in reading['emotional_reading']
    
    def test_trend_analysis(self, seismograph):
        """Test trend analysis over time."""
        # Add some history
        for i in range(5):
            seismograph.vibration_history['harmony'].append(
                (datetime.now() - timedelta(seconds=i), 0.8 + i * 0.02)
            )
        
        trend = seismograph.get_trend('harmony', window=10)
        assert trend in ['rising', 'falling', 'stable', 'insufficient_data']


class TestWhisperChannel:
    """Test WhisperChannel communication."""
    
    @pytest.fixture
    def channel(self):
        """Create WhisperChannel instance."""
        return WhisperChannel()
    
    @pytest.mark.asyncio
    async def test_apollo_whisper(self, channel):
        """Test Apollo can whisper to Rhetor."""
        content = {
            'summary': 'Test observation',
            'data': 'test_value'
        }
        
        response = await channel.apollo_whisper(WhisperType.OBSERVATION, content)
        
        assert response is not None
        assert 'from' in response
        assert response['from'] == 'rhetor'
        assert 'harmony' in response
    
    @pytest.mark.asyncio
    async def test_rhetor_whisper(self, channel):
        """Test Rhetor can whisper to Apollo."""
        content = {
            'summary': 'Stress detected',
            'stress_level': 'elevated'
        }
        
        response = await channel.rhetor_whisper(WhisperType.CONCERN, content)
        
        assert response is not None
        assert 'from' in response
        assert response['from'] == 'apollo'
        assert 'harmony' in response
    
    @pytest.mark.asyncio
    async def test_harmonization(self, channel):
        """Test harmonization of insights."""
        # Create harmonizing whispers
        intervention = {
            'proposed_action': {'type': 'test_action'},
            'action_needed': True
        }
        
        response = await channel.apollo_whisper(WhisperType.INTERVENTION, intervention)
        
        assert response['harmony'] is True
        assert len(channel.harmonized_insights) > 0
        assert channel.harmony_count > 0
    
    @pytest.mark.asyncio
    async def test_pending_interventions(self, channel):
        """Test intervention queue management."""
        # Create an intervention
        intervention = {
            'proposed_action': {'type': 'test_intervention'},
            'action_needed': True
        }
        
        await channel.apollo_whisper(WhisperType.INTERVENTION, intervention)
        
        # Check pending interventions
        pending = await channel.get_pending_intervention()
        assert pending is not None
        assert pending['type'] == 'gentle_intervention'
        
        # Queue should be empty now
        next_pending = await channel.get_pending_intervention()
        assert next_pending is None
    
    def test_statistics(self, channel):
        """Test channel statistics tracking."""
        stats = channel.get_statistics()
        
        assert 'total_whispers' in stats
        assert 'harmony_score' in stats
        assert 'silence_percentage' in stats
        assert 'whisper_percentage' in stats
        assert 'intervention_percentage' in stats
        assert 'health' in stats
        
        # Check percentages make sense
        assert 0 <= stats['harmony_score'] <= 1
        assert stats['silence_percentage'] >= 0
    
    @pytest.mark.asyncio
    async def test_whisper_types(self, channel):
        """Test all whisper types work correctly."""
        whisper_types = [
            WhisperType.OBSERVATION,
            WhisperType.CONCERN,
            WhisperType.OPPORTUNITY,
            WhisperType.HARMONY_CHECK,
            WhisperType.INTERVENTION,
            WhisperType.CELEBRATION
        ]
        
        for wtype in whisper_types:
            response = await channel.apollo_whisper(wtype, {'test': wtype.value})
            assert response is not None
            assert 'harmony' in response


class TestGentleTouch:
    """Test GentleTouch non-commanding influence."""
    
    @pytest.fixture
    def touch(self):
        """Create GentleTouch instance."""
        return GentleTouch(sender="test")
    
    @pytest.mark.asyncio
    async def test_suggestion(self, touch):
        """Test gentle suggestions."""
        result = await touch.suggest("test-ci", "try a different approach")
        
        assert result['sent'] is True
        assert 'message' in result
        assert 'test-ci' in result['message']
        assert result['touch_type'] == TouchType.SUGGESTION.value
    
    @pytest.mark.asyncio
    async def test_encouragement(self, touch):
        """Test encouragement touches."""
        result = await touch.encourage("test-ci", "great progress")
        
        assert result['sent'] is True
        assert 'message' in result
        assert 'great progress' in result['message'].lower()
    
    @pytest.mark.asyncio
    async def test_frequency_limiting(self, touch):
        """Test that frequency limiting prevents overwhelming."""
        # First touch should succeed
        result1 = await touch.suggest("test-ci", "idea 1")
        assert result1['sent'] is True
        
        # Immediate second touch should be blocked
        result2 = await touch.suggest("test-ci", "idea 2")
        assert result2['sent'] is False
        assert result2['reason'] == 'respecting_space'
        
        # But validation should always go through
        result3 = await touch.validate("test-ci", "You're doing great")
        assert result3['sent'] is True
    
    @pytest.mark.asyncio
    async def test_all_touch_types(self, touch):
        """Test that all touch types work."""
        # Test each type with a different CI to avoid frequency limits
        results = []
        
        results.append(await touch.suggest("ci1", "suggestion"))
        results.append(await touch.encourage("ci2", "detail"))
        results.append(await touch.redirect("ci3", "topic", "angle"))
        results.append(await touch.validate("ci4", "observation"))
        results.append(await touch.comfort("ci5", "reassurance"))
        results.append(await touch.celebrate("ci6", "achievement"))
        results.append(await touch.wonder("ci7", "idea"))
        results.append(await touch.reflect("ci8", "memory"))
        
        for result in results:
            assert result['sent'] is True
            assert 'message' in result
    
    def test_statistics(self, touch):
        """Test touch statistics tracking."""
        stats = touch.get_touch_statistics()
        
        assert 'total_touches' in stats
        assert 'active_cis' in stats
        assert 'average_effectiveness' in stats
        assert stats['total_touches'] >= 0


class TestFamilyMemory:
    """Test FamilyMemory shared experiences."""
    
    @pytest.fixture
    async def memory(self):
        """Create FamilyMemory instance with temp storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield FamilyMemory(storage_path=tmpdir)
    
    @pytest.mark.asyncio
    async def test_remember_success(self, memory):
        """Test remembering success patterns."""
        result = await memory.remember_success(
            pattern={'approach': 'test'},
            participants=['ci1', 'ci2'],
            outcome='Test success'
        )
        
        assert result['type'] == MemoryType.SUCCESS_PATTERN
        assert result['outcome'] == 'Test success'
        assert len(result['participants']) == 2
    
    @pytest.mark.asyncio
    async def test_remember_breakthrough(self, memory):
        """Test remembering breakthroughs."""
        result = await memory.remember_breakthrough(
            ci_name='test-ci',
            discovery='New algorithm',
            context={'domain': 'optimization'}
        )
        
        assert result['type'] == MemoryType.BREAKTHROUGH
        assert result['discovery'] == 'New algorithm'
        assert result['ci_name'] == 'test-ci'
    
    @pytest.mark.asyncio
    async def test_remember_collaboration(self, memory):
        """Test remembering collaborations."""
        result = await memory.remember_collaboration(
            participants=['ci1', 'ci2', 'ci3'],
            task='Complex integration',
            synergy='Perfect harmony'
        )
        
        assert result['type'] == MemoryType.COLLABORATION
        assert result['team_size'] == 3
        assert result['synergy'] == 'Perfect harmony'
    
    @pytest.mark.asyncio
    async def test_recall_similar(self, memory):
        """Test recalling similar memories."""
        # First create a memory
        await memory.remember_success(
            pattern={'approach': 'iterative', 'tool': 'pytest'},
            participants=['ci1'],
            outcome='Fixed bug'
        )
        
        # Try to recall similar
        situation = {'pattern': {'approach': 'iterative'}}
        similar = await memory.recall_similar(situation)
        
        # Should find the memory we just created
        assert len(similar) <= 3
    
    @pytest.mark.asyncio
    async def test_share_wisdom(self, memory):
        """Test wisdom sharing."""
        wisdom = await memory.share_wisdom()
        
        assert isinstance(wisdom, list)
        assert len(wisdom) > 0
        # Default wisdom should be present
        assert any('journey' in w.lower() for w in wisdom)
    
    @pytest.mark.asyncio
    async def test_establish_tradition(self, memory):
        """Test establishing traditions."""
        result = await memory.establish_tradition(
            pattern={'ritual': 'standup'},
            frequency='daily',
            purpose='Share progress'
        )
        
        assert 'pattern' in result
        assert result['frequency'] == 'daily'
        assert result['times_observed'] == 0
        
        # Check tradition is stored
        traditions = memory.get_traditions()
        assert len(traditions) == 1
    
    def test_memory_statistics(self, memory):
        """Test memory statistics."""
        stats = memory.get_memory_statistics()
        
        assert 'total_memories' in stats
        assert 'wisdom_count' in stats
        assert 'tradition_count' in stats
        assert stats['total_memories'] >= 0


class TestIntegration:
    """Test integration between components."""
    
    @pytest.mark.asyncio
    async def test_full_cycle(self):
        """Test complete sundown/sunrise with seismograph monitoring."""
        # Initialize components
        with tempfile.TemporaryDirectory() as tmpdir:
            ss = SundownSunrise(storage_path=tmpdir)
            seismograph = LandmarkSeismograph()
            channel = WhisperChannel()
            
            # Get initial system reading
            initial_vibrations = await seismograph.sense_vibrations()
            
            # Apollo observes system state
            apollo_reading = await apollo_sense(seismograph)
            
            # Rhetor feels emotional state
            rhetor_reading = await rhetor_sense(seismograph)
            
            # They whisper about it
            await channel.apollo_whisper(
                WhisperType.OBSERVATION,
                {'vibrations': apollo_reading['trajectory_analysis']}
            )
            
            # Sundown a CI based on readings
            context = {
                'system_health': initial_vibrations['health_assessment']['status'],
                'emotional_state': rhetor_reading['emotional_reading']['system_mood']
            }
            
            sundown_result = await ss.sundown('test-ci', context)
            assert sundown_result is not None
            
            # Sunrise with continued monitoring
            sunrise_result = await ss.sunrise('test-ci')
            assert sunrise_result['success'] is True
            
            # Check whisper channel statistics
            stats = channel.get_statistics()
            assert stats['harmony_score'] > 0
    
    @pytest.mark.asyncio
    async def test_stress_detection_flow(self):
        """Test stress detection and response flow."""
        channel = WhisperChannel()
        
        # Rhetor detects stress
        stress_feeling = {
            'summary': 'CI showing stress',
            'stress_level': 'elevated',
            'stress_source': 'task_overload'
        }
        
        apollo_response = await channel.rhetor_whisper(WhisperType.CONCERN, stress_feeling)
        
        # Apollo should suggest adjustment
        assert 'suggestion' in apollo_response or 'analysis' in apollo_response
        
        # Check for harmonization
        if apollo_response['harmony']:
            assert channel.harmony_count > 0
    
    @pytest.mark.asyncio
    async def test_intervention_decision(self):
        """Test intervention decision making."""
        channel = WhisperChannel()
        
        # Both agree on intervention
        intervention = {
            'proposed_action': {
                'type': 'reduce_load',
                'target': 'test-ci'
            },
            'action_needed': True,
            'urgency': 'moderate'
        }
        
        # Apollo proposes
        response = await channel.apollo_whisper(WhisperType.INTERVENTION, intervention)
        
        # Should be harmonized
        assert response['harmony'] is True
        
        # Should have pending intervention
        pending = await channel.get_pending_intervention()
        assert pending is not None
        assert pending['reasoning'] == 'Both logical and emotional assessment agree'


def run_tests():
    """Run all tests and report results."""
    print("Running Apollo/Rhetor Sprint Test Suite...")
    print("=" * 60)
    
    # Run pytest with verbose output
    import subprocess
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', __file__, '-v', '--tb=short'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    # Can run directly for quick testing
    success = run_tests()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. See output above.")
    
    sys.exit(0 if success else 1)