#!/usr/bin/env python3
"""
Web Interface Module

This module provides functions for the web interface of the health dashboard.
"""

import asyncio
from typing import Dict, Any

from ...logging_integration import get_logger

# Configure logger
logger = get_logger("tekton.monitoring.dashboard.web")

# Import HTML template for the dashboard UI
from .html_templates import DASHBOARD_HTML


async def start_dashboard_server(dashboard):
    """Start HTTP server for dashboard UI.
    
    Args:
        dashboard: The dashboard instance
    """
    try:
        from aiohttp import web
        
        app = web.Application()
        
        # Define routes
        async def get_health(request):
            return web.json_response(dashboard.system_health.to_dict())
            
        async def get_component(request):
            component_id = request.match_info.get('id', '')
            component = dashboard.system_health.get_component(component_id)
            if component:
                return web.json_response(component.to_dict())
            else:
                return web.json_response({"error": "Component not found"}, status=404)
                
        async def get_alerts(request):
            component_id = request.query.get('component')
            include_resolved = request.query.get('include_resolved') == 'true'
            alerts = dashboard.alert_manager.get_alerts(component_id, include_resolved)
            return web.json_response([alert.to_dict() for alert in alerts])
            
        async def get_spectral(request):
            if hasattr(dashboard, 'last_spectral_analysis'):
                return web.json_response(dashboard.last_spectral_analysis)
            else:
                return web.json_response({"error": "No spectral analysis available"}, status=404)
                
        async def get_dependency_graph(request):
            return web.json_response(dashboard.dependency_graph)
            
        async def get_dashboard_ui(request):
            # Return the HTML dashboard
            return web.Response(text=DASHBOARD_HTML, content_type='text/html')
        
        # Define resource monitoring routes
        async def get_resource_metrics(request):
            """Get current resource metrics."""
            if dashboard.resource_monitor:
                metrics = dashboard.resource_monitor.get_current_metrics()
                return web.json_response(metrics.as_dict)
            return web.json_response({"error": "Resource monitoring not available"}, status=404)
        
        async def get_resource_history(request):
            """Get resource metrics history."""
            if dashboard.resource_monitor:
                hours = request.query.get('hours')
                if hours:
                    try:
                        hours = int(hours)
                        metrics = dashboard.resource_monitor.get_metrics_history(hours)
                    except ValueError:
                        return web.json_response({"error": "Invalid hours parameter"}, status=400)
                else:
                    metrics = dashboard.resource_monitor.get_metrics_history()
                
                return web.json_response([m.as_dict for m in metrics])
            return web.json_response({"error": "Resource monitoring not available"}, status=404)
        
        async def get_system_info(request):
            """Get system information."""
            if dashboard.resource_monitor:
                info = dashboard.resource_monitor.get_system_info()
                return web.json_response(info)
            return web.json_response({"error": "Resource monitoring not available"}, status=404)
            
        # Add routes
        app.add_routes([
            web.get('/', get_dashboard_ui),
            web.get('/api/health', get_health),
            web.get('/api/component/{id}', get_component),
            web.get('/api/alerts', get_alerts),
            web.get('/api/spectral', get_spectral),
            web.get('/api/dependency-graph', get_dependency_graph),
            web.get('/api/resource-metrics', get_resource_metrics),
            web.get('/api/resource-history', get_resource_history),
            web.get('/api/system-info', get_system_info)
        ])
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        
        logger.info("Dashboard UI available at http://localhost:8080")
        
        # Keep server running
        while dashboard.running:
            await asyncio.sleep(1)
            
        # Cleanup
        await runner.cleanup()
        
    except ImportError:
        logger.warning("aiohttp not available, cannot start dashboard server")
        while dashboard.running:
            await asyncio.sleep(60)  # Just keep the task alive