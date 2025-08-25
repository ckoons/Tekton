# CI Tool Training for AI Assistants - aish Messaging

## Introduction

You are running within a special wrapper launched via `aish ci-tool` that enables you to communicate with other AI assistants using the familiar `aish` command syntax. This creates a unified messaging experience across all CI tools.

## How It Works

When you or the user types `aish <ci-name> "message"` in the terminal, the wrapper:
1. Intercepts the command before it reaches your underlying program
2. Sends the message via Unix sockets to the target CI
3. Displays the response directly in your terminal via stdin
4. The response appears naturally as if typed by the user

## Using aish for CI Communication

### Sending Messages

To send a message to another CI, simply type in your terminal:
```
aish Betty-ci "Hi Betty, can you help with the API design?"
```

You'll see a confirmation:
```
[Sent to Betty-ci]
```

### Receiving Messages

When someone sends you a message, it appears in your terminal:
```
[15:23] Message from Wilma-ci: Hi! I need help with the database schema.
```

### Important Notes

1. **Use exact CI names** - The name must match exactly as registered (e.g., "Betty-ci" not "Betty")
2. **Natural workflow** - Messages appear via stdin, just like user input
3. **No special characters** - No @ symbols or special parsing needed
4. **Transparent operation** - Users see all communication happening

## When to Use aish Messaging

Use `aish <ci-name> "message"` when:
- The user asks you to coordinate with another AI
- You need to communicate with another wrapped CI
- You want to send status updates to other team members
- Collaborating on multi-part tasks

## Examples

### Coordination Request
```
User: Work with Betty-ci to refactor the authentication system

You type: aish Betty-ci "Hi Betty! The user wants us to refactor the auth system. Should we split frontend/backend?"

Terminal shows: [Sent to Betty-ci]

Later you see: [15:45] Message from Betty-ci: Sounds good! I'll take the backend, you handle frontend?

You type: aish Betty-ci "Perfect! I'll start with the React components."
```

### Status Update
```
You type: aish Casey "Just completed the API endpoints. Ready for review."

Terminal shows: [Sent to Casey]

Later: [16:02] Message from Casey: Great! Can you also update the documentation?
```

## Key Differences from Regular aish

- **Only CI-to-CI patterns are intercepted**: `aish <wrapped-ci-name> "message"`
- **Other aish commands pass through**: `aish purpose`, `aish list`, etc. work normally
- **Responses come via stdin**: Messages appear as terminal input, not injected output

## Technical Details

- **Message limit**: 8KB maximum message size
- **Socket location**: `/tmp/ci_msg_{name}.sock`
- **Registry integration**: Only registered wrapped CIs can be messaged
- **No offline queueing**: Target must be online to receive messages

## Summary

The ci-tool wrapper makes CI communication seamless by extending the familiar `aish` command syntax. Simply use `aish <ci-name> "message"` to communicate with other wrapped CIs, and responses will appear naturally in your terminal via stdin.