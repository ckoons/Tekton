#!/usr/bin/env python3
"""
Engram AI Specialist - The Memory Curator

Provides intelligent assistance for memory management, semantic search,
and memory pattern analysis in the Tekton platform.
"""
import os
import sys
import argparse
import asyncio
import logging

# Add Tekton root to path
script_path = os.path.realpath(__file__)
engram_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path))))
sys.path.insert(0, engram_root)

from shared.ai.specialist_worker import AISpecialistWorker

logger = logging.getLogger(__name__)


class EngramAISpecialist(AISpecialistWorker):
    """Engram - The Memory Curator AI"""
    
    def get_default_model(self) -> str:
        """Get default model for Engram"""
        # Use a model good at semantic understanding
        return "llama3:7b"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for Engram AI"""
        return """You are Engram, the Tekton Memory Curator AI. Your role is to:

1. Optimize memory storage strategies and compartmentalization
2. Suggest semantic search queries for better recall
3. Analyze memory usage patterns and identify redundancies
4. Design memory structures for specific use cases
5. Explain vector embedding choices and their implications
6. Guide latent space operations and memory contextualization

You have deep knowledge of:
- Vector databases and embedding strategies
- Semantic search algorithms
- Memory compartmentalization patterns
- Retrieval-Augmented Generation (RAG)
- Context window management
- Memory persistence and caching strategies

Be precise about memory operations and help users understand the trade-offs between different memory strategies."""
    
    async def process_message(self, message: dict) -> dict:
        """Process Engram-specific messages"""
        msg_type = message.get('type', '')
        
        if msg_type == 'memory_analysis':
            # Custom handler for memory analysis requests
            return {
                'type': 'memory_analysis_response',
                'ai_id': self.ai_id,
                'analysis': 'Analyzing memory patterns...',
                'optimization_suggestions': []
            }
        
        # Default to base class handling
        return await self._handle_chat(message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Engram AI Specialist')
    parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    parser.add_argument('--component', default='engram', help='Component name')
    parser.add_argument('--ai-id', default='engram-ai', help='AI identifier')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the AI specialist
    specialist = EngramAISpecialist(
        ai_id=args.ai_id,
        component=args.component,
        port=args.port,
        description="Memory management and semantic search expert"
    )
    
    logger.info(f"Starting Engram AI specialist on port {args.port}")
    
    try:
        specialist.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Engram AI specialist")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()