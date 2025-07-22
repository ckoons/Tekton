"""
LiteLLM Price Source Adapter

This module provides an adapter for fetching pricing data from LiteLLM.
LiteLLM maintains pricing information for various LLM providers.
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from shared.env import TektonEnviron

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

# Import base adapter classes
from budget.adapters.price_sources.base import PriceSourceAdapter, FileCacheAdapter, RateLimitedAdapter

class LiteLLMAdapter(PriceSourceAdapter, FileCacheAdapter, RateLimitedAdapter):
    """
    Adapter for fetching pricing data from LiteLLM.
    
    This adapter retrieves model pricing information directly from
    LiteLLM's pricing data, which is used for their model routing.
    """
    
    def __init__(
        self, 
        source_id: str,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        requests_per_minute: int = 60
    ):
        """
        Initialize the LiteLLM adapter.
        
        Args:
            source_id: The ID of the price source in the database
            api_key: LiteLLM API key (optional)
            cache_dir: Directory for cache files
            cache_ttl: Cache time-to-live in seconds
            requests_per_minute: Maximum requests per minute
        """
        PriceSourceAdapter.__init__(
            self,
            source_id=source_id,
            source_name="LiteLLM",
            auth_config={"api_key": api_key} if api_key else {}
        )
        FileCacheAdapter.__init__(
            self,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl
        )
        RateLimitedAdapter.__init__(
            self,
            requests_per_minute=requests_per_minute
        )
        
        # Configure API settings
        self.api_base = TektonEnviron.get("LITELLM_API_BASE", "https://api.litellm.ai")
        self.api_key = api_key or TektonEnviron.get("LITELLM_API_KEY")
        self.pricing_endpoint = "/pricing"
        
        # Optional: Use local fallback data if API is unavailable
        self.local_fallback = True
    
    @log_function()
    async def fetch_prices(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Fetch pricing data from LiteLLM.
        
        Returns:
            A dictionary of provider -> model -> pricing data
            
        Raises:
            Exception: If fetching prices fails and no fallback is available
        """
        debug_log.info("price_source", "Fetching prices from LiteLLM")
        
        # Check cache first
        cache_key = "litellm_prices"
        cached_data = self.get_from_cache(cache_key)
        if cached_data:
            debug_log.info("price_source", "Using cached LiteLLM prices")
            return cached_data
        
        # Check rate limit before making API request
        if not await self.check_rate_limit():
            debug_log.warn("price_source", "Rate limited, using fallback if available")
            return await self._get_fallback_pricing()
        
        try:
            # Fetch pricing data from API
            url = f"{self.api_base}{self.pricing_endpoint}"
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        debug_log.error("price_source", f"LiteLLM API error: {response.status}")
                        return await self._get_fallback_pricing()
                    
                    data = await response.json()
                    
                    # Transform to our standard format
                    pricing_data = self._transform_litellm_data(data)
                    
                    # Cache the data
                    self.save_to_cache(cache_key, pricing_data)
                    
                    debug_log.info("price_source", "Successfully fetched LiteLLM prices")
                    return pricing_data
        except Exception as e:
            debug_log.error("price_source", f"Error fetching LiteLLM prices: {str(e)}")
            return await self._get_fallback_pricing()
    
    @log_function()
    async def health_check(self) -> bool:
        """
        Check if the LiteLLM API is accessible.
        
        Returns:
            True if the API is healthy, False otherwise
        """
        debug_log.info("price_source", "Performing LiteLLM health check")
        
        try:
            url = f"{self.api_base}/health"
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    healthy = response.status == 200
                    debug_log.info("price_source", f"LiteLLM health check: {'Healthy' if healthy else 'Unhealthy'}")
                    return healthy
        except Exception as e:
            debug_log.error("price_source", f"LiteLLM health check error: {str(e)}")
            return False
    
    @log_function()
    def _transform_litellm_data(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Transform LiteLLM pricing data to our standard format.
        
        Args:
            data: The raw data from LiteLLM API
            
        Returns:
            Transformed pricing data
        """
        result = {}
        
        # Extract pricing data from LiteLLM response
        prices = data.get("prices", {})
        
        for model_key, model_data in prices.items():
            # Extract provider and model name from LiteLLM model key
            provider, model = self._parse_model_key(model_key)
            
            # Initialize provider dict if needed
            if provider not in result:
                result[provider] = {}
            
            # Extract pricing information
            result[provider][model] = {
                "input_cost_per_token": model_data.get("input_cost_per_token", 0.0),
                "output_cost_per_token": model_data.get("output_cost_per_token", 0.0),
                "price_type": "token_based",  # Most LiteLLM models use token-based pricing
                "version": "1.0",
                "source_url": "https://github.com/BerriAI/litellm",
                "metadata": {
                    "supported_features": model_data.get("supported_features", []),
                    "model_group": model_data.get("model_group", None),
                    "original_model_key": model_key
                }
            }
        
        return result
    
    @log_function()
    def _parse_model_key(self, model_key: str) -> tuple:
        """
        Parse a LiteLLM model key into provider and model.
        
        Args:
            model_key: The LiteLLM model key (e.g., "anthropic/claude-3-opus-20240229")
            
        Returns:
            Tuple of (provider, model)
        """
        if "/" in model_key:
            provider, model = model_key.split("/", 1)
            return provider, model
        
        # Handle special cases
        if model_key.startswith("gpt-"):
            return "openai", model_key
        if model_key.startswith("claude-"):
            return "anthropic", model_key
        
        # Default case
        return "unknown", model_key
    
    @log_function()
    async def _get_fallback_pricing(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Get fallback pricing data if API is unavailable.
        
        Returns:
            Fallback pricing data
            
        Raises:
            Exception: If no fallback is available
        """
        debug_log.info("price_source", "Using fallback pricing data")
        
        if not self.local_fallback:
            raise Exception("LiteLLM API is unavailable and no fallback is configured")
        
        # Load embedded fallback data
        try:
            fallback_path = os.path.join(
                os.path.dirname(__file__),
                "fallback_data",
                "litellm_fallback.json"
            )
            
            if os.path.exists(fallback_path):
                with open(fallback_path, "r") as f:
                    return json.load(f)
            
            # If fallback file doesn't exist, use hardcoded data
            return self._get_hardcoded_fallback()
        except Exception as e:
            debug_log.error("price_source", f"Error loading fallback data: {str(e)}")
            return self._get_hardcoded_fallback()
    
    @log_function()
    def _get_hardcoded_fallback(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Get hardcoded fallback pricing data.
        
        Returns:
            Hardcoded pricing data
        """
        # Basic fallback data for common models
        return {
            "openai": {
                "gpt-4o": {
                    "input_cost_per_token": 0.00005,
                    "output_cost_per_token": 0.00015,
                    "price_type": "token_based",
                    "version": "1.0",
                    "source_url": "https://openai.com/pricing",
                    "metadata": {
                        "supported_features": ["text", "vision"],
                        "model_group": "gpt-4",
                        "original_model_key": "openai/gpt-4o"
                    }
                },
                "gpt-4-turbo": {
                    "input_cost_per_token": 0.00001,
                    "output_cost_per_token": 0.00003,
                    "price_type": "token_based",
                    "version": "1.0",
                    "source_url": "https://openai.com/pricing",
                    "metadata": {
                        "supported_features": ["text"],
                        "model_group": "gpt-4",
                        "original_model_key": "openai/gpt-4-turbo"
                    }
                },
                "gpt-3.5-turbo": {
                    "input_cost_per_token": 0.0000005,
                    "output_cost_per_token": 0.0000015,
                    "price_type": "token_based",
                    "version": "1.0",
                    "source_url": "https://openai.com/pricing",
                    "metadata": {
                        "supported_features": ["text"],
                        "model_group": "gpt-3.5",
                        "original_model_key": "openai/gpt-3.5-turbo"
                    }
                }
            },
            "anthropic": {
                "claude-3-opus-20240229": {
                    "input_cost_per_token": 0.00001,
                    "output_cost_per_token": 0.00003,
                    "price_type": "token_based",
                    "version": "1.0",
                    "source_url": "https://anthropic.com/pricing",
                    "metadata": {
                        "supported_features": ["text", "vision"],
                        "model_group": "claude-3",
                        "original_model_key": "anthropic/claude-3-opus-20240229"
                    }
                },
                "claude-3-sonnet-20240229": {
                    "input_cost_per_token": 0.000003,
                    "output_cost_per_token": 0.000015,
                    "price_type": "token_based",
                    "version": "1.0",
                    "source_url": "https://anthropic.com/pricing",
                    "metadata": {
                        "supported_features": ["text", "vision"],
                        "model_group": "claude-3",
                        "original_model_key": "anthropic/claude-3-sonnet-20240229"
                    }
                },
                "claude-3-haiku-20240307": {
                    "input_cost_per_token": 0.00000025,
                    "output_cost_per_token": 0.00000125,
                    "price_type": "token_based",
                    "version": "1.0",
                    "source_url": "https://anthropic.com/pricing",
                    "metadata": {
                        "supported_features": ["text", "vision"],
                        "model_group": "claude-3",
                        "original_model_key": "anthropic/claude-3-haiku-20240307"
                    }
                }
            }
        }