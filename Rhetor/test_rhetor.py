#!/usr/bin/env python3
"""
Test script for Rhetor LLM Manager.

This script sends a test message to the Rhetor API and prints the response.
"""

import os
from shared.env import TektonEnviron
import sys
import logging
import asyncio
import json
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("rhetor.test")

RHETOR_URL = TektonEnviron.get("RHETOR_URL", "http://localhost:8003")

async def test_providers():
    """Test retrieving available providers."""
    logger.info(f"Testing providers endpoint at {RHETOR_URL}/providers")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{RHETOR_URL}/providers") as resp:
                if resp.status != 200:
                    logger.error(f"Failed to get providers: {resp.status}")
                    return False
                
                providers = await resp.json()
                logger.info(f"Available providers:")
                
                for provider_id, provider_info in providers["providers"].items():
                    availability = "Available" if provider_info["available"] else "Unavailable"
                    logger.info(f"- {provider_info['name']} ({provider_id}): {availability}")
                    
                    if provider_info["available"]:
                        logger.info(f"  Models:")
                        for model in provider_info["models"]:
                            logger.info(f"  - {model['name']} ({model['id']})")
                
                logger.info(f"Default provider: {providers['default_provider']}")
                logger.info(f"Default model: {providers['default_model']}")
                
                return True
    except Exception as e:
        logger.error(f"Error testing providers: {e}")
        return False

async def test_message():
    """Test sending a message."""
    logger.info(f"Testing message endpoint at {RHETOR_URL}/message")
    
    try:
        async with aiohttp.ClientSession() as session:
            message_payload = {
                "message": "Hello, I'm testing the Rhetor LLM Manager. Please respond with a brief greeting.",
                "context_id": "test",
                "task_type": "chat",
                "streaming": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            }
            
            async with session.post(
                f"{RHETOR_URL}/message",
                json=message_payload,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to send message: {resp.status}")
                    return False
                
                response = await resp.json()
                
                if "error" in response:
                    logger.error(f"Error in response: {response['error']}")
                    return False
                
                logger.info(f"Response from {response.get('provider', 'unknown')} model {response.get('model', 'unknown')}:")
                logger.info(f"{response['message']}")
                
                return True
    except Exception as e:
        logger.error(f"Error testing message: {e}")
        return False

async def main():
    """Run the tests."""
    logger.info("Testing Rhetor LLM Manager")
    
    # Test providers
    providers_success = await test_providers()
    if not providers_success:
        logger.error("Provider test failed")
        
    # Test message
    message_success = await test_message()
    if not message_success:
        logger.error("Message test failed")
    
    # Show overall results
    if providers_success and message_success:
        logger.info("All tests passed!")
        return 0
    else:
        logger.error("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))