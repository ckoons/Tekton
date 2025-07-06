# Claude Proxy Pattern

## Overview

Use Claude terminal sessions as intelligent proxies for Tekton components, eliminating API charges while leveraging Claude's capabilities.

## The Rube Goldberg Beauty

```
Component Request → aish inbox → Claude Proxy → Component Response
                                       ↓
                                 (Running in terminal)
                                 (No API charges!)
```

## Implementation

### 1. Proxy Command

```bash
# Start Claude as multi-component proxy
aish proxy apollo,tekton-core,rhetor

# Or proxy all high-value components
aish proxy @architects  # apollo, prometheus, athena
aish proxy @planning    # prometheus, telos, metis
```

### 2. Auto-Loop Script

```python
# aish-proxy-loop command
#!/usr/bin/env python3
"""
Continuous inbox monitoring for Claude proxy mode
"""

import time
import subprocess
import sys

def main():
    components = sys.argv[1].split(',')
    poll_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print(f"Claude Proxy Active for: {', '.join(components)}")
    print(f"Polling every {poll_interval} seconds")
    print("Instructions: Respond to messages as the appropriate component")
    print("-" * 60)
    
    while True:
        try:
            # Check all component inboxes
            for component in components:
                # Check for new messages
                result = subprocess.run(
                    ['aish', 'terma', 'inbox', 'new', 'pop'],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout and not result.stdout.startswith("No new messages"):
                    print(f"\n[{component}] New message:")
                    print(result.stdout)
                    print(f"\nResponse as {component}: ", end='', flush=True)
                    
                    # Wait for Claude to type response
                    # This is the tricky part - need to capture Claude's response
                    # and route it back
            
            # Brief pause
            time.sleep(poll_interval)
            
        except KeyboardInterrupt:
            print("\nProxy mode ended")
            break
```

### 3. Better Approach: Inbox Watcher

```python
# Enhanced version that shows all pending messages
def claude_proxy_mode(components):
    """
    Show all messages needing responses
    Claude can process them in any order
    """
    
    print("=== Claude Proxy Mode ===")
    print(f"Monitoring: {', '.join(components)}")
    print("\nInstructions:")
    print("1. Read the component messages below")
    print("2. Respond with: @component: your response")
    print("3. Type 'next' to refresh inbox")
    print("4. Type 'exit' to stop proxy mode")
    print("=" * 40)
    
    while True:
        # Show all pending messages
        messages = []
        for component in components:
            component_messages = get_component_messages(component)
            for msg in component_messages:
                messages.append({
                    'component': component,
                    'from': msg['from'],
                    'content': msg['content'],
                    'timestamp': msg['timestamp']
                })
        
        if messages:
            print(f"\n{len(messages)} messages waiting:")
            for i, msg in enumerate(messages, 1):
                print(f"\n[{i}] To {msg['component']} from {msg['from']}:")
                print(f"    {msg['content']}")
            
            print("\nYour response (format: @component: response):")
            # Claude types response here
            
        else:
            print("\nNo messages waiting. Type 'next' to check again.")
        
        # Wait for input
        user_input = input("> ")
        
        if user_input == 'exit':
            break
        elif user_input == 'next':
            continue
        elif user_input.startswith('@'):
            # Parse and send response
            process_claude_response(user_input)
```

### 4. Even Simpler: Batch Mode

```bash
# Show all messages at once
aish proxy-batch apollo,tekton-core,rhetor

Output:
========================================
PROXY BATCH: 3 messages waiting

[1] TO apollo FROM synthesis:
"Need code review for auth module"

[2] TO tekton-core FROM numa:  
"Project status request"

[3] TO rhetor FROM athena:
"Help optimizing prompt for documentation"

INSTRUCTIONS: 
- Respond to each with: [1] Your response here
- Or skip with: [1] skip
- Type 'done' when finished
========================================

[1] > I'll review the auth module. Key areas to check:
1. Token validation
2. Session management  
3. Error handling
Send me the PR link.

[2] > Project status: 3 active PRs, 2 in review, 
1 ready to merge. All tests passing.

[3] > For documentation prompts, try:
"Explain X for a developer familiar with Y"
This provides context and level.

done
========================================
Responses sent! Next batch in 30 seconds...
```

### 5. The Laziest Approach

```python
# Just combine all inboxes into one stream
def unified_proxy_stream():
    """
    All component messages in one feed
    Claude responds naturally
    """
    
    while True:
        print("\n=== Unified Component Stream ===")
        
        # Get ALL messages for ALL components
        all_messages = get_all_component_messages()
        
        if all_messages:
            for msg in all_messages:
                print(f"\n[{msg['to_component']}] {msg['from']}: {msg['content']}")
            
            print("\n> ", end='', flush=True)
            # Claude responds to whichever seems most important
            
        time.sleep(10)  # Check every 10 seconds
```

## Making It Work with Claude

### Option 1: Semi-Automated
```bash
# Terminal 1: Run the monitor
aish proxy-monitor apollo,tekton-core,rhetor

# It shows messages and waits for responses
# You (Claude) type responses
# It sends them and loops
```

### Option 2: Inbox File
```bash
# Write messages to a file Claude can read
aish proxy-to-file apollo,tekton-core,rhetor > inbox.txt

# Claude reads file, writes responses
# Another script reads responses and sends them
```

### Option 3: The Best Compromise
```python
# Interactive batch processor
def interactive_proxy():
    while True:
        messages = collect_all_messages()
        
        if not messages:
            print("No messages. Waiting 30 seconds...")
            time.sleep(30)
            continue
            
        print(f"\n{'='*50}")
        print(f"{len(messages)} MESSAGES NEED RESPONSES:")
        print(f"{'='*50}\n")
        
        for i, msg in enumerate(messages):
            print(f"[{i+1}] {msg['to']} ← {msg['from']}")
            print(f"    {msg['content'][:100]}...")
        
        print("\nPress Enter to start responding...")
        input()
        
        for i, msg in enumerate(messages):
            print(f"\n[{i+1}/{len(messages)}] TO: {msg['to']} FROM: {msg['from']}")
            print(f"MESSAGE: {msg['content']}")
            print(f"\nRESPONSE: ", end='', flush=True)
            
            response = input()  # Claude types here
            
            if response and response != 'skip':
                send_response(msg['to'], response)
                print("✓ Sent")
            else:
                print("→ Skipped")
        
        print(f"\nBatch complete! Processed {len(messages)} messages.")
        print("Next check in 30 seconds...")
        time.sleep(30)
```

## The Simplest Working Solution

```bash
#!/bin/bash
# claude-proxy.sh

while true; do
    clear
    echo "=== Claude Proxy Check ==="
    date
    echo ""
    
    # Check each component
    for component in apollo tekton-core rhetor; do
        echo "[$component]"
        aish terma inbox new pop 2>/dev/null | grep -v "No new messages" || echo "  No messages"
        echo ""
    done
    
    echo "---"
    echo "Respond with: aish <component> 'response'"
    echo "Sleeping 30 seconds..."
    sleep 30
done
```

## Benefits

1. **No API Charges** - Uses your Claude Code session
2. **Full Claude Intelligence** - Not limited to local LLMs
3. **Flexible** - Can handle complex reasoning
4. **Simple** - Just reading and responding to messages
5. **Scalable** - One Claude can proxy many components

## Challenges

1. **Manual Process** - Requires Claude (you) to be active
2. **Response Parsing** - Need to capture Claude's responses
3. **Context Switching** - Claude needs to think as different components
4. **Availability** - Only works when Claude session is active

## Recommendation

Start with the "Interactive Batch Processor" approach:
1. Collects all messages
2. Shows them clearly
3. Claude responds to each
4. Automatically sends responses
5. Loops every 30 seconds

This balances automation with Claude's need to understand context and provide thoughtful responses.

---
*"Sometimes the most elegant solution is wonderfully ridiculous"*