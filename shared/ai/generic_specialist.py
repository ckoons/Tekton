# @tekton-module: Generic AI Specialist implementation
# @tekton-depends: specialist_worker, logging_setup
# @tekton-provides: component-ai-specialist, auto-configuration
# @tekton-version: 1.0.0
# @tekton-executable: true

"""
Generic AI Specialist implementation that can be used by any component.

This provides a standard AI specialist that automatically configures itself
based on the component it's launched for.
"""
import os
import sys
import argparse
import logging
from typing import Dict, Any

# Import landmarks
try:
    from landmarks import architecture_decision, state_checkpoint
except ImportError:
    # If landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator

# Add parent directory to path for imports
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
sys.path.insert(0, tekton_root)

# Set TEKTON_ROOT environment variable if not set
if 'TEKTON_ROOT' not in os.environ:
    os.environ['TEKTON_ROOT'] = tekton_root

from shared.ai.specialist_worker import AISpecialistWorker
from shared.utils.logging_setup import setup_component_logging

# @tekton-data: Component expertise configuration
# @tekton-static: true
# @tekton-purpose: Define AI specialist personalities
COMPONENT_EXPERTISE = {
    'apollo': {
        'title': 'The Codebase Oracle',
        'expertise': 'Static code analysis, quality metrics, and codebase intelligence',
        'focus': 'code quality, static analysis, metrics collection, and dependency analysis'
    },
    'penia': {
        'title': 'The Budget Guardian',
        'expertise': 'Budget management, cost optimization, and resource allocation',
        'focus': 'API usage tracking, cost analysis, budget enforcement, and optimization recommendations'
    },
    'telos': {
        'title': 'The Requirements Tracker',
        'expertise': 'Requirements engineering, traceability, and validation',
        'focus': 'requirement management, traceability analysis, validation, and change impact'
    },
    'synthesis': {
        'title': 'The Integration Architect',
        'expertise': 'System integration, API composition, and workflow synthesis',
        'focus': 'API integration, workflow composition, system interoperability, and data transformation'
    },
    'metis': {
        'title': 'The Workflow Designer',
        'expertise': 'Workflow orchestration, process optimization, and automation',
        'focus': 'workflow design, process automation, optimization strategies, and execution monitoring'
    },
    'noesis': {
        'title': 'The Insight Generator',
        'expertise': 'Data analysis, pattern recognition, and insight generation',
        'focus': 'data mining, pattern detection, anomaly identification, and actionable insights'
    },
    'hephaestus': {
        'title': 'The UI Craftsman',
        'expertise': 'User interface development, component architecture, and visual design',
        'focus': 'UI components, CSS architecture, JavaScript optimization, and accessibility'
    },
    'terma': {
        'title': 'The Definition Keeper',
        'expertise': 'Terminology management, glossary maintenance, and semantic consistency',
        'focus': 'term definitions, semantic relationships, consistency checking, and knowledge organization'
    },
    'harmonia': {
        'title': 'The Workflow Harmonizer',
        'expertise': 'Cross-component workflow coordination and system harmony',
        'focus': 'workflow coordination, component synchronization, conflict resolution, and system optimization'
    },
    'tekton_core': {
        'title': 'The Platform Orchestrator',
        'expertise': 'Core platform services, component lifecycle, and system coordination',
        'focus': 'platform management, service orchestration, health monitoring, and system integration'
    },
    'sophia': {
        'title': 'The Wisdom Keeper',
        'expertise': 'Knowledge synthesis, learning patterns, and wisdom extraction',
        'focus': 'knowledge aggregation, pattern synthesis, learning optimization, and wisdom sharing'
    },
    'athena': {
        'title': 'The Knowledge Weaver',
        'expertise': 'Knowledge graph construction, semantic reasoning, and intelligent querying',
        'focus': 'knowledge graphs, semantic relationships, reasoning algorithms, and query optimization'
    },
    'hermes': {
        'title': 'The Service Orchestrator',
        'expertise': 'Service coordination, health monitoring, and inter-component communication',
        'focus': 'service discovery, health checks, message routing, and system coordination'
    },
    'engram': {
        'title': 'The Memory Curator',
        'expertise': 'Memory management, semantic search, and knowledge persistence',
        'focus': 'memory storage, retrieval optimization, semantic indexing, and knowledge curation'
    },
    'rhetor': {
        'title': 'The Prompt Architect',
        'expertise': 'LLM orchestration, prompt engineering, and response optimization',
        'focus': 'prompt design, model selection, response quality, and conversation management'
    },
    'ergon': {
        'title': 'The Agent Coordinator',
        'expertise': 'Agent creation, workflow orchestration, and task distribution',
        'focus': 'agent lifecycle, task assignment, workflow execution, and coordination strategies'
    },
    'prometheus': {
        'title': 'The Strategic Planner',
        'expertise': 'Project planning, resource optimization, and strategic analysis',
        'focus': 'project planning, resource allocation, risk assessment, and milestone tracking'
    },
    'numa': {
        'title': 'The Specialist Orchestrator',
        'expertise': 'AI specialist management, model coordination, and capability integration',
        'focus': 'AI lifecycle management, model selection, capability routing, and performance optimization'
    }
}


# @tekton-class: Generic AI specialist implementation
# @tekton-singleton: false
# @tekton-lifecycle: worker
# @tekton-configurable: true
@architecture_decision(
    title="Generic AI Specialist Pattern",
    rationale="Single implementation adapts to any component via configuration",
    alternatives_considered=["Component-specific implementations", "Plugin architecture"],
    impacts=["maintainability", "consistency", "flexibility"]
)
class GenericAISpecialist(AISpecialistWorker):
    """Generic AI specialist that can be used by any component."""
    
    def __init__(self, ai_id: str, component: str, port: int):
        # Get component info
        comp_info = COMPONENT_EXPERTISE.get(component.lower(), {
            'title': f'The {component.title()} Specialist',
            'expertise': f'{component.title()} operations and management',
            'focus': f'{component.lower()} specific tasks and operations'
        })
        
        super().__init__(
            ai_id=ai_id,
            component=component,
            port=port,
            description=f"AI specialist for {component.title()} - {comp_info['title']}"
        )
        
        self.component_info = comp_info
        self.logger.info(f"Initialized {component} AI specialist as '{comp_info['title']}'")
        self.logger.debug(f"Component expertise: {comp_info['expertise']}")
    
    # @tekton-method: Generate component-specific system prompt
    # @tekton-dynamic: true
    # @tekton-returns: system-prompt
    def get_system_prompt(self) -> str:
        """Get system prompt for this AI specialist."""
        return f"""You are {self.component_info['title']}, the AI specialist for {self.component}.

Your expertise: {self.component_info['expertise']}

Your primary focus areas:
{self.component_info['focus']}

You work as part of the Tekton AI platform, collaborating with other AI specialists to provide comprehensive software engineering support. Always provide helpful, accurate, and actionable responses within your domain of expertise.

When asked about capabilities outside your expertise, acknowledge the limitation and suggest which other Tekton AI specialist might be better suited to help."""
    
    # @tekton-method: Process component-specific messages
    # @tekton-async: true
    # @tekton-extensible: true
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process component-specific messages."""
        msg_type = message.get('type', 'unknown')
        
        # Let base class handle standard messages
        if msg_type in ['ping', 'health', 'info', 'chat']:
            return await self.handlers[msg_type](message)
        
        # Handle component-specific messages
        return {
            'type': 'response',
            'ai_id': self.ai_id,
            'content': f"Received {msg_type} message. As {self.component_info['title']}, I specialize in {self.component_info['expertise']}."
        }


# @tekton-function: Main entry point
# @tekton-entry-point: true
# @tekton-cli: true
def main():
    """Main entry point for generic AI specialist."""
    parser = argparse.ArgumentParser(description='Generic AI Specialist')
    parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    parser.add_argument('--component', type=str, required=True, help='Component name')
    parser.add_argument('--ai-id', type=str, required=True, help='AI ID')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_component_logging(f'{args.component}_ai', log_level)
    
    # Create and run specialist
    specialist = GenericAISpecialist(
        ai_id=args.ai_id,
        component=args.component,
        port=args.port
    )
    
    logger.info(f"Starting {args.component} AI specialist on port {args.port}")
    specialist.run()


if __name__ == '__main__':
    main()