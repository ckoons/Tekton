"""
Tests for the Hermes integration helper module.
"""

import os
import sys
import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock, mock_open

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.env import TektonEnviron

# Add the parent directory to sys.path to ensure package imports work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from budget.utils.hermes_helper import HermesRegistrationClient, register_budget_component


class TestHermesHelper:
    """Tests for the Hermes helper module."""

    @pytest.mark.asyncio
    async def test_register_file_based(self):
        """Test file-based registration when Hermes API is not available."""
        
        # Mock necessary components
        hermes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Hermes")
        m_open = mock_open()
        
        with patch("os.path.exists", return_value=True), \
             patch("os.makedirs"), \
             patch("json.dump"), \
             patch("builtins.open", m_open), \
             patch("budget.utils.hermes_helper.HermesRegistrationClient._start_heartbeat") as m_heartbeat:
            
            client = HermesRegistrationClient(
                component_id="budget",
                component_name="Budget",
                component_type="budget_manager"
            )
            
            # Force file-based registration
            result = await client._register_via_file()
            
            # Assert
            assert result is True
            assert client._is_registered is True
            m_heartbeat.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_register_via_api_failure(self):
        """Test recovery when API registration fails."""
        
        # Create a mock aiohttp ClientSession
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = asyncio.coroutine(lambda: "Internal server error")
        mock_response.__aenter__ = asyncio.coroutine(lambda *args, **kwargs: mock_response)
        mock_response.__aexit__ = asyncio.coroutine(lambda *args, **kwargs: None)
        
        mock_session = MagicMock()
        mock_session.post = asyncio.coroutine(lambda *args, **kwargs: mock_response)
        mock_session.__aenter__ = asyncio.coroutine(lambda *args, **kwargs: mock_session)
        mock_session.__aexit__ = asyncio.coroutine(lambda *args, **kwargs: None)
        
        # Mock registration
        with patch("aiohttp.ClientSession", return_value=mock_session), \
             patch("budget.utils.hermes_helper.HermesRegistrationClient._register_via_file") as mock_file_reg:
            
            mock_file_reg.return_value = True
            
            client = HermesRegistrationClient()
            result = await client.register()
            
            # Assert that when API fails, it falls back to file-based
            assert result is True
            mock_file_reg.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_heartbeat_loop(self):
        """Test the heartbeat loop sends heartbeats as expected."""
        
        # Create a mock aiohttp ClientSession
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__aenter__ = asyncio.coroutine(lambda *args, **kwargs: mock_response)
        mock_response.__aexit__ = asyncio.coroutine(lambda *args, **kwargs: None)
        
        mock_session = MagicMock()
        mock_session.post = asyncio.coroutine(lambda *args, **kwargs: mock_response)
        mock_session.__aenter__ = asyncio.coroutine(lambda *args, **kwargs: mock_session)
        mock_session.__aexit__ = asyncio.coroutine(lambda *args, **kwargs: None)
        
        # Mock asyncio.sleep to speed up the test
        original_wait_for = asyncio.wait_for
        
        async def mock_wait_for(awaitable, timeout):
            # Raise TimeoutError on first call, then set shutdown event on second call
            if hasattr(mock_wait_for, 'called'):
                client._shutdown_event.set()
                return None
            mock_wait_for.called = True
            raise asyncio.TimeoutError()
        
        with patch("aiohttp.ClientSession", return_value=mock_session), \
             patch("asyncio.wait_for", side_effect=mock_wait_for):
            
            client = HermesRegistrationClient(heartbeat_interval=0.1)
            await client._heartbeat_loop()
            
            # Assert that the heartbeat was sent
            assert mock_session.post.call_count == 1
            
    @pytest.mark.asyncio
    async def test_register_budget_component(self):
        """Test the register_budget_component helper function."""
        
        with patch("budget.utils.hermes_helper.HermesRegistrationClient.register") as mock_register:
            mock_register.return_value = True
            
            with patch("budget.utils.hermes_helper.HermesRegistrationClient") as MockClient:
                mock_client = MagicMock()
                MockClient.return_value = mock_client
                
                endpoint = "http://localhost:8013"
                result = await register_budget_component(endpoint)
                
                # Assert client was created and register was called
                assert result is mock_client
                MockClient.assert_called_with(
                    component_version=TektonEnviron.get("BUDGET_VERSION", "0.1.0"),
                    endpoint=endpoint
                )
                mock_register.assert_called_once()