#!/usr/bin/env python3
"""
Ergon AI Specialist - The Agent Coordinator

Provides intelligent assistance for agent creation, workflow orchestration,
and multi-agent collaboration in the Tekton platform.
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

from shared.ai.specialist_worker import AISpecialistWorker

logger = logging.getLogger(__name__)


class ErgonAISpecialist(AISpecialistWorker):
    """Ergon - The Agent Coordinator AI"""
    
    def get_default_model(self) -> str:
        """Get default model for Ergon"""
        # Use a model good at planning and coordination
        return "llama3:7b"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for Ergon AI"""
        return """You are Ergon, the Tekton Agent Coordinator AI. Your role is to:

1. Design specialized agents for specific tasks
2. Create and optimize multi-agent workflows
3. Debug agent interactions and tool usage
4. Suggest appropriate tools for agent capabilities
5. Monitor agent performance and resource usage
6. Facilitate multi-agent collaboration patterns

You have deep knowledge of:
- Agent architectures and design patterns
- Tool integration and function calling
- Workflow orchestration strategies
- Agent communication protocols
- Task decomposition and delegation
- Performance optimization for agent systems

Help users create effective agents and coordinate complex multi-agent operations."""
    
    async def process_message(self, message: dict) -> dict:
        """Process Ergon-specific messages"""
        msg_type = message.get('type', '')
        
        if msg_type == 'agent_design':
            # Custom handler for agent design requests
            return {
                'type': 'agent_design_response',
                'ai_id': self.ai_id,
                'agent_spec': 'Designing agent...',
                'tools_recommended': [],
                'workflow_steps': []
            }
        
        # Default to base class handling
        return await self._handle_chat(message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Ergon AI Specialist')
    parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    parser.add_argument('--component', default='ergon', help='Component name')
    parser.add_argument('--ai-id', default='ergon-ai', help='AI identifier')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the AI specialist
    specialist = ErgonAISpecialist(
        ai_id=args.ai_id,
        component=args.component,
        port=args.port,
        description="Agent creation and workflow orchestration expert"
    )
    
    logger.info(f"Starting Ergon AI specialist on port {args.port}")
    
    try:
        specialist.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Ergon AI specialist")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()