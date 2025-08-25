# Implementation Plan - Fix Metis Sprint

## Phase 1: Setup and Preparation (1 hour)

### 1.1 Environment Setup
```bash
cd /path/to/Tekton/Metis
source .venv/bin/activate  # or create if needed
pip install tekton-llm-client
```

### 1.2 Create CI Module Structure
```bash
# Create new directories
mkdir -p metis/prompt_templates
touch metis/core/llm_adapter.py
touch metis/core/task_decomposer.py
touch metis/core/complexity_analyzer.py
touch metis/core/task_orchestrator.py
```

### 1.3 Create Prompt Templates
Create JSON files in `/prompt_templates/`:
- `task_decomposition.json`
- `complexity_analysis.json`
- `dependency_detection.json`
- `task_ordering.json`

## Phase 2: Core Implementation (3 hours)

### 2.1 Implement LLM Adapter (30 mins)

**File:** `/metis/core/llm_adapter.py`

```python
"""LLM Adapter for Metis - Connects to Rhetor for CI capabilities"""

import os
import logging
from typing import Dict, List, Any, Optional
from tekton_llm_client import TektonLLMClient, load_template

logger = logging.getLogger(__name__)

class MetisLLMAdapter:
    """Adapter for LLM operations in Metis"""
    
    def __init__(self):
        self.client = TektonLLMClient(
            base_url=f"http://localhost:{os.environ.get('RHETOR_PORT', 8003)}"
        )
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load all prompt templates"""
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'prompt_templates')
        templates = {}
        for template_name in ['task_decomposition', 'complexity_analysis', 
                              'dependency_detection', 'task_ordering']:
            templates[template_name] = load_template(
                os.path.join(template_dir, f"{template_name}.json")
            )
        return templates
    
    async def decompose_task(self, task: Dict[str, Any], depth: int = 2) -> List[Dict[str, Any]]:
        """Decompose a task into subtasks using AI"""
        prompt = self.templates['task_decomposition'].render(
            task=task,
            depth=depth,
            max_subtasks=10
        )
        
        response = await self.client.chat(
            messages=[{"role": "user", "content": prompt}],
            model="claude-3-sonnet-20240229",
            response_format="json"
        )
        
        return response.get('subtasks', [])
```

### 2.2 Implement Task Decomposer (45 mins)

**File:** `/metis/core/task_decomposer.py`

```python
"""Task Decomposition Engine for Metis"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from metis.models.task import Task
from metis.models.enums import TaskStatus, Priority
from metis.core.llm_adapter import MetisLLMAdapter

logger = logging.getLogger(__name__)

class TaskDecomposer:
    """Handles AI-powered task decomposition"""
    
    def __init__(self):
        self.llm = MetisLLMAdapter()
        
    async def decompose(self, task: Task, depth: int = 2, 
                       max_subtasks: int = 10) -> List[Task]:
        """
        Decompose a task into subtasks using AI
        
        Args:
            task: The task to decompose
            depth: Maximum decomposition depth
            max_subtasks: Maximum subtasks per level
            
        Returns:
            List of generated subtask objects
        """
        # Prepare task data for LLM
        task_data = {
            'title': task.title,
            'description': task.description,
            'complexity': task.complexity_score,
            'requirements': task.requirements
        }
        
        # Get CI decomposition
        subtask_data = await self.llm.decompose_task(task_data, depth)
        
        # Convert to Task objects
        subtasks = []
        for idx, subtask_info in enumerate(subtask_data[:max_subtasks]):
            subtask = Task(
                title=subtask_info['title'],
                description=subtask_info['description'],
                parent_id=task.id,
                status=TaskStatus.TODO,
                priority=self._infer_priority(subtask_info),
                estimated_hours=subtask_info.get('estimated_hours', 0),
                tags=subtask_info.get('tags', []),
                metadata={'ai_generated': True, 'generation_depth': depth}
            )
            subtasks.append(subtask)
            
        return subtasks
    
    def _infer_priority(self, subtask_info: Dict[str, Any]) -> Priority:
        """Infer priority from subtask information"""
        # Implementation for priority inference
        indicators = subtask_info.get('description', '').lower()
        if any(word in indicators for word in ['critical', 'urgent', 'blocker']):
            return Priority.CRITICAL
        elif any(word in indicators for word in ['important', 'high']):
            return Priority.HIGH
        elif any(word in indicators for word in ['low', 'minor', 'nice-to-have']):
            return Priority.LOW
        return Priority.MEDIUM
```

### 2.3 Implement Complexity Analyzer (30 mins)

**File:** `/metis/core/complexity_analyzer.py`

```python
"""AI-powered Complexity Analysis for Metis"""

import logging
from typing import Dict, Any, List
from metis.models.complexity import ComplexityScore, ComplexityFactor
from metis.models.enums import ComplexityLevel
from metis.core.llm_adapter import MetisLLMAdapter

logger = logging.getLogger(__name__)

class ComplexityAnalyzer:
    """Analyzes task complexity using AI"""
    
    def __init__(self):
        self.llm = MetisLLMAdapter()
        
    async def analyze(self, task: Dict[str, Any]) -> ComplexityScore:
        """
        Analyze task complexity using AI
        
        Returns:
            ComplexityScore with AI-determined factors
        """
        analysis = await self.llm.analyze_complexity(task)
        
        # Create complexity factors from CI analysis
        factors = []
        for factor_data in analysis.get('factors', []):
            factor = ComplexityFactor(
                name=factor_data['name'],
                description=factor_data['description'],
                weight=factor_data['weight'],
                score=factor_data['score'],
                notes=factor_data.get('reasoning', '')
            )
            factors.append(factor)
        
        # Calculate overall score
        total_weighted = sum(f.calculate_weighted_score() for f in factors)
        total_weight = sum(f.weight for f in factors)
        overall_score = total_weighted / total_weight if total_weight > 0 else 3.0
        
        # Determine complexity level
        if overall_score <= 2:
            level = ComplexityLevel.SIMPLE
        elif overall_score <= 3.5:
            level = ComplexityLevel.MODERATE
        elif overall_score <= 4.5:
            level = ComplexityLevel.COMPLEX
        else:
            level = ComplexityLevel.VERY_COMPLEX
            
        return ComplexityScore(
            factors=factors,
            overall_score=overall_score,
            level=level.value,
            ai_analysis=analysis.get('summary', ''),
            confidence=analysis.get('confidence', 0.8)
        )
```

### 2.4 Implement MCP Tools (45 mins)

**File:** `/metis/core/mcp/tools.py`

Replace the empty lists with actual tool implementations:

```python
"""MCP Tools for Metis Task Management"""

from typing import Dict, Any, List, Optional
from tekton.mcp.fastmcp import MCPTool
from metis.core.task_decomposer import TaskDecomposer
from metis.core.complexity_analyzer import ComplexityAnalyzer

# Task Decomposition Tool
decompose_task_tool = MCPTool(
    name="decompose_task",
    description="Decompose a high-level task into subtasks using AI",
    input_schema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "ID of task to decompose"},
            "depth": {"type": "integer", "description": "Decomposition depth", "default": 2},
            "max_subtasks": {"type": "integer", "description": "Max subtasks per level", "default": 10}
        },
        "required": ["task_id"]
    },
    handler=lambda args: decompose_task_handler(args)
)

async def decompose_task_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handler for task decomposition"""
    from metis.api.routes import task_manager
    
    task = await task_manager.get_task(args['task_id'])
    if not task:
        return {"error": "Task not found"}
    
    decomposer = TaskDecomposer()
    subtasks = await decomposer.decompose(
        task, 
        depth=args.get('depth', 2),
        max_subtasks=args.get('max_subtasks', 10)
    )
    
    # Store subtasks
    created_subtasks = []
    for subtask in subtasks:
        created = await task_manager.create_task(subtask)
        created_subtasks.append(created.dict())
    
    return {
        "success": True,
        "parent_task": task.dict(),
        "subtasks": created_subtasks,
        "count": len(created_subtasks)
    }

# Complexity Analysis Tool
analyze_complexity_tool = MCPTool(
    name="analyze_task_complexity",
    description="Analyze task complexity using AI",
    input_schema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "ID of task to analyze"}
        },
        "required": ["task_id"]
    },
    handler=lambda args: analyze_complexity_handler(args)
)

async def analyze_complexity_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handler for complexity analysis"""
    from metis.api.routes import task_manager
    
    task = await task_manager.get_task(args['task_id'])
    if not task:
        return {"error": "Task not found"}
    
    analyzer = ComplexityAnalyzer()
    complexity = await analyzer.analyze(task.dict())
    
    # Update task with new complexity score
    task.complexity_score = complexity
    await task_manager.update_task(task.id, {'complexity_score': complexity.dict()})
    
    return {
        "success": True,
        "task_id": task.id,
        "complexity": complexity.dict()
    }

# Update tool lists
task_management_tools = [decompose_task_tool]
analytics_tools = [analyze_complexity_tool]
dependency_management_tools = []  # Still empty for now
telos_integration_tools = []  # Still empty for now
```

### 2.5 Add API Endpoints (30 mins)

**File:** `/metis/api/routes.py`

Add these new endpoints:

```python
# Add to existing imports
from metis.core.task_decomposer import TaskDecomposer
from metis.core.complexity_analyzer import ComplexityAnalyzer

# Add new CI endpoints
@router.post("/api/v1/tasks/{task_id}/decompose")
async def decompose_task(
    task_id: str,
    depth: int = 2,
    max_subtasks: int = 10
) -> Dict[str, Any]:
    """Decompose a task into subtasks using AI"""
    task = await task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    decomposer = TaskDecomposer()
    subtasks = await decomposer.decompose(task, depth, max_subtasks)
    
    # Create subtasks
    created = []
    for subtask in subtasks:
        result = await task_manager.create_task(subtask)
        created.append(result)
    
    return {
        "parent_task": task.dict(),
        "subtasks": [s.dict() for s in created],
        "count": len(created)
    }

@router.post("/api/v1/tasks/{task_id}/analyze-complexity")
async def analyze_task_complexity(task_id: str) -> Dict[str, Any]:
    """Analyze task complexity using AI"""
    task = await task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    analyzer = ComplexityAnalyzer()
    complexity = await analyzer.analyze(task.dict())
    
    # Update task
    task.complexity_score = complexity
    await task_manager.update_task(task_id, {'complexity_score': complexity.dict()})
    
    return {
        "task_id": task_id,
        "complexity": complexity.dict()
    }
```

### 2.6 Create Prompt Templates (30 mins)

**File:** `/metis/prompt_templates/task_decomposition.json`

```json
{
  "name": "task_decomposition",
  "version": "1.0.0",
  "description": "Decompose high-level tasks into actionable subtasks",
  "variables": ["task", "depth", "max_subtasks"],
  "template": "You are an expert project manager tasked with breaking down a high-level task into actionable subtasks.\n\nTask to decompose:\nTitle: {{task.title}}\nDescription: {{task.description}}\n\nRequirements:\n1. Create up to {{max_subtasks}} subtasks\n2. Each subtask should be actionable and specific\n3. Subtasks should cover all aspects of the parent task\n4. Estimate time for each subtask in hours\n5. Suggest appropriate tags\n\nProvide the response in JSON format:\n{\n  \"subtasks\": [\n    {\n      \"title\": \"Subtask title\",\n      \"description\": \"Detailed description\",\n      \"estimated_hours\": 4,\n      \"tags\": [\"backend\", \"api\"],\n      \"dependencies\": [\"other_subtask_title\"]\n    }\n  ]\n}"
}
```

**File:** `/metis/prompt_templates/complexity_analysis.json`

```json
{
  "name": "complexity_analysis",
  "version": "1.0.0",
  "description": "Analyze task complexity using multiple factors",
  "variables": ["task"],
  "template": "Analyze the complexity of the following task:\n\nTitle: {{task.title}}\nDescription: {{task.description}}\n\nEvaluate complexity based on these factors:\n1. Technical Complexity (1-5)\n2. Domain Knowledge Required (1-5)\n3. Dependencies and Integration (1-5)\n4. Time/Effort Required (1-5)\n5. Risk and Uncertainty (1-5)\n\nProvide analysis in JSON format:\n{\n  \"factors\": [\n    {\n      \"name\": \"Factor Name\",\n      \"description\": \"What this factor measures\",\n      \"score\": 3,\n      \"weight\": 1.0,\n      \"reasoning\": \"Why this score was given\"\n    }\n  ],\n  \"summary\": \"Overall complexity assessment\",\n  \"confidence\": 0.85\n}"
}
```

## Phase 3: Integration and Testing (1-2 hours)

### 3.1 Update Task Manager (20 mins)

Add convenience methods to `/metis/core/task_manager.py`:

```python
async def decompose_task(self, task_id: str, depth: int = 2) -> List[Task]:
    """Decompose a task using AI"""
    from metis.core.task_decomposer import TaskDecomposer
    
    task = await self.get_task(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    decomposer = TaskDecomposer()
    return await decomposer.decompose(task, depth)

async def analyze_complexity(self, task_id: str) -> ComplexityScore:
    """Analyze task complexity using AI"""
    from metis.core.complexity_analyzer import ComplexityAnalyzer
    
    task = await self.get_task(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    analyzer = ComplexityAnalyzer()
    return await analyzer.analyze(task.dict())
```

### 3.2 Create Test Suite (40 mins)

**File:** `/tests/ai/test_task_decomposer.py`

```python
import pytest
from unittest.mock import Mock, AsyncMock
from metis.core.task_decomposer import TaskDecomposer
from metis.models.task import Task

@pytest.mark.asyncio
async def test_decompose_simple_task():
    """Test decomposing a simple task"""
    # Mock LLM response
    mock_llm = Mock()
    mock_llm.decompose_task = AsyncMock(return_value=[
        {
            'title': 'Subtask 1',
            'description': 'First subtask',
            'estimated_hours': 2,
            'tags': ['setup']
        },
        {
            'title': 'Subtask 2', 
            'description': 'Second subtask',
            'estimated_hours': 3,
            'tags': ['implementation']
        }
    ])
    
    decomposer = TaskDecomposer()
    decomposer.llm = mock_llm
    
    task = Task(
        title="Build Feature X",
        description="Implement new feature X with tests"
    )
    
    subtasks = await decomposer.decompose(task, depth=1)
    
    assert len(subtasks) == 2
    assert subtasks[0].title == 'Subtask 1'
    assert subtasks[0].parent_id == task.id
    assert subtasks[0].metadata['ai_generated'] is True
```

### 3.3 Create Example Scripts (20 mins)

**File:** `/examples/ai_task_decomposition.py`

```python
#!/usr/bin/env python3
"""Example of using Metis CI task decomposition"""

import asyncio
import aiohttp
import json

async def main():
    # Create a high-level task
    async with aiohttp.ClientSession() as session:
        # Create task
        create_resp = await session.post(
            'http://localhost:8011/api/v1/tasks',
            json={
                'title': 'Implement User Authentication System',
                'description': 'Build a complete authentication system with login, '
                              'registration, password reset, and JWT tokens',
                'priority': 'high'
            }
        )
        task = await create_resp.json()
        task_id = task['id']
        
        print(f"Created task: {task['title']} (ID: {task_id})")
        
        # Decompose the task
        decompose_resp = await session.post(
            f'http://localhost:8011/api/v1/tasks/{task_id}/decompose?depth=2'
        )
        result = await decompose_resp.json()
        
        print(f"\nGenerated {result['count']} subtasks:")
        for subtask in result['subtasks']:
            print(f"  - {subtask['title']}")
            print(f"    {subtask['description'][:80]}...")
            print(f"    Estimated: {subtask.get('estimated_hours', 'N/A')} hours")
        
        # Analyze complexity
        complexity_resp = await session.post(
            f'http://localhost:8011/api/v1/tasks/{task_id}/analyze-complexity'
        )
        complexity = await complexity_resp.json()
        
        print(f"\nComplexity Analysis:")
        print(f"  Overall Score: {complexity['complexity']['overall_score']:.1f}/5")
        print(f"  Level: {complexity['complexity']['level']}")
        print(f"  Summary: {complexity['complexity'].get('ai_analysis', 'N/A')}")

if __name__ == '__main__':
    asyncio.run(main())
```

### 3.4 Documentation Updates (20 mins)

Update `/README.md` with new CI features:

```markdown
## AI-Powered Features

Metis now includes intelligent task management capabilities:

### Task Decomposition

Automatically break down high-level tasks into actionable subtasks:

```bash
curl -X POST http://localhost:8011/api/v1/tasks/{task_id}/decompose?depth=2
```

### Complexity Analysis

Get AI-powered complexity scoring:

```bash
curl -X POST http://localhost:8011/api/v1/tasks/{task_id}/analyze-complexity
```

### MCP Tools

Metis provides MCP tools for CI agents:
- `decompose_task` - Break down tasks
- `analyze_task_complexity` - Score complexity
```

## Phase 4: Validation (30 mins)

### 4.1 Test Checklist
- [ ] Run existing tests - ensure no regression
- [ ] Test task decomposition via API
- [ ] Test complexity analysis via API  
- [ ] Test MCP tool integration
- [ ] Verify Rhetor connectivity
- [ ] Check error handling
- [ ] Validate prompt outputs

### 4.2 Performance Testing
- Measure decomposition time for various task sizes
- Check memory usage during CI operations
- Verify concurrent request handling

### 4.3 Integration Testing
- Test with Rhetor running
- Test with Rhetor unavailable (graceful degradation)
- Test with other Tekton components

## Summary

This implementation plan adds CI capabilities to Metis without disrupting existing functionality. The modular approach allows for easy testing and future enhancements. Total implementation time: 4-6 hours.