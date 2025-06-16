"""
Tests for the Unified Registration Protocol implementation.
"""

import unittest
import asyncio
import time
import uuid
from unittest.mock import MagicMock, patch

from hermes.core.service_discovery import ServiceRegistry
from hermes.core.message_bus import MessageBus
from hermes.core.registration import RegistrationManager, RegistrationClient, RegistrationToken


class TestRegistrationToken(unittest.TestCase):
    """Test cases for the RegistrationToken class."""
    
    def test_token_generation_validation(self):
        """Test that a token can be generated and validated."""
        # Create a token
        component_id = "test_component"
        secret_key = "test_secret"
        token = RegistrationToken(component_id=component_id, secret_key=secret_key)
        token_str = token.generate()
        
        # Validate the token
        payload = RegistrationToken.validate(token_str, secret_key)
        
        # Check payload
        self.assertIsNotNone(payload)
        self.assertEqual(payload["component_id"], component_id)
        self.assertEqual(payload["token_id"], token.token_id)
        self.assertEqual(payload["iat"], token.issued_at)
        self.assertEqual(payload["exp"], token.expires_at)
    
    def test_invalid_token(self):
        """Test that an invalid token is rejected."""
        # Create a token
        component_id = "test_component"
        secret_key = "test_secret"
        token = RegistrationToken(component_id=component_id, secret_key=secret_key)
        token_str = token.generate()
        
        # Try to validate with wrong secret
        payload = RegistrationToken.validate(token_str, "wrong_secret")
        self.assertIsNone(payload)
    
    def test_expired_token(self):
        """Test that an expired token is rejected."""
        # Create a token with negative expiration
        component_id = "test_component"
        secret_key = "test_secret"
        token = RegistrationToken(component_id=component_id, secret_key=secret_key, expiration=-10)
        token_str = token.generate()
        
        # Try to validate
        payload = RegistrationToken.validate(token_str, secret_key)
        self.assertIsNone(payload)


class TestRegistrationManager(unittest.TestCase):
    """Test cases for the RegistrationManager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mocks
        self.service_registry = MagicMock(spec=ServiceRegistry)
        self.message_bus = MagicMock(spec=MessageBus)
        
        # Create registration manager
        self.secret_key = "test_secret"
        self.manager = RegistrationManager(
            service_registry=self.service_registry,
            message_bus=self.message_bus,
            secret_key=self.secret_key
        )
    
    def test_register_component(self):
        """Test registering a component."""
        # Set up service registry mock
        self.service_registry.register.return_value = True
        
        # Register component
        component_id = "test_component"
        name = "Test Component"
        version = "1.0.0"
        component_type = "test"
        endpoint = "localhost:1234"
        capabilities = ["test.capability1", "test.capability2"]
        
        success, token_str = self.manager.register_component(
            component_id=component_id,
            name=name,
            version=version,
            component_type=component_type,
            endpoint=endpoint,
            capabilities=capabilities
        )
        
        # Check results
        self.assertTrue(success)
        self.assertIsNotNone(token_str)
        
        # Verify service registry was called
        self.service_registry.register.assert_called_once_with(
            service_id=component_id,
            name=name,
            version=version,
            endpoint=endpoint,
            capabilities=capabilities,
            health_check=None,
            metadata={"type": component_type}
        )
        
        # Verify message bus was called
        self.message_bus.publish.assert_called_once()
        args, kwargs = self.message_bus.publish.call_args
        self.assertEqual(kwargs["topic"], "tekton.registration.completed")
    
    def test_unregister_component(self):
        """Test unregistering a component."""
        # Register a component first
        component_id = "test_component"
        self.service_registry.register.return_value = True
        success, token_str = self.manager.register_component(
            component_id=component_id,
            name="Test Component",
            version="1.0.0",
            component_type="test",
            endpoint="localhost:1234",
            capabilities=[]
        )
        
        # Reset mocks
        self.service_registry.reset_mock()
        self.message_bus.reset_mock()
        
        # Set up service registry mock for unregister
        self.service_registry.unregister.return_value = True
        
        # Unregister component
        success = self.manager.unregister_component(
            component_id=component_id,
            token_str=token_str
        )
        
        # Check results
        self.assertTrue(success)
        
        # Verify service registry was called
        self.service_registry.unregister.assert_called_once_with(component_id)
        
        # Verify message bus was called
        self.message_bus.publish.assert_called_once()
        args, kwargs = self.message_bus.publish.call_args
        self.assertEqual(kwargs["topic"], "tekton.registration.revoked")


class TestRegistrationClient(unittest.TestCase):
    """Test cases for the RegistrationClient class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock message bus
        self.message_bus = MagicMock(spec=MessageBus)
        
        # Create registration client
        self.component_id = "test_component"
        self.client = RegistrationClient(
            component_id=self.component_id,
            name="Test Component",
            version="1.0.0",
            component_type="test",
            endpoint="localhost:1234",
            capabilities=["test.capability1", "test.capability2"],
            message_bus=self.message_bus
        )
    
    async def test_register(self):
        """Test registering a component."""
        # Set up message bus mock for publish
        self.message_bus.publish.return_value = True
        
        # Simulate registration response
        def side_effect(topic, callback):
            if topic == f"tekton.registration.response.{self.component_id}":
                # Call the callback with a fake response
                callback({
                    "payload": {
                        "success": True,
                        "token": "fake_token"
                    }
                })
            return True
        
        self.message_bus.subscribe.side_effect = side_effect
        
        # Register component
        success = await self.client.register()
        
        # Check results
        self.assertTrue(success)
        self.assertEqual(self.client.token, "fake_token")
        
        # Verify message bus was called
        self.message_bus.publish.assert_called_once()
        args, kwargs = self.message_bus.publish.call_args
        self.assertEqual(kwargs["topic"], "tekton.registration.request")


if __name__ == "__main__":
    unittest.main()