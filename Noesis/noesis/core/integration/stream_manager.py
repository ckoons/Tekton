"""
Stream Manager for Noesis
Coordinates data streaming from multiple sources for theoretical analysis
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .engram_stream import EngramDataStreamer, NoesisMemoryAnalyzer
from ..theoretical.base import MathematicalFramework
from landmarks import (
    architecture_decision,
    integration_point,
    performance_boundary,
    state_checkpoint
)

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Streaming Analysis Architecture",
    rationale="Real-time theoretical analysis of streaming data enables early warning systems and dynamic insights",
    alternatives_considered=["Batch processing at intervals", "On-demand analysis only"],
    decided_by="Noesis Team"
)
@state_checkpoint(
    title="Stream Analysis State",
    state_type="ephemeral",
    persistence=False,
    consistency_requirements="Analysis results cached with 1-hour retention",
    recovery_strategy="Restart streaming and rebuild analysis cache from live data"
)
class TheoreticalStreamManager:
    """
    Manages data streams for theoretical analysis in Noesis
    Coordinates between Engram memory streams and theoretical analyzers
    """
    
    def __init__(self, theoretical_framework=None):
        self.theoretical_framework = theoretical_framework
        
        # Stream components
        self.engram_streamer: Optional[EngramDataStreamer] = None
        self.memory_analyzer: Optional[NoesisMemoryAnalyzer] = None
        
        # Stream status
        self.is_active = False
        self.start_time: Optional[datetime] = None
        
        # Analysis results cache
        self.analysis_results: Dict[str, Any] = {}
        self.analysis_history: List[Dict[str, Any]] = []
        
        logger.info("Initialized theoretical stream manager")
    
    @integration_point(
        title="Stream Manager Configuration",
        target_component="Engram API and theoretical analyzers",
        protocol="Configuration-based initialization",
        data_flow="Configuration → Stream components",
        critical_notes="Must validate Engram availability before starting streams"
    )
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize stream manager with configuration"""
        config = config or {}
        
        try:
            # Initialize Engram data streamer
            engram_config = config.get("engram", {})
            poll_interval = engram_config.get("poll_interval", 5.0)
            engram_url = engram_config.get("url")
            
            self.engram_streamer = EngramDataStreamer(
                engram_url=engram_url,
                poll_interval=poll_interval
            )
            
            # Initialize memory analyzer
            self.memory_analyzer = NoesisMemoryAnalyzer(
                theoretical_framework=self.theoretical_framework
            )
            
            # Connect analyzer to streamer
            self.engram_streamer.add_listener(self.memory_analyzer)
            
            logger.info("Stream manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize stream manager: {e}")
            raise
    
    @performance_boundary(
        title="Streaming Analysis Pipeline",
        sla="Process updates within 1s of receipt",
        optimization_notes="Parallel analysis, incremental updates, result caching",
        metrics={"update_latency": "1s", "poll_interval": "5s"}
    )
    async def start_streaming(self) -> None:
        """Start all data streams"""
        if self.is_active:
            logger.warning("Streaming already active")
            return
        
        try:
            if not self.engram_streamer:
                raise RuntimeError("Stream manager not initialized")
            
            # Start Engram streaming
            await self.engram_streamer.start_streaming()
            
            self.is_active = True
            self.start_time = datetime.now()
            
            # Start analysis update task
            asyncio.create_task(self._analysis_update_loop())
            
            logger.info("Started all data streams")
            
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            await self.stop_streaming()
            raise
    
    async def stop_streaming(self) -> None:
        """Stop all data streams"""
        if not self.is_active:
            return
        
        self.is_active = False
        
        try:
            if self.engram_streamer:
                await self.engram_streamer.stop_streaming()
            
            logger.info("Stopped all data streams")
            
        except Exception as e:
            logger.error(f"Error stopping streams: {e}")
    
    async def _analysis_update_loop(self) -> None:
        """Periodically update analysis results"""
        while self.is_active:
            try:
                await self._update_analysis_results()
                await asyncio.sleep(30.0)  # Update every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analysis update loop: {e}")
                await asyncio.sleep(5.0)  # Brief pause before retry
    
    async def _update_analysis_results(self) -> None:
        """Update aggregated analysis results"""
        try:
            current_results = {
                "timestamp": datetime.now().isoformat(),
                "stream_status": {
                    "active": self.is_active,
                    "uptime_minutes": (
                        (datetime.now() - self.start_time).total_seconds() / 60
                        if self.start_time else 0
                    )
                }
            }
            
            # Get Engram analysis results
            if self.memory_analyzer:
                memory_analysis = self.memory_analyzer.get_analysis_results()
                memory_stats = self.memory_analyzer.get_memory_statistics()
                
                current_results["memory_analysis"] = memory_analysis
                current_results["memory_statistics"] = memory_stats
            
            # Get current Engram state
            if self.engram_streamer:
                current_state = self.engram_streamer.get_current_state()
                if current_state:
                    current_results["current_memory_state"] = current_state.to_dict()
                
                # Get recent history
                recent_history = self.engram_streamer.get_memory_history(
                    duration=timedelta(minutes=10),
                    limit=20
                )
                current_results["recent_memory_history"] = [
                    state.to_dict() for state in recent_history
                ]
            
            # Store results
            self.analysis_results = current_results
            
            # Add to history (limited size)
            self.analysis_history.append(current_results)
            if len(self.analysis_history) > 100:
                self.analysis_history = self.analysis_history[-100:]
            
        except Exception as e:
            logger.error(f"Error updating analysis results: {e}")
    
    async def get_theoretical_insights(self) -> Dict[str, Any]:
        """Get current theoretical insights from stream analysis"""
        insights = {
            "timestamp": datetime.now().isoformat(),
            "insights": []
        }
        
        if not self.memory_analyzer:
            return insights
        
        try:
            analysis_results = self.memory_analyzer.get_analysis_results()
            
            # Extract insights from manifold analysis
            if "manifold" in analysis_results:
                manifold_data = analysis_results["manifold"]
                if hasattr(manifold_data, 'data'):
                    manifold_insights = self._extract_manifold_insights(manifold_data.data)
                    insights["insights"].extend(manifold_insights)
            
            # Extract insights from dynamics analysis
            if "dynamics" in analysis_results:
                dynamics_data = analysis_results["dynamics"]
                if hasattr(dynamics_data, 'data'):
                    dynamics_insights = self._extract_dynamics_insights(dynamics_data.data)
                    insights["insights"].extend(dynamics_insights)
            
            # Extract insights from catastrophe analysis
            if "catastrophe" in analysis_results:
                catastrophe_data = analysis_results["catastrophe"]
                if hasattr(catastrophe_data, 'data'):
                    catastrophe_insights = self._extract_catastrophe_insights(catastrophe_data.data)
                    insights["insights"].extend(catastrophe_insights)
            
            # Extract insights from event patterns
            if "event_patterns" in analysis_results:
                event_patterns = analysis_results["event_patterns"]
                pattern_insights = self._extract_pattern_insights(event_patterns)
                insights["insights"].extend(pattern_insights)
            
        except Exception as e:
            logger.error(f"Error extracting theoretical insights: {e}")
            insights["error"] = str(e)
        
        return insights
    
    def _extract_manifold_insights(self, manifold_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract insights from manifold analysis"""
        insights = []
        
        try:
            # Dimensionality insights
            if "intrinsic_dimension" in manifold_data:
                dim = manifold_data["intrinsic_dimension"]
                insights.append({
                    "type": "manifold_dimensionality",
                    "insight": f"Memory state manifold has intrinsic dimension {dim}",
                    "confidence": manifold_data.get("confidence", 0.8),
                    "implications": [
                        f"Memory operates in {dim}-dimensional latent space",
                        "State transitions are constrained to this manifold"
                    ]
                })
            
            # Curvature insights
            if "curvature" in manifold_data:
                curvature = manifold_data["curvature"]
                if curvature > 0.1:
                    insights.append({
                        "type": "manifold_curvature",
                        "insight": "Memory manifold shows significant positive curvature",
                        "confidence": 0.7,
                        "implications": [
                            "Memory states cluster in curved regions",
                            "Non-linear dynamics dominate memory evolution"
                        ]
                    })
            
        except Exception as e:
            logger.error(f"Error extracting manifold insights: {e}")
        
        return insights
    
    def _extract_dynamics_insights(self, dynamics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract insights from dynamics analysis"""
        insights = []
        
        try:
            # Stability insights
            if "stability" in dynamics_data:
                stability = dynamics_data["stability"]
                if stability < 0.5:
                    insights.append({
                        "type": "dynamics_instability",
                        "insight": "Memory system shows dynamic instability",
                        "confidence": 0.8,
                        "implications": [
                            "Memory states are highly responsive to inputs",
                            "System may be near critical transitions"
                        ]
                    })
            
            # Attractor insights
            if "attractors" in dynamics_data:
                attractors = dynamics_data["attractors"]
                if len(attractors) > 1:
                    insights.append({
                        "type": "multiple_attractors",
                        "insight": f"Memory dynamics show {len(attractors)} stable attractors",
                        "confidence": 0.7,
                        "implications": [
                            "Multiple stable memory configurations exist",
                            "System can switch between different operational modes"
                        ]
                    })
            
        except Exception as e:
            logger.error(f"Error extracting dynamics insights: {e}")
        
        return insights
    
    def _extract_catastrophe_insights(self, catastrophe_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract insights from catastrophe analysis"""
        insights = []
        
        try:
            # Phase transition insights
            if "phase_transitions" in catastrophe_data:
                transitions = catastrophe_data["phase_transitions"]
                if transitions:
                    insights.append({
                        "type": "phase_transitions",
                        "insight": f"Detected {len(transitions)} memory phase transitions",
                        "confidence": 0.8,
                        "implications": [
                            "Memory undergoes discrete state changes",
                            "Critical thresholds govern memory reorganization"
                        ]
                    })
            
            # Bifurcation insights
            if "bifurcations" in catastrophe_data:
                bifurcations = catastrophe_data["bifurcations"]
                if bifurcations:
                    insights.append({
                        "type": "bifurcations",
                        "insight": "Memory system shows bifurcation behavior",
                        "confidence": 0.7,
                        "implications": [
                            "Memory can split into distinct branches",
                            "Small changes can lead to qualitatively different outcomes"
                        ]
                    })
            
        except Exception as e:
            logger.error(f"Error extracting catastrophe insights: {e}")
        
        return insights
    
    def _extract_pattern_insights(self, pattern_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract insights from event pattern analysis"""
        insights = []
        
        try:
            # Event rate insights
            if "event_rate" in pattern_data:
                rate = pattern_data["event_rate"]
                if rate > 10:  # events per minute
                    insights.append({
                        "type": "high_activity",
                        "insight": f"High memory activity detected: {rate:.1f} events/min",
                        "confidence": 0.9,
                        "implications": [
                            "Memory system is actively processing",
                            "High cognitive load or learning activity"
                        ]
                    })
            
            # Pattern insights
            if "type_distribution" in pattern_data:
                distribution = pattern_data["type_distribution"]
                dominant_event = max(distribution.items(), key=lambda x: x[1])[0]
                
                insights.append({
                    "type": "dominant_event_pattern",
                    "insight": f"Dominant memory activity: {dominant_event}",
                    "confidence": 0.8,
                    "implications": [
                        f"Memory system primarily engaged in {dominant_event}",
                        "Activity pattern indicates specific cognitive focus"
                    ]
                })
            
        except Exception as e:
            logger.error(f"Error extracting pattern insights: {e}")
        
        return insights
    
    def get_stream_status(self) -> Dict[str, Any]:
        """Get current status of all streams"""
        return {
            "active": self.is_active,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime_minutes": (
                (datetime.now() - self.start_time).total_seconds() / 60
                if self.start_time else 0
            ),
            "engram_streamer": {
                "active": self.engram_streamer.is_streaming if self.engram_streamer else False,
                "listeners": len(self.engram_streamer.listeners) if self.engram_streamer else 0
            },
            "memory_analyzer": {
                "initialized": self.memory_analyzer is not None,
                "observations": len(self.memory_analyzer.state_vectors) if self.memory_analyzer else 0,
                "events": len(self.memory_analyzer.event_log) if self.memory_analyzer else 0
            }
        }
    
    def get_analysis_results(self) -> Dict[str, Any]:
        """Get latest analysis results"""
        return self.analysis_results.copy()
    
    def get_analysis_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get historical analysis results"""
        return self.analysis_history[-limit:] if self.analysis_history else []
    
    async def force_analysis_update(self) -> None:
        """Force an immediate update of analysis results"""
        await self._update_analysis_results()
    
    async def shutdown(self) -> None:
        """Shutdown stream manager and cleanup resources"""
        await self.stop_streaming()
        
        # Clear caches
        self.analysis_results.clear()
        self.analysis_history.clear()
        
        logger.info("Stream manager shut down")