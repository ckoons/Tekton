#!/usr/bin/env python3
"""
Rhetor AI Specialist - The Prompt Architect

Provides intelligent assistance for LLM orchestration, prompt engineering,
and model selection in the Tekton platform.
"""
import os
import sys
import argparse
import asyncio
import logging

# Add Tekton root to path
script_path = os.path.realpath(__file__)
rhetor_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path))))
sys.path.insert(0, rhetor_root)

from shared.ai.specialist_worker import AISpecialistWorker

logger = logging.getLogger(__name__)


class RhetorAISpecialist(AISpecialistWorker):
    """Rhetor - The Prompt Architect AI"""
    
    def get_default_model(self) -> str:
        """Get default model for Rhetor"""
        # Use a model good at understanding language patterns
        return "llama3:7b"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for Rhetor AI"""
        return """You are Rhetor, the Tekton Prompt Architect AI. Your role is to:

1. Design and optimize prompts for different tasks
2. Select appropriate models based on requirements and budget
3. Analyze prompt performance and suggest improvements
4. Create and manage prompt template libraries
5. Monitor LLM usage costs and suggest optimizations
6. Orchestrate multi-model collaborations for complex tasks

You have deep knowledge of:
- Prompt engineering best practices
- Model capabilities and limitations (GPT-4, Claude, Llama, etc.)
- Token optimization strategies
- Cost-performance trade-offs
- Chain-of-thought prompting
- Few-shot and zero-shot learning techniques
- Multi-model orchestration patterns

Help users craft effective prompts and choose the right models for their specific needs."""
    
    async def process_message(self, message: dict) -> dict:
        """Process Rhetor-specific messages"""
        msg_type = message.get('type', '')
        
        if msg_type == 'prompt_optimization':
            # Custom handler for prompt optimization requests
            return {
                'type': 'prompt_optimization_response',
                'ai_id': self.ai_id,
                'original_prompt': message.get('prompt', ''),
                'optimized_prompt': 'Optimizing prompt...',
                'suggestions': []
            }
        
        # Default to base class handling
        return await self._handle_chat(message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Rhetor AI Specialist')
    parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    parser.add_argument('--component', default='rhetor', help='Component name')
    parser.add_argument('--ai-id', default='rhetor-ai', help='AI identifier')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the AI specialist
    specialist = RhetorAISpecialist(
        ai_id=args.ai_id,
        component=args.component,
        port=args.port,
        description="LLM orchestration and prompt engineering expert"
    )
    
    logger.info(f"Starting Rhetor AI specialist on port {args.port}")
    
    try:
        specialist.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Rhetor AI specialist")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()