# Workflow: Message Routing Debug

## When to Use
- Messages aren't appearing where expected
- Testing if forwarding is working
- Verifying AI communication paths
- Debugging "no response" issues

## Prerequisites
- [ ] `aish` command available
- [ ] In a terma terminal (check with `aish whoami`)

## Steps

1. Check current forwarding setup → See what's forwarded where
   ```bash
   aish forward list
   ```
   Expected output shows active forwards like:
   ```
   numa → Terminal-1
   tekton → CI_Terminal
   ```

2. Test with self-forward → Verify forwarding mechanism works
   ```bash
   # Get your terminal name
   aish whoami
   # Forward an AI to yourself  
   aish forward apollo $(aish whoami)
   # Send test message
   aish apollo "test message"
   # You should see the message in your terminal
   ```

3. Check system status → Verify components are running
   ```bash
   aish status
   ```
   Look for:
   - ✓ marks for running AIs
   - Forward arrows showing routing
   - Active terminals list

4. Decision point:
   - If message appeared: Forwarding works, issue is elsewhere
   - If no message: Continue to step 5
   
5. Debug specific AI → Test direct communication
   ```bash
   # Unforward first
   aish unforward apollo
   # Send direct message with capture
   aish --capture apollo "ping"
   # Check captured output
   cat ~/.tekton/aish/captures/last_output.txt
   ```

## Common Issues

- **Error**: No response from AI
  - **Fix**: Check if AI is running
  - **Command**: `aish status | grep apollo`
  
- **Error**: "Failed to send message to X"
  - **Fix**: AI might be down, check Rhetor
  - **Command**: `tekton status rhetor`

- **Error**: Messages going to wrong terminal
  - **Fix**: Clear and reset forwarding
  - **Commands**: 
    ```bash
    aish unforward [ai-name]
    aish forward [ai-name] [correct-terminal]
    ```

## Success Verification
- [ ] Test message appears in terminal: `aish apollo "verify"`
- [ ] Status shows correct routing: `aish status`
- [ ] No errors in output

## Advanced Pattern: The Tee Trick
Casey's pattern for enhanced message flow:
```bash
# Temporarily route through Tekton for analysis
aish unforward numa
aish numa "complex problem needing insight"
aish forward numa $(aish whoami)
```
This sends the message through Tekton AI for enhancement before returning.

## Next Workflows
- If still broken: [Component Not Responding workflow]
- If fixed: [Output Preservation workflow]

## Real Example
```bash
$ aish whoami
Casey_Gemini_Terminal

$ aish forward list
numa → Beth_Terminal
apollo → Casey_Terminal

$ aish forward numa Casey_Gemini_Terminal
Forwarding numa messages to Casey_Gemini_Terminal

$ aish numa "test"
[Terminal displays the numa response]

$ aish status
Active AI Forwards:
  ✓ numa         → Casey_Gemini_Terminal
  ✓ apollo       → Casey_Terminal
```

## Notes
- Forwarding persists across sessions (stored in registry)
- Multiple terminals can receive same AI (broadcast pattern)
- The "tee" pattern is powerful for CI enhancement
- Always verify with `aish whoami` first