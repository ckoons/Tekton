"""Telos-Prometheus integration for planning requirements.

This module provides a connector between Telos requirements and Prometheus
planning capabilities, enabling bidirectional communication.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from telos.core.requirements import RequirementsManager, Requirement, Project

logger = logging.getLogger(__name__)


class TelosPrometheusConnector:
    """Bridge between Telos requirements and Prometheus planning."""
    
    def __init__(self, requirements_manager: RequirementsManager):
        """
        Initialize the connector.
        
        Args:
            requirements_manager: The requirements manager instance
        """
        self.requirements_manager = requirements_manager
        self.queries = []  # Store queries from Prometheus to Telos/user
        self.prometheus_available = False
        
        # Try to import Prometheus planning engine (optional dependency)
        try:
            from prometheus.core.planning_engine import PlanningEngine
            from tekton.utils.port_config import get_prometheus_url
            
            # Initialize with standardized port config
            prometheus_url = get_prometheus_url()
            self.planning_engine = PlanningEngine(prometheus_url=prometheus_url)
            self.prometheus_available = True
            logger.info(f"Initialized Prometheus connection with URL: {prometheus_url}")
        except ImportError:
            logger.warning("Prometheus planning engine not available. Planning features will be limited.")
            self.planning_engine = None
    
    async def initialize(self) -> bool:
        """
        Initialize the connector and planning engine.
        
        Returns:
            Success status
        """
        if not self.prometheus_available:
            return False
            
        try:
            # Initialize the planning engine
            return await self.planning_engine.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize planning engine: {e}")
            return False
    
    async def prepare_requirements_for_planning(self, project_id: str) -> Dict[str, Any]:
        """
        Process requirements to determine planning readiness.
        
        Args:
            project_id: Project ID
            
        Returns:
            Analysis results
        """
        # Get the project
        project = self.requirements_manager.get_project(project_id)
        if not project:
            return {"status": "error", "message": f"Project {project_id} not found"}
            
        # Analyze requirements for completeness, clarity, etc.
        try:
            from telos.ui.interactive_refine import analyze_requirements_for_planning
            analysis_result = await analyze_requirements_for_planning(
                self.requirements_manager, project_id
            )
            
            if analysis_result["status"] == "error":
                return analysis_result
                
            if analysis_result["status"] == "needs_refinement":
                # Not ready for planning
                return {
                    "status": "needs_refinement",
                    "message": "Some requirements need refinement before planning",
                    "analysis": analysis_result
                }
                
            # Requirements are ready - prepare context
            context = self._prepare_planning_context(project)
            return {
                "status": "ready",
                "message": "Requirements are ready for planning",
                "context": context,
                "analysis": analysis_result
            }
        except Exception as e:
            logger.error(f"Error analyzing requirements: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_plan(self, project_id: str) -> Dict[str, Any]:
        """
        Create a plan for a project using Prometheus.
        
        Args:
            project_id: Project ID
            
        Returns:
            Plan results
        """
        # Check if Prometheus is available
        if not self.prometheus_available or not self.planning_engine:
            return {
                "status": "error", 
                "message": "Prometheus planning engine not available"
            }
        
        # Check if project exists
        project = self.requirements_manager.get_project(project_id)
        if not project:
            return {"status": "error", "message": f"Project {project_id} not found"}
            
        # Check if requirements are ready for planning
        readiness = await self.prepare_requirements_for_planning(project_id)
        if readiness["status"] != "ready":
            return readiness
            
        # Generate plan using Prometheus
        try:
            # Compile the objective statement
            objective = self._compile_objective(project)
            context = readiness["context"]
            
            # Create the plan
            plan_result = await self.planning_engine.create_plan(objective, context)
            
            # Store the plan in project metadata
            self._store_plan_in_project(project, plan_result, objective)
            
            return {
                "status": "success",
                "message": "Plan created successfully",
                "plan": plan_result
            }
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return {"status": "error", "message": str(e)}
    
    async def request_clarification(self, project_id: str, requirement_id: str, 
                                  question: str) -> Dict[str, Any]:
        """
        Request clarification from the user about a requirement.
        
        Args:
            project_id: Project ID
            requirement_id: Requirement ID
            question: Question to ask
            
        Returns:
            Query status
        """
        # Make sure requirement exists
        requirement = self.requirements_manager.get_requirement(project_id, requirement_id)
        if not requirement:
            return {
                "status": "error", 
                "message": f"Requirement {requirement_id} not found in project {project_id}"
            }
            
        # Add the query to the list
        query_id = len(self.queries)
        self.queries.append({
            "query_id": query_id,
            "project_id": project_id,
            "requirement_id": requirement_id,
            "question": question,
            "timestamp": time.time(),
            "status": "pending"
        })
        
        return {
            "status": "success",
            "message": "Clarification requested",
            "query_id": query_id
        }
    
    def get_pending_queries(self) -> List[Dict[str, Any]]:
        """
        Get all pending clarification queries.
        
        Returns:
            List of pending queries
        """
        return [q for q in self.queries if q["status"] == "pending"]
    
    async def answer_clarification(self, query_id: int, answer: str) -> Dict[str, Any]:
        """
        Provide an answer to a clarification query.
        
        Args:
            query_id: Query ID
            answer: User's answer
            
        Returns:
            Update status
        """
        # Find the query
        if query_id < 0 or query_id >= len(self.queries):
            return {"status": "error", "message": f"Query ID {query_id} not found"}
            
        query = self.queries[query_id]
        if query["status"] != "pending":
            return {"status": "error", "message": f"Query {query_id} is not pending"}
            
        # Update the query
        query["answer"] = answer
        query["status"] = "answered"
        query["answer_timestamp"] = time.time()
        
        # Update the requirement with this clarification
        try:
            project_id = query["project_id"]
            requirement_id = query["requirement_id"]
            requirement = self.requirements_manager.get_requirement(project_id, requirement_id)
            
            if requirement:
                # Add to requirement metadata
                if "clarifications" not in requirement.metadata:
                    requirement.metadata["clarifications"] = []
                    
                requirement.metadata["clarifications"].append({
                    "question": query["question"],
                    "answer": answer,
                    "timestamp": time.time()
                })
                
                # Update the requirement
                self.requirements_manager.update_requirement(
                    project_id, requirement_id, metadata=requirement.metadata
                )
                
                return {"status": "success", "message": "Clarification recorded"}
            else:
                return {"status": "error", "message": "Requirement no longer exists"}
        except Exception as e:
            logger.error(f"Error recording clarification: {e}")
            return {"status": "error", "message": str(e)}
    
    def _compile_objective(self, project: Project) -> str:
        """
        Compile project requirements into a planning objective.
        
        Args:
            project: Project object
            
        Returns:
            Objective statement
        """
        # Start with project name
        objective = f"Create a plan for {project.name}"
        
        # Add project description if available
        if project.description:
            objective += f": {project.description}"
            
        # Add high-priority requirements if available
        high_priority_reqs = []
        for req_id, req in project.requirements.items():
            if req.priority in ["high", "critical"]:
                high_priority_reqs.append(req)
                
        if high_priority_reqs:
            objective += "\n\nPrimary goals:"
            for req in high_priority_reqs[:3]:  # Limit to top 3
                objective += f"\n- {req.title}"
                
        return objective
    
    def _prepare_planning_context(self, project: Project) -> Dict[str, Any]:
        """
        Prepare detailed context from requirements for planning.
        
        Args:
            project: Project object
            
        Returns:
            Context dictionary for planning
        """
        context = {
            "project_info": {
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            },
            "requirements": {
                "functional": [],
                "non_functional": [],
                "constraints": []
            },
            "dependencies": {},
            "priorities": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }
        }
        
        # Process each requirement
        for req_id, req in project.requirements.items():
            # Create basic requirement info
            req_info = {
                "id": req_id,
                "title": req.title,
                "description": req.description,
                "status": req.status,
                "priority": req.priority,
                "tags": req.tags
            }
            
            # Add to type-based categories
            req_type = req.requirement_type
            if req_type == "non-functional" or req_type == "non_functional":
                context["requirements"]["non_functional"].append(req_info)
            elif req_type == "constraint":
                context["requirements"]["constraints"].append(req_info)
            else:
                context["requirements"]["functional"].append(req_info)
                
            # Add to priority-based lists
            context["priorities"][req.priority].append(req_id)
            
            # Track dependencies
            if req.dependencies:
                context["dependencies"][req_id] = req.dependencies
        
        return context
    
    def _store_plan_in_project(self, project: Project, plan: Dict[str, Any], 
                             objective: str) -> None:
        """
        Store a generated plan in the project metadata.
        
        Args:
            project: Project object
            plan: Plan data
            objective: Planning objective
        """
        # Create a plan summary
        plan_content = plan.get("plan", "")
        plan_summary = plan_content.split("\n")[0] if plan_content else "No plan content"
        
        # Create plan metadata
        plan_data = {
            "plan_id": plan.get("thought_id", str(int(time.time()))),
            "created_at": time.time(),
            "objective": objective,
            "complexity_score": plan.get("complexity_score", 0.0),
            "content": plan_content,
            "summary": plan_summary[:100]  # Truncate to reasonable length
        }
        
        # Add to project metadata
        if "plans" not in project.metadata:
            project.metadata["plans"] = []
            
        project.metadata["plans"].append(plan_data)
        
        # Save the project
        self.requirements_manager._save_project(project)


# Command-line functions
async def create_plan_cmd(requirements_manager: RequirementsManager, project_id: str) -> None:
    """
    Create a plan for a project using the Prometheus connector.
    
    Args:
        requirements_manager: Requirements manager instance
        project_id: Project ID
    """
    connector = TelosPrometheusConnector(requirements_manager)
    
    # Initialize the connector
    initialized = await connector.initialize()
    if not initialized:
        print("⚠ Prometheus planning engine not available or failed to initialize")
        print("  Planning preview will be shown, but no actual plan will be generated")
        
    # Prepare requirements for planning
    print(f"Analyzing requirements for project {project_id}...")
    readiness = await connector.prepare_requirements_for_planning(project_id)
    
    if readiness["status"] == "error":
        print(f"Error: {readiness['message']}")
        return
        
    # Show readiness analysis
    if "analysis" in readiness:
        analysis = readiness["analysis"]
        print(f"\nPlanning Readiness: {analysis['requirements_ready']}/{analysis['requirements_total']} requirements ready ({analysis['readiness_percentage']:.1f}%)")
        
    # If not ready, show what needs to be refined
    if readiness["status"] == "needs_refinement":
        print("\n⚠ Some requirements need refinement before planning:")
        
        for i, req_analysis in enumerate(readiness.get("analysis", {}).get("analyses", [])[:3]):
            if not req_analysis.get("ready", False):
                print(f"\n{i+1}. {req_analysis['title']} ({req_analysis['requirement_id']})")
                print(f"   Score: {req_analysis['score']:.2f}")
                
                for suggestion in req_analysis.get("suggestions", []):
                    print(f"   - {suggestion}")
                    
        print("\nRefine these requirements with:")
        print(f"   telos refine requirement {project_id} --requirement-id <id>")
        return
        
    # Requirements are ready, create plan
    if initialized:
        # Create actual plan
        print("\nCreating plan with Prometheus planning engine...")
        result = await connector.create_plan(project_id)
        
        if result["status"] == "error":
            print(f"Error: {result['message']}")
            return
            
        # Show plan
        plan = result.get("plan", {})
        print("\nPlan created successfully!\n")
        print(plan.get("plan", "No plan content available"))
    else:
        # Show preview of planning context
        print("\n(Preview mode - Prometheus not available)\n")
        context = readiness.get("context", {})
        
        # Get project info
        project = requirements_manager.get_project(project_id)
        
        # Generate a simple plan structure
        print(f"# Plan for {project.name}\n")
        print("## Project Overview")
        print(f"{project.description}\n")
        
        print("## Requirements Summary")
        print(f"- Functional Requirements: {len(context.get('requirements', {}).get('functional', []))}")
        print(f"- Non-Functional Requirements: {len(context.get('requirements', {}).get('non_functional', []))}")
        print(f"- Constraints: {len(context.get('requirements', {}).get('constraints', []))}\n")
        
        print("## Critical Requirements")
        for req_id in context.get("priorities", {}).get("critical", []):
            req = requirements_manager.get_requirement(project_id, req_id)
            if req:
                print(f"- {req.title}")
        
        print("\n## Integration with Prometheus")
        print("When connected to Prometheus, a full plan will be generated here.")