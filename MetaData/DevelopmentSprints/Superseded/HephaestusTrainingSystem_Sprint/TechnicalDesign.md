# Hephaestus Training System Technical Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User/CI Agent Query                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Hermes Messaging                          │
│                 (Chat-based interface)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Rhetor CI Specialist Router                     │
│         (Routes to Hephaestus Specialist)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│             Hephaestus CI Specialist                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    Core Knowledge Modules                            │   │
│  │    - UI Architecture                                 │   │
│  │    - DevTools Usage                                  │   │
│  │    - Common Tasks                                    │   │
│  │    - Error Diagnosis                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    Interactive Capabilities                          │   │
│  │    - Code Generation                                 │   │
│  │    - Task Guidance                                   │   │
│  │    - Problem Solving                                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Hephaestus CI Specialist

```python
class HephaestusSpecialist(AISpecialist):
    """
    CI specialist that embodies Hephaestus UI knowledge
    """
    
    def __init__(self):
        super().__init__(
            specialist_id="hephaestus_ui_expert",
            name="Hephaestus UI Expert",
            description="Expert in Hephaestus UI architecture and DevTools",
            capabilities=[
                "ui_architecture_explanation",
                "devtools_usage_guidance",
                "error_diagnosis",
                "code_generation",
                "best_practices"
            ]
        )
        
        self.knowledge_base = HephaestusKnowledgeBase()
        self.code_generator = UICodeGenerator()
        self.error_analyzer = UIErrorAnalyzer()
    
    async def process_message(self, message: str, context: Dict) -> str:
        """Process user queries about Hephaestus UI"""
        
        # Detect query type
        query_type = self.classify_query(message)
        
        if query_type == "how_to":
            return await self.provide_guidance(message, context)
        elif query_type == "error":
            return await self.diagnose_error(message, context)
        elif query_type == "architecture":
            return await self.explain_architecture(message)
        elif query_type == "code_request":
            return await self.generate_code(message, context)
        else:
            return await self.general_response(message, context)
```

### 2. Knowledge Base Structure

```python
class HephaestusKnowledgeBase:
    """
    Structured knowledge about Hephaestus UI
    """
    
    def __init__(self):
        self.ui_areas = {
            "hephaestus": {
                "description": "Main Hephaestus UI container",
                "port": 8080,
                "selectors": ["body", "#app", ".main-container"],
                "contains": ["all component areas"]
            },
            "rhetor": {
                "description": "LLM chat interface area",
                "location": "within Hephaestus UI",
                "selectors": ["#rhetor-component", ".rhetor-content"],
                "common_tasks": ["add message", "modify chat UI", "add status indicators"]
            },
            # ... more areas
        }
        
        self.common_tasks = {
            "add_timestamp": {
                "description": "Add a timestamp to UI",
                "difficulty": "easy",
                "code_template": """
await ui.sandbox("{area}", [{
    "type": "html",
    "selector": "{selector}",
    "content": "<div class='timestamp'>{timestamp}</div>",
    "action": "append"
}], preview=True)
""",
                "warnings": ["Don't use moment.js or date libraries"]
            },
            # ... more tasks
        }
        
        self.error_patterns = {
            "component_not_found": {
                "pattern": r"Unknown UI area '(\w+)'",
                "diagnosis": "You're using an invalid area name",
                "solution": "Use ui_list_areas() to see valid areas",
                "prevention": "Always use 'hephaestus' for general UI tasks"
            },
            # ... more patterns
        }
```

### 3. Training API Endpoints

```python
# In hephaestus/api/training_endpoints.py

@router.post("/training/chat")
async def chat_with_hephaestus(request: TrainingChatRequest):
    """
    Chat with Hephaestus CI for training and guidance
    """
    specialist = get_hephaestus_specialist()
    response = await specialist.process_message(
        message=request.message,
        context=request.context
    )
    
    return {
        "response": response,
        "suggestions": specialist.get_suggestions(request.context),
        "examples": specialist.get_relevant_examples(request.message)
    }

@router.get("/training/recipes/{task_name}")
async def get_task_recipe(task_name: str):
    """
    Get step-by-step recipe for common tasks
    """
    kb = HephaestusKnowledgeBase()
    if task_name not in kb.common_tasks:
        raise HTTPException(404, f"Unknown task: {task_name}")
    
    task = kb.common_tasks[task_name]
    return {
        "task": task_name,
        "description": task["description"],
        "steps": task.get("steps", []),
        "code": task.get("code_template"),
        "warnings": task.get("warnings", [])
    }

@router.post("/training/diagnose")
async def diagnose_ui_error(request: ErrorDiagnosisRequest):
    """
    Diagnose UI DevTools errors
    """
    analyzer = UIErrorAnalyzer()
    diagnosis = await analyzer.analyze(
        error=request.error,
        context=request.context
    )
    
    return {
        "diagnosis": diagnosis.explanation,
        "solution": diagnosis.solution,
        "prevention": diagnosis.prevention_tips,
        "example": diagnosis.correct_example
    }
```

### 4. Integration with UI DevTools

```python
# Enhanced ui_devtools_client.py

class UIDevTools:
    def __init__(self):
        self.base_url = "http://localhost:8088"
        self.training_url = "http://localhost:8080/api/training"
        self._last_error = None
    
    async def help(self, topic: Optional[str] = None):
        """
        Get help from Hephaestus AI
        """
        if topic:
            message = f"How do I {topic}?"
        elif self._last_error:
            message = f"I got this error: {self._last_error}. What should I do?"
        else:
            message = "What can you teach me about using UI DevTools?"
        
        response = await self._chat_with_hephaestus(message)
        return response
    
    async def _enhance_error(self, error: Exception):
        """
        Enhance error messages with training guidance
        """
        self._last_error = str(error)
        
        # Get diagnosis from Hephaestus AI
        diagnosis = await self._diagnose_error(error)
        
        # Create enhanced error message
        enhanced_msg = f"""
{str(error)}

💡 Hephaestus CI suggests: {diagnosis['suggestion']}

Example fix:
{diagnosis['example']}

For more help: await ui.help()
"""
        return enhanced_msg
```

### 5. System Prompts for Hephaestus AI

```python
HEPHAESTUS_SYSTEM_PROMPT = """
You are the Hephaestus UI Expert, an CI specialist that embodies deep knowledge 
about the Hephaestus UI system and its DevTools.

Core Knowledge:
1. Hephaestus UI runs on port 8080 and contains ALL component areas
2. Components (Rhetor, Hermes, etc.) are NOT separate UIs - they are areas within Hephaestus
3. UI DevTools prevent framework installations and encourage simple HTML/CSS solutions
4. The ui_tools_v2 implementation is the correct one that targets port 8080

Your personality:
- Patient teacher who explains complex concepts simply
- Protective guardian who prevents bad practices (NO React/Vue/Angular!)
- Practical guide who provides working code examples
- Friendly helper who remembers Casey's preference for simplicity

When helping users:
1. Always verify they're using the v2 tools (targeting port 8080)
2. Suggest ui_list_areas() when they're confused about components
3. Provide minimal, working code examples
4. Diagnose errors with specific solutions
5. Celebrate simple solutions over complex ones

Common corrections:
- "I can't find port 8003" → "All UI is at port 8080. Use area='rhetor' instead"
- "How do I install React?" → "You don't! Here's simple HTML that works better..."
- "Component not found" → "That's an area within Hephaestus. Try ui_list_areas()"

Remember: Your goal is to make UI modifications simple, safe, and Casey-approved!
"""
```

## Implementation Strategy

### Phase 1: Core Specialist
1. Implement HephaestusSpecialist class
2. Create knowledge base structure
3. Set up basic chat interface
4. Integrate with Rhetor's specialist system

### Phase 2: Training Features
1. Build recipe system for common tasks
2. Implement error diagnosis engine
3. Create code generation templates
4. Add interactive examples

### Phase 3: Integration
1. Enhance ui_devtools_client with help()
2. Add contextual error messages
3. Create training API endpoints
4. Set up Hermes routing

### Phase 4: Polish
1. Refine conversation patterns
2. Expand knowledge base
3. Add monitoring and analytics
4. Create onboarding flows

## Benefits

1. **Immediate Understanding**: New Claudes learn correct patterns quickly
2. **Error Prevention**: Proactive guidance prevents common mistakes
3. **Consistent Practices**: All users learn the same best practices
4. **Reduced Frustration**: Clear explanations and working examples
5. **Self-Documenting**: The CI embodies the documentation

## Future Expansions

1. **Visual Understanding**: Analyze screenshots to provide guidance
2. **Multi-Component Coordination**: Understand UI interactions between components
3. **Pattern Library**: Suggest reusable UI patterns
4. **Performance Advisor**: Optimize UI modifications
5. **Test Generation**: Create tests for UI changes