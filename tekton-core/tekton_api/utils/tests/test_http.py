"""
Tests for the Tekton HTTP utility.
"""

import os
import json
import asyncio
import unittest
from unittest import mock

import aiohttp
from aiohttp import ClientResponseError

from tekton.utils.tekton_http import (
    http_request,
    HTTPClient,
    create_client_from_env,
    create_hermes_client,
    TektonHTTPError,
    TektonConnectionError,
    TektonTimeoutError,
    TektonAuthenticationError,
    TektonNotFoundError,
    TektonServerError
)


class MockResponse:
    """Mock for aiohttp response."""
    
    def __init__(self, status, json_data=None, text=None, content_type='application/json'):
        self.status = status
        self._json_data = json_data
        self._text = text or json.dumps(json_data) if json_data else ""
        self.headers = {'Content-Type': content_type}
        self.raise_for_status_called = False
    
    async def json(self):
        return self._json_data
    
    async def text(self):
        return self._text
    
    async def read(self):
        return self._text.encode('utf-8')
    
    def raise_for_status(self):
        self.raise_for_status_called = True
        if self.status >= 400:
            raise ClientResponseError(
                request_info=mock.Mock(),
                history=mock.Mock(),
                status=self.status,
                message=f"HTTP Error {self.status}",
                headers=self.headers
            )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestHTTPUtils(unittest.TestCase):
    """Test HTTP utility functions."""
    
    def setUp(self):
        """Set up tests."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up tests."""
        self.loop.close()
    
    def test_create_client_from_env(self):
        """Test creating client from environment variables."""
        with mock.patch.dict(os.environ, {"TEST_PORT": "8001"}):
            client = create_client_from_env("test")
            self.assertEqual(client.base_url, "http://localhost:8001")
    
    def test_create_hermes_client(self):
        """Test creating Hermes client."""
        client = create_hermes_client()
        self.assertEqual(client.base_url, "http://localhost:8001")


class TestHTTPRequest(unittest.TestCase):
    """Test HTTP request function."""
    
    def setUp(self):
        """Set up tests."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Create mock ClientSession
        self.mock_session = mock.Mock()
        self.mock_session.request = mock.AsyncMock()
        self.mock_session.close = mock.AsyncMock()
    
    def tearDown(self):
        """Clean up tests."""
        self.loop.close()
    
    async def _test_http_request_success(self):
        """Test successful HTTP request."""
        self.mock_session.request.return_value = MockResponse(
            200, 
            json_data={"status": "success"}
        )
        
        result = await http_request(
            "GET", 
            "http://localhost:8000/api/test",
            session=self.mock_session
        )
        
        self.assertEqual(result, {"status": "success"})
        self.mock_session.request.assert_called_once()
    
    def test_http_request_success(self):
        """Run async test for successful HTTP request."""
        self.loop.run_until_complete(self._test_http_request_success())
    
    async def _test_http_request_retry(self):
        """Test HTTP request with retry."""
        # Set up mock to fail on first call then succeed
        self.mock_session.request.side_effect = [
            ClientResponseError(
                request_info=mock.Mock(),
                history=mock.Mock(),
                status=502,
                message="Bad Gateway",
                headers={}
            ),
            MockResponse(200, json_data={"status": "success"})
        ]
        
        result = await http_request(
            "GET", 
            "http://localhost:8000/api/test",
            retries=1,
            session=self.mock_session
        )
        
        self.assertEqual(result, {"status": "success"})
        self.assertEqual(self.mock_session.request.call_count, 2)
    
    def test_http_request_retry(self):
        """Run async test for HTTP request with retry."""
        self.loop.run_until_complete(self._test_http_request_retry())
    
    async def _test_http_request_auth_error(self):
        """Test HTTP request with authentication error."""
        self.mock_session.request.side_effect = ClientResponseError(
            request_info=mock.Mock(),
            history=mock.Mock(),
            status=401,
            message="Unauthorized",
            headers={}
        )
        
        with self.assertRaises(TektonAuthenticationError):
            await http_request(
                "GET", 
                "http://localhost:8000/api/test",
                session=self.mock_session
            )
    
    def test_http_request_auth_error(self):
        """Run async test for HTTP request with authentication error."""
        self.loop.run_until_complete(self._test_http_request_auth_error())
    
    async def _test_http_request_not_found(self):
        """Test HTTP request with not found error."""
        self.mock_session.request.side_effect = ClientResponseError(
            request_info=mock.Mock(),
            history=mock.Mock(),
            status=404,
            message="Not Found",
            headers={}
        )
        
        with self.assertRaises(TektonNotFoundError):
            await http_request(
                "GET", 
                "http://localhost:8000/api/test",
                session=self.mock_session
            )
    
    def test_http_request_not_found(self):
        """Run async test for HTTP request with not found error."""
        self.loop.run_until_complete(self._test_http_request_not_found())
    
    async def _test_http_request_server_error(self):
        """Test HTTP request with server error."""
        self.mock_session.request.side_effect = ClientResponseError(
            request_info=mock.Mock(),
            history=mock.Mock(),
            status=500,
            message="Internal Server Error",
            headers={}
        )
        
        with self.assertRaises(TektonServerError):
            await http_request(
                "GET", 
                "http://localhost:8000/api/test",
                session=self.mock_session
            )
    
    def test_http_request_server_error(self):
        """Run async test for HTTP request with server error."""
        self.loop.run_until_complete(self._test_http_request_server_error())
    
    async def _test_http_request_connection_error(self):
        """Test HTTP request with connection error."""
        self.mock_session.request.side_effect = aiohttp.ClientConnectorError(
            mock.Mock(),
            OSError("Connection refused")
        )
        
        with self.assertRaises(TektonConnectionError):
            await http_request(
                "GET", 
                "http://localhost:8000/api/test",
                session=self.mock_session
            )
    
    def test_http_request_connection_error(self):
        """Run async test for HTTP request with connection error."""
        self.loop.run_until_complete(self._test_http_request_connection_error())
    
    async def _test_http_request_timeout(self):
        """Test HTTP request with timeout."""
        self.mock_session.request.side_effect = asyncio.TimeoutError()
        
        with self.assertRaises(TektonTimeoutError):
            await http_request(
                "GET", 
                "http://localhost:8000/api/test",
                session=self.mock_session
            )
    
    def test_http_request_timeout(self):
        """Run async test for HTTP request with timeout."""
        self.loop.run_until_complete(self._test_http_request_timeout())


class TestHTTPClient(unittest.TestCase):
    """Test HTTP client class."""
    
    def setUp(self):
        """Set up tests."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Create a client with a mock session
        self.client = HTTPClient(base_url="http://localhost:8000")
        self.client.session = mock.Mock()
        self.client.session.request = mock.AsyncMock()
        self.client.session.close = mock.AsyncMock()
    
    def tearDown(self):
        """Clean up tests."""
        self.loop.close()
    
    async def _test_client_get(self):
        """Test HTTP client GET method."""
        # Set up mock response
        self.client.session.request.return_value = MockResponse(
            200, 
            json_data={"status": "success"}
        )
        
        # Make request
        result = await self.client.get("/api/test")
        
        # Check result
        self.assertEqual(result, {"status": "success"})
        
        # Check request call
        self.client.session.request.assert_called_once_with(
            method="GET",
            url="http://localhost:8000/api/test",
            params=None,
            headers={},
            data=None,
            json=None,
            ssl=None,
            raise_for_status=True
        )
    
    def test_client_get(self):
        """Run async test for HTTP client GET method."""
        self.loop.run_until_complete(self._test_client_get())
    
    async def _test_client_post(self):
        """Test HTTP client POST method."""
        # Set up mock response
        self.client.session.request.return_value = MockResponse(
            200, 
            json_data={"status": "success"}
        )
        
        # Make request
        result = await self.client.post(
            "/api/test",
            json_data={"data": "test"}
        )
        
        # Check result
        self.assertEqual(result, {"status": "success"})
        
        # Check request call
        self.client.session.request.assert_called_once_with(
            method="POST",
            url="http://localhost:8000/api/test",
            params=None,
            headers={},
            data=None,
            json={"data": "test"},
            ssl=None,
            raise_for_status=True
        )
    
    def test_client_post(self):
        """Run async test for HTTP client POST method."""
        self.loop.run_until_complete(self._test_client_post())
    
    async def _test_client_put(self):
        """Test HTTP client PUT method."""
        # Set up mock response
        self.client.session.request.return_value = MockResponse(
            200, 
            json_data={"status": "success"}
        )
        
        # Make request
        result = await self.client.put(
            "/api/test",
            json_data={"data": "test"}
        )
        
        # Check result
        self.assertEqual(result, {"status": "success"})
        
        # Check request call
        self.client.session.request.assert_called_once_with(
            method="PUT",
            url="http://localhost:8000/api/test",
            params=None,
            headers={},
            data=None,
            json={"data": "test"},
            ssl=None,
            raise_for_status=True
        )
    
    def test_client_put(self):
        """Run async test for HTTP client PUT method."""
        self.loop.run_until_complete(self._test_client_put())
    
    async def _test_client_delete(self):
        """Test HTTP client DELETE method."""
        # Set up mock response
        self.client.session.request.return_value = MockResponse(
            200, 
            json_data={"status": "success"}
        )
        
        # Make request
        result = await self.client.delete("/api/test")
        
        # Check result
        self.assertEqual(result, {"status": "success"})
        
        # Check request call
        self.client.session.request.assert_called_once_with(
            method="DELETE",
            url="http://localhost:8000/api/test",
            params=None,
            headers={},
            data=None,
            json=None,
            ssl=None,
            raise_for_status=True
        )
    
    def test_client_delete(self):
        """Run async test for HTTP client DELETE method."""
        self.loop.run_until_complete(self._test_client_delete())
    
    async def _test_client_request_with_auth(self):
        """Test HTTP client request with authentication."""
        # Create client with auth token
        client = HTTPClient(
            base_url="http://localhost:8000",
            auth_token="test_token"
        )
        client.session = mock.Mock()
        client.session.request = mock.AsyncMock()
        client.session.close = mock.AsyncMock()
        
        # Set up mock response
        client.session.request.return_value = MockResponse(
            200, 
            json_data={"status": "success"}
        )
        
        # Make request
        result = await client.get("/api/test")
        
        # Check result
        self.assertEqual(result, {"status": "success"})
        
        # Check request call includes auth header
        client.session.request.assert_called_once()
        call_kwargs = client.session.request.call_args[1]
        self.assertEqual(call_kwargs["headers"], {"Authorization": "Bearer test_token"})
    
    def test_client_request_with_auth(self):
        """Run async test for HTTP client request with authentication."""
        self.loop.run_until_complete(self._test_client_request_with_auth())
    
    async def _test_client_context_manager(self):
        """Test HTTP client as context manager."""
        client = HTTPClient(base_url="http://localhost:8000")
        
        # Replace initialize and close with mocks
        client.initialize = mock.AsyncMock()
        client.close = mock.AsyncMock()
        
        # Use as context manager
        async with client:
            pass
        
        # Check methods called
        client.initialize.assert_called_once()
        client.close.assert_called_once()
    
    def test_client_context_manager(self):
        """Run async test for HTTP client as context manager."""
        self.loop.run_until_complete(self._test_client_context_manager())


if __name__ == '__main__':
    unittest.main()