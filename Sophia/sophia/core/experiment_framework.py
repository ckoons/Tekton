"""
Experiment Framework for Sophia.

This module implements a framework for designing, running, and analyzing experiments.
"""

import os
import json
import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum

from .metrics_engine import get_metrics_engine
from .analysis_engine import get_analysis_engine
from sophia.models.experiment import ExperimentStatus, ExperimentType

# Configure logging
logger = logging.getLogger("sophia.experiment_framework")

class ExperimentRunner:
    """Handles the execution of experiments."""
    
    def __init__(self, experiment_config, metrics_engine, analysis_engine):
        """
        Initialize an experiment runner.
        
        Args:
            experiment_config: Configuration for the experiment
            metrics_engine: Metrics engine instance
            analysis_engine: Analysis engine instance
        """
        self.config = experiment_config
        self.metrics_engine = metrics_engine
        self.analysis_engine = analysis_engine
        self.results = {}
        self.is_running = False
        self.start_time = None
        self.end_time = None
        
    async def run(self):
        """
        Execute the experiment based on its type.
        
        Returns:
            Experiment results
        """
        if self.is_running:
            logger.warning(f"Experiment {self.config['id']} is already running")
            return False
            
        self.is_running = True
        self.start_time = datetime.utcnow()
        
        try:
            # Update experiment status
            self.config["status"] = ExperimentStatus.RUNNING
            self.config["actual_start_time"] = self.start_time.isoformat() + "Z"
            
            logger.info(f"Starting experiment {self.config['id']} of type {self.config['experiment_type']}")
            
            # Execute based on experiment type
            if self.config["experiment_type"] == ExperimentType.A_B_TEST:
                self.results = await self._run_ab_test()
            elif self.config["experiment_type"] == ExperimentType.MULTIVARIATE:
                self.results = await self._run_multivariate_test()
            elif self.config["experiment_type"] == ExperimentType.SHADOW_MODE:
                self.results = await self._run_shadow_mode_test()
            elif self.config["experiment_type"] == ExperimentType.CANARY:
                self.results = await self._run_canary_test()
            elif self.config["experiment_type"] == ExperimentType.PARAMETER_TUNING:
                self.results = await self._run_parameter_tuning()
            elif self.config["experiment_type"] == ExperimentType.BEFORE_AFTER:
                self.results = await self._run_before_after_test()
            elif self.config["experiment_type"] == ExperimentType.BASELINE_COMPARISON:
                self.results = await self._run_baseline_comparison()
            else:
                logger.error(f"Unsupported experiment type: {self.config['experiment_type']}")
                self.config["status"] = ExperimentStatus.FAILED
                self.is_running = False
                return False
                
            # Update experiment status
            self.end_time = datetime.utcnow()
            self.config["actual_end_time"] = self.end_time.isoformat() + "Z"
            self.config["status"] = ExperimentStatus.COMPLETED
            self.is_running = False
            
            logger.info(f"Experiment {self.config['id']} completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error running experiment {self.config['id']}: {e}")
            self.config["status"] = ExperimentStatus.FAILED
            self.is_running = False
            return False
            
    async def _run_ab_test(self):
        """
        Run an A/B test experiment.
        
        Returns:
            Experiment results
        """
        logger.info(f"Running A/B test for experiment {self.config['id']}")
        
        # Get experiment parameters
        parameters = self.config["parameters"]
        metrics = self.config["metrics"]
        target_components = self.config["target_components"]
        sample_size = self.config.get("sample_size", 1000)
        
        # Validate parameters
        if "control" not in parameters or "treatment" not in parameters:
            raise ValueError("A/B test requires 'control' and 'treatment' parameters")
            
        # Collect baseline metrics for control
        control_metrics = await self._collect_metrics(
            metrics=metrics,
            components=target_components,
            condition=parameters["control"],
            sample_size=sample_size // 2
        )
        
        # Collect metrics for treatment
        treatment_metrics = await self._collect_metrics(
            metrics=metrics,
            components=target_components,
            condition=parameters["treatment"],
            sample_size=sample_size // 2
        )
        
        # Compare metrics
        comparison = await self._compare_metrics(control_metrics, treatment_metrics)
        
        # Calculate confidence level
        confidence_level = await self._calculate_confidence_level(comparison)
        
        # Determine outcome and recommendation
        conclusion, recommended_action = await self._determine_outcome(comparison, confidence_level)
        
        # Return results
        return {
            "control": control_metrics,
            "treatment": treatment_metrics,
            "comparison": comparison,
            "confidence_level": confidence_level,
            "conclusion": conclusion,
            "recommended_action": recommended_action
        }
        
    async def _run_multivariate_test(self):
        """
        Run a multivariate test experiment.
        
        Returns:
            Experiment results
        """
        logger.info(f"Running multivariate test for experiment {self.config['id']}")
        
        # Get experiment parameters
        parameters = self.config["parameters"]
        metrics = self.config["metrics"]
        target_components = self.config["target_components"]
        sample_size = self.config.get("sample_size", 1000)
        
        # Validate parameters
        if "variables" not in parameters or "combinations" not in parameters:
            raise ValueError("Multivariate test requires 'variables' and 'combinations' parameters")
            
        # Collect metrics for each combination
        combination_metrics = {}
        samples_per_combination = sample_size // len(parameters["combinations"])
        
        for combo_name, combo_values in parameters["combinations"].items():
            combination_metrics[combo_name] = await self._collect_metrics(
                metrics=metrics,
                components=target_components,
                condition=combo_values,
                sample_size=samples_per_combination
            )
            
        # Compare all combinations
        comparison = await self._compare_multivariate_metrics(combination_metrics)
        
        # Identify best combination
        best_combination, confidence_levels = await self._identify_best_combination(comparison)
        
        # Determine outcome and recommendation
        conclusion, recommended_action = await self._determine_multivariate_outcome(
            best_combination, confidence_levels
        )
        
        # Return results
        return {
            "combinations": combination_metrics,
            "comparison": comparison,
            "best_combination": best_combination,
            "confidence_levels": confidence_levels,
            "conclusion": conclusion,
            "recommended_action": recommended_action
        }
        
    async def _run_shadow_mode_test(self):
        """
        Run a shadow mode test experiment.
        
        Returns:
            Experiment results
        """
        logger.info(f"Running shadow mode test for experiment {self.config['id']}")
        
        # Get experiment parameters
        parameters = self.config["parameters"]
        metrics = self.config["metrics"]
        target_components = self.config["target_components"]
        duration = self.config.get("duration", "24h")
        
        # Validate parameters
        if "production" not in parameters or "shadow" not in parameters:
            raise ValueError("Shadow mode test requires 'production' and 'shadow' parameters")
            
        # Parse duration
        duration_seconds = self._parse_duration(duration)
        
        # Run production and shadow systems in parallel
        production_metrics = await self._collect_metrics_for_duration(
            metrics=metrics,
            components=target_components,
            condition=parameters["production"],
            duration_seconds=duration_seconds
        )
        
        shadow_metrics = await self._collect_metrics_for_duration(
            metrics=metrics,
            components=target_components,
            condition=parameters["shadow"],
            duration_seconds=duration_seconds
        )
        
        # Compare metrics
        comparison = await self._compare_metrics(production_metrics, shadow_metrics)
        
        # Analyze differences
        differences = await self._analyze_shadow_differences(comparison)
        
        # Identify risks and benefits
        risks, benefits = await self._identify_shadow_risks_benefits(differences)
        
        # Determine readiness for production
        is_ready, confidence_level = await self._determine_shadow_readiness(differences, risks)
        
        # Return results
        return {
            "production": production_metrics,
            "shadow": shadow_metrics,
            "comparison": comparison,
            "differences": differences,
            "risks": risks,
            "benefits": benefits,
            "is_ready_for_production": is_ready,
            "confidence_level": confidence_level,
            "conclusion": "Ready for production" if is_ready else "Not ready for production",
            "recommended_action": "Deploy to production" if is_ready else "Continue development"
        }
        
    async def _run_canary_test(self):
        """
        Run a canary test experiment.
        
        Returns:
            Experiment results
        """
        logger.info(f"Running canary test for experiment {self.config['id']}")
        
        # Get experiment parameters
        parameters = self.config["parameters"]
        metrics = self.config["metrics"]
        target_components = self.config["target_components"]
        
        # Validate parameters
        if "stable" not in parameters or "canary" not in parameters:
            raise ValueError("Canary test requires 'stable' and 'canary' parameters")
            
        if "traffic_percentage" not in parameters:
            parameters["traffic_percentage"] = 10  # Default to 10% traffic
            
        if "rollout_steps" not in parameters:
            parameters["rollout_steps"] = [10, 25, 50, 100]  # Default rollout steps
            
        # Run initial canary with initial traffic percentage
        results_by_step = {}
        current_percentage = parameters["traffic_percentage"]
        
        for step in parameters["rollout_steps"]:
            # Update traffic percentage
            current_percentage = step
            
            # Collect metrics for stable and canary
            stable_metrics = await self._collect_metrics_with_traffic_split(
                metrics=metrics,
                components=target_components,
                condition=parameters["stable"],
                traffic_percentage=100 - current_percentage
            )
            
            canary_metrics = await self._collect_metrics_with_traffic_split(
                metrics=metrics,
                components=target_components,
                condition=parameters["canary"],
                traffic_percentage=current_percentage
            )
            
            # Compare metrics
            comparison = await self._compare_metrics(stable_metrics, canary_metrics)
            
            # Check for errors or degradation
            has_errors, has_degradation = await self._check_canary_health(canary_metrics, comparison)
            
            # Store results for this step
            results_by_step[str(step)] = {
                "traffic_percentage": step,
                "stable_metrics": stable_metrics,
                "canary_metrics": canary_metrics,
                "comparison": comparison,
                "has_errors": has_errors,
                "has_degradation": has_degradation
            }
            
            # Stop if there are errors or significant degradation
            if has_errors or has_degradation:
                logger.warning(f"Stopping canary test at {step}% due to issues")
                break
                
        # Determine overall canary result
        is_successful = not any(step_result.get("has_errors") or step_result.get("has_degradation") 
                               for step_result in results_by_step.values())
                               
        # Return results
        return {
            "steps": results_by_step,
            "is_successful": is_successful,
            "final_traffic_percentage": current_percentage,
            "conclusion": "Canary successful" if is_successful else "Canary failed",
            "recommended_action": "Deploy to all traffic" if is_successful else "Rollback to stable version"
        }
        
    async def _run_parameter_tuning(self):
        """
        Run a parameter tuning experiment.
        
        Returns:
            Experiment results
        """
        logger.info(f"Running parameter tuning for experiment {self.config['id']}")
        
        # Get experiment parameters
        parameters = self.config["parameters"]
        metrics = self.config["metrics"]
        target_components = self.config["target_components"]
        
        # Validate parameters
        if "parameters_to_tune" not in parameters:
            raise ValueError("Parameter tuning requires 'parameters_to_tune' parameter")
            
        # Generate parameter combinations
        parameter_combinations = await self._generate_parameter_combinations(
            parameters["parameters_to_tune"]
        )
        
        # Run tests for each combination
        results_by_combination = {}
        
        for i, combination in enumerate(parameter_combinations):
            # Generate a unique name for this combination
            combo_name = f"combination_{i}"
            
            # Collect metrics for this combination
            combo_metrics = await self._collect_metrics(
                metrics=metrics,
                components=target_components,
                condition=combination,
                sample_size=parameters.get("samples_per_combination", 100)
            )
            
            # Store results
            results_by_combination[combo_name] = {
                "parameters": combination,
                "metrics": combo_metrics
            }
            
        # Analyze results and find optimal parameters
        optimal_combination, performance_by_metric = await self._find_optimal_parameters(
            results_by_combination, metrics
        )
        
        # Return results
        return {
            "combinations_tested": len(parameter_combinations),
            "results_by_combination": results_by_combination,
            "optimal_combination": optimal_combination,
            "performance_by_metric": performance_by_metric,
            "conclusion": f"Optimal parameters identified: {optimal_combination}",
            "recommended_action": f"Update configuration with optimal parameters"
        }
        
    async def _run_before_after_test(self):
        """
        Run a before/after test experiment.
        
        Returns:
            Experiment results
        """
        logger.info(f"Running before/after test for experiment {self.config['id']}")
        
        # Get experiment parameters
        parameters = self.config["parameters"]
        metrics = self.config["metrics"]
        target_components = self.config["target_components"]
        duration = self.config.get("duration", "24h")
        
        # Validate parameters
        if "before" not in parameters or "after" not in parameters:
            raise ValueError("Before/after test requires 'before' and 'after' parameters")
            
        # Parse duration
        duration_seconds = self._parse_duration(duration)
        
        # Collect metrics for before state
        before_metrics = await self._collect_metrics_for_duration(
            metrics=metrics,
            components=target_components,
            condition=parameters["before"],
            duration_seconds=duration_seconds
        )
        
        # Apply change
        await self._apply_change(parameters["after"])
        
        # Collect metrics for after state
        after_metrics = await self._collect_metrics_for_duration(
            metrics=metrics,
            components=target_components,
            condition=parameters["after"],
            duration_seconds=duration_seconds
        )
        
        # Compare metrics
        comparison = await self._compare_metrics(before_metrics, after_metrics)
        
        # Calculate improvement and degradation
        improvements, degradations = await self._calculate_improvements_degradations(comparison)
        
        # Calculate overall impact
        impact_score = await self._calculate_impact_score(improvements, degradations)
        
        # Determine outcome
        is_successful = impact_score > 0
        
        # Return results
        return {
            "before": before_metrics,
            "after": after_metrics,
            "comparison": comparison,
            "improvements": improvements,
            "degradations": degradations,
            "impact_score": impact_score,
            "is_successful": is_successful,
            "conclusion": "Change improved system" if is_successful else "Change degraded system",
            "recommended_action": "Keep change" if is_successful else "Revert change"
        }
        
    async def _run_baseline_comparison(self):
        """
        Run a baseline comparison experiment.
        
        Returns:
            Experiment results
        """
        logger.info(f"Running baseline comparison for experiment {self.config['id']}")
        
        # Get experiment parameters
        parameters = self.config["parameters"]
        metrics = self.config["metrics"]
        target_components = self.config["target_components"]
        
        # Validate parameters
        if "baseline" not in parameters or "candidates" not in parameters:
            raise ValueError("Baseline comparison requires 'baseline' and 'candidates' parameters")
            
        # Collect metrics for baseline
        baseline_metrics = await self._collect_metrics(
            metrics=metrics,
            components=target_components,
            condition=parameters["baseline"],
            sample_size=parameters.get("samples_per_candidate", 100)
        )
        
        # Collect metrics for each candidate
        candidates_metrics = {}
        
        for candidate_name, candidate_config in parameters["candidates"].items():
            candidates_metrics[candidate_name] = await self._collect_metrics(
                metrics=metrics,
                components=target_components,
                condition=candidate_config,
                sample_size=parameters.get("samples_per_candidate", 100)
            )
            
        # Compare candidates to baseline
        comparisons = {}
        
        for candidate_name, candidate_metrics in candidates_metrics.items():
            comparisons[candidate_name] = await self._compare_metrics(
                baseline_metrics, candidate_metrics
            )
            
        # Rank candidates
        ranked_candidates = await self._rank_candidates(comparisons)
        
        # Identify best candidate
        best_candidate = ranked_candidates[0] if ranked_candidates else None
        
        # Return results
        return {
            "baseline": baseline_metrics,
            "candidates": candidates_metrics,
            "comparisons": comparisons,
            "ranked_candidates": ranked_candidates,
            "best_candidate": best_candidate,
            "conclusion": f"Best candidate: {best_candidate}" if best_candidate else "No candidates outperformed baseline",
            "recommended_action": f"Adopt {best_candidate}" if best_candidate else "Keep baseline"
        }
        
    async def _collect_metrics(self, metrics, components, condition, sample_size):
        """
        Collect metrics for an experiment condition.
        
        Args:
            metrics: List of metrics to collect
            components: Target components
            condition: Experiment condition
            sample_size: Number of samples to collect
            
        Returns:
            Collected metrics
        """
        # This would normally interact with the actual components
        # For now, we simulate metric collection
        logger.info(f"Collecting {sample_size} samples for condition: {condition}")
        
        collected_metrics = {}
        
        for metric_id in metrics:
            # Use the metrics engine to query recent metrics
            metric_data = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=components,
                limit=sample_size,
                context={"condition": condition}
            )
            
            collected_metrics[metric_id] = metric_data
            
        return collected_metrics
        
    async def _collect_metrics_for_duration(self, metrics, components, condition, duration_seconds):
        """
        Collect metrics for a specific duration.
        
        Args:
            metrics: List of metrics to collect
            components: Target components
            condition: Experiment condition
            duration_seconds: Duration in seconds
            
        Returns:
            Collected metrics
        """
        # Calculate start and end times
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=duration_seconds)
        
        # Format as ISO strings
        start_time_iso = start_time.isoformat() + "Z"
        end_time_iso = end_time.isoformat() + "Z"
        
        logger.info(f"Collecting metrics from {start_time_iso} to {end_time_iso} for condition: {condition}")
        
        collected_metrics = {}
        
        for metric_id in metrics:
            # Use the metrics engine to query metrics for the time period
            metric_data = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=components,
                start_time=start_time_iso,
                end_time=end_time_iso,
                context={"condition": condition}
            )
            
            collected_metrics[metric_id] = metric_data
            
        return collected_metrics
        
    async def _collect_metrics_with_traffic_split(self, metrics, components, condition, traffic_percentage):
        """
        Collect metrics with traffic split.
        
        Args:
            metrics: List of metrics to collect
            components: Target components
            condition: Experiment condition
            traffic_percentage: Percentage of traffic to collect
            
        Returns:
            Collected metrics
        """
        # This would normally involve a traffic splitting mechanism
        # For now, we simulate metric collection with traffic percentage
        logger.info(f"Collecting metrics with {traffic_percentage}% traffic for condition: {condition}")
        
        collected_metrics = {}
        
        for metric_id in metrics:
            # Use the metrics engine to query metrics with traffic context
            metric_data = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=components,
                limit=100,  # Arbitrary limit
                context={
                    "condition": condition,
                    "traffic_percentage": traffic_percentage
                }
            )
            
            collected_metrics[metric_id] = metric_data
            
        return collected_metrics
        
    async def _compare_metrics(self, baseline_metrics, comparison_metrics):
        """
        Compare two sets of metrics.
        
        Args:
            baseline_metrics: Baseline metrics
            comparison_metrics: Comparison metrics
            
        Returns:
            Comparison results
        """
        # This would normally involve statistical comparison
        # For now, we simulate comparison
        logger.info("Comparing metrics")
        
        comparison_results = {}
        
        for metric_id, baseline_data in baseline_metrics.items():
            if metric_id not in comparison_metrics:
                continue
                
            comparison_data = comparison_metrics[metric_id]
            
            # Use the analysis engine to compare metrics
            comparison_results[metric_id] = await self.analysis_engine.compare_metric_sets(
                baseline_data, comparison_data
            )
            
        return comparison_results
        
    async def _compare_multivariate_metrics(self, combination_metrics):
        """
        Compare metrics from multiple combinations.
        
        Args:
            combination_metrics: Metrics for each combination
            
        Returns:
            Comparison results
        """
        # This would normally involve comparing all combinations
        # For now, we simulate multivariate comparison
        logger.info("Comparing multivariate metrics")
        
        comparison_results = {}
        
        # Get a list of all metric IDs
        all_metric_ids = set()
        for combo_metrics in combination_metrics.values():
            all_metric_ids.update(combo_metrics.keys())
            
        # Compare each combination against all others for each metric
        for metric_id in all_metric_ids:
            metric_comparisons = {}
            
            for combo1_name, combo1_metrics in combination_metrics.items():
                if metric_id not in combo1_metrics:
                    continue
                    
                combo_comparison = {}
                
                for combo2_name, combo2_metrics in combination_metrics.items():
                    if combo1_name == combo2_name or metric_id not in combo2_metrics:
                        continue
                        
                    # Use the analysis engine to compare metrics
                    combo_comparison[combo2_name] = await self.analysis_engine.compare_metric_sets(
                        combo1_metrics[metric_id], combo2_metrics[metric_id]
                    )
                    
                metric_comparisons[combo1_name] = combo_comparison
                
            comparison_results[metric_id] = metric_comparisons
            
        return comparison_results
        
    async def _calculate_confidence_level(self, comparison):
        """
        Calculate the confidence level for experiment results.
        
        Args:
            comparison: Comparison results
            
        Returns:
            Confidence level (0-1)
        """
        # This would normally involve statistical analysis
        # For now, we simulate confidence calculation
        logger.info("Calculating confidence level")
        
        # Use the analysis engine to calculate confidence
        confidence_levels = []
        
        for metric_id, comparison_data in comparison.items():
            confidence = comparison_data.get("confidence", 0.5)
            confidence_levels.append(confidence)
            
        # Average confidence across all metrics
        if confidence_levels:
            return sum(confidence_levels) / len(confidence_levels)
        else:
            return 0.0
            
    async def _determine_outcome(self, comparison, confidence_level):
        """
        Determine the outcome of an experiment.
        
        Args:
            comparison: Comparison results
            confidence_level: Confidence level
            
        Returns:
            Conclusion and recommended action
        """
        # This would normally involve analysis of the comparison
        # For now, we simulate outcome determination
        logger.info("Determining experiment outcome")
        
        # Count improvements and degradations
        improvements = 0
        degradations = 0
        
        for metric_id, comparison_data in comparison.items():
            if comparison_data.get("percent_change", 0) > 0:
                improvements += 1
            elif comparison_data.get("percent_change", 0) < 0:
                degradations += 1
                
        # Determine if treatment is better than control
        is_better = improvements > degradations
        
        # Determine conclusion
        if confidence_level >= 0.95:
            conclusion = "Treatment is significantly better than control" if is_better else "Treatment is significantly worse than control"
            recommended_action = "Adopt treatment" if is_better else "Reject treatment"
        elif confidence_level >= 0.8:
            conclusion = "Treatment appears better than control, but more data is needed" if is_better else "Treatment appears worse than control, but more data is needed"
            recommended_action = "Continue testing with larger sample" if is_better else "Reject treatment"
        else:
            conclusion = "Inconclusive results, more data is needed"
            recommended_action = "Continue testing with larger sample"
            
        return conclusion, recommended_action
        
    async def _identify_best_combination(self, comparison):
        """
        Identify the best combination from multivariate testing.
        
        Args:
            comparison: Comparison results
            
        Returns:
            Best combination and confidence levels
        """
        # This would normally involve analysis of all combinations
        # For now, we simulate best combination identification
        logger.info("Identifying best combination")
        
        # Score each combination
        combination_scores = {}
        confidence_levels = {}
        
        # Extract all combination names
        all_combinations = set()
        for metric_comparisons in comparison.values():
            all_combinations.update(metric_comparisons.keys())
            
        # Initialize scores
        for combo_name in all_combinations:
            combination_scores[combo_name] = 0
            confidence_levels[combo_name] = []
            
        # Calculate scores based on pairwise comparisons
        for metric_id, metric_comparisons in comparison.items():
            for combo1_name, combo1_comparisons in metric_comparisons.items():
                for combo2_name, comparison_data in combo1_comparisons.items():
                    if comparison_data.get("percent_change", 0) > 0:
                        combination_scores[combo1_name] += 1
                    else:
                        combination_scores[combo2_name] += 1
                        
                    confidence_levels[combo1_name].append(comparison_data.get("confidence", 0.5))
                    confidence_levels[combo2_name].append(comparison_data.get("confidence", 0.5))
                    
        # Average confidence levels
        for combo_name, confidence_values in confidence_levels.items():
            if confidence_values:
                confidence_levels[combo_name] = sum(confidence_values) / len(confidence_values)
            else:
                confidence_levels[combo_name] = 0.0
                
        # Find the best combination
        best_combination = None
        best_score = -1
        
        for combo_name, score in combination_scores.items():
            if score > best_score:
                best_score = score
                best_combination = combo_name
                
        return best_combination, confidence_levels
        
    async def _determine_multivariate_outcome(self, best_combination, confidence_levels):
        """
        Determine the outcome of a multivariate experiment.
        
        Args:
            best_combination: Best combination
            confidence_levels: Confidence levels for each combination
            
        Returns:
            Conclusion and recommended action
        """
        # This would normally involve analysis of the best combination
        # For now, we simulate outcome determination
        logger.info("Determining multivariate experiment outcome")
        
        if not best_combination:
            return "No clear winner among combinations", "Continue testing with modified parameters"
            
        # Get confidence for best combination
        best_confidence = confidence_levels.get(best_combination, 0.0)
        
        # Determine conclusion
        if best_confidence >= 0.95:
            conclusion = f"Combination '{best_combination}' is significantly better than others"
            recommended_action = f"Adopt combination '{best_combination}'"
        elif best_confidence >= 0.8:
            conclusion = f"Combination '{best_combination}' appears better than others, but more data is needed"
            recommended_action = "Continue testing with larger sample"
        else:
            conclusion = "Inconclusive results, more data is needed"
            recommended_action = "Continue testing with larger sample"
            
        return conclusion, recommended_action
        
    async def _analyze_shadow_differences(self, comparison):
        """
        Analyze differences between production and shadow systems.
        
        Args:
            comparison: Comparison results
            
        Returns:
            Analysis of differences
        """
        # This would normally involve detailed analysis
        # For now, we simulate difference analysis
        logger.info("Analyzing shadow differences")
        
        differences = {}
        
        for metric_id, comparison_data in comparison.items():
            percent_change = comparison_data.get("percent_change", 0)
            is_significant = comparison_data.get("is_significant", False)
            
            differences[metric_id] = {
                "percent_change": percent_change,
                "is_significant": is_significant,
                "direction": "improvement" if percent_change > 0 else "degradation" if percent_change < 0 else "neutral",
                "magnitude": "large" if abs(percent_change) > 20 else "medium" if abs(percent_change) > 5 else "small"
            }
            
        return differences
        
    async def _identify_shadow_risks_benefits(self, differences):
        """
        Identify risks and benefits from shadow testing.
        
        Args:
            differences: Analysis of differences
            
        Returns:
            Risks and benefits
        """
        # This would normally involve detailed analysis
        # For now, we simulate risk and benefit identification
        logger.info("Identifying shadow risks and benefits")
        
        risks = []
        benefits = []
        
        for metric_id, difference in differences.items():
            if difference["direction"] == "degradation" and difference["is_significant"]:
                risks.append({
                    "metric_id": metric_id,
                    "percent_change": difference["percent_change"],
                    "magnitude": difference["magnitude"],
                    "description": f"Significant degradation in {metric_id}"
                })
            elif difference["direction"] == "improvement" and difference["is_significant"]:
                benefits.append({
                    "metric_id": metric_id,
                    "percent_change": difference["percent_change"],
                    "magnitude": difference["magnitude"],
                    "description": f"Significant improvement in {metric_id}"
                })
                
        return risks, benefits
        
    async def _determine_shadow_readiness(self, differences, risks):
        """
        Determine readiness for production from shadow testing.
        
        Args:
            differences: Analysis of differences
            risks: Identified risks
            
        Returns:
            Readiness status and confidence level
        """
        # This would normally involve detailed analysis
        # For now, we simulate readiness determination
        logger.info("Determining shadow readiness")
        
        # Count significant degradations by magnitude
        large_degradations = sum(1 for risk in risks if risk["magnitude"] == "large")
        medium_degradations = sum(1 for risk in risks if risk["magnitude"] == "medium")
        
        # Determine readiness
        if large_degradations > 0:
            is_ready = False
            confidence_level = 0.9
        elif medium_degradations > 2:
            is_ready = False
            confidence_level = 0.8
        elif medium_degradations > 0:
            is_ready = True
            confidence_level = 0.7
        else:
            is_ready = True
            confidence_level = 0.95
            
        return is_ready, confidence_level
        
    async def _check_canary_health(self, canary_metrics, comparison):
        """
        Check the health of a canary deployment.
        
        Args:
            canary_metrics: Metrics from canary
            comparison: Comparison results
            
        Returns:
            Error and degradation flags
        """
        # This would normally involve detailed health checks
        # For now, we simulate health checking
        logger.info("Checking canary health")
        
        # Check for errors
        has_errors = False
        
        for metric_id, metric_data in canary_metrics.items():
            if metric_id.startswith("error.") and metric_data:
                # Check if error rate is above threshold
                error_value = metric_data[0].get("value", 0) if metric_data else 0
                if error_value > 0.01:  # 1% error rate threshold
                    has_errors = True
                    break
                    
        # Check for significant degradation
        has_degradation = False
        
        for metric_id, comparison_data in comparison.items():
            if metric_id.startswith("perf.") and comparison_data.get("is_significant", False):
                percent_change = comparison_data.get("percent_change", 0)
                if percent_change < -20:  # 20% degradation threshold
                    has_degradation = True
                    break
                    
        return has_errors, has_degradation
        
    async def _generate_parameter_combinations(self, parameters_to_tune):
        """
        Generate parameter combinations for tuning.
        
        Args:
            parameters_to_tune: Parameters to tune with possible values
            
        Returns:
            List of parameter combinations
        """
        # This would normally involve a cartesian product of parameter values
        # For now, we simulate combination generation
        logger.info("Generating parameter combinations")
        
        combinations = []
        
        # Generate a simple list of combinations for demonstration
        keys = list(parameters_to_tune.keys())
        
        if not keys:
            return []
            
        # Get values for first parameter
        values = parameters_to_tune[keys[0]]
        
        # Initialize with first parameter's values
        for value in values:
            combinations.append({keys[0]: value})
            
        # Add remaining parameters one by one
        for i in range(1, len(keys)):
            new_combinations = []
            key = keys[i]
            values = parameters_to_tune[key]
            
            for combo in combinations:
                for value in values:
                    new_combo = combo.copy()
                    new_combo[key] = value
                    new_combinations.append(new_combo)
                    
            combinations = new_combinations
            
        return combinations
        
    async def _find_optimal_parameters(self, results_by_combination, metrics):
        """
        Find optimal parameters from tuning results.
        
        Args:
            results_by_combination: Results for each combination
            metrics: Metrics used for evaluation
            
        Returns:
            Optimal combination and performance by metric
        """
        # This would normally involve optimization analysis
        # For now, we simulate optimal parameter finding
        logger.info("Finding optimal parameters")
        
        # Score each combination
        scores_by_combination = {}
        performance_by_metric = {}
        
        for combo_name, combo_results in results_by_combination.items():
            scores_by_combination[combo_name] = 0
            
            for metric_id, metric_data in combo_results["metrics"].items():
                if metric_id not in performance_by_metric:
                    performance_by_metric[metric_id] = {}
                    
                # Calculate average value for this metric
                avg_value = sum(m.get("value", 0) for m in metric_data) / len(metric_data) if metric_data else 0
                
                # Store performance
                performance_by_metric[metric_id][combo_name] = avg_value
                
                # Score based on optimization goal (assume higher is better)
                scores_by_combination[combo_name] += avg_value
                
        # Find the combination with the highest score
        best_combo_name = max(scores_by_combination, key=scores_by_combination.get) if scores_by_combination else None
        
        if best_combo_name:
            best_parameters = results_by_combination[best_combo_name]["parameters"]
        else:
            best_parameters = {}
            
        return best_parameters, performance_by_metric
        
    async def _apply_change(self, after_condition):
        """
        Apply a change for before/after testing.
        
        Args:
            after_condition: Condition to apply
            
        Returns:
            True if successful
        """
        # This would normally involve applying a real change
        # For now, we simulate applying a change
        logger.info(f"Applying change: {after_condition}")
        
        # Simulate a delay for the change to take effect
        await asyncio.sleep(1)
        
        return True
        
    async def _calculate_improvements_degradations(self, comparison):
        """
        Calculate improvements and degradations from comparison.
        
        Args:
            comparison: Comparison results
            
        Returns:
            Improvements and degradations
        """
        # This would normally involve detailed analysis
        # For now, we simulate improvement and degradation analysis
        logger.info("Calculating improvements and degradations")
        
        improvements = {}
        degradations = {}
        
        for metric_id, comparison_data in comparison.items():
            percent_change = comparison_data.get("percent_change", 0)
            is_significant = comparison_data.get("is_significant", False)
            
            if is_significant:
                if percent_change > 0:
                    improvements[metric_id] = {
                        "percent_change": percent_change,
                        "confidence": comparison_data.get("confidence", 0.5),
                        "magnitude": "large" if percent_change > 20 else "medium" if percent_change > 5 else "small"
                    }
                elif percent_change < 0:
                    degradations[metric_id] = {
                        "percent_change": percent_change,
                        "confidence": comparison_data.get("confidence", 0.5),
                        "magnitude": "large" if abs(percent_change) > 20 else "medium" if abs(percent_change) > 5 else "small"
                    }
                    
        return improvements, degradations
        
    async def _calculate_impact_score(self, improvements, degradations):
        """
        Calculate overall impact score from improvements and degradations.
        
        Args:
            improvements: Identified improvements
            degradations: Identified degradations
            
        Returns:
            Impact score (-1 to 1)
        """
        # This would normally involve a weighted scoring system
        # For now, we simulate impact calculation
        logger.info("Calculating impact score")
        
        # Count improvements and degradations by magnitude
        large_improvements = sum(1 for imp in improvements.values() if imp["magnitude"] == "large")
        medium_improvements = sum(1 for imp in improvements.values() if imp["magnitude"] == "medium")
        small_improvements = sum(1 for imp in improvements.values() if imp["magnitude"] == "small")
        
        large_degradations = sum(1 for deg in degradations.values() if deg["magnitude"] == "large")
        medium_degradations = sum(1 for deg in degradations.values() if deg["magnitude"] == "medium")
        small_degradations = sum(1 for deg in degradations.values() if deg["magnitude"] == "small")
        
        # Calculate weighted score
        improvement_score = (3 * large_improvements + 2 * medium_improvements + small_improvements)
        degradation_score = (3 * large_degradations + 2 * medium_degradations + small_degradations)
        
        # Normalize to -1 to 1 range
        if improvement_score == 0 and degradation_score == 0:
            return 0.0
            
        max_score = max(improvement_score, degradation_score)
        normalized_improvement = improvement_score / max_score
        normalized_degradation = degradation_score / max_score
        
        impact_score = normalized_improvement - normalized_degradation
        
        return impact_score
        
    async def _rank_candidates(self, comparisons):
        """
        Rank candidates based on comparisons to baseline.
        
        Args:
            comparisons: Comparison results for each candidate
            
        Returns:
            Ranked list of candidates
        """
        # This would normally involve detailed ranking
        # For now, we simulate candidate ranking
        logger.info("Ranking candidates")
        
        # Score each candidate
        candidate_scores = {}
        
        for candidate_name, comparison in comparisons.items():
            score = 0
            
            for metric_id, comparison_data in comparison.items():
                percent_change = comparison_data.get("percent_change", 0)
                is_significant = comparison_data.get("is_significant", False)
                
                if is_significant:
                    if percent_change > 0:
                        # Improvement
                        score += 1 + (percent_change / 100)
                    elif percent_change < 0:
                        # Degradation
                        score -= 1 + (abs(percent_change) / 100)
                        
            candidate_scores[candidate_name] = score
            
        # Rank candidates by score
        ranked_candidates = sorted(candidate_scores.keys(), key=lambda x: candidate_scores[x], reverse=True)
        
        # Filter out candidates that are worse than baseline
        ranked_candidates = [c for c in ranked_candidates if candidate_scores[c] > 0]
        
        return ranked_candidates
        
    def _parse_duration(self, duration_str):
        """
        Parse duration string to seconds.
        
        Args:
            duration_str: Duration string (e.g., "24h", "30m", "60s")
            
        Returns:
            Duration in seconds
        """
        if not duration_str:
            return 86400  # Default to 24 hours
            
        unit = duration_str[-1]
        value = int(duration_str[:-1])
        
        if unit == "s":
            return value
        elif unit == "m":
            return value * 60
        elif unit == "h":
            return value * 3600
        elif unit == "d":
            return value * 86400
        else:
            return 86400  # Default to 24 hours

class ExperimentFramework:
    """
    Experiment Framework for Sophia.
    
    Provides a framework for designing, running, and analyzing experiments to
    validate hypotheses and drive continuous improvement.
    """
    
    def __init__(self):
        """Initialize the experiment framework."""
        self.is_initialized = False
        self.metrics_engine = None
        self.analysis_engine = None
        self.experiments = {}
        self.active_runners = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the experiment framework.
        
        Returns:
            True if initialization was successful
        """
        logger.info("Initializing Sophia Experiment Framework...")
        
        # Get required engines
        self.metrics_engine = await get_metrics_engine()
        self.analysis_engine = await get_analysis_engine()
        
        # Load existing experiments
        await self._load_experiments()
        
        self.is_initialized = True
        logger.info("Sophia Experiment Framework initialized successfully")
        return True
        
    async def start(self) -> bool:
        """
        Start the experiment framework.
        
        Returns:
            True if successful
        """
        if not self.is_initialized:
            success = await self.initialize()
            if not success:
                logger.error("Failed to initialize Experiment Framework")
                return False
                
        logger.info("Starting Sophia Experiment Framework...")
        
        # Start scheduled experiments
        scheduled_experiments = [
            exp_id for exp_id, exp in self.experiments.items()
            if exp.get("status") == ExperimentStatus.SCHEDULED
        ]
        
        for exp_id in scheduled_experiments:
            scheduled_time = self.experiments[exp_id].get("start_time")
            if scheduled_time:
                # Parse scheduled time
                scheduled_dt = datetime.fromisoformat(scheduled_time.rstrip("Z"))
                
                # Check if it's time to start
                if scheduled_dt <= datetime.utcnow():
                    await self.start_experiment(exp_id)
                    
        logger.info("Sophia Experiment Framework started successfully")
        return True
        
    async def stop(self) -> bool:
        """
        Stop the experiment framework and clean up resources.
        
        Returns:
            True if successful
        """
        logger.info("Stopping Sophia Experiment Framework...")
        
        # Stop all active runners
        for exp_id, runner in self.active_runners.items():
            if runner.is_running:
                logger.info(f"Stopping experiment runner for {exp_id}")
                # Mark the experiment as failed
                self.experiments[exp_id]["status"] = ExperimentStatus.FAILED
                
        # Clear active runners
        self.active_runners = {}
        
        # Save experiments
        await self._save_experiments()
        
        logger.info("Sophia Experiment Framework stopped successfully")
        return True
        
    async def create_experiment(
        self,
        name: str,
        description: str,
        experiment_type: Union[str, ExperimentType],
        target_components: List[str],
        hypothesis: str,
        metrics: List[str],
        parameters: Dict[str, Any],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        sample_size: Optional[int] = None,
        min_confidence: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new experiment.
        
        Args:
            name: Name of the experiment
            description: Description of the experiment
            experiment_type: Type of experiment
            target_components: List of components involved in the experiment
            hypothesis: Hypothesis being tested
            metrics: List of metrics to be tracked
            parameters: Parameters for the experiment
            start_time: Scheduled start time (ISO format)
            end_time: Scheduled end time (ISO format)
            sample_size: Target sample size
            min_confidence: Minimum confidence level required
            tags: Tags for categorizing the experiment
            
        Returns:
            Experiment ID
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Create experiment ID
        experiment_id = str(uuid.uuid4())
        
        # Determine initial status
        status = ExperimentStatus.SCHEDULED if start_time else ExperimentStatus.DRAFT
        
        # Convert experiment_type to string if it's an enum
        if isinstance(experiment_type, ExperimentType):
            experiment_type = experiment_type.value
            
        # Create experiment
        experiment = {
            "id": experiment_id,
            "name": name,
            "description": description,
            "experiment_type": experiment_type,
            "target_components": target_components,
            "hypothesis": hypothesis,
            "metrics": metrics,
            "parameters": parameters,
            "start_time": start_time,
            "end_time": end_time,
            "sample_size": sample_size,
            "min_confidence": min_confidence,
            "tags": tags or [],
            "status": status,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "results": None
        }
        
        # Store experiment
        self.experiments[experiment_id] = experiment
        
        # Save experiments
        await self._save_experiments()
        
        logger.info(f"Created experiment {experiment_id}: {name}")
        return experiment_id
        
    async def query_experiments(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query experiments with filtering.
        
        Args:
            query: Query parameters
            
        Returns:
            List of matching experiments
        """
        if not self.is_initialized:
            await self.initialize()
            
        filtered_experiments = []
        
        # Extract query parameters
        status = query.get("status")
        experiment_type = query.get("experiment_type")
        target_components = query.get("target_components")
        tags = query.get("tags")
        start_after = query.get("start_after")
        start_before = query.get("start_before")
        limit = query.get("limit", 100)
        offset = query.get("offset", 0)
        
        # Convert to ISO format if needed
        if start_after and not start_after.endswith("Z"):
            start_after = datetime.fromisoformat(start_after).isoformat() + "Z"
        if start_before and not start_before.endswith("Z"):
            start_before = datetime.fromisoformat(start_before).isoformat() + "Z"
            
        # Filter experiments
        for exp_id, exp in self.experiments.items():
            # Check status
            if status and exp.get("status") != status:
                continue
                
            # Check experiment type
            if experiment_type and exp.get("experiment_type") != experiment_type:
                continue
                
            # Check target components
            if target_components and not any(comp in exp.get("target_components", []) for comp in target_components):
                continue
                
            # Check tags
            if tags and not any(tag in exp.get("tags", []) for tag in tags):
                continue
                
            # Check start time
            if start_after and exp.get("start_time") and exp.get("start_time") < start_after:
                continue
                
            if start_before and exp.get("start_time") and exp.get("start_time") > start_before:
                continue
                
            # Add to filtered list
            filtered_experiments.append(exp)
            
        # Sort by creation time (newest first)
        filtered_experiments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        paginated_experiments = filtered_experiments[offset:offset + limit]
        
        return paginated_experiments
        
    async def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Experiment data or None if not found
        """
        if not self.is_initialized:
            await self.initialize()
            
        return self.experiments.get(experiment_id)
        
    async def update_experiment(self, experiment_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing experiment.
        
        Args:
            experiment_id: ID of the experiment
            updates: Updates to apply
            
        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Check if experiment exists
        if experiment_id not in self.experiments:
            logger.error(f"Experiment not found: {experiment_id}")
            return False
            
        # Get current experiment
        experiment = self.experiments[experiment_id]
        
        # Validate updates
        current_status = experiment.get("status")
        new_status = updates.get("status")
        
        if new_status and new_status != current_status:
            # Check if status transition is valid
            if not self._is_valid_status_transition(current_status, new_status):
                logger.error(f"Invalid status transition: {current_status} -> {new_status}")
                return False
                
        # Apply updates
        for key, value in updates.items():
            if key != "id" and key != "created_at":
                experiment[key] = value
                
        # Update timestamp
        experiment["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Save experiments
        await self._save_experiments()
        
        logger.info(f"Updated experiment {experiment_id}")
        return True
        
    async def start_experiment(self, experiment_id: str) -> bool:
        """
        Start an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Check if experiment exists
        if experiment_id not in self.experiments:
            logger.error(f"Experiment not found: {experiment_id}")
            return False
            
        # Get the experiment
        experiment = self.experiments[experiment_id]
        
        # Check if experiment can be started
        if experiment.get("status") not in [ExperimentStatus.DRAFT, ExperimentStatus.SCHEDULED]:
            logger.error(f"Cannot start experiment with status: {experiment.get('status')}")
            return False
            
        # Create a runner for the experiment
        runner = ExperimentRunner(
            experiment_config=experiment,
            metrics_engine=self.metrics_engine,
            analysis_engine=self.analysis_engine
        )
        
        # Store the runner
        self.active_runners[experiment_id] = runner
        
        # Start the runner in the background
        asyncio.create_task(self._run_experiment(experiment_id, runner))
        
        logger.info(f"Started experiment {experiment_id}")
        return True
        
    async def stop_experiment(self, experiment_id: str) -> bool:
        """
        Stop an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Check if experiment exists
        if experiment_id not in self.experiments:
            logger.error(f"Experiment not found: {experiment_id}")
            return False
            
        # Check if experiment is running
        if experiment_id not in self.active_runners:
            logger.error(f"Experiment is not running: {experiment_id}")
            return False
            
        # Get the runner
        runner = self.active_runners[experiment_id]
        
        # Mark the experiment as failed
        self.experiments[experiment_id]["status"] = ExperimentStatus.FAILED
        
        # Remove the runner
        del self.active_runners[experiment_id]
        
        # Save experiments
        await self._save_experiments()
        
        logger.info(f"Stopped experiment {experiment_id}")
        return True
        
    async def analyze_experiment(self, experiment_id: str) -> bool:
        """
        Analyze an experiment's results.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Check if experiment exists
        if experiment_id not in self.experiments:
            logger.error(f"Experiment not found: {experiment_id}")
            return False
            
        # Get the experiment
        experiment = self.experiments[experiment_id]
        
        # Check if experiment is completed
        if experiment.get("status") != ExperimentStatus.COMPLETED:
            logger.error(f"Cannot analyze experiment with status: {experiment.get('status')}")
            return False
            
        # Update status
        experiment["status"] = ExperimentStatus.ANALYZING
        
        # Start analysis in the background
        asyncio.create_task(self._analyze_experiment_results(experiment_id))
        
        logger.info(f"Started analysis for experiment {experiment_id}")
        return True
        
    async def get_experiment_results(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get results of a completed experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Experiment results or None if not available
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Check if experiment exists
        if experiment_id not in self.experiments:
            logger.error(f"Experiment not found: {experiment_id}")
            return None
            
        # Get the experiment
        experiment = self.experiments[experiment_id]
        
        # Check if results are available
        if experiment.get("status") not in [ExperimentStatus.COMPLETED, ExperimentStatus.ANALYZED]:
            logger.error(f"Results not available for experiment with status: {experiment.get('status')}")
            return None
            
        # Return results
        return experiment.get("results")
        
    async def delete_experiment(self, experiment_id: str) -> bool:
        """
        Delete an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Check if experiment exists
        if experiment_id not in self.experiments:
            logger.error(f"Experiment not found: {experiment_id}")
            return False
            
        # Stop the experiment if it's running
        if experiment_id in self.active_runners:
            await self.stop_experiment(experiment_id)
            
        # Remove the experiment
        del self.experiments[experiment_id]
        
        # Save experiments
        await self._save_experiments()
        
        logger.info(f"Deleted experiment {experiment_id}")
        return True
        
    async def _run_experiment(self, experiment_id: str, runner: ExperimentRunner) -> None:
        """
        Run an experiment in the background.
        
        Args:
            experiment_id: ID of the experiment
            runner: Experiment runner
        """
        try:
            # Start the runner
            success = await runner.run()
            
            # Update experiment
            experiment = self.experiments[experiment_id]
            
            if success:
                # Store results
                experiment["results"] = runner.results
                experiment["status"] = ExperimentStatus.COMPLETED
            else:
                experiment["status"] = ExperimentStatus.FAILED
                
            # Remove the runner
            if experiment_id in self.active_runners:
                del self.active_runners[experiment_id]
                
            # Save experiments
            await self._save_experiments()
        except Exception as e:
            logger.error(f"Error running experiment {experiment_id}: {e}")
            
            # Update experiment status
            if experiment_id in self.experiments:
                self.experiments[experiment_id]["status"] = ExperimentStatus.FAILED
                
            # Remove the runner
            if experiment_id in self.active_runners:
                del self.active_runners[experiment_id]
                
            # Save experiments
            await self._save_experiments()
            
    async def _analyze_experiment_results(self, experiment_id: str) -> None:
        """
        Analyze experiment results in the background.
        
        Args:
            experiment_id: ID of the experiment
        """
        try:
            # Get the experiment
            experiment = self.experiments[experiment_id]
            
            # Get the results
            results = experiment.get("results", {})
            
            # Use the analysis engine for deeper analysis
            analysis = await self.analysis_engine.analyze_experiment_results(results)
            
            # Update results with analysis
            updated_results = {
                **results,
                "deep_analysis": analysis
            }
            
            # Update experiment
            experiment["results"] = updated_results
            experiment["status"] = ExperimentStatus.ANALYZED
            
            # Save experiments
            await self._save_experiments()
            
            logger.info(f"Completed analysis for experiment {experiment_id}")
        except Exception as e:
            logger.error(f"Error analyzing experiment {experiment_id}: {e}")
            
            # Update experiment status
            if experiment_id in self.experiments:
                self.experiments[experiment_id]["status"] = ExperimentStatus.COMPLETED
                
            # Save experiments
            await self._save_experiments()
            
    async def _load_experiments(self) -> bool:
        """
        Load experiments from storage.
        
        Returns:
            True if successful
        """
        # Define the experiments file path
        file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "experiments", "experiments.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Load experiments
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    self.experiments = json.load(f)
                logger.info(f"Loaded {len(self.experiments)} experiments from {file_path}")
            else:
                self.experiments = {}
                logger.info(f"No experiments file found at {file_path}, starting with empty state")
                
            return True
        except Exception as e:
            logger.error(f"Error loading experiments: {e}")
            self.experiments = {}
            return False
            
    async def _save_experiments(self) -> bool:
        """
        Save experiments to storage.
        
        Returns:
            True if successful
        """
        # Define the experiments file path
        file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "experiments", "experiments.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save experiments
        try:
            with open(file_path, "w") as f:
                json.dump(self.experiments, f, indent=2)
            logger.info(f"Saved {len(self.experiments)} experiments to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving experiments: {e}")
            return False
            
    def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        """
        Check if a status transition is valid.
        
        Args:
            current_status: Current status
            new_status: New status
            
        Returns:
            True if the transition is valid
        """
        # Define valid transitions
        valid_transitions = {
            ExperimentStatus.DRAFT: [ExperimentStatus.SCHEDULED, ExperimentStatus.RUNNING],
            ExperimentStatus.SCHEDULED: [ExperimentStatus.RUNNING, ExperimentStatus.CANCELLED],
            ExperimentStatus.RUNNING: [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED],
            ExperimentStatus.COMPLETED: [ExperimentStatus.ANALYZING],
            ExperimentStatus.ANALYZING: [ExperimentStatus.ANALYZED, ExperimentStatus.COMPLETED],
            ExperimentStatus.ANALYZED: [],
            ExperimentStatus.FAILED: [],
            ExperimentStatus.CANCELLED: []
        }
        
        # Check if the transition is valid
        valid_next_statuses = valid_transitions.get(current_status, [])
        return new_status in valid_next_statuses

# Global singleton instance
_experiment_framework = ExperimentFramework()

async def get_experiment_framework() -> ExperimentFramework:
    """
    Get the global experiment framework instance.
    
    Returns:
        ExperimentFramework instance
    """
    if not _experiment_framework.is_initialized:
        await _experiment_framework.initialize()
    return _experiment_framework