#!/usr/bin/env python3
"""
Test Registration - Script to test the Unified Registration Protocol.

This script provides a command-line utility for testing the Hermes
registration system by registering a test component, sending heartbeats,
and querying services.
"""

import os
import sys
import time
import argparse
import logging
import json
from typing import Dict, List, Any
from shared.env import TektonEnviron
from shared.urls import tekton_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the test script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test Hermes Registration Protocol")
    parser.add_argument(
        "--api-endpoint",
        default=tekton_url("hermes", "/api"),
        help="Hermes API endpoint URL"
    )
    parser.add_argument(
        "--component-id",
        default=f"test-component-{int(time.time())}",
        help="Component ID to register"
    )
    parser.add_argument(
        "--component-name",
        default="Test Component",
        help="Component name"
    )
    parser.add_argument(
        "--component-type",
        default="test",
        help="Component type"
    )
    parser.add_argument(
        "--action",
        choices=["register", "heartbeat", "unregister", "query", "full-test"],
        default="full-test",
        help="Action to perform"
    )
    parser.add_argument(
        "--heartbeat-count",
        type=int,
        default=3,
        help="Number of heartbeats to send in full test"
    )
    args = parser.parse_args()
    
    try:
        # Import Hermes registration client
        from hermes.core.registration import RegistrationClientAPI
        
        # Create registration client
        client = RegistrationClientAPI(
            component_id=args.component_id,
            name=args.component_name,
            version="1.0.0",
            component_type=args.component_type,
            endpoint=f"http://localhost:8080/{args.component_id}",
            capabilities=["test", "example"],
            api_endpoint=args.api_endpoint,
            metadata={
                "description": "Test component for Hermes registration system",
                "test_instance": True
            }
        )
        
        # Perform requested action
        if args.action == "register":
            _register_component(client)
        elif args.action == "heartbeat":
            _send_heartbeat(client)
        elif args.action == "unregister":
            _unregister_component(client)
        elif args.action == "query":
            _query_services(client)
        elif args.action == "full-test":
            _run_full_test(client, args.heartbeat_count)
        
    except ImportError as e:
        logger.error(f"Failed to import Hermes registration client: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during registration test: {e}")
        sys.exit(2)

def _register_component(client):
    """Register a test component."""
    logger.info(f"Registering component {client.component_id}")
    success = client.register()
    if success:
        logger.info(f"Component registered successfully. Token: {client.token[:10]}...")
    else:
        logger.error("Failed to register component")
        sys.exit(1)

def _send_heartbeat(client):
    """Send a heartbeat for a registered component."""
    if not client.token:
        _register_component(client)
    
    logger.info(f"Sending heartbeat for component {client.component_id}")
    success = client._send_heartbeat()
    if success:
        logger.info("Heartbeat sent successfully")
    else:
        logger.error("Failed to send heartbeat")
        sys.exit(1)

def _unregister_component(client):
    """Unregister a test component."""
    if not client.token:
        _register_component(client)
    
    logger.info(f"Unregistering component {client.component_id}")
    success = client.unregister()
    if success:
        logger.info("Component unregistered successfully")
    else:
        logger.error("Failed to unregister component")
        sys.exit(1)

def _query_services(client):
    """Query services from the registry."""
    logger.info("Querying services")
    services = client.find_services()
    logger.info(f"Found {len(services)} services:")
    for service in services:
        logger.info(f"  {service['name']} ({service['component_id']}) - {service['component_type']}")
        logger.info(f"    Capabilities: {', '.join(service['capabilities'])}")
        logger.info(f"    Endpoint: {service['endpoint']}")
        logger.info(f"    Healthy: {service['healthy']}")

def _run_full_test(client, heartbeat_count):
    """Run a full test of registration, heartbeats, query, and unregistration."""
    # Register component
    _register_component(client)
    
    # Send heartbeats
    logger.info(f"Sending {heartbeat_count} heartbeats...")
    for i in range(heartbeat_count):
        _send_heartbeat(client)
        time.sleep(1)
    
    # Query services
    _query_services(client)
    
    # Unregister component
    _unregister_component(client)
    
    logger.info("Full test completed successfully")

if __name__ == "__main__":
    main()