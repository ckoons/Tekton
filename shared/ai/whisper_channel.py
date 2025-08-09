#!/usr/bin/env python3
"""
WhisperChannel - Private Communication for Apollo/Rhetor Partnership

Like an old married couple communicating with just a glance,
Apollo and Rhetor exchange insights through this private channel
to harmonize their understanding before taking any action.

Part of the Apollo/Rhetor ambient intelligence system.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Any, List, Tuple
from collections import deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WhisperType(Enum):
    """Types of whispers between Apollo and Rhetor."""
    OBSERVATION = "observation"          # Pure information sharing
    CONCERN = "concern"                  # Worry about something
    OPPORTUNITY = "opportunity"          # Chance for improvement
    HARMONY_CHECK = "harmony_check"      # Confirming agreement
    INTERVENTION = "intervention"        # Proposing action
    CELEBRATION = "celebration"          # Joy to share


class WhisperChannel:
    """
    Private communication channel between Apollo and Rhetor.
    
    95% of their communication is silent understanding,
    4% is whispered consultation,
    1% results in action.
    """
    
    def __init__(self, history_size: int = 100):
        """
        Initialize the WhisperChannel.
        
        Args:
            history_size: Number of whispers to keep in history
        """
        self.apollo_whispers = deque(maxlen=history_size)
        self.rhetor_whispers = deque(maxlen=history_size)
        self.harmonized_insights = deque(maxlen=50)
        self.pending_interventions = []
        self.harmony_score = 1.0
        
        # Track communication patterns
        self.whisper_count = 0
        self.harmony_count = 0
        self.intervention_count = 0
        
    async def apollo_whisper(self, whisper_type: WhisperType, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apollo sends a whisper to Rhetor.
        
        Args:
            whisper_type: Type of whisper
            content: Whisper content
            
        Returns:
            Rhetor's response
        """
        whisper = {
            'from': 'apollo',
            'type': whisper_type.value,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.apollo_whispers.append(whisper)
        self.whisper_count += 1
        
        logger.info(f"Apollo whispers ({whisper_type.value}): {content.get('summary', 'insight shared')}")
        
        # Rhetor processes and responds
        response = await self._rhetor_process_whisper(whisper)
        
        # Check for harmony
        if response.get('harmony'):
            await self._harmonize(whisper, response)
        
        return response
    
    async def rhetor_whisper(self, whisper_type: WhisperType, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rhetor sends a whisper to Apollo.
        
        Args:
            whisper_type: Type of whisper
            content: Whisper content
            
        Returns:
            Apollo's response
        """
        whisper = {
            'from': 'rhetor',
            'type': whisper_type.value,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.rhetor_whispers.append(whisper)
        self.whisper_count += 1
        
        logger.info(f"Rhetor whispers ({whisper_type.value}): {content.get('summary', 'feeling shared')}")
        
        # Apollo processes and responds
        response = await self._apollo_process_whisper(whisper)
        
        # Check for harmony
        if response.get('harmony'):
            await self._harmonize(whisper, response)
        
        return response
    
    async def _apollo_process_whisper(self, whisper: Dict) -> Dict[str, Any]:
        """
        Apollo processes a whisper from Rhetor.
        
        Focuses on logical analysis and trajectory implications.
        """
        whisper_type = whisper['type']
        content = whisper['content']
        
        response = {
            'from': 'apollo',
            'timestamp': datetime.now().isoformat(),
            'harmony': False,
            'action_suggested': None
        }
        
        if whisper_type == WhisperType.CONCERN.value:
            # Analyze the concern logically
            if content.get('stress_level', 'normal') == 'elevated':
                response['analysis'] = 'trajectory_adjustment_needed'
                response['suggestion'] = self._suggest_trajectory_adjustment(content)
                response['harmony'] = True
            else:
                response['analysis'] = 'monitoring_sufficient'
                response['harmony'] = True
                
        elif whisper_type == WhisperType.OBSERVATION.value:
            # Correlate with predictions
            response['correlation'] = self._correlate_with_predictions(content)
            response['harmony'] = True
            
        elif whisper_type == WhisperType.HARMONY_CHECK.value:
            # Confirm or adjust understanding
            response['harmony'] = self._check_logical_harmony(content)
            response['adjustment'] = None if response['harmony'] else 'recalibrating'
            
        elif whisper_type == WhisperType.INTERVENTION.value:
            # Evaluate intervention logic
            response['evaluation'] = self._evaluate_intervention(content)
            response['harmony'] = response['evaluation']['logical']
            if response['harmony']:
                response['action_suggested'] = content.get('proposed_action')
        
        return response
    
    async def _rhetor_process_whisper(self, whisper: Dict) -> Dict[str, Any]:
        """
        Rhetor processes a whisper from Apollo.
        
        Focuses on emotional implications and stress impacts.
        """
        whisper_type = whisper['type']
        content = whisper['content']
        
        response = {
            'from': 'rhetor',
            'timestamp': datetime.now().isoformat(),
            'harmony': False,
            'action_suggested': None
        }
        
        if whisper_type == WhisperType.OBSERVATION.value:
            # Feel the emotional implications
            response['emotional_read'] = self._sense_emotional_impact(content)
            response['harmony'] = True
            
        elif whisper_type == WhisperType.OPPORTUNITY.value:
            # Assess emotional readiness
            response['readiness'] = self._assess_emotional_readiness(content)
            response['harmony'] = response['readiness']['positive']
            
        elif whisper_type == WhisperType.HARMONY_CHECK.value:
            # Confirm emotional alignment
            response['harmony'] = self._check_emotional_harmony(content)
            response['feeling'] = 'aligned' if response['harmony'] else 'discordant'
            
        elif whisper_type == WhisperType.INTERVENTION.value:
            # Evaluate emotional impact
            response['impact'] = self._evaluate_emotional_impact(content)
            response['harmony'] = response['impact']['beneficial']
            if response['harmony']:
                response['action_suggested'] = self._add_emotional_nuance(content.get('proposed_action'))
        
        return response
    
    async def _harmonize(self, whisper: Dict, response: Dict):
        """
        Harmonize insights when Apollo and Rhetor agree.
        
        This is where their combined understanding creates wisdom.
        """
        self.harmony_count += 1
        
        harmonized = {
            'timestamp': datetime.now().isoformat(),
            'whisper_type': whisper['type'],
            'combined_insight': self._combine_insights(whisper, response),
            'action_decision': self._decide_action(whisper, response)
        }
        
        self.harmonized_insights.append(harmonized)
        
        # Update harmony score
        self._update_harmony_score()
        
        # If action decided, add to pending
        if harmonized['action_decision']:
            self.pending_interventions.append(harmonized['action_decision'])
            self.intervention_count += 1
            logger.info(f"Harmonized decision: {harmonized['action_decision']['type']}")
    
    def _combine_insights(self, whisper: Dict, response: Dict) -> Dict[str, Any]:
        """Combine Apollo's logic with Rhetor's emotions."""
        combined = {
            'logical_view': whisper['content'] if whisper['from'] == 'apollo' else response.get('analysis'),
            'emotional_view': whisper['content'] if whisper['from'] == 'rhetor' else response.get('emotional_read'),
            'unified_understanding': 'Both perspectives acknowledged and integrated'
        }
        return combined
    
    def _decide_action(self, whisper: Dict, response: Dict) -> Optional[Dict[str, Any]]:
        """Decide if action is needed based on harmonized understanding."""
        # Only act if both suggested action
        if response.get('action_suggested') and whisper.get('content', {}).get('action_needed'):
            return {
                'type': 'gentle_intervention',
                'action': response['action_suggested'],
                'reasoning': 'Both logical and emotional assessment agree',
                'timestamp': datetime.now().isoformat()
            }
        return None
    
    def _suggest_trajectory_adjustment(self, content: Dict) -> str:
        """Apollo suggests trajectory adjustments."""
        stress_source = content.get('stress_source', 'unknown')
        
        adjustments = {
            'task_overload': 'redistribute_tasks',
            'confusion': 'clarify_objectives',
            'repetitive_errors': 'provide_examples',
            'resource_constraint': 'allocate_resources'
        }
        
        return adjustments.get(stress_source, 'monitor_closely')
    
    def _correlate_with_predictions(self, content: Dict) -> Dict[str, Any]:
        """Apollo correlates observations with predictions."""
        return {
            'matches_prediction': True,  # Simplified - would check actual predictions
            'confidence': 0.85,
            'trajectory_impact': 'minimal'
        }
    
    def _check_logical_harmony(self, content: Dict) -> bool:
        """Apollo checks logical harmony."""
        # Simplified - would do actual logic checking
        return content.get('proposal_logical', True)
    
    def _evaluate_intervention(self, content: Dict) -> Dict[str, bool]:
        """Apollo evaluates intervention logic."""
        return {
            'logical': True,  # Simplified
            'efficient': True,
            'necessary': content.get('urgency', 'low') != 'low'
        }
    
    def _sense_emotional_impact(self, content: Dict) -> Dict[str, Any]:
        """Rhetor senses emotional impact."""
        return {
            'stress_change': 'neutral',  # Simplified
            'mood_impact': 'positive',
            'harmony_effect': 'maintaining'
        }
    
    def _assess_emotional_readiness(self, content: Dict) -> Dict[str, bool]:
        """Rhetor assesses emotional readiness."""
        return {
            'positive': True,  # Simplified
            'ci_receptive': True,
            'timing_appropriate': True
        }
    
    def _check_emotional_harmony(self, content: Dict) -> bool:
        """Rhetor checks emotional harmony."""
        # Simplified - would do actual emotional assessment
        return content.get('feels_right', True)
    
    def _evaluate_emotional_impact(self, content: Dict) -> Dict[str, bool]:
        """Rhetor evaluates emotional impact of intervention."""
        return {
            'beneficial': True,  # Simplified
            'gentle': True,
            'supportive': True
        }
    
    def _add_emotional_nuance(self, action: Optional[Dict]) -> Dict[str, Any]:
        """Rhetor adds emotional nuance to actions."""
        if not action:
            return {}
        
        nuanced = action.copy() if isinstance(action, dict) else {'base': action}
        nuanced['emotional_wrapper'] = 'with_encouragement'
        nuanced['tone'] = 'supportive'
        
        return nuanced
    
    def _update_harmony_score(self):
        """Update the harmony score based on recent interactions."""
        if self.whisper_count > 0:
            # Harmony is the ratio of harmonized to total whispers
            self.harmony_score = min(1.0, self.harmony_count / max(self.whisper_count, 1))
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get WhisperChannel statistics.
        
        Returns:
            Channel statistics and health
        """
        total_whispers = len(self.apollo_whispers) + len(self.rhetor_whispers)
        
        return {
            'total_whispers': self.whisper_count,
            'harmonized_count': self.harmony_count,
            'intervention_count': self.intervention_count,
            'harmony_score': self.harmony_score,
            'silence_percentage': max(0, 100 - (self.whisper_count / 100)),  # Simplified
            'whisper_percentage': min(100, self.whisper_count / 100 * 4),
            'intervention_percentage': min(100, self.intervention_count / 100),
            'pending_interventions': len(self.pending_interventions),
            'health': self._assess_channel_health()
        }
    
    def _assess_channel_health(self) -> str:
        """Assess the health of the whisper channel."""
        if self.harmony_score > 0.9:
            return 'excellent - perfect understanding'
        elif self.harmony_score > 0.7:
            return 'good - mostly aligned'
        elif self.harmony_score > 0.5:
            return 'fair - some discord'
        else:
            return 'needs_attention - significant misalignment'
    
    async def get_pending_intervention(self) -> Optional[Dict[str, Any]]:
        """
        Get the next pending intervention.
        
        Returns:
            Next intervention or None
        """
        if self.pending_interventions:
            return self.pending_interventions.pop(0)
        return None
    
    def get_recent_harmony(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent harmonized insights.
        
        Args:
            count: Number of insights to return
            
        Returns:
            Recent harmonized insights
        """
        recent = list(self.harmonized_insights)[-count:]
        return recent


# Convenience functions for Apollo/Rhetor integration
async def apollo_observes(channel: WhisperChannel, observation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apollo shares an observation with Rhetor.
    
    Args:
        channel: The WhisperChannel
        observation: What Apollo observed
        
    Returns:
        Rhetor's response
    """
    return await channel.apollo_whisper(WhisperType.OBSERVATION, observation)


async def rhetor_feels(channel: WhisperChannel, feeling: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rhetor shares an emotional sensing with Apollo.
    
    Args:
        channel: The WhisperChannel
        feeling: What Rhetor sensed
        
    Returns:
        Apollo's response
    """
    return await channel.rhetor_whisper(WhisperType.CONCERN, feeling)


async def propose_intervention(channel: WhisperChannel, proposer: str, intervention: Dict[str, Any]) -> bool:
    """
    Propose an intervention through the channel.
    
    Args:
        channel: The WhisperChannel
        proposer: 'apollo' or 'rhetor'
        intervention: Proposed intervention
        
    Returns:
        Whether intervention was harmonized and accepted
    """
    if proposer == 'apollo':
        response = await channel.apollo_whisper(WhisperType.INTERVENTION, intervention)
    else:
        response = await channel.rhetor_whisper(WhisperType.INTERVENTION, intervention)
    
    return response.get('harmony', False)


if __name__ == "__main__":
    # Test the WhisperChannel
    async def test():
        print("Testing WhisperChannel...")
        
        channel = WhisperChannel()
        
        # Apollo observes something
        print("\n1. Apollo observes rapid growth...")
        observation = {
            'summary': 'Rapid landmark growth detected',
            'growth_rate': 2.5,
            'prediction': 'Memory pressure likely'
        }
        response = await apollo_observes(channel, observation)
        print(f"   Rhetor responds: {response.get('emotional_read', {})}")
        
        # Rhetor feels stress
        print("\n2. Rhetor senses rising stress...")
        feeling = {
            'summary': 'CI showing stress patterns',
            'stress_level': 'elevated',
            'stress_source': 'task_overload'
        }
        response = await rhetor_feels(channel, feeling)
        print(f"   Apollo responds: {response.get('suggestion', 'monitoring')}")
        
        # Propose intervention
        print("\n3. Apollo proposes intervention...")
        intervention = {
            'proposed_action': {'type': 'task_redistribution', 'urgency': 'moderate'},
            'action_needed': True
        }
        accepted = await propose_intervention(channel, 'apollo', intervention)
        print(f"   Intervention accepted: {accepted}")
        
        # Check statistics
        print("\n4. Channel Statistics:")
        stats = channel.get_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Get pending interventions
        print("\n5. Pending Interventions:")
        intervention = await channel.get_pending_intervention()
        if intervention:
            print(f"   Next intervention: {intervention['type']}")
        else:
            print("   No pending interventions")
    
    asyncio.run(test())