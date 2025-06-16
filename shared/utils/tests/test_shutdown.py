"""
Tests for graceful shutdown utilities.
"""
import pytest
import asyncio
import signal
from unittest.mock import Mock, patch, AsyncMock
from contextlib import asynccontextmanager

from shared.utils.shutdown import (
    GracefulShutdown,
    component_lifespan,
    create_shutdown_handler,
    ShutdownMetrics
)
from shared.utils.errors import ShutdownError


@pytest.mark.asyncio
async def test_graceful_shutdown_init():
    """Test GracefulShutdown initialization."""
    shutdown = GracefulShutdown("test_component")
    
    assert shutdown.component_name == "test_component"
    assert not shutdown.shutdown_event.is_set()
    assert len(shutdown.cleanup_tasks) == 0


@pytest.mark.asyncio
async def test_register_cleanup():
    """Test cleanup task registration."""
    shutdown = GracefulShutdown("test_component")
    
    cleanup1 = AsyncMock()
    cleanup2 = AsyncMock()
    
    shutdown.register_cleanup(cleanup1)
    shutdown.register_cleanup(cleanup2)
    
    assert len(shutdown.cleanup_tasks) == 2


@pytest.mark.asyncio
async def test_shutdown_sequence():
    """Test shutdown sequence executes all cleanup tasks."""
    shutdown = GracefulShutdown("test_component")
    
    cleanup1 = AsyncMock()
    cleanup2 = AsyncMock()
    cleanup3 = AsyncMock()
    
    shutdown.register_cleanup(cleanup1)
    shutdown.register_cleanup(cleanup2)
    shutdown.register_cleanup(cleanup3)
    
    metrics = await shutdown.shutdown_sequence()
    
    cleanup1.assert_called_once()
    cleanup2.assert_called_once()
    cleanup3.assert_called_once()
    
    assert metrics.component_name == "test_component"
    assert metrics.cleanup_tasks_completed == 3
    assert metrics.total_time > 0


@pytest.mark.asyncio
async def test_shutdown_with_timeout():
    """Test shutdown timeout handling."""
    shutdown = GracefulShutdown("test_component")
    
    async def slow_cleanup():
        await asyncio.sleep(5)
    
    shutdown.register_cleanup(slow_cleanup)
    
    # Should timeout after 1 second
    metrics = await shutdown.shutdown_sequence(timeout=1)
    
    assert metrics.cleanup_tasks_completed == 0
    assert metrics.timeout_occurred
    assert metrics.total_time >= 1.0


@pytest.mark.asyncio
async def test_shutdown_with_failing_cleanup():
    """Test shutdown continues even if cleanup task fails."""
    shutdown = GracefulShutdown("test_component")
    
    async def failing_cleanup():
        raise Exception("Cleanup failed")
    
    cleanup_success = AsyncMock()
    
    shutdown.register_cleanup(failing_cleanup)
    shutdown.register_cleanup(cleanup_success)
    
    metrics = await shutdown.shutdown_sequence()
    
    cleanup_success.assert_called_once()
    assert metrics.cleanup_tasks_completed == 1
    assert len(metrics.cleanup_errors) == 1


@pytest.mark.asyncio
async def test_signal_handling():
    """Test signal handler sets shutdown event."""
    with patch('signal.signal') as mock_signal:
        shutdown = GracefulShutdown("test_component")
        
        # Verify signals were registered
        assert mock_signal.call_count == 2
        calls = mock_signal.call_args_list
        assert calls[0][0][0] == signal.SIGTERM
        assert calls[1][0][0] == signal.SIGINT
        
        # Simulate signal
        shutdown._handle_signal(signal.SIGTERM, None)
        assert shutdown.shutdown_event.is_set()


@pytest.mark.asyncio
async def test_component_lifespan():
    """Test FastAPI lifespan context manager."""
    startup_called = False
    cleanup_called = False
    
    async def startup_func():
        nonlocal startup_called
        startup_called = True
    
    async def cleanup_func():
        nonlocal cleanup_called
        cleanup_called = True
    
    app = Mock()  # Mock FastAPI app
    
    async with component_lifespan(
        "test_component",
        startup_func,
        [cleanup_func]
    )(app):
        assert startup_called
        assert not cleanup_called
    
    assert cleanup_called


@pytest.mark.asyncio
async def test_create_shutdown_handler():
    """Test creating standardized shutdown handler."""
    cleanup1 = AsyncMock()
    cleanup2 = AsyncMock()
    
    handler = create_shutdown_handler(
        "test_component",
        [cleanup1, cleanup2]
    )
    
    await handler()
    
    cleanup1.assert_called_once()
    cleanup2.assert_called_once()


@pytest.mark.asyncio
async def test_shutdown_metrics():
    """Test shutdown metrics collection."""
    shutdown = GracefulShutdown("test_component")
    
    async def fast_cleanup():
        await asyncio.sleep(0.1)
    
    async def medium_cleanup():
        await asyncio.sleep(0.2)
    
    shutdown.register_cleanup(fast_cleanup)
    shutdown.register_cleanup(medium_cleanup)
    
    metrics = await shutdown.shutdown_sequence()
    
    assert metrics.component_name == "test_component"
    assert metrics.cleanup_tasks_completed == 2
    assert metrics.total_time >= 0.2  # Should run in parallel
    assert metrics.total_time < 0.5   # But not sequentially
    assert not metrics.timeout_occurred
    assert len(metrics.cleanup_errors) == 0


@pytest.mark.asyncio
async def test_shutdown_with_dependencies():
    """Test shutdown with dependency cleanup order."""
    call_order = []
    
    async def cleanup_connections():
        call_order.append("connections")
        await asyncio.sleep(0.1)
    
    async def cleanup_cache():
        call_order.append("cache")
        await asyncio.sleep(0.1)
    
    async def cleanup_logs():
        call_order.append("logs")
    
    shutdown = GracefulShutdown("test_component")
    
    # Register in dependency order
    shutdown.register_cleanup(cleanup_connections)
    shutdown.register_cleanup(cleanup_cache)
    shutdown.register_cleanup(cleanup_logs)
    
    await shutdown.shutdown_sequence()
    
    # Should execute in parallel, so order might vary
    assert len(call_order) == 3
    assert "connections" in call_order
    assert "cache" in call_order
    assert "logs" in call_order


if __name__ == "__main__":
    pytest.main([__file__, "-v"])