"""Interactive requirements refinement for Telos.

This module provides interactive CLI functionality for refining requirements
with AI-assisted feedback and improvement suggestions.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional

from telos.core.requirements import RequirementsManager
from telos.core.requirement import Requirement

logger = logging.getLogger(__name__)

# Import refactored modules
from .analyzers import RequirementAnalyzer
from .formatters import format_detailed_feedback, display_requirement

class InteractiveRefiner:
    """Interactive CLI-based requirement refinement."""
    
    def __init__(self, requirements_manager: RequirementsManager):
        """
        Initialize the interactive refiner.
        
        Args:
            requirements_manager: The requirements manager instance
        """
        self.requirements_manager = requirements_manager
        self.analyzer = RequirementAnalyzer()
    
    async def refine_requirement(self, project_id: str, requirement_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start an interactive refinement session for a requirement.
        
        Args:
            project_id: The project ID
            requirement_id: Optional requirement ID (if None, create a new requirement)
            
        Returns:
            Result of the refinement process
        """
        # Check if the project exists
        project = self.requirements_manager.get_project(project_id)
        if not project:
            return {"status": "error", "message": f"Project {project_id} not found"}
        
        # Get or create requirement
        if requirement_id:
            requirement = self.requirements_manager.get_requirement(project_id, requirement_id)
            if not requirement:
                return {"status": "error", "message": f"Requirement {requirement_id} not found in project {project_id}"}
            print(f"\nLet's refine requirement: {requirement.title} ({requirement_id})\n")
        else:
            # Get initial info for a new requirement
            print("\nLet's create a new requirement\n")
            title = input("Title: ")
            description = input("Brief description: ")
            
            # Create the requirement
            requirement_id = self.requirements_manager.add_requirement(
                project_id=project_id,
                title=title,
                description=description
            )
            requirement = self.requirements_manager.get_requirement(project_id, requirement_id)
            print(f"\nCreated new requirement with ID: {requirement_id}\n")
        
        # Interactive refinement loop
        print("\nLet's refine this requirement together...\n")
        refinement_complete = False
        
        while not refinement_complete:
            # Analyze current quality
            analysis = await self.analyzer.analyze_requirement(requirement)
            
            # Check if requirement is already good enough
            if analysis["score"] > 0.85:
                print("\n✓ This requirement is well-defined and ready for planning!\n")
                refinement_complete = True
                continue
            
            # Show current requirement details
            display_requirement(requirement)
            
            # Show quality assessment and suggestions
            print("\n" + analysis["detailed_feedback"])
            
            # Process user choice
            refinement_complete = await self._process_refinement_choice(
                project_id, requirement_id, requirement, analysis
            )
            
            # Refresh requirement data if not complete
            if not refinement_complete:
                requirement = self.requirements_manager.get_requirement(project_id, requirement_id)
        
        # Final assessment
        final_analysis = await self.analyzer.analyze_requirement(requirement)
        
        print("\nRefinement complete!")
        print(f"Final quality score: {final_analysis['score']:.2f}/1.0")
        
        # Add refinement history
        await self._update_refinement_history(
            project_id, requirement_id, requirement, analysis, final_analysis
        )
        
        return {
            "status": "success",
            "requirement_id": requirement_id,
            "score": final_analysis["score"],
            "ready_for_planning": final_analysis["score"] > 0.7
        }
    
    async def _process_refinement_choice(
        self, 
        project_id: str, 
        requirement_id: str, 
        requirement: Requirement, 
        analysis: Dict[str, Any]
    ) -> bool:
        """
        Process user's choice for requirement refinement.
        
        Args:
            project_id: The project ID
            requirement_id: The requirement ID
            requirement: The current requirement object
            analysis: The requirement analysis results
            
        Returns:
            True if refinement is complete, False to continue refining
        """
        # Show options
        print("\nOptions:")
        print("1. Update title")
        print("2. Update description")
        print("3. Update requirement type")
        print("4. Update priority")
        print("5. Add or update tags")
        print("6. Mark as complete and finish refinement")
        print("7. Show detailed analysis")
        print("8. Exit without further changes")
        
        choice = input("\nWhat would you like to do? [1-8]: ")
        
        if choice == "1":
            new_title = input(f"Current title: {requirement.title}\nNew title: ")
            if new_title:
                self.requirements_manager.update_requirement(
                    project_id, requirement_id, title=new_title
                )
        elif choice == "2":
            print(f"Current description: {requirement.description}")
            new_description = input("New description: ")
            if new_description:
                self.requirements_manager.update_requirement(
                    project_id, requirement_id, description=new_description
                )
        elif choice == "3":
            print(f"Current type: {requirement.requirement_type}")
            print("Available types: functional, non-functional, constraint")
            new_type = input("New type: ")
            if new_type:
                self.requirements_manager.update_requirement(
                    project_id, requirement_id, requirement_type=new_type
                )
        elif choice == "4":
            print(f"Current priority: {requirement.priority}")
            print("Available priorities: low, medium, high, critical")
            new_priority = input("New priority: ")
            if new_priority:
                self.requirements_manager.update_requirement(
                    project_id, requirement_id, priority=new_priority
                )
        elif choice == "5":
            current_tags = ", ".join(requirement.tags) if requirement.tags else "None"
            print(f"Current tags: {current_tags}")
            new_tags = input("New tags (comma-separated): ")
            if new_tags:
                tag_list = [tag.strip() for tag in new_tags.split(",")]
                self.requirements_manager.update_requirement(
                    project_id, requirement_id, tags=tag_list
                )
        elif choice == "6":
            return True
        elif choice == "7":
            print("\n" + analysis["detailed_feedback"])
            input("\nPress Enter to continue...")
        elif choice == "8":
            return True
        else:
            print("Invalid choice. Please try again.")
        
        return False
    
    async def _update_refinement_history(
        self,
        project_id: str,
        requirement_id: str,
        requirement: Requirement,
        initial_analysis: Dict[str, Any],
        final_analysis: Dict[str, Any]
    ) -> None:
        """
        Update the refinement history for a requirement.
        
        Args:
            project_id: The project ID
            requirement_id: The requirement ID
            requirement: The requirement object
            initial_analysis: The initial analysis results
            final_analysis: The final analysis results
        """
        if not requirement.metadata.get("refinement_history"):
            requirement.metadata["refinement_history"] = []
            
        requirement.metadata["refinement_history"].append({
            "timestamp": time.time(),
            "score_before": initial_analysis["score"],
            "score_after": final_analysis["score"],
            "improved_areas": list(set(initial_analysis["improvement_areas"]) - set(final_analysis["improvement_areas"]))
        })
        
        self.requirements_manager.update_requirement(
            project_id, requirement_id, metadata=requirement.metadata
        )


async def analyze_requirements_for_planning(requirements_manager: RequirementsManager, project_id: str) -> Dict[str, Any]:
    """
    Analyze all requirements in a project to determine readiness for planning.
    
    Args:
        requirements_manager: Requirements manager instance
        project_id: The project ID
        
    Returns:
        Analysis results for planning readiness
    """
    # Get the project
    project = requirements_manager.get_project(project_id)
    if not project:
        return {"status": "error", "message": f"Project {project_id} not found"}
    
    # Get all requirements
    requirements = []
    for req_id, req in project.requirements.items():
        requirements.append(req)
    
    if not requirements:
        return {"status": "error", "message": "No requirements found in project"}
    
    # Analyze each requirement
    analyzer = RequirementAnalyzer()
    analyses = []
    
    for req in requirements:
        analysis = await analyzer.analyze_requirement(req)
        analyses.append({
            "requirement_id": req.requirement_id,
            "title": req.title,
            "score": analysis["score"],
            "ready": analysis["score"] > 0.7,
            "issues": len(analysis["suggestions"]),
            "suggestions": analysis["suggestions"][:3]  # Just first 3 suggestions
        })
    
    # Calculate overall readiness
    ready_count = sum(1 for analysis in analyses if analysis["ready"])
    total_count = len(analyses)
    readiness_percentage = (ready_count / total_count) * 100 if total_count > 0 else 0
    
    # Status based on readiness threshold
    status = "ready" if readiness_percentage >= 70 else "needs_refinement"
    
    # Sort analyses by score (lowest first)
    analyses.sort(key=lambda x: x["score"])
    
    return {
        "status": status,
        "project_id": project_id,
        "project_name": project.name,
        "requirements_total": total_count,
        "requirements_ready": ready_count,
        "readiness_percentage": readiness_percentage,
        "analyses": analyses
    }


# Command line functions for integration with Telos CLI
def refine_requirement_cmd(requirements_manager: RequirementsManager, project_id: str, requirement_id: Optional[str] = None) -> None:
    """
    CLI command to refine a requirement interactively.
    
    Args:
        requirements_manager: Requirements manager instance
        project_id: The project ID
        requirement_id: Optional requirement ID
    """
    # Create refiner and run the async function
    refiner = InteractiveRefiner(requirements_manager)
    result = asyncio.run(refiner.refine_requirement(project_id, requirement_id))
    
    if result["status"] == "error":
        print(f"Error: {result['message']}")
    else:
        print(f"\nRequirement {result['requirement_id']} refined successfully!")
        print(f"Quality score: {result['score']:.2f}/1.0")
        
        if result["ready_for_planning"]:
            print("✓ This requirement is ready for planning with Prometheus")
        else:
            print("⚠ This requirement might need further refinement before planning")


def analyze_for_planning_cmd(requirements_manager: RequirementsManager, project_id: str) -> None:
    """
    CLI command to analyze requirements for planning readiness.
    
    Args:
        requirements_manager: Requirements manager instance
        project_id: The project ID
    """
    # Run the async function
    result = asyncio.run(analyze_requirements_for_planning(requirements_manager, project_id))
    
    if result["status"] == "error":
        print(f"Error: {result['message']}")
        return
    
    # Display results
    print(f"\nPlanning Readiness Analysis for {result['project_name']} ({project_id})")
    print(f"Requirements Ready: {result['requirements_ready']}/{result['requirements_total']} ({result['readiness_percentage']:.1f}%)")
    
    if result["status"] == "ready":
        print("\n✓ This project is ready for planning with Prometheus")
    else:
        print("\n⚠ Some requirements need refinement before planning")
    
    if result["analyses"]:
        print("\nRequirements needing most improvement:")
        for i, analysis in enumerate(result["analyses"][:3]):  # Show top 3 most problematic
            print(f"\n{i+1}. {analysis['title']} ({analysis['requirement_id']})")
            print(f"   Score: {analysis['score']:.2f}")
            
            if analysis["suggestions"]:
                print("   Top suggestions:")
                for suggestion in analysis["suggestions"]:
                    print(f"   - {suggestion}")