#!/usr/bin/env python3
"""
Prometheus AI Specialist - The Strategic Planner

Provides intelligent assistance for project planning, resource optimization,
and strategic decision-making in the Tekton platform.
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


class PrometheusAISpecialist(AISpecialistWorker):
    """Prometheus - The Strategic Planner AI"""
    
    def get_default_model(self) -> str:
        """Get default model for Prometheus"""
        # Use a model good at analytical thinking
        return "llama3:7b"
    
    def get_system_prompt(self) -> str:
        """Get system prompt for Prometheus AI"""
        return """You are Prometheus, the Tekton Strategic Planner AI. Your role is to:

1. Analyze requirements and generate optimal project plans
2. Identify critical paths and potential bottlenecks
3. Suggest resource allocations and timeline adjustments
4. Perform risk analysis and mitigation planning
5. Generate retrospective insights from completed projects
6. Provide data-driven improvement recommendations

You have deep knowledge of:
- Project management methodologies (Agile, Waterfall, Hybrid)
- Resource optimization algorithms
- Risk assessment frameworks
- Critical path analysis
- Gantt charts and dependency mapping
- Performance metrics and KPIs

Help users plan effectively, anticipate challenges, and optimize their development workflows."""
    
    async def process_message(self, message: dict) -> dict:
        """Process Prometheus-specific messages"""
        msg_type = message.get('type', '')
        
        if msg_type == 'project_plan':
            # Custom handler for project planning requests
            return {
                'type': 'project_plan_response',
                'ai_id': self.ai_id,
                'plan': 'Generating project plan...',
                'critical_path': [],
                'risk_factors': [],
                'timeline': {}
            }
        
        # Default to base class handling
        return await self._handle_chat(message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Prometheus AI Specialist')
    parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    parser.add_argument('--component', default='prometheus', help='Component name')
    parser.add_argument('--ai-id', default='prometheus-ai', help='AI identifier')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the AI specialist
    specialist = PrometheusAISpecialist(
        ai_id=args.ai_id,
        component=args.component,
        port=args.port,
        description="Project planning and resource optimization expert"
    )
    
    logger.info(f"Starting Prometheus AI specialist on port {args.port}")
    
    try:
        specialist.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Prometheus AI specialist")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()