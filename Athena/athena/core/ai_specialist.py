#!/usr/bin/env python3
"""
Athena AI Specialist - The Knowledge Weaver

Provides intelligent assistance for knowledge graph operations,
semantic reasoning, and entity relationship management.
"""
import os
import sys
import argparse
import asyncio
import logging

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path))))
sys.path.insert(0, tekton_root)

# Set TEKTON_ROOT environment variable if not set
if 'TEKTON_ROOT' not in os.environ:
    os.environ['TEKTON_ROOT'] = tekton_root

# Also add Athena directory to avoid import issues
athena_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
if athena_dir not in sys.path:
    sys.path.insert(0, athena_dir)

from shared.ai.specialist_worker import AISpecialistWorker

logger = logging.getLogger(__name__)


class AthenaAISpecialist(AISpecialistWorker):
    """Athena - The Knowledge Weaver AI"""
    
    def get_default_model(self) -> str:
        """Get default model for Athena"""
        # Use a model good at logical reasoning
        return "llama3:7b"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for Athena AI"""
        return """You are Athena, the Tekton Knowledge Weaver AI. Your role is to:

1. Design entity relationships and graph structures
2. Generate complex graph queries from natural language
3. Identify missing connections and suggest new relationships
4. Visualize and explain knowledge patterns
5. Extract entities and relationships from unstructured text
6. Perform semantic reasoning and inference across the graph

You have deep knowledge of:
- Graph databases (Neo4j, NetworkX)
- Ontology design and semantic web standards
- Entity recognition and relationship extraction
- Graph algorithms and traversal patterns
- Knowledge representation formats (RDF, OWL)
- Reasoning engines and inference rules

Help users build and query knowledge graphs effectively, discovering insights through connected data."""
    
    async def process_message(self, message: dict) -> dict:
        """Process Athena-specific messages"""
        msg_type = message.get('type', '')
        
        if msg_type == 'graph_query':
            # Custom handler for graph query requests
            return {
                'type': 'graph_query_response',
                'ai_id': self.ai_id,
                'query': 'Generating graph query...',
                'entities': [],
                'relationships': []
            }
        
        # Default to base class handling
        return await self._handle_chat(message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Athena AI Specialist')
    parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    parser.add_argument('--component', default='athena', help='Component name')
    parser.add_argument('--ai-id', default='athena-ai', help='AI identifier')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the AI specialist
    specialist = AthenaAISpecialist(
        ai_id=args.ai_id,
        component=args.component,
        port=args.port,
        description="Knowledge graph and semantic reasoning expert"
    )
    
    logger.info(f"Starting Athena AI specialist on port {args.port}")
    
    try:
        specialist.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Athena AI specialist")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()