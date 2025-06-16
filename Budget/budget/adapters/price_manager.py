"""
Price Manager

This module provides a manager for coordinating price source adapters and
verifying pricing data across multiple sources.
"""

import os
import uuid
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Type
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

# Import domain models and repositories
from budget.data.models import (
    ProviderPricing, PriceType, PriceUpdateRecord, PriceSource
)
from budget.data.repository import (
    pricing_repo, update_repo, source_repo
)

# Import price source adapters
from budget.adapters.price_sources import (
    PriceSourceAdapter, LiteLLMAdapter, LLMPricesAdapter, PretrainedAIAdapter
)

class PriceManager:
    """
    Manager for price source adapters and price verification.
    
    This class coordinates the fetching and verification of pricing data
    from multiple sources, and updates the pricing database accordingly.
    """
    
    def __init__(self):
        """Initialize the price manager."""
        self.adapters = {}
        self.source_trust_scores = {}
        self.verification_threshold = 0.8  # 80% agreement required for verification
        self.price_tolerance = 0.1  # 10% tolerance for price differences
        
        # Configuration
        self.update_schedule_minutes = 60 * 6  # Check for updates every 6 hours
        self.update_schedule_enabled = True
        
        self.cache_dir = os.path.join(os.getcwd(), ".cache", "price_sources")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    @log_function()
    async def initialize(self):
        """
        Initialize the price manager and load adapters.
        
        This method loads the available price sources from the database
        and initializes the corresponding adapters.
        """
        debug_log.info("price_manager", "Initializing price manager")
        
        # Get all active price sources
        sources = source_repo.get_active_sources()
        
        if not sources:
            debug_log.warn("price_manager", "No active price sources found")
            await self._create_default_sources()
            sources = source_repo.get_active_sources()
        
        # Initialize adapters for each source
        for source in sources:
            await self._initialize_adapter(source)
            self.source_trust_scores[source.source_id] = source.trust_score
        
        debug_log.info("price_manager", f"Initialized {len(self.adapters)} price source adapters")
        
        # Start update scheduler if enabled
        if self.update_schedule_enabled:
            debug_log.info("price_manager", f"Starting price update scheduler (every {self.update_schedule_minutes} minutes)")
            # In a production environment, we would use a proper scheduler
            # like APScheduler or Celery, but for simplicity we'll use a
            # background task with asyncio
            asyncio.create_task(self._update_scheduler())
    
    @log_function()
    async def _update_scheduler(self):
        """
        Background task for scheduled price updates.
        """
        while self.update_schedule_enabled:
            try:
                # Check for sources that need updating
                sources_to_update = source_repo.get_sources_for_update()
                
                if sources_to_update:
                    debug_log.info("price_manager", f"Scheduled update for {len(sources_to_update)} price sources")
                    for source in sources_to_update:
                        if source.source_id in self.adapters:
                            await self.update_prices_from_source(source.source_id)
                            # Update the last_update timestamp
                            source_repo.update_source_timestamp(source.source_id, True)
            except Exception as e:
                debug_log.error("price_manager", f"Error in update scheduler: {str(e)}")
            
            # Sleep until next update
            await asyncio.sleep(self.update_schedule_minutes * 60)
    
    @log_function()
    async def _create_default_sources(self):
        """
        Create default price sources if none exist.
        """
        debug_log.info("price_manager", "Creating default price sources")
        
        # Define default sources
        default_sources = [
            {
                "name": "LiteLLM",
                "description": "LiteLLM's pricing database",
                "url": "https://api.litellm.ai",
                "type": "api",
                "trust_score": 0.9,
                "update_frequency": 360,  # 6 hours
                "is_active": True
            },
            {
                "name": "LLMPrices",
                "description": "LLMPrices.com website scraper",
                "url": "https://llmprices.com",
                "type": "scraper",
                "trust_score": 0.8,
                "update_frequency": 720,  # 12 hours
                "is_active": True
            },
            {
                "name": "PretrainedAI",
                "description": "Pretrained.ai website scraper",
                "url": "https://pretrained.ai",
                "type": "scraper",
                "trust_score": 0.7,
                "update_frequency": 1440,  # 24 hours
                "is_active": True
            }
        ]
        
        # Create sources in the database
        for source_data in default_sources:
            source = PriceSource(
                source_id=str(uuid.uuid4()),
                name=source_data["name"],
                description=source_data["description"],
                url=source_data["url"],
                type=source_data["type"],
                trust_score=source_data["trust_score"],
                update_frequency=source_data["update_frequency"],
                is_active=source_data["is_active"],
                last_update=None,
                next_update=None,
                auth_required=False,
                auth_config={}
            )
            
            source_repo.create(source)
            debug_log.info("price_manager", f"Created price source: {source.name}")
    
    @log_function()
    async def _initialize_adapter(self, source: PriceSource):
        """
        Initialize an adapter for a price source.
        
        Args:
            source: The price source
            
        Returns:
            True if adapter was initialized, False otherwise
        """
        try:
            # Create adapter based on source type
            if source.name == "LiteLLM":
                api_key = os.environ.get("LITELLM_API_KEY")
                adapter = LiteLLMAdapter(
                    source_id=source.source_id,
                    api_key=api_key,
                    cache_dir=os.path.join(self.cache_dir, "litellm")
                )
            elif source.name == "LLMPrices":
                adapter = LLMPricesAdapter(
                    source_id=source.source_id,
                    cache_dir=os.path.join(self.cache_dir, "llmprices")
                )
            elif source.name == "PretrainedAI":
                adapter = PretrainedAIAdapter(
                    source_id=source.source_id,
                    cache_dir=os.path.join(self.cache_dir, "pretrained_ai")
                )
            else:
                debug_log.warn("price_manager", f"Unknown price source type: {source.name}")
                return False
            
            # Store adapter
            self.adapters[source.source_id] = adapter
            debug_log.info("price_manager", f"Initialized adapter for {source.name}")
            return True
        except Exception as e:
            debug_log.error("price_manager", f"Error initializing adapter for {source.name}: {str(e)}")
            return False
    
    @log_function()
    async def update_all_prices(self) -> Dict[str, Any]:
        """
        Update pricing data from all sources and verify against each other.
        
        Returns:
            Summary of the update operation
        """
        debug_log.info("price_manager", "Updating prices from all sources")
        
        results = {}
        all_prices = {}
        errors = []
        
        # Fetch prices from all sources
        for source_id, adapter in self.adapters.items():
            source = source_repo.get_by_id(source_id)
            if not source:
                continue
                
            try:
                # Perform health check
                is_healthy = await adapter.health_check()
                if not is_healthy:
                    debug_log.warn("price_manager", f"Source {source.name} is not healthy, skipping update")
                    errors.append({
                        "source": source.name,
                        "error": "Source is not healthy",
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                # Fetch prices
                prices = await adapter.fetch_prices()
                
                # Store prices for verification
                all_prices[source_id] = prices
                
                # Update source timestamp
                source_repo.update_source_timestamp(source_id, True)
                
                # Add to results
                results[source.name] = {
                    "status": "success",
                    "models_count": sum(len(models) for models in prices.values()),
                    "providers_count": len(prices),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                debug_log.error("price_manager", f"Error updating prices from {source.name}: {str(e)}")
                errors.append(adapter.format_error(e))
                source_repo.update_source_timestamp(source_id, False)
                
                # Add to results
                results[source.name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Verify and update pricing data in the database
        if all_prices:
            verified_count, updated_count = await self._verify_and_update_prices(all_prices)
            
            # Add verification results to summary
            results["verification"] = {
                "verified_count": verified_count,
                "updated_count": updated_count,
                "timestamp": datetime.now().isoformat()
            }
        
        # Add errors to summary
        if errors:
            results["errors"] = errors
        
        debug_log.info("price_manager", "Price update completed")
        return results
    
    @log_function()
    async def update_prices_from_source(self, source_id: str) -> Dict[str, Any]:
        """
        Update pricing data from a specific source.
        
        Args:
            source_id: The source ID
            
        Returns:
            Summary of the update operation
        """
        debug_log.info("price_manager", f"Updating prices from source {source_id}")
        
        if source_id not in self.adapters:
            debug_log.error("price_manager", f"Source {source_id} not found")
            return {"status": "error", "error": "Source not found"}
        
        source = source_repo.get_by_id(source_id)
        if not source:
            debug_log.error("price_manager", f"Source {source_id} not found in database")
            return {"status": "error", "error": "Source not found in database"}
        
        adapter = self.adapters[source_id]
        
        try:
            # Perform health check
            is_healthy = await adapter.health_check()
            if not is_healthy:
                debug_log.warn("price_manager", f"Source {source.name} is not healthy, skipping update")
                source_repo.update_source_timestamp(source_id, False)
                return {
                    "status": "error",
                    "error": "Source is not healthy",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Fetch prices
            prices = await adapter.fetch_prices()
            
            # Update source timestamp
            source_repo.update_source_timestamp(source_id, True)
            
            # Verify and update pricing data in the database
            verified_count, updated_count = await self._verify_and_update_prices({source_id: prices})
            
            return {
                "status": "success",
                "models_count": sum(len(models) for models in prices.values()),
                "providers_count": len(prices),
                "verified_count": verified_count,
                "updated_count": updated_count,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            debug_log.error("price_manager", f"Error updating prices from {source.name}: {str(e)}")
            source_repo.update_source_timestamp(source_id, False)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @log_function()
    async def _verify_and_update_prices(
        self,
        all_prices: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]
    ) -> tuple:
        """
        Verify and update pricing data in the database.
        
        Args:
            all_prices: Pricing data from all sources
            
        Returns:
            Tuple of (verified_count, updated_count)
        """
        debug_log.info("price_manager", "Verifying and updating prices")
        
        verified_count = 0
        updated_count = 0
        
        # Collect all provider/model pairs
        all_models = set()
        for source_prices in all_prices.values():
            for provider, models in source_prices.items():
                for model in models:
                    all_models.add((provider, model))
        
        # Process each provider/model pair
        for provider, model in all_models:
            # Collect prices for this model from all sources
            model_prices = {}
            for source_id, source_prices in all_prices.items():
                if provider in source_prices and model in source_prices[provider]:
                    model_prices[source_id] = source_prices[provider][model]
            
            # Skip if only one source has this model
            if len(model_prices) < 2:
                debug_log.debug("price_manager", 
                               f"Skipping verification for {provider}/{model}: Only one source")
                
                # Still update the price if it's from a trusted source
                if len(model_prices) == 1:
                    source_id = list(model_prices.keys())[0]
                    if self.source_trust_scores.get(source_id, 0.0) >= 0.8:
                        updated = await self._update_price(
                            provider, model, source_id, model_prices[source_id],
                            False  # Not verified by multiple sources
                        )
                        if updated:
                            updated_count += 1
                
                continue
            
            # Verify prices across sources
            verified, primary_source_id = self._verify_price_agreement(provider, model, model_prices)
            
            if verified:
                verified_count += 1
                updated = await self._update_price(
                    provider, model, primary_source_id, model_prices[primary_source_id],
                    True  # Verified by multiple sources
                )
                if updated:
                    updated_count += 1
            else:
                debug_log.warn("price_manager", 
                              f"Price verification failed for {provider}/{model}: Sources disagree")
                
                # Create a conflict alert (in a real implementation)
                # This would trigger a process for manual review or resolution
                
                # Still update with the most trusted source
                best_source_id = max(model_prices.keys(), 
                                    key=lambda s: self.source_trust_scores.get(s, 0.0))
                
                updated = await self._update_price(
                    provider, model, best_source_id, model_prices[best_source_id],
                    False  # Not verified by multiple sources
                )
                if updated:
                    updated_count += 1
        
        debug_log.info("price_manager", 
                     f"Price verification completed: {verified_count} verified, {updated_count} updated")
        return verified_count, updated_count
    
    @log_function()
    def _verify_price_agreement(
        self,
        provider: str,
        model: str,
        model_prices: Dict[str, Dict[str, Any]]
    ) -> tuple:
        """
        Verify price agreement across multiple sources.
        
        Args:
            provider: The provider name
            model: The model name
            model_prices: Pricing data from all sources
            
        Returns:
            Tuple of (verified, primary_source_id)
        """
        # Get the most trusted source as primary
        primary_source_id = max(model_prices.keys(), 
                               key=lambda s: self.source_trust_scores.get(s, 0.0))
        primary_price = model_prices[primary_source_id]
        
        # Count agreements
        agreements = 0
        total_sources = len(model_prices)
        
        for source_id, price_data in model_prices.items():
            if source_id == primary_source_id:
                agreements += 1
                continue
            
            # Check if prices are within tolerance
            input_price_match = self._is_price_match(
                primary_price.get("input_cost_per_token", 0.0),
                price_data.get("input_cost_per_token", 0.0)
            )
            
            output_price_match = self._is_price_match(
                primary_price.get("output_cost_per_token", 0.0),
                price_data.get("output_cost_per_token", 0.0)
            )
            
            if input_price_match and output_price_match:
                agreements += 1
        
        # Calculate agreement ratio
        agreement_ratio = agreements / total_sources
        
        # Determine if verification passes
        verified = agreement_ratio >= self.verification_threshold
        
        debug_log.debug("price_manager", 
                       f"Price verification for {provider}/{model}: " +
                       f"{agreements}/{total_sources} sources agree " +
                       f"({agreement_ratio:.2f}), verified={verified}")
        
        return verified, primary_source_id
    
    @log_function()
    def _is_price_match(self, price1: float, price2: float) -> bool:
        """
        Check if two prices are within tolerance.
        
        Args:
            price1: First price
            price2: Second price
            
        Returns:
            True if prices match within tolerance, False otherwise
        """
        # If both prices are zero, consider them matching
        if price1 == 0.0 and price2 == 0.0:
            return True
        
        # If one price is zero and the other is not, they don't match
        if price1 == 0.0 or price2 == 0.0:
            return False
        
        # Calculate difference as a percentage of the larger price
        max_price = max(price1, price2)
        difference = abs(price1 - price2) / max_price
        
        return difference <= self.price_tolerance
    
    @log_function()
    async def _update_price(
        self,
        provider: str,
        model: str,
        source_id: str,
        price_data: Dict[str, Any],
        verified: bool
    ) -> bool:
        """
        Update a price in the database.
        
        Args:
            provider: The provider name
            model: The model name
            source_id: The source ID
            price_data: The pricing data
            verified: Whether the price was verified by multiple sources
            
        Returns:
            True if the price was updated, False otherwise
        """
        source = source_repo.get_by_id(source_id)
        if not source:
            debug_log.error("price_manager", f"Source {source_id} not found in database")
            return False
        
        adapter = self.adapters.get(source_id)
        if not adapter:
            debug_log.error("price_manager", f"Adapter for source {source_id} not found")
            return False
        
        try:
            # Check if there is a current price
            current_pricing = pricing_repo.get_current_pricing(provider, model)
            
            # Create pricing object
            new_pricing = adapter.create_pricing_object(provider, model, price_data)
            new_pricing.verified = verified
            
            # Set the source details
            new_pricing.source = source_id
            
            # Save the new pricing
            saved_pricing = pricing_repo.create(new_pricing)
            
            # If there was a previous price, create an update record
            if current_pricing:
                changes = self._calculate_price_changes(current_pricing, new_pricing)
                
                update_record = PriceUpdateRecord(
                    update_id=str(uuid.uuid4()),
                    provider=provider,
                    model=model,
                    previous_pricing_id=current_pricing.pricing_id,
                    new_pricing_id=saved_pricing.pricing_id,
                    source=source_id,
                    verification_status="verified" if verified else "unverified",
                    timestamp=datetime.now(),
                    changes=changes
                )
                
                update_repo.create(update_record)
            
            debug_log.info("price_manager", 
                         f"Updated price for {provider}/{model} from {source.name}")
            return True
        except Exception as e:
            debug_log.error("price_manager", 
                          f"Error updating price for {provider}/{model}: {str(e)}")
            return False
    
    @log_function()
    def _calculate_price_changes(
        self,
        old_pricing: ProviderPricing,
        new_pricing: ProviderPricing
    ) -> Dict[str, Any]:
        """
        Calculate changes between two pricing objects.
        
        Args:
            old_pricing: The old pricing object
            new_pricing: The new pricing object
            
        Returns:
            Dictionary of changes
        """
        changes = {}
        
        # Check input price change
        old_input = old_pricing.input_cost_per_token
        new_input = new_pricing.input_cost_per_token
        if old_input != new_input:
            changes["input_cost_per_token"] = {
                "old": old_input,
                "new": new_input,
                "change_percent": (
                    ((new_input - old_input) / old_input * 100)
                    if old_input > 0 else None
                )
            }
        
        # Check output price change
        old_output = old_pricing.output_cost_per_token
        new_output = new_pricing.output_cost_per_token
        if old_output != new_output:
            changes["output_cost_per_token"] = {
                "old": old_output,
                "new": new_output,
                "change_percent": (
                    ((new_output - old_output) / old_output * 100)
                    if old_output > 0 else None
                )
            }
        
        # Add other fields that changed
        for field in ["price_type", "input_cost_per_char", "output_cost_per_char",
                     "cost_per_image", "cost_per_second", "fixed_cost_per_request"]:
            old_value = getattr(old_pricing, field)
            new_value = getattr(new_pricing, field)
            
            if old_value != new_value:
                changes[field] = {
                    "old": old_value,
                    "new": new_value
                }
        
        return changes

# Create global instance
price_manager = PriceManager()