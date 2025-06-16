#!/usr/bin/env python3
"""
Dashboard Server Component

This module provides HTTP server capabilities for the dashboard.
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable

from ...logging_integration import get_logger, LogCategory

# Configure logger
logger = get_logger("tekton.monitoring.dashboard.server")


class DashboardServer:
    """
    HTTP server for the dashboard UI.
    
    Provides a web interface for the monitoring dashboard with status
    visualization, dependency graphs, and alerts.
    """
    
    def __init__(self, 
                dashboard=None,
                host: str = "127.0.0.1",
                port: int = 8080):
        """
        Initialize the dashboard server.
        
        Args:
            dashboard: Dashboard instance
            host: Host address to bind to
            port: Port to listen on
        """
        self.dashboard = dashboard
        self.host = host
        self.port = port
        self.app = None
        self.runner = None
        self.site = None
        
    async def start(self):
        """Start the dashboard server."""
        try:
            import aiohttp
            from aiohttp import web
        except ImportError:
            logger.error("aiohttp is required for the dashboard server")
            return
            
        # Create application
        self.app = web.Application()
        
        # Register routes
        register_routes(self.app, self.dashboard)
        
        # Start server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        logger.info(f"Dashboard server started at http://{self.host}:{self.port}")
    
    async def stop(self):
        """Stop the dashboard server."""
        if self.site:
            await self.site.stop()
            
        if self.runner:
            await self.runner.cleanup()
            
        logger.info("Dashboard server stopped")


async def start_server(dashboard, host="127.0.0.1", port=8080):
    """Start a dashboard server.
    
    Args:
        dashboard: Dashboard instance
        host: Host address to bind to
        port: Port to listen on
    """
    try:
        import aiohttp
        from aiohttp import web
    except ImportError:
        logger.error("aiohttp is required for the dashboard server")
        return
        
    # Create application
    app = web.Application()
    
    # Register routes
    register_routes(app, dashboard)
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info(f"Dashboard server started at http://{host}:{port}")
    
    return app, runner, site


def register_routes(app, dashboard):
    """Register HTTP routes for the dashboard UI.
    
    Args:
        app: aiohttp application
        dashboard: Dashboard instance
    """
    try:
        from aiohttp import web
    except ImportError:
        logger.error("aiohttp is required for the dashboard server")
        return
    
    # Static HTML templates
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Tekton Health Dashboard</title>
        <style>
            body {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", 
                    Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #ddd;
            }
            header h1 {
                margin: 0;
                color: #2c3e50;
            }
            .status-pill {
                padding: 5px 12px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 14px;
            }
            .status-healthy {
                background-color: #27ae60;
            }
            .status-degraded {
                background-color: #f39c12;
            }
            .status-unhealthy {
                background-color: #e74c3c;
            }
            .status-unknown {
                background-color: #95a5a6;
            }
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .card-header {
                padding: 15px 20px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #f8f9fa;
            }
            .card-header h2 {
                margin: 0;
                font-size: 18px;
                color: #2c3e50;
            }
            .card-body {
                padding: 20px;
            }
            .card-footer {
                padding: 15px 20px;
                border-top: 1px solid #eee;
                font-size: 14px;
                color: #7f8c8d;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table th, table td {
                text-align: left;
                padding: 12px 15px;
                border-bottom: 1px solid #eee;
            }
            table th {
                background-color: #f8f9fa;
                font-weight: 600;
                color: #2c3e50;
            }
            .alerts-list {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            .alert-item {
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 6px;
                border-left: 4px solid #f39c12;
            }
            .alert-critical {
                border-left-color: #e74c3c;
                background-color: #fdecea;
            }
            .alert-warning {
                border-left-color: #f39c12;
                background-color: #fef5e7;
            }
            .alert-info {
                border-left-color: #3498db;
                background-color: #ebf5fb;
            }
            .alert-title {
                margin: 0 0 5px 0;
                font-weight: 600;
                font-size: 16px;
            }
            .alert-description {
                margin: 0;
                color: #555;
            }
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                gap: 15px;
            }
            .metric-card {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                text-align: center;
            }
            .metric-value {
                font-size: 24px;
                font-weight: bold;
                margin: 8px 0;
                color: #2c3e50;
            }
            .metric-label {
                font-size: 14px;
                color: #7f8c8d;
                margin: 0;
            }
            .refresh-button {
                padding: 8px 16px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.2s;
            }
            .refresh-button:hover {
                background-color: #2980b9;
            }
            @media (max-width: 768px) {
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }
                .metrics-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Tekton Health Dashboard</h1>
                <div>
                    <span id="system-status" class="status-pill status-unknown">Unknown</span>
                    <button id="refresh-btn" class="refresh-button">Refresh</button>
                </div>
            </header>
            
            <div class="card">
                <div class="card-header">
                    <h2>System Overview</h2>
                    <span id="last-updated"></span>
                </div>
                <div class="card-body">
                    <div class="metrics-grid" id="system-metrics">
                        <!-- System metrics will be inserted here -->
                    </div>
                </div>
            </div>
            
            <h2>Components</h2>
            <div class="dashboard-grid" id="components-grid">
                <!-- Component cards will be inserted here -->
            </div>
            
            <h2>Active Alerts</h2>
            <div class="card">
                <div class="card-body">
                    <ul class="alerts-list" id="alerts-list">
                        <!-- Alerts will be inserted here -->
                    </ul>
                </div>
            </div>
        </div>
        
        <script>
            // Update dashboard with data
            function updateDashboard(data) {
                // Update system status
                const systemStatusElement = document.getElementById('system-status');
                if (data.system_health && data.system_health.overall_status) {
                    const status = data.system_health.overall_status;
                    systemStatusElement.textContent = status;
                    systemStatusElement.className = 'status-pill status-' + status.toLowerCase();
                }
                
                // Update last updated time
                const lastUpdated = document.getElementById('last-updated');
                lastUpdated.textContent = 'Last updated: ' + new Date().toLocaleTimeString();
                
                // Update system metrics
                const systemMetricsElement = document.getElementById('system-metrics');
                if (data.system_health && data.system_health.metrics) {
                    systemMetricsElement.innerHTML = '';
                    
                    const metrics = data.system_health.metrics;
                    for (const [key, value] of Object.entries(metrics)) {
                        // Format metric name
                        const label = key.replace(/_/g, ' ')
                            .replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
                            
                        // Format metric value
                        let formattedValue = value;
                        if (typeof value === 'number') {
                            formattedValue = Number.isInteger(value) ? value : value.toFixed(1);
                            
                            // Add percentage sign if appropriate
                            if (key.includes('percentage') || key.includes('rate')) {
                                formattedValue = formattedValue + '%';
                            }
                        }
                        
                        const metricHtml = `
                            <div class="metric-card">
                                <p class="metric-value">${formattedValue}</p>
                                <p class="metric-label">${label}</p>
                            </div>
                        `;
                        systemMetricsElement.innerHTML += metricHtml;
                    }
                }
                
                // Update components
                const componentsGrid = document.getElementById('components-grid');
                if (data.system_health && data.system_health.components) {
                    componentsGrid.innerHTML = '';
                    
                    const components = Object.values(data.system_health.components);
                    components.sort((a, b) => {
                        // Sort by status (unhealthy first, then degraded, then healthy)
                        const statusOrder = { 'UNHEALTHY': 0, 'DEGRADED': 1, 'HEALTHY': 2, 'UNKNOWN': 3 };
                        return statusOrder[a.status] - statusOrder[b.status];
                    });
                    
                    for (const component of components) {
                        const componentHtml = `
                            <div class="card">
                                <div class="card-header">
                                    <h2>${component.component_name || component.component_id}</h2>
                                    <span class="status-pill status-${component.status.toLowerCase()}">${component.status}</span>
                                </div>
                                <div class="card-body">
                                    <table>
                                        <tr>
                                            <th>ID</th>
                                            <td>${component.component_id}</td>
                                        </tr>
                                        <tr>
                                            <th>Type</th>
                                            <td>${component.component_type || 'N/A'}</td>
                                        </tr>
                                        <tr>
                                            <th>State</th>
                                            <td>${component.state || 'N/A'}</td>
                                        </tr>
                                        ${component.metrics ? Object.entries(component.metrics).map(([key, value]) => `
                                            <tr>
                                                <th>${key.replace(/_/g, ' ').replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); })}</th>
                                                <td>${typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(2)) : value}</td>
                                            </tr>
                                        `).join('') : ''}
                                    </table>
                                </div>
                            </div>
                        `;
                        componentsGrid.innerHTML += componentHtml;
                    }
                }
                
                // Update alerts
                const alertsList = document.getElementById('alerts-list');
                if (data.system_health && data.system_health.alerts) {
                    const alerts = data.system_health.alerts.filter(alert => !alert.resolved);
                    
                    if (alerts.length === 0) {
                        alertsList.innerHTML = '<li>No active alerts</li>';
                    } else {
                        alertsList.innerHTML = '';
                        
                        for (const alert of alerts) {
                            const severityClass = alert.severity === 'CRITICAL' ? 'alert-critical' : 
                                (alert.severity === 'WARNING' ? 'alert-warning' : 'alert-info');
                                
                            const timestamp = new Date(alert.timestamp * 1000).toLocaleString();
                            
                            const alertHtml = `
                                <li class="alert-item ${severityClass}">
                                    <h3 class="alert-title">${alert.title}</h3>
                                    <p class="alert-description">${alert.description}</p>
                                    <p class="alert-meta">
                                        ${alert.component_id ? `Component: ${alert.component_id} | ` : ''}
                                        ${timestamp}
                                    </p>
                                </li>
                            `;
                            alertsList.innerHTML += alertHtml;
                        }
                    }
                }
            }
            
            // Fetch dashboard data
            async function fetchDashboardData() {
                try {
                    const response = await fetch('/api/dashboard');
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    const data = await response.json();
                    updateDashboard(data);
                } catch (error) {
                    console.error('Error fetching dashboard data:', error);
                }
            }
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', () => {
                // Fetch initial data
                fetchDashboardData();
                
                // Set up refresh button
                const refreshButton = document.getElementById('refresh-btn');
                refreshButton.addEventListener('click', fetchDashboardData);
                
                // Set up auto-refresh
                setInterval(fetchDashboardData, 10000);  // Refresh every 10 seconds
            });
        </script>
    </body>
    </html>
    """
    
    # API routes
    async def health_check(request):
        return web.json_response({"status": "ok"})
    
    async def get_dashboard_data(request):
        if dashboard:
            system_health = dashboard.get_system_health()
            return web.json_response({
                "system_health": {
                    "overall_status": system_health.overall_status.value,
                    "metrics": system_health.metrics,
                    "components": {cid: {
                        "component_id": c.component_id,
                        "component_name": c.component_name,
                        "component_type": c.component_type,
                        "status": c.status.value,
                        "state": c.state,
                        "metrics": c.metrics
                    } for cid, c in system_health.components.items()},
                    "alerts": [{
                        "severity": a.severity.value,
                        "title": a.title,
                        "description": a.description,
                        "component_id": a.component_id,
                        "timestamp": a.timestamp,
                        "resolved": a.resolved
                    } for a in dashboard.alert_manager.get_alerts(include_resolved=False)]
                }
            })
        else:
            return web.json_response({"error": "Dashboard not available"}, status=503)
    
    async def get_dashboard_ui(request):
        return web.Response(text=html_template, content_type="text/html")
    
    # Register routes
    app.add_routes([
        web.get("/", get_dashboard_ui),
        web.get("/health", health_check),
        web.get("/api/dashboard", get_dashboard_data),
    ])
