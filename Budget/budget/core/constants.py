"""
Budget Constants and Configuration

This module defines constants and default configurations for the Budget component.
"""

from enum import Enum
from typing import Dict, Any

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


# Default token budget limits per tier
DEFAULT_TOKEN_LIMITS = {
    "local_lightweight": {
        "hourly": 1000000,    # 1M tokens/hour
        "daily": 10000000,    # 10M tokens/day
        "weekly": 50000000,   # 50M tokens/week
        "monthly": 200000000, # 200M tokens/month
        "per_session": 8000   # 8K tokens/session
    },
    "local_midweight": {
        "hourly": 500000,     # 500K tokens/hour
        "daily": 5000000,     # 5M tokens/day
        "weekly": 25000000,   # 25M tokens/week
        "monthly": 100000000, # 100M tokens/month
        "per_session": 16000  # 16K tokens/session
    },
    "remote_heavyweight": {
        "hourly": 100000,     # 100K tokens/hour
        "daily": 1000000,     # 1M tokens/day
        "weekly": 5000000,    # 5M tokens/week
        "monthly": 20000000,  # 20M tokens/month
        "per_session": 32000  # 32K tokens/session
    }
}

# Default cost budget limits
DEFAULT_COST_LIMITS = {
    "hourly": 0.50,   # $0.50 per hour
    "daily": 5.00,    # $5.00 per day
    "weekly": 25.00,  # $25.00 per week
    "monthly": 100.00 # $100.00 per month
}

# Default token allocation per task type and priority
DEFAULT_ALLOCATIONS = {
    "default": {
        1: 1000,  # LOW priority
        5: 2000,  # NORMAL priority
        8: 4000,  # HIGH priority
        10: 8000  # CRITICAL priority
    },
    "chat": {
        1: 2000,
        5: 4000,
        8: 8000,
        10: 16000
    },
    "coding": {
        1: 4000,
        5: 8000,
        8: 16000,
        10: 32000
    },
    "analysis": {
        1: 4000,
        5: 8000,
        8: 16000,
        10: 32000
    },
    "embedding": {
        1: 10000,
        5: 25000,
        8: 50000,
        10: 100000
    }
}

# Model tier mappings
DEFAULT_MODEL_TIERS = {
    # Local lightweight models
    "codellama": "local_lightweight",
    "deepseek-coder": "local_lightweight",
    "starcoder": "local_lightweight",
    "phi-2": "local_lightweight",
    "gemma-2b": "local_lightweight",
    
    # Local midweight models
    "claude-haiku": "local_midweight",
    "claude-3-haiku": "local_midweight",
    "llama-3": "local_midweight",
    "mistral": "local_midweight",
    "qwen": "local_midweight",
    "gemma-7b": "local_midweight",
    
    # Remote heavyweight models
    "gpt-4": "remote_heavyweight",
    "gpt-4o": "remote_heavyweight",
    "claude-3-opus": "remote_heavyweight",
    "claude-3-sonnet": "remote_heavyweight",
    "claude-3.5-sonnet": "remote_heavyweight",
    "claude-3.7-sonnet": "remote_heavyweight"
}

# Provider default tiers
DEFAULT_PROVIDER_TIERS = {
    "openai": "remote_heavyweight",
    "anthropic": "remote_heavyweight",
    "ollama": "local_midweight",
    "local": "local_lightweight"
}

# Initial pricing database
# These values will be updated by the price monitoring system
INITIAL_PRICING_DATA = {
    "anthropic": {
        "claude-3-opus-20240229": {
            "input_cost_per_token": 0.000015,
            "output_cost_per_token": 0.000075,
        },
        "claude-3-sonnet-20240229": {
            "input_cost_per_token": 0.000003,
            "output_cost_per_token": 0.000015,
        },
        "claude-3-haiku-20240307": {
            "input_cost_per_token": 0.00000025,
            "output_cost_per_token": 0.00000125,
        },
        "claude-3-5-sonnet-20240620": {
            "input_cost_per_token": 0.000003,
            "output_cost_per_token": 0.000013,
        },
        "claude-3-7-sonnet-20250219": {
            "input_cost_per_token": 0.000003,
            "output_cost_per_token": 0.000013,
        }
    },
    "openai": {
        "gpt-4": {
            "input_cost_per_token": 0.00003,
            "output_cost_per_token": 0.00006,
        },
        "gpt-4-turbo": {
            "input_cost_per_token": 0.00001,
            "output_cost_per_token": 0.00003,
        },
        "gpt-4o": {
            "input_cost_per_token": 0.00001,
            "output_cost_per_token": 0.00003,
        },
        "gpt-3.5-turbo": {
            "input_cost_per_token": 0.0000005,
            "output_cost_per_token": 0.0000015,
        }
    },
    "ollama": {  # Local models are free
        "llama3": {
            "input_cost_per_token": 0.0,
            "output_cost_per_token": 0.0,
        }
    },
    "simulated": {  # Simulated provider is free
        "simulated-standard": {
            "input_cost_per_token": 0.0,
            "output_cost_per_token": 0.0,
        }
    }
}

# Price source configuration
DEFAULT_PRICE_SOURCES = [
    {
        "name": "LiteLLM",
        "description": "LiteLLM pricing database",
        "url": "https://github.com/BerriAI/litellm",
        "type": "api",
        "trust_score": 0.9,
        "update_frequency": 1440,  # Once per day
        "is_active": True
    },
    {
        "name": "LLMPrices.com",
        "description": "Community-maintained LLM pricing website",
        "url": "https://llmprices.com",
        "type": "scraper",
        "trust_score": 0.8,
        "update_frequency": 1440,  # Once per day
        "is_active": True
    },
    {
        "name": "Pretrained.ai",
        "description": "Pretrained.ai model cost index",
        "url": "https://pretrained.ai",
        "type": "scraper",
        "trust_score": 0.7,
        "update_frequency": 1440,  # Once per day
        "is_active": True
    }
]

# Thresholds for alerts
ALERT_THRESHOLDS = {
    "warning": 0.8,   # 80% of budget
    "critical": 0.95  # 95% of budget
}

# Database configuration
DATABASE_CONFIG = {
    "type": "sqlite",
    "connection_string": "sqlite:///budget.db",
    "pool_size": 5,
    "max_overflow": 10
}