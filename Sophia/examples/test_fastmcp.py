#!/usr/bin/env python3
"""
Comprehensive test suite for Sophia FastMCP integration.

This test suite validates all 16 MCP tools across Sophia's three capabilities:
- ML/CI Analysis Tools (6 tools)
- Research Management Tools (6 tools)  
- Intelligence Measurement Tools (4 tools)

Expected success rate: 75%+ (12/16 tools should pass)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class SophiaFastMCPTester:
    """Test suite for Sophia FastMCP integration."""
    
    def __init__(self, base_url: str = "http://localhost:8006"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self.results = []
        
    async def cleanup(self):
        """Clean up resources."""
        await self.client.aclose()
        
    async def run_tool_test(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run a test for a specific MCP tool."""
        try:
            logger.info(f"Testing tool: {tool_name}")
            
            response = await self.client.post(
                f"/mcp/tools/{tool_name}",
                json=parameters,
                timeout=15.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ {tool_name} - SUCCESS")
                return {
                    "tool": tool_name,
                    "status": "success",
                    "response": result,
                    "error": None
                }
            else:
                logger.warning(f"✗ {tool_name} - HTTP {response.status_code}")
                return {
                    "tool": tool_name,
                    "status": "http_error",
                    "response": None,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"✗ {tool_name} - EXCEPTION: {e}")
            return {
                "tool": tool_name,
                "status": "exception",
                "response": None,
                "error": str(e)
            }
    
    async def test_health_check(self) -> bool:
        """Test if Sophia is running and healthy."""
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    # ML/CI Analysis Tools Tests (6 tools)
    
    async def test_analyze_component_performance(self):
        """Test analyze_component_performance tool."""
        parameters = {
            "component_name": "Terma",
            "metrics_data": {"cpu_usage": 0.75, "memory_usage": 0.60},
            "analysis_depth": "comprehensive"
        }
        return await self.run_tool_test("analyze_component_performance", parameters)
    
    async def test_extract_patterns(self):
        """Test extract_patterns tool."""
        parameters = {
            "data_source": "system_metrics",
            "pattern_types": ["usage", "performance", "error"],
            "time_window": "14d"
        }
        return await self.run_tool_test("extract_patterns", parameters)
    
    async def test_predict_optimization_impact(self):
        """Test predict_optimization_impact tool."""
        parameters = {
            "optimization_type": "caching",
            "target_component": "Sophia",
            "parameters": {"cache_size": "1GB", "ttl": "1h"}
        }
        return await self.run_tool_test("predict_optimization_impact", parameters)
    
    async def test_design_ml_experiment(self):
        """Test design_ml_experiment tool."""
        parameters = {
            "hypothesis": "Implementing caching will improve response times by 30%",
            "target_metrics": ["response_time", "throughput", "error_rate"],
            "experiment_duration": "4w"
        }
        return await self.run_tool_test("design_ml_experiment", parameters)
    
    async def test_analyze_ecosystem_trends(self):
        """Test analyze_ecosystem_trends tool."""
        parameters = {
            "time_range": "90d",
            "trend_categories": ["performance", "usage", "reliability", "growth"]
        }
        return await self.run_tool_test("analyze_ecosystem_trends", parameters)
    
    async def test_forecast_system_evolution(self):
        """Test forecast_system_evolution tool."""
        parameters = {
            "forecast_horizon": "12m",
            "evolution_factors": ["complexity", "performance", "user_base", "capabilities"]
        }
        return await self.run_tool_test("forecast_system_evolution", parameters)
    
    # Research Management Tools Tests (6 tools)
    
    async def test_create_research_project(self):
        """Test create_research_project tool."""
        parameters = {
            "project_title": "Tekton Component Optimization Study",
            "research_objectives": [
                "Identify performance bottlenecks",
                "Develop optimization strategies",
                "Validate improvements"
            ],
            "timeline": "6m"
        }
        return await self.run_tool_test("create_research_project", parameters)
    
    async def test_manage_experiment_lifecycle(self):
        """Test manage_experiment_lifecycle tool."""
        parameters = {
            "experiment_id": "exp_sophia_test_001",
            "action": "start_experiment",
            "parameters": {"sample_size": 1000, "duration": "2w"}
        }
        return await self.run_tool_test("manage_experiment_lifecycle", parameters)
    
    async def test_validate_optimization_results(self):
        """Test validate_optimization_results tool."""
        parameters = {
            "optimization_id": "opt_caching_001",
            "validation_criteria": [
                "performance_improvement",
                "stability_maintained",
                "resource_efficiency"
            ],
            "comparison_baseline": "pre_optimization_baseline"
        }
        return await self.run_tool_test("validate_optimization_results", parameters)
    
    async def test_generate_research_recommendations(self):
        """Test generate_research_recommendations tool."""
        parameters = {
            "research_area": "system_performance",
            "current_findings": {
                "bottlenecks": ["database_queries", "network_latency"],
                "improvement_potential": "40%"
            },
            "priority_level": "high"
        }
        return await self.run_tool_test("generate_research_recommendations", parameters)
    
    async def test_track_research_progress(self):
        """Test track_research_progress tool."""
        parameters = {
            "project_id": "proj_tekton_optimization_001",
            "progress_metrics": [
                "timeline_adherence",
                "budget_utilization",
                "milestone_completion",
                "quality_metrics"
            ]
        }
        return await self.run_tool_test("track_research_progress", parameters)
    
    async def test_synthesize_research_findings(self):
        """Test synthesize_research_findings tool."""
        parameters = {
            "research_projects": [
                "proj_perf_analysis_001",
                "proj_user_behavior_002",
                "proj_optimization_003"
            ],
            "synthesis_scope": "comprehensive"
        }
        return await self.run_tool_test("synthesize_research_findings", parameters)
    
    # Intelligence Measurement Tools Tests (4 tools)
    
    async def test_measure_component_intelligence(self):
        """Test measure_component_intelligence tool."""
        parameters = {
            "component_name": "Rhetor",
            "intelligence_dimensions": [
                "reasoning",
                "learning",
                "adaptation",
                "creativity",
                "problem_solving"
            ],
            "measurement_depth": "comprehensive"
        }
        return await self.run_tool_test("measure_component_intelligence", parameters)
    
    async def test_compare_intelligence_profiles(self):
        """Test compare_intelligence_profiles tool."""
        parameters = {
            "components": ["Terma", "Sophia", "Rhetor", "Engram"],
            "comparison_dimensions": [
                "reasoning",
                "learning",
                "adaptation",
                "problem_solving"
            ]
        }
        return await self.run_tool_test("compare_intelligence_profiles", parameters)
    
    async def test_track_intelligence_evolution(self):
        """Test track_intelligence_evolution tool."""
        parameters = {
            "component_name": "Sophia",
            "tracking_period": "60d",
            "evolution_metrics": [
                "learning_velocity",
                "adaptation_rate",
                "problem_solving_improvement",
                "knowledge_accumulation"
            ]
        }
        return await self.run_tool_test("track_intelligence_evolution", parameters)
    
    async def test_generate_intelligence_insights(self):
        """Test generate_intelligence_insights tool."""
        parameters = {
            "analysis_scope": "ecosystem_wide",
            "insight_categories": [
                "performance_insights",
                "learning_patterns",
                "optimization_opportunities",
                "future_predictions"
            ]
        }
        return await self.run_tool_test("generate_intelligence_insights", parameters)
    
    # Workflow Tests
    
    async def test_complete_research_analysis_workflow(self):
        """Test complete_research_analysis workflow."""
        parameters = {
            "research_topic": "cross_component_optimization",
            "components": ["Terma", "Sophia", "Rhetor"],
            "analysis_depth": "comprehensive",
            "include_predictions": True
        }
        
        try:
            response = await self.client.post(
                "/mcp/workflows/complete_research_analysis",
                json=parameters,
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info("✓ complete_research_analysis workflow - SUCCESS")
                return {"workflow": "complete_research_analysis", "status": "success", "response": response.json()}
            else:
                logger.warning(f"✗ complete_research_analysis workflow - HTTP {response.status_code}")
                return {"workflow": "complete_research_analysis", "status": "http_error", "error": response.text}
                
        except Exception as e:
            logger.error(f"✗ complete_research_analysis workflow - EXCEPTION: {e}")
            return {"workflow": "complete_research_analysis", "status": "exception", "error": str(e)}
    
    async def test_intelligence_assessment_workflow(self):
        """Test intelligence_assessment workflow."""
        parameters = {
            "assessment_scope": "selected_components",
            "target_components": ["Sophia", "Rhetor"],
            "assessment_depth": "detailed",
            "include_recommendations": True
        }
        
        try:
            response = await self.client.post(
                "/mcp/workflows/intelligence_assessment",
                json=parameters,
                timeout=25.0
            )
            
            if response.status_code == 200:
                logger.info("✓ intelligence_assessment workflow - SUCCESS")
                return {"workflow": "intelligence_assessment", "status": "success", "response": response.json()}
            else:
                logger.warning(f"✗ intelligence_assessment workflow - HTTP {response.status_code}")
                return {"workflow": "intelligence_assessment", "status": "http_error", "error": response.text}
                
        except Exception as e:
            logger.error(f"✗ intelligence_assessment workflow - EXCEPTION: {e}")
            return {"workflow": "intelligence_assessment", "status": "exception", "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all FastMCP tests and return comprehensive results."""
        logger.info("="*60)
        logger.info("SOPHIA FASTMCP INTEGRATION TEST SUITE")
        logger.info("="*60)
        
        # Check if Sophia is available
        logger.info("Checking Sophia availability...")
        if not await self.test_health_check():
            logger.error("❌ Sophia is not available - skipping tests")
            return {
                "overall_status": "service_unavailable",
                "sophia_available": False,
                "tests_run": 0,
                "total_tests": 18,
                "success_rate": 0.0,
                "results": []
            }
        
        logger.info("✅ Sophia is healthy")
        
        # Define all test methods
        test_methods = [
            # ML/CI Analysis Tools (6)
            self.test_analyze_component_performance,
            self.test_extract_patterns,
            self.test_predict_optimization_impact,
            self.test_design_ml_experiment,
            self.test_analyze_ecosystem_trends,
            self.test_forecast_system_evolution,
            
            # Research Management Tools (6)
            self.test_create_research_project,
            self.test_manage_experiment_lifecycle,
            self.test_validate_optimization_results,
            self.test_generate_research_recommendations,
            self.test_track_research_progress,
            self.test_synthesize_research_findings,
            
            # Intelligence Measurement Tools (4)
            self.test_measure_component_intelligence,
            self.test_compare_intelligence_profiles,
            self.test_track_intelligence_evolution,
            self.test_generate_intelligence_insights
        ]
        
        # Run individual tool tests
        logger.info(f"\nRunning {len(test_methods)} tool tests...")
        tool_results = []
        
        for i, test_method in enumerate(test_methods, 1):
            logger.info(f"[{i}/{len(test_methods)}] Running {test_method.__name__}...")
            result = await test_method()
            tool_results.append(result)
            await asyncio.sleep(0.5)  # Brief pause between tests
        
        # Run workflow tests
        logger.info("\nRunning advanced workflow tests...")
        workflow_results = [
            await self.test_complete_research_analysis_workflow(),
            await self.test_intelligence_assessment_workflow()
        ]
        
        # Combine all results
        all_results = tool_results + workflow_results
        self.results = all_results
        
        # Calculate success metrics
        successful_tests = len([r for r in all_results if r.get("status") == "success"])
        total_tests = len(all_results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Categorize results
        ml_analysis_results = tool_results[:6]
        research_mgmt_results = tool_results[6:12]
        intelligence_results = tool_results[12:16]
        
        ml_success = len([r for r in ml_analysis_results if r.get("status") == "success"])
        research_success = len([r for r in research_mgmt_results if r.get("status") == "success"])
        intelligence_success = len([r for r in intelligence_results if r.get("status") == "success"])
        workflow_success = len([r for r in workflow_results if r.get("status") == "success"])
        
        # Generate summary
        logger.info("\n" + "="*60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Successful: {successful_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"")
        logger.info(f"ML/CI Analysis Tools: {ml_success}/6 ({(ml_success/6)*100:.1f}%)")
        logger.info(f"Research Management Tools: {research_success}/6 ({(research_success/6)*100:.1f}%)")
        logger.info(f"Intelligence Tools: {intelligence_success}/4 ({(intelligence_success/4)*100:.1f}%)")
        logger.info(f"Advanced Workflows: {workflow_success}/2 ({(workflow_success/2)*100:.1f}%)")
        
        if success_rate >= 75:
            logger.info(f"🎉 SUCCESS: Sophia FastMCP integration is working well!")
        elif success_rate >= 50:
            logger.info(f"⚠️  PARTIAL: Sophia FastMCP integration has some issues")
        else:
            logger.info(f"❌ FAILURE: Sophia FastMCP integration needs attention")
        
        # Log failed tests
        failed_tests = [r for r in all_results if r.get("status") != "success"]
        if failed_tests:
            logger.info(f"\n📋 Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                test_name = test.get("tool") or test.get("workflow", "unknown")
                error = test.get("error", "Unknown error")
                logger.info(f"  ❌ {test_name}: {error}")
        
        return {
            "overall_status": "success" if success_rate >= 75 else "partial" if success_rate >= 50 else "failure",
            "sophia_available": True,
            "tests_run": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "category_results": {
                "ml_analysis": {"successful": ml_success, "total": 6, "rate": (ml_success/6)*100},
                "research_management": {"successful": research_success, "total": 6, "rate": (research_success/6)*100},
                "intelligence_measurement": {"successful": intelligence_success, "total": 4, "rate": (intelligence_success/4)*100},
                "workflows": {"successful": workflow_success, "total": 2, "rate": (workflow_success/2)*100}
            },
            "detailed_results": all_results,
            "failed_tests": failed_tests,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Main test execution function."""
    tester = SophiaFastMCPTester()
    
    try:
        # Run all tests
        results = await tester.run_all_tests()
        
        # Save detailed results to file
        with open(f"sophia_fastmcp_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        # Exit with appropriate code
        if results["overall_status"] == "success":
            exit(0)
        elif results["overall_status"] == "partial":
            exit(1)
        else:
            exit(2)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Test run interrupted by user")
        exit(130)
    except Exception as e:
        logger.error(f"💥 Unexpected error during test execution: {e}")
        exit(1)
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())