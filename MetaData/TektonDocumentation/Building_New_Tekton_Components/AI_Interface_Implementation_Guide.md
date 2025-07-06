# AI Interface Implementation Guide

## Overview

This guide provides comprehensive instructions for implementing AI interfaces in Tekton components. Every Tekton component should leverage AI capabilities to enhance user experience, automate complex tasks, and provide intelligent insights.

**Important Update (June 2025)**: This guide has been updated to use the new unified AI system. All examples now use the real AI infrastructure in `/Tekton/shared/ai/` that connects to Greek Chorus AIs on ports 45000-50000.

## Core AI Integration Points

### 1. Chat Interface (Primary AI Interaction)

The chat interface is the primary way users interact with AI in your component. It's provided by the Tekton LLM Client and integrates seamlessly with Hephaestus.

#### Basic Setup

```javascript
// In your component's initialization
initializeChat() {
    const chatContainer = document.getElementById('mycomponent-chat-container');
    if (chatContainer && window.TektonLLMClient) {
        window.TektonLLMClient.initializeChat('mycomponent', chatContainer);
    }
}
```

#### Advanced Configuration

```javascript
// Configure chat with multiple contexts and custom handlers
initializeAdvancedChat() {
    const chatConfig = {
        component: 'mycomponent',
        container: document.getElementById('mycomponent-chat-container'),
        
        // Define multiple chat contexts
        contexts: {
            main: {
                systemPrompt: `You are an AI assistant for MyComponent. 
                              Help users with operations, answer questions, 
                              and provide guidance on best practices.`,
                tools: ['analyze_data', 'execute_operation', 'get_status'],
                temperature: 0.7
            },
            help: {
                systemPrompt: `You are a helpful guide for MyComponent. 
                              Explain features, provide tutorials, and 
                              answer how-to questions.`,
                tools: ['get_documentation', 'explain_feature', 'show_example'],
                temperature: 0.5
            },
            debug: {
                systemPrompt: `You are a debugging assistant for MyComponent. 
                              Analyze errors, trace issues, and suggest fixes.`,
                tools: ['analyze_logs', 'trace_operation', 'get_metrics', 'suggest_fix'],
                temperature: 0.3
            }
        },
        
        // Event handlers
        onMessage: this.handleChatMessage.bind(this),
        onToolCall: this.handleToolCall.bind(this),
        onContextSwitch: this.handleContextSwitch.bind(this),
        
        // UI customization
        theme: 'dark',
        position: 'right',
        width: 350,
        collapsible: true
    };
    
    if (window.TektonLLMClient) {
        this.chatInterface = window.TektonLLMClient.createChat(chatConfig);
    }
}
```

### 2. MCP Tools (Programmatic AI Access)

Expose your component's functionality as MCP tools that AI agents can discover and use.

#### Basic Tool Implementation

```python
# mycomponent/api/mcp_endpoints.py
from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio

# Initialize FastMCP with dependencies
mcp = FastMCP("mycomponent", dependencies=["engram", "rhetor", "apollo"])

@mcp.tool()
async def analyze_data(
    data: str, 
    analysis_type: str = "summary",
    include_recommendations: bool = True
) -> Dict[str, Any]:
    """
    Analyze data using AI capabilities.
    
    This tool uses Rhetor's LLM capabilities to analyze data and provide insights.
    
    Args:
        data: The data to analyze (can be JSON, text, or structured data)
        analysis_type: Type of analysis - summary, insights, patterns, anomalies
        include_recommendations: Whether to include actionable recommendations
    
    Returns:
        Analysis results including insights, patterns, and recommendations
    
    Examples:
        >>> await analyze_data('{"sales": [100, 150, 120]}', "patterns")
        {"patterns": ["Upward trend with mid-period dip"], "insights": [...]}
    """
    # Use simple AI system for analysis
    from shared.ai.simple_ai import ai_send
    
    # Apollo AI is best for code/data analysis on port 45012
    ai_id = "apollo-ai"
    host = "localhost"
    port = 45012
    
    # Construct analysis prompt
    prompt = f"""
    Analyze the following data for {analysis_type}:
    
    {data}
    
    Provide:
    1. Key insights
    2. Notable patterns
    3. Potential issues or anomalies
    {"4. Actionable recommendations" if include_recommendations else ""}
    
    Format the response as structured JSON.
    """
    
    # Send analysis request to Apollo AI
    response = await ai_send(ai_id, prompt, host, port)
    
    response = await client.send_message(
        host=specialist['host'],
        port=specialist['port'],
        message=prompt,
        context={"analysis_type": analysis_type}
    )
    
    # Store analysis in Engram for future reference
    engram = mcp.get_dependency("engram")
    await engram.call_tool(
        "store_memory",
        {
            "content": response.get("response"),
            "memory_type": "analysis",
            "tags": ["mycomponent", analysis_type, "ai_analysis"],
            "metadata": {
                "original_data_hash": hash(data),
                "analysis_type": analysis_type
            }
        }
    )
    
    return {
        "analysis_type": analysis_type,
        "results": response.get("response"),
        "confidence": response.get("confidence", 0.8),
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### Advanced Tool with Multi-AI Integration

```python
@mcp.tool()
async def intelligent_optimization(
    target_metric: str,
    constraints: Dict[str, Any] = None,
    optimization_level: str = "balanced"
) -> Dict[str, Any]:
    """
    Perform intelligent optimization using multiple AI components.
    
    This advanced tool coordinates between Engram (memory), Apollo (planning),
    and Sophia (research) to provide comprehensive optimization recommendations.
    
    Args:
        target_metric: The metric to optimize (e.g., "performance", "cost", "efficiency")
        constraints: Constraints to consider during optimization
        optimization_level: aggressive, balanced, or conservative
    
    Returns:
        Comprehensive optimization plan with actions and expected outcomes
    """
    # Step 1: Gather historical patterns from Engram
    engram = mcp.get_dependency("engram")
    historical_patterns = await engram.call_tool(
        "query_memories",
        {
            "query": f"optimization results for {target_metric}",
            "memory_type": "optimization",
            "limit": 10
        }
    )
    
    # Step 2: Create optimization plan with Apollo
    apollo = mcp.get_dependency("apollo")
    optimization_plan = await apollo.call_tool(
        "plan_actions",
        {
            "goal": f"optimize {target_metric}",
            "context": {
                "historical_data": historical_patterns,
                "constraints": constraints,
                "level": optimization_level
            }
        }
    )
    
    # Step 3: Validate with Sophia's research capabilities
    sophia = mcp.get_dependency("sophia")
    research_validation = await sophia.call_tool(
        "analyze_optimization",
        {
            "plan": optimization_plan,
            "target_metric": target_metric,
            "validation_depth": "comprehensive"
        }
    )
    
    # Step 4: Use Rhetor to generate human-readable summary
    rhetor = mcp.get_dependency("rhetor")
    summary = await rhetor.call_tool(
        "generate_response",
        {
            "prompt": f"Summarize this optimization plan in clear, actionable terms: {optimization_plan}",
            "context": "optimization_summary",
            "max_length": 500
        }
    )
    
    return {
        "optimization_plan": optimization_plan,
        "validation": research_validation,
        "summary": summary.get("response"),
        "expected_improvement": research_validation.get("expected_improvement", "10-20%"),
        "risk_assessment": research_validation.get("risk_level", "low"),
        "implementation_steps": optimization_plan.get("actions", [])
    }
```

### 3. Natural Language Commands

Enable users to control your component using natural language.

```python
@mcp.tool()
async def execute_natural_command(
    command: str,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Execute a natural language command.
    
    Examples:
        - "Show me the performance metrics for the last hour"
        - "Configure the component for maximum throughput"
        - "What went wrong with the last operation?"
        - "Optimize memory usage"
    
    Args:
        command: Natural language command from the user
        context: Current component state and context
    
    Returns:
        Command execution results
    """
    # Use Rhetor to understand intent
    rhetor = mcp.get_dependency("rhetor")
    intent_analysis = await rhetor.call_tool(
        "analyze_intent",
        {
            "text": command,
            "context": "component_command",
            "possible_intents": [
                "query_data",
                "modify_configuration", 
                "analyze_problem",
                "execute_action",
                "get_help"
            ]
        }
    )
    
    intent = intent_analysis.get("intent")
    parameters = intent_analysis.get("parameters", {})
    
    # Route to appropriate handler
    if intent == "query_data":
        return await handle_data_query(parameters, context)
    elif intent == "modify_configuration":
        return await handle_configuration_change(parameters, context)
    elif intent == "analyze_problem":
        return await handle_problem_analysis(parameters, context)
    elif intent == "execute_action":
        return await handle_action_execution(parameters, context)
    else:
        return await handle_help_request(command, context)
```

## UI Components for AI

### 1. AI-Powered Command Palette

```html
<!-- Add to your component HTML -->
<div class="mycomponent__ai-command-bar">
    <div class="mycomponent__ai-input-wrapper">
        <span class="mycomponent__ai-icon">🤖</span>
        <input type="text" 
               class="mycomponent__ai-input"
               id="ai-command-input"
               placeholder="Ask AI anything about MyComponent..."
               autocomplete="off">
        <button class="mycomponent__ai-submit" onclick="submitAICommand()">
            <span>→</span>
        </button>
    </div>
    <div class="mycomponent__ai-suggestions" id="ai-suggestions"></div>
</div>
```

```javascript
// AI Command Palette implementation
class AICommandPalette {
    constructor(component) {
        this.component = component;
        this.input = document.getElementById('ai-command-input');
        this.suggestions = document.getElementById('ai-suggestions');
        this.setupEventListeners();
        this.suggestionCache = new Map();
    }
    
    setupEventListeners() {
        // Real-time AI suggestions
        this.input.addEventListener('input', 
            this.debounce(this.getAISuggestions.bind(this), 300)
        );
        
        // Handle command submission
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.executeCommand();
            }
        });
        
        // Navigate suggestions with arrow keys
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateSuggestions(e.key === 'ArrowDown' ? 1 : -1);
            }
        });
    }
    
    async getAISuggestions() {
        const query = this.input.value.trim();
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }
        
        // Check cache first
        if (this.suggestionCache.has(query)) {
            this.displaySuggestions(this.suggestionCache.get(query));
            return;
        }
        
        try {
            // Get AI-powered suggestions
            const response = await fetch(`${this.component.config.apiUrl}/api/mcp/v2/tools/call`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: 'get_command_suggestions',
                    arguments: {
                        query,
                        context: this.component.state,
                        limit: 5
                    }
                })
            });
            
            const result = await response.json();
            const suggestions = result.suggestions || [];
            
            // Cache the results
            this.suggestionCache.set(query, suggestions);
            
            // Display suggestions
            this.displaySuggestions(suggestions);
            
        } catch (error) {
            console.error('Failed to get AI suggestions:', error);
        }
    }
    
    displaySuggestions(suggestions) {
        if (!suggestions.length) {
            this.hideSuggestions();
            return;
        }
        
        this.suggestions.innerHTML = suggestions.map((s, i) => `
            <div class="mycomponent__ai-suggestion ${i === 0 ? 'selected' : ''}" 
                 data-index="${i}"
                 data-command="${s.command}">
                <div class="mycomponent__suggestion-main">
                    <span class="mycomponent__suggestion-icon">${s.icon || '💡'}</span>
                    <span class="mycomponent__suggestion-text">${s.display}</span>
                </div>
                <span class="mycomponent__suggestion-hint">${s.hint || ''}</span>
            </div>
        `).join('');
        
        this.suggestions.style.display = 'block';
        this.selectedIndex = 0;
        
        // Add click handlers
        this.suggestions.querySelectorAll('.mycomponent__ai-suggestion').forEach(el => {
            el.addEventListener('click', () => {
                this.input.value = el.dataset.command;
                this.executeCommand();
            });
        });
    }
    
    async executeCommand() {
        const command = this.input.value.trim();
        if (!command) return;
        
        // Show loading state
        this.input.disabled = true;
        this.input.classList.add('loading');
        
        try {
            // Execute via MCP
            const response = await fetch(`${this.component.config.apiUrl}/api/mcp/v2/tools/call`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: 'execute_natural_command',
                    arguments: {
                        command,
                        context: this.component.state
                    }
                })
            });
            
            const result = await response.json();
            
            // Handle the result
            this.handleCommandResult(result);
            
            // Clear input
            this.input.value = '';
            this.hideSuggestions();
            
        } catch (error) {
            console.error('Command execution failed:', error);
            this.showError('Failed to execute command');
        } finally {
            this.input.disabled = false;
            this.input.classList.remove('loading');
        }
    }
    
    handleCommandResult(result) {
        // Update UI based on command result
        if (result.action === 'navigate') {
            this.component.switchTab(result.target);
        } else if (result.action === 'display') {
            this.component.displayData(result.data);
        } else if (result.action === 'notify') {
            this.component.showNotification(result.message);
        }
        
        // Show command feedback
        this.showCommandFeedback(result);
    }
}
```

### 2. AI Insights Panel

```html
<!-- AI Insights Panel -->
<div class="mycomponent__ai-insights-panel">
    <div class="mycomponent__panel-header">
        <h3>AI Insights</h3>
        <div class="mycomponent__insight-controls">
            <select id="insight-timeframe" onchange="updateInsightTimeframe()">
                <option value="1h">Last Hour</option>
                <option value="24h" selected>Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
            </select>
            <button class="mycomponent__btn--small" onclick="refreshInsights()">
                Refresh
            </button>
        </div>
    </div>
    
    <div class="mycomponent__insights-container">
        <!-- Real-time insights -->
        <div class="mycomponent__insight-card mycomponent__insight-card--live" 
             id="live-insights">
            <h4>Live Analysis</h4>
            <div class="mycomponent__live-feed">
                <!-- Real-time AI insights appear here -->
            </div>
        </div>
        
        <!-- Pattern detection -->
        <div class="mycomponent__insight-card">
            <h4>Detected Patterns</h4>
            <ul class="mycomponent__pattern-list" id="pattern-list">
                <!-- AI-detected patterns -->
            </ul>
        </div>
        
        <!-- Predictions -->
        <div class="mycomponent__insight-card">
            <h4>Predictions</h4>
            <div class="mycomponent__predictions" id="ai-predictions">
                <!-- AI predictions -->
            </div>
        </div>
        
        <!-- Recommendations -->
        <div class="mycomponent__insight-card">
            <h4>AI Recommendations</h4>
            <div class="mycomponent__recommendations" id="ai-recommendations">
                <!-- Actionable recommendations -->
            </div>
        </div>
    </div>
</div>
```

### 3. Conversational Configuration

```javascript
// AI-powered configuration assistant
class ConfigurationAssistant {
    constructor(component) {
        this.component = component;
        this.currentStep = 0;
        this.configData = {};
        this.conversation = [];
    }
    
    async startConfiguration(configType) {
        // Initialize conversation with AI
        const response = await this.callAI('start_configuration', {
            type: configType,
            current_config: this.component.config,
            user_level: 'intermediate' // Could be detected/asked
        });
        
        this.conversation.push({
            role: 'assistant',
            content: response.greeting,
            timestamp: new Date()
        });
        
        this.showConversation();
        this.askNextQuestion(response.first_question);
    }
    
    async processUserResponse(response) {
        // Add to conversation
        this.conversation.push({
            role: 'user',
            content: response,
            timestamp: new Date()
        });
        
        // Process with AI
        const aiResponse = await this.callAI('process_config_response', {
            response,
            conversation: this.conversation,
            partial_config: this.configData,
            step: this.currentStep
        });
        
        // Update config data
        if (aiResponse.extracted_values) {
            Object.assign(this.configData, aiResponse.extracted_values);
        }
        
        // Add AI response to conversation
        this.conversation.push({
            role: 'assistant',
            content: aiResponse.message,
            timestamp: new Date()
        });
        
        // Continue or complete
        if (aiResponse.complete) {
            this.completeConfiguration();
        } else {
            this.askNextQuestion(aiResponse.next_question);
        }
    }
    
    showConversation() {
        const container = document.getElementById('config-conversation');
        container.innerHTML = this.conversation.map(msg => `
            <div class="mycomponent__chat-message mycomponent__chat-message--${msg.role}">
                <div class="mycomponent__message-content">${msg.content}</div>
                <div class="mycomponent__message-time">
                    ${new Date(msg.timestamp).toLocaleTimeString()}
                </div>
            </div>
        `).join('');
        
        container.scrollTop = container.scrollHeight;
    }
}
```

## Best Practices

### 1. Context-Aware AI

Always provide rich context to AI for better responses:

```python
@mcp.tool()
async def get_contextual_help(topic: str) -> Dict[str, Any]:
    """Provide context-aware help using AI."""
    
    # Gather comprehensive context
    context = {
        "component_state": await get_component_state(),
        "recent_actions": await get_recent_actions(limit=10),
        "error_history": await get_recent_errors(hours=1),
        "user_preferences": await get_user_preferences(),
        "current_performance": await get_performance_metrics()
    }
    
    # Use context for better AI responses
    rhetor = mcp.get_dependency("rhetor")
    response = await rhetor.call_tool(
        "generate_contextual_help",
        {
            "topic": topic,
            "context": context,
            "personalization_level": "high"
        }
    )
    
    return response
```

### 2. Progressive AI Enhancement

Start with basic AI features and progressively enhance:

```javascript
class ProgressiveAI {
    constructor(component) {
        this.component = component;
        this.aiLevel = this.detectAILevel();
        this.initializeAI();
    }
    
    detectAILevel() {
        // Detect user's comfort with AI
        const stored = localStorage.getItem('ai_comfort_level');
        if (stored) return stored;
        
        // Default based on usage patterns
        return 'intermediate';
    }
    
    initializeAI() {
        switch(this.aiLevel) {
            case 'beginner':
                this.setupBasicAI();
                break;
            case 'intermediate':
                this.setupBasicAI();
                this.setupIntermediateAI();
                break;
            case 'advanced':
                this.setupBasicAI();
                this.setupIntermediateAI();
                this.setupAdvancedAI();
                break;
        }
    }
    
    setupBasicAI() {
        // Simple suggestions and help
        this.enableAISuggestions();
        this.enableContextualHelp();
    }
    
    setupIntermediateAI() {
        // Natural language commands
        this.enableNaturalCommands();
        this.enableSmartAutomation();
    }
    
    setupAdvancedAI() {
        // Predictive features and complex automation
        this.enablePredictiveAnalytics();
        this.enableAutonomousOptimization();
        this.enableAIWorkflows();
    }
}
```

### 3. AI Feedback Loop

Implement feedback mechanisms to improve AI responses:

```python
@mcp.tool()
async def record_ai_feedback(
    interaction_id: str,
    feedback_type: str,  # helpful, not_helpful, wrong
    details: str = None
) -> Dict[str, Any]:
    """Record user feedback on AI interactions."""
    
    # Store feedback in Engram
    engram = mcp.get_dependency("engram")
    await engram.call_tool(
        "store_memory",
        {
            "content": {
                "interaction_id": interaction_id,
                "feedback": feedback_type,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            },
            "memory_type": "ai_feedback",
            "tags": ["feedback", feedback_type]
        }
    )
    
    # If negative feedback, trigger improvement flow
    if feedback_type in ["not_helpful", "wrong"]:
        await trigger_ai_improvement(interaction_id, feedback_type, details)
    
    return {"status": "feedback_recorded", "thank_you": True}
```

### 4. Performance Optimization

Cache AI responses and use appropriate models:

```python
class AICache:
    def __init__(self, ttl=3600):
        self.cache = {}
        self.ttl = ttl
    
    async def get_or_compute(self, key, compute_func, force_refresh=False):
        if not force_refresh and key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['value']
        
        # Compute new value
        value = await compute_func()
        
        # Cache it
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        
        return value

# Use in MCP tools
ai_cache = AICache(ttl=1800)  # 30 minute cache

@mcp.tool()
async def get_ai_analysis(data: str) -> Dict[str, Any]:
    """Get AI analysis with intelligent caching."""
    
    cache_key = f"analysis_{hash(data)}"
    
    async def compute_analysis():
        from shared.ai.simple_ai import ai_send
        
        # Use Apollo AI for analysis on port 45012
        response = await ai_send("apollo-ai", data, "localhost", 45012)
        
        return await client.send_message(
            host=specialist['host'],
            port=specialist['port'],
            message=f"Analyze this data: {data}"
        )
    
    return await ai_cache.get_or_compute(cache_key, compute_analysis)
```

## Testing AI Features

### 1. Mock AI Responses for Testing

```python
# test_ai_features.py
class MockAIResponses:
    @staticmethod
    async def mock_rhetor_response(tool_name, arguments):
        responses = {
            "analyze_data": {
                "analysis": "Mock analysis result",
                "confidence": 0.95
            },
            "generate_response": {
                "response": "Mock generated response",
                "tokens_used": 150
            }
        }
        return responses.get(tool_name, {"error": "Unknown tool"})

# In tests
async def test_ai_analysis():
    with patch('mcp.get_dependency') as mock_dep:
        mock_dep.return_value.call_tool = MockAIResponses.mock_rhetor_response
        
        result = await analyze_data("test data")
        assert result["results"]["analysis"] == "Mock analysis result"
```

### 2. AI Feature Flags

```javascript
// Enable/disable AI features for testing
class AIFeatureFlags {
    static flags = {
        enableNaturalCommands: true,
        enablePredictiveAnalytics: false,
        enableAutoOptimization: false,
        mockAIResponses: false  // For testing
    };
    
    static isEnabled(feature) {
        return this.flags[feature] ?? false;
    }
    
    static mock(feature, enabled) {
        const original = this.flags[feature];
        this.flags[feature] = enabled;
        return () => { this.flags[feature] = original; };
    }
}

// Usage
if (AIFeatureFlags.isEnabled('enableNaturalCommands')) {
    this.setupNaturalCommands();
}
```

## Troubleshooting

### Common Issues

1. **Chat Interface Not Appearing**
   - Check if `tekton-llm-client.js` is loaded
   - Verify container element exists
   - Check browser console for errors

2. **MCP Tools Not Working**
   - Ensure FastMCP is properly initialized
   - Check dependencies are available
   - Verify tool registration

3. **AI Responses Too Slow**
   - Implement caching strategies
   - Use appropriate model selection
   - Consider async/streaming responses

4. **Context Not Being Used**
   - Verify context is being passed correctly
   - Check context size limits
   - Ensure relevant context extraction

## Summary

Implementing AI interfaces in Tekton components involves:

1. **Chat Integration** - Primary user-facing AI interface
2. **MCP Tools** - Expose functionality for AI agents
3. **Natural Language** - Enable conversational control
4. **Smart UI Elements** - AI-powered interface components
5. **Multi-AI Coordination** - Leverage multiple AI services
6. **Performance Optimization** - Cache and optimize AI calls
7. **Progressive Enhancement** - Start simple, add complexity
8. **Feedback Loops** - Continuously improve AI responses

Remember: AI should enhance, not complicate. Keep the user experience simple while leveraging powerful AI capabilities behind the scenes.

## Using the Unified AI System

The examples in this guide now use the unified AI system located in `/Tekton/shared/ai/`. Key components:

1. **AISocketClient** - Handles socket communication with streaming support
2. **simple_ai** - Direct socket communication interface  
3. **Fixed port mapping** - Deterministic AI port assignment (45000 + component offset)
4. **Event System** - Real-time updates about AI availability

For more details, see:
- `/Tekton/shared/ai/socket_client.py` - Socket communication with streaming
- `/Tekton/shared/ai/simple_ai.py` - Simple AI communication interface
- `/Tekton/shared/ai/ai_service_simple.py` - Core message queue service