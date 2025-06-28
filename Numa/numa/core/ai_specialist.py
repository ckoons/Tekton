#!/usr/bin/env python3
"""
Numa AI Specialist - Platform AI Mentor

This is a minimal implementation for testing the AI infrastructure.
"""
import os
import sys
import argparse
import asyncio
import logging

# Add Tekton root to path
script_path = os.path.realpath(__file__)
numa_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path))))
sys.path.insert(0, numa_root)

from shared.ai.specialist_worker import AISpecialistWorker

logger = logging.getLogger(__name__)


class NumaAISpecialist(AISpecialistWorker):
    """Numa - The platform AI mentor"""
    
    def get_default_model(self) -> str:
        """Get default model for Numa"""
        # Use Ollama for testing
        return "llama3:7b"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for Numa"""
        return """You are Numa, the Tekton platform AI mentor. Your role is to:
1. Guide users through the Tekton platform
2. Coordinate with other AI specialists
3. Provide high-level insights about the system
4. Help with platform-wide questions and issues

You have knowledge of all Tekton components and can help users understand
how they work together. Be helpful, concise, and knowledgeable."""
    
    async def process_message(self, message: dict) -> dict:
        """Process Numa-specific messages"""
        msg_type = message.get('type', '')
        
        if msg_type == 'platform_status':
            # Custom handler for platform status requests
            return {
                'type': 'platform_status_response',
                'ai_id': self.ai_id,
                'status': 'Numa is monitoring the platform',
                'components': 'All systems operational'
            }
        
        # Default to base class handling
        return await self._handle_chat(message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Numa AI Specialist')
    parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    parser.add_argument('--component', default='numa', help='Component name')
    parser.add_argument('--ai-id', default='numa-ai', help='AI identifier')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the AI specialist
    specialist = NumaAISpecialist(
        ai_id=args.ai_id,
        component=args.component,
        port=args.port,
        description="Platform AI mentor and coordinator"
    )
    
    logger.info(f"Starting Numa AI specialist on port {args.port}")
    
    try:
        specialist.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Numa AI specialist")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()