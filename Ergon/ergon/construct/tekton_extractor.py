"""
Tekton Component Extractor for Construct.

Allows extracting parts of Tekton as reusable solutions.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func): return func
        return decorator
    def integration_point(**kwargs):
        def decorator(func): return func
        return decorator


@architecture_decision(
    title="Tekton Component Extraction",
    description="Allow Tekton components to be packaged as reusable solutions",
    rationale="Users want to leverage existing Tekton components in their solutions",
    alternatives_considered=["Copy-paste code", "Git submodules", "Direct dependencies"],
    impacts=["solution_reusability", "component_versioning", "registry_growth"],
    decided_by="Casey",
    decision_date="2025-08-24"
)
class TektonExtractor:
    """Extract Tekton components as solutions."""
    
    # Map of Tekton components that can be extracted
    EXTRACTABLE_COMPONENTS = {
        'athena': {
            'name': 'Athena Knowledge Graph',
            'description': 'Intelligent code understanding and navigation system',
            'capabilities': ['code_analysis', 'knowledge_graph', 'semantic_search'],
            'interfaces': {
                'inputs': [{'name': 'code_path', 'type': 'path'}],
                'outputs': [{'name': 'knowledge_graph', 'type': 'json'}]
            }
        },
        'rhetor': {
            'name': 'Rhetor Communication Hub',
            'description': 'Multi-AI communication and coordination system',
            'capabilities': ['ai_communication', 'team_chat', 'message_routing'],
            'interfaces': {
                'inputs': [{'name': 'message', 'type': 'text'}],
                'outputs': [{'name': 'response', 'type': 'text'}]
            }
        },
        'aish': {
            'name': 'AISH AI Shell',
            'description': 'AI-powered shell for CI interaction',
            'capabilities': ['shell', 'ci_management', 'command_execution'],
            'interfaces': {
                'inputs': [{'name': 'command', 'type': 'text'}],
                'outputs': [{'name': 'result', 'type': 'text'}]
            }
        },
        'hephaestus': {
            'name': 'Hephaestus UI Framework',
            'description': 'Component-based UI system with AI integration',
            'capabilities': ['ui_framework', 'component_system', 'ai_chat'],
            'interfaces': {
                'inputs': [{'name': 'component_config', 'type': 'json'}],
                'outputs': [{'name': 'ui_component', 'type': 'html'}]
            }
        },
        'engram': {
            'name': 'Engram Memory System',
            'description': 'Persistent memory and context management for AIs',
            'capabilities': ['memory', 'context', 'persistence'],
            'interfaces': {
                'inputs': [{'name': 'memory_key', 'type': 'string'}],
                'outputs': [{'name': 'memory_value', 'type': 'json'}]
            }
        }
    }
    
    def __init__(self):
        """Initialize the extractor."""
        self.tekton_root = Path(__file__).parent.parent.parent.parent
    
    def list_extractable(self) -> List[Dict[str, Any]]:
        """List all extractable Tekton components."""
        return [
            {
                'id': comp_id,
                'name': info['name'],
                'description': info['description'],
                'capabilities': info['capabilities']
            }
            for comp_id, info in self.EXTRACTABLE_COMPONENTS.items()
        ]
    
    @integration_point(
        title="Component Extraction",
        description="Extract Tekton component as Registry solution",
        target_component="Registry",
        protocol="solution_package",
        data_flow="tekton_component → solution_definition → registry"
    )
    def extract_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Extract a Tekton component as a solution.
        
        Args:
            component_id: ID of the component to extract
            
        Returns:
            Solution definition ready for Registry
        """
        if component_id not in self.EXTRACTABLE_COMPONENTS:
            return None
        
        info = self.EXTRACTABLE_COMPONENTS[component_id]
        
        # Build solution package
        solution = {
            'type': 'solution',
            'name': info['name'],
            'version': '1.0.0',
            'source': 'tekton',
            'content': {
                'description': info['description'],
                'capabilities': info['capabilities'],
                'interfaces': info['interfaces'],
                'implementation': {
                    'type': 'reference',
                    'module': f'tekton.{component_id}',
                    'requires': ['tekton_core']
                },
                'deployment': {
                    'standalone': component_id in ['aish', 'athena'],
                    'requires_ui': component_id == 'hephaestus',
                    'requires_ai': component_id in ['rhetor', 'aish']
                }
            },
            'metadata': {
                'extracted_from': 'Tekton',
                'component_path': str(self.tekton_root / component_id),
                'documentation': f'https://tekton.ai/docs/{component_id}'
            }
        }
        
        return solution
    
    def suggest_for_purpose(self, purpose: str) -> List[str]:
        """
        Suggest Tekton components based on purpose.
        
        Args:
            purpose: User's stated purpose
            
        Returns:
            List of suggested component IDs
        """
        purpose_lower = purpose.lower()
        suggestions = []
        
        # Simple keyword matching - could be enhanced with NLP
        if 'knowledge' in purpose_lower or 'understand' in purpose_lower:
            suggestions.append('athena')
        
        if 'chat' in purpose_lower or 'communication' in purpose_lower:
            suggestions.append('rhetor')
        
        if 'shell' in purpose_lower or 'command' in purpose_lower:
            suggestions.append('aish')
        
        if 'ui' in purpose_lower or 'interface' in purpose_lower:
            suggestions.append('hephaestus')
        
        if 'memory' in purpose_lower or 'context' in purpose_lower:
            suggestions.append('engram')
        
        return suggestions
    
    def create_extraction_prompt(self, component_id: str) -> str:
        """
        Create a prompt for CI to help with extraction.
        
        Args:
            component_id: Component to extract
            
        Returns:
            Prompt for CI engagement
        """
        info = self.EXTRACTABLE_COMPONENTS.get(component_id, {})
        
        return f"""
You are helping extract the {info.get('name', component_id)} component from Tekton.

Purpose: {info.get('description', 'Unknown')}

Your role is to:
1. Analyze what the user wants to build
2. Determine if this Tekton component would help
3. Suggest how to adapt it for their needs
4. Identify any missing pieces they'll need
5. Guide the packaging and deployment

The user is building: [User's purpose will be inserted here]

How can we best extract and adapt {component_id} for their needs?
"""


# Export for use in Construct
def get_tekton_suggestions(purpose: str) -> Dict[str, Any]:
    """
    Get Tekton component suggestions for a purpose.
    
    Args:
        purpose: User's stated purpose
        
    Returns:
        Suggestions with extraction info
    """
    extractor = TektonExtractor()
    
    # Get suggested components
    suggested_ids = extractor.suggest_for_purpose(purpose)
    
    # Get full info for each
    suggestions = []
    for comp_id in suggested_ids:
        component = extractor.extract_component(comp_id)
        if component:
            suggestions.append({
                'id': comp_id,
                'solution': component,
                'reason': f"Tekton's {comp_id} provides {', '.join(component['content']['capabilities'])}"
            })
    
    return {
        'tekton_components': suggestions,
        'extraction_available': len(suggestions) > 0,
        'message': f"Found {len(suggestions)} relevant Tekton components"
    }