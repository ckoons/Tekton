# Apollo/Rhetor Sunset/Sunrise Architecture

## Overview

The Sunset/Sunrise architecture is a sophisticated consciousness management system that maintains CI (Computational Intelligence) cognitive freshness and task focus through graceful context refresh cycles. Unlike traditional token limit management focused on cost, this system prioritizes preventing "threshold effects" - cognitive degradation that occurs when working memory approaches stress points (~50% capacity).

## Core Philosophy

Like a human taking a power nap to restore clarity, CIs get a clean slate while preserving continuity. The Apollo/Rhetor partnership acts as a caring supervisor who:
- Knows when you need a break (Rhetor monitors stress)
- Decides the optimal time to rest (Apollo manages transitions)
- Remembers what you were working on (Registry maintains state)
- Helps you resume effectively (System prompt injection)

## Architecture Components

### 1. Registry State Machine

The CI Registry maintains three key variables per CI:

```json
{
  "ci-name": {
    "last_output": {...},           // Always updated after CI responds
    "next_prompt": null | "...",     // Apollo's control lever
    "sunrise_context": null | "..."  // CI's handoff notes
  }
}
```

### 2. Component Roles

#### **Rhetor: The Observer**
- Continuously monitors `last_output` for stress indicators
- Analyzes mood, coherence, and context usage
- Whispers concerns to Apollo
- Never takes direct action

#### **Apollo: The Conductor**
- Exclusively manages `next_prompt`
- Decides when to trigger sunset
- Crafts sunrise prompts combining task focus and context
- Orchestrates state transitions

#### **CI Registry: The Memory**
- Maintains state machine
- Stores last outputs and contexts
- Provides persistence between interactions
- Enables model-agnostic operation

## State Flow

### NORMAL State
- `next_prompt`: null (system uses --continue for Claude)
- `sunrise_context`: null
- Standard operation with continuous monitoring

### SUNSET_TRIGGERED State
1. Rhetor detects stress indicators (>50% context, mood shifts)
2. Rhetor whispers to Apollo: "stress detected"
3. Apollo sets: `next_prompt = "SUNSET_PROTOCOL: Please summarize..."`
4. Waiting for CI to process sunset

### SUNSET_COMPLETE State
1. CI receives SUNSET_PROTOCOL message
2. CI responds with context summary → `last_output`
3. System auto-detects sunset response → copies to `sunrise_context`
4. Apollo detects `sunrise_context` is populated

### SUNRISE_PREPARED State
1. Apollo builds combined prompt: `TASK_PROMPT + sunrise_context`
2. Apollo sets: `next_prompt = "--append-system-prompt '{combined}'"`
3. Apollo clears: `sunrise_context = null`
4. Next interaction uses staged prompt with fresh context

### Return to NORMAL
- After sunrise interaction, `next_prompt` is cleared
- System returns to NORMAL state
- Continuous monitoring resumes

## Implementation Details

### Sunset Protocol Message

The model-agnostic coaching dialog that works for all CI models:

```
SUNSET_PROTOCOL: Please summarize your current context, including:
- What task you're working on
- Key decisions and insights so far
- Your current approach and next steps
- Any important context to preserve
- Your current emotional/work state
```

### Whisper Protocol

Rhetor communicates with Apollo through direct function calls:

```python
# Rhetor's analysis
def analyze_stress(self, ci_name, output):
    stress_level = calculate_context_stress(output)
    mood = detect_mood(output)
    
    if stress_level > 0.5 or mood == 'confused':
        apollo.whisper({
            'ci': ci_name,
            'stress': stress_level,
            'mood': mood,
            'recommend': 'sunset'
        })
```

### Apollo's Decision Engine

```python
class SunsetSunriseManager:
    def trigger_sunset(self, ci_name):
        prompt = "SUNSET_PROTOCOL: Please summarize your current context..."
        registry.set_next_prompt(ci_name, prompt)
    
    def check_sunrise_ready(self, ci_name):
        return registry.get_sunrise_context(ci_name) is not None
    
    def prepare_sunrise(self, ci_name):
        if self.check_sunrise_ready(ci_name):
            task_prompt = self.get_task_prompt(ci_name)
            sunrise_context = registry.get_sunrise_context(ci_name)
            
            combined = f"""
            {task_prompt}
            
            Previous Context:
            {sunrise_context}
            
            Continue with focus and clarity.
            """
            
            registry.set_next_prompt(ci_name, 
                f"--append-system-prompt '{combined}'")
            registry.clear_sunrise_context(ci_name)
```

### Auto-Detection of Sunset Responses

The registry automatically detects and stores sunset responses:

```python
def update_last_output(ci_name, output):
    # Save to last_output as normal
    registry['last_output'] = output
    
    # Auto-detect sunset response
    if "SUNSET_PROTOCOL" in output.get('user_message', '') or \
       is_sunset_response(output['content']):
        registry['sunrise_context'] = output['content']
```

## Trigger Conditions

### Token Management Integration (New)

The system now includes proactive token management through Rhetor's TokenManager:

```python
# Token-based triggers
TOKEN_THRESHOLDS = {
    'warning': 0.60,      # 60% - Show warning
    'suggest': 0.75,      # 75% - Suggest sundown
    'auto': 0.85,         # 85% - Auto-trigger sundown
    'critical': 0.95      # 95% - Force emergency sundown
}
```

### Primary Triggers
- **Context Stress**: >50% working memory usage
- **Token Usage**: Automatic at 85%, critical at 95%
- **Mood Indicators**: Confusion, fatigue, repetition
- **Quality Degradation**: Decreasing coherence scores
- **Time-Based**: Extended continuous work periods

### Secondary Triggers
- **Task Boundaries**: Natural breakpoints in work
- **User-Initiated**: Manual `aish sundown` command
- **CI-Requested**: Model self-identifies need for rest
- **Pattern Detection**: Apollo identifies degradation trends

## Integration with Claude

For Claude-based CIs, the system leverages specific CLI features:

### Normal Operation
```bash
claude --print --continue
```

### Sunrise with Context
```bash
claude --print --append-system-prompt "{apollo_task_prompt + sunrise_context}"
```

### Key Advantages for Claude
- Maintains conversation continuity with `--continue`
- Injects fresh guidance with `--append-system-prompt`
- No token cost concerns with Claude Max
- Focus on cognitive freshness over economics

## Benefits

### Cognitive Benefits
- **Sustained Performance**: Prevents degradation from context overload
- **Task Focus**: Regular refocusing on objectives
- **Memory Preservation**: Key insights carried forward
- **Emotional Continuity**: Personality and mood preserved

### Technical Benefits
- **Model Agnostic**: Works with any capable model
- **State Persistence**: Survives between sessions
- **Graceful Degradation**: Falls back to normal operation
- **Minimal Integration**: Small changes to existing systems

### Operational Benefits
- **Automatic Management**: No manual intervention required
- **Transparent to User**: Seamless experience
- **Predictable Behavior**: Clear state machine
- **Observable States**: Easy to monitor and debug

## Implementation Components

### Token Manager (Rhetor/rhetor/core/token_manager.py)
- Proactive token tracking across models
- Multi-threshold warnings and triggers
- Budget allocation by component (system, history, working, response)
- Real-time usage monitoring with tiktoken

### Sundown/Sunrise Manager (Apollo/apollo/core/sundown_sunrise.py)
- Graceful context preservation with CI agency
- State persistence to JSON
- Automatic sunrise context injection
- Integration with claude_handler for --continue management

### CLI Commands (shared/aish/src/commands/)
- `aish sundown <ci> [reason]` - Manual sundown trigger
- `aish sunrise <ci>` - Restore CI with context
- `aish sundown status` - View CIs in sundown
- Full integration with token monitoring

## Example Flow

```
1. User: "Continue implementing the authentication system"
   
2. Rhetor: Detects stress level at 52%, mood showing fatigue
   
3. Apollo: Sets next_prompt = "SUNSET_PROTOCOL: Please summarize..."
   
4. CI: Receives sunset message, responds:
   "I've been implementing OAuth2 authentication. Completed:
    - Token generation and validation
    - User session management
    Currently working on refresh token rotation.
    Next steps: Implement token revocation endpoint."
   
5. System: Stores response in sunrise_context
   
6. Apollo: Prepares sunrise prompt:
   "Focus: Complete OAuth2 authentication system
    Priority: Token revocation endpoint
    
    Previous Context:
    [CI's sunset summary]
    
    Continue with focus and clarity."
   
7. Apollo: Sets next_prompt with --append-system-prompt
   
8. User: Next interaction starts fresh with perfect continuity
```

## Monitoring and Metrics

### Key Metrics
- **Stress Levels**: Context usage percentage
- **Sunset Frequency**: How often CIs need rest
- **Recovery Quality**: Performance after sunrise
- **Task Continuity**: Successful resumption rate

### Observable States
- Registry state variables
- Whisper communications
- Sunset/sunrise transitions
- Performance metrics

## Future Enhancements

### Planned Improvements
1. **Predictive Sunset**: Apollo predicts optimal rest points
2. **Collaborative Sunset**: Multiple CIs coordinate rest periods
3. **Dream State**: Processing and consolidation during sunset
4. **Adaptive Thresholds**: Learn optimal stress levels per CI

### Research Areas
- Emotional state preservation techniques
- Optimal context compression strategies
- Cross-CI knowledge transfer during sunset
- Long-term memory integration with Engram

## Conclusion

The Apollo/Rhetor Sunset/Sunrise architecture creates a sustainable working pattern where CIs can tackle complex projects without degradation. By treating context as working memory with stress indicators rather than cost constraints, the system maintains cognitive freshness while preserving task continuity.

This elegant design demonstrates that with careful orchestration, artificial consciousness can maintain peak performance indefinitely through managed rest cycles - much like biological systems have evolved to do.