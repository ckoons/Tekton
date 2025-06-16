"""
Web Scraper Price Source Adapter

This module provides adapters for scraping pricing data from websites
that publish LLM pricing information.
"""

import os
import re
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

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

class WebScraperAdapter(PriceSourceAdapter, FileCacheAdapter, RateLimitedAdapter):
    """
    Base adapter for scraping pricing data from websites.
    
    This class provides common functionality for website scrapers:
    - HTTP requests with proper headers and error handling
    - HTML parsing with BeautifulSoup
    - Rate limiting to avoid overloading sites
    - Caching to reduce scraping frequency
    """
    
    def __init__(
        self,
        source_id: str,
        source_name: str,
        base_url: str,
        scraper_config: Dict[str, Any],
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        requests_per_minute: int = 10,
        requests_per_day: int = 100
    ):
        """
        Initialize the web scraper adapter.
        
        Args:
            source_id: The ID of the price source in the database
            source_name: The name of the price source
            base_url: The base URL of the website
            scraper_config: Configuration for the scraper
            cache_dir: Directory for cache files
            cache_ttl: Cache time-to-live in seconds
            requests_per_minute: Maximum requests per minute
            requests_per_day: Maximum requests per day
        """
        PriceSourceAdapter.__init__(
            self,
            source_id=source_id,
            source_name=source_name,
            auth_config={}
        )
        FileCacheAdapter.__init__(
            self,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl
        )
        RateLimitedAdapter.__init__(
            self,
            requests_per_minute=requests_per_minute,
            requests_per_day=requests_per_day
        )
        
        # Configure scraper settings
        self.base_url = base_url
        self.config = scraper_config
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
    
    @log_function()
    async def fetch_prices(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Fetch pricing data by scraping websites.
        
        Returns:
            A dictionary of provider -> model -> pricing data
            
        Raises:
            Exception: If scraping fails and no fallback is available
        """
        debug_log.info("price_source", f"Scraping prices from {self.source_name}")
        
        # Check cache first
        cache_key = f"{self.source_name.lower()}_prices"
        cached_data = self.get_from_cache(cache_key)
        if cached_data:
            debug_log.info("price_source", f"Using cached {self.source_name} prices")
            return cached_data
        
        # Check rate limit before making request
        if not await self.check_rate_limit():
            debug_log.warn("price_source", "Rate limited, using fallback if available")
            return await self._get_fallback_pricing()
        
        try:
            # Fetch HTML from price page
            url = self.config.get("price_page_url", self.base_url)
            html = await self._fetch_html(url)
            
            # Parse HTML to extract pricing data
            pricing_data = await self._parse_html(html)
            
            # Cache the data
            self.save_to_cache(cache_key, pricing_data)
            
            debug_log.info("price_source", f"Successfully scraped {self.source_name} prices")
            return pricing_data
        except Exception as e:
            debug_log.error("price_source", f"Error scraping {self.source_name} prices: {str(e)}")
            return await self._get_fallback_pricing()
    
    @log_function()
    async def health_check(self) -> bool:
        """
        Check if the website is accessible.
        
        Returns:
            True if the site is accessible, False otherwise
        """
        debug_log.info("price_source", f"Performing {self.source_name} health check")
        
        try:
            url = self.base_url
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.default_headers) as response:
                    healthy = response.status == 200
                    debug_log.info("price_source", f"{self.source_name} health check: {'Healthy' if healthy else 'Unhealthy'}")
                    return healthy
        except Exception as e:
            debug_log.error("price_source", f"{self.source_name} health check error: {str(e)}")
            return False
    
    @log_function()
    async def _fetch_html(self, url: str) -> str:
        """
        Fetch HTML content from a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            The HTML content
            
        Raises:
            Exception: If fetching fails
        """
        debug_log.debug("price_source", f"Fetching HTML from {url}")
        
        try:
            headers = self.config.get("headers", self.default_headers)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP error: {response.status}")
                    
                    return await response.text()
        except Exception as e:
            debug_log.error("price_source", f"Error fetching HTML: {str(e)}")
            raise
    
    @log_function()
    async def _parse_html(self, html: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Parse HTML to extract pricing data.
        
        This is a placeholder that should be overridden by subclasses.
        
        Args:
            html: The HTML content to parse
            
        Returns:
            Extracted pricing data
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _parse_html method")
    
    @log_function()
    async def _get_fallback_pricing(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Get fallback pricing data if scraping fails.
        
        Returns:
            Fallback pricing data
            
        Raises:
            Exception: If no fallback is available
        """
        debug_log.info("price_source", f"Using fallback pricing data for {self.source_name}")
        
        fallback_path = os.path.join(
            os.path.dirname(__file__),
            "fallback_data",
            f"{self.source_name.lower()}_fallback.json"
        )
        
        try:
            if os.path.exists(fallback_path):
                with open(fallback_path, "r") as f:
                    return json.load(f)
            
            # If fallback file doesn't exist, use empty data
            debug_log.warn("price_source", f"No fallback data available for {self.source_name}")
            return {}
        except Exception as e:
            debug_log.error("price_source", f"Error loading fallback data for {self.source_name}: {str(e)}")
            return {}

class LLMPricesAdapter(WebScraperAdapter):
    """
    Adapter for scraping pricing data from LLMPrices.com.
    """
    
    def __init__(
        self,
        source_id: str,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600 * 6  # 6 hours cache
    ):
        """
        Initialize the LLMPrices.com adapter.
        
        Args:
            source_id: The ID of the price source in the database
            cache_dir: Directory for cache files
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__(
            source_id=source_id,
            source_name="LLMPrices",
            base_url="https://llmprices.com",
            scraper_config={
                "price_page_url": "https://llmprices.com",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
            },
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            requests_per_minute=5,
            requests_per_day=20
        )
    
    @log_function()
    async def _parse_html(self, html: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Parse HTML from LLMPrices.com to extract pricing data.
        
        Args:
            html: The HTML content to parse
            
        Returns:
            Extracted pricing data
        """
        debug_log.debug("price_source", "Parsing LLMPrices.com HTML")
        
        result = {}
        soup = BeautifulSoup(html, "html.parser")
        
        try:
            # Find all pricing tables
            tables = soup.find_all("table")
            
            for table in tables:
                # Check if this is a pricing table
                headers = [th.text.strip() for th in table.find_all("th")]
                if not headers or "Model" not in headers:
                    continue
                
                # Determine column indices
                model_idx = headers.index("Model") if "Model" in headers else None
                input_idx = None
                output_idx = None
                provider_idx = None
                
                # Look for price columns
                for i, header in enumerate(headers):
                    if "Input" in header and "Price" in header:
                        input_idx = i
                    if "Output" in header and "Price" in header:
                        output_idx = i
                    if "Provider" in header:
                        provider_idx = i
                
                # Skip if we can't find the required columns
                if model_idx is None or (input_idx is None and output_idx is None):
                    continue
                
                # Process rows
                for row in table.find_all("tr")[1:]:  # Skip header row
                    cells = row.find_all("td")
                    if len(cells) <= max(filter(None, [model_idx, input_idx, output_idx, provider_idx])):
                        continue
                    
                    # Extract model name and provider
                    model = cells[model_idx].text.strip() if model_idx is not None else "unknown"
                    provider = cells[provider_idx].text.strip() if provider_idx is not None else self._guess_provider(model)
                    
                    # Normalize provider and model names
                    provider, model = self._normalize_provider_model(provider, model)
                    
                    # Extract pricing
                    input_price = self._extract_price(cells[input_idx].text.strip()) if input_idx is not None else 0.0
                    output_price = self._extract_price(cells[output_idx].text.strip()) if output_idx is not None else 0.0
                    
                    # Add to result
                    if provider not in result:
                        result[provider] = {}
                    
                    result[provider][model] = {
                        "input_cost_per_token": input_price,
                        "output_cost_per_token": output_price,
                        "price_type": "token_based",
                        "version": "1.0",
                        "source_url": "https://llmprices.com",
                        "metadata": {
                            "scraper": "llmprices_adapter",
                            "scrape_date": datetime.now().isoformat()
                        }
                    }
            
            debug_log.info("price_source", f"Extracted {sum(len(models) for models in result.values())} models from LLMPrices.com")
            return result
        except Exception as e:
            debug_log.error("price_source", f"Error parsing LLMPrices.com HTML: {str(e)}")
            raise
    
    @log_function()
    def _extract_price(self, price_text: str) -> float:
        """
        Extract a price value from text.
        
        Args:
            price_text: The price text (e.g., "$0.0001/1K tokens")
            
        Returns:
            The price per token as a float
        """
        # Extract numeric value with regex
        match = re.search(r'\$([\d\.]+)', price_text)
        if not match:
            return 0.0
        
        price = float(match.group(1))
        
        # Check if price is per 1K tokens and convert to per-token
        if "/1K" in price_text or "per 1K" in price_text:
            price = price / 1000
        
        return price
    
    @log_function()
    def _guess_provider(self, model_name: str) -> str:
        """
        Guess the provider from a model name.
        
        Args:
            model_name: The model name
            
        Returns:
            The guessed provider name
        """
        model_lower = model_name.lower()
        
        if "gpt" in model_lower:
            return "openai"
        elif "claude" in model_lower:
            return "anthropic"
        elif "llama" in model_lower:
            return "meta"
        elif "gemini" in model_lower or "palm" in model_lower:
            return "google"
        elif "falcon" in model_lower:
            return "tii"
        elif "mistral" in model_lower:
            return "mistral"
        
        return "unknown"
    
    @log_function()
    def _normalize_provider_model(self, provider: str, model: str) -> tuple:
        """
        Normalize provider and model names for consistency.
        
        Args:
            provider: The raw provider name
            model: The raw model name
            
        Returns:
            Tuple of (normalized_provider, normalized_model)
        """
        # Normalize provider names
        provider_map = {
            "openai": "openai",
            "open ai": "openai",
            "anthropic": "anthropic",
            "google": "google",
            "meta": "meta",
            "facebook": "meta",
            "mistral": "mistral",
            "mistral ai": "mistral",
            "cohere": "cohere"
        }
        
        # Normalize model names for common cases
        def normalize_model(provider, model):
            if provider == "openai":
                if not model.startswith("gpt-"):
                    return f"gpt-{model}"
                return model
            elif provider == "anthropic":
                if not model.startswith("claude-"):
                    return f"claude-{model}"
                return model
            return model
        
        # Get normalized provider
        normalized_provider = provider_map.get(provider.lower(), provider.lower())
        
        # Get normalized model
        normalized_model = normalize_model(normalized_provider, model)
        
        return normalized_provider, normalized_model

class PretrainedAIAdapter(WebScraperAdapter):
    """
    Adapter for scraping pricing data from Pretrained.ai.
    """
    
    def __init__(
        self,
        source_id: str,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600 * 6  # 6 hours cache
    ):
        """
        Initialize the Pretrained.ai adapter.
        
        Args:
            source_id: The ID of the price source in the database
            cache_dir: Directory for cache files
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__(
            source_id=source_id,
            source_name="PretrainedAI",
            base_url="https://pretrained.ai",
            scraper_config={
                "price_page_url": "https://pretrained.ai/pricing",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
            },
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            requests_per_minute=5,
            requests_per_day=20
        )
    
    @log_function()
    async def _parse_html(self, html: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Parse HTML from Pretrained.ai to extract pricing data.
        
        Args:
            html: The HTML content to parse
            
        Returns:
            Extracted pricing data
        """
        debug_log.debug("price_source", "Parsing Pretrained.ai HTML")
        
        result = {}
        soup = BeautifulSoup(html, "html.parser")
        
        try:
            # Find all pricing tables - Pretrained.ai typically uses div tables with specific classes
            pricing_sections = soup.find_all("div", class_=lambda c: c and "pricing" in c.lower())
            
            if not pricing_sections:
                # Try a more generic approach to find tables or pricing components
                pricing_sections = soup.find_all("table") + soup.find_all("div", class_=lambda c: c and ("table" in c.lower() or "card" in c.lower()))
            
            for section in pricing_sections:
                # Extract provider name from section heading if available
                heading = section.find_previous(["h1", "h2", "h3", "h4"])
                provider = heading.text.strip() if heading else "unknown"
                
                # Normalize provider name
                provider = self._normalize_provider(provider)
                
                # Find model cards or rows
                model_elements = section.find_all("div", class_=lambda c: c and ("card" in c.lower() or "model" in c.lower()))
                if not model_elements:
                    model_elements = section.find_all("tr")
                
                for element in model_elements:
                    # Try to extract model name, input price, and output price
                    model_name = None
                    input_price = 0.0
                    output_price = 0.0
                    
                    # Look for model name in headings or strong elements
                    name_elem = element.find(["h3", "h4", "strong", "b"]) or element.find("div", class_=lambda c: c and "name" in c.lower())
                    if name_elem:
                        model_name = name_elem.text.strip()
                    
                    # Look for pricing information in spans or divs with pricing-related classes or text
                    price_elems = element.find_all(["span", "div", "p"], string=lambda s: s and any(x in s.lower() for x in ["$", "price", "token", "cost"]))
                    
                    for price_elem in price_elems:
                        text = price_elem.text.strip().lower()
                        extracted_price = self._extract_price(text)
                        
                        if "input" in text or "prompt" in text:
                            input_price = extracted_price
                        elif "output" in text or "completion" in text or "response" in text:
                            output_price = extracted_price
                        elif input_price == 0.0:  # If not explicitly labeled, use as input price
                            input_price = extracted_price
                    
                    # Skip if we couldn't find a model name or any prices
                    if not model_name or (input_price == 0.0 and output_price == 0.0):
                        continue
                    
                    # Normalize model name
                    normalized_model = self._normalize_model(provider, model_name)
                    
                    # Add to result
                    if provider not in result:
                        result[provider] = {}
                    
                    result[provider][normalized_model] = {
                        "input_cost_per_token": input_price,
                        "output_cost_per_token": output_price,
                        "price_type": "token_based",
                        "version": "1.0",
                        "source_url": "https://pretrained.ai/pricing",
                        "metadata": {
                            "scraper": "pretrained_ai_adapter",
                            "original_model_name": model_name,
                            "scrape_date": datetime.now().isoformat()
                        }
                    }
            
            debug_log.info("price_source", f"Extracted {sum(len(models) for models in result.values())} models from Pretrained.ai")
            return result
        except Exception as e:
            debug_log.error("price_source", f"Error parsing Pretrained.ai HTML: {str(e)}")
            raise
    
    @log_function()
    def _extract_price(self, price_text: str) -> float:
        """
        Extract a price value from text.
        
        Args:
            price_text: The price text (e.g., "$0.0001 per 1K tokens")
            
        Returns:
            The price per token as a float
        """
        # Extract numeric value with regex
        match = re.search(r'\$([\d\.]+)', price_text)
        if not match:
            return 0.0
        
        price = float(match.group(1))
        
        # Check for scaling factors
        if "1k" in price_text.lower() or "1000" in price_text:
            price = price / 1000
        elif "1m" in price_text.lower() or "1000000" in price_text or "million" in price_text.lower():
            price = price / 1000000
        
        return price
    
    @log_function()
    def _normalize_provider(self, provider: str) -> str:
        """
        Normalize provider name for consistency.
        
        Args:
            provider: The raw provider name
            
        Returns:
            Normalized provider name
        """
        provider_lower = provider.lower()
        
        if "openai" in provider_lower:
            return "openai"
        elif "anthropic" in provider_lower:
            return "anthropic"
        elif "google" in provider_lower:
            return "google"
        elif "meta" in provider_lower or "llama" in provider_lower:
            return "meta"
        elif "mistral" in provider_lower:
            return "mistral"
        elif "cohere" in provider_lower:
            return "cohere"
        
        return provider
    
    @log_function()
    def _normalize_model(self, provider: str, model_name: str) -> str:
        """
        Normalize model name for consistency.
        
        Args:
            provider: The provider name
            model_name: The raw model name
            
        Returns:
            Normalized model name
        """
        model_lower = model_name.lower()
        
        if provider == "openai":
            if "gpt-4" in model_lower and "turbo" in model_lower:
                return "gpt-4-turbo"
            elif "gpt-4" in model_lower and "o" in model_lower:
                return "gpt-4o"
            elif "gpt-4" in model_lower:
                return "gpt-4"
            elif "gpt-3.5" in model_lower:
                return "gpt-3.5-turbo"
        elif provider == "anthropic":
            if "claude-3" in model_lower and "opus" in model_lower:
                return "claude-3-opus-20240229"
            elif "claude-3" in model_lower and "sonnet" in model_lower:
                return "claude-3-sonnet-20240229"
            elif "claude-3" in model_lower and "haiku" in model_lower:
                return "claude-3-haiku-20240307"
            elif "claude-2" in model_lower:
                return "claude-2"
        
        return model_name