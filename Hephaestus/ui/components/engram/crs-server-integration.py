"""
Cognitive Research System - Server Integration
Bridges Engram UI with Sophia/Noesis backend services
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict
import websockets
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class PatternState(Enum):
    EMERGING = "emerging"
    STRENGTHENING = "strengthening"
    STABLE = "stable"
    FADING = "fading"

@dataclass
class CognitivePattern:
    id: str
    name: str
    state: PatternState
    strength: float
    description: str
    detected_at: datetime
    source: str = "engram"
    
@dataclass
class ResearchRequest:
    id: str
    type: str
    query: str
    priority: ResearchPriority
    context: Dict[str, Any]
    requested_at: datetime
    
@dataclass
class Discovery:
    id: str
    summary: str
    details: Dict[str, Any]
    confidence: float
    novelty: str
    sources: List[str]
    discovered_at: datetime

class CognitiveResearchServer:
    def __init__(self, host="localhost", port=8100):
        self.host = host
        self.port = port
        self.connections = defaultdict(set)
        self.patterns = {}
        self.research_queue = asyncio.Queue()
        self.discoveries = {}
        self.learning_history = []
        
        # Component connections
        self.sophia_connection = None
        self.noesis_connection = None
        
    async def start(self):
        """Start the CRS server"""
        logger.info(f"Starting Cognitive Research Server on {self.host}:{self.port}")
        
        # Start WebSocket servers for different streams
        await asyncio.gather(
            self.start_engram_stream(),
            self.start_sophia_stream(),
            self.start_noesis_stream(),
            self.process_research_queue()
        )
    
    async def start_engram_stream(self):
        """Handle Engram cognitive data stream"""
        async def handle_engram(websocket, path):
            logger.info(f"Engram connected from {websocket.remote_address}")
            self.connections['engram'].add(websocket)
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    await self.process_engram_data(data, websocket)
            except websockets.exceptions.ConnectionClosed:
                logger.info("Engram disconnected")
            finally:
                self.connections['engram'].discard(websocket)
        
        await websockets.serve(handle_engram, self.host, self.port, 
                               subprotocols=["engram"])
    
    async def start_sophia_stream(self):
        """Handle Sophia learning engine stream"""
        async def handle_sophia(websocket, path):
            logger.info(f"Sophia connected from {websocket.remote_address}")
            self.connections['sophia'].add(websocket)
            self.sophia_connection = websocket
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    await self.process_sophia_data(data)
            except websockets.exceptions.ConnectionClosed:
                logger.info("Sophia disconnected")
            finally:
                self.connections['sophia'].discard(websocket)
                if self.sophia_connection == websocket:
                    self.sophia_connection = None
        
        await websockets.serve(handle_sophia, self.host, self.port + 1,
                               subprotocols=["sophia"])
    
    async def start_noesis_stream(self):
        """Handle Noesis discovery engine stream"""
        async def handle_noesis(websocket, path):
            logger.info(f"Noesis connected from {websocket.remote_address}")
            self.connections['noesis'].add(websocket)
            self.noesis_connection = websocket
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    await self.process_noesis_data(data)
            except websockets.exceptions.ConnectionClosed:
                logger.info("Noesis disconnected")
            finally:
                self.connections['noesis'].discard(websocket)
                if self.noesis_connection == websocket:
                    self.noesis_connection = None
        
        await websockets.serve(handle_noesis, self.host, self.port + 2,
                               subprotocols=["noesis"])
    
    async def process_engram_data(self, data: Dict, websocket):
        """Process data from Engram UI"""
        data_type = data.get('type')
        
        if data_type == 'pattern_detected':
            pattern = self.create_pattern(data['pattern'])
            await self.handle_pattern_detection(pattern)
            
        elif data_type == 'blindspot_found':
            await self.handle_blindspot(data['blindspot'])
            
        elif data_type == 'inefficiency_detected':
            await self.handle_inefficiency(data['inefficiency'])
            
        elif data_type == 'research_request':
            request = self.create_research_request(data['research'])
            await self.queue_research(request)
            
        elif data_type == 'cognitive_state':
            await self.handle_cognitive_state(data['state'])
    
    async def process_sophia_data(self, data: Dict):
        """Process data from Sophia learning engine"""
        data_type = data.get('type')
        
        if data_type == 'pattern_learned':
            await self.integrate_learned_pattern(data['pattern'])
            
        elif data_type == 'knowledge_update':
            await self.update_knowledge_base(data['knowledge'])
            
        elif data_type == 'learning_complete':
            await self.broadcast_learning_complete(data['learning'])
    
    async def process_noesis_data(self, data: Dict):
        """Process data from Noesis discovery engine"""
        data_type = data.get('type')
        
        if data_type == 'discovery_made':
            discovery = self.create_discovery(data['discovery'])
            await self.handle_discovery(discovery)
            
        elif data_type == 'research_complete':
            await self.handle_research_complete(data['results'])
            
        elif data_type == 'exploration_update':
            await self.broadcast_exploration_update(data['exploration'])
    
    def create_pattern(self, pattern_data: Dict) -> CognitivePattern:
        """Create a CognitivePattern from raw data"""
        return CognitivePattern(
            id=pattern_data.get('id', f"pattern_{datetime.now().timestamp()}"),
            name=pattern_data['name'],
            state=PatternState(pattern_data.get('state', 'emerging')),
            strength=pattern_data.get('strength', 0.5),
            description=pattern_data.get('description', ''),
            detected_at=datetime.now()
        )
    
    def create_research_request(self, request_data: Dict) -> ResearchRequest:
        """Create a ResearchRequest from raw data"""
        return ResearchRequest(
            id=f"research_{datetime.now().timestamp()}",
            type=request_data.get('type', 'general'),
            query=request_data['query'],
            priority=ResearchPriority(request_data.get('priority', 'medium')),
            context=request_data.get('context', {}),
            requested_at=datetime.now()
        )
    
    def create_discovery(self, discovery_data: Dict) -> Discovery:
        """Create a Discovery from raw data"""
        return Discovery(
            id=discovery_data.get('id', f"discovery_{datetime.now().timestamp()}"),
            summary=discovery_data['summary'],
            details=discovery_data.get('details', {}),
            confidence=discovery_data.get('confidence', 0.5),
            novelty=discovery_data.get('novelty', 'interesting'),
            sources=discovery_data.get('sources', []),
            discovered_at=datetime.now()
        )
    
    async def handle_pattern_detection(self, pattern: CognitivePattern):
        """Handle detected pattern"""
        logger.info(f"Pattern detected: {pattern.name} ({pattern.state.value})")
        
        # Store pattern
        self.patterns[pattern.id] = pattern
        
        # If pattern is significant, trigger research
        if pattern.strength > 0.7 and pattern.state in [PatternState.EMERGING, PatternState.STRENGTHENING]:
            await self.trigger_pattern_research(pattern)
        
        # Broadcast to connected clients
        await self.broadcast_to_stream('engram', {
            'type': 'pattern_processed',
            'pattern': asdict(pattern)
        })
    
    async def handle_blindspot(self, blindspot: Dict):
        """Handle detected blindspot"""
        logger.info(f"Blindspot found: {blindspot.get('text', 'Unknown')}")
        
        # Create immediate research request
        research = ResearchRequest(
            id=f"blindspot_{datetime.now().timestamp()}",
            type='blindspot_correction',
            query=self.generate_blindspot_query(blindspot),
            priority=ResearchPriority.HIGH,
            context={'blindspot': blindspot},
            requested_at=datetime.now()
        )
        
        # Queue with high priority
        await self.queue_research(research, priority=True)
        
        # Notify Sophia for learning
        if self.sophia_connection:
            await self.sophia_connection.send(json.dumps({
                'type': 'blindspot_alert',
                'blindspot': blindspot
            }))
    
    async def handle_inefficiency(self, inefficiency: Dict):
        """Handle detected inefficiency"""
        logger.info(f"Inefficiency detected: {inefficiency.get('text', 'Unknown')}")
        
        # Research optimization strategies
        research = ResearchRequest(
            id=f"inefficiency_{datetime.now().timestamp()}",
            type='optimization',
            query=f"optimize {inefficiency.get('text', '')}",
            priority=ResearchPriority.MEDIUM,
            context={'inefficiency': inefficiency},
            requested_at=datetime.now()
        )
        
        await self.queue_research(research)
    
    async def handle_cognitive_state(self, state: Dict):
        """Handle cognitive state update"""
        logger.info(f"Cognitive state update: {state}")
        
        # Adjust research priorities based on cognitive state
        if state.get('brainRegions'):
            await self.adjust_research_priorities(state['brainRegions'])
    
    async def trigger_pattern_research(self, pattern: CognitivePattern):
        """Trigger research for a pattern"""
        research = ResearchRequest(
            id=f"pattern_research_{pattern.id}",
            type='pattern_analysis',
            query=f"{pattern.name} {pattern.description} best practices",
            priority=ResearchPriority.MEDIUM,
            context={'pattern': asdict(pattern)},
            requested_at=datetime.now()
        )
        
        await self.queue_research(research)
    
    def generate_blindspot_query(self, blindspot: Dict) -> str:
        """Generate search query to address blindspot"""
        text = blindspot.get('text', '')
        keywords = self.extract_keywords(text)
        return f"avoid {' '.join(keywords)} common mistakes best practices"
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'of', 'in', 'to'}
        words = text.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 3]
    
    async def queue_research(self, request: ResearchRequest, priority: bool = False):
        """Queue research request"""
        if priority:
            # Add to front of queue for high priority
            temp_queue = asyncio.Queue()
            await temp_queue.put(request)
            
            # Transfer existing queue
            while not self.research_queue.empty():
                item = await self.research_queue.get()
                await temp_queue.put(item)
            
            self.research_queue = temp_queue
        else:
            await self.research_queue.put(request)
        
        logger.info(f"Queued research: {request.type} (Priority: {request.priority.value})")
    
    async def process_research_queue(self):
        """Process queued research requests"""
        while True:
            try:
                request = await self.research_queue.get()
                await self.execute_research(request)
            except Exception as e:
                logger.error(f"Error processing research: {e}")
            
            await asyncio.sleep(1)  # Rate limiting
    
    async def execute_research(self, request: ResearchRequest):
        """Execute research request"""
        logger.info(f"Executing research: {request.type} - {request.query}")
        
        # Send to Noesis for discovery
        if self.noesis_connection:
            await self.noesis_connection.send(json.dumps({
                'type': 'research_request',
                'request': asdict(request)
            }))
        
        # Simulate research for testing
        await asyncio.sleep(2)
        
        # Generate simulated results
        results = {
            'request_id': request.id,
            'query': request.query,
            'findings': [
                {
                    'source': 'Documentation',
                    'content': f"Best practice for {request.query}",
                    'confidence': 0.8
                }
            ],
            'recommendations': [
                f"Apply {request.type} pattern",
                "Monitor improvements"
            ]
        }
        
        await self.handle_research_complete(results)
    
    async def handle_discovery(self, discovery: Discovery):
        """Handle new discovery"""
        logger.info(f"Discovery made: {discovery.summary}")
        
        # Store discovery
        self.discoveries[discovery.id] = discovery
        
        # Broadcast to Engram
        await self.broadcast_to_stream('engram', {
            'type': 'discovery_made',
            'discovery': asdict(discovery)
        })
        
        # Send to Sophia for learning
        if self.sophia_connection:
            await self.sophia_connection.send(json.dumps({
                'type': 'new_discovery',
                'discovery': asdict(discovery)
            }))
    
    async def handle_research_complete(self, results: Dict):
        """Handle completed research"""
        logger.info(f"Research complete: {results.get('query', 'Unknown')}")
        
        # Broadcast results
        await self.broadcast_to_stream('engram', {
            'type': 'research_complete',
            'results': results
        })
        
        # Store in learning history
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'research',
            'results': results
        })
    
    async def integrate_learned_pattern(self, pattern: Dict):
        """Integrate pattern learned by Sophia"""
        logger.info(f"Integrating learned pattern: {pattern.get('name', 'Unknown')}")
        
        # Broadcast to Engram
        await self.broadcast_to_stream('engram', {
            'type': 'pattern_learned',
            'pattern': pattern
        })
    
    async def update_knowledge_base(self, knowledge: Dict):
        """Update knowledge base with new information"""
        logger.info(f"Knowledge base update: {knowledge.get('topic', 'Unknown')}")
        
        # Broadcast update
        await self.broadcast_to_stream('engram', {
            'type': 'knowledge_updated',
            'knowledge': knowledge
        })
    
    async def adjust_research_priorities(self, brain_regions: Dict):
        """Adjust research priorities based on brain activity"""
        active_regions = [region for region, activity in brain_regions.items() if activity > 0.7]
        
        for region in active_regions:
            if region == 'hippocampus':
                # Prioritize memory consolidation research
                logger.info("Prioritizing memory consolidation research")
            elif region == 'prefrontalCortex':
                # Prioritize planning and solution research
                logger.info("Prioritizing solution exploration")
            elif region == 'temporalLobe':
                # Prioritize language and documentation research
                logger.info("Prioritizing documentation research")
    
    async def broadcast_to_stream(self, stream: str, data: Dict):
        """Broadcast data to all connections in a stream"""
        connections = self.connections.get(stream, set())
        if connections:
            message = json.dumps(data)
            await asyncio.gather(
                *[ws.send(message) for ws in connections],
                return_exceptions=True
            )
    
    async def broadcast_learning_complete(self, learning: Dict):
        """Broadcast learning completion"""
        await self.broadcast_to_stream('engram', {
            'type': 'learning_complete',
            'learning': learning
        })
    
    async def broadcast_exploration_update(self, exploration: Dict):
        """Broadcast exploration update"""
        await self.broadcast_to_stream('engram', {
            'type': 'exploration_update',
            'exploration': exploration
        })

async def main():
    """Main entry point"""
    server = CognitiveResearchServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())