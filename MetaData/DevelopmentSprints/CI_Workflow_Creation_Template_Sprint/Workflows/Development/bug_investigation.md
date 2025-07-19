# Workflow: Bug Investigation

## When to Use
- Unexpected behavior in code
- Error messages that need investigation
- Performance problems
- Integration failures
- "It worked yesterday" situations

## Prerequisites
- [ ] Reproducible test case (or at least a description)
- [ ] Access to relevant logs and systems
- [ ] Clean workspace to isolate issue

## Steps

1. Reproduce the issue → Confirm the problem exists
   ```bash
   # Document the exact steps
   echo "Bug reproduction steps:" > bug_investigation.md
   echo "1. Run command: aish numa 'test'" >> bug_investigation.md
   echo "2. Expected: Response appears" >> bug_investigation.md  
   echo "3. Actual: No response" >> bug_investigation.md
   
   # Try to reproduce
   aish numa "test"
   ```

2. Isolate the failure point → Narrow down where it breaks
   ```bash
   # Check component health first
   aish status
   tekton status numa
   
   # Test direct communication
   curl -X POST http://localhost:$(tekton status numa --json | jq -r .port)/
   
   # Check with verbose/debug mode
   AISH_DEBUG=1 aish numa "test"
   ```

3. Gather context → Collect all relevant information
   ```bash
   # Capture system state
   tekton status --json > bug_context.json
   aish status --json >> bug_context.json
   
   # Get recent logs
   tekton logs numa --tail 50 > numa_logs.txt
   
   # Check for recent changes
   git log --oneline -10
   git diff HEAD~1
   ```

4. Use AI to analyze → Let Claude help investigate
   ```bash
   # In your terminal with Claude access
   # Paste the error and context
   
   # Or use Apollo for pattern recognition
   aish --capture apollo "analyze this error pattern: [paste error]"
   
   # Get debugging suggestions
   aish numa "debug steps for: connection refused on port 8316"
   ```

5. Test hypotheses → Systematically verify theories
   ```bash
   # Hypothesis 1: Port conflict
   lsof -i :8316
   
   # Hypothesis 2: Process crashed
   ps aux | grep numa
   
   # Hypothesis 3: Configuration issue
   cat $TEKTON_ROOT/.tekton/config/numa.yaml
   ```

6. Implement fix → Apply and test solution
   ```bash
   # Apply fix
   [make changes]
   
   # Test immediately
   [run test command]
   
   # Verify fix works consistently
   for i in {1..5}; do
     echo "Test $i:"
     [run test command]
     sleep 1
   done
   ```

## Investigation Patterns

### Binary Search Pattern
```bash
# When it "worked before", find when it broke
git bisect start
git bisect bad HEAD
git bisect good [last-known-good-commit]
# Test each commit git gives you
```

### Differential Diagnosis Pattern
```bash
# Compare working vs broken environment
# In working environment
tekton -c A status --json > working.json
# In broken environment  
tekton -c B status --json > broken.json
# Compare
diff working.json broken.json
```

### Trace Execution Pattern
```bash
# Add debug output to trace execution
export AISH_DEBUG=1
export TEKTON_DEBUG=1
# Run with system call tracing
strace -o trace.log aish numa "test"
# Or Python tracing
python -m trace -t aish numa "test"
```

### AI-Assisted Pattern (The Whisper)
```bash
# When stuck, whisper to yourself through Claude
# Compact context first if needed
/compact

# Then explain the problem to Claude in terminal
# "I'm seeing X when I do Y, but expecting Z..."
# Claude can see your terminal context and suggest next steps
```

## Common Bug Patterns

- **Pattern**: "Connection refused"
  - **Usual cause**: Service not running
  - **Quick check**: `tekton status [component]`
  - **Fix**: `tekton restart [component]`

- **Pattern**: "No such file or directory"  
  - **Usual cause**: Wrong environment or path
  - **Quick check**: `echo $TEKTON_ROOT; pwd`
  - **Fix**: `cd $TEKTON_ROOT; source shared/.activate`

- **Pattern**: "Import error" / "Module not found"
  - **Usual cause**: Python path issues
  - **Quick check**: `python -c "import sys; print(sys.path)"`
  - **Fix**: `export PYTHONPATH=$PYTHONPATH:$TEKTON_ROOT`

- **Pattern**: Silent failures (exit 0 but nothing happens)
  - **Usual cause**: Swallowed exceptions
  - **Quick check**: Add debug prints or use debugger
  - **Fix**: Find the try/except catching everything

## Advanced Debugging

### Time Travel Debugging
```bash
# Capture state before bug
aish --capture status > before.txt
# Reproduce bug
[trigger bug]
# Capture state after
aish --capture status > after.txt
# Compare
diff before.txt after.txt
```

### Component Isolation
```bash
# Test component in isolation
cd $TEKTON_ROOT/components/numa
python -m numa.main --test-mode
```

### Network Debugging
```bash
# Monitor network traffic
tcpdump -i lo0 -n port 8316
# In another terminal, trigger bug
aish numa "test"
```

## Success Verification
- [ ] Bug reproduces consistently before fix
- [ ] Bug does not reproduce after fix
- [ ] No new issues introduced
- [ ] Root cause understood and documented
- [ ] Test added to prevent regression

## Documentation Template
```markdown
## Bug: [Brief Description]
Date: [YYYY-MM-DD]
Reporter: [Who found it]
Severity: [Low/Medium/High/Critical]

### Symptoms
- What happens
- Error messages
- When it occurs

### Root Cause
[Technical explanation]

### Fix
[What was changed and why]

### Prevention
[How to prevent similar issues]
```

## Next Workflows
- If fix works: [Testing and Validation workflow]
- If stuck: [Escalation and Help workflow]
- If systemic issue: [Architecture Review workflow]

## Real Example
```bash
$ aish numa "analyze code"
aish: Failed to send message to numa

$ aish status
AI Components:
  ✗ numa         (port 8316)
  ✓ apollo       (port 8312)

$ tekton status numa
numa: stopped

$ tekton logs numa --tail 5
[ERROR] Port 8316 already in use
[ERROR] Failed to start server

$ lsof -i :8316
COMMAND   PID    USER   FD   TYPE
python3   4823   casey  4u   IPv4

$ kill 4823

$ tekton start numa
Starting numa... OK

$ aish numa "analyze code"
I'll help you analyze the code. Please share...
```

## Notes
- Document as you debug - future you will thank you
- Binary search is powerful for "it worked before" bugs
- Check the obvious first (is it running? right environment?)
- Use AI assistants throughout investigation
- Casey's wisdom: "The bug is usually in the last place you changed"
- The whisper pattern with Claude is especially powerful for complex bugs