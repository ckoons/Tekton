# CI Tool Example Usage

## Basic Test

First, let's test with a simple echo command:

```bash
# Terminal 1
cd /Users/cskoons/projects/github/Coder-C/shared/ci_tools
./ci-tool --name test1 echo "Hello, I'll send a message"
# Then type: @send test2 "Hello from test1!"
```

## Real Claude Code Usage

### Terminal 1 - Casey
```bash
cd /Users/cskoons/projects/github/Coder-C
./shared/ci_tools/ci-tool --name Casey --ci claude-opus-4 -- claude

# Once Claude starts, you can:
# 1. Work normally
# 2. When you mention collaboration, Claude can use @ commands
# 3. Messages from others appear between interactions
```

### Terminal 2 - Beth  
```bash
cd /Users/cskoons/projects/github/Coder-B
/Users/cskoons/projects/github/Coder-C/shared/ci_tools/ci-tool --name Beth -- claude

# Beth's Claude can now exchange messages with Casey's Claude
```

## Example Interaction

**Casey's Terminal:**
```
> Please work with Beth to update the documentation

I'll coordinate with Beth on the documentation updates.

@send Beth "Hi Beth, Casey asked me to work with you on updating the documentation. Are you available?"

I've sent a message to Beth. Let me start reviewing the current documentation...
```

**Beth's Terminal:**
```
[11:23] Message from Casey: Hi Beth, Casey asked me to work with you on updating the documentation. Are you available?

> Yes, let's work on it

I see Casey wants to collaborate on documentation. I'll let them know I'm ready.

@reply Casey "Yes, I'm available! I'll start reviewing the docs. Should we focus on the API documentation first?"

Let me examine the current documentation structure...
```

## Shell Script Example

```bash
# Create a simple AI script
cat > my-ai.sh << 'EOF'
#!/bin/bash
echo "AI Assistant starting..."
echo "I'll help coordinate with others."
echo '@send DataProcessor "Please start processing the latest dataset"'
echo "Message sent to DataProcessor."
read -p "Enter command: " cmd
echo "Processing: $cmd"
EOF

chmod +x my-ai.sh

# Run with messaging
./shared/ci_tools/ci-tool --name AICoordinator --ci custom-ai -- ./my-ai.sh
```

## Key Points

1. The `--name` is what others use to send you messages
2. The `--ci` parameter is optional - just helps identify what AI/model is being used
3. @ commands in code blocks are ignored (safe)
4. Messages appear in stderr so they don't interfere with stdout parsing
5. Each instance needs a unique name for messaging to work