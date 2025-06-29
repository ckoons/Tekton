#!/usr/bin/env python3
"""
AI Config Sync Service

Synchronizes the AI configuration file with the AI Registry state.
This runs periodically and checks if Rhetor has made changes that need
to be persisted to the config file.
"""
import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
sys.path.insert(0, tekton_root)

from shared.ai.registry_client import AIRegistryClient

logger = logging.getLogger(__name__)


class AIConfigSync:
    """
    Synchronizes AI configuration between the config file and registry.
    
    Flow:
    1. Rhetor updates registry and sets "last_updated" timestamp
    2. This service checks timestamp periodically
    3. If timestamp is set, sync registry state to config and clear timestamp
    """
    
    def __init__(self):
        self.registry = AIRegistryClient()
        self.config_path = Path(tekton_root) / "config" / "tekton_ai_config.json"
        self.sync_interval = 30  # Check every 30 seconds
        self._running = False
        
    def load_config(self) -> Dict[str, Any]:
        """Load the current AI configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "description": "Tekton AI Platform Configuration",
            "last_sync": None,
            "ai_specialists": {}
        }
    
    def save_config(self, config: Dict[str, Any]):
        """Save the AI configuration atomically."""
        # Update last sync time
        config["last_sync"] = datetime.now().isoformat()
        
        # Write to temp file first
        temp_path = self.config_path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Atomic rename
        temp_path.replace(self.config_path)
        logger.info(f"Saved AI config with {len(config.get('ai_specialists', {}))} specialists")
    
    def check_registry_update_flag(self) -> Optional[float]:
        """
        Check if Rhetor has marked the registry as updated.
        
        Returns:
            Timestamp if update flag is set, None otherwise
        """
        # Check for update marker file
        update_marker = self.registry.registry_base / '.config_update_needed'
        if update_marker.exists():
            try:
                with open(update_marker, 'r') as f:
                    data = json.load(f)
                    return data.get('timestamp')
            except Exception as e:
                logger.error(f"Failed to read update marker: {e}")
        return None
    
    def clear_update_flag(self):
        """Clear the registry update flag."""
        update_marker = self.registry.registry_base / '.config_update_needed'
        if update_marker.exists():
            try:
                update_marker.unlink()
                logger.debug("Cleared update flag")
            except Exception as e:
                logger.error(f"Failed to clear update flag: {e}")
    
    def sync_from_registry(self):
        """
        Sync the current registry state to the config file.
        
        This is called when Rhetor has made changes that need to be persisted.
        """
        try:
            # Load current config
            config = self.load_config()
            
            # Get all AIs from registry
            registry_ais = self.registry.list_platform_ais()
            
            # Update config with registry state
            for ai_id, ai_data in registry_ais.items():
                component = ai_data.get('component', ai_id)
                
                # Preserve existing config if available, update with registry data
                if component in config['ai_specialists']:
                    # Update port and metadata from registry
                    config['ai_specialists'][component]['port'] = ai_data['port']
                    config['ai_specialists'][component]['active'] = True
                    
                    # Merge metadata
                    if 'metadata' in ai_data:
                        if 'metadata' not in config['ai_specialists'][component]:
                            config['ai_specialists'][component]['metadata'] = {}
                        config['ai_specialists'][component]['metadata'].update(ai_data['metadata'])
                else:
                    # New AI not in config - add it
                    config['ai_specialists'][component] = {
                        'component': component,
                        'port': ai_data['port'],
                        'active': True,
                        'auto_start': False,  # Don't auto-start newly discovered AIs
                        'metadata': ai_data.get('metadata', {}),
                        'model': 'llama3.3:70b',  # Default model
                        'roles': [self.registry._component_to_role(component)]
                    }
                    logger.info(f"Added new AI to config: {component}")
            
            # Mark inactive AIs that are in config but not registry
            for component in config['ai_specialists']:
                if component + '-ai' not in registry_ais:
                    config['ai_specialists'][component]['active'] = False
            
            # Save updated config
            self.save_config(config)
            
            # Clear the update flag
            self.clear_update_flag()
            
            logger.info("Successfully synced registry to config")
            
        except Exception as e:
            logger.error(f"Failed to sync from registry: {e}")
    
    async def run_sync_loop(self):
        """Run the periodic sync check loop."""
        self._running = True
        logger.info(f"Starting AI config sync service (checking every {self.sync_interval}s)")
        
        while self._running:
            try:
                # Check if sync is needed
                update_timestamp = self.check_registry_update_flag()
                
                if update_timestamp:
                    logger.info(f"Registry update detected (timestamp: {update_timestamp})")
                    self.sync_from_registry()
                else:
                    logger.debug("No registry updates to sync")
                
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
            
            # Wait for next check
            await asyncio.sleep(self.sync_interval)
    
    def stop(self):
        """Stop the sync service."""
        self._running = False
        logger.info("Stopping AI config sync service")


def main():
    """Run the AI config sync service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [AI_CONFIG_SYNC] [%(levelname)s] %(message)s'
    )
    
    sync_service = AIConfigSync()
    
    try:
        # Run the sync loop
        asyncio.run(sync_service.run_sync_loop())
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        sync_service.stop()


if __name__ == '__main__':
    main()