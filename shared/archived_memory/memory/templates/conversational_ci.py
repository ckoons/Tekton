"""
Memory Template for Conversational CIs
Optimized for chat-based interactions and dialogue management.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from ..middleware import (
    MemoryConfig,
    InjectionStyle,
    MemoryTier
)
from ..decorators import (
    with_memory,
    memory_aware,
    memory_context
)


@dataclass
class ConversationalMemoryTemplate:
    """
    Memory template for conversational CIs like Hermes, Rhetor.
    
    Features:
    - Recent conversation history
    - Session continuity
    - User preferences tracking
    - Natural language injection
    """
    
    # Default configuration
    config = MemoryConfig(
        namespace="conversational",
        injection_style=InjectionStyle.NATURAL,
        memory_tiers=[
            MemoryTier.RECENT,      # Last 10-20 messages
            MemoryTier.SESSION,     # Current session context
            MemoryTier.ASSOCIATIONS # Related past conversations
        ],
        store_inputs=True,
        store_outputs=True,
        inject_context=True,
        context_depth=20,
        relevance_threshold=0.6,
        max_context_size=1500,
        enable_collective=False,
        performance_sla_ms=150
    )
    
    # Decorator presets
    decorators = {
        'message_handler': 'conversational_message',
        'context_retrieval': 'conversation_context',
        'session_management': 'session_memory',
        'preference_learning': 'user_preferences'
    }
    
    # Memory patterns
    patterns = {
        'greeting': {
            'tiers': [MemoryTier.SESSION],
            'depth': 5,
            'style': InjectionStyle.MINIMAL
        },
        'question_answering': {
            'tiers': [MemoryTier.RECENT, MemoryTier.DOMAIN],
            'depth': 15,
            'style': InjectionStyle.NATURAL
        },
        'storytelling': {
            'tiers': [MemoryTier.SESSION, MemoryTier.ASSOCIATIONS],
            'depth': 25,
            'style': InjectionStyle.CREATIVE
        },
        'clarification': {
            'tiers': [MemoryTier.RECENT],
            'depth': 10,
            'style': InjectionStyle.STRUCTURED
        }
    }


# Decorator implementations for conversational CIs

def conversational_message(func):
    """Decorator for handling conversational messages."""
    return with_memory(
        namespace="conversation",
        memory_tiers=[MemoryTier.RECENT, MemoryTier.SESSION],
        injection_style=InjectionStyle.NATURAL,
        context_depth=15,
        store_inputs=True,
        store_outputs=True
    )(func)


def conversation_context(func):
    """Decorator for retrieving conversation context."""
    return memory_context(
        context_type="conversation",
        lookback_window="30_minutes",
        include_associations=True,
        semantic_clustering=False
    )(func)


def session_memory(func):
    """Decorator for session management."""
    return with_memory(
        namespace="session",
        memory_tiers=[MemoryTier.SESSION],
        injection_style=InjectionStyle.MINIMAL,
        context_depth=10,
        store_inputs=True,
        store_outputs=False
    )(func)


def user_preferences(func):
    """Decorator for learning user preferences."""
    return with_memory(
        namespace="preferences",
        memory_tiers=[MemoryTier.DOMAIN],
        injection_style=InjectionStyle.STRUCTURED,
        store_inputs=False,
        store_outputs=True,
        relevance_threshold=0.8
    )(func)


# Example usage class

class ConversationalCI:
    """Example implementation of a conversational CI with memory."""
    
    def __init__(self, ci_name: str):
        self.ci_name = ci_name
        self.template = ConversationalMemoryTemplate()
        self.memory_context = None
    
    @conversational_message
    async def handle_message(self, message: str, user: str) -> str:
        """
        Handle incoming message with automatic memory.
        
        Memory context is automatically injected and response stored.
        """
        # Access injected memory context
        context = self.memory_context
        
        # Use recent conversation history
        recent_messages = context.recent if context else []
        
        # Generate response based on context
        response = await self._generate_response(message, recent_messages)
        
        return response
    
    @conversation_context
    async def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation with context."""
        context = self.memory_context
        
        return {
            'message_count': len(context.recent) if context else 0,
            'session_duration': self._calculate_session_duration(context),
            'topics': self._extract_topics(context),
            'sentiment': self._analyze_sentiment(context)
        }
    
    @user_preferences
    async def learn_preference(self, preference_type: str, value: Any):
        """Learn and store user preference."""
        # This will automatically store the preference
        return {
            'type': preference_type,
            'value': value,
            'learned_at': 'now'
        }
    
    async def _generate_response(self, message: str, context: List) -> str:
        """Generate response based on message and context."""
        # Placeholder for actual response generation
        return f"Response to: {message}"
    
    def _calculate_session_duration(self, context) -> str:
        """Calculate current session duration."""
        # Placeholder implementation
        return "15 minutes"
    
    def _extract_topics(self, context) -> List[str]:
        """Extract topics from conversation context."""
        # Placeholder implementation
        return ["greeting", "weather", "assistance"]
    
    def _analyze_sentiment(self, context) -> str:
        """Analyze conversation sentiment."""
        # Placeholder implementation
        return "positive"


# Configuration builder

def create_conversational_config(
    ci_name: str,
    **overrides
) -> MemoryConfig:
    """
    Create memory configuration for a conversational CI.
    
    Args:
        ci_name: Name of the CI
        **overrides: Configuration overrides
        
    Returns:
        Configured MemoryConfig
    """
    base_config = ConversationalMemoryTemplate.config
    
    # Apply overrides
    config_dict = {
        'namespace': ci_name,
        'injection_style': base_config.injection_style,
        'memory_tiers': base_config.memory_tiers,
        'store_inputs': base_config.store_inputs,
        'store_outputs': base_config.store_outputs,
        'inject_context': base_config.inject_context,
        'context_depth': base_config.context_depth,
        'relevance_threshold': base_config.relevance_threshold,
        'max_context_size': base_config.max_context_size,
        'enable_collective': base_config.enable_collective,
        'performance_sla_ms': base_config.performance_sla_ms
    }
    
    config_dict.update(overrides)
    
    return MemoryConfig(**config_dict)