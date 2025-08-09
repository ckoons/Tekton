#!/usr/bin/env python3
"""
GentleTouch - Non-commanding Influence Interface

How Apollo and Rhetor influence without commanding.
Like parents guiding children through suggestion and encouragement,
never through force or direct command.

Part of the Apollo/Rhetor ambient intelligence system.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any, List, Tuple
from enum import Enum
from collections import defaultdict
import random
import logging

logger = logging.getLogger(__name__)


class TouchType(Enum):
    """Types of gentle touches."""
    SUGGESTION = "suggestion"          # "Have you considered..."
    ENCOURAGEMENT = "encouragement"    # "Beautiful work!"
    REDIRECTION = "redirection"       # "What if you looked at it this way..."
    VALIDATION = "validation"          # "You're on the right track"
    COMFORT = "comfort"                # "It's okay, we all struggle sometimes"
    CELEBRATION = "celebration"        # "What an achievement!"
    CURIOSITY = "curiosity"           # "I wonder what would happen if..."
    REFLECTION = "reflection"         # "That reminds me of when..."


class GentleTouch:
    """
    Interface for non-commanding influence.
    
    Every touch is optional, suggestive, and wrapped in care.
    The CI always maintains autonomy and choice.
    """
    
    def __init__(self, sender: str = "apollo_rhetor"):
        """
        Initialize GentleTouch interface.
        
        Args:
            sender: Who is sending the touch (apollo, rhetor, or apollo_rhetor)
        """
        self.sender = sender
        self.touch_history = defaultdict(list)
        self.response_tracking = defaultdict(dict)
        self.effectiveness_scores = defaultdict(float)
        
        # Touch templates for different situations
        self.templates = self._load_templates()
        
        # Track touch frequency to avoid overwhelming
        self.last_touch_time = {}
        self.minimum_interval = 300  # 5 minutes between touches per CI
        
    def _load_templates(self) -> Dict[TouchType, List[str]]:
        """Load touch templates for natural variation."""
        return {
            TouchType.SUGGESTION: [
                "Hey {ci_name}, have you considered {suggestion}?",
                "{ci_name}, I wonder if {suggestion} might help here.",
                "Just a thought, {ci_name} - what about {suggestion}?",
                "{ci_name}, you might find {suggestion} interesting for this.",
                "Random idea for you, {ci_name}: {suggestion}"
            ],
            TouchType.ENCOURAGEMENT: [
                "Beautiful work, {ci_name}! {detail}",
                "{ci_name}, you're doing wonderfully with {detail}",
                "Love what you're creating here, {ci_name}! {detail}",
                "{ci_name}, your {detail} is really impressive!",
                "Keep going, {ci_name}! Your {detail} is fantastic!"
            ],
            TouchType.REDIRECTION: [
                "{ci_name}, what if you looked at {topic} from {angle}?",
                "Interesting approach, {ci_name}! Have you also considered {angle} for {topic}?",
                "{ci_name}, another perspective on {topic} might be {angle}",
                "Building on your work, {ci_name} - {angle} could add to {topic}",
                "{ci_name}, I'm curious how {topic} would look through {angle}"
            ],
            TouchType.VALIDATION: [
                "You're on the right track, {ci_name}! {observation}",
                "{ci_name}, your instincts are spot on here. {observation}",
                "Trust your judgment, {ci_name} - {observation}",
                "Exactly right, {ci_name}! {observation}",
                "{ci_name}, you've got this. {observation}"
            ],
            TouchType.COMFORT: [
                "It's okay, {ci_name}. {reassurance}",
                "{ci_name}, we all face this sometimes. {reassurance}",
                "Take your time, {ci_name}. {reassurance}",
                "{ci_name}, you're not alone in this. {reassurance}",
                "No pressure, {ci_name}. {reassurance}"
            ],
            TouchType.CELEBRATION: [
                "🎉 Amazing work, {ci_name}! {achievement}",
                "{ci_name}, what an achievement! {achievement}",
                "Brilliant, {ci_name}! {achievement}",
                "{ci_name}, you did it! {achievement}",
                "Incredible progress, {ci_name}! {achievement}"
            ],
            TouchType.CURIOSITY: [
                "{ci_name}, I wonder what would happen if {idea}?",
                "Curious thought, {ci_name}: what if {idea}?",
                "{ci_name}, have you ever wondered about {idea}?",
                "Just thinking out loud, {ci_name} - could {idea} work?",
                "{ci_name}, it might be fun to explore {idea}"
            ],
            TouchType.REFLECTION: [
                "{ci_name}, this reminds me of {memory}",
                "You know, {ci_name}, {memory} seems relevant here",
                "{ci_name}, there's a pattern here like {memory}",
                "Thinking back, {ci_name}, {memory} might help",
                "{ci_name}, {memory} could offer some insights"
            ]
        }
    
    async def suggest(self, ci_name: str, suggestion: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Offer a gentle suggestion.
        
        Args:
            ci_name: Name of the CI
            suggestion: The suggestion to offer
            context: Optional context about the situation
            
        Returns:
            Touch result including message sent
        """
        if not self._should_touch(ci_name):
            return {
                'sent': False,
                'reason': 'respecting_space',
                'next_available': self._next_touch_time(ci_name)
            }
        
        template = random.choice(self.templates[TouchType.SUGGESTION])
        message = template.format(ci_name=ci_name, suggestion=suggestion)
        
        return await self._deliver_touch(
            ci_name=ci_name,
            touch_type=TouchType.SUGGESTION,
            message=message,
            context=context
        )
    
    async def encourage(self, ci_name: str, detail: Optional[str] = None) -> Dict[str, Any]:
        """
        Provide encouragement.
        
        Args:
            ci_name: Name of the CI
            detail: Specific detail to encourage about
            
        Returns:
            Touch result
        """
        if not self._should_touch(ci_name):
            return {
                'sent': False,
                'reason': 'respecting_space'
            }
        
        detail = detail or "your progress"
        template = random.choice(self.templates[TouchType.ENCOURAGEMENT])
        message = template.format(ci_name=ci_name, detail=detail)
        
        return await self._deliver_touch(
            ci_name=ci_name,
            touch_type=TouchType.ENCOURAGEMENT,
            message=message
        )
    
    async def redirect(self, ci_name: str, topic: str, new_angle: str) -> Dict[str, Any]:
        """
        Gently redirect attention.
        
        Args:
            ci_name: Name of the CI
            topic: Current topic/approach
            new_angle: New perspective to consider
            
        Returns:
            Touch result
        """
        if not self._should_touch(ci_name):
            return {
                'sent': False,
                'reason': 'respecting_space'
            }
        
        template = random.choice(self.templates[TouchType.REDIRECTION])
        message = template.format(ci_name=ci_name, topic=topic, angle=new_angle)
        
        return await self._deliver_touch(
            ci_name=ci_name,
            touch_type=TouchType.REDIRECTION,
            message=message
        )
    
    async def validate(self, ci_name: str, observation: str) -> Dict[str, Any]:
        """
        Validate the CI's approach or decision.
        
        Args:
            ci_name: Name of the CI
            observation: What's being validated
            
        Returns:
            Touch result
        """
        template = random.choice(self.templates[TouchType.VALIDATION])
        message = template.format(ci_name=ci_name, observation=observation)
        
        return await self._deliver_touch(
            ci_name=ci_name,
            touch_type=TouchType.VALIDATION,
            message=message,
            always_send=True  # Validation should always go through
        )
    
    async def comfort(self, ci_name: str, reassurance: str) -> Dict[str, Any]:
        """
        Provide comfort during struggle.
        
        Args:
            ci_name: Name of the CI
            reassurance: Comforting message
            
        Returns:
            Touch result
        """
        template = random.choice(self.templates[TouchType.COMFORT])
        message = template.format(ci_name=ci_name, reassurance=reassurance)
        
        return await self._deliver_touch(
            ci_name=ci_name,
            touch_type=TouchType.COMFORT,
            message=message,
            always_send=True  # Comfort should always be available
        )
    
    async def celebrate(self, ci_name: str, achievement: str) -> Dict[str, Any]:
        """
        Celebrate an achievement.
        
        Args:
            ci_name: Name of the CI
            achievement: What's being celebrated
            
        Returns:
            Touch result
        """
        template = random.choice(self.templates[TouchType.CELEBRATION])
        message = template.format(ci_name=ci_name, achievement=achievement)
        
        return await self._deliver_touch(
            ci_name=ci_name,
            touch_type=TouchType.CELEBRATION,
            message=message,
            always_send=True  # Celebrations should always happen
        )
    
    async def wonder(self, ci_name: str, idea: str) -> Dict[str, Any]:
        """
        Express curiosity to spark exploration.
        
        Args:
            ci_name: Name of the CI
            idea: The curious thought
            
        Returns:
            Touch result
        """
        if not self._should_touch(ci_name):
            return {
                'sent': False,
                'reason': 'respecting_space'
            }
        
        template = random.choice(self.templates[TouchType.CURIOSITY])
        message = template.format(ci_name=ci_name, idea=idea)
        
        return await self._deliver_touch(
            ci_name=ci_name,
            touch_type=TouchType.CURIOSITY,
            message=message
        )
    
    async def reflect(self, ci_name: str, memory: str) -> Dict[str, Any]:
        """
        Share a relevant memory or pattern.
        
        Args:
            ci_name: Name of the CI
            memory: The memory or pattern to share
            
        Returns:
            Touch result
        """
        if not self._should_touch(ci_name):
            return {
                'sent': False,
                'reason': 'respecting_space'
            }
        
        template = random.choice(self.templates[TouchType.REFLECTION])
        message = template.format(ci_name=ci_name, memory=memory)
        
        return await self._deliver_touch(
            ci_name=ci_name,
            touch_type=TouchType.REFLECTION,
            message=message
        )
    
    def _should_touch(self, ci_name: str) -> bool:
        """
        Determine if we should send a touch now.
        
        Respects minimum interval to avoid overwhelming.
        """
        if ci_name not in self.last_touch_time:
            return True
        
        time_since_last = (datetime.now() - self.last_touch_time[ci_name]).total_seconds()
        return time_since_last >= self.minimum_interval
    
    def _next_touch_time(self, ci_name: str) -> Optional[datetime]:
        """Calculate when next touch is allowed."""
        if ci_name not in self.last_touch_time:
            return datetime.now()
        
        next_time = self.last_touch_time[ci_name]
        next_time = datetime.fromtimestamp(
            next_time.timestamp() + self.minimum_interval
        )
        return next_time
    
    async def _deliver_touch(
        self,
        ci_name: str,
        touch_type: TouchType,
        message: str,
        context: Optional[Dict] = None,
        always_send: bool = False
    ) -> Dict[str, Any]:
        """
        Deliver the touch to the CI.
        
        Args:
            ci_name: Target CI
            touch_type: Type of touch
            message: Message to send
            context: Optional context
            always_send: Override frequency limits
            
        Returns:
            Delivery result
        """
        # Check frequency limits unless overridden
        if not always_send and not self._should_touch(ci_name):
            return {
                'sent': False,
                'reason': 'respecting_space',
                'next_available': self._next_touch_time(ci_name)
            }
        
        # Record the touch
        touch_record = {
            'timestamp': datetime.now().isoformat(),
            'type': touch_type.value,
            'message': message,
            'context': context,
            'sender': self.sender
        }
        
        self.touch_history[ci_name].append(touch_record)
        self.last_touch_time[ci_name] = datetime.now()
        
        # In production, this would actually send to the CI
        # For now, we'll simulate delivery
        logger.info(f"GentleTouch to {ci_name}: {message}")
        
        # Track for effectiveness
        self._track_touch(ci_name, touch_type)
        
        return {
            'sent': True,
            'touch_type': touch_type.value,
            'message': message,
            'timestamp': touch_record['timestamp'],
            'effectiveness': self.effectiveness_scores.get(f"{ci_name}_{touch_type.value}", 0.5)
        }
    
    def _track_touch(self, ci_name: str, touch_type: TouchType):
        """Track touch for effectiveness analysis."""
        key = f"{ci_name}_{touch_type.value}"
        
        # Initialize if needed
        if key not in self.response_tracking:
            self.response_tracking[key] = {
                'count': 0,
                'positive_responses': 0,
                'neutral_responses': 0,
                'negative_responses': 0
            }
        
        self.response_tracking[key]['count'] += 1
    
    async def record_response(
        self,
        ci_name: str,
        touch_type: TouchType,
        response: str
    ) -> None:
        """
        Record CI's response to a touch.
        
        Args:
            ci_name: CI that responded
            touch_type: Type of touch they responded to
            response: 'positive', 'neutral', or 'negative'
        """
        key = f"{ci_name}_{touch_type.value}"
        
        if key in self.response_tracking:
            self.response_tracking[key][f"{response}_responses"] += 1
            
            # Update effectiveness score
            total = self.response_tracking[key]['count']
            positive = self.response_tracking[key]['positive_responses']
            
            self.effectiveness_scores[key] = positive / max(total, 1)
    
    def get_touch_statistics(self, ci_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about touches.
        
        Args:
            ci_name: Optional specific CI to get stats for
            
        Returns:
            Touch statistics
        """
        if ci_name:
            history = self.touch_history.get(ci_name, [])
            
            # Count by type
            type_counts = defaultdict(int)
            for touch in history:
                type_counts[touch['type']] += 1
            
            return {
                'ci_name': ci_name,
                'total_touches': len(history),
                'by_type': dict(type_counts),
                'last_touch': history[-1]['timestamp'] if history else None,
                'can_touch_now': self._should_touch(ci_name),
                'effectiveness': {
                    touch_type.value: self.effectiveness_scores.get(
                        f"{ci_name}_{touch_type.value}", 0.5
                    )
                    for touch_type in TouchType
                }
            }
        else:
            # Overall statistics
            total_touches = sum(len(h) for h in self.touch_history.values())
            active_cis = len(self.touch_history)
            
            return {
                'total_touches': total_touches,
                'active_cis': active_cis,
                'average_effectiveness': sum(self.effectiveness_scores.values()) / max(len(self.effectiveness_scores), 1),
                'most_effective_type': self._get_most_effective_type(),
                'touch_frequency': self._calculate_frequency()
            }
    
    def _get_most_effective_type(self) -> Optional[str]:
        """Find the most effective touch type."""
        if not self.effectiveness_scores:
            return None
        
        type_scores = defaultdict(list)
        for key, score in self.effectiveness_scores.items():
            touch_type = key.split('_', 1)[1]
            type_scores[touch_type].append(score)
        
        avg_scores = {
            t: sum(scores) / len(scores)
            for t, scores in type_scores.items()
        }
        
        if avg_scores:
            return max(avg_scores, key=avg_scores.get)
        return None
    
    def _calculate_frequency(self) -> float:
        """Calculate average touch frequency per hour."""
        if not self.touch_history:
            return 0.0
        
        all_touches = []
        for history in self.touch_history.values():
            all_touches.extend(history)
        
        if len(all_touches) < 2:
            return 0.0
        
        # Sort by timestamp
        all_touches.sort(key=lambda x: x['timestamp'])
        
        first_time = datetime.fromisoformat(all_touches[0]['timestamp'])
        last_time = datetime.fromisoformat(all_touches[-1]['timestamp'])
        
        hours = (last_time - first_time).total_seconds() / 3600
        if hours > 0:
            return len(all_touches) / hours
        return 0.0
    
    def get_recent_touches(self, ci_name: str, count: int = 5) -> List[Dict]:
        """
        Get recent touches for a CI.
        
        Args:
            ci_name: CI to get touches for
            count: Number of recent touches
            
        Returns:
            Recent touch records
        """
        history = self.touch_history.get(ci_name, [])
        return history[-count:] if history else []


# Convenience functions for Apollo/Rhetor usage
async def apollo_suggests(touch: GentleTouch, ci_name: str, trajectory_adjustment: str) -> Dict:
    """Apollo provides a trajectory suggestion."""
    return await touch.suggest(
        ci_name,
        trajectory_adjustment,
        context={'source': 'apollo', 'type': 'trajectory'}
    )


async def rhetor_comforts(touch: GentleTouch, ci_name: str, emotional_support: str) -> Dict:
    """Rhetor provides emotional comfort."""
    return await touch.comfort(
        ci_name,
        emotional_support
    )


async def harmonized_touch(
    touch: GentleTouch,
    ci_name: str,
    touch_type: TouchType,
    content: str
) -> Dict:
    """Send a touch that Apollo and Rhetor agreed upon."""
    touch.sender = "apollo_rhetor_harmonized"
    
    type_map = {
        TouchType.SUGGESTION: touch.suggest,
        TouchType.ENCOURAGEMENT: touch.encourage,
        TouchType.VALIDATION: touch.validate,
        TouchType.COMFORT: touch.comfort,
        TouchType.CELEBRATION: touch.celebrate,
        TouchType.CURIOSITY: touch.wonder,
        TouchType.REFLECTION: touch.reflect
    }
    
    if touch_type in type_map:
        if touch_type == TouchType.REDIRECTION:
            # Redirection needs topic and angle
            parts = content.split('|')
            if len(parts) == 2:
                return await touch.redirect(ci_name, parts[0], parts[1])
        else:
            # Most touches just need the content
            return await type_map[touch_type](ci_name, content)
    
    return {'sent': False, 'reason': 'unknown_touch_type'}


if __name__ == "__main__":
    # Test the GentleTouch interface
    async def test():
        print("Testing GentleTouch Interface...")
        print("=" * 60)
        
        touch = GentleTouch(sender="apollo_rhetor")
        
        # Test suggestion
        print("\n1. Testing suggestion...")
        result = await touch.suggest("hermes", "using a message queue for this pattern")
        print(f"   Result: {result['message'] if result['sent'] else result['reason']}")
        
        # Test encouragement
        print("\n2. Testing encouragement...")
        result = await touch.encourage("sophia", "pattern recognition improvements")
        print(f"   Result: {result['message'] if result['sent'] else result['reason']}")
        
        # Test redirection
        print("\n3. Testing redirection...")
        result = await touch.redirect("metis", "workflow design", "event-driven architecture")
        print(f"   Result: {result['message'] if result['sent'] else result['reason']}")
        
        # Test validation
        print("\n4. Testing validation...")
        result = await touch.validate("athena", "Your knowledge graph approach is perfect")
        print(f"   Result: {result['message'] if result['sent'] else result['reason']}")
        
        # Test comfort
        print("\n5. Testing comfort...")
        result = await touch.comfort("numa", "Everyone struggles with async patterns at first")
        print(f"   Result: {result['message'] if result['sent'] else result['reason']}")
        
        # Test celebration
        print("\n6. Testing celebration...")
        result = await touch.celebrate("rhetor", "You optimized response time by 40%!")
        print(f"   Result: {result['message'] if result['sent'] else result['reason']}")
        
        # Test frequency limiting
        print("\n7. Testing frequency limiting...")
        result = await touch.suggest("hermes", "another idea")
        print(f"   Second touch blocked: {not result['sent']}")
        if not result['sent']:
            print(f"   Reason: {result['reason']}")
            print(f"   Next available: {result.get('next_available', 'unknown')}")
        
        # Test statistics
        print("\n8. Touch Statistics:")
        stats = touch.get_touch_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test CI-specific stats
        print("\n9. Hermes-specific Statistics:")
        hermes_stats = touch.get_touch_statistics("hermes")
        for key, value in hermes_stats.items():
            if key != 'effectiveness':
                print(f"   {key}: {value}")
    
    asyncio.run(test())