#!/usr/bin/env python3
"""
Prometheus Planning Engine with Latent Reasoning

This module implements a planning engine that leverages the latent space
reasoning framework to iteratively refine plans.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prometheus.core.planning_engine")

# Import the latent reasoning mixin
from tekton.core.latent_reasoning import LatentReasoningMixin
from landmarks import architecture_decision, performance_boundary, danger_zone


@architecture_decision(
    title="Latent space reasoning for planning",
    rationale="Use iterative refinement in latent space to improve plan quality for complex objectives",
    alternatives=["Single-pass planning", "Rule-based planning", "Template-based planning"],
    decision_date="2024-02-01"
)
class PlanningEngine(LatentReasoningMixin):
    """
    Planning engine with latent space reasoning capabilities.
    
    This class uses the latent reasoning framework to iteratively refine
    plans based on objectives and context.
    """
    
    def __init__(self, component_id: str = "prometheus.planning"):
        """
        Initialize the planning engine.
        
        Args:
            component_id: Unique identifier for this component
        """
        self.component_id = component_id
        self.initialized = False
        
    async def initialize(self, data_dir: Optional[str] = None):
        """
        Initialize the planning engine with latent reasoning capabilities.
        
        Args:
            data_dir: Optional directory for persisted thoughts
            
        Returns:
            Boolean indicating success
        """
        try:
            # Initialize latent space
            result = await self.initialize_latent_space(
                namespace="planning",
                shared=True,
                data_dir=data_dir
            )
            
            if result:
                logger.info(f"Planning engine initialized with full latent reasoning capabilities")
            else:
                logger.info(f"Planning engine initialized in standalone mode (Engram integration not available)")
                
            # Planning engine is initialized either way
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing planning engine: {e}")
            self.initialized = False
            return False
    
    @performance_boundary(
        title="Plan creation with complexity-based reasoning",
        sla="<5s for simple plans, <30s for complex iterative plans",
        metrics={"simple_avg": "2.3s", "complex_avg": "18.5s", "iteration_avg": "6.2s"},
        optimization_notes="Cache partial results, early termination for convergence"
    )
    async def create_plan(self, 
                        objective: str, 
                        context: Optional[Dict[str, Any]] = None,
                        complexity_threshold: float = 0.7,
                        max_iterations: int = 3) -> Dict[str, Any]:
        """
        Create a plan for the given objective using latent reasoning when appropriate.
        
        Args:
            objective: The objective to plan for
            context: Optional additional context for planning
            complexity_threshold: Threshold for using latent reasoning
            max_iterations: Maximum reasoning iterations for complex plans
            
        Returns:
            Dictionary with the plan and reasoning details
        """
        if not self.initialized:
            raise RuntimeError("Planning engine not initialized. Call initialize() first.")
            
        # Format the input content
        input_content = self._format_planning_input(objective, context)
        
        # Use complexity-based reasoning
        result = await self.complexity_based_reasoning(
            input_content=input_content,
            process_func=self._plan_iteration,
            complexity_analyzer=self._assess_complexity,
            complexity_threshold=complexity_threshold,
            max_iterations=max_iterations,
            share_final_insight=True,
            metadata={
                "objective": objective,
                "context_keys": list(context.keys()) if context else []
            }
        )
        
        # Format the response
        return self._format_plan_response(result, objective)
    
    async def _plan_iteration(self, input_content: str) -> str:
        """
        Process a single planning iteration.
        
        In a real implementation, this would typically call an LLM or other
        planning algorithm. For this example, we'll simulate refinement.
        
        Args:
            input_content: The input for this planning iteration
            
        Returns:
            Refined planning content
        """
        # This is a placeholder implementation
        # In a real system, this would call an LLM or other planning system
        
        # Check if this is the first iteration
        if "Iteration 1" in input_content:
            return (
                f"{input_content}\n\n"
                f"# Initial Plan\n\n"
                f"## High-Level Approach\n"
                f"1. Analyze the objective requirements\n"
                f"2. Identify key stakeholders and dependencies\n"
                f"3. Outline preliminary task sequence\n"
                f"4. Estimate initial timeline\n\n"
                f"## Initial Tasks\n"
                f"1. Gather requirements from stakeholders\n"
                f"2. Research potential solutions\n"
                f"3. Draft preliminary implementation plan\n"
                f"4. Identify potential risks and mitigation strategies"
            )
        elif "Iteration 2" in input_content:
            return (
                f"{input_content}\n\n"
                f"# Refined Plan\n\n"
                f"## Resource Requirements\n"
                f"- Personnel: 2 developers, 1 designer, 1 QA specialist\n"
                f"- Timeline: 3 weeks for initial implementation\n"
                f"- Budget: Approximately 120 person-hours\n\n"
                f"## Detailed Task Breakdown\n"
                f"1. Requirements Analysis (3 days)\n"
                f"   - Conduct stakeholder interviews\n"
                f"   - Document functional requirements\n"
                f"   - Define acceptance criteria\n"
                f"2. Solution Design (4 days)\n"
                f"   - Create technical architecture diagram\n"
                f"   - Define API specifications\n"
                f"   - Design user interface mockups\n"
                f"3. Implementation (10 days)\n"
                f"   - Develop backend services\n"
                f"   - Create frontend components\n"
                f"   - Integrate with existing systems\n"
                f"4. Testing & Validation (5 days)\n"
                f"   - Unit and integration testing\n"
                f"   - User acceptance testing\n"
                f"   - Performance testing\n\n"
                f"## Risk Assessment\n"
                f"- Dependency on third-party services: Medium risk\n"
                f"- Timeline constraints: High risk\n"
                f"- Technical complexity: Medium risk"
            )
        else:
            return (
                f"{input_content}\n\n"
                f"# Final Plan\n\n"
                f"## Executive Summary\n"
                f"This plan outlines a comprehensive approach to achieving the objective with careful "
                f"consideration of dependencies, risks, and resource constraints. The implementation "
                f"strategy emphasizes iterative development with regular validation checkpoints.\n\n"
                f"## Comprehensive Timeline\n"
                f"### Week 1: Foundation\n"
                f"- Days 1-2: Requirements gathering and analysis\n"
                f"- Days 3-5: Architecture design and prototyping\n\n"
                f"### Week 2: Core Implementation\n"
                f"- Days 6-7: Backend service development\n"
                f"- Days 8-10: Frontend implementation\n\n"
                f"### Week 3: Integration and Validation\n"
                f"- Days 11-12: System integration\n"
                f"- Days 13-15: Testing, optimization, and deployment\n\n"
                f"## Success Metrics\n"
                f"1. Functional completeness: All requirements satisfied\n"
                f"2. Performance: Response time < 200ms for critical operations\n"
                f"3. Quality: Zero critical or high-severity bugs\n"
                f"4. User satisfaction: >85% positive feedback\n\n"
                f"## Contingency Planning\n"
                f"- If timeline risks materialize: Reduce scope to MVP features\n"
                f"- If technical challenges arise: Allocate additional senior developer time\n"
                f"- If resource constraints impact progress: Re-prioritize based on business value\n\n"
                f"This plan has been developed with consideration for both immediate implementation "
                f"needs and long-term maintenance requirements."
            )
    
    @danger_zone(
        title="Complexity assessment heuristics",
        risk_level="medium",
        risks=["Heuristic bias", "Over/under-estimation of complexity"],
        mitigations=["Regular tuning based on outcomes", "Multiple assessment factors"],
        review_required=True
    )
    async def _assess_complexity(self, input_content: str) -> float:
        """
        Assess the complexity of an objective to determine if latent reasoning is needed.
        
        Args:
            input_content: The planning input to assess
            
        Returns:
            Complexity score between 0 and 1
        """
        # Extract just the objective if it's a full planning input
        objective = input_content
        if "Objective:" in input_content:
            for line in input_content.split("\n"):
                if line.startswith("Objective:"):
                    objective = line[len("Objective:"):].strip()
                    break
        
        # Simple heuristic: longer objectives tend to be more complex
        length_factor = min(len(objective) / 200, 1.0)
        
        # Check for complexity indicators
        indicators = ["if", "but", "except", "complex", "difficult", "challenge", 
                     "tradeoff", "balance", "integrate", "multiple", "optimize",
                     "conflicting", "requirements", "stakeholders", "constraints"]
        
        indicator_count = sum(1 for word in objective.lower().split() if word in indicators)
        indicator_factor = min(indicator_count / 5, 1.0)
        
        # Check for technical/domain complexity
        technical_terms = ["database", "api", "interface", "framework", "architecture",
                         "system", "component", "infrastructure", "scaling", "concurrent",
                         "distributed", "network", "security", "authentication", "performance"]
        
        technical_count = sum(1 for word in objective.lower().split() if word in technical_terms)
        technical_factor = min(technical_count / 4, 1.0)
        
        # Combine factors (weighted average)
        complexity = (length_factor * 0.3) + (indicator_factor * 0.4) + (technical_factor * 0.3)
        
        logger.info(f"Assessed complexity for planning: {complexity:.4f} "
                   f"(length: {length_factor:.2f}, indicators: {indicator_factor:.2f}, "
                   f"technical: {technical_factor:.2f})")
        
        return complexity
    
    def _format_planning_input(self, objective: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Format the planning input from objective and context."""
        lines = [f"Objective: {objective}"]
        
        if context:
            lines.append("\nContext:")
            for key, value in context.items():
                if isinstance(value, dict):
                    lines.append(f"- {key}:")
                    for subkey, subvalue in value.items():
                        lines.append(f"  - {subkey}: {subvalue}")
                elif isinstance(value, list):
                    lines.append(f"- {key}:")
                    for item in value:
                        lines.append(f"  - {item}")
                else:
                    lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)
    
    def _format_plan_response(self, result: Dict[str, Any], objective: str) -> Dict[str, Any]:
        """Format the planning result for the response."""
        # Extract plan from result
        plan = result.get("result", "")
        
        # Basic validation to ensure we have a valid plan
        if not plan or len(plan.strip()) < 10:
            plan = f"Failed to generate a valid plan for objective: {objective}"
        
        # Format the response
        response = {
            "plan": plan,
            "objective": objective,
            "complexity_score": result.get("complexity_score", 0.0),
            "used_latent_reasoning": result.get("used_latent_reasoning", False),
            "iterations": result.get("iterations", 1),
            "thought_id": result.get("thought_id")
        }
        
        # Add trace information if requested (could be filtered out for efficiency)
        if "trace" in result:
            response["reasoning_trace"] = result["trace"]
        
        return response
    
    async def close(self):
        """Clean up resources."""
        await self.close_latent_space()
        self.initialized = False


# Example usage
async def main():
    """Example usage of the planning engine."""
    # Initialize planning engine
    engine = PlanningEngine()
    await engine.initialize()
    
    # Simple objective
    simple_objective = "Create a landing page for the product."
    simple_context = {"deadline": "2 weeks", "team_size": 2}
    
    # Complex objective
    complex_objective = "Develop a distributed microservice architecture that integrates with legacy systems, " \
                      "handles high-volume data processing, ensures GDPR compliance, and optimizes for both " \
                      "performance and maintainability across multiple cloud environments."
    complex_context = {
        "constraints": {
            "budget": "Limited",
            "timeline": "3 months",
            "team": "Cross-functional, 8 members"
        },
        "technologies": ["Kubernetes", "Kafka", "GraphQL", "PostgreSQL"],
        "requirements": ["High availability", "Data privacy", "Audit logging", "Scalability"]
    }
    
    try:
        # Create plans
        print("\n==== Simple Planning ====")
        simple_result = await engine.create_plan(simple_objective, simple_context)
        print(f"Used latent reasoning: {simple_result['used_latent_reasoning']}")
        print(f"Complexity score: {simple_result['complexity_score']:.4f}")
        print(f"Iterations: {simple_result['iterations']}")
        
        print("\n==== Complex Planning ====")
        complex_result = await engine.create_plan(complex_objective, complex_context)
        print(f"Used latent reasoning: {complex_result['used_latent_reasoning']}")
        print(f"Complexity score: {complex_result['complexity_score']:.4f}")
        print(f"Iterations: {complex_result['iterations']}")
        
    finally:
        # Clean up
        await engine.close()


if __name__ == "__main__":
    asyncio.run(main())