# Sophia Analysis Summary

**Generated**: 2025-06-21T17:26:49.074472

## Statistics
- Files analyzed: 43
- Functions: 425
- Classes: 76
- Landmarks identified: 410
- API endpoints: 68
- MCP tools: 0

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/client.py
- SophiaClient (line 27): Class definition
- SophiaClient.close (line 64): Async function
- SophiaClient.is_available (line 72): Async function
- SophiaClient.submit_metric (line 94): Async function
- SophiaClient.submit_metrics_batch (line 130): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/examples/client_usage.py
- submit_metrics_example (line 30): Async function
- query_metrics_example (line 76): Async function
- experiment_example (line 103): Async function
- recommendation_example (line 145): Async function
- intelligence_measurement_example (line 181): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/scripts/check_impl_status.py
- check_core_components (line 63): Public function
- check_dependencies (line 103): Public function
- check_shared_utilities (line 119): Public function
- check_sophia_utils (line 135): Public function
- check_ui_components (line 157): Public function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/ml_engine.py
- ModelRegistry (line 16): Class definition
- ModelRegistry.register_model (line 31): Async function
- ModelRegistry.load_model (line 69): Async function
- ModelRegistry.unload_model (line 97): Async function
- ModelRegistry.get_model_info (line 122): Public function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/intelligence_measurement.py
- IntelligenceMeasurer (line 24): Class definition
- IntelligenceMeasurer.measure_language_processing (line 38): Async function
- IntelligenceMeasurer.measure_reasoning (line 116): Async function
- IntelligenceMeasurer.measure_knowledge (line 194): Async function
- IntelligenceMeasurer.measure_learning (line 272): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/metrics_engine.py
- MetricsStore (line 18): Class definition
- MetricsStore.store_metric (line 43): Async function
- MetricsStore.query_metrics (line 79): Async function
- MetricsStore.aggregate_metrics (line 132): Async function, High complexity
- MetricsEngine (line 510): Class definition

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/analysis_engine.py
- AnalysisEngine (line 22): Class definition
- AnalysisEngine.initialize (line 39): Async function
- AnalysisEngine.start (line 58): Async function
- AnalysisEngine.stop (line 81): Async function
- AnalysisEngine.analyze_metric_patterns (line 100): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/experiment_framework.py
- ExperimentRunner (line 23): Class definition
- ExperimentRunner.run (line 43): Async function, High complexity
- ExperimentFramework (line 1270): Class definition
- ExperimentFramework.initialize (line 1286): Async function
- ExperimentFramework.start (line 1306): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/pattern_detection.py
- PatternType (line 24): Class definition
- PatternConfidence (line 37): Class definition
- PatternDirection (line 45): Class definition
- PatternEngine (line 53): Class definition
- PatternEngine.initialize (line 71): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/sophia_component.py
- SophiaComponent (line 10): Class definition
- SophiaComponent.get_capabilities (line 148): Public function
- SophiaComponent.get_metadata (line 159): Public function
- SophiaComponent.get_component_status (line 166): High complexity
- SophiaComponent.check_all_engines_initialized (line 196): Public function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/llm_adapter.py
- LlmAdapter (line 89): Class definition
- LlmAdapter.initialize (line 106): Async function
- LlmAdapter.get_client (line 159): Async function
- LlmAdapter.analyze_metrics (line 177): Async function
- LlmAdapter.generate_recommendations (line 239): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/recommendation_system.py
- RecommendationStatus (line 26): Class definition
- RecommendationPriority (line 36): Class definition
- RecommendationImpact (line 43): Class definition
- RecommendationSource (line 49): Class definition
- RecommendationSystem (line 59): Class definition

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/utils/tekton_utils.py
- import_tekton_utils (line 59): Public function
- has_util (line 84): Public function
- get_util (line 99): Public function
- get_config (line 116): Public function
- get_sophia_port (line 134): Public function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/utils/llm_integration.py
- SophiaLLMIntegration (line 98): Class definition
- SophiaLLMIntegration.initialize (line 131): Async function
- SophiaLLMIntegration.shutdown (line 251): Async function
- SophiaLLMIntegration.get_client (line 265): Async function
- SophiaLLMIntegration.analyze_metrics (line 318): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/models/metrics.py
- MetricSubmission (line 13): Class definition
- MetricQuery (line 24): Class definition
- MetricResponse (line 37): Class definition
- MetricAggregationQuery (line 45): Class definition
- MetricDefinition (line 57): Class definition

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/models/research.py
- ResearchApproach (line 13): Class definition
- ResearchStatus (line 25): Class definition
- ResearchProjectCreate (line 37): Class definition
- ResearchProjectUpdate (line 52): Class definition
- ResearchProjectQuery (line 66): Class definition

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/models/intelligence.py
- IntelligenceDimension (line 13): Class definition
- MeasurementMethod (line 28): Class definition
- IntelligenceMeasurementCreate (line 41): Class definition
- IntelligenceMeasurementQuery (line 56): Class definition
- IntelligenceMeasurementResponse (line 73): Class definition

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/models/recommendation.py
- RecommendationStatus (line 13): Class definition
- RecommendationPriority (line 25): Class definition
- RecommendationType (line 34): Class definition
- RecommendationCreate (line 48): Class definition
- RecommendationUpdate (line 64): Class definition

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/models/experiment.py
- ExperimentStatus (line 14): Class definition
- ExperimentType (line 27): Class definition
- ExperimentCreate (line 39): Class definition
- ExperimentUpdate (line 56): Class definition
- ExperimentQuery (line 68): Class definition

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/models/component.py
- ComponentType (line 13): Class definition
- PerformanceCategory (line 24): Class definition
- ComponentRegister (line 35): Class definition
- ComponentUpdate (line 51): Class definition
- ComponentQuery (line 66): Class definition

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/app_simple.py
- root (line 43): Async function
- health (line 52): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/app_enhanced.py
- get_component_ports (line 55): Public function
- get_session (line 165): Async function
- cleanup_session (line 173): Async function
- save_health_data (line 180): Async function, Has side effects
- cancel_background_task (line 195): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/fastmcp_endpoints.py
- MCPRequest (line 32): Class definition
- MCPResponse (line 38): Class definition
- get_ml_status (line 71): Async function
- execute_research_workflow (line 100): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/app.py
- startup_callback (line 62): Async function
- ready (line 104): Async function
- discovery (line 119): Async function
- health (line 147): Async function
- websocket_endpoint (line 172): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/mcp/hermes_bridge.py
- SophiaMCPBridge (line 17): Class definition
- SophiaMCPBridge.initialize (line 32): Async function
- SophiaMCPBridge.register_default_tools (line 57): Async function
- SophiaMCPBridge.register_fastmcp_tools (line 72): Async function
- SophiaMCPBridge.register_fastmcp_tool (line 85): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/mcp/tools.py
- SophiaMLAnalysisTools (line 17): Class definition
- SophiaMLAnalysisTools.analyze_component_performance (line 21): Public function
- SophiaMLAnalysisTools.extract_patterns (line 61): High complexity
- SophiaMLAnalysisTools.predict_optimization_impact (line 115): Public function
- SophiaMLAnalysisTools.design_ml_experiment (line 171): Public function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/mcp/__init__.py
- get_all_capabilities (line 21): Public function
- get_all_tools (line 30): Public function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/core/mcp/capabilities.py
- MLAnalysisCapability (line 12): Class definition
- MLAnalysisCapability.get_supported_operations (line 20): Public function
- MLAnalysisCapability.get_capability_metadata (line 32): Public function
- ResearchManagementCapability (line 46): Class definition
- ResearchManagementCapability.get_supported_operations (line 54): Public function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/endpoints/metrics.py
- explain_metrics (line 29): Async function
- submit_metric (line 55): Async function
- query_metrics (line 87): Async function
- aggregate_metrics (line 125): Async function
- get_available_metrics (line 140): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/endpoints/research.py
- create_research_project (line 33): Async function
- query_research_projects (line 64): Async function
- get_research_project (line 103): Async function
- update_research_project (line 127): Async function
- create_csa_analysis (line 156): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/endpoints/recommendations.py
- analyze_with_llm (line 32): Async function
- generate_recommendations_with_llm (line 54): Async function
- generate_component_recommendations (line 78): Async function
- create_recommendation (line 107): Async function
- query_recommendations (line 139): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/endpoints/intelligence.py
- create_intelligence_measurement (line 30): Async function
- query_intelligence_measurements (line 61): Async function
- get_component_intelligence_profile (line 108): Async function
- compare_component_intelligence (line 136): Async function
- get_intelligence_dimensions (line 170): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/endpoints/experiments.py
- design_experiment_with_llm (line 31): Async function
- create_experiment (line 55): Async function
- query_experiments (line 88): Async function
- get_experiment (line 127): Async function
- update_experiment (line 150): Async function

### /Users/cskoons/projects/github/Tekton/Sophia/sophia/api/endpoints/components.py
- register_component (line 31): Async function
- query_components (line 68): Async function
- get_component (line 109): Async function
- update_component (line 133): Async function
- analyze_component_performance (line 162): Async function
