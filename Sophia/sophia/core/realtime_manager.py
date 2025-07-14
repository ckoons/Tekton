"""
Real-time WebSocket Manager for Sophia

This module provides real-time communication capabilities for theory validation,
experiment monitoring, and metrics streaming using WebSocket connections on
the standard Sophia port (8014) at the /ws endpoint.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from fastapi import WebSocket

from shared.urls import tekton_url

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and real-time event broadcasting for Sophia.
    
    Provides real-time updates for:
    - Theory validation experiments
    - Metrics streaming
    - Experiment monitoring
    - Analysis session collaboration
    """
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: List[WebSocket] = []
        self.client_subscriptions: Dict[str, Set[str]] = {}
        self.experiment_monitors: Dict[str, Set[WebSocket]] = {}
        self.metrics_subscribers: List[WebSocket] = []
        self.theory_subscribers: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket connection
            
        Returns:
            Client ID for the connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
        client_id = f"client_{id(websocket)}_{int(time.time())}"
        self.client_subscriptions[client_id] = set()
        
        # Initialize connection attributes
        websocket.client_id = client_id
        websocket.subscriptions = set()
        websocket.monitored_experiments = set()
        websocket.metrics_filters = []
        websocket.theory_subscriptions = set()
        
        logger.info(f"WebSocket client connected: {client_id}")
        
        # Send welcome message with connection info
        await websocket.send_json({
            "type": "connection_established",
            "client_id": client_id,
            "sophia_url": tekton_url("sophia"),
            "websocket_url": tekton_url("sophia", "/ws", scheme="ws"),
            "timestamp": time.time()
        })
        
        return client_id
    
    def disconnect(self, websocket: WebSocket):
        """
        Handle WebSocket disconnection.
        
        Args:
            websocket: WebSocket connection to remove
        """
        try:
            # Remove from active connections
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            # Clean up subscriptions
            client_id = getattr(websocket, 'client_id', None)
            if client_id and client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]
            
            # Clean up experiment monitoring
            for experiment_id, monitors in self.experiment_monitors.items():
                monitors.discard(websocket)
            
            # Clean up metrics subscriptions
            if websocket in self.metrics_subscribers:
                self.metrics_subscribers.remove(websocket)
            
            # Clean up theory subscriptions
            for validation_type, subscribers in self.theory_subscribers.items():
                subscribers.discard(websocket)
            
            logger.info(f"WebSocket client disconnected: {client_id}")
            
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect cleanup: {e}")
    
    async def subscribe_to_events(self, websocket: WebSocket, event_types: List[str]):
        """
        Subscribe a client to specific event types.
        
        Args:
            websocket: Client WebSocket connection
            event_types: List of event types to subscribe to
        """
        if hasattr(websocket, 'subscriptions'):
            websocket.subscriptions.update(event_types)
        
        client_id = getattr(websocket, 'client_id', 'unknown')
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].update(event_types)
    
    async def monitor_experiment(self, websocket: WebSocket, experiment_id: str):
        """
        Subscribe a client to experiment monitoring.
        
        Args:
            websocket: Client WebSocket connection
            experiment_id: ID of experiment to monitor
        """
        if experiment_id not in self.experiment_monitors:
            self.experiment_monitors[experiment_id] = set()
        
        self.experiment_monitors[experiment_id].add(websocket)
        
        if hasattr(websocket, 'monitored_experiments'):
            websocket.monitored_experiments.add(experiment_id)
    
    async def subscribe_to_metrics(self, websocket: WebSocket, metric_filter: Dict[str, Any]):
        """
        Subscribe a client to real-time metrics streaming.
        
        Args:
            websocket: Client WebSocket connection
            metric_filter: Filter criteria for metrics
        """
        if websocket not in self.metrics_subscribers:
            self.metrics_subscribers.append(websocket)
        
        if hasattr(websocket, 'metrics_filters'):
            websocket.metrics_filters.append(metric_filter)
    
    async def subscribe_to_theory_validation(self, websocket: WebSocket, validation_types: List[str]):
        """
        Subscribe a client to theory validation events.
        
        Args:
            websocket: Client WebSocket connection
            validation_types: Types of validation events to subscribe to
        """
        for validation_type in validation_types:
            if validation_type not in self.theory_subscribers:
                self.theory_subscribers[validation_type] = set()
            self.theory_subscribers[validation_type].add(websocket)
        
        if hasattr(websocket, 'theory_subscriptions'):
            websocket.theory_subscriptions.update(validation_types)
    
    async def broadcast_experiment_update(self, experiment_id: str, update_data: Dict[str, Any]):
        """
        Broadcast experiment status update to all monitoring clients.
        
        Args:
            experiment_id: ID of the experiment
            update_data: Update data to broadcast
        """
        if experiment_id in self.experiment_monitors:
            message = {
                "type": "experiment_update",
                "experiment_id": experiment_id,
                "data": update_data,
                "timestamp": time.time()
            }
            
            disconnected = []
            for websocket in self.experiment_monitors[experiment_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send experiment update to client: {e}")
                    disconnected.append(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                self.experiment_monitors[experiment_id].discard(websocket)
    
    async def broadcast_metrics_update(self, metric_data: Dict[str, Any]):
        """
        Broadcast real-time metrics to subscribed clients.
        
        Args:
            metric_data: Metric data to broadcast
        """
        message = {
            "type": "metrics_update",
            "data": metric_data,
            "timestamp": time.time()
        }
        
        disconnected = []
        for websocket in self.metrics_subscribers:
            try:
                # Check if metric matches client's filters
                if self._matches_metric_filters(metric_data, getattr(websocket, 'metrics_filters', [])):
                    await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send metrics update to client: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            if websocket in self.metrics_subscribers:
                self.metrics_subscribers.remove(websocket)
    
    async def broadcast_theory_validation_event(self, validation_type: str, event_data: Dict[str, Any]):
        """
        Broadcast theory validation event to subscribed clients.
        
        Args:
            validation_type: Type of validation event
            event_data: Event data to broadcast
        """
        if validation_type in self.theory_subscribers:
            message = {
                "type": "theory_validation_event",
                "validation_type": validation_type,
                "data": event_data,
                "timestamp": time.time()
            }
            
            disconnected = []
            for websocket in self.theory_subscribers[validation_type]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send theory validation event to client: {e}")
                    disconnected.append(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                self.theory_subscribers[validation_type].discard(websocket)
    
    async def broadcast_general_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Broadcast general event to all subscribed clients.
        
        Args:
            event_type: Type of event
            event_data: Event data to broadcast
        """
        message = {
            "type": event_type,
            "data": event_data,
            "timestamp": time.time()
        }
        
        disconnected = []
        for websocket in self.active_connections:
            try:
                # Check if client is subscribed to this event type
                if hasattr(websocket, 'subscriptions') and event_type in websocket.subscriptions:
                    await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send event to client: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            if websocket in self.active_connections:
                self.disconnect(websocket)
    
    def _matches_metric_filters(self, metric_data: Dict[str, Any], filters: List[Dict[str, Any]]) -> bool:
        """
        Check if metric data matches any of the client's filters.
        
        Args:
            metric_data: Metric data to check
            filters: List of filter criteria
            
        Returns:
            True if metric matches any filter
        """
        if not filters:
            return True  # No filters means accept all
        
        for filter_criteria in filters:
            match = True
            
            # Check metric_id filter
            if "metric_id" in filter_criteria:
                if metric_data.get("metric_id") != filter_criteria["metric_id"]:
                    match = False
            
            # Check source filter
            if "source" in filter_criteria:
                if metric_data.get("source") != filter_criteria["source"]:
                    match = False
            
            # Check tags filter
            if "tags" in filter_criteria:
                metric_tags = metric_data.get("tags", [])
                required_tags = filter_criteria["tags"]
                if not all(tag in metric_tags for tag in required_tags):
                    match = False
            
            if match:
                return True
        
        return False
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get current WebSocket connection statistics.
        
        Returns:
            Dictionary with connection statistics
        """
        return {
            "total_connections": len(self.active_connections),
            "experiment_monitors": {
                exp_id: len(monitors) for exp_id, monitors in self.experiment_monitors.items()
            },
            "metrics_subscribers": len(self.metrics_subscribers),
            "theory_subscribers": {
                val_type: len(subscribers) for val_type, subscribers in self.theory_subscribers.items()
            },
            "client_subscriptions": {
                client_id: list(subs) for client_id, subs in self.client_subscriptions.items()
            }
        }


# Global singleton instance
_websocket_manager = None


def get_websocket_manager() -> WebSocketManager:
    """
    Get the global WebSocket manager instance.
    
    Returns:
        WebSocketManager instance
    """
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager


# Integration helpers for other Sophia components
async def notify_experiment_progress(experiment_id: str, progress_data: Dict[str, Any]):
    """
    Helper function to notify WebSocket clients of experiment progress.
    
    Args:
        experiment_id: ID of the experiment
        progress_data: Progress data to broadcast
    """
    manager = get_websocket_manager()
    await manager.broadcast_experiment_update(experiment_id, progress_data)


async def notify_metrics_collected(metric_data: Dict[str, Any]):
    """
    Helper function to notify WebSocket clients of new metrics.
    
    Args:
        metric_data: Metric data to broadcast
    """
    manager = get_websocket_manager()
    await manager.broadcast_metrics_update(metric_data)


async def notify_theory_validation_result(validation_type: str, result_data: Dict[str, Any]):
    """
    Helper function to notify WebSocket clients of theory validation results.
    
    Args:
        validation_type: Type of validation performed
        result_data: Validation result data
    """
    manager = get_websocket_manager()
    await manager.broadcast_theory_validation_event(validation_type, result_data)