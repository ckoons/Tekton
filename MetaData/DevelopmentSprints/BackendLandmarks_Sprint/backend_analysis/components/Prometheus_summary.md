# Prometheus Analysis Summary

**Generated**: 2025-06-21T17:26:06.148036

## Statistics
- Files analyzed: 48
- Functions: 426
- Classes: 93
- Landmarks identified: 453
- API endpoints: 69
- MCP tools: 10

## Patterns Found
- websocket
- fastapi
- async
- error_handling
- mcp
- singleton

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Prometheus/examples/client_usage.py
- demonstrate_planning_capabilities (line 29): Async function
- demonstrate_retrospective_capabilities (line 182): Async function, High complexity
- main (line 294): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/client.py
- PrometheusClient (line 19): Class definition
- PrometheusClient.close (line 86): Async function
- PrometheusClient.health_check (line 159): Async function
- PrometheusClient.create_plan (line 170): Async function
- PrometheusClient.get_plan (line 205): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/core/critical_path.py
- CriticalPathAnalyzer (line 18): Class definition
- CriticalPathAnalyzer.analyze_plan (line 37): Async function
- CriticalPathAnalyzer.visualize (line 320): Public function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/core/planning_engine.py
- PlanningEngine (line 25): Class definition
- PlanningEngine.initialize (line 43): Async function
- PlanningEngine.create_plan (line 75): Async function
- PlanningEngine.close (line 299): Async function
- main (line 306): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/core/prometheus_component.py
- PrometheusComponent (line 17): Class definition
- PrometheusComponent.get_capabilities (line 94): Public function
- PrometheusComponent.get_metadata (line 104): Public function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/utils/telos_connector.py
- TelosConnector (line 25): Class definition
- TelosConnector.initialize (line 43): Async function
- TelosConnector.get_requirements (line 94): Async function, High complexity
- TelosConnector.get_project (line 147): Async function, High complexity
- TelosConnector.create_plan_from_requirements (line 192): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/utils/rhetor_adapter.py
- RhetorLLMAdapter (line 25): Class definition
- RhetorLLMAdapter.initialize (line 43): Async function
- RhetorLLMAdapter.generate_prompt (line 94): Async function, High complexity
- RhetorLLMAdapter.breakdown_tasks (line 170): Async function, High complexity
- RhetorLLMAdapter.analyze_retrospective (line 293): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/utils/engram_connector.py
- EngramConnector (line 25): Class definition
- EngramConnector.initialize (line 43): Async function
- EngramConnector.store_execution_record (line 81): Async function, High complexity
- EngramConnector.store_retrospective (line 140): Async function, High complexity
- EngramConnector.get_historical_data (line 200): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/utils/hermes_helper.py
- register_with_hermes (line 15): Async function, Has side effects, High complexity
- prometheus_capabilities (line 134): Async function
- epimethius_capabilities (line 201): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/utils/llm_adapter.py
- PrometheusLLMAdapter (line 35): Class definition
- PrometheusLLMAdapter.generate_text (line 317): Async function
- PrometheusLLMAdapter.stream_generator (line 360): Async function
- PrometheusLLMAdapter.breakdown_tasks (line 385): Async function
- PrometheusLLMAdapter.analyze_retrospective (line 490): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/models/metrics.py
- PerformanceMetric (line 12): Class definition
- PerformanceMetric.to_dict (line 42): Public function
- PerformanceMetric.from_dict (line 60): Public function
- PerformanceMetric.create_new (line 87): Public function
- MetricSeries (line 133): Class definition

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/models/plan.py
- ResourceRequirement (line 12): Class definition
- ResourceRequirement.to_dict (line 37): Public function
- ResourceRequirement.from_dict (line 53): Public function
- Milestone (line 74): Class definition
- Milestone.to_dict (line 99): Public function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/models/task.py
- Task (line 12): Class definition
- Task.to_dict (line 48): Public function
- Task.from_dict (line 70): Public function
- Task.update_status (line 103): Public function
- Task.update_progress (line 115): Public function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/models/timeline.py
- TimelineEvent (line 14): Class definition
- TimelineEntry (line 27): Class definition
- TimelineEntry.to_dict (line 52): Public function
- TimelineEntry.from_dict (line 68): Public function
- TimelineEntry.update_dates (line 94): Public function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/models/execution.py
- ExecutionIssue (line 14): Class definition
- ExecutionIssue.to_dict (line 45): Public function
- ExecutionIssue.from_dict (line 64): Public function
- ExecutionIssue.resolve (line 93): Public function
- ExecutionIssue.mitigate (line 100): Public function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/models/improvement.py
- Improvement (line 12): Class definition
- Improvement.to_dict (line 56): Public function
- Improvement.from_dict (line 80): Public function
- Improvement.update_status (line 116): Public function
- Improvement.assign_to (line 143): Public function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/models/retrospective.py
- RetroItem (line 14): Class definition
- RetroItem.to_dict (line 37): Public function
- RetroItem.from_dict (line 52): Public function
- RetroItem.add_vote (line 72): Public function
- RetroItem.remove_vote (line 77): Public function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/models/resource.py
- Resource (line 12): Class definition
- Resource.to_dict (line 37): Public function
- Resource.from_dict (line 53): Public function
- Resource.add_skill (line 74): Public function
- Resource.remove_skill (line 80): Public function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/app_old.py
- lifespan (line 55): Async function, High complexity
- create_app (line 154): Public function
- ready (line 189): Async function
- http_exception_handler (line 244): Async function
- general_exception_handler (line 255): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/fastmcp_endpoints.py
- MCPRequest (line 31): Class definition
- MCPResponse (line 37): Class definition
- get_planning_status (line 68): Async function
- execute_analysis_workflow (line 97): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/fixed_app.py
- lifespan (line 24): Async function
- create_app (line 44): Public function
- root (line 77): Async function
- health_check (line 87): Async function
- get_status (line 97): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/app.py
- startup_callback (line 47): Async function
- create_app (line 55): Public function
- ready (line 80): Async function
- http_exception_handler (line 126): Async function
- general_exception_handler (line 137): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/core/mcp/hermes_bridge.py
- PrometheusMCPBridge (line 16): Class definition
- PrometheusMCPBridge.initialize (line 31): Async function
- PrometheusMCPBridge.register_default_tools (line 67): Async function
- PrometheusMCPBridge.register_fastmcp_tools (line 82): Async function
- PrometheusMCPBridge.register_fastmcp_tool (line 95): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/core/mcp/tools.py
- PrometheusPlanner (line 22): Class definition
- create_project_plan (line 38): Async function, MCP tool
- analyze_critical_path (line 127): Async function, High complexity, MCP tool
- optimize_timeline (line 204): Async function, MCP tool
- create_milestone (line 256): Async function, MCP tool

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/core/mcp/capabilities.py
- PlanningCapability (line 16): Class definition
- RetrospectiveAnalysisCapability (line 26): Class definition
- ResourceManagementCapability (line 36): Class definition
- ImprovementRecommendationsCapability (line 46): Class definition

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/endpoints/tasks.py
- list_tasks (line 24): Async function
- create_task (line 88): Async function
- get_task (line 150): Async function
- update_task (line 181): Async function, High complexity
- delete_task (line 255): Async function, Has side effects

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/endpoints/improvement.py
- list_improvements (line 34): Async function, High complexity
- create_improvement (line 107): Async function
- get_improvement (line 163): Async function
- update_improvement (line 185): Async function, High complexity
- update_improvement_status (line 258): Async function

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/endpoints/retrospective.py
- list_retrospectives (line 32): Async function
- create_retrospective (line 89): Async function
- get_retrospective (line 139): Async function
- update_retrospective (line 161): Async function, High complexity
- delete_retrospective (line 212): Async function, Has side effects

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/endpoints/llm_integration.py
- get_llm_adapter (line 29): Async function
- analyze_plan (line 42): Async function, High complexity
- analyze_retrospective (line 207): Async function, High complexity
- get_improvement_suggestions (line 624): Async function, High complexity
- analyze_risks (line 841): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/endpoints/planning.py
- list_plans (line 31): Async function
- create_plan (line 78): Async function
- get_plan (line 123): Async function
- update_plan (line 145): Async function, High complexity
- delete_plan (line 196): Async function, Has side effects

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/endpoints/resources.py
- list_resources (line 28): Async function
- create_resource (line 85): Async function
- get_resource (line 127): Async function
- update_resource (line 149): Async function, High complexity
- delete_resource (line 200): Async function, Has side effects, High complexity

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/endpoints/tracking.py
- get_tracking_data (line 27): Async function, High complexity
- update_tracking (line 180): Async function, Has side effects, High complexity
- get_burndown_chart (line 386): Async function, High complexity
- get_tracking_metrics (line 598): Async function, Has side effects, High complexity

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/endpoints/timelines.py
- get_timeline (line 28): Async function
- create_timeline (line 69): Async function
- update_timeline (line 153): Async function, Has side effects, High complexity
- get_gantt_chart (line 264): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/endpoints/history.py
- list_execution_records (line 33): Async function
- create_execution_record (line 86): Async function
- get_execution_record (line 164): Async function
- update_execution_record (line 186): Async function, High complexity
- get_variance_analysis (line 402): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/models/improvement.py
- ImprovementCreate (line 13): Class definition
- ImprovementUpdate (line 30): Class definition
- ImprovementStatusUpdate (line 46): Class definition
- ImprovementPatternCreate (line 53): Class definition
- ImprovementPatternUpdate (line 65): Class definition

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/models/retrospective.py
- RetroItemCreate (line 13): Class definition
- RetroItemUpdate (line 22): Class definition
- ActionItemCreate (line 31): Class definition
- ActionItemUpdate (line 43): Class definition
- RetrospectiveCreate (line 57): Class definition

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/models/shared.py
- TrackingUpdate (line 13): Class definition
- TrackingRequest (line 24): Class definition
- BurndownRequest (line 34): Class definition
- TrackingMetricsRequest (line 48): Class definition
- LLMAnalysisRequest (line 58): Class definition

### /Users/cskoons/projects/github/Tekton/Prometheus/prometheus/api/models/planning.py
- TaskCreate (line 13): Class definition
- TaskCreate.end_date_after_start_date (line 29): Public function
- TaskUpdate (line 35): Class definition
- TaskUpdate.end_date_after_start_date (line 55): Public function
- MilestoneCreate (line 61): Class definition
