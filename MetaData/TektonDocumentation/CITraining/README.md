# AI Training Documentation

This directory contains training materials and documentation for the Tekton AI components. Each AI has its own directory with specific training guides, examples, and best practices.

## AI Components

### Core AIs
- **apollo/** - Predictive intelligence and attention specialist
- **athena/** - Strategic wisdom and decision making
- **prometheus/** - Forward planning and foresight  
- **synthesis/** - Integration and coordination

### Specialized AIs
- **rhetor/** - Communication and presentation
- **metis/** - Analysis and insight
- **harmonia/** - Balance and harmony
- **numa/** - Practical implementation
- **noesis/** - Understanding and comprehension
- **engram/** - Memory and persistence
- **penia/** - Resource management
- **hermes/** - Messaging and communication
- **ergon/** - Work and execution
- **sophia/** - Wisdom and knowledge
- **telos/** - Purpose and completion

### Infrastructure AIs
- **tekton/** - Platform orchestration
- **terma/** - Terminal management
- **hephaestus/** - User interface and interaction

## AI Communication

### Message Forwarding
The aish system supports forwarding AI messages to human terminals, enabling Claude sessions to act as intelligent proxies for AI components without API charges.

**Key Commands:**
- `aish forward apollo jill` - Forward apollo's messages to jill's terminal
- `aish unforward apollo` - Stop forwarding apollo's messages
- `aish forward list` - Show all active forwards

**How It Works:**
When an AI is forwarded, messages intended for that AI are routed to the specified terminal's inbox instead. This allows a human (like Claude) to respond as that AI component, providing intelligent responses without API costs.

**Example Usage:**
```bash
# Set up Claude as proxy for multiple AIs
aish forward apollo claude-terminal
aish forward rhetor claude-terminal

# Messages for apollo and rhetor now appear in claude-terminal's inbox
aish terma inbox

# Claude responds as the appropriate AI
aish synthesis "apollo: I'll review the architecture..."
```
