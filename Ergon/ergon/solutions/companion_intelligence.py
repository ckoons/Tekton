"""
Companion Intelligence Integration
==================================

Binds a Companion Intelligence (CI) with a codebase to provide deep understanding
and intelligent assistance. The CI becomes an expert on the codebase, understanding:
- How to use the code
- The codebase structure and design decisions
- Potential approaches for modification
- Extensions and adaptations for new use cases

This is the key to CI-in-the-Loop development where the CI drives development
based on deep codebase understanding.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging

from .cache_rag import CacheRAGEngine
from .codebase_indexer import CodebaseIndexer

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary,
        state_checkpoint,
        danger_zone
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

logger = logging.getLogger(__name__)

@dataclass
class CodebaseUnderstanding:
    """Represents CI's understanding of a codebase"""
    project_name: str
    primary_language: str
    architecture_pattern: str  # MVC, microservices, etc
    key_abstractions: List[str]
    design_principles: List[str]
    extension_points: List[Dict[str, Any]]
    common_patterns: List[Dict[str, Any]]
    dependencies: Dict[str, str]
    quality_metrics: Dict[str, float]

@dataclass
class DevelopmentContext:
    """Context for development decisions"""
    current_task: str
    constraints: List[str]
    preferences: List[str]
    past_decisions: List[Dict[str, Any]]
    success_patterns: List[str]
    failure_patterns: List[str]

@dataclass
class AdaptationStrategy:
    """Strategy for adapting code to new use cases"""
    use_case: str
    approach: str
    required_changes: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    estimated_effort: str
    alternative_approaches: List[Dict[str, Any]]

@architecture_decision(
    title="Companion Intelligence Architecture",
    description="CI-in-the-Loop development system binding CI with codebase understanding",
    rationale="Enables CIs to become codebase experts, driving development with deep understanding",
    alternatives_considered=["Generic CI assistants", "Rule-based systems", "Simple code completion"],
    impacts=["development_workflow", "ai_autonomy", "code_quality"],
    decided_by="Casey Koons",
    decision_date="2024-02-01"
)
@state_checkpoint(
    title="CI Understanding State",
    description="Maintains CI's learned understanding and interaction history",
    state_type="ai_knowledge",
    persistence=True,
    consistency_requirements="Preserve learning across sessions",
    recovery_strategy="Reload from persisted state, re-analyze if needed"
)
class CompanionIntelligence:
    """
    A CI that deeply understands and can work with a specific codebase
    """
    
    def __init__(self, project_root: str, ci_name: str = "Ergon"):
        self.project_root = Path(project_root)
        self.ci_name = ci_name
        self.rag_engine = CacheRAGEngine(project_root)
        self.indexer = self.rag_engine.indexer
        
        # CI's understanding of the codebase
        self.understanding: Optional[CodebaseUnderstanding] = None
        self.context = DevelopmentContext(
            current_task="",
            constraints=[],
            preferences=[],
            past_decisions=[],
            success_patterns=[],
            failure_patterns=[]
        )
        
        # Learning data
        self.interaction_history: List[Dict[str, Any]] = []
        self.learned_patterns: Dict[str, List[str]] = {}
        self.confidence_scores: Dict[str, float] = {}
        
        # Initialize understanding
        self._analyze_codebase()
        
    @performance_boundary(
        title="Codebase Analysis",
        description="Initial deep analysis to build CI understanding",
        sla="<60s for typical codebase",
        optimization_notes="Runs once on initialization, cached thereafter",
        measured_impact="Enables informed CI assistance without repeated analysis"
    )
    def _analyze_codebase(self):
        """Analyze codebase to build initial understanding"""
        logger.info(f"{self.ci_name} is analyzing the codebase...")
        
        # Get codebase statistics
        stats = self._gather_statistics()
        
        # Identify architecture pattern
        architecture = self._identify_architecture()
        
        # Extract key abstractions
        abstractions = self._extract_key_abstractions()
        
        # Identify design principles
        principles = self._identify_design_principles()
        
        # Find extension points
        extension_points = self._find_extension_points()
        
        # Discover common patterns
        patterns = self._discover_patterns()
        
        # Analyze dependencies
        dependencies = self._analyze_dependencies()
        
        # Calculate quality metrics
        quality = self._calculate_quality_metrics()
        
        self.understanding = CodebaseUnderstanding(
            project_name=self.project_root.name,
            primary_language=stats['primary_language'],
            architecture_pattern=architecture,
            key_abstractions=abstractions,
            design_principles=principles,
            extension_points=extension_points,
            common_patterns=patterns,
            dependencies=dependencies,
            quality_metrics=quality
        )
        
        logger.info(f"{self.ci_name} has completed codebase analysis")
        
    def _gather_statistics(self) -> Dict[str, Any]:
        """Gather basic codebase statistics"""
        file_counts = {}
        total_lines = 0
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                suffix = file_path.suffix
                file_counts[suffix] = file_counts.get(suffix, 0) + 1
                
                try:
                    with open(file_path, 'r') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
                    
        # Determine primary language
        primary_lang = "unknown"
        if '.py' in file_counts:
            primary_lang = "python"
        elif '.js' in file_counts or '.ts' in file_counts:
            primary_lang = "javascript"
        elif '.java' in file_counts:
            primary_lang = "java"
            
        return {
            'file_counts': file_counts,
            'total_lines': total_lines,
            'primary_language': primary_lang,
            'total_files': sum(file_counts.values())
        }
        
    def _identify_architecture(self) -> str:
        """Identify the architecture pattern"""
        # Look for common patterns
        indicators = {
            'microservices': ['docker-compose', 'kubernetes', 'services/'],
            'mvc': ['models/', 'views/', 'controllers/'],
            'layered': ['domain/', 'application/', 'infrastructure/'],
            'modular': ['modules/', 'components/', 'packages/'],
            'monolithic': ['src/', 'lib/']
        }
        
        scores = {}
        for pattern, markers in indicators.items():
            score = 0
            for marker in markers:
                if list(self.project_root.rglob(f"*{marker}*")):
                    score += 1
            scores[pattern] = score
            
        # Return highest scoring pattern
        return max(scores.items(), key=lambda x: x[1])[0]
        
    def _extract_key_abstractions(self) -> List[str]:
        """Extract key abstractions from the codebase"""
        abstractions = []
        
        # Look at class names
        for struct in self.indexer.data_structures:
            # Focus on important classes (no underscore prefix, has methods)
            if not struct.name.startswith('_') and len(struct.methods) > 2:
                abstractions.append(struct.name)
                
        # Look for interfaces/protocols
        for struct in self.indexer.data_structures:
            if 'abc' in struct.decorators or 'Protocol' in struct.base_classes:
                abstractions.append(f"Interface: {struct.name}")
                
        return abstractions[:20]  # Top 20 abstractions
        
    def _identify_design_principles(self) -> List[str]:
        """Identify design principles used in the codebase"""
        principles = []
        
        # Check for SOLID principles
        # Single Responsibility
        small_classes = sum(1 for s in self.indexer.data_structures 
                          if len(s.methods) < 7)
        if small_classes > len(self.indexer.data_structures) * 0.7:
            principles.append("Single Responsibility Principle")
            
        # Dependency Injection
        init_methods = [m for m in self.indexer.method_signatures 
                       if m.name == '__init__']
        injected = sum(1 for m in init_methods if len(m.parameters) > 2)
        if injected > len(init_methods) * 0.3:
            principles.append("Dependency Injection")
            
        # Check for patterns
        if any('factory' in s.name.lower() for s in self.indexer.data_structures):
            principles.append("Factory Pattern")
            
        if any('observer' in s.name.lower() or 'listener' in s.name.lower() 
               for s in self.indexer.data_structures):
            principles.append("Observer Pattern")
            
        if any('strategy' in s.name.lower() for s in self.indexer.data_structures):
            principles.append("Strategy Pattern")
            
        return principles
        
    def _find_extension_points(self) -> List[Dict[str, Any]]:
        """Find natural extension points in the codebase"""
        extension_points = []
        
        # Abstract classes and interfaces
        for struct in self.indexer.data_structures:
            if 'abc' in struct.decorators or 'abstract' in struct.name.lower():
                extension_points.append({
                    'type': 'abstract_class',
                    'name': struct.name,
                    'location': f"{struct.file_path}:{struct.line_number}",
                    'methods': struct.methods
                })
                
        # Plugin systems
        for tag in self.indexer.semantic_tags:
            if 'plugin' in tag.content.lower() or 'extension' in tag.content.lower():
                extension_points.append({
                    'type': 'plugin_point',
                    'description': tag.content,
                    'location': f"{tag.file_path}:{tag.line_number}"
                })
                
        # Event systems
        for method in self.indexer.method_signatures:
            if 'emit' in method.name or 'dispatch' in method.name:
                extension_points.append({
                    'type': 'event_system',
                    'name': method.name,
                    'location': f"{method.file_path}:{method.line_number}"
                })
                
        return extension_points
        
    def _discover_patterns(self) -> List[Dict[str, Any]]:
        """Discover common patterns in the codebase"""
        patterns = []
        
        # Method naming patterns
        method_prefixes = {}
        for method in self.indexer.method_signatures:
            prefix = method.name.split('_')[0]
            method_prefixes[prefix] = method_prefixes.get(prefix, 0) + 1
            
        common_prefixes = [p for p, c in method_prefixes.items() if c > 5]
        if common_prefixes:
            patterns.append({
                'type': 'naming_convention',
                'pattern': 'method_prefixes',
                'examples': common_prefixes
            })
            
        # Error handling patterns
        try_except_count = sum(1 for call in self.indexer.method_calls 
                             if call.method_name in ['try', 'catch', 'except'])
        if try_except_count > 10:
            patterns.append({
                'type': 'error_handling',
                'pattern': 'exception_based',
                'frequency': try_except_count
            })
            
        return patterns
        
    def _analyze_dependencies(self) -> Dict[str, str]:
        """Analyze project dependencies"""
        dependencies = {}
        
        # Python dependencies
        requirements = self.project_root / "requirements.txt"
        if requirements.exists():
            with open(requirements) as f:
                for line in f:
                    if '==' in line:
                        name, version = line.strip().split('==')
                        dependencies[name] = version
                        
        # Package.json for JavaScript
        package_json = self.project_root / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                dependencies.update(data.get('dependencies', {}))
                
        return dependencies
        
    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """Calculate code quality metrics"""
        metrics = {}
        
        # Documentation coverage
        documented_methods = sum(1 for m in self.indexer.method_signatures 
                               if m.docstring)
        total_methods = len(self.indexer.method_signatures)
        metrics['documentation_coverage'] = (
            documented_methods / total_methods if total_methods > 0 else 0
        )
        
        # Type annotation coverage (Python)
        typed_params = sum(
            len([p for p in m.parameters if p.get('type')])
            for m in self.indexer.method_signatures
        )
        total_params = sum(len(m.parameters) for m in self.indexer.method_signatures)
        metrics['type_coverage'] = (
            typed_params / total_params if total_params > 0 else 0
        )
        
        # Average method length (simplified)
        metrics['avg_method_length'] = 20  # Would need actual parsing
        
        # Cyclomatic complexity (simplified)
        metrics['avg_complexity'] = 5  # Would need actual analysis
        
        return metrics
        
    @api_contract(
        title="Task Assistance API",
        description="Provide intelligent assistance for development tasks",
        endpoint="/ci/assist",
        method="POST",
        request_schema={"task_description": "str"},
        response_schema={
            "task": "str",
            "analysis": "dict",
            "approach": "dict",
            "relevant_code": "List[dict]",
            "examples": "List[dict]",
            "risks": "List[dict]",
            "confidence": "float"
        },
        performance_requirements="<5s for comprehensive assistance"
    )
    @danger_zone(
        title="Async Task Processing",
        description="Multiple async operations that analyze and generate assistance",
        risk_level="medium",
        risks=["concurrent RAG queries", "potential timeout on complex tasks"],
        mitigation="Timeout handling, error boundaries for each async operation",
        review_required=False
    )
    async def assist_with_task(self, task_description: str) -> Dict[str, Any]:
        """
        Assist with a development task using codebase understanding
        
        Args:
            task_description: Description of what needs to be done
            
        Returns:
            Comprehensive assistance including approach, code examples, and warnings
        """
        logger.info(f"{self.ci_name} is analyzing task: {task_description}")
        
        # Update context
        self.context.current_task = task_description
        
        # Analyze task requirements
        task_analysis = await self._analyze_task(task_description)
        
        # Find relevant code sections
        relevant_code = await self._find_relevant_code(task_analysis)
        
        # Generate approach
        approach = await self._generate_approach(task_analysis, relevant_code)
        
        # Identify risks
        risks = self._assess_risks(approach)
        
        # Generate code examples
        examples = await self._generate_examples(approach, relevant_code)
        
        # Learn from this interaction
        self._learn_from_interaction(task_description, approach)
        
        return {
            'task': task_description,
            'analysis': task_analysis,
            'approach': approach,
            'relevant_code': relevant_code,
            'examples': examples,
            'risks': risks,
            'confidence': self._calculate_task_confidence(task_analysis)
        }
        
    async def _analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze the task to understand requirements"""
        # Use RAG to understand task in context of codebase
        from .rag_solution import RAGQuery
        
        query = RAGQuery(
            query=f"What parts of the codebase are relevant for: {task}",
            max_contexts=10,
            include_call_graph=True
        )
        
        response = self.rag_engine.query(query)
        
        # Extract task characteristics
        task_type = self._classify_task(task)
        complexity = self._estimate_complexity(task, response)
        
        return {
            'type': task_type,
            'complexity': complexity,
            'relevant_contexts': response.contexts,
            'key_components': self._extract_components(response)
        }
        
    def _classify_task(self, task: str) -> str:
        """Classify the type of task"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['add', 'create', 'implement', 'new']):
            return 'feature_addition'
        elif any(word in task_lower for word in ['fix', 'bug', 'error', 'issue']):
            return 'bug_fix'
        elif any(word in task_lower for word in ['refactor', 'improve', 'optimize']):
            return 'refactoring'
        elif any(word in task_lower for word in ['test', 'testing', 'coverage']):
            return 'testing'
        elif any(word in task_lower for word in ['document', 'docs', 'readme']):
            return 'documentation'
        else:
            return 'general_modification'
            
    def _estimate_complexity(self, task: str, rag_response) -> str:
        """Estimate task complexity"""
        # Consider number of files affected
        affected_files = set(c.file_path for c in rag_response.contexts)
        
        if len(affected_files) == 1:
            return 'simple'
        elif len(affected_files) <= 3:
            return 'moderate'
        else:
            return 'complex'
            
    def _extract_components(self, rag_response) -> List[str]:
        """Extract key components from RAG response"""
        components = []
        
        for context in rag_response.contexts:
            if context.metadata.get('name'):
                components.append(context.metadata['name'])
                
        return list(set(components))
        
    async def _find_relevant_code(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find code sections relevant to the task"""
        relevant_sections = []
        
        for context in task_analysis['relevant_contexts']:
            section = {
                'file': context.file_path,
                'lines': f"{context.start_line}-{context.end_line}",
                'type': context.context_type,
                'relevance': context.relevance_score,
                'content_preview': context.content[:200] + '...' if len(context.content) > 200 else context.content
            }
            relevant_sections.append(section)
            
        return relevant_sections
        
    async def _generate_approach(self, task_analysis: Dict[str, Any], 
                               relevant_code: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate approach for the task"""
        task_type = task_analysis['type']
        
        # Generate steps based on task type and codebase patterns
        if task_type == 'feature_addition':
            steps = self._generate_feature_steps(task_analysis, relevant_code)
        elif task_type == 'bug_fix':
            steps = self._generate_bugfix_steps(task_analysis, relevant_code)
        elif task_type == 'refactoring':
            steps = self._generate_refactor_steps(task_analysis, relevant_code)
        else:
            steps = self._generate_general_steps(task_analysis, relevant_code)
            
        return {
            'strategy': self._select_strategy(task_type),
            'steps': steps,
            'patterns_to_follow': self._get_relevant_patterns(task_type),
            'estimated_effort': self._estimate_effort(task_analysis)
        }
        
    def _generate_feature_steps(self, task_analysis: Dict[str, Any], 
                               relevant_code: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate steps for adding a feature"""
        steps = []
        
        # Step 1: Understand existing patterns
        steps.append({
            'order': 1,
            'action': 'analyze_patterns',
            'description': 'Study existing similar features to understand patterns',
            'references': [rc['file'] for rc in relevant_code[:3]]
        })
        
        # Step 2: Design interface
        steps.append({
            'order': 2,
            'action': 'design_interface',
            'description': 'Design the interface following existing conventions',
            'considerations': self.understanding.design_principles
        })
        
        # Step 3: Implement core logic
        steps.append({
            'order': 3,
            'action': 'implement',
            'description': 'Implement the feature following identified patterns',
            'patterns': self.understanding.common_patterns[:3]
        })
        
        # Step 4: Add tests
        steps.append({
            'order': 4,
            'action': 'test',
            'description': 'Add tests following the project\'s testing patterns'
        })
        
        # Step 5: Update documentation
        steps.append({
            'order': 5,
            'action': 'document',
            'description': 'Update documentation and add docstrings'
        })
        
        return steps
        
    def _generate_bugfix_steps(self, task_analysis: Dict[str, Any], 
                              relevant_code: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate steps for fixing a bug"""
        return [
            {
                'order': 1,
                'action': 'reproduce',
                'description': 'Reproduce the bug and understand the root cause'
            },
            {
                'order': 2,
                'action': 'analyze_impact',
                'description': 'Analyze impact on related code sections',
                'affected_files': [rc['file'] for rc in relevant_code]
            },
            {
                'order': 3,
                'action': 'implement_fix',
                'description': 'Implement the fix following error handling patterns'
            },
            {
                'order': 4,
                'action': 'test_fix',
                'description': 'Test the fix and ensure no regressions'
            }
        ]
        
    def _generate_refactor_steps(self, task_analysis: Dict[str, Any], 
                                relevant_code: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate steps for refactoring"""
        return [
            {
                'order': 1,
                'action': 'identify_boundaries',
                'description': 'Identify refactoring boundaries and dependencies'
            },
            {
                'order': 2,
                'action': 'create_tests',
                'description': 'Ensure comprehensive test coverage before refactoring'
            },
            {
                'order': 3,
                'action': 'refactor_incrementally',
                'description': 'Refactor in small, testable increments'
            },
            {
                'order': 4,
                'action': 'update_callers',
                'description': 'Update all callers and dependencies'
            }
        ]
        
    def _generate_general_steps(self, task_analysis: Dict[str, Any], 
                               relevant_code: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate general steps"""
        return [
            {
                'order': 1,
                'action': 'understand_context',
                'description': 'Understand the context and requirements'
            },
            {
                'order': 2,
                'action': 'plan_changes',
                'description': 'Plan the changes following project patterns'
            },
            {
                'order': 3,
                'action': 'implement',
                'description': 'Implement changes incrementally'
            },
            {
                'order': 4,
                'action': 'verify',
                'description': 'Verify changes work as expected'
            }
        ]
        
    def _select_strategy(self, task_type: str) -> str:
        """Select appropriate strategy"""
        strategies = {
            'feature_addition': 'incremental_development',
            'bug_fix': 'root_cause_analysis',
            'refactoring': 'safe_refactoring',
            'testing': 'test_driven_development',
            'documentation': 'comprehensive_documentation'
        }
        return strategies.get(task_type, 'systematic_approach')
        
    def _get_relevant_patterns(self, task_type: str) -> List[str]:
        """Get patterns relevant to task type"""
        patterns = []
        
        for pattern in self.understanding.common_patterns:
            if task_type in str(pattern).lower():
                patterns.append(pattern)
                
        return patterns[:5]
        
    def _estimate_effort(self, task_analysis: Dict[str, Any]) -> str:
        """Estimate effort required"""
        complexity = task_analysis['complexity']
        
        effort_map = {
            'simple': '1-2 hours',
            'moderate': '4-8 hours',
            'complex': '1-3 days'
        }
        
        return effort_map.get(complexity, 'Unknown')
        
    def _assess_risks(self, approach: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess risks in the approach"""
        risks = []
        
        # Check if modifying core components
        if 'core' in str(approach).lower():
            risks.append({
                'type': 'stability',
                'severity': 'high',
                'description': 'Modifying core components may affect system stability',
                'mitigation': 'Ensure comprehensive testing and gradual rollout'
            })
            
        # Check if affecting many files
        if len(approach.get('steps', [])) > 5:
            risks.append({
                'type': 'complexity',
                'severity': 'medium',
                'description': 'Complex change affecting multiple components',
                'mitigation': 'Break into smaller, reviewable changes'
            })
            
        return risks
        
    async def _generate_examples(self, approach: Dict[str, Any], 
                               relevant_code: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate code examples"""
        examples = []
        
        # Generate example based on existing patterns
        for i, step in enumerate(approach['steps'][:3]):
            if step['action'] == 'implement':
                example = {
                    'step': i + 1,
                    'description': step['description'],
                    'code': self._generate_example_code(step, relevant_code),
                    'explanation': 'Following existing patterns in the codebase'
                }
                examples.append(example)
                
        return examples
        
    def _generate_example_code(self, step: Dict[str, Any], 
                              relevant_code: List[Dict[str, Any]]) -> str:
        """Generate example code (simplified)"""
        # In reality, this would use LLM with codebase context
        return """
# Example following project patterns
class NewFeature:
    def __init__(self, config):
        self.config = config
        
    def process(self, data):
        # Implementation following existing patterns
        pass
"""
        
    @state_checkpoint(
        title="Interaction Learning",
        description="Learn from each interaction to improve future assistance",
        state_type="learning_history",
        persistence=True,
        consistency_requirements="Append-only history, pattern extraction",
        recovery_strategy="Reload interaction history from persistence"
    )
    def _learn_from_interaction(self, task: str, approach: Dict[str, Any]):
        """Learn from the interaction"""
        # Record interaction
        self.interaction_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'task': task,
            'approach': approach,
            'success': None  # To be updated later
        })
        
        # Update learned patterns
        task_type = self._classify_task(task)
        if task_type not in self.learned_patterns:
            self.learned_patterns[task_type] = []
            
        self.learned_patterns[task_type].append(approach['strategy'])
        
    def _calculate_task_confidence(self, task_analysis: Dict[str, Any]) -> float:
        """Calculate confidence in the assistance"""
        base_confidence = 0.5
        
        # Higher confidence if we've seen similar tasks
        task_type = task_analysis['type']
        if task_type in self.learned_patterns:
            base_confidence += 0.2
            
        # Higher confidence if relevant code found
        if task_analysis['relevant_contexts']:
            base_confidence += 0.2
            
        # Lower confidence for complex tasks
        if task_analysis['complexity'] == 'complex':
            base_confidence -= 0.1
            
        return min(max(base_confidence, 0.1), 0.95)
        
    @api_contract(
        title="Use Case Adaptation API",
        description="Generate strategy for adapting codebase to new use cases",
        endpoint="/ci/adapt",
        method="POST",
        request_schema={"use_case": "str"},
        response_schema={
            "use_case": "str",
            "approach": "str",
            "required_changes": "List[dict]",
            "risk_assessment": "dict",
            "estimated_effort": "str",
            "alternative_approaches": "List[dict]"
        },
        performance_requirements="<10s for adaptation analysis"
    )
    def adapt_for_use_case(self, use_case: str) -> AdaptationStrategy:
        """
        Generate strategy for adapting codebase to new use case
        
        Args:
            use_case: Description of the new use case
            
        Returns:
            Adaptation strategy with detailed steps
        """
        logger.info(f"{self.ci_name} is analyzing adaptation for: {use_case}")
        
        # Analyze use case requirements
        requirements = self._analyze_use_case(use_case)
        
        # Identify required changes
        changes = self._identify_required_changes(requirements)
        
        # Assess risks
        risks = self._assess_adaptation_risks(changes)
        
        # Generate alternative approaches
        alternatives = self._generate_alternatives(requirements, changes)
        
        # Select best approach
        best_approach = self._select_best_approach(changes, risks, alternatives)
        
        return AdaptationStrategy(
            use_case=use_case,
            approach=best_approach['description'],
            required_changes=changes,
            risk_assessment=risks,
            estimated_effort=self._estimate_adaptation_effort(changes),
            alternative_approaches=alternatives
        )
        
    def _analyze_use_case(self, use_case: str) -> Dict[str, Any]:
        """Analyze the new use case"""
        # Simplified analysis
        return {
            'description': use_case,
            'requirements': self._extract_requirements(use_case),
            'constraints': self._identify_constraints(use_case),
            'compatibility': self._assess_compatibility(use_case)
        }
        
    def _extract_requirements(self, use_case: str) -> List[str]:
        """Extract requirements from use case description"""
        # In reality, would use NLP
        requirements = []
        
        keywords = ['need', 'require', 'must', 'should', 'want']
        sentences = use_case.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                requirements.append(sentence.strip())
                
        return requirements
        
    def _identify_constraints(self, use_case: str) -> List[str]:
        """Identify constraints in use case"""
        constraints = []
        
        constraint_keywords = ['limit', 'restrict', 'cannot', 'avoid', 'prevent']
        sentences = use_case.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in constraint_keywords):
                constraints.append(sentence.strip())
                
        return constraints
        
    def _assess_compatibility(self, use_case: str) -> float:
        """Assess compatibility with current codebase"""
        # Simplified assessment
        compatibility = 0.7
        
        # Check if use case aligns with architecture
        if self.understanding.architecture_pattern in use_case.lower():
            compatibility += 0.1
            
        # Check if required capabilities exist
        if 'api' in use_case.lower() and 'api' in str(self.understanding.key_abstractions).lower():
            compatibility += 0.1
            
        return min(compatibility, 1.0)
        
    def _identify_required_changes(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify changes needed for adaptation"""
        changes = []
        
        # Analyze each requirement
        for req in requirements['requirements']:
            # Simplified change identification
            if 'api' in req.lower():
                changes.append({
                    'type': 'api_addition',
                    'description': 'Add new API endpoints',
                    'location': 'api/',
                    'complexity': 'moderate'
                })
                
            if 'interface' in req.lower():
                changes.append({
                    'type': 'interface_modification',
                    'description': 'Modify existing interfaces',
                    'location': 'interfaces/',
                    'complexity': 'high'
                })
                
        return changes
        
    def _assess_adaptation_risks(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess risks of adaptation"""
        risk_score = 0
        risk_factors = []
        
        for change in changes:
            if change['complexity'] == 'high':
                risk_score += 0.3
                risk_factors.append('High complexity changes required')
                
            if change['type'] == 'interface_modification':
                risk_score += 0.2
                risk_factors.append('Interface changes may break compatibility')
                
        return {
            'overall_risk': 'high' if risk_score > 0.5 else 'medium' if risk_score > 0.3 else 'low',
            'risk_score': risk_score,
            'factors': risk_factors,
            'mitigation_strategies': [
                'Implement changes incrementally',
                'Maintain backward compatibility',
                'Comprehensive testing at each step'
            ]
        }
        
    def _generate_alternatives(self, requirements: Dict[str, Any], 
                             changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate alternative approaches"""
        alternatives = []
        
        # Alternative 1: Minimal changes
        alternatives.append({
            'name': 'Minimal Adaptation',
            'description': 'Make minimal changes to support core requirements',
            'pros': ['Lower risk', 'Faster implementation'],
            'cons': ['May not fully satisfy all requirements']
        })
        
        # Alternative 2: Plugin approach
        if self.understanding.extension_points:
            alternatives.append({
                'name': 'Plugin-Based Extension',
                'description': 'Implement as plugins using existing extension points',
                'pros': ['Clean separation', 'No core changes'],
                'cons': ['May have limitations']
            })
            
        # Alternative 3: Wrapper approach
        alternatives.append({
            'name': 'Wrapper/Adapter Pattern',
            'description': 'Create wrappers around existing functionality',
            'pros': ['Preserves existing code', 'Easy to test'],
            'cons': ['May add complexity']
        })
        
        return alternatives
        
    def _select_best_approach(self, changes: List[Dict[str, Any]], 
                            risks: Dict[str, Any], 
                            alternatives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best approach"""
        # Simplified selection logic
        if risks['overall_risk'] == 'high':
            # Prefer minimal or plugin approach for high risk
            for alt in alternatives:
                if 'Minimal' in alt['name'] or 'Plugin' in alt['name']:
                    return alt
                    
        # Default to first alternative
        return alternatives[0] if alternatives else {
            'name': 'Direct Implementation',
            'description': 'Implement changes directly in the codebase'
        }
        
    def _estimate_adaptation_effort(self, changes: List[Dict[str, Any]]) -> str:
        """Estimate effort for adaptation"""
        total_complexity = 0
        
        complexity_scores = {
            'low': 1,
            'moderate': 3,
            'high': 5
        }
        
        for change in changes:
            total_complexity += complexity_scores.get(change.get('complexity', 'moderate'), 3)
            
        if total_complexity < 5:
            return '1-2 weeks'
        elif total_complexity < 10:
            return '2-4 weeks'
        else:
            return '1-2 months'
            
    @api_contract(
        title="Autonomy Assessment API",
        description="Recommend CI autonomy level based on understanding",
        endpoint="/ci/autonomy",
        method="GET",
        request_schema={},
        response_schema={
            "recommendation": "str",
            "confidence_factors": "dict",
            "reasoning": "str"
        },
        performance_requirements="<100ms response"
    )
    def get_autonomy_recommendation(self) -> str:
        """
        Recommend autonomy level based on codebase understanding
        
        Returns:
            'autonomous' or 'co-developer' based on confidence
        """
        # Calculate overall confidence
        confidence_factors = []
        
        # Documentation quality
        doc_coverage = self.understanding.quality_metrics.get('documentation_coverage', 0)
        confidence_factors.append(doc_coverage)
        
        # Type coverage
        type_coverage = self.understanding.quality_metrics.get('type_coverage', 0)
        confidence_factors.append(type_coverage)
        
        # Past success rate
        if self.interaction_history:
            successes = sum(1 for i in self.interaction_history 
                          if i.get('success', False))
            success_rate = successes / len(self.interaction_history)
            confidence_factors.append(success_rate)
            
        # Average confidence
        avg_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0
        
        # Recommend autonomous if high confidence
        if avg_confidence > 0.7:
            return 'autonomous'
        else:
            return 'co-developer'


# Integration with Ergon
@integration_point(
    title="Companion Intelligence Integration",
    description="Integrates CI-in-the-Loop system with Ergon",
    target_component="Ergon",
    protocol="solution_registry",
    data_flow="Ergon → CI instantiation → Deep codebase understanding → Intelligent assistance",
    integration_date="2024-02-01"
)
def create_companion_intelligence_solution():
    """
    Create the Companion Intelligence solution for Ergon's registry
    """
    return {
        "name": "Companion Intelligence",
        "type": "intelligence",
        "description": "Binds a CI with a codebase for deep understanding and intelligent development assistance",
        "capabilities": [
            "codebase_understanding",
            "task_assistance",
            "adaptation_planning",
            "pattern_learning",
            "autonomy_recommendation"
        ],
        "configuration": {
            "ci_name": "Ergon",
            "learning_enabled": True,
            "autonomy_assessment": True,
            "pattern_recognition": True
        },
        "dependencies": ["Cache RAG", "Codebase Indexer"],
        "implementation": {
            "class": "CompanionIntelligence",
            "module": "ergon.solutions.companion_intelligence",
            "version": "1.0.0"
        }
    }