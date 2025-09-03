# Greek Chorus Session Management

## ⚠️ IMPORTANT: The Real Solution

**When you get "Prompt is too long" error:**
1. **DON'T use `--continue`** - it always includes full context
2. **DO use `chorus-fresh` or plain `claude`** to start fresh
3. There is **NO way to trim context** and continue

## The Problem
Claude Code stores conversations in JSONL files (1MB+). The `--continue` flag ALWAYS uses the full context - you cannot trim it.

## Working Solutions

### 🆕 `chorus-fresh` - Start Fresh (RECOMMENDED)
```bash
# Start a NEW conversation, avoiding "prompt too long" error
./scripts/chorus-fresh "Your message here"

# This is equivalent to:
claude "Your message here"  # without --continue
```

### 📊 `tekton-chorus status` - Check Context Size
```bash
# See how large your context has grown
./scripts/tekton-chorus status
```
Shows context size in KB, message count, and recommendations.

### 🧹 `chorus-clean` - Clean Up Old Conversations  
```bash
# Remove archived conversations, free disk space
./scripts/chorus-clean
```

### 🗄️ `tekton-chorus reset` - Archive Sessions
```bash
# Archives large conversation files
./scripts/tekton-chorus reset soft
```
**Note:** This does NOT allow `--continue` to work - it just archives files.

## Correct Workflow  

### When you get "prompt too long" error:

**Option 1: Use chorus-fresh (Recommended)**
```bash
./scripts/chorus-fresh "Continue with the task..."
```

**Option 2: Use claude directly (without --continue)**
```bash
claude "Continue with the task..."
```

**Option 3: Just send your message normally**
```bash
echo "Continue with the task..."
```

### What NOT to do:
```bash
# ❌ WRONG - This will still fail with "prompt too long"
./scripts/tekton-chorus reset soft
claude --continue "Message"  # Still includes full context!
```

## How It Really Works

1. **chorus-fresh** - Starts a NEW Claude session without --continue
2. **Context files** - Stored in `~/.claude/projects/{project-path}/` as JSONL
3. **--continue flag** - ALWAYS includes full context, cannot be trimmed
4. **Reset/archive** - Only moves files, doesn't affect Claude's context loading

## Best Practices

1. **Monitor context size:**
   ```bash
   ./scripts/tekton-chorus status
   ```

2. **When context > 500KB, start fresh:**
   ```bash
   ./scripts/chorus-fresh "Your message"
   ```

3. **Clean up old conversations:**
   ```bash
   ./scripts/chorus-clean
   ```

## Files

- `scripts/chorus-fresh` - Start fresh Claude session
- `scripts/tekton-chorus` - Check status and manage sessions
- `scripts/chorus-clean` - Clean up old conversation files
- `scripts/chorus-reset` - Archive conversations (doesn't help with --continue)
- `shared/ai/session_manager.py` - Python session management module