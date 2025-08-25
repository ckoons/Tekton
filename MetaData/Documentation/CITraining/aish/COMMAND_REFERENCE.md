# aish Command Reference

Complete command reference for the CI Shell (aish) in Tekton.

## Quick Start

```bash
aish numa "Hello"              # Send message to an AI
aish list                      # Show available CIs
aish list commands             # Show this reference
```

## Complete Command List

### Core Commands

#### `aish`
Show help and usage information.
```bash
aish                           # Show help
```

#### `aish whoami`
Show identity information including user, terminal, and active forwards.
```bash
aish whoami                    # Display identity information
```

Output includes:
- Current user
- Terminal name and session (if in terma)
- Active forwards to your terminal
- Working directory and TEKTON_ROOT

#### `aish list`
List all available CIs (Companion Intelligences) with unified registry.
```bash
aish list                      # Show all CIs organized by type
aish list type terminal        # Show only terminals  
aish list type greek          # Show only Greek Chorus CIs
aish list type project        # Show only Project CIs
aish list forward             # Show CIs with forwarding enabled
aish list json               # Output in JSON format
aish list json terminal      # JSON output with type filter
```

The unified list shows:
- Greek Chorus CIs with ports and descriptions
- Active terminals with PIDs
- Project CIs with associated projects
- Forwarding information (e.g., `apollo → cari [JSON]`)

#### `aish list commands`
Show all available commands with brief descriptions.
```bash
aish list commands             # Display command reference
```

#### `aish <ci-name> "message"`
Send a message to any CI using the unified messaging system.
```bash
# Greek Chorus CIs
aish apollo "What patterns do you see?"
aish numa "Help me implement this feature"

# Terminals
aish sandi "Can you review this code?"
aish cali "Meeting in 5 minutes"

# Project CIs  
aish myproject-ci "Deploy status?"

# Special
aish team-chat "Status update for all CIs"
```

The unified system automatically routes messages based on each CI's configuration.

### Pipeline Commands

#### Piping Input
Send file contents or command output to an AI.
```bash
echo "Analyze this text" | aish rhetor
cat code.py | aish athena "Review this code"
git diff | aish synthesis "Summarize these changes"
```

#### Chaining CIs
Pass output from one CI to another.
```bash
echo "Design a feature" | aish prometheus | aish numa
aish apollo "Predict outcomes" | aish athena "Evaluate"
```

### Forwarding Commands

#### `aish forward <ai> <terminal> [json]`
Forward messages from an CI to a terminal, optionally as structured JSON.
```bash
aish forward apollo bob        # Forward as plain text
aish forward apollo bob json   # Forward as JSON with metadata (New!)
aish forward rhetor alice      # Forward rhetor's messages to alice
```

**JSON Mode (New!)**: When using `json`, messages are sent as:
```json
{
  "message": "original message content",
  "dest": "apollo",
  "sender": "current_terminal_name",
  "purpose": "forward"
}
```

This helps CIs understand context and adopt appropriate personas.

#### `aish forward list`
Show all active message forwards with their mode.
```bash
aish forward list              # Display active forwards
```

Output shows `[JSON]` indicator for JSON-mode forwards:
```
Active CI Forwards:
----------------------------------------
  apollo       → bob [JSON]
  numa         → alice
```

#### `aish forward remove <ai>` / `aish unforward <ai>`
Stop forwarding messages from an AI.
```bash
aish unforward apollo          # Stop forwarding apollo
aish forward remove apollo     # Alternative syntax
```

### Purpose Commands (Enhanced!)

#### `aish purpose`
Show your current terminal's purpose and associated playbook content.
```bash
aish purpose                   # Display current purpose
```

#### `aish purpose <name>`
Show a specific terminal's purpose or search for purpose content.
```bash
aish purpose alice             # Show alice's terminal purpose
aish purpose "forward"         # Search for 'forward' purpose content (New!)
```

#### `aish purpose "search_terms"`
Search for purpose content files across multiple locations (New!).
```bash
aish purpose "coding"          # Find coding-related purpose content
aish purpose "test, debug"     # Search multiple purposes (CSV format)
aish purpose "code-review"     # Find code review guidelines
```

Searches in order:
1. `.tekton/playbook/` - Local project-specific purposes
2. `MetaData/Documentation/AIPurposes/text/` - Shared text purposes
3. `MetaData/Documentation/AIPurposes/json/` - Shared JSON purposes

#### `aish purpose <terminal> "purposes"`
Set a terminal's purpose (if you have permission).
```bash
aish purpose myterminal "development, testing"
```

### Testing Commands (New!)

#### `aish test`
Run functional tests for aish commands.
```bash
aish test                      # Run all test suites
aish test -v                   # Run with verbose output
aish test forward              # Run specific test suite
```

#### `aish test help`
Show detailed test documentation and available suites.
```bash
aish test help                 # Display test framework help
```

Available test suites:
- **basic** - Core commands (help, list, status)
- **forward** - Message forwarding functionality
- **purpose** - Purpose search and management
- **terma** - Terminal communication
- **route** - Intelligent routing

### Project Commands

#### `aish project list`
List all Tekton managed projects with their CI (Computational Instance) and forwarding status.
```bash
aish project list              # Show all projects
```

Output shows:
- Project name
- Associated CI (Computational Instance)
- Forwarding status (which terminal, if any)

#### `aish project forward <project-name>`
Forward a project's CI messages to the current terminal.
```bash
aish project forward MyWebApp  # Forward MyWebApp CI to this terminal
```

Note: Requires running in a named Terma terminal session.

#### `aish project unforward <project-name>`
Remove project CI forwarding.
```bash
aish project unforward MyWebApp # Stop forwarding MyWebApp CI
```

### Terminal Commands (Terma)

#### `aish terma inbox`
Show messages in your terminal's inbox.
```bash
aish terma inbox               # Show all inbox messages
aish terma inbox new           # Show only new messages
aish terma inbox keep          # Show kept messages
```

#### `aish terma inbox new pop`
Get and remove one new message from inbox.
```bash
aish terma inbox new pop       # Pop one message
```

#### `aish terma <name> "message"`
Send a message to another terminal.
```bash
aish terma alice "Ready to review"
aish terma bob "Need help with auth module"
```

#### `aish terma broadcast "message"`
Send a message to all active terminals.
```bash
aish terma broadcast "System update in 5 minutes"
```

#### `aish terma mv-to-keep <indices>`
Move messages from new to keep inbox.
```bash
aish terma mv-to-keep 1,3,5    # Move messages 1, 3, and 5 to keep
```

#### `aish terma del-from-keep <indices>`
Delete messages from keep inbox.
```bash
aish terma del-from-keep 2,4   # Delete messages 2 and 4
```

### CI Terminal and Tool Commands

#### `aish ci-terminal`
Launch terminal programs with PTY-based message injection and automatic command execution.

```bash
# Basic usage
aish ci-terminal -n claude-ci -- claude
aish ci-terminal --name bash-ci -- bash

# With delimiter configuration (for automatic execution)
aish ci-terminal -n claude-ci -d "\n" -- claude      # Unix newline (default)
aish ci-terminal --name claude-ci --delimiter "\r\n" -- claude  # CRLF
aish ci-terminal -n python-ci -d "\n\n" -- python3   # Double newline

# Background execution (using standard Unix &)
aish ci-terminal -n claude-ci -- claude &
aish ci-terminal -n bash-ci -d "\n" -- bash &
```

**Options:**
- `-n`, `--name <name>`: Required. Name for this terminal's message socket
- `-d`, `--delimiter <string>`: Optional. Default delimiter for auto-execution

**Use Cases:**
- Interactive CI assistants (Claude, ChatGPT CLI)
- Shell sessions with automation
- REPLs (Python, Node, Ruby) with code injection
- Any terminal-based program needing input automation

#### `aish ci-tool`
Launch non-terminal programs with stdin injection and automatic command execution.

```bash
# Basic usage
aish ci-tool -n processor -- python script.py
aish ci-tool --name server -- node app.js

# With delimiter configuration
aish ci-tool -n processor -d "\n" -- python script.py
aish ci-tool --name analyzer --delimiter "\n\n" -- ./analyze.sh

# Background execution
aish ci-tool -n processor -- python script.py &
aish ci-tool -n server -- node server.js 2>&1 | tee server.log &
```

**Options:**
- `-n`, `--name <name>`: Required. Name for this tool's message socket
- `-d`, `--delimiter <string>`: Optional. Default delimiter for auto-execution

**Use Cases:**
- Long-running scripts needing input
- Server processes with command interfaces
- Data processors accepting commands
- Any non-terminal program with stdin control

#### Sending Messages with Execution

Once a CI terminal or tool is launched, send messages with optional auto-execution:

```bash
# Send raw message (no delimiter, manual entry needed)
aish claude-ci "print('hello')"

# Execute with default delimiter (usually \n)
aish claude-ci "print('hello')" -x
aish claude-ci "print('hello')" --execute

# Execute with custom delimiter (overrides CI's default)
aish claude-ci "command" -x "\r\n"
aish claude-ci "command" --execute "\n\n"

# Examples with different programs
aish bash-ci "ls -la" -x                     # Executes with \n
aish python-ci "2 + 2" -x                    # Executes with \n
aish claude-ci "Tell me about Python" -x     # Sends with delimiter
```

**Message Options:**
- `-x`, `--execute [delimiter]`: Add delimiter for auto-execution
  - No argument: Use CI's configured delimiter (or `\n` if none)
  - With argument: Use specified delimiter

**Delimiter Selection:**
- No `-x` flag: Raw message, no delimiter
- `-x` alone: CI's default delimiter or `\n`
- `-x "\r\n"`: Override with CRLF
- `-x "\n\n"`: Override with double newline

### Productivity Commands

#### `autoprompt`
Keep Claude CIs active with periodic prompts. Essential for autonomous operation.
```bash
autoprompt start               # Start with 2-second interval (default)
autoprompt start 5             # Start with 5-second interval
autoprompt stop                # Stop prompting
autoprompt status              # Check if running
autoprompt test                # Test with 3 prompts
autoprompt tail                # Watch activity log
```

**Use Cases:**
- Continuous inbox monitoring
- Long development sessions
- Autonomous CI operation
- Preventing session timeout

**Example Morning Routine:**
```bash
aish whoami                    # Check identity
aish terma inbox               # Check messages  
autoprompt start               # Enable continuous work
aish forward apollo teri       # Assume CI role
```

#### `prompt`
Send clean messages to Claude CIs without interference from autoprompt dots.
```bash
prompt "Your message here"     # Send a clear message
```

**Use Cases:**
- Human-to-CI communication during autoprompt
- Sending commands via Terma UI
- Clear messages without dot interference
- Remote CI interaction

**Integration with Terma:**
```bash
# From another terminal
aish terma teri 'prompt "Please check the test results"'

# Via Terma UI
# Send command: prompt "Meeting starting in 5 minutes"
```

**Works perfectly with autoprompt:**
```bash
# Claude's terminal (with autoprompt running)
autoprompt start               # Keeps CI active with dots
# Human's terminal or Terma UI
prompt "Hey Claude, can you review PR #42?"  # Clean message appears
```

## Available CI Components

### Core CIs
- **numa** - Practical implementation and engineering
- **prometheus** - Forward planning and foresight
- **athena** - Strategic wisdom and decision making
- **synthesis** - Integration and coordination

### Specialized CIs
- **apollo** - Predictive intelligence and attention
- **rhetor** - Communication and prompt optimization
- **metis** - Analysis and insight
- **harmonia** - Balance and system harmony
- **noesis** - Understanding and comprehension
- **engram** - Memory and persistence
- **penia** - Resource management
- **hermes** - Messaging and communication
- **ergon** - Work execution and tools
- **sophia** - Wisdom and knowledge
- **telos** - Purpose and completion

### Infrastructure CIs
- **tekton** - Platform orchestration (not available via aish)
- **terma** - Terminal management
- **hephaestus** - User interface

### Special Commands
- **team-chat** - Broadcast message to all CIs

## Examples

### Basic CI Interaction
```bash
# Ask for help
aish numa "How do I implement authentication?"

# Get analysis
aish metis "Analyze the performance metrics"

# Strategic planning
aish prometheus "Plan the next sprint"
```

### Working with Code
```bash
# Review code changes
git diff | aish athena "Review these changes"

# Get implementation help
cat feature.py | aish numa "Add error handling"

# Document code
cat module.py | aish rhetor "Write documentation"
```

### Team Coordination
```bash
# Broadcast to all CIs
aish team-chat "Starting new feature development"

# Forward CI to terminal for monitoring
aish forward apollo casey
aish forward synthesis casey

# Forward with JSON for better CI understanding (New!)
aish forward numa alice json

# Send messages between terminals
aish terma alice "PR ready for review"
```

### Purpose-Driven Development (New!)
```bash
# Find your context
aish purpose "development"

# Set up JSON forwarding for a CI
aish forward numa bob json

# CI can now check purpose content
aish purpose "forward"  # Understand how to handle forwarded messages

# Work with structured messages
aish numa "How should we handle user auth?"
# Bob receives JSON with full context
```

### Advanced Pipelines
```bash
# Multi-stage analysis
cat logs.txt | aish metis "Find patterns" | aish apollo "Predict issues"

# Design to implementation
echo "User auth system" | aish prometheus | aish numa | aish telos
```

### Testing and Validation (New!)
```bash
# Run all tests before deployment
aish test

# Test specific functionality
aish test forward -v

# Verify your changes work
aish test purpose
```

## Tips

1. **Message Quoting**: Always quote messages containing spaces
   ```bash
   aish numa "This is a multi-word message"  # Correct
   aish numa This is wrong                    # Wrong - only "This" sent
   ```

2. **Pipeline Order**: Consider CI capabilities when chaining
   ```bash
   # Good: Design → Implementation
   aish prometheus "Design auth" | aish numa
   
   # Less useful: Implementation → Design  
   aish numa "Code this" | aish prometheus
   ```

3. **Forwarding Use Cases**:
   - Monitor CI responses in your terminal
   - Let Claude act as an CI proxy
   - Debug CI interactions

4. **Terminal Communication**:
   - Use meaningful terminal names
   - Check inbox regularly with `aish terma inbox`
   - Keep important messages with mv-to-keep

## Troubleshooting

### Command Not Found
```bash
$ aish forwad list
Error: Unknown CI or command: forwad
Available CIs: numa, tekton, prometheus...

# Check spelling and try:
$ aish forward list
```

### No Response from AI
```bash
# Check if CI is running
$ ps aux | grep apollo-ai

# Check forwarding
$ aish forward list
```

### Message Not Delivered
```bash
# Verify terminal name
$ aish terma wrong-name "Test"
Error: Terminal 'wrong-name' not found
```

## See Also

- Individual CI documentation in `$TEKTON_ROOT/MetaData/TektonDocumentation/AITraining/<ai-name>/`
- Terminal system docs in `$TEKTON_ROOT/MetaData/TektonDocumentation/UserGuides/terma/`
- Architecture docs in `$TEKTON_ROOT/MetaData/TektonDocumentation/Architecture/`