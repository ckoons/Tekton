"""
API endpoints for Sophia integration
Enables theory-experiment collaboration between Noesis and Sophia
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..core.integration import SophiaBridge, CollaborationProtocol
from ..models.experiment import TheoryDrivenExperiment, TheoryValidationResult

logger = logging.getLogger(__name__)

# Create router for Sophia integration
router = APIRouter(prefix="/api/sophia", tags=["sophia_integration"])

# Initialize Sophia bridge
sophia_bridge = SophiaBridge()


# Request/Response models
class TheoryValidationRequest(BaseModel):
    """Request to validate theoretical predictions"""
    theoretical_prediction: Dict[str, Any] = Field(
        description="Theoretical model predictions"
    )
    confidence_intervals: Dict[str, Any] = Field(
        description="Confidence intervals for predictions"
    )
    suggested_metrics: List[str] = Field(
        description="Metrics to validate"
    )
    experiment_name: Optional[str] = Field(
        None,
        description="Custom name for the experiment"
    )


class HypothesisGenerationRequest(BaseModel):
    """Request to generate hypothesis from analysis"""
    analysis_results: Dict[str, Any] = Field(
        description="Results from Noesis analysis"
    )
    analysis_type: str = Field(
        description="Type of analysis performed"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context"
    )


class ExperimentInterpretationRequest(BaseModel):
    """Request to interpret experiment results"""
    experiment_id: str = Field(
        description="Sophia experiment ID"
    )
    theoretical_context: Dict[str, Any] = Field(
        description="Theoretical framework context"
    )


class IterativeRefinementRequest(BaseModel):
    """Request to start iterative refinement cycle"""
    initial_theory: Dict[str, Any] = Field(
        description="Initial theoretical model"
    )
    max_iterations: int = Field(
        5,
        description="Maximum refinement iterations",
        ge=1,
        le=10
    )
    convergence_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom convergence criteria"
    )


# Endpoints
@router.post("/validate-theory", response_model=Dict[str, Any])
async def validate_theory(
    request: TheoryValidationRequest,
    background_tasks: BackgroundTasks
):
    """
    Create theory validation protocol with Sophia
    
    Submits theoretical predictions to Sophia for experimental validation
    """
    try:
        protocol = await sophia_bridge.create_theory_validation_protocol(
            theoretical_prediction=request.theoretical_prediction,
            confidence_intervals=request.confidence_intervals,
            suggested_metrics=request.suggested_metrics
        )
        
        # Schedule background monitoring
        background_tasks.add_task(
            monitor_validation_protocol,
            protocol.protocol_id
        )
        
        return {
            "status": "success",
            "protocol": protocol.to_dict(),
            "sophia_experiment_id": protocol.experiment_component.get("experiment_id"),
            "message": "Theory validation protocol created and submitted to Sophia"
        }
        
    except Exception as e:
        logger.error(f"Theory validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-hypothesis", response_model=Dict[str, Any])
async def generate_hypothesis(request: HypothesisGenerationRequest):
    """
    Generate experimental hypothesis from theoretical analysis
    
    Converts Noesis analysis results into testable hypotheses for Sophia
    """
    try:
        result = await sophia_bridge.generate_hypothesis_from_analysis(
            analysis_results=request.analysis_results,
            analysis_type=request.analysis_type
        )
        
        return {
            "status": "success",
            "hypothesis": result["hypothesis"],
            "experiment_design": result["experiment_design"],
            "key_predictions": result["key_predictions"],
            "source_analysis": result["source_analysis"]
        }
        
    except Exception as e:
        logger.error(f"Hypothesis generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interpret-results", response_model=Dict[str, Any])
async def interpret_experiment_results(request: ExperimentInterpretationRequest):
    """
    Interpret Sophia experiment results using Noesis theory
    
    Provides theoretical interpretation and suggests model refinements
    """
    try:
        interpretation = await sophia_bridge.interpret_experiment_results(
            experiment_id=request.experiment_id,
            theoretical_context=request.theoretical_context
        )
        
        return {
            "status": "success",
            "interpretation": interpretation,
            "validation_status": interpretation["validation_status"],
            "insights": interpretation["insights"],
            "suggested_refinements": interpretation["suggested_refinements"]
        }
        
    except Exception as e:
        logger.error(f"Result interpretation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/iterative-refinement", response_model=Dict[str, Any])
async def start_iterative_refinement(
    request: IterativeRefinementRequest,
    background_tasks: BackgroundTasks
):
    """
    Start iterative theory-experiment refinement cycle
    
    Creates a cycle of theory refinement based on experimental feedback
    """
    try:
        cycle_config = await sophia_bridge.create_iterative_refinement_cycle(
            initial_theory=request.initial_theory,
            max_iterations=request.max_iterations
        )
        
        # Schedule background refinement process
        background_tasks.add_task(
            run_refinement_cycle,
            cycle_config["cycle_id"]
        )
        
        return {
            "status": "success",
            "cycle_config": cycle_config,
            "message": f"Started refinement cycle {cycle_config['cycle_id']}"
        }
        
    except Exception as e:
        logger.error(f"Refinement cycle error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/protocols", response_model=List[Dict[str, Any]])
async def get_active_protocols():
    """Get all active theory-experiment protocols"""
    try:
        protocols = [
            protocol.to_dict() 
            for protocol in sophia_bridge.active_protocols.values()
        ]
        
        return protocols
        
    except Exception as e:
        logger.error(f"Error fetching protocols: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/protocols/{protocol_id}", response_model=Dict[str, Any])
async def get_protocol(protocol_id: str):
    """Get specific theory-experiment protocol"""
    try:
        if protocol_id not in sophia_bridge.active_protocols:
            raise HTTPException(
                status_code=404,
                detail=f"Protocol {protocol_id} not found"
            )
        
        protocol = sophia_bridge.active_protocols[protocol_id]
        return protocol.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching protocol: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiment-from-theory", response_model=Dict[str, Any])
async def create_experiment_from_theory(experiment: TheoryDrivenExperiment):
    """
    Create Sophia experiment from theoretical model
    
    Directly creates an experiment in Sophia based on theoretical predictions
    """
    try:
        # Convert to Sophia experiment format
        sophia_experiment = {
            "name": experiment.name,
            "description": experiment.description,
            "experiment_type": experiment.experiment_type,
            "target_components": experiment.target_components,
            "hypothesis": f"Theory-driven: {experiment.predictions}",
            "metrics": experiment.suggested_metrics,
            "parameters": {
                **experiment.parameters,
                "theoretical_basis": experiment.theoretical_basis,
                "predictions": experiment.predictions,
                "validation_criteria": experiment.validation_criteria
            },
            "tags": ["theory_driven", "noesis_generated"]
        }
        
        # Submit to Sophia
        protocol_id = f"direct_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        experiment_id = await sophia_bridge._submit_experiment_to_sophia(
            sophia_experiment,
            protocol_id
        )
        
        if experiment_id:
            return {
                "status": "success",
                "experiment_id": experiment_id,
                "message": "Experiment created in Sophia"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to create experiment in Sophia"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Experiment creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_integration_status():
    """Get status of Sophia integration"""
    return {
        "status": "active",
        "sophia_url": sophia_bridge.sophia_url,
        "active_protocols": len(sophia_bridge.active_protocols),
        "protocol_types": [
            protocol.protocol_type 
            for protocol in sophia_bridge.active_protocols.values()
        ],
        "capabilities": [
            "theory_validation",
            "hypothesis_generation",
            "result_interpretation",
            "iterative_refinement"
        ]
    }


# Background tasks
async def monitor_validation_protocol(protocol_id: str):
    """Monitor validation protocol progress"""
    logger.info(f"Started monitoring protocol {protocol_id}")
    # TODO: Implement periodic checking of experiment status
    pass


async def run_refinement_cycle(cycle_id: str):
    """Run iterative refinement cycle"""
    logger.info(f"Started refinement cycle {cycle_id}")
    # TODO: Implement iterative refinement logic
    pass