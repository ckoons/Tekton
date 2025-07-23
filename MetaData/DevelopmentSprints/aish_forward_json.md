# Dev Sprint: `aish forward --json` Structured Message Enhancement

## Goal
Add `--json` flag to forward command to convert text messages into structured JSON for CI processing.

## Current Behavior
- `aish forward apollo bari` - forwards apollo's responses to terminal bari as plain text
- Messages are forwarded as-is without any metadata or structure

## New Behavior with --json
- `aish forward apollo bari --json` - forwards apollo's responses to bari as JSON
- When a message is sent to apollo, it gets converted to:
  ```json
  {
    "message": "original text message",
    "dest": "apollo",
    "sender": "current_terminal",
    "purpose": "forward"
  }
  ```
- Bari receives this JSON and can process it to adopt apollo's persona
- Allows one CI to handle multiple personas based on the JSON metadata

## Use Case
Enables CIs to act as intelligent routers/processors, adopting different personas based on structured input rather than just forwarding plain text.

## Implementation Details
1. Add `--json` flag parsing to forward command
2. Store the flag state with the forward configuration
3. In the message sending flow, check if the forward has --json enabled
4. If enabled, wrap the message in JSON structure before sending to destination
5. Include metadata: original destination, sender, purpose

## Test Cases
1. `aish forward apollo bari --json` - set up JSON forwarding
2. `aish numa "hello"` - numa's response should arrive at bari as JSON
3. `aish forward list` - should show which forwards have --json enabled
4. `aish forward apollo bari` - without --json should still work as plain text

## Success Criteria
- JSON structure includes all necessary metadata for persona adoption
- Backward compatibility - existing forwards continue working as plain text
- Clear indication in `forward list` which forwards use JSON mode