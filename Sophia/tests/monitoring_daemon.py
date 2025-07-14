#!/usr/bin/env python3
"""
Continuous monitoring daemon for Sophia
Monitors health, performance, and data quality
"""

import asyncio
import logging
import json
import time
import psutil
import os
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Add Sophia root to path
sophia_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if sophia_root not in sys.path:
    sys.path.insert(0, sophia_root)

# Add Tekton root to path
tekton_root = os.path.abspath(os.path.join(sophia_root, '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)


@dataclass
class HealthMetric:
    """Health metric data structure"""
    name: str
    value: float
    status: str  # "healthy", "warning", "critical"
    timestamp: datetime
    threshold_warning: float = None
    threshold_critical: float = None
    unit: str = ""
    description: str = ""


@dataclass
class MonitoringAlert:
    """Monitoring alert data structure"""
    alert_id: str
    severity: str  # "info", "warning", "critical"
    component: str
    metric: str
    message: str
    timestamp: datetime
    resolved: bool = False


class SophiaMonitoringDaemon:
    """Continuous monitoring daemon for Sophia"""
    
    def __init__(self):
        self.running = False
        self.check_interval = 30  # seconds
        self.metrics_history = []
        self.active_alerts = {}
        self.alert_thresholds = self._load_alert_thresholds()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sophia_monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("SophiaMonitoring")
    
    def _load_alert_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load alert thresholds configuration"""
        return {
            "cpu_usage": {"warning": 70.0, "critical": 90.0},
            "memory_usage": {"warning": 80.0, "critical": 95.0},
            "disk_usage": {"warning": 85.0, "critical": 95.0},
            "response_time": {"warning": 1000.0, "critical": 5000.0},  # ms
            "error_rate": {"warning": 0.05, "critical": 0.10},  # 5%, 10%
            "experiment_failure_rate": {"warning": 0.20, "critical": 0.50},
            "prediction_accuracy": {"warning": 0.70, "critical": 0.50},  # below these values
            "pattern_detection_rate": {"warning": 0.30, "critical": 0.10}  # below these values
        }
    
    async def start_monitoring(self):
        """Start the monitoring daemon"""
        self.logger.info("Starting Sophia monitoring daemon...")
        self.running = True
        
        try:
            while self.running:
                await self.perform_health_checks()
                await self.check_performance_metrics()
                await self.validate_data_quality()
                await self.monitor_system_resources()
                await self.check_component_health()
                
                # Process alerts
                await self.process_alerts()
                
                # Cleanup old metrics
                self.cleanup_old_metrics()
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring daemon stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring daemon error: {e}")
        finally:
            self.running = False
    
    async def perform_health_checks(self):
        """Perform comprehensive health checks"""
        self.logger.debug("Performing health checks...")
        
        try:
            # Check if Sophia API is responsive
            import httpx
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get("http://localhost:8006/health", timeout=5.0)
                    
                    if response.status_code == 200:
                        health_data = response.json()
                        
                        # Record API health metric
                        self.record_metric(HealthMetric(
                            name="api_health",
                            value=1.0 if health_data.get("status") == "healthy" else 0.0,
                            status="healthy" if health_data.get("status") == "healthy" else "critical",
                            timestamp=datetime.now(),
                            description="Sophia API health status"
                        ))
                        
                        # Check individual engines
                        engines = health_data.get("engines", {})
                        for engine_name, engine_status in engines.items():
                            self.record_metric(HealthMetric(
                                name=f"engine_health_{engine_name}",
                                value=1.0 if engine_status else 0.0,
                                status="healthy" if engine_status else "critical",
                                timestamp=datetime.now(),
                                description=f"{engine_name} engine health"
                            ))
                    
                    else:
                        self.record_metric(HealthMetric(
                            name="api_health",
                            value=0.0,
                            status="critical",
                            timestamp=datetime.now(),
                            description=f"API returned status {response.status_code}"
                        ))
                
                except (httpx.ConnectError, httpx.TimeoutException):
                    self.record_metric(HealthMetric(
                        name="api_health",
                        value=0.0,
                        status="critical",
                        timestamp=datetime.now(),
                        description="API not reachable"
                    ))
        
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
    
    async def check_performance_metrics(self):
        """Check performance metrics"""
        self.logger.debug("Checking performance metrics...")
        
        try:
            # Simulate performance metric collection
            # In real implementation, this would query Sophia's metrics
            
            # Response time check
            response_time = await self.measure_api_response_time()
            self.record_metric(HealthMetric(
                name="response_time",
                value=response_time,
                status=self.get_status_for_threshold("response_time", response_time),
                timestamp=datetime.now(),
                threshold_warning=self.alert_thresholds["response_time"]["warning"],
                threshold_critical=self.alert_thresholds["response_time"]["critical"],
                unit="ms",
                description="API response time"
            ))
            
            # Simulated metrics processing rate
            processing_rate = await self.measure_metrics_processing_rate()
            self.record_metric(HealthMetric(
                name="metrics_processing_rate",
                value=processing_rate,
                status="healthy" if processing_rate > 100 else "warning",
                timestamp=datetime.now(),
                unit="metrics/second",
                description="Metrics processing rate"
            ))
            
        except Exception as e:
            self.logger.error(f"Performance check error: {e}")
    
    async def validate_data_quality(self):
        """Validate data quality"""
        self.logger.debug("Validating data quality...")
        
        try:
            # Simulate data quality checks
            # In real implementation, this would check database integrity
            
            # Data completeness check
            completeness_score = await self.check_data_completeness()
            self.record_metric(HealthMetric(
                name="data_completeness",
                value=completeness_score,
                status="healthy" if completeness_score > 0.95 else "warning" if completeness_score > 0.8 else "critical",
                timestamp=datetime.now(),
                threshold_warning=0.95,
                threshold_critical=0.8,
                unit="ratio",
                description="Data completeness ratio"
            ))
            
            # Data freshness check
            freshness_score = await self.check_data_freshness()
            self.record_metric(HealthMetric(
                name="data_freshness",
                value=freshness_score,
                status="healthy" if freshness_score > 0.9 else "warning" if freshness_score > 0.7 else "critical",
                timestamp=datetime.now(),
                unit="ratio",
                description="Data freshness score"
            ))
            
        except Exception as e:
            self.logger.error(f"Data quality check error: {e}")
    
    async def monitor_system_resources(self):
        """Monitor system resource usage"""
        self.logger.debug("Monitoring system resources...")
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric(HealthMetric(
                name="cpu_usage",
                value=cpu_percent,
                status=self.get_status_for_threshold("cpu_usage", cpu_percent),
                timestamp=datetime.now(),
                threshold_warning=self.alert_thresholds["cpu_usage"]["warning"],
                threshold_critical=self.alert_thresholds["cpu_usage"]["critical"],
                unit="%",
                description="CPU usage percentage"
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.record_metric(HealthMetric(
                name="memory_usage",
                value=memory_percent,
                status=self.get_status_for_threshold("memory_usage", memory_percent),
                timestamp=datetime.now(),
                threshold_warning=self.alert_thresholds["memory_usage"]["warning"],
                threshold_critical=self.alert_thresholds["memory_usage"]["critical"],
                unit="%",
                description="Memory usage percentage"
            ))
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric(HealthMetric(
                name="disk_usage",
                value=disk_percent,
                status=self.get_status_for_threshold("disk_usage", disk_percent),
                timestamp=datetime.now(),
                threshold_warning=self.alert_thresholds["disk_usage"]["warning"],
                threshold_critical=self.alert_thresholds["disk_usage"]["critical"],
                unit="%",
                description="Disk usage percentage"
            ))
            
        except Exception as e:
            self.logger.error(f"Resource monitoring error: {e}")
    
    async def check_component_health(self):
        """Check health of individual Sophia components"""
        self.logger.debug("Checking component health...")
        
        try:
            # Check database connectivity
            db_health = await self.check_database_health()
            self.record_metric(HealthMetric(
                name="database_health",
                value=1.0 if db_health else 0.0,
                status="healthy" if db_health else "critical",
                timestamp=datetime.now(),
                description="Database connectivity"
            ))
            
            # Check WebSocket health
            ws_health = await self.check_websocket_health()
            self.record_metric(HealthMetric(
                name="websocket_health",
                value=1.0 if ws_health else 0.0,
                status="healthy" if ws_health else "warning",
                timestamp=datetime.now(),
                description="WebSocket connectivity"
            ))
            
        except Exception as e:
            self.logger.error(f"Component health check error: {e}")
    
    async def measure_api_response_time(self) -> float:
        """Measure API response time"""
        try:
            import httpx
            
            start_time = time.time()
            async with httpx.AsyncClient() as client:
                await client.get("http://localhost:8006/health", timeout=10.0)
            end_time = time.time()
            
            return (end_time - start_time) * 1000  # Convert to milliseconds
        except:
            return 9999.0  # High value for timeout/error
    
    async def measure_metrics_processing_rate(self) -> float:
        """Measure metrics processing rate"""
        # Simulate metrics processing rate measurement
        # In real implementation, this would query actual metrics
        import random
        return random.uniform(80, 150)  # metrics per second
    
    async def check_data_completeness(self) -> float:
        """Check data completeness ratio"""
        # Simulate data completeness check
        import random
        return random.uniform(0.85, 0.99)
    
    async def check_data_freshness(self) -> float:
        """Check data freshness score"""
        # Simulate data freshness check
        import random
        return random.uniform(0.75, 0.95)
    
    async def check_database_health(self) -> bool:
        """Check database health"""
        # Simulate database health check
        # In real implementation, this would test database connectivity
        return True
    
    async def check_websocket_health(self) -> bool:
        """Check WebSocket health"""
        # Simulate WebSocket health check
        # In real implementation, this would test WebSocket connectivity
        return True
    
    def get_status_for_threshold(self, metric_name: str, value: float) -> str:
        """Get status based on threshold"""
        if metric_name not in self.alert_thresholds:
            return "healthy"
        
        thresholds = self.alert_thresholds[metric_name]
        
        if value >= thresholds["critical"]:
            return "critical"
        elif value >= thresholds["warning"]:
            return "warning"
        else:
            return "healthy"
    
    def record_metric(self, metric: HealthMetric):
        """Record a health metric"""
        self.metrics_history.append(metric)
        
        # Generate alert if needed
        if metric.status in ["warning", "critical"]:
            self.generate_alert(metric)
        
        # Log metric
        self.logger.info(f"Metric: {metric.name} = {metric.value}{metric.unit} ({metric.status})")
    
    def generate_alert(self, metric: HealthMetric):
        """Generate an alert for a metric"""
        alert_id = f"{metric.name}_{metric.status}_{int(metric.timestamp.timestamp())}"
        
        if alert_id not in self.active_alerts:
            alert = MonitoringAlert(
                alert_id=alert_id,
                severity=metric.status,
                component="sophia",
                metric=metric.name,
                message=f"{metric.name} is {metric.status}: {metric.value}{metric.unit}",
                timestamp=metric.timestamp
            )
            
            self.active_alerts[alert_id] = alert
            self.logger.warning(f"ALERT: {alert.message}")
    
    async def process_alerts(self):
        """Process and potentially resolve alerts"""
        current_time = datetime.now()
        
        # Auto-resolve alerts older than 10 minutes if metric is now healthy
        for alert_id, alert in list(self.active_alerts.items()):
            if not alert.resolved:
                # Check if we have recent healthy metrics for this metric
                recent_metrics = [
                    m for m in self.metrics_history[-10:] 
                    if m.name == alert.metric and m.timestamp > current_time - timedelta(minutes=5)
                ]
                
                if recent_metrics and all(m.status == "healthy" for m in recent_metrics):
                    alert.resolved = True
                    self.logger.info(f"RESOLVED: Alert {alert_id} - metric is now healthy")
                    del self.active_alerts[alert_id]
    
    def cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory growth"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics_history = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > datetime.now() - timedelta(minutes=5)
        ]
        
        status_counts = {"healthy": 0, "warning": 0, "critical": 0}
        for metric in recent_metrics:
            status_counts[metric.status] = status_counts.get(metric.status, 0) + 1
        
        overall_status = "healthy"
        if status_counts["critical"] > 0:
            overall_status = "critical"
        elif status_counts["warning"] > 0:
            overall_status = "warning"
        
        return {
            "overall_status": overall_status,
            "metrics_count": len(recent_metrics),
            "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
            "last_check": datetime.now().isoformat(),
            "status_breakdown": status_counts
        }
    
    def generate_report(self) -> str:
        """Generate monitoring report"""
        status = self.get_current_status()
        
        report = []
        report.append("SOPHIA MONITORING REPORT")
        report.append("=" * 50)
        report.append(f"Overall Status: {status['overall_status'].upper()}")
        report.append(f"Last Check: {status['last_check']}")
        report.append(f"Active Alerts: {status['active_alerts']}")
        report.append("")
        
        report.append("Recent Metrics:")
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > datetime.now() - timedelta(minutes=10)
        ]
        
        for metric in recent_metrics[-20:]:  # Last 20 metrics
            status_emoji = "✅" if metric.status == "healthy" else "⚠️" if metric.status == "warning" else "❌"
            report.append(f"  {status_emoji} {metric.name}: {metric.value}{metric.unit}")
        
        if self.active_alerts:
            report.append("")
            report.append("Active Alerts:")
            for alert in self.active_alerts.values():
                if not alert.resolved:
                    severity_emoji = "⚠️" if alert.severity == "warning" else "❌"
                    report.append(f"  {severity_emoji} {alert.message}")
        
        return "\n".join(report)
    
    def stop_monitoring(self):
        """Stop the monitoring daemon"""
        self.logger.info("Stopping monitoring daemon...")
        self.running = False


async def main():
    """Main entry point for monitoring daemon"""
    daemon = SophiaMonitoringDaemon()
    
    try:
        await daemon.start_monitoring()
    except KeyboardInterrupt:
        print("\nStopping monitoring daemon...")
        daemon.stop_monitoring()


if __name__ == "__main__":
    print("🔍 Sophia Monitoring Daemon")
    print("Starting continuous monitoring...")
    print("Press Ctrl+C to stop")
    
    asyncio.run(main())