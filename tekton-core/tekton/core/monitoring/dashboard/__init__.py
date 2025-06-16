"""
Dashboard package for monitoring Tekton components.

This package provides modules for the Health Dashboard system, which monitors
and visualizes the health and status of Tekton components.
"""

from .dashboard_core import HealthDashboard, MonitoringDashboard, get_dashboard

__all__ = [
    'HealthDashboard',
    'MonitoringDashboard', 
    'get_dashboard'
]