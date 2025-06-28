"""
AI Health Monitor for Tekton AI specialists.

Monitors AI health and implements auto-recovery.
"""
import asyncio
import logging
from typing import Dict, Set, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AIHealthMonitor:
    """Monitors health of AI specialists."""
    
    def __init__(self, 
                 registry_client,
                 check_interval: float = 60.0,
                 timeout_threshold: float = 300.0):
        """
        Initialize AI Health Monitor.
        
        Args:
            registry_client: AI registry client instance
            check_interval: Seconds between health checks
            timeout_threshold: Seconds before AI is considered unresponsive
        """
        self.registry_client = registry_client
        self.check_interval = check_interval
        self.timeout_threshold = timeout_threshold
        
        # Track last response times
        self.last_response: Dict[str, datetime] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False
        
    async def check_ai_health(self, ai_id: str) -> bool:
        """
        Check health of a specific AI.
        
        Args:
            ai_id: AI identifier
            
        Returns:
            True if healthy, False otherwise
        """
        socket_info = self.registry_client.get_ai_socket(ai_id)
        if not socket_info:
            return False
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(socket_info[0], socket_info[1]),
                timeout=5.0
            )
            
            # Send health check
            health_msg = '{"type": "health"}\n'
            writer.write(health_msg.encode())
            await writer.drain()
            
            # Wait for response
            response = await asyncio.wait_for(reader.readline(), timeout=5.0)
            
            writer.close()
            await writer.wait_closed()
            
            if response:
                self.last_response[ai_id] = datetime.now()
                return True
                
        except Exception as e:
            logger.warning(f"Health check failed for {ai_id}: {e}")
            
        return False
    
    async def monitor_loop(self):
        """Main monitoring loop."""
        logger.info("AI Health Monitor started")
        
        while self.running:
            try:
                # Get all registered AIs
                ais = self.registry_client.list_platform_ais()
                
                for ai_id in ais:
                    # Check if we should verify health
                    last_check = self.last_response.get(ai_id)
                    
                    if last_check is None:
                        # First check
                        await self.check_ai_health(ai_id)
                    elif (datetime.now() - last_check).total_seconds() > self.timeout_threshold:
                        # AI hasn't responded in a while
                        logger.warning(f"AI {ai_id} unresponsive for {self.timeout_threshold}s")
                        
                        # Try health check
                        if not await self.check_ai_health(ai_id):
                            logger.error(f"AI {ai_id} failed health check")
                            # TODO: Implement auto-recovery here
                            # For now, just log the issue
                
                # Sleep until next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def start(self):
        """Start health monitoring."""
        if self.running:
            return
            
        self.running = True
        self.monitoring_task = asyncio.create_task(self.monitor_loop())
        logger.info("Health monitoring started")
    
    async def stop(self):
        """Stop health monitoring."""
        self.running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Health monitoring stopped")
    
    def get_health_summary(self) -> Dict[str, Dict]:
        """Get health summary for all AIs."""
        ais = self.registry_client.list_platform_ais()
        summary = {}
        
        for ai_id in ais:
            last_check = self.last_response.get(ai_id)
            
            if last_check:
                time_since = (datetime.now() - last_check).total_seconds()
                status = 'healthy' if time_since < self.timeout_threshold else 'unresponsive'
            else:
                status = 'unknown'
                time_since = None
                
            summary[ai_id] = {
                'status': status,
                'last_response': last_check.isoformat() if last_check else None,
                'seconds_since_response': time_since
            }
            
        return summary