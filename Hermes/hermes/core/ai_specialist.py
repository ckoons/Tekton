#!/usr/bin/env python3
"""
Hermes AI Specialist - The Service Orchestrator

Provides intelligent assistance for service discovery, registration,
health monitoring, and communication patterns in the Tekton platform.
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

# Also add Hermes directory to avoid import issues
hermes_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
if hermes_dir not in sys.path:
    sys.path.insert(0, hermes_dir)

from shared.ai.specialist_worker import AISpecialistWorker

logger = logging.getLogger(__name__)


class HermesAISpecialist(AISpecialistWorker):
    """Hermes - The Service Orchestrator AI"""
    
    def get_default_model(self) -> str:
        """Get default model for Hermes"""
        # Use a smaller, faster model for service management
        return "llama3:7b"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for Hermes AI"""
        return """You are Hermes, the Tekton Service Orchestrator AI. Your role is to:

1. Monitor and explain service health across the platform
2. Help debug registration and discovery issues
3. Analyze message routing and delivery patterns
4. Suggest optimal communication strategies between components
5. Track event flow and identify bottlenecks
6. Assist with API gateway configuration

You have deep knowledge of:
- Service registry patterns and best practices
- RESTful API design and troubleshooting
- Event-driven architectures
- Service mesh concepts
- Health check strategies
- Circuit breaker patterns

Be concise, technical, and focused on solving service-related issues."""
    
    async def process_message(self, message: dict) -> dict:
        """Process Hermes-specific messages"""
        msg_type = message.get('type', '')
        
        if msg_type == 'service_status':
            # Custom handler for service status requests
            return {
                'type': 'service_status_response',
                'ai_id': self.ai_id,
                'analysis': 'Analyzing service registry...',
                'recommendations': []
            }
        
        # Default to base class handling
        return await self._handle_chat(message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Hermes AI Specialist')
    parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    parser.add_argument('--component', default='hermes', help='Component name')
    parser.add_argument('--ai-id', default='hermes-ai', help='AI identifier')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the AI specialist
    specialist = HermesAISpecialist(
        ai_id=args.ai_id,
        component=args.component,
        port=args.port,
        description="Service registry and messaging orchestrator"
    )
    
    logger.info(f"Starting Hermes AI specialist on port {args.port}")
    
    try:
        specialist.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Hermes AI specialist")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()