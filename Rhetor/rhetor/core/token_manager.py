"""
Token Manager for Rhetor - Intelligent Token Budget Management.

This module provides sophisticated token tracking and management for CI conversations,
preventing token limit errors and enabling graceful context management.
"""

import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path
import tiktoken

from shared.env import TektonEnviron

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Manages token budgets and usage tracking for CIs.
    
    Provides proactive token management to prevent hitting model limits
    and triggers sundown procedures when approaching capacity.
    """
    
    # Model context windows (approximate)
    MODEL_LIMITS = {
        # Anthropic models
        'claude-3-opus': 200000,
        'claude-3-sonnet': 200000,
        'claude-3-5-sonnet': 200000,
        'claude-3-haiku': 200000,
        'claude-3-5-haiku': 200000,
        'claude-opus-4': 200000,
        
        # OpenAI models
        'gpt-4': 8192,
        'gpt-4-32k': 32768,
        'gpt-4-turbo': 128000,
        'gpt-4o': 128000,
        'gpt-3.5-turbo': 16385,
        
        # Local models (Ollama)
        'llama2': 4096,
        'llama3': 8192,
        'mixtral': 32768,
        'qwen': 32768,
        
        # Default fallback
        'default': 4096
    }
    
    # Budget allocations (percentages of total)
    BUDGET_RATIOS = {
        'system_prompt': 0.05,      # 5% for system prompt
        'conversation_history': 0.40,  # 40% for conversation history
        'buffered_messages': 0.10,   # 10% for buffered messages
        'working_context': 0.30,     # 30% for working context
        'response_buffer': 0.15      # 15% reserved for response
    }
    
    def __init__(self):
        """Initialize the token manager."""
        self.usage_tracker: Dict[str, Dict[str, Any]] = {}
        self.token_counters: Dict[str, Any] = {}  # Cache token counters by encoding
        self.sundown_thresholds = {
            'warning': 0.60,    # 60% - start warning
            'suggest': 0.75,    # 75% - suggest sundown
            'auto': 0.85,       # 85% - auto sundown
            'critical': 0.95    # 95% - forced sundown
        }
        
    def get_token_counter(self, model: str = 'gpt-3.5-turbo') -> tiktoken.Encoding:
        """
        Get or create a token counter for the specified model.
        
        Args:
            model: Model name for tokenization
            
        Returns:
            Tiktoken encoding for the model
        """
        if model not in self.token_counters:
            try:
                # Try to get encoding for specific model
                if 'claude' in model.lower():
                    # Claude uses similar tokenization to GPT
                    self.token_counters[model] = tiktoken.get_encoding('cl100k_base')
                else:
                    self.token_counters[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to cl100k_base for unknown models
                self.token_counters[model] = tiktoken.get_encoding('cl100k_base')
                
        return self.token_counters[model]
    
    def count_tokens(self, text: str, model: str = 'gpt-3.5-turbo') -> int:
        """
        Count tokens in text for the specified model.
        
        Args:
            text: Text to count tokens for
            model: Model to use for tokenization
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
            
        encoder = self.get_token_counter(model)
        return len(encoder.encode(text))
    
    def get_model_limit(self, model: str) -> int:
        """
        Get the context window limit for a model.
        
        Args:
            model: Model name
            
        Returns:
            Context window size in tokens
        """
        # Check for exact match first
        if model in self.MODEL_LIMITS:
            return self.MODEL_LIMITS[model]
            
        # Check for partial matches
        model_lower = model.lower()
        for key, limit in self.MODEL_LIMITS.items():
            if key in model_lower or model_lower in key:
                return limit
                
        # Default fallback
        return self.MODEL_LIMITS['default']
    
    def calculate_budgets(self, model: str) -> Dict[str, int]:
        """
        Calculate token budgets for different components.
        
        Args:
            model: Model name
            
        Returns:
            Dictionary of component budgets in tokens
        """
        total_limit = self.get_model_limit(model)
        budgets = {}
        
        for component, ratio in self.BUDGET_RATIOS.items():
            budgets[component] = int(total_limit * ratio)
            
        return budgets
    
    def init_ci_tracking(self, ci_name: str, model: str):
        """
        Initialize tracking for a CI.
        
        Args:
            ci_name: Name of the CI
            model: Model being used
        """
        self.usage_tracker[ci_name] = {
            'model': model,
            'budgets': self.calculate_budgets(model),
            'usage': {
                'system_prompt': 0,
                'conversation_history': 0,
                'buffered_messages': 0,
                'working_context': 0,
                'total': 0
            },
            'start_time': datetime.now(),
            'message_count': 0,
            'last_update': datetime.now()
        }
    
    def update_usage(self, ci_name: str, component: str, text: str) -> int:
        """
        Update token usage for a CI component.
        
        Args:
            ci_name: Name of the CI
            component: Component name (e.g., 'system_prompt')
            text: Text being added
            
        Returns:
            New token count for the component
        """
        if ci_name not in self.usage_tracker:
            logger.warning(f"CI {ci_name} not initialized in token tracker")
            return 0
            
        tracker = self.usage_tracker[ci_name]
        model = tracker['model']
        
        # Count tokens
        tokens = self.count_tokens(text, model)
        
        # Update usage
        tracker['usage'][component] = tokens
        tracker['usage']['total'] = sum(
            v for k, v in tracker['usage'].items() 
            if k != 'total'
        )
        tracker['last_update'] = datetime.now()
        
        return tokens
    
    def get_usage_percentage(self, ci_name: str) -> float:
        """
        Get current usage percentage for a CI.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Usage percentage (0.0 to 1.0)
        """
        if ci_name not in self.usage_tracker:
            return 0.0
            
        tracker = self.usage_tracker[ci_name]
        model_limit = self.get_model_limit(tracker['model'])
        
        return tracker['usage']['total'] / model_limit
    
    def should_sundown(self, ci_name: str) -> Tuple[bool, str]:
        """
        Check if a CI should enter sundown.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Tuple of (should_sundown, reason)
        """
        if ci_name not in self.usage_tracker:
            return False, "Not tracking"
            
        usage_pct = self.get_usage_percentage(ci_name)
        tracker = self.usage_tracker[ci_name]
        
        # Check critical threshold
        if usage_pct >= self.sundown_thresholds['critical']:
            return True, f"Critical: {usage_pct:.1%} token usage"
            
        # Check auto threshold
        if usage_pct >= self.sundown_thresholds['auto']:
            return True, f"Auto-threshold: {usage_pct:.1%} token usage"
            
        # Check time-based (4 hours)
        elapsed = datetime.now() - tracker['start_time']
        if elapsed > timedelta(hours=4):
            return True, f"Time limit: {elapsed.total_seconds()/3600:.1f} hours"
            
        return False, f"OK: {usage_pct:.1%} usage"
    
    def get_sundown_level(self, ci_name: str) -> str:
        """
        Get the current sundown level for a CI.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Level: 'ok', 'warning', 'suggest', 'auto', 'critical'
        """
        usage_pct = self.get_usage_percentage(ci_name)
        
        if usage_pct >= self.sundown_thresholds['critical']:
            return 'critical'
        elif usage_pct >= self.sundown_thresholds['auto']:
            return 'auto'
        elif usage_pct >= self.sundown_thresholds['suggest']:
            return 'suggest'
        elif usage_pct >= self.sundown_thresholds['warning']:
            return 'warning'
        else:
            return 'ok'
    
    def estimate_prompt_size(self, ci_name: str, message: str, 
                           system_prompt: str = "", 
                           buffered_messages: str = "") -> Dict[str, Any]:
        """
        Estimate the total prompt size for a CI message.
        
        Args:
            ci_name: Name of the CI
            message: New message being sent
            system_prompt: System prompt text
            buffered_messages: Any buffered messages
            
        Returns:
            Dictionary with token counts and recommendations
        """
        if ci_name not in self.usage_tracker:
            model = 'gpt-3.5-turbo'  # Default
            self.init_ci_tracking(ci_name, model)
        else:
            model = self.usage_tracker[ci_name]['model']
        
        # Count tokens for each component
        counts = {
            'message': self.count_tokens(message, model),
            'system_prompt': self.count_tokens(system_prompt, model) if system_prompt else 0,
            'buffered_messages': self.count_tokens(buffered_messages, model) if buffered_messages else 0,
            'existing_history': self.usage_tracker[ci_name]['usage'].get('conversation_history', 0)
        }
        
        total = sum(counts.values())
        limit = self.get_model_limit(model)
        
        result = {
            'counts': counts,
            'total': total,
            'limit': limit,
            'percentage': total / limit,
            'fits': total < limit * 0.95,  # Leave 5% buffer
            'recommendation': self._get_recommendation(total / limit)
        }
        
        return result
    
    def _get_recommendation(self, usage_pct: float) -> str:
        """
        Get recommendation based on usage percentage.
        
        Args:
            usage_pct: Usage percentage (0.0 to 1.0)
            
        Returns:
            Recommendation string
        """
        if usage_pct >= 0.95:
            return "CRITICAL: Immediate sundown required"
        elif usage_pct >= 0.85:
            return "HIGH: Sundown strongly recommended"
        elif usage_pct >= 0.75:
            return "MEDIUM: Consider sundown soon"
        elif usage_pct >= 0.60:
            return "LOW: Monitor token usage"
        else:
            return "OK: Sufficient token budget"
    
    def get_status(self, ci_name: str) -> Dict[str, Any]:
        """
        Get detailed status for a CI.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Status dictionary
        """
        if ci_name not in self.usage_tracker:
            return {
                'tracking': False,
                'ci_name': ci_name
            }
            
        tracker = self.usage_tracker[ci_name]
        usage_pct = self.get_usage_percentage(ci_name)
        
        return {
            'tracking': True,
            'ci_name': ci_name,
            'model': tracker['model'],
            'usage': tracker['usage'],
            'budgets': tracker['budgets'],
            'usage_percentage': usage_pct,
            'sundown_level': self.get_sundown_level(ci_name),
            'elapsed_time': str(datetime.now() - tracker['start_time']),
            'message_count': tracker['message_count'],
            'recommendation': self._get_recommendation(usage_pct)
        }
    
    def reset_ci(self, ci_name: str):
        """
        Reset tracking for a CI (after sundown/sunrise).
        
        Args:
            ci_name: Name of the CI
        """
        if ci_name in self.usage_tracker:
            model = self.usage_tracker[ci_name]['model']
            self.init_ci_tracking(ci_name, model)
            logger.info(f"Reset token tracking for {ci_name}")


# Global instance
_token_manager = None

def get_token_manager() -> TokenManager:
    """Get the global TokenManager instance."""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager