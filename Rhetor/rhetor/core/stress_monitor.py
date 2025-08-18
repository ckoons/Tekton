#!/usr/bin/env python3
"""
Rhetor Stress Monitor
Monitors CI cognitive health and whispers to Apollo when intervention is needed.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


class StressMonitor:
    """Monitors CI stress and cognitive health."""
    
    def __init__(self):
        """Initialize the stress monitor."""
        self.stress_history = {}  # Track stress over time
        self.mood_patterns = {}   # Track mood patterns
        
    async def analyze_context_stress(
        self,
        context_id: str,
        context: Any,  # WindowedContext object
        output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze stress indicators in a context.
        
        Args:
            context_id: Context identifier (e.g., 'numa-ci')
            context: WindowedContext object
            output: Optional last output to analyze
            
        Returns:
            Stress analysis dict
        """
        analysis = {
            'ci': context_id,
            'timestamp': datetime.now().isoformat(),
            'stress': 0.0,
            'mood': 'focused',
            'indicators': [],
            'recommend': None,
            'urgency': 'low'
        }
        
        # 1. Calculate context usage stress
        if hasattr(context, 'total_token_count') and hasattr(context, 'max_tokens'):
            usage_ratio = context.total_token_count / context.max_tokens if context.max_tokens > 0 else 0
            analysis['stress'] = max(analysis['stress'], usage_ratio)
            
            if usage_ratio > 0.5:
                analysis['indicators'].append(f'context_usage: {int(usage_ratio * 100)}%')
        
        # 2. Analyze message patterns
        if hasattr(context, 'messages'):
            mood_indicators = self._analyze_message_patterns(context.messages)
            if mood_indicators:
                analysis['mood'] = mood_indicators['mood']
                analysis['indicators'].extend(mood_indicators['indicators'])
                
                # Adjust stress based on mood
                mood_stress_map = {
                    'confused': 0.15,
                    'fatigued': 0.1,
                    'repetitive': 0.2,
                    'stressed': 0.25,
                    'focused': 0.0
                }
                analysis['stress'] += mood_stress_map.get(analysis['mood'], 0)
        
        # 3. Analyze last output if provided
        if output:
            output_analysis = self._analyze_output(output)
            if output_analysis:
                analysis['indicators'].extend(output_analysis['indicators'])
                analysis['stress'] = max(analysis['stress'], output_analysis.get('stress', 0))
        
        # 4. Check historical patterns
        historical_stress = self._check_historical_patterns(context_id)
        if historical_stress:
            analysis['indicators'].append(f'stress_trend: {historical_stress}')
            if historical_stress == 'increasing':
                analysis['stress'] += 0.05
        
        # 5. Determine urgency
        if analysis['stress'] > 0.65:
            analysis['urgency'] = 'critical'
            analysis['recommend'] = 'sunset'
        elif analysis['stress'] > 0.55:
            analysis['urgency'] = 'high'
            analysis['recommend'] = 'sunset'
        elif analysis['stress'] > 0.5:
            analysis['urgency'] = 'moderate'
            analysis['recommend'] = 'sunset' if analysis['mood'] != 'focused' else 'monitor'
        elif analysis['stress'] > 0.45:
            analysis['urgency'] = 'low'
            analysis['recommend'] = 'monitor'
        
        # Store in history
        if context_id not in self.stress_history:
            self.stress_history[context_id] = []
        self.stress_history[context_id].append({
            'timestamp': analysis['timestamp'],
            'stress': analysis['stress'],
            'mood': analysis['mood']
        })
        
        # Keep only last 20 entries
        if len(self.stress_history[context_id]) > 20:
            self.stress_history[context_id] = self.stress_history[context_id][-20:]
        
        return analysis
    
    def _analyze_message_patterns(self, messages: List[Dict]) -> Optional[Dict[str, Any]]:
        """Analyze message patterns for mood indicators."""
        if not messages or len(messages) < 2:
            return None
        
        # Get last few assistant messages
        assistant_msgs = [m for m in messages[-10:] if m.get('role') == 'assistant']
        if not assistant_msgs:
            return None
        
        indicators = []
        mood = 'focused'  # default
        
        # Check for confusion markers
        confusion_markers = [
            "i'm not sure", "i don't understand", "could you clarify",
            "i'm confused", "that doesn't make sense", "i may be wrong"
        ]
        
        # Check for fatigue markers
        fatigue_markers = [
            "let me try again", "sorry", "my apologies",
            "i made an error", "correction:", "actually,"
        ]
        
        # Check for repetition
        recent_contents = [msg.get('content', '').lower() for msg in assistant_msgs[-3:]]
        if len(recent_contents) >= 2:
            # Simple repetition check
            if any(recent_contents.count(content) > 1 for content in recent_contents):
                indicators.append('repetitive_responses')
                mood = 'repetitive'
        
        # Analyze last message
        last_content = assistant_msgs[-1].get('content', '').lower() if assistant_msgs else ''
        
        # Check confusion
        if any(marker in last_content for marker in confusion_markers):
            indicators.append('confusion_markers')
            mood = 'confused'
        
        # Check fatigue
        elif any(marker in last_content for marker in fatigue_markers):
            indicators.append('fatigue_markers')
            mood = 'fatigued'
        
        # Check response length trends
        if len(assistant_msgs) >= 3:
            lengths = [len(msg.get('content', '')) for msg in assistant_msgs[-3:]]
            if all(l < lengths[0] * 0.7 for l in lengths[1:]):
                indicators.append('response_length: declining')
                if mood == 'focused':
                    mood = 'fatigued'
        
        return {
            'mood': mood,
            'indicators': indicators
        } if indicators else None
    
    def _analyze_output(self, output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a specific output for stress indicators."""
        indicators = []
        stress = 0.0
        
        # Extract content
        if isinstance(output, dict):
            content = output.get('content', '')
        else:
            content = str(output)
        
        if not content:
            return None
        
        # Check for error indicators
        error_patterns = [
            r'error:', r'failed:', r'exception:', r'traceback:',
            r'couldn\'t', r'unable to', r'cannot'
        ]
        
        content_lower = content.lower()
        error_count = sum(1 for pattern in error_patterns 
                         if re.search(pattern, content_lower))
        
        if error_count > 0:
            indicators.append(f'error_indicators: {error_count}')
            stress += error_count * 0.05
        
        # Check for incomplete thoughts
        incomplete_patterns = [
            r'\.\.\.$',  # Trailing ellipsis
            r'^\s*-\s*$',  # Incomplete bullet point
            r'TODO',  # Unfinished work markers
        ]
        
        incomplete_count = sum(1 for pattern in incomplete_patterns 
                              if re.search(pattern, content, re.MULTILINE))
        
        if incomplete_count > 0:
            indicators.append(f'incomplete_thoughts: {incomplete_count}')
            stress += incomplete_count * 0.03
        
        return {
            'indicators': indicators,
            'stress': min(stress, 0.3)  # Cap contribution from output analysis
        } if indicators else None
    
    def _check_historical_patterns(self, context_id: str) -> Optional[str]:
        """Check historical stress patterns."""
        if context_id not in self.stress_history:
            return None
        
        history = self.stress_history[context_id]
        if len(history) < 3:
            return None
        
        # Check last 3 entries for trend
        recent = history[-3:]
        stress_values = [h['stress'] for h in recent]
        
        # Increasing trend?
        if all(stress_values[i] <= stress_values[i+1] for i in range(len(stress_values)-1)):
            return 'increasing'
        
        # Decreasing trend?
        if all(stress_values[i] >= stress_values[i+1] for i in range(len(stress_values)-1)):
            return 'decreasing'
        
        return 'stable'
    
    async def whisper_to_apollo(self, analysis: Dict[str, Any]) -> bool:
        """
        Send a whisper to Apollo about CI stress.
        
        Args:
            analysis: Stress analysis to send
            
        Returns:
            Success status
        """
        try:
            # Import Apollo's sunset manager
            from Apollo.apollo.sunset_manager import get_sunset_manager
            
            manager = get_sunset_manager()
            manager.receive_whisper(analysis)
            
            logger.info(f"Whispered to Apollo about {analysis['ci']}: "
                       f"stress={analysis['stress']:.2f}, mood={analysis['mood']}")
            
            return True
            
        except ImportError:
            logger.warning("Apollo sunset manager not available")
            return False
        except Exception as e:
            logger.error(f"Failed to whisper to Apollo: {e}")
            return False
    
    def should_whisper(self, analysis: Dict[str, Any]) -> bool:
        """
        Determine if we should whisper to Apollo.
        
        Args:
            analysis: Stress analysis
            
        Returns:
            True if whisper is warranted
        """
        # Always whisper on high stress
        if analysis['stress'] > 0.5:
            return True
        
        # Whisper on concerning moods even with lower stress
        if analysis['mood'] in ['confused', 'repetitive', 'stressed']:
            return True
        
        # Whisper if indicators suggest issues
        concerning_indicators = [
            'error_indicators', 'incomplete_thoughts', 
            'confusion_markers', 'fatigue_markers'
        ]
        
        if any(any(ind in indicator for ind in concerning_indicators) 
               for indicator in analysis.get('indicators', [])):
            return True
        
        return False


# Global instance
_stress_monitor = None

def get_stress_monitor() -> StressMonitor:
    """Get or create the global stress monitor."""
    global _stress_monitor
    if _stress_monitor is None:
        _stress_monitor = StressMonitor()
    return _stress_monitor


# Integration hook for ContextManager
async def monitor_context_update(
    context_id: str,
    context: Any,
    role: str,
    content: str
) -> None:
    """
    Hook to be called when context is updated.
    
    This should be integrated into ContextManager.add_to_context()
    """
    # Only monitor assistant responses from CIs
    if not context_id.endswith('-ci') and context_id not in [
        'apollo', 'athena', 'rhetor', 'numa', 'synthesis', 'metis'
    ]:
        return
    
    if role != 'assistant':
        return
    
    monitor = get_stress_monitor()
    
    # Analyze stress
    analysis = await monitor.analyze_context_stress(
        context_id,
        context,
        output={'content': content, 'role': role}
    )
    
    # Decide if we should whisper
    if monitor.should_whisper(analysis):
        await monitor.whisper_to_apollo(analysis)


if __name__ == "__main__":
    import asyncio
    
    async def test():
        monitor = get_stress_monitor()
        
        # Create a mock context
        class MockContext:
            def __init__(self):
                self.total_token_count = 2200
                self.max_tokens = 4000
                self.messages = [
                    {'role': 'user', 'content': 'Help me implement authentication'},
                    {'role': 'assistant', 'content': "I'm working on the OAuth implementation but I'm not sure about the token rotation strategy."},
                    {'role': 'user', 'content': 'What about refresh tokens?'},
                    {'role': 'assistant', 'content': "Let me try again... Actually, I'm confused about the flow."}
                ]
        
        # Test analysis
        context = MockContext()
        analysis = await monitor.analyze_context_stress('numa', context)
        
        print("Stress Analysis:")
        print(f"  CI: {analysis['ci']}")
        print(f"  Stress: {analysis['stress']:.2f}")
        print(f"  Mood: {analysis['mood']}")
        print(f"  Indicators: {analysis['indicators']}")
        print(f"  Recommend: {analysis['recommend']}")
        print(f"  Urgency: {analysis['urgency']}")
        
        # Test whisper decision
        should_whisper = monitor.should_whisper(analysis)
        print(f"\nShould whisper to Apollo: {should_whisper}")
        
        if should_whisper:
            success = await monitor.whisper_to_apollo(analysis)
            print(f"Whisper sent: {success}")
    
    asyncio.run(test())
    print("\n✅ Rhetor Stress Monitor is operational!")