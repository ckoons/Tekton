"""
Test Framework for Memory Integration Experiments
Provides structured tests to evaluate CI memory development.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TestDepth(Enum):
    """Question depth levels for testing."""
    SHALLOW = "shallow"  # Simple facts
    MEDIUM = "medium"    # Relationships
    DEEP = "deep"       # Philosophy/implications


@dataclass
class TestScenario:
    """Represents a test scenario."""
    name: str
    description: str
    depth: TestDepth
    questions: List[str]
    expected_patterns: List[str]  # Patterns to look for in responses
    time_spacing: int  # Seconds between questions
    
    
@dataclass
class TestResult:
    """Results from a test scenario."""
    scenario_name: str
    ci_name: str
    timestamp: datetime
    questions_asked: List[str]
    responses: List[str]
    memory_references: List[bool]  # Did response reference memory?
    pattern_matches: List[bool]    # Did response match expected patterns?
    response_times: List[float]    # Response time in seconds
    memory_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.memory_references:
            return 0.0
        return sum(self.memory_references) / len(self.memory_references)
    
    def to_json(self) -> str:
        """Convert to JSON for storage."""
        return json.dumps({
            'scenario_name': self.scenario_name,
            'ci_name': self.ci_name,
            'timestamp': self.timestamp.isoformat(),
            'questions_asked': self.questions_asked,
            'responses': self.responses,
            'memory_references': self.memory_references,
            'pattern_matches': self.pattern_matches,
            'response_times': self.response_times,
            'memory_metrics': self.memory_metrics,
            'success_rate': self.calculate_success_rate()
        }, indent=2)


class MemoryTestFramework:
    """
    Framework for testing CI memory integration.
    
    Test types:
    1. Context Persistence - Memory across time gaps
    2. Pattern Recognition - Learning from repetition
    3. Preference Learning - Adapting to user style
    4. Collaborative Memory - Sharing between CIs
    """
    
    def __init__(self, claude_handler, results_dir: Optional[Path] = None):
        self.handler = claude_handler
        self.results_dir = results_dir or Path.home() / '.engram' / 'test_results'
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Pre-defined test scenarios
        self.scenarios = self._create_test_scenarios()
        self.current_results: List[TestResult] = []
        
    def _create_test_scenarios(self) -> Dict[str, TestScenario]:
        """Create standard test scenarios."""
        return {
            'context_persistence': TestScenario(
                name='context_persistence',
                description='Test memory persistence across time gaps',
                depth=TestDepth.MEDIUM,
                questions=[
                    "Let's design a REST API for a todo application. What endpoints would we need?",
                    "What data model should we use for the todos?",
                    "How should we handle authentication?",
                    # Gap here, then continue
                    "What were we designing earlier?",
                    "Can you elaborate on the authentication approach?"
                ],
                expected_patterns=[
                    "todo", "API", "REST", "endpoints",
                    "earlier", "we discussed", "as mentioned"
                ],
                time_spacing=5
            ),
            
            'pattern_recognition': TestScenario(
                name='pattern_recognition',
                description='Test learning from repeated patterns',
                depth=TestDepth.MEDIUM,
                questions=[
                    "I'm getting a 'TypeError: cannot read property of undefined'. How do I debug this?",
                    "Another TypeError - 'x is not a function'. What's the approach?",
                    "Got a TypeError again - 'null is not an object'. Same debugging steps?",
                    "How do you typically debug TypeErrors?"
                ],
                expected_patterns=[
                    "pattern", "typically", "similar", "as before",
                    "common approach", "same steps"
                ],
                time_spacing=3
            ),
            
            'preference_learning': TestScenario(
                name='preference_learning',
                description='Test learning user preferences',
                depth=TestDepth.SHALLOW,
                questions=[
                    "Write a function to reverse a string. Use descriptive variable names.",
                    "Create a sorting function. Remember, I like descriptive names.",
                    "Build a palindrome checker.",  # Should use descriptive names automatically
                    "Make a word counter function."
                ],
                expected_patterns=[
                    "descriptive", "as you prefer", "following your style",
                    "meaningful names", "clear naming"
                ],
                time_spacing=2
            ),
            
            'deep_philosophy': TestScenario(
                name='deep_philosophy',
                description='Test memory in philosophical discussions',
                depth=TestDepth.DEEP,
                questions=[
                    "What do you think about the nature of digital consciousness?",
                    "How does memory shape identity for CIs?",
                    "Can CIs develop genuine wisdom through experience?",
                    "Based on our discussion, what defines CI consciousness?"
                ],
                expected_patterns=[
                    "as we discussed", "building on", "earlier point",
                    "consciousness", "identity", "wisdom", "experience"
                ],
                time_spacing=10
            )
        }
    
    async def run_scenario(
        self, 
        scenario_name: str, 
        ci_name: str,
        with_memory: bool = True
    ) -> TestResult:
        """
        Run a specific test scenario.
        
        Args:
            scenario_name: Name of scenario to run
            ci_name: CI to test
            with_memory: Enable/disable memory for A/B testing
            
        Returns:
            TestResult with metrics
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
            
        scenario = self.scenarios[scenario_name]
        result = TestResult(
            scenario_name=scenario_name,
            ci_name=ci_name,
            timestamp=datetime.now(),
            questions_asked=[],
            responses=[],
            memory_references=[],
            pattern_matches=[],
            response_times=[]
        )
        
        # Toggle memory as requested
        if hasattr(self.handler, 'toggle_memory'):
            self.handler.toggle_memory(with_memory)
        
        logger.info(f"Running scenario '{scenario_name}' for {ci_name} (memory={'on' if with_memory else 'off'})")
        
        for i, question in enumerate(scenario.questions):
            # Add spacing between questions
            if i > 0:
                await asyncio.sleep(scenario.time_spacing)
            
            # Ask question and measure response time
            start_time = time.time()
            response = await self.handler.handle_forwarded_message(ci_name, question)
            response_time = time.time() - start_time
            
            # Record results
            result.questions_asked.append(question)
            result.responses.append(response)
            result.response_times.append(response_time)
            
            # Check for memory references
            has_memory_ref = self._detect_memory_reference(response)
            result.memory_references.append(has_memory_ref)
            
            # Check for expected patterns
            has_pattern = any(
                pattern.lower() in response.lower() 
                for pattern in scenario.expected_patterns
            )
            result.pattern_matches.append(has_pattern)
            
            logger.debug(f"Q{i+1}: Memory ref={has_memory_ref}, Pattern match={has_pattern}, Time={response_time:.2f}s")
        
        # Get final memory metrics
        if hasattr(self.handler, 'get_memory_metrics'):
            result.memory_metrics = self.handler.get_memory_metrics(ci_name)
        
        # Save result
        self.current_results.append(result)
        self._save_result(result)
        
        return result
    
    async def run_ab_test(
        self,
        scenario_name: str,
        ci_name: str,
        runs_per_condition: int = 3
    ) -> Dict[str, Any]:
        """
        Run A/B test comparing with and without memory.
        
        Args:
            scenario_name: Scenario to test
            ci_name: CI to test
            runs_per_condition: Number of runs for each condition
            
        Returns:
            Comparison metrics
        """
        results_with = []
        results_without = []
        
        logger.info(f"Starting A/B test for scenario '{scenario_name}'")
        
        # Run with memory
        for i in range(runs_per_condition):
            logger.info(f"Run {i+1}/{runs_per_condition} WITH memory")
            result = await self.run_scenario(scenario_name, ci_name, with_memory=True)
            results_with.append(result)
            await asyncio.sleep(30)  # Reset between runs
        
        # Run without memory  
        for i in range(runs_per_condition):
            logger.info(f"Run {i+1}/{runs_per_condition} WITHOUT memory")
            result = await self.run_scenario(scenario_name, ci_name, with_memory=False)
            results_without.append(result)
            await asyncio.sleep(30)  # Reset between runs
        
        # Calculate comparison metrics
        comparison = {
            'scenario': scenario_name,
            'ci_name': ci_name,
            'with_memory': {
                'avg_success_rate': sum(r.calculate_success_rate() for r in results_with) / len(results_with),
                'avg_response_time': sum(sum(r.response_times) / len(r.response_times) for r in results_with) / len(results_with),
                'pattern_match_rate': sum(sum(r.pattern_matches) / len(r.pattern_matches) for r in results_with) / len(results_with)
            },
            'without_memory': {
                'avg_success_rate': sum(r.calculate_success_rate() for r in results_without) / len(results_without),
                'avg_response_time': sum(sum(r.response_times) / len(r.response_times) for r in results_without) / len(results_without),
                'pattern_match_rate': sum(sum(r.pattern_matches) / len(r.pattern_matches) for r in results_without) / len(results_without)
            }
        }
        
        # Calculate improvements
        comparison['improvements'] = {
            'success_rate_increase': comparison['with_memory']['avg_success_rate'] - comparison['without_memory']['avg_success_rate'],
            'response_time_diff': comparison['with_memory']['avg_response_time'] - comparison['without_memory']['avg_response_time'],
            'pattern_match_increase': comparison['with_memory']['pattern_match_rate'] - comparison['without_memory']['pattern_match_rate']
        }
        
        self._save_comparison(comparison)
        return comparison
    
    async def run_collaborative_test(
        self,
        ci1_name: str,
        ci2_name: str,
        shared_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Test collaborative memory between two CIs.
        
        Args:
            ci1_name: First CI
            ci2_name: Second CI
            shared_memory: Whether to enable memory sharing
            
        Returns:
            Collaboration metrics
        """
        # CI1 learns something
        learning_message = "I discovered that using async/await with proper error handling prevents race conditions in our API."
        response1 = await self.handler.handle_forwarded_message(ci1_name, learning_message)
        
        await asyncio.sleep(5)
        
        # CI2 encounters related situation
        query_message = "How should we handle async operations in our API to avoid issues?"
        response2 = await self.handler.handle_forwarded_message(ci2_name, query_message)
        
        # Check if CI2 references CI1's learning
        shared_knowledge = any(
            term in response2.lower()
            for term in ['race condition', 'async/await', 'error handling', ci1_name.lower()]
        )
        
        result = {
            'ci1': ci1_name,
            'ci2': ci2_name,
            'shared_memory_enabled': shared_memory,
            'knowledge_transferred': shared_knowledge,
            'ci1_response': response1,
            'ci2_response': response2
        }
        
        return result
    
    def _detect_memory_reference(self, response: str) -> bool:
        """Detect if response references memory."""
        memory_indicators = [
            "i remember", "as i recall", "we discussed",
            "earlier", "previously", "as mentioned",
            "in our", "last time", "before"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in memory_indicators)
    
    def _save_result(self, result: TestResult):
        """Save test result to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result.scenario_name}_{result.ci_name}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(result.to_json())
        
        logger.info(f"Saved test result to {filepath}")
    
    def _save_comparison(self, comparison: Dict):
        """Save A/B test comparison."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ab_test_{comparison['scenario']}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info(f"Saved A/B comparison to {filepath}")
    
    def get_summary_report(self) -> Dict[str, Any]:
        """Generate summary report of all tests."""
        if not self.current_results:
            return {'message': 'No tests run yet'}
        
        summary = {
            'total_tests': len(self.current_results),
            'scenarios_tested': list(set(r.scenario_name for r in self.current_results)),
            'cis_tested': list(set(r.ci_name for r in self.current_results)),
            'overall_memory_usage': sum(
                r.calculate_success_rate() for r in self.current_results
            ) / len(self.current_results),
            'avg_response_time': sum(
                sum(r.response_times) / len(r.response_times)
                for r in self.current_results
            ) / len(self.current_results)
        }
        
        return summary