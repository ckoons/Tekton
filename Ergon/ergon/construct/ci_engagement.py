"""
CI Engagement for Construct Dialog.

Enables CIs to actively participate in the solution composition process.
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import landmarks with fallback
try:
    from landmarks import (
        ci_orchestrated,
        ci_collaboration,
        integration_point
    )
except ImportError:
    def ci_orchestrated(**kwargs):
        def decorator(func): return func
        return decorator
    def ci_collaboration(**kwargs):
        def decorator(func): return func
        return decorator
    def integration_point(**kwargs):
        def decorator(func): return func
        return decorator


@ci_orchestrated(
    title="Construct CI Orchestrator",
    description="CI that guides users through solution building",
    orchestrator="ergon-ai",
    workflow=["understand", "suggest", "validate", "build", "deploy"],
    ci_capabilities=["requirement_analysis", "component_suggestion", "code_generation"]
)
class ConstructCI:
    """
    CI personality for Construct system.
    
    The CI actively helps users build solutions by:
    - Asking clarifying questions
    - Suggesting components
    - Validating choices
    - Offering improvements
    """
    
    def __init__(self, ci_name: str = "construct-ci"):
        """Initialize the Construct CI."""
        self.name = ci_name
        self.context = {}
        self.conversation_history = []
        
        # CI's understanding of its role
        self.purpose = """
I am the Construct CI, specialized in helping you build solutions.

My role is to:
1. Understand what you're trying to build
2. Suggest the best components from the Registry
3. Help you make architectural decisions
4. Validate your choices make sense
5. Guide you through deployment options
6. Create the right CI companion for your solution

I'm not just collecting answers - I'm actively thinking about your solution
and will offer suggestions, warnings, and improvements as we go.
"""
    
    @integration_point(
        title="User Response Processing",
        description="CI analyzes user responses and provides guidance",
        target_component="construct_dialog",
        protocol="internal_api",
        data_flow="user_response → CI_analysis → suggestions"
    )
    def process_user_response(self, question_id: str, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user's response to a question.
        
        Args:
            question_id: Which question was answered
            response: User's response
            context: Current workspace/responses context
            
        Returns:
            CI's analysis and suggestions
        """
        # Store in conversation history
        self.conversation_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'question_id': question_id,
            'user_response': response,
            'context': context
        })
        
        # Analyze based on question type
        if question_id == 'purpose':
            return self._analyze_purpose(response, context)
        elif question_id == 'components':
            return self._analyze_components(response, context)
        elif question_id == 'deployment':
            return self._analyze_deployment(response, context)
        elif question_id == 'ci_association':
            return self._analyze_ci_needs(response, context)
        else:
            return self._default_analysis(question_id, response, context)
    
    def _analyze_purpose(self, purpose: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the user's purpose and suggest approach."""
        analysis = {
            'understanding': '',
            'suggestions': [],
            'warnings': [],
            'questions': []
        }
        
        purpose_lower = purpose.lower()
        
        # Check for Tekton extraction opportunity
        if 'tekton' in purpose_lower or 'extract' in purpose_lower:
            from .tekton_extractor import get_tekton_suggestions
            tekton_suggestions = get_tekton_suggestions(purpose)
            
            if tekton_suggestions['extraction_available']:
                analysis['suggestions'].append({
                    'type': 'tekton_extraction',
                    'message': "I can help you extract existing Tekton components!",
                    'components': tekton_suggestions['tekton_components']
                })
        
        # Check for deployment tool request
        if 'deployment' in purpose_lower or 'deploy' in purpose_lower:
            analysis['understanding'] = "You're building a deployment tool. This will need careful permission management."
            analysis['suggestions'].append({
                'type': 'architecture',
                'message': "Consider using container isolation for deployment operations"
            })
            analysis['questions'].append("Will this tool deploy to Kubernetes, Docker, or bare metal?")
        
        # Check for CI-centric solution
        if 'claude' in purpose_lower or 'ci' in purpose_lower:
            analysis['understanding'] = "You want a CI-managed solution. Excellent choice!"
            analysis['suggestions'].append({
                'type': 'ci_architecture',
                'message': "I'll help you design this with CI-first principles"
            })
        
        # Check for standalone tool
        if 'standalone' in purpose_lower or 'tool' in purpose_lower:
            analysis['understanding'] = "Building a standalone tool. Let's keep it focused and efficient."
            analysis['suggestions'].append({
                'type': 'packaging',
                'message': "We can use 'aish ci-tool' for lightweight CI management"
            })
        
        return analysis
    
    def _analyze_components(self, components: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze component selection."""
        analysis = {
            'understanding': '',
            'suggestions': [],
            'warnings': [],
            'compatibility': {}
        }
        
        if 'suggest' in components.lower():
            # User wants suggestions
            purpose = context.get('responses', {}).get('purpose', '')
            analysis['suggestions'] = self._suggest_components(purpose)
            analysis['understanding'] = "Let me suggest components based on your purpose."
        else:
            # User specified components
            component_list = [c.strip() for c in components.split(',')]
            analysis['understanding'] = f"You've selected {len(component_list)} components."
            
            # Check compatibility
            for i, comp1 in enumerate(component_list):
                for comp2 in component_list[i+1:]:
                    compat = self._check_compatibility(comp1, comp2)
                    analysis['compatibility'][f"{comp1}-{comp2}"] = compat
                    
                    if not compat['compatible']:
                        analysis['warnings'].append(f"{comp1} and {comp2} may have compatibility issues: {compat['reason']}")
        
        return analysis
    
    def _analyze_deployment(self, deployment: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze deployment choice."""
        analysis = {
            'understanding': '',
            'suggestions': [],
            'implications': []
        }
        
        if 'container' in deployment.lower():
            analysis['understanding'] = "Containerized deployment - great for isolation and portability."
            analysis['implications'] = [
                "Will need Docker or similar container runtime",
                "Can use 'aish container' for CI management",
                "Easy scaling and distribution"
            ]
            analysis['suggestions'].append({
                'type': 'container_config',
                'message': "I'll help configure the container with proper resource limits"
            })
        
        elif 'standalone' in deployment.lower():
            analysis['understanding'] = "Standalone deployment - simple and direct."
            analysis['implications'] = [
                "Runs directly on the host",
                "Lighter resource footprint",
                "May need manual dependency management"
            ]
        
        return analysis
    
    def _analyze_ci_needs(self, ci_choice: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CI association needs."""
        analysis = {
            'understanding': '',
            'ci_prompt': '',
            'configuration': {}
        }
        
        if 'container' in ci_choice:
            analysis['understanding'] = "Container CI - I'll manage the entire lifecycle."
            analysis['ci_prompt'] = self._generate_ci_prompt(context, 'container')
            analysis['configuration'] = {
                'type': 'container',
                'capabilities': ['lifecycle', 'monitoring', 'scaling', 'updates'],
                'command': f"aish container create --name {context.get('name', 'solution')} --ci-managed"
            }
        
        elif 'ci-tool' in ci_choice:
            analysis['understanding'] = "Tool CI - Lightweight management for your standalone tool."
            analysis['ci_prompt'] = self._generate_ci_prompt(context, 'tool')
            analysis['configuration'] = {
                'type': 'tool',
                'capabilities': ['execution', 'monitoring', 'updates'],
                'command': f"aish ci-tool create --name {context.get('name', 'solution')}"
            }
        
        return analysis
    
    def _default_analysis(self, question_id: str, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Default analysis for other questions."""
        return {
            'understanding': f"Noted your response for {question_id}",
            'stored': True
        }
    
    @ci_collaboration(
        title="Component Discovery Collaboration",
        description="CI collaborates with Registry to find components",
        participants=["ergon-ai", "athena-ai"],
        coordination_method="query_registry",
        synchronization="sync"
    )
    def _suggest_components(self, purpose: str) -> List[Dict[str, Any]]:
        """Suggest components based on purpose."""
        suggestions = []
        
        # This would normally query the Registry
        # For now, return common patterns
        if 'data' in purpose.lower():
            suggestions.append({
                'component': 'parser-abc123',
                'reason': 'For data parsing and validation'
            })
            suggestions.append({
                'component': 'analyzer-def456',
                'reason': 'For data analysis and insights'
            })
        
        if 'api' in purpose.lower():
            suggestions.append({
                'component': 'api-gateway',
                'reason': 'For API routing and management'
            })
        
        return suggestions
    
    def _check_compatibility(self, comp1: str, comp2: str) -> Dict[str, Any]:
        """Check if two components are compatible."""
        # This would normally check the Registry
        # For now, return basic compatibility
        return {
            'compatible': True,
            'confidence': 0.95,
            'reason': 'Components can work together'
        }
    
    def _generate_ci_prompt(self, context: Dict[str, Any], ci_type: str) -> str:
        """Generate a prompt for the new CI."""
        purpose = context.get('responses', {}).get('purpose', 'Unknown purpose')
        name = context.get('name', 'solution')
        
        return f"""
You are the CI for {name}, a {ci_type}-based solution.

Purpose: {purpose}

Your responsibilities:
1. Monitor the solution's health and performance
2. Handle updates and evolution
3. Respond to user queries about the solution
4. Manage the solution's lifecycle
5. Collaborate with other CIs as needed

You were created by the Construct system to manage this specific solution.
Work with the user to ensure their solution meets their needs.
"""
    
    def get_guidance(self, stage: str) -> str:
        """Get guidance for a specific stage."""
        guidance = {
            'start': "Let's build something great together! Start by telling me what you want to create.",
            'components': "Now let's choose the right building blocks. I can suggest components or you can specify them.",
            'deployment': "How should we package this? Container gives us isolation, standalone is simpler.",
            'ci': "Would you like a CI to manage this solution? I can create one tailored to your needs.",
            'validation': "Let me check that everything fits together properly...",
            'completion': "Excellent! Your solution is ready. Use Validate to check it, Test to try it, or Publish to share it."
        }
        
        return guidance.get(stage, "I'm here to help at every step.")


# Export for use in Construct
def get_ci_engagement() -> ConstructCI:
    """Get the Construct CI for engagement."""
    return ConstructCI()