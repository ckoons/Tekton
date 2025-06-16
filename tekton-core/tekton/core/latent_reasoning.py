#!/usr/bin/env python3
"""
Latent Reasoning Framework for Tekton

This module provides a mixin class that components can use to integrate
with the continuous latent space reasoning framework.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable

# Configure logging
logger = logging.getLogger("tekton.core.latent_reasoning")


class LatentReasoningMixin:
    """
    Mixin class to provide latent space reasoning capabilities to components.
    
    This class allows components to integrate with the latent space reasoning
    framework, enabling iterative refinement of thoughts and cross-component
    insight sharing.
    """
    
    async def initialize_latent_space(self, 
                                    namespace: str = "default",
                                    shared: bool = True,
                                    max_history: int = 20,
                                    data_dir: Optional[str] = None):
        """Initialize the component's latent space."""
        if not hasattr(self, 'component_id'):
            raise AttributeError("Component must define 'component_id' to use latent reasoning")
        
        try:
            from engram.integrations.hermes.latent_space_adapter import SharedLatentSpace
            
            self.latent_space = SharedLatentSpace(
                component_id=self.component_id,
                namespace=namespace,
                max_history=max_history,
                data_dir=data_dir,
                shared_insights=shared
            )
            
            await self.latent_space.start()
            
            if shared:
                await self.latent_space.register_insight_handler(self._handle_external_insight)
                
            logger.info(f"Initialized latent space for {self.component_id} in namespace {namespace}")
            return True
            
        except ImportError as e:
            logger.error(f"Error importing SharedLatentSpace: {e}")
            logger.error("Make sure Engram with Hermes integration is available in your environment")
            return False
        except Exception as e:
            logger.error(f"Error initializing latent space: {e}")
            return False
    
    async def _handle_external_insight(self, insight: Dict[str, Any]):
        """Handle insights shared by other components."""
        source = insight.get("source_component", "unknown")
        summary = insight.get("summary", "No summary available")
        logger.info(f"{self.component_id} received insight from {source}: {summary[:100]}...")
        
    async def with_latent_reasoning(
        self, 
        input_content: str, 
        process_func: Callable[[str], Awaitable[str]],
        max_iterations: int = 3,
        convergence_threshold: float = 0.95,
        evaluate_func: Optional[Callable[[str, str], Awaitable[float]]] = None,
        share_final_insight: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process input with iterative latent space reasoning."""
        if not hasattr(self, 'latent_space'):
            raise RuntimeError(f"Latent space not initialized for {self.__class__.__name__}. "
                             f"Call initialize_latent_space() first.")
                             
        metadata = metadata or {}
        metadata.update({
            "component_id": self.component_id,
            "max_iterations": max_iterations,
            "convergence_threshold": convergence_threshold,
            "process_type": "iterative_refinement"
        })
        
        thought_id = await self.latent_space.initialize_thought(
            thought_seed=input_content,
            metadata=metadata
        )
        
        current_content = input_content
        iteration = 0
        converged = False
        similarity = 0.0
        
        logger.info(f"Starting latent reasoning process with max {max_iterations} iterations")
        
        if evaluate_func is None:
            from engram.core.latent_space import ConvergenceDetector
            evaluate_func = ConvergenceDetector.text_similarity
        
        while iteration < max_iterations and not converged:
            iteration += 1
            logger.info(f"Latent reasoning iteration {iteration}/{max_iterations}")
            
            refinement_prompt = (
                f"Iteration {iteration}/{max_iterations}: Refine the previous thinking by "
                f"adding depth, considering edge cases, or addressing weaknesses:\n\n"
                f"{current_content}"
            )
            
            try:
                iteration_start = time.time()
                refined_content = await process_func(refinement_prompt)
                iteration_time = time.time() - iteration_start
                
                iteration_metadata = {
                    "processing_time": iteration_time,
                    "iteration": iteration,
                    "prompt_length": len(refinement_prompt),
                    "result_length": len(refined_content)
                }
                
                if iteration > 1:
                    similarity = await evaluate_func(current_content, refined_content)
                    iteration_metadata["similarity"] = similarity
                    converged = similarity >= convergence_threshold
                    
                    if converged:
                        logger.info(f"Latent reasoning converged after {iteration} iterations "
                                   f"(similarity: {similarity:.4f})")
                
                await self.latent_space.refine_thought(
                    thought_id=thought_id, 
                    refinement=refined_content,
                    iteration=iteration,
                    metadata_updates=iteration_metadata
                )
                
                current_content = refined_content
                
            except Exception as e:
                logger.error(f"Error in latent reasoning iteration {iteration}: {e}")
                
        final_metadata = {
            "iterations_performed": iteration,
            "converged": converged,
            "final_similarity": similarity,
            "reached_max_iterations": iteration >= max_iterations
        }
        
        await self.latent_space.finalize_thought(
            thought_id=thought_id,
            final_content=current_content,
            persist=True,
            metadata_updates=final_metadata
        )
        
        if share_final_insight:
            summary = (
                f"Completed latent reasoning after {iteration} iterations "
                f"(converged: {converged}, similarity: {similarity:.4f})"
            )
            
            await self.latent_space.share_insight(
                thought_id=thought_id,
                summary=summary
            )
        
        trace = await self.latent_space.get_reasoning_trace(
            thought_id=thought_id,
            include_iterations=True
        )
        
        return {
            "result": current_content,
            "iterations": iteration,
            "thought_id": thought_id,
            "converged": converged,
            "similarity": similarity,
            "trace": trace
        }
        
    async def confidence_based_reasoning(
        self,
        input_content: str,
        process_func: Callable[[str], Awaitable[Dict[str, Any]]],
        confidence_threshold: float = 0.7,
        max_iterations: int = 3,
        share_final_insight: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process input with confidence-based reasoning, refining only if confidence is low."""
        if not hasattr(self, 'latent_space'):
            raise RuntimeError(f"Latent space not initialized for {self.__class__.__name__}. "
                             f"Call initialize_latent_space() first.")
        
        metadata = metadata or {}
        metadata.update({
            "component_id": self.component_id,
            "confidence_threshold": confidence_threshold,
            "max_iterations": max_iterations,
            "process_type": "confidence_based"
        })
        
        logger.info(f"Starting confidence-based reasoning for {self.component_id}")
        iteration_start = time.time()
        initial_result = await process_func(input_content)
        iteration_time = time.time() - iteration_start
        
        result_content = initial_result.get("result", "")
        confidence = initial_result.get("confidence", 0.0)
        
        metadata.update({
            "initial_confidence": confidence,
            "initial_processing_time": iteration_time
        })
        
        thought_content = f"Initial result (confidence: {confidence:.4f}):\n\n{result_content}"
        
        thought_id = await self.latent_space.initialize_thought(
            thought_seed=thought_content,
            metadata=metadata
        )
        
        if confidence >= confidence_threshold:
            logger.info(f"Initial confidence {confidence:.4f} meets threshold {confidence_threshold:.4f}")
            
            await self.latent_space.finalize_thought(
                thought_id=thought_id,
                persist=True,
                metadata_updates={
                    "iterations_performed": 1,
                    "final_confidence": confidence,
                    "needed_refinement": False
                }
            )
            
            if share_final_insight:
                await self.latent_space.share_insight(
                    thought_id=thought_id,
                    summary=f"Confident result (score: {confidence:.4f}) without latent refinement"
                )
            
            return {
                "result": result_content,
                "confidence": confidence,
                "iterations": 1,
                "thought_id": thought_id,
                "needed_refinement": False,
                "trace": await self.latent_space.get_reasoning_trace(thought_id, include_iterations=True)
            }
        
        logger.info(f"Initial confidence {confidence:.4f} below threshold {confidence_threshold:.4f}")
        
        current_result = initial_result
        current_content = result_content
        iteration = 1
        
        while confidence < confidence_threshold and iteration < max_iterations:
            iteration += 1
            
            refinement_prompt = (
                f"The previous answer had low confidence ({confidence:.4f}). "
                f"Please reconsider and provide a more confident answer:\n\n"
                f"Question: {input_content}\n"
                f"Previous answer: {current_content}"
            )
            
            iteration_start = time.time()
            refined_result = await process_func(refinement_prompt)
            iteration_time = time.time() - iteration_start
            
            new_content = refined_result.get("result", "")
            confidence = refined_result.get("confidence", 0.0)
            
            iteration_metadata = {
                "iteration": iteration,
                "confidence": confidence,
                "processing_time": iteration_time,
                "prompt_length": len(refinement_prompt),
                "result_length": len(new_content)
            }
            
            iteration_content = f"Iteration {iteration} result (confidence: {confidence:.4f}):\n\n{new_content}"
            
            await self.latent_space.refine_thought(
                thought_id=thought_id,
                refinement=iteration_content,
                iteration=iteration,
                metadata_updates=iteration_metadata
            )
            
            current_result = refined_result
            current_content = new_content
            
            logger.info(f"Iteration {iteration} confidence: {confidence:.4f}")
            
            if confidence >= confidence_threshold:
                logger.info(f"Reached confidence threshold after {iteration} iterations")
                break
        
        await self.latent_space.finalize_thought(
            thought_id=thought_id,
            persist=True,
            metadata_updates={
                "iterations_performed": iteration,
                "final_confidence": confidence,
                "reached_confidence_threshold": confidence >= confidence_threshold,
                "reached_max_iterations": iteration >= max_iterations,
                "needed_refinement": True
            }
        )
        
        if share_final_insight:
            summary = (
                f"{'Confident' if confidence >= confidence_threshold else 'Final'} "
                f"result after {iteration} iterations (confidence: {confidence:.4f})"
            )
            
            await self.latent_space.share_insight(
                thought_id=thought_id,
                summary=summary
            )
        
        return {
            "result": current_content,
            "confidence": confidence,
            "iterations": iteration,
            "thought_id": thought_id,
            "needed_refinement": True,
            "reached_threshold": confidence >= confidence_threshold,
            "trace": await self.latent_space.get_reasoning_trace(thought_id, include_iterations=True)
        }
        
    async def complexity_based_reasoning(
        self,
        input_content: str,
        process_func: Callable[[str], Awaitable[str]],
        complexity_analyzer: Callable[[str], Awaitable[float]],
        complexity_threshold: float = 0.7,
        max_iterations: int = 3,
        convergence_threshold: float = 0.95,
        share_final_insight: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process input based on complexity, using latent reasoning only for complex inputs."""
        complexity_score = await complexity_analyzer(input_content)
        
        metadata = metadata or {}
        metadata.update({
            "complexity_score": complexity_score,
            "complexity_threshold": complexity_threshold,
            "process_type": "complexity_based"
        })
        
        if complexity_score >= complexity_threshold:
            logger.info(f"Input complexity {complexity_score:.4f} above threshold, using latent reasoning")
            
            result = await self.with_latent_reasoning(
                input_content=input_content,
                process_func=process_func,
                max_iterations=max_iterations,
                convergence_threshold=convergence_threshold,
                share_final_insight=share_final_insight,
                metadata=metadata
            )
            
            result["complexity_score"] = complexity_score
            result["used_latent_reasoning"] = True
            
            return result
        else:
            logger.info(f"Input complexity {complexity_score:.4f} below threshold, processing directly")
            
            if not hasattr(self, 'latent_space'):
                raise RuntimeError(f"Latent space not initialized for {self.__class__.__name__}.")
            
            thought_id = await self.latent_space.initialize_thought(
                thought_seed=input_content,
                metadata=metadata
            )
            
            try:
                iteration_start = time.time()
                result_content = await process_func(input_content)
                iteration_time = time.time() - iteration_start
                
                await self.latent_space.finalize_thought(
                    thought_id=thought_id,
                    final_content=result_content,
                    persist=True,
                    metadata_updates={
                        "processing_time": iteration_time,
                        "iterations_performed": 1,
                        "used_latent_reasoning": False
                    }
                )
                
                if share_final_insight:
                    await self.latent_space.share_insight(
                        thought_id=thought_id,
                        summary=f"Direct processing for simple input (complexity: {complexity_score:.4f})"
                    )
                
                return {
                    "result": result_content,
                    "iterations": 1,
                    "thought_id": thought_id,
                    "complexity_score": complexity_score,
                    "used_latent_reasoning": False,
                    "trace": await self.latent_space.get_reasoning_trace(thought_id, include_iterations=True)
                }
                
            except Exception as e:
                logger.error(f"Error in direct processing: {e}")
                raise
    
    async def close_latent_space(self):
        """Clean up latent space resources."""
        if hasattr(self, 'latent_space'):
            try:
                await self.latent_space.close()
                logger.info(f"Closed latent space for {self.component_id}")
            except Exception as e:
                logger.error(f"Error closing latent space: {e}")


# Simple implementation to demonstrate usage
class SimpleLatentComponent:
    """Simple component demonstrating latent reasoning integration."""
    
    def __init__(self, component_id: str):
        self.component_id = component_id
        
    async def process(self, input_content: str) -> str:
        """Simple processing function."""
        return f"Processed: {input_content}"
        
    async def analyze_complexity(self, input_content: str) -> float:
        """Simple complexity analyzer."""
        # Basic heuristic: length-based complexity
        return min(len(input_content) / 500, 1.0)
        
    async def process_with_confidence(self, input_content: str) -> Dict[str, Any]:
        """Processing function that returns confidence."""
        return {
            "result": f"Processed: {input_content}",
            "confidence": 0.5 + (len(input_content) % 10) / 20.0  # Simple variability
        }