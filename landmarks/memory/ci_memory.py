"""
CI Memory System - Persistent memory for Companion Intelligences
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

from ..core.registry import LandmarkRegistry
from ..core.landmark import Landmark


class CIMemory:
    """
    Persistent memory system for Companion Intelligences.
    Provides context persistence across sessions and landmark access.
    """
    
    def __init__(self, ci_name: str):
        self.ci_name = ci_name
        self.memory_root = Path("/Users/cskoons/projects/github/Tekton/ci_memory")
        self.memory_dir = self.memory_root / ci_name
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory files
        self.session_file = self.memory_dir / "current_session.json"
        self.context_file = self.memory_dir / "context.json"
        self.knowledge_file = self.memory_dir / "knowledge.json"
        self.conversation_file = self.memory_dir / "conversations.json"
        
        # Load memories
        self.working_memory = self._load_memory(self.session_file)
        self.long_term_memory = self._load_memory(self.knowledge_file)
        self.conversation_history = self._load_memory(self.conversation_file)
        
        # Initialize if new CI
        if not self.working_memory:
            self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize memory structure for new CI"""
        self.working_memory = {
            'ci_name': self.ci_name,
            'created': datetime.now().isoformat(),
            'session_count': 0,
            'current_focus': None,
            'active_tasks': [],
            'memory': defaultdict(dict)
        }
        
        self.long_term_memory = {
            'learned_patterns': {},
            'component_expertise': {},
            'decision_history': [],
            'frequently_accessed': {}
        }
        
        self.save()
    
    def remember(self, key: str, value: Any, category: str = "general"):
        """
        Store information in working memory.
        
        Args:
            key: Memory key
            value: Information to store
            category: Category for organization (e.g., "decisions", "tasks", "context")
        """
        if 'memory' not in self.working_memory:
            self.working_memory['memory'] = {}
            
        if category not in self.working_memory['memory']:
            self.working_memory['memory'][category] = {}
            
        self.working_memory['memory'][category][key] = {
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'access_count': 0
        }
        
        self.save()
    
    def recall(self, key: str, category: str = "general") -> Optional[Any]:
        """
        Retrieve information from memory.
        
        Args:
            key: Memory key
            category: Category to search in
            
        Returns:
            Stored value or None if not found
        """
        memory = self.working_memory.get('memory', {})
        
        if category in memory and key in memory[category]:
            item = memory[category][key]
            item['access_count'] += 1
            item['last_accessed'] = datetime.now().isoformat()
            self.save()
            return item['value']
            
        # Check long-term memory
        if category in self.long_term_memory and key in self.long_term_memory[category]:
            return self.long_term_memory[category][key]
            
        return None
    
    def learn(self, pattern: str, example: Dict[str, Any], category: str = "patterns"):
        """
        Store learned patterns in long-term memory.
        
        Args:
            pattern: Pattern name
            example: Example of the pattern
            category: Type of learning
        """
        if category not in self.long_term_memory:
            self.long_term_memory[category] = {}
            
        if pattern not in self.long_term_memory[category]:
            self.long_term_memory[category][pattern] = {
                'examples': [],
                'first_seen': datetime.now().isoformat(),
                'frequency': 0
            }
        
        self.long_term_memory[category][pattern]['examples'].append(example)
        self.long_term_memory[category][pattern]['frequency'] += 1
        self.long_term_memory[category][pattern]['last_seen'] = datetime.now().isoformat()
        
        self.save()
    
    def set_focus(self, component: str, task: str):
        """Set current focus area"""
        self.working_memory['current_focus'] = {
            'component': component,
            'task': task,
            'started': datetime.now().isoformat()
        }
        self.save()
    
    def add_conversation(self, role: str, content: str, context: Optional[Dict] = None):
        """Add to conversation history"""
        if 'conversations' not in self.conversation_history:
            self.conversation_history['conversations'] = []
            
        self.conversation_history['conversations'].append({
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'content': content,
            'context': context or {}
        })
        
        # Keep last 100 conversations
        if len(self.conversation_history['conversations']) > 100:
            self.conversation_history['conversations'] = self.conversation_history['conversations'][-100:]
            
        self.save()
    
    def search_landmarks(self, query: str, component: Optional[str] = None) -> List[Landmark]:
        """
        Search landmarks relevant to a query.
        
        Args:
            query: Search query
            component: Optional component filter
            
        Returns:
            List of relevant landmarks
        """
        # Track search for learning
        self.remember(f"search_{datetime.now().isoformat()}", 
                     {'query': query, 'component': component}, 
                     category='searches')
        
        # Use registry search
        results = LandmarkRegistry.search(query)
        
        # Filter by component if specified
        if component:
            results = [l for l in results if l.component == component]
            
        # Learn from frequently accessed landmarks
        for landmark in results[:5]:  # Top 5 results
            freq_key = f"landmark_{landmark.id}"
            current = self.long_term_memory.get('frequently_accessed', {}).get(freq_key, 0)
            
            if 'frequently_accessed' not in self.long_term_memory:
                self.long_term_memory['frequently_accessed'] = {}
                
            self.long_term_memory['frequently_accessed'][freq_key] = current + 1
            
        return results
    
    def get_landmarks_for_component(self, component: str) -> List[Landmark]:
        """Get all landmarks for a specific component"""
        return LandmarkRegistry.list(component=component)
    
    def get_related_landmarks(self, landmark_id: str) -> List[Landmark]:
        """Get landmarks related to a given landmark"""
        return LandmarkRegistry.get_related(landmark_id)
    
    def summarize_session(self) -> Dict[str, Any]:
        """Summarize current session for handoff"""
        memory = self.working_memory.get('memory', {})
        
        return {
            'ci_name': self.ci_name,
            'session_start': self.working_memory.get('created'),
            'current_focus': self.working_memory.get('current_focus'),
            'active_tasks': self.working_memory.get('active_tasks', []),
            'memory_categories': list(memory.keys()),
            'items_remembered': sum(len(items) for items in memory.values()),
            'recent_searches': [
                item['value'] for key, item in memory.get('searches', {}).items()
            ][-10:]  # Last 10 searches
        }
    
    def _load_memory(self, file_path: Path) -> Dict[str, Any]:
        """Load memory from file"""
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save(self):
        """Save all memories to disk"""
        # Save working memory
        with open(self.session_file, 'w') as f:
            json.dump(self.working_memory, f, indent=2)
            
        # Save long-term memory
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.long_term_memory, f, indent=2)
            
        # Save conversation history
        with open(self.conversation_file, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
    
    def new_session(self):
        """Start a new session while preserving long-term memory"""
        # Increment session count
        self.working_memory['session_count'] = self.working_memory.get('session_count', 0) + 1
        
        # Archive current working memory to long-term if important
        important_memories = self.working_memory.get('memory', {}).get('decisions', {})
        if important_memories:
            if 'decision_history' not in self.long_term_memory:
                self.long_term_memory['decision_history'] = []
                
            self.long_term_memory['decision_history'].append({
                'session': self.working_memory['session_count'],
                'date': datetime.now().isoformat(),
                'decisions': important_memories
            })
        
        # Reset working memory but keep identity
        self._initialize_memory()
        self.working_memory['session_count'] = self.working_memory.get('session_count', 0)
        
        self.save()


class NumaMemory(CIMemory):
    """
    Specialized memory for Numa, the overseer CI.
    Includes additional capabilities for coordinating other CIs.
    """
    
    def __init__(self):
        super().__init__("Numa")
        
        # Additional Numa-specific memory
        self.ci_registry_file = self.memory_dir / "ci_registry.json"
        self.ci_registry = self._load_memory(self.ci_registry_file)
        
        if not self.ci_registry:
            self._initialize_ci_registry()
    
    def _initialize_ci_registry(self):
        """Initialize registry of other CIs"""
        self.ci_registry = {
            'companion_intelligences': {
                'Hermes-CI': {
                    'domain': 'messaging',
                    'expertise': ['websocket', 'pub-sub', 'event-routing'],
                    'last_interaction': None
                },
                'Engram-CI': {
                    'domain': 'memory',
                    'expertise': ['storage', 'retrieval', 'semantic-search'],
                    'last_interaction': None
                },
                'Apollo-CI': {
                    'domain': 'orchestration',
                    'expertise': ['coordination', 'planning', 'optimization'],
                    'last_interaction': None
                },
                'Prometheus-CI': {
                    'domain': 'ai-integration',
                    'expertise': ['llm', 'prompting', 'model-selection'],
                    'last_interaction': None
                }
            }
        }
        self.save_ci_registry()
    
    def route_to_ci(self, query: str) -> str:
        """Determine which CI should handle a query"""
        query_lower = query.lower()
        
        # Simple keyword routing for now
        routing_map = {
            'Hermes-CI': ['message', 'websocket', 'event', 'pub', 'sub'],
            'Engram-CI': ['memory', 'storage', 'remember', 'recall', 'search'],
            'Apollo-CI': ['orchestr', 'coordinate', 'plan', 'optimize', 'action'],
            'Prometheus-CI': ['llm', 'ai', 'model', 'prompt', 'gpt', 'claude']
        }
        
        for ci, keywords in routing_map.items():
            if any(keyword in query_lower for keyword in keywords):
                # Update last interaction
                self.ci_registry['companion_intelligences'][ci]['last_interaction'] = \
                    datetime.now().isoformat()
                self.save_ci_registry()
                return ci
                
        return 'Numa'  # Default to self
    
    def save_ci_registry(self):
        """Save CI registry"""
        with open(self.ci_registry_file, 'w') as f:
            json.dump(self.ci_registry, f, indent=2)