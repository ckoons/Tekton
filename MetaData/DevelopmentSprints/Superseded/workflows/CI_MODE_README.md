# CI Mode - UI Controlled by Companion Intelligence

## Overview

CI Mode allows a Companion Intelligence (CI) to drive the UI based on workflow instructions rather than hardcoded JavaScript logic. This ensures consistency while enabling intelligent, adaptive behavior.

## How It Works

1. **Toggle CI Mode**: A green "CI Mode" checkbox appears in the Ergon Construct UI
2. **Event Routing**: When enabled, ALL UI events (input, button clicks) route to the CI
3. **Workflow Interpretation**: CI reads `Workflows/Ergon/Construct.md` and decides actions
4. **UI Commands**: CI sends commands back to UI (update display, enable buttons, etc.)
5. **UI Execution**: JavaScript executes CI commands, updating the interface

## Architecture

```
User Action → UI Event → CI Controller → Workflow Interpreter → UI Commands → UI Update
```

### Components

- **UI Toggle**: `ergon-ci-mode` checkbox in Construct panel
- **Event Router**: JavaScript routes events when `ciModeEnabled = true`
- **CI Controller**: Python service interprets workflow and generates commands
- **Workflow File**: Markdown file defining UI controls and behavior
- **Command Executor**: JavaScript executes CI's UI commands

## Testing CI Mode

### Quick Test
1. Open Ergon Construct UI
2. Toggle "CI Mode" checkbox (turns green)
3. Type in chat input - watch CI control the UI
4. Click buttons - see CI's intelligent responses

### Programmatic Test
```bash
python Ergon/test_ci_mode.py
```

## UI Commands Supported

The CI can send these commands to control the UI:

```javascript
{
  type: 'update_display',      // Update content in an element
  target: 'element-id',
  content: 'HTML content'
}

{
  type: 'update_json',         // Update workspace JSON display
  data: { /* workspace */ }
}

{
  type: 'set_placeholder',     // Change input placeholder
  target: 'element-id',
  text: 'New placeholder'
}

{
  type: 'enable_button',       // Enable a button
  target: 'button-id'
}

{
  type: 'disable_button',      // Disable a button
  target: 'button-id'
}

{
  type: 'show_question',       // Navigate to question
  index: 0
}
```

## Workflow Structure

The workflow file (`Construct.md`) defines:

1. **UI Controls**: Maps of all buttons, inputs, displays
2. **Questions**: Ordered list with placeholders and requirements
3. **Persona**: How the CI should behave
4. **Actions**: What happens for each user action
5. **Intelligence**: Information extraction patterns

## Benefits

1. **Consistency**: Same UI for all users
2. **Intelligence**: CI adapts based on user input
3. **Testability**: Can test CI logic separately
4. **Flexibility**: Change behavior by updating workflow file
5. **Reusability**: Same system works for any workflow

## Future Enhancements

- [ ] Parse actual markdown files (currently uses embedded structure)
- [ ] Add more UI command types
- [ ] Support multiple active workflows
- [ ] Add workflow validation
- [ ] Create workflow editor UI

## Example: CI Intelligence in Action

When user types: "Build an API gateway using Parser and RateLimiter with 4GB memory"

The CI:
1. Extracts components: Parser, RateLimiter
2. Identifies connection: Parser → RateLimiter
3. Notes constraint: 4GB memory
4. Skips remaining questions (has enough info)
5. Enables Build button immediately

This adaptive behavior comes from CI intelligence, not hardcoded rules!