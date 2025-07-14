"""
Recommendation System for Sophia

This module provides a system for generating, tracking, and validating
improvement recommendations for the Tekton ecosystem based on
metrics analysis and experimentation.
"""

import os
import json
import uuid
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum

# Import other core engines
from .metrics_engine import get_metrics_engine
from .analysis_engine import get_analysis_engine
from .database import get_database
# Note: LLM adapter and experiment framework may not be available yet
# We'll handle their absence gracefully

logger = logging.getLogger("sophia.recommendation_system")

class RecommendationStatus(str, Enum):
    """Recommendation status enumeration."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    IMPLEMENTING = "implementing"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    REJECTED = "rejected"
    FAILED = "failed"

class RecommendationPriority(str, Enum):
    """Recommendation priority enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RecommendationImpact(str, Enum):
    """Recommendation impact enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RecommendationSource(str, Enum):
    """Recommendation source enumeration."""
    ANALYSIS = "analysis"
    EXPERIMENT = "experiment"
    ANOMALY = "anomaly"
    MANUAL = "manual"
    PATTERN = "pattern"
    CSA = "computational_spectral_analysis"
    CT = "catastrophe_theory"

class RecommendationSystem:
    """
    Core recommendation system for generating and tracking improvement suggestions.
    
    Provides a comprehensive approach to continuous improvement through
    data-driven recommendations and validation.
    """
    
    def __init__(self):
        """Initialize the recommendation system."""
        self.is_initialized = False
        self.recommendations = {}
        self.metrics_engine = None
        self.analysis_engine = None
        self.experiment_framework = None
        self.database = None
        self.generation_tasks = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the recommendation system.
        
        Returns:
            True if initialization was successful
        """
        logger.info("Initializing Sophia Recommendation System...")
        
        # Get required engines
        self.metrics_engine = await get_metrics_engine()
        self.analysis_engine = await get_analysis_engine()
        
        # Initialize database
        self.database = await get_database()
        
        # Try to get experiment framework (may not be available yet)
        try:
            from .experiment_framework import get_experiment_framework
            self.experiment_framework = await get_experiment_framework()
        except ImportError:
            logger.warning("Experiment framework not available, some features will be limited")
            self.experiment_framework = None
        
        # Load recommendations if available
        await self._load_recommendations()
        
        self.is_initialized = True
        logger.info("Sophia Recommendation System initialized successfully")
        return True
        
    async def start(self) -> bool:
        """
        Start the recommendation system and background tasks.
        
        Returns:
            True if successful
        """
        if not self.is_initialized:
            success = await self.initialize()
            if not success:
                logger.error("Failed to initialize Recommendation System")
                return False
                
        logger.info("Starting Sophia Recommendation System...")
        
        # Start periodic recommendations generation
        self.generation_tasks["periodic_recommendations"] = asyncio.create_task(
            self._generate_periodic_recommendations()
        )
        
        logger.info("Sophia Recommendation System started successfully")
        return True
        
    async def stop(self) -> bool:
        """
        Stop the recommendation system and clean up resources.
        
        Returns:
            True if successful
        """
        logger.info("Stopping Sophia Recommendation System...")
        
        # Cancel background tasks
        for task_name, task in self.generation_tasks.items():
            logger.info(f"Cancelling task: {task_name}")
            task.cancel()
            
        self.generation_tasks = {}
        
        logger.info("Sophia Recommendation System stopped successfully")
        return True
        
    async def create_recommendation(
        self,
        title: str,
        description: str,
        component_ids: List[str],
        impact_areas: List[str],
        estimated_impact: float,
        effort_estimate: Union[str, RecommendationImpact],
        implementation_plan: str,
        supporting_metrics: Optional[List[str]] = None,
        experiments: Optional[List[str]] = None,
        source: Optional[Union[str, RecommendationSource]] = RecommendationSource.ANALYSIS,
        priority: Optional[Union[str, RecommendationPriority]] = RecommendationPriority.MEDIUM,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new recommendation.
        
        Args:
            title: Recommendation title
            description: Detailed description
            component_ids: Affected components
            impact_areas: Areas of impact (performance, usability, etc.)
            estimated_impact: Estimated impact (0.0 to 1.0)
            effort_estimate: Estimated effort (low, medium, high)
            implementation_plan: Detailed implementation plan
            supporting_metrics: Metrics supporting the recommendation
            experiments: Related experiments
            source: Source of the recommendation
            priority: Priority level
            tags: Tags for categorizing the recommendation
            
        Returns:
            Created recommendation
        """
        # Validate required fields
        if not title or not description:
            raise ValueError("Title and description are required")
            
        if not component_ids or not isinstance(component_ids, list):
            raise ValueError("Component IDs must be a non-empty list")
            
        if not impact_areas or not isinstance(impact_areas, list):
            raise ValueError("Impact areas must be a non-empty list")
            
        if not isinstance(estimated_impact, (int, float)) or estimated_impact < 0 or estimated_impact > 1:
            raise ValueError("Estimated impact must be a float between 0.0 and 1.0")
            
        if not implementation_plan:
            raise ValueError("Implementation plan is required")
            
        # Create recommendation ID
        recommendation_id = str(uuid.uuid4())
        
        # Convert enum values to strings if needed
        source_value = source.value if isinstance(source, RecommendationSource) else source
        priority_value = priority.value if isinstance(priority, RecommendationPriority) else priority
        effort_value = effort_estimate.value if isinstance(effort_estimate, RecommendationImpact) else effort_estimate
        
        # Create recommendation object
        recommendation = {
            "id": recommendation_id,
            "title": title,
            "description": description,
            "component_ids": component_ids,
            "impact_areas": impact_areas,
            "estimated_impact": float(estimated_impact),
            "effort_estimate": effort_value,
            "implementation_plan": implementation_plan,
            "supporting_metrics": supporting_metrics or [],
            "experiments": experiments or [],
            "source": source_value,
            "priority": priority_value,
            "tags": tags or [],
            "status": RecommendationStatus.PROPOSED,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "implemented_at": None,
            "verified_at": None,
            "acceptance_criteria": [],
            "verification_results": None,
            "implementation_notes": []
        }
        
        # Add to recommendations
        self.recommendations[recommendation_id] = recommendation
        
        # Save recommendations
        await self._save_recommendations()
        
        return recommendation
        
    async def update_recommendation_status(
        self,
        recommendation_id: str,
        status: Union[str, RecommendationStatus],
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a recommendation.
        
        Args:
            recommendation_id: ID of the recommendation
            status: New status
            notes: Optional notes about the status change
            
        Returns:
            Updated recommendation
        """
        if recommendation_id not in self.recommendations:
            raise ValueError(f"Recommendation not found: {recommendation_id}")
            
        recommendation = self.recommendations[recommendation_id]
        
        # Convert enum value to string if needed
        status_value = status.value if isinstance(status, RecommendationStatus) else status
        
        # Validate status transition
        current_status = recommendation["status"]
        valid_transitions = {
            RecommendationStatus.PROPOSED: [
                RecommendationStatus.APPROVED, 
                RecommendationStatus.REJECTED
            ],
            RecommendationStatus.APPROVED: [
                RecommendationStatus.IMPLEMENTING,
                RecommendationStatus.REJECTED
            ],
            RecommendationStatus.IMPLEMENTING: [
                RecommendationStatus.IMPLEMENTED,
                RecommendationStatus.FAILED
            ],
            RecommendationStatus.IMPLEMENTED: [
                RecommendationStatus.VERIFIED,
                RecommendationStatus.FAILED
            ],
            RecommendationStatus.VERIFIED: [],
            RecommendationStatus.REJECTED: [
                RecommendationStatus.PROPOSED  # Allow reconsidering rejected recommendations
            ],
            RecommendationStatus.FAILED: [
                RecommendationStatus.IMPLEMENTING  # Allow retrying failed implementations
            ]
        }
        
        valid_status_values = [s.value for s in valid_transitions.get(current_status, [])]
        
        if status_value not in valid_status_values and status_value != current_status:
            valid_status_names = [s.value for s in valid_transitions.get(current_status, [])]
            raise ValueError(f"Invalid status transition from {current_status} to {status_value}. Valid transitions: {valid_status_names}")
        
        # Update status
        recommendation["status"] = status_value
        recommendation["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Add note if provided
        if notes:
            if "status_history" not in recommendation:
                recommendation["status_history"] = []
                
            recommendation["status_history"].append({
                "from": current_status,
                "to": status_value,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "notes": notes
            })
            
        # Update status-specific timestamps
        if status_value == RecommendationStatus.IMPLEMENTED:
            recommendation["implemented_at"] = datetime.utcnow().isoformat() + "Z"
        elif status_value == RecommendationStatus.VERIFIED:
            recommendation["verified_at"] = datetime.utcnow().isoformat() + "Z"
            
        # Save recommendations
        await self._save_recommendations()
        
        return recommendation
        
    async def add_implementation_note(
        self,
        recommendation_id: str,
        note: str
    ) -> Dict[str, Any]:
        """
        Add an implementation note to a recommendation.
        
        Args:
            recommendation_id: ID of the recommendation
            note: Implementation note
            
        Returns:
            Updated recommendation
        """
        if recommendation_id not in self.recommendations:
            raise ValueError(f"Recommendation not found: {recommendation_id}")
            
        recommendation = self.recommendations[recommendation_id]
        
        # Add note
        if "implementation_notes" not in recommendation:
            recommendation["implementation_notes"] = []
            
        recommendation["implementation_notes"].append({
            "note": note,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        recommendation["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Save recommendations
        await self._save_recommendations()
        
        return recommendation
        
    async def add_acceptance_criteria(
        self,
        recommendation_id: str,
        criteria: str
    ) -> Dict[str, Any]:
        """
        Add an acceptance criteria to a recommendation.
        
        Args:
            recommendation_id: ID of the recommendation
            criteria: Acceptance criteria
            
        Returns:
            Updated recommendation
        """
        if recommendation_id not in self.recommendations:
            raise ValueError(f"Recommendation not found: {recommendation_id}")
            
        recommendation = self.recommendations[recommendation_id]
        
        # Add criteria
        if "acceptance_criteria" not in recommendation:
            recommendation["acceptance_criteria"] = []
            
        recommendation["acceptance_criteria"].append(criteria)
        recommendation["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Save recommendations
        await self._save_recommendations()
        
        return recommendation
        
    async def verify_recommendation(
        self,
        recommendation_id: str,
        verification_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify a recommendation after implementation.
        
        Args:
            recommendation_id: ID of the recommendation
            verification_results: Results of verification
            
        Returns:
            Updated recommendation
        """
        if recommendation_id not in self.recommendations:
            raise ValueError(f"Recommendation not found: {recommendation_id}")
            
        recommendation = self.recommendations[recommendation_id]
        
        # Check if recommendation is implemented
        if recommendation["status"] != RecommendationStatus.IMPLEMENTED:
            raise ValueError(f"Recommendation must be implemented before verification. Current status: {recommendation['status']}")
            
        # Add verification results
        recommendation["verification_results"] = verification_results
        recommendation["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Update status if all criteria are met
        criteria_met = verification_results.get("criteria_met", False)
        if criteria_met:
            await self.update_recommendation_status(
                recommendation_id=recommendation_id,
                status=RecommendationStatus.VERIFIED,
                notes="All acceptance criteria met during verification"
            )
        else:
            await self.update_recommendation_status(
                recommendation_id=recommendation_id,
                status=RecommendationStatus.FAILED,
                notes="Failed to meet all acceptance criteria during verification"
            )
            
        return recommendation
        
    async def get_recommendation(self, recommendation_id: str) -> Dict[str, Any]:
        """
        Get recommendation data.
        
        Args:
            recommendation_id: ID of the recommendation
            
        Returns:
            Recommendation data
        """
        if recommendation_id not in self.recommendations:
            raise ValueError(f"Recommendation not found: {recommendation_id}")
            
        return self.recommendations[recommendation_id]
        
    async def list_recommendations(
        self,
        status: Optional[Union[RecommendationStatus, str]] = None,
        component_id: Optional[str] = None,
        tag: Optional[str] = None,
        priority: Optional[Union[RecommendationPriority, str]] = None,
        source: Optional[Union[RecommendationSource, str]] = None,
        impact_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        List recommendations with optional filtering.
        
        Args:
            status: Filter by recommendation status
            component_id: Filter by affected component
            tag: Filter by tag
            priority: Filter by priority
            source: Filter by source
            impact_threshold: Filter by minimum impact
            
        Returns:
            List of matching recommendations
        """
        # Convert enum values to strings if needed
        status_value = status.value if isinstance(status, RecommendationStatus) else status
        priority_value = priority.value if isinstance(priority, RecommendationPriority) else priority
        source_value = source.value if isinstance(source, RecommendationSource) else source
        
        # Filter recommendations
        filtered_recommendations = []
        
        for rec_id, rec in self.recommendations.items():
            # Apply status filter
            if status_value and rec["status"] != status_value:
                continue
                
            # Apply component filter
            if component_id and component_id not in rec.get("component_ids", []):
                continue
                
            # Apply tag filter
            if tag and tag not in rec.get("tags", []):
                continue
                
            # Apply priority filter
            if priority_value and rec["priority"] != priority_value:
                continue
                
            # Apply source filter
            if source_value and rec["source"] != source_value:
                continue
                
            # Apply impact threshold filter
            if impact_threshold is not None and rec["estimated_impact"] < impact_threshold:
                continue
                
            # Add to results
            filtered_recommendations.append(rec)
            
        # Sort by priority and impact
        priority_map = {
            RecommendationPriority.CRITICAL.value: 4,
            RecommendationPriority.HIGH.value: 3,
            RecommendationPriority.MEDIUM.value: 2,
            RecommendationPriority.LOW.value: 1
        }
        
        filtered_recommendations.sort(
            key=lambda x: (
                priority_map.get(x["priority"], 0),
                x["estimated_impact"]
            ),
            reverse=True
        )
        
        return filtered_recommendations
        
    async def generate_recommendations_from_analysis(
        self,
        component_id: str,
        time_window: str = "7d",
        use_llm: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on analysis of a component's metrics.
        
        Args:
            component_id: ID of the component to analyze
            time_window: Time window for analysis
            use_llm: Whether to use LLM for enhanced recommendations
            
        Returns:
            List of generated recommendations
        """
        # Get component analysis
        try:
            analysis = await self.analysis_engine.analyze_component_performance(
                component_id=component_id,
                time_window=time_window
            )
        except Exception as e:
            logger.error(f"Error analyzing component {component_id}: {e}")
            return []
            
        # Check if we have analysis data
        if not analysis or "metric_analyses" not in analysis:
            logger.warning(f"No analysis data available for component {component_id}")
            return []
        
        # Generate recommendations using LLM if enabled
        if use_llm:
            try:
                logger.info(f"Generating LLM-based recommendations for component {component_id}")
                
                # Try to get LLM adapter (may not be available)
                try:
                    from .llm_adapter import get_llm_adapter
                    llm_adapter = await get_llm_adapter()
                    
                    # Generate LLM-enhanced analysis
                    llm_analysis = await llm_adapter.analyze_metrics(
                        metrics_data=analysis,
                        component_id=component_id
                    )
                    
                    # Generate recommendations based on LLM analysis
                    llm_recommendations = await llm_adapter.generate_recommendations(
                        analysis_results=llm_analysis,
                        target_component=component_id,
                        count=5  # Request 5 recommendations
                    )
                except ImportError:
                    logger.warning("LLM adapter not available, using rule-based recommendations only")
                    llm_recommendations = []
                
                # Create recommendations from LLM output
                created_recommendations = []
                
                for rec_data in llm_recommendations:
                    try:
                        # Map LLM recommendation fields to our schema
                        title = rec_data.get("title", "LLM Generated Recommendation")
                        description = rec_data.get("description", "No description provided")
                        
                        # Map impact to estimated_impact (0.0-1.0 scale)
                        impact_str = rec_data.get("impact", "medium").lower()
                        estimated_impact = {
                            "high": 0.8,
                            "medium": 0.5,
                            "low": 0.3
                        }.get(impact_str, 0.5)
                        
                        # Map effort to effort_estimate (enum value)
                        effort_str = rec_data.get("effort", "medium").lower()
                        effort_estimate = {
                            "high": RecommendationImpact.HIGH,
                            "medium": RecommendationImpact.MEDIUM,
                            "low": RecommendationImpact.LOW
                        }.get(effort_str, RecommendationImpact.MEDIUM)
                        
                        # Extract implementation steps
                        implementation_steps = rec_data.get("implementation_steps", [])
                        if isinstance(implementation_steps, list):
                            implementation_plan = "\n".join([f"{i+1}. {step}" for i, step in enumerate(implementation_steps)])
                        else:
                            implementation_plan = rec_data.get("implementation_steps", "No implementation plan provided")
                        
                        # Create the recommendation
                        recommendation = await self.create_recommendation(
                            title=title,
                            description=description,
                            component_ids=[component_id],
                            impact_areas=rec_data.get("impact_areas", ["performance"]),
                            estimated_impact=estimated_impact,
                            effort_estimate=effort_estimate,
                            implementation_plan=implementation_plan,
                            supporting_metrics=rec_data.get("supporting_metrics", []),
                            source=RecommendationSource.ANALYSIS,
                            priority=RecommendationPriority.MEDIUM,
                            tags=["llm-generated", "analysis-generated", "auto-generated"]
                        )
                        
                        created_recommendations.append(recommendation)
                        
                    except Exception as e:
                        logger.error(f"Error creating LLM recommendation: {e}")
                
                # If we successfully created LLM recommendations, return them
                if created_recommendations:
                    logger.info(f"Generated {len(created_recommendations)} LLM-based recommendations for {component_id}")
                    return created_recommendations
                    
                # Otherwise, fall back to rule-based recommendations
                logger.warning(f"No valid LLM recommendations generated, falling back to rule-based approach")
                
            except Exception as e:
                logger.error(f"Error generating LLM recommendations for {component_id}: {e}")
                logger.info("Falling back to rule-based recommendation generation")
                
        # Traditional rule-based recommendation generation (fallback)
        recommendations = []
        
        # Check for performance issues
        performance_recommendations = await self._analyze_performance_metrics(
            component_id, analysis
        )
        recommendations.extend(performance_recommendations)
        
        # Check for resource issues
        resource_recommendations = await self._analyze_resource_metrics(
            component_id, analysis
        )
        recommendations.extend(resource_recommendations)
        
        # Check for error rates
        error_recommendations = await self._analyze_error_metrics(
            component_id, analysis
        )
        recommendations.extend(error_recommendations)
        
        # Check for anomalies
        anomaly_recommendations = await self._analyze_anomalies(
            component_id, analysis
        )
        recommendations.extend(anomaly_recommendations)
        
        # Create recommendations
        created_recommendations = []
        
        for rec_data in recommendations:
            try:
                recommendation = await self.create_recommendation(
                    title=rec_data["title"],
                    description=rec_data["description"],
                    component_ids=[component_id],
                    impact_areas=rec_data["impact_areas"],
                    estimated_impact=rec_data["estimated_impact"],
                    effort_estimate=rec_data["effort_estimate"],
                    implementation_plan=rec_data["implementation_plan"],
                    supporting_metrics=rec_data.get("supporting_metrics", []),
                    source=RecommendationSource.ANALYSIS,
                    priority=rec_data["priority"],
                    tags=["analysis-generated", "auto-generated", "rule-based"]
                )
                
                created_recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error creating recommendation: {e}")
                
        return created_recommendations
        
    async def generate_recommendation_from_experiment(
        self,
        experiment_id: str,
        use_llm: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a recommendation based on experiment results.
        
        Args:
            experiment_id: ID of the experiment
            use_llm: Whether to use LLM for enhanced recommendation generation
            
        Returns:
            Generated recommendation or None if unsuccessful
        """
        try:
            # Check if experiment framework is available
            if not self.experiment_framework:
                logger.warning("Experiment framework not available, cannot generate recommendation from experiment")
                return None
                
            # Get experiment report
            report = await self.experiment_framework.generate_experiment_report(
                experiment_id=experiment_id
            )
        except Exception as e:
            logger.error(f"Error generating experiment report: {e}")
            return None
            
        # Check if experiment was analyzed
        if report["status"] != "analyzed":
            logger.warning(f"Experiment {experiment_id} has not been analyzed yet")
            return None
            
        # Check if experiment has recommendations
        recommendations = report.get("recommendations", [])
        if not recommendations:
            logger.warning(f"Experiment {experiment_id} has no recommendations")
            return None
            
        # Use the highest priority recommendation
        primary_recommendation = recommendations[0]
        
        # Check if it's an implementation recommendation
        if primary_recommendation.get("type") != "implementation":
            logger.info(f"Experiment {experiment_id} does not recommend implementation")
            return None
            
        # Try LLM-enhanced recommendation generation if enabled
        if use_llm:
            try:
                logger.info(f"Generating LLM-enhanced recommendation for experiment {experiment_id}")
                
                # Try to get LLM adapter (may not be available)
                try:
                    from .llm_adapter import get_llm_adapter
                    llm_adapter = await get_llm_adapter()
                    
                    # Create hypothesis from experiment details
                    hypothesis = f"Implementing the changes tested in experiment '{report['name']}' will improve {', '.join(report['metrics'])}"
                    
                    # Generate a well-designed experiment with LLM
                    experiment_design = await llm_adapter.design_experiment(
                        hypothesis=hypothesis,
                        available_components=report["components"],
                        metrics_summary={"metrics": report["metrics"], "conclusion": report["conclusion"]}
                    )
                except ImportError:
                    logger.warning("LLM adapter not available, using basic experiment-based recommendation")
                    experiment_design = None
                
                # Generate a recommendation based on the experiment
                title = f"Implement changes from experiment: {report['name']}"
                
                # Create implementation plan from the experiment design
                implementation_steps = experiment_design.get("implementation_steps", []) if experiment_design else []
                if not implementation_steps and experiment_design:
                    implementation_steps = experiment_design.get("methodology", [])
                    
                # Format the implementation plan
                if isinstance(implementation_steps, list):
                    implementation_plan = "\n".join([f"{i+1}. {step}" for i, step in enumerate(implementation_steps)])
                else:
                    implementation_plan = str(implementation_steps)
                    
                # If we don't have a good implementation plan from LLM, use default
                if not implementation_plan or implementation_plan == "[]":
                    implementation_plan = (
                        f"1. Implement the test configuration from experiment {experiment_id}:\n"
                        f"   - {json.dumps(report['test_config'], indent=2)}\n\n"
                        f"2. Apply changes to the following components: {', '.join(report['components'])}\n\n"
                        f"3. Monitor the following metrics to verify improvements: {', '.join(report['metrics'])}\n\n"
                        f"4. Compare performance before and after implementation to verify expected improvements"
                    )
                    
                # Enhance the description with LLM if available
                if 'llm_adapter' in locals() and llm_adapter:
                    try:
                        llm_explanation = await llm_adapter.explain_analysis(
                            analysis_data={
                                "experiment": report["name"],
                                "conclusion": report["conclusion"],
                                "metrics": report["metrics"],
                                "components": report["components"]
                            },
                            audience="technical"
                        )
                        description = llm_explanation if llm_explanation else None
                    except Exception as e:
                        logger.warning(f"LLM explanation failed: {e}")
                        description = None
                else:
                    description = None
                
                if not description:
                    description = (
                        f"Based on the results of experiment '{report['name']}', "
                        f"we recommend implementing the tested changes. "
                        f"\n\nExperiment conclusion: {report['conclusion']}"
                    )
                
                # Create acceptance criteria
                acceptance_criteria = []
                success_criteria = experiment_design.get("success_criteria", []) if experiment_design else []
                
                if success_criteria and isinstance(success_criteria, list):
                    acceptance_criteria = success_criteria
                else:
                    # Default acceptance criteria
                    for metric_id in report["metrics"]:
                        acceptance_criteria.append(
                            f"Improvement in {metric_id} matching or exceeding experiment results"
                        )
                
                # Create recommendation
                recommendation = await self.create_recommendation(
                    title=title,
                    description=description,
                    component_ids=report["components"],
                    impact_areas=experiment_design.get("impact_areas", ["performance"]) if experiment_design else ["performance"],
                    estimated_impact=0.8,  # High impact since it's validated by experiment
                    effort_estimate=RecommendationImpact.MEDIUM,
                    implementation_plan=implementation_plan,
                    supporting_metrics=report["metrics"],
                    experiments=[experiment_id],
                    source=RecommendationSource.EXPERIMENT,
                    priority=RecommendationPriority.HIGH,
                    tags=["experiment-validated", "llm-enhanced", "auto-generated"]
                )
                
                # Add acceptance criteria
                for criteria in acceptance_criteria:
                    await self.add_acceptance_criteria(
                        recommendation_id=recommendation["id"],
                        criteria=criteria
                    )
                    
                return recommendation
                
            except Exception as e:
                logger.error(f"Error generating LLM recommendation from experiment: {e}")
                logger.info("Falling back to rule-based recommendation generation")
        
        # Generate recommendation using rule-based approach (fallback)
        try:
            # Create title
            title = f"Implement changes from experiment: {report['name']}"
            
            # Create description
            description = (
                f"Based on the results of experiment '{report['name']}', "
                f"we recommend implementing the tested changes. "
                f"\n\nExperiment conclusion: {report['conclusion']}"
            )
            
            # Create implementation plan
            implementation_plan = (
                f"1. Implement the test configuration from experiment {experiment_id}:\n"
                f"   - {json.dumps(report['test_config'], indent=2)}\n\n"
                f"2. Apply changes to the following components: {', '.join(report['components'])}\n\n"
                f"3. Monitor the following metrics to verify improvements: {', '.join(report['metrics'])}\n\n"
                f"4. Compare performance before and after implementation to verify expected improvements"
            )
            
            # Create acceptance criteria
            acceptance_criteria = []
            for metric_id in report["metrics"]:
                acceptance_criteria.append(
                    f"Improvement in {metric_id} matching or exceeding experiment results"
                )
            
            # Create recommendation
            recommendation = await self.create_recommendation(
                title=title,
                description=description,
                component_ids=report["components"],
                impact_areas=["performance"], # This could be more specific based on metrics
                estimated_impact=0.8, # High impact since it's validated by experiment
                effort_estimate=RecommendationImpact.MEDIUM,
                implementation_plan=implementation_plan,
                supporting_metrics=report["metrics"],
                experiments=[experiment_id],
                source=RecommendationSource.EXPERIMENT,
                priority=RecommendationPriority.HIGH,
                tags=["experiment-validated", "rule-based", "auto-generated"]
            )
            
            # Add acceptance criteria
            for criteria in acceptance_criteria:
                await self.add_acceptance_criteria(
                    recommendation_id=recommendation["id"],
                    criteria=criteria
                )
                
            return recommendation
            
        except Exception as e:
            logger.error(f"Error creating recommendation from experiment: {e}")
            return None
            
    async def generate_cross_component_recommendations(
        self,
        time_window: str = "7d"
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations that span multiple components.
        
        Args:
            time_window: Time window for analysis
            
        Returns:
            List of generated recommendations
        """
        # Get system-wide performance analysis
        try:
            system_analysis = await self.analysis_engine.analyze_system_performance(
                time_window=time_window
            )
        except Exception as e:
            logger.error(f"Error analyzing system performance: {e}")
            return []
            
        # Check for correlation between components
        component_ids = system_analysis.get("components_analyzed", [])
        
        # Get metrics for analysis
        metrics = ["perf.response_time", "ops.error_count", "res.cpu_usage"]
        
        # Analyze correlations between components
        correlation_recommendations = []
        
        for metric_id in metrics:
            # Check pairs of components
            for i, comp1 in enumerate(component_ids):
                for j, comp2 in enumerate(component_ids):
                    if i >= j:  # Only check each pair once
                        continue
                        
                    # Analyze correlation for this pair and metric
                    try:
                        correlation = await self.analysis_engine.analyze_multi_metric_correlations(
                            metric_ids=[f"{metric_id}:{comp1}", f"{metric_id}:{comp2}"],
                            time_window=time_window
                        )
                        
                        # Check if there's a strong correlation
                        if correlation.get("has_strong_correlations", False):
                            # Generate recommendation
                            recommendation_data = await self._generate_correlation_recommendation(
                                comp1, comp2, metric_id, correlation
                            )
                            
                            if recommendation_data:
                                correlation_recommendations.append(recommendation_data)
                                
                    except Exception as e:
                        logger.error(f"Error analyzing correlation between {comp1} and {comp2}: {e}")
        
        # Check for system-wide bottlenecks
        bottleneck_recommendations = await self._analyze_system_bottlenecks(
            system_analysis
        )
        
        # Combine recommendations
        all_recommendations = correlation_recommendations + bottleneck_recommendations
        
        # Create recommendations
        created_recommendations = []
        
        for rec_data in all_recommendations:
            try:
                recommendation = await self.create_recommendation(
                    title=rec_data["title"],
                    description=rec_data["description"],
                    component_ids=rec_data["component_ids"],
                    impact_areas=rec_data["impact_areas"],
                    estimated_impact=rec_data["estimated_impact"],
                    effort_estimate=rec_data["effort_estimate"],
                    implementation_plan=rec_data["implementation_plan"],
                    supporting_metrics=rec_data.get("supporting_metrics", []),
                    source=RecommendationSource.ANALYSIS,
                    priority=rec_data["priority"],
                    tags=["cross-component", "auto-generated"]
                )
                
                created_recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error creating recommendation: {e}")
                
        return created_recommendations
        
    async def _analyze_performance_metrics(
        self,
        component_id: str,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze performance metrics and generate recommendations.
        
        Args:
            component_id: Component ID
            analysis: Component analysis data
            
        Returns:
            List of recommendation data
        """
        recommendations = []
        metric_analyses = analysis.get("metric_analyses", {})
        
        # Check response time
        if "perf.response_time" in metric_analyses:
            response_analysis = metric_analyses["perf.response_time"]
            
            # Look for slow response times
            if "statistics" in response_analysis and "mean" in response_analysis["statistics"]:
                mean_response = response_analysis["statistics"]["mean"]
                
                # Check if response time is high
                threshold = 1000  # 1 second (adjust as needed)
                if mean_response > threshold:
                    # Check if there's a trend
                    trend_direction = None
                    trend_strength = 0
                    
                    if "trends" in response_analysis and "direction" in response_analysis["trends"]:
                        trend_direction = response_analysis["trends"]["direction"]
                        trend_strength = response_analysis["trends"].get("strength", 0)
                    
                    # Only recommend if stable or increasing trend
                    if trend_direction != "decreasing" or trend_strength < 0.5:
                        # Create recommendation
                        recommendations.append({
                            "title": f"Optimize response time for {component_id}",
                            "description": (
                                f"The {component_id} component has high average response times of {mean_response:.1f}ms, "
                                f"which is above the recommended threshold of {threshold}ms. "
                                f"{'Response times show an increasing trend, indicating a growing performance issue.' if trend_direction == 'increasing' and trend_strength > 0.5 else ''} "
                                f"Optimizing response times will improve user experience and system responsiveness."
                            ),
                            "impact_areas": ["performance", "user experience"],
                            "estimated_impact": 0.7,
                            "effort_estimate": "medium",
                            "implementation_plan": (
                                f"1. Profile {component_id} to identify bottlenecks\n"
                                f"2. Optimize database queries and IO operations\n"
                                f"3. Consider implementing caching where appropriate\n"
                                f"4. Review and optimize algorithm complexity\n"
                                f"5. Consider parallel processing for independent operations\n"
                                f"6. Measure response times before and after optimization"
                            ),
                            "supporting_metrics": ["perf.response_time"],
                            "priority": "high" if mean_response > threshold * 2 else "medium"
                        })
            
            # Look for response time anomalies
            if "anomalies" in response_analysis and response_analysis["anomalies"].get("has_anomalies", False):
                anomaly_count = response_analysis["anomalies"].get("anomaly_count", 0)
                if anomaly_count > 3:  # Threshold for significant anomalies
                    recommendations.append({
                        "title": f"Investigate response time anomalies in {component_id}",
                        "description": (
                            f"The {component_id} component has {anomaly_count} response time anomalies. "
                            f"These anomalies indicate inconsistent performance that could affect user experience. "
                            f"Investigating and addressing these anomalies will improve system reliability."
                        ),
                        "impact_areas": ["performance", "reliability"],
                        "estimated_impact": 0.6,
                        "effort_estimate": "medium",
                        "implementation_plan": (
                            f"1. Analyze logs during anomaly periods\n"
                            f"2. Check for resource contention or external dependencies\n"
                            f"3. Identify patterns in anomaly occurrences\n"
                            f"4. Implement targeted fixes for identified causes\n"
                            f"5. Add monitoring for early detection of similar issues"
                        ),
                        "supporting_metrics": ["perf.response_time"],
                        "priority": "high" if anomaly_count > 10 else "medium"
                    })
                    
        # Check throughput
        if "perf.throughput" in metric_analyses:
            throughput_analysis = metric_analyses["perf.throughput"]
            
            # Look for declining throughput
            if ("trends" in throughput_analysis and 
                throughput_analysis["trends"].get("direction") == "decreasing" and
                throughput_analysis["trends"].get("strength", 0) > 0.6):
                
                recommendations.append({
                    "title": f"Address declining throughput in {component_id}",
                    "description": (
                        f"The {component_id} component shows a significant decline in throughput. "
                        f"This indicates degrading performance that could affect system capacity. "
                        f"Addressing this trend will maintain system capacity and responsiveness."
                    ),
                    "impact_areas": ["performance", "capacity"],
                    "estimated_impact": 0.75,
                    "effort_estimate": "medium",
                    "implementation_plan": (
                        f"1. Identify bottlenecks through performance profiling\n"
                        f"2. Check for recent changes that may have affected throughput\n"
                        f"3. Optimize resource utilization and concurrency\n"
                        f"4. Consider scaling horizontally if appropriate\n"
                        f"5. Implement performance regression testing"
                    ),
                    "supporting_metrics": ["perf.throughput"],
                    "priority": "high"
                })
                
        return recommendations
        
    async def _analyze_resource_metrics(
        self,
        component_id: str,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze resource metrics and generate recommendations.
        
        Args:
            component_id: Component ID
            analysis: Component analysis data
            
        Returns:
            List of recommendation data
        """
        recommendations = []
        metric_analyses = analysis.get("metric_analyses", {})
        
        # Check CPU usage
        if "res.cpu_usage" in metric_analyses:
            cpu_analysis = metric_analyses["res.cpu_usage"]
            
            # Look for high CPU usage
            if "statistics" in cpu_analysis and "mean" in cpu_analysis["statistics"]:
                mean_cpu = cpu_analysis["statistics"]["mean"]
                
                # Check if CPU usage is high
                if mean_cpu > 80:  # 80% threshold
                    recommendations.append({
                        "title": f"Optimize CPU usage in {component_id}",
                        "description": (
                            f"The {component_id} component has high average CPU usage of {mean_cpu:.1f}%, "
                            f"which could lead to performance degradation or bottlenecks. "
                            f"Optimizing CPU usage will improve system responsiveness and capacity."
                        ),
                        "impact_areas": ["performance", "resource utilization"],
                        "estimated_impact": 0.65,
                        "effort_estimate": "medium",
                        "implementation_plan": (
                            f"1. Profile {component_id} to identify CPU-intensive operations\n"
                            f"2. Optimize algorithms and data structures\n"
                            f"3. Consider parallelizing CPU-intensive tasks\n"
                            f"4. Implement caching for repetitive computations\n"
                            f"5. Review and optimize loops and recursive operations\n"
                            f"6. Consider using dedicated workers for intensive operations"
                        ),
                        "supporting_metrics": ["res.cpu_usage", "perf.response_time"],
                        "priority": "high" if mean_cpu > 90 else "medium"
                    })
                    
        # Check memory usage
        if "res.memory_usage" in metric_analyses:
            memory_analysis = metric_analyses["res.memory_usage"]
            
            # Look for high or growing memory usage
            if "statistics" in memory_analysis and "mean" in memory_analysis["statistics"]:
                mean_memory = memory_analysis["statistics"]["mean"]
                
                # Check if memory usage is high
                # This threshold would depend on the component's expected memory footprint
                memory_threshold = 1000  # 1GB (adjust as needed)
                
                if mean_memory > memory_threshold:
                    # Check if there's a trend
                    trend_direction = None
                    trend_strength = 0
                    
                    if "trends" in memory_analysis and "direction" in memory_analysis["trends"]:
                        trend_direction = memory_analysis["trends"]["direction"]
                        trend_strength = memory_analysis["trends"].get("strength", 0)
                    
                    # Create recommendation for high memory usage
                    recommendations.append({
                        "title": f"Optimize memory usage in {component_id}",
                        "description": (
                            f"The {component_id} component has high average memory usage of {mean_memory:.1f}MB. "
                            f"{'Memory usage shows an increasing trend, which could indicate a memory leak.' if trend_direction == 'increasing' and trend_strength > 0.5 else ''} "
                            f"Optimizing memory usage will improve system stability and resource efficiency."
                        ),
                        "impact_areas": ["performance", "resource utilization", "stability"],
                        "estimated_impact": 0.7,
                        "effort_estimate": "medium" if trend_direction != "increasing" else "high",
                        "implementation_plan": (
                            f"1. Profile memory usage to identify memory-intensive areas\n"
                            f"{'2. Check for memory leaks using appropriate tools\n' if trend_direction == 'increasing' else '2. Review data structures and object lifecycles\n'}"
                            f"3. Optimize object creation and destruction patterns\n"
                            f"4. Consider implementing object pooling for frequently used objects\n"
                            f"5. Review caching strategies and cache sizes\n"
                            f"6. Monitor memory usage after optimization"
                        ),
                        "supporting_metrics": ["res.memory_usage"],
                        "priority": "high" if trend_direction == "increasing" and trend_strength > 0.5 else "medium"
                    })
                    
        # Check token usage (for LLM components)
        if "res.token_usage" in metric_analyses:
            token_analysis = metric_analyses["res.token_usage"]
            
            # Check if this is an LLM-related component
            is_llm_component = any(x in component_id.lower() for x in ["llm", "rhetor", "language"])
            
            if is_llm_component and "statistics" in token_analysis and "sum" in token_analysis["statistics"]:
                token_sum = token_analysis["statistics"]["sum"]
                
                # Check for high token usage
                # This would depend on expected usage and budgetary constraints
                if token_sum > 100000:  # Adjust as needed
                    recommendations.append({
                        "title": f"Optimize LLM token usage in {component_id}",
                        "description": (
                            f"The {component_id} component has high token usage of {token_sum} tokens. "
                            f"Optimizing token usage will reduce operational costs and improve efficiency."
                        ),
                        "impact_areas": ["cost", "efficiency"],
                        "estimated_impact": 0.6,
                        "effort_estimate": "medium",
                        "implementation_plan": (
                            f"1. Analyze patterns of token usage\n"
                            f"2. Optimize prompt engineering to reduce token consumption\n"
                            f"3. Implement tiered model selection based on task complexity\n"
                            f"4. Consider caching common responses\n"
                            f"5. Use embeddings and retrieval for context compression\n"
                            f"6. Monitor token usage after optimization"
                        ),
                        "supporting_metrics": ["res.token_usage"],
                        "priority": "high" if token_sum > 1000000 else "medium"
                    })
        
        return recommendations
        
    async def _analyze_error_metrics(
        self,
        component_id: str,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze error metrics and generate recommendations.
        
        Args:
            component_id: Component ID
            analysis: Component analysis data
            
        Returns:
            List of recommendation data
        """
        recommendations = []
        error_analysis = analysis.get("error_analysis")
        
        if not error_analysis:
            return recommendations
            
        # Check for high error counts
        if "statistics" in error_analysis and "sum" in error_analysis["statistics"]:
            error_sum = error_analysis["statistics"]["sum"]
            
            # Check if error count is high
            if error_sum > 100:  # Threshold for significant errors
                # Check if there's a trend
                trend_direction = None
                trend_strength = 0
                
                if "trends" in error_analysis and "direction" in error_analysis["trends"]:
                    trend_direction = error_analysis["trends"]["direction"]
                    trend_strength = error_analysis["trends"].get("strength", 0)
                
                # Create recommendation for high error count
                recommendations.append({
                    "title": f"Address high error rate in {component_id}",
                    "description": (
                        f"The {component_id} component has a high error count of {error_sum} errors. "
                        f"{'Error count shows an increasing trend, indicating a growing reliability issue.' if trend_direction == 'increasing' and trend_strength > 0.5 else ''} "
                        f"Addressing these errors will improve system reliability and user experience."
                    ),
                    "impact_areas": ["reliability", "user experience"],
                    "estimated_impact": 0.8,
                    "effort_estimate": "medium",
                    "implementation_plan": (
                        f"1. Analyze error logs to identify patterns and root causes\n"
                        f"2. Prioritize errors by frequency and impact\n"
                        f"3. Implement robust error handling for high-impact errors\n"
                        f"4. Add monitoring for early detection of error spikes\n"
                        f"5. Consider adding circuit breakers for external dependencies\n"
                        f"6. Verify fixes with targeted testing"
                    ),
                    "supporting_metrics": ["ops.error_count"],
                    "priority": "critical" if error_sum > 1000 or (trend_direction == "increasing" and trend_strength > 0.7) else "high"
                })
                
        # Check for error patterns
        if "patterns" in error_analysis and error_analysis["patterns"].get("has_pattern", False):
            pattern_type = error_analysis["patterns"].get("pattern_type")
            
            if pattern_type == "cyclic" or pattern_type == "seasonal":
                recommendations.append({
                    "title": f"Investigate {pattern_type} error pattern in {component_id}",
                    "description": (
                        f"The {component_id} component shows a {pattern_type} pattern in error occurrences. "
                        f"This suggests a recurring issue that may be related to scheduled tasks, "
                        f"load patterns, or external dependencies. Addressing this pattern will "
                        f"improve system reliability."
                    ),
                    "impact_areas": ["reliability", "predictability"],
                    "estimated_impact": 0.7,
                    "effort_estimate": "medium",
                    "implementation_plan": (
                        f"1. Correlate error patterns with system events and schedules\n"
                        f"2. Identify potential causes of the {pattern_type} pattern\n"
                        f"3. Implement monitoring specifically around pattern peaks\n"
                        f"4. Add resources or optimize processing during peak error periods\n"
                        f"5. Consider implementing retries with exponential backoff\n"
                        f"6. Verify resolution with extended monitoring"
                    ),
                    "supporting_metrics": ["ops.error_count"],
                    "priority": "high"
                })
                
        return recommendations
        
    async def _analyze_anomalies(
        self,
        component_id: str,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze anomalies and generate recommendations.
        
        Args:
            component_id: Component ID
            analysis: Component analysis data
            
        Returns:
            List of recommendation data
        """
        recommendations = []
        
        # Check if component has anomalies
        if not analysis.get("has_anomalies", False):
            return recommendations
            
        anomaly_count = analysis.get("anomaly_count", 0)
        
        # Only generate recommendation for significant anomalies
        if anomaly_count < 5:
            return recommendations
            
        # Identify metrics with anomalies
        metrics_with_anomalies = []
        metric_analyses = analysis.get("metric_analyses", {})
        
        for metric_id, metric_analysis in metric_analyses.items():
            if "anomalies" in metric_analysis and metric_analysis["anomalies"].get("has_anomalies", False):
                metrics_with_anomalies.append(metric_id)
                
        if not metrics_with_anomalies:
            return recommendations
            
        # Create recommendation for anomalies
        recommendations.append({
            "title": f"Investigate performance anomalies in {component_id}",
            "description": (
                f"The {component_id} component has {anomaly_count} anomalies across "
                f"{len(metrics_with_anomalies)} metrics: {', '.join(metrics_with_anomalies)}. "
                f"These anomalies indicate inconsistent behavior that could affect "
                f"system reliability and user experience. Investigating and addressing "
                f"these anomalies will improve system stability."
            ),
            "impact_areas": ["reliability", "performance", "user experience"],
            "estimated_impact": 0.6,
            "effort_estimate": "medium",
            "implementation_plan": (
                f"1. Analyze logs during anomaly periods\n"
                f"2. Correlate anomalies across metrics to identify patterns\n"
                f"3. Check for environmental factors (load, dependencies, etc.)\n"
                f"4. Identify specific operations or code paths related to anomalies\n"
                f"5. Implement targeted fixes for identified causes\n"
                f"6. Add monitoring for early detection of similar anomalies"
            ),
            "supporting_metrics": metrics_with_anomalies,
            "priority": "high" if anomaly_count > 20 else "medium",
            "source": "anomaly"
        })
        
        return recommendations
        
    async def _generate_correlation_recommendation(
        self,
        component1: str,
        component2: str,
        metric_id: str,
        correlation: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a recommendation based on component correlation.
        
        Args:
            component1: First component ID
            component2: Second component ID
            metric_id: Metric ID
            correlation: Correlation analysis
            
        Returns:
            Recommendation data or None
        """
        # Get the strongest correlation
        strong_correlations = correlation.get("strong_correlations", [])
        if not strong_correlations:
            return None
            
        correlation_data = strong_correlations[0]
        corr_value = correlation_data.get("correlation", 0)
        corr_direction = correlation_data.get("direction", "unknown")
        
        # Generate recommendation based on correlation
        if corr_direction == "positive" and corr_value > 0.8:
            # Strong positive correlation - potential for optimization
            return {
                "title": f"Optimize interaction between {component1} and {component2}",
                "description": (
                    f"There is a strong positive correlation ({corr_value:.2f}) between "
                    f"{component1} and {component2} for {metric_id}. "
                    f"This indicates that these components are tightly coupled and "
                    f"may benefit from coordinated optimization or load balancing."
                ),
                "component_ids": [component1, component2],
                "impact_areas": ["performance", "efficiency"],
                "estimated_impact": 0.7,
                "effort_estimate": "medium",
                "implementation_plan": (
                    f"1. Analyze interaction patterns between {component1} and {component2}\n"
                    f"2. Identify potential bottlenecks in their communication\n"
                    f"3. Consider implementing caching or buffering between components\n"
                    f"4. Optimize data transfer formats and frequencies\n"
                    f"5. Implement coordinated scaling strategies\n"
                    f"6. Monitor performance after optimization"
                ),
                "supporting_metrics": [metric_id],
                "priority": "high" if corr_value > 0.9 else "medium"
            }
        elif corr_direction == "negative" and corr_value < -0.8:
            # Strong negative correlation - potential for resource competition
            return {
                "title": f"Address resource competition between {component1} and {component2}",
                "description": (
                    f"There is a strong negative correlation ({corr_value:.2f}) between "
                    f"{component1} and {component2} for {metric_id}. "
                    f"This suggests resource competition or conflicting operations "
                    f"that may be degrading overall system performance."
                ),
                "component_ids": [component1, component2],
                "impact_areas": ["performance", "resource utilization"],
                "estimated_impact": 0.75,
                "effort_estimate": "medium",
                "implementation_plan": (
                    f"1. Identify shared resources used by both components\n"
                    f"2. Analyze resource usage patterns to confirm competition\n"
                    f"3. Consider separating resources or implementing dedicated resources\n"
                    f"4. Implement resource scheduling or prioritization\n"
                    f"5. Monitor resource usage patterns after changes\n"
                    f"6. Verify performance improvement in both components"
                ),
                "supporting_metrics": [metric_id],
                "priority": "high" if corr_value < -0.9 else "medium"
            }
            
        return None
        
    async def _analyze_system_bottlenecks(
        self,
        system_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze system-wide bottlenecks and generate recommendations.
        
        Args:
            system_analysis: System performance analysis
            
        Returns:
            List of recommendation data
        """
        recommendations = []
        
        # Check system-wide metrics
        system_metrics = system_analysis.get("system_metrics", {})
        
        # Check for high average response time
        avg_response_time = system_metrics.get("avg_response_time")
        if avg_response_time and avg_response_time > 1000:  # 1 second
            # Get components with highest response times
            slow_components = []
            component_analyses = system_analysis.get("component_analyses", {})
            
            for comp_id, comp_analysis in component_analyses.items():
                if "overall_health" in comp_analysis and comp_analysis["overall_health"].get("score", 100) < 70:
                    slow_components.append(comp_id)
                    
            if slow_components:
                recommendations.append({
                    "title": "Address system-wide response time bottlenecks",
                    "description": (
                        f"System-wide average response time is high ({avg_response_time:.1f}ms), "
                        f"affecting overall system performance. Key components contributing to "
                        f"this issue: {', '.join(slow_components[:3])}. Optimizing these components "
                        f"will improve system-wide responsiveness."
                    ),
                    "component_ids": slow_components[:3],  # Focus on top 3 problematic components
                    "impact_areas": ["performance", "user experience"],
                    "estimated_impact": 0.8,
                    "effort_estimate": "high",
                    "implementation_plan": (
                        f"1. Conduct system-wide performance profiling\n"
                        f"2. Focus optimization efforts on identified slow components\n"
                        f"3. Implement performance benchmarks for critical paths\n"
                        f"4. Consider architectural changes to reduce dependencies\n"
                        f"5. Implement caching strategies across components\n"
                        f"6. Monitor system-wide response times after optimization"
                    ),
                    "supporting_metrics": ["perf.response_time"],
                    "priority": "high" if avg_response_time > 2000 else "medium"
                })
                
        # Check for high error rates
        total_errors = system_metrics.get("total_errors", 0)
        if total_errors > 1000:  # Significant error count
            # Get components with highest error counts
            error_components = []
            component_analyses = system_analysis.get("component_analyses", {})
            
            for comp_id, comp_analysis in component_analyses.items():
                metrics_analyzed = comp_analysis.get("metrics_analyzed", [])
                if "ops.error_count" in metrics_analyzed:
                    error_components.append(comp_id)
                    
            if error_components:
                recommendations.append({
                    "title": "Address system-wide reliability issues",
                    "description": (
                        f"System-wide error count is high ({total_errors} errors), "
                        f"affecting overall system reliability. Components with error metrics: "
                        f"{', '.join(error_components)}. Addressing these errors will improve "
                        f"system stability and user experience."
                    ),
                    "component_ids": error_components,
                    "impact_areas": ["reliability", "user experience"],
                    "estimated_impact": 0.85,
                    "effort_estimate": "high",
                    "implementation_plan": (
                        f"1. Conduct system-wide error log analysis\n"
                        f"2. Categorize errors by type, frequency, and impact\n"
                        f"3. Prioritize error resolution based on user impact\n"
                        f"4. Implement improved error handling across components\n"
                        f"5. Add system-wide monitoring for error patterns\n"
                        f"6. Conduct targeted testing for error scenarios"
                    ),
                    "supporting_metrics": ["ops.error_count"],
                    "priority": "critical" if total_errors > 5000 else "high"
                })
                
        return recommendations
        
    async def _generate_periodic_recommendations(self) -> None:
        """Run periodic recommendation generation as a background task."""
        try:
            # Initial delay to allow system to stabilize
            await asyncio.sleep(300)  # 5 minutes
            
            while True:
                try:
                    logger.info("Running periodic recommendation generation")
                    
                    # Get all component IDs
                    # This would normally be fetched from Hermes service registry
                    # For now, we'll use a simple set
                    component_ids = ["rhetor", "engram", "terma", "athena"]
                    
                    # Generate recommendations for each component
                    for component_id in component_ids:
                        try:
                            recommendations = await self.generate_recommendations_from_analysis(
                                component_id=component_id,
                                time_window="7d"
                            )
                            
                            logger.info(f"Generated {len(recommendations)} recommendations for {component_id}")
                            
                        except Exception as e:
                            logger.error(f"Error generating recommendations for {component_id}: {e}")
                            
                    # Generate cross-component recommendations
                    try:
                        cross_recommendations = await self.generate_cross_component_recommendations(
                            time_window="7d"
                        )
                        
                        logger.info(f"Generated {len(cross_recommendations)} cross-component recommendations")
                        
                    except Exception as e:
                        logger.error(f"Error generating cross-component recommendations: {e}")
                        
                    # Sleep until next run (daily)
                    logger.info("Completed periodic recommendation generation")
                    await asyncio.sleep(86400)  # 24 hours
                    
                except Exception as e:
                    logger.error(f"Error in periodic recommendation generation: {e}")
                    await asyncio.sleep(3600)  # 1 hour before retry
                    
        except asyncio.CancelledError:
            logger.info("Periodic recommendation generation task cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in recommendation generation task: {e}")
            
    async def _load_recommendations(self) -> bool:
        """
        Load recommendations from storage.
        
        Returns:
            True if successful
        """
        try:
            if self.database:
                # Load recommendations from database
                recommendations_data = await self.database.get_all_recommendations()
                self.recommendations = {}
                
                for rec_data in recommendations_data:
                    rec_id = rec_data.get('id')
                    if rec_id:
                        self.recommendations[rec_id] = rec_data
                        
                logger.info(f"Loaded {len(self.recommendations)} recommendations from database")
            else:
                # Fallback to empty data if no database
                self.recommendations = {}
                logger.warning("No database available, starting with empty recommendations")
                
            return True
            
        except Exception as e:
            logger.error(f"Error loading recommendations: {e}")
            # Fallback to empty data on error
            self.recommendations = {}
            return False
        
    async def _save_recommendations(self) -> bool:
        """
        Save recommendations to storage.
        
        Returns:
            True if successful
        """
        try:
            if self.database:
                # Save recommendations to database
                for rec_id, recommendation in self.recommendations.items():
                    await self.database.save_recommendation(
                        recommendation_id=rec_id,
                        title=recommendation.get('title', ''),
                        description=recommendation.get('description', ''),
                        priority=recommendation.get('priority', 'medium'),
                        status=recommendation.get('status', 'proposed'),
                        source=recommendation.get('source', 'analysis'),
                        context=recommendation,
                        created_at=recommendation.get('created_at'),
                        updated_at=recommendation.get('updated_at')
                    )
                    
                logger.debug(f"Saved {len(self.recommendations)} recommendations to database")
            else:
                logger.warning(f"No database available, cannot save {len(self.recommendations)} recommendations")
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving recommendations: {e}")
            return False

# Global singleton instance
_recommendation_system = RecommendationSystem()

async def get_recommendation_system() -> RecommendationSystem:
    """
    Get the global recommendation system instance.
    
    Returns:
        RecommendationSystem instance
    """
    if not _recommendation_system.is_initialized:
        await _recommendation_system.initialize()
    return _recommendation_system