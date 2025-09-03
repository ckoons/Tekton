# Greek Chorus Session Management - REAL SOLUTION

## The Problem
When you get: `Claude error (exit code 1): Prompt is too long`

## The ACTUAL Solution

### ✅ What Actually Works:

1. **Start a FRESH conversation** (don't use --continue):
   ```bash
   # Just send your message without --continue
   echo "Your message here"
   
   # Or use claude without --continue
   claude "Your message here"
   ```

2. **Use chorus-fresh for easy fresh starts**:
   ```bash
   ./scripts/chorus-fresh "Your message here"
   ```

### ❌ What DOESN'T Work:
- Using `--continue` after a reset (Claude still sees the full context)
- Soft resets with markers (Claude ignores them)
- Moving conversation files (Claude tracks sessions internally)

## Why This Happens

Claude Code maintains conversation context in JSONL files:
- Location: `~/.claude/projects/-Users-...-Coder-A/*.jsonl`
- These can grow to 1MB+ with long conversations
- Claude's `--continue` flag ALWAYS uses the full context
- There's NO way to "trim" the context and continue

## The Tools We Built

### 🆕 `chorus-fresh` - Start Fresh (RECOMMENDED)
```bash
# Start a new conversation, avoiding the error
./scripts/chorus-fresh "Continue working on the task"
```

### 📊 `tekton-chorus status` - Check Context Size
```bash
# See how large your context has grown
./scripts/tekton-chorus status
```
Shows:
- Current context size in KB
- Number of messages
- Whether you need a fresh start

### 🗄️ `tekton-chorus reset` - Archive Old Conversations
```bash
# Archives the large conversation file
./scripts/tekton-chorus reset soft
```
This moves old conversations to `archived/` subdirectory for cleanup.

## Best Practices

1. **Monitor context size** regularly:
   ```bash
   ./scripts/tekton-chorus status
   ```

2. **Start fresh when context > 500KB**:
   ```bash
   ./scripts/chorus-fresh "Your message"
   ```

3. **Don't use --continue with large contexts**
   - It will always fail with "Prompt too long"
   - Start fresh instead

4. **Clean up old conversations periodically**:
   ```bash
   # Archive old conversations
   ./scripts/tekton-chorus reset soft
   ```

## Quick Reference

| Situation | Command | Result |
|-----------|---------|--------|
| Context too large error | `chorus-fresh "message"` | Starts fresh conversation |
| Check context size | `tekton-chorus status` | Shows size & recommendations |
| Archive old convos | `tekton-chorus reset soft` | Moves to archived/ |
| Normal message | `echo "message"` | Sends to current session |

## The Bottom Line

**When you get "Prompt too long":**
1. DON'T use `--continue`
2. DO start fresh with `chorus-fresh` or just `echo`
3. Your conversation continues naturally even without --continue