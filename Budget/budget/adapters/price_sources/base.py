"""
Price Source Adapter Base

This module provides the base classes for price source adapters.
These adapters fetch model pricing information from external sources.
"""

import os
import abc
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

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

# Import domain models
from budget.data.models import ProviderPricing, PriceType, PriceUpdateRecord, PriceSource

class PriceSourceAdapter(abc.ABC):
    """
    Base class for price source adapters.
    
    This abstract class defines the interface that all price source adapters
    must implement to fetch pricing data from external sources.
    """
    
    def __init__(self, source_id: str, source_name: str, auth_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the price source adapter.
        
        Args:
            source_id: The ID of the price source in the database
            source_name: The name of the price source
            auth_config: Authentication configuration for the source (optional)
        """
        self.source_id = source_id
        self.source_name = source_name
        self.auth_config = auth_config or {}
        
    @abc.abstractmethod
    async def fetch_prices(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Fetch pricing data from the source.
        
        Returns:
            A dictionary of provider -> model -> pricing data
            Format: {
                "provider1": {
                    "model1": {
                        "input_cost_per_token": 0.0001,
                        "output_cost_per_token": 0.0002,
                        ...
                    },
                    ...
                },
                ...
            }
        
        Raises:
            Exception: If fetching prices fails
        """
        pass
    
    @abc.abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the price source is healthy and accessible.
        
        Returns:
            True if the source is healthy, False otherwise
        """
        pass
    
    @log_function()
    def create_pricing_object(
        self,
        provider: str,
        model: str,
        price_data: Dict[str, Any]
    ) -> ProviderPricing:
        """
        Create a ProviderPricing object from raw price data.
        
        Args:
            provider: The provider name
            model: The model name
            price_data: The raw price data for the model
            
        Returns:
            A ProviderPricing object
        """
        debug_log.debug("price_source", f"Creating pricing object for {provider}/{model}")
        
        # Determine price type
        price_type = PriceType.TOKEN_BASED
        if price_data.get("price_type"):
            try:
                price_type = PriceType(price_data["price_type"])
            except ValueError:
                debug_log.warn("price_source", f"Invalid price type: {price_data['price_type']}")
        
        # Create pricing object
        return ProviderPricing(
            provider=provider,
            model=model,
            price_type=price_type,
            input_cost_per_token=price_data.get("input_cost_per_token", 0.0),
            output_cost_per_token=price_data.get("output_cost_per_token", 0.0),
            input_cost_per_char=price_data.get("input_cost_per_char", 0.0),
            output_cost_per_char=price_data.get("output_cost_per_char", 0.0),
            cost_per_image=price_data.get("cost_per_image"),
            cost_per_second=price_data.get("cost_per_second"),
            fixed_cost_per_request=price_data.get("fixed_cost_per_request"),
            version=price_data.get("version", "1.0"),
            source=self.source_id,
            source_url=price_data.get("source_url"),
            verified=False,  # Will be verified later
            effective_date=datetime.now(),
            metadata=price_data.get("metadata", {})
        )
    
    @log_function()
    def format_error(self, error: Exception) -> Dict[str, Any]:
        """
        Format an error for logging and reporting.
        
        Args:
            error: The exception that occurred
            
        Returns:
            A dictionary with error details
        """
        return {
            "source": self.source_name,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.now().isoformat()
        }

class FileCacheAdapter:
    """
    Mixin for file-based caching of price data.
    
    This class provides methods for caching price data to disk
    and retrieving it when needed.
    """
    
    def __init__(self, cache_dir: str = None, cache_ttl: int = 3600):
        """
        Initialize the file cache.
        
        Args:
            cache_dir: Directory for cache files (defaults to .cache in current dir)
            cache_ttl: Cache time-to-live in seconds (defaults to 1 hour)
        """
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), ".cache")
        self.cache_ttl = cache_ttl
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    @log_function()
    def get_cache_path(self, key: str) -> str:
        """
        Get the cache file path for a key.
        
        Args:
            key: The cache key
            
        Returns:
            Path to the cache file
        """
        # Sanitize key for filename
        safe_key = "".join(c for c in key if c.isalnum() or c in "._-")
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    @log_function()
    def get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache if available and not expired.
        
        Args:
            key: The cache key
            
        Returns:
            Cached data if available and fresh, None otherwise
        """
        cache_path = self.get_cache_path(key)
        
        try:
            # Check if cache file exists
            if not os.path.exists(cache_path):
                debug_log.debug("price_source", f"Cache miss for {key}: file not found")
                return None
            
            # Check if cache is expired
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
            if file_age.total_seconds() > self.cache_ttl:
                debug_log.debug("price_source", f"Cache expired for {key}")
                return None
            
            # Read and parse cache file
            with open(cache_path, "r") as f:
                data = json.load(f)
                debug_log.debug("price_source", f"Cache hit for {key}")
                return data
        except Exception as e:
            debug_log.warn("price_source", f"Cache error for {key}: {str(e)}")
            return None
    
    @log_function()
    def save_to_cache(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Save data to cache.
        
        Args:
            key: The cache key
            data: The data to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_path = self.get_cache_path(key)
        
        try:
            # Write data to cache file
            with open(cache_path, "w") as f:
                json.dump(data, f)
                debug_log.debug("price_source", f"Saved to cache: {key}")
                return True
        except Exception as e:
            debug_log.warn("price_source", f"Cache write error for {key}: {str(e)}")
            return False

class RateLimitedAdapter:
    """
    Mixin for rate-limited access to price sources.
    
    This class provides methods for rate limiting requests to
    external APIs to avoid hitting rate limits.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_day: Optional[int] = None
    ):
        """
        Initialize the rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_day: Maximum requests per day (optional)
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        
        # Tracking for rate limiting
        self.minute_requests = []
        self.day_requests = []
    
    @log_function()
    async def check_rate_limit(self) -> bool:
        """
        Check if current request would exceed rate limits.
        
        Returns:
            True if request is allowed, False if rate limited
        """
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        day_ago = now - timedelta(days=1)
        
        # Remove old timestamps
        self.minute_requests = [t for t in self.minute_requests if t > minute_ago]
        if self.requests_per_day:
            self.day_requests = [t for t in self.day_requests if t > day_ago]
        
        # Check minute limit
        if len(self.minute_requests) >= self.requests_per_minute:
            debug_log.warn("price_source", f"Rate limit exceeded: {self.requests_per_minute} requests per minute")
            return False
        
        # Check day limit if configured
        if self.requests_per_day and len(self.day_requests) >= self.requests_per_day:
            debug_log.warn("price_source", f"Rate limit exceeded: {self.requests_per_day} requests per day")
            return False
        
        # Record this request
        self.minute_requests.append(now)
        if self.requests_per_day:
            self.day_requests.append(now)
        
        return True