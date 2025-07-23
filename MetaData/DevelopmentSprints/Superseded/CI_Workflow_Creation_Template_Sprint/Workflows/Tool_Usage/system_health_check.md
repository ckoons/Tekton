# Workflow: System Health Check

## When to Use
- Before starting any development session
- When things feel "off" or slow
- After system updates or restarts
- Before important demonstrations
- As part of regular maintenance

## Prerequisites
- [ ] `tekton` command available
- [ ] `jq` installed for JSON parsing (optional but helpful)

## Steps

1. Quick overall health check → Get system status
   ```bash
   tekton status --json | jq -r '.system'
   ```
   Expected output:
   ```json
   {
     "status": "healthy",
     "uptime": "2h 34m",
     "load": [0.5, 0.8, 0.7]
   }
   ```

2. Check core components → Verify critical services
   ```bash
   # Check all at once
   tekton status
   # Or check specific component
   tekton status rhetor
   tekton status terma
   ```
   Look for "running" or "active" states

3. Verify AI components → Ensure AI services are responsive
   ```bash
   aish status
   ```
   Look for:
   - ✓ marks indicating running AIs
   - Correct port assignments
   - No port conflicts

4. Check message flow → Test end-to-end communication
   ```bash
   # Quick ping test
   aish numa "ping" && echo "✓ Numa responsive"
   aish apollo "ping" && echo "✓ Apollo responsive"
   ```

5. Decision tree:
   - All ✓ marks: System healthy, proceed with work
   - Some ✗ marks: Check specific components (step 6)
   - Many ✗ marks: Full restart might be needed (step 7)

6. Component-specific checks → Dig into problems
   ```bash
   # For stopped component
   tekton status [component] --verbose
   # Check logs
   tekton logs [component] --tail 20
   # Try restart
   tekton restart [component]
   ```

7. Full system restart → When multiple issues exist
   ```bash
   # Graceful restart
   tekton stop
   tekton start
   # Verify after restart
   tekton status
   ```

## Health Check Patterns

### Morning Startup Pattern
```bash
# One-liner health check
tekton status --json | jq -r '.components[] | select(.status != "running") | .name' || echo "All systems go!"
```

### Pre-Demo Pattern
```bash
# Thorough check before important session
tekton status
aish status  
aish numa "health check"
echo "Demo ready: $(date)"
```

### Diagnostic Pattern
```bash
# When something's wrong
tekton status --json > /tmp/tekton_health_$(date +%s).json
aish status --json > /tmp/aish_health_$(date +%s).json
# Compare with previous healthy state
```

## Common Issues

- **Issue**: Component shows "stopped" but should be running
  - **Fix**: Restart the specific component
  - **Command**: `tekton restart [component]`
  
- **Issue**: Port conflict (component can't start)
  - **Fix**: Find and kill process using port
  - **Commands**:
    ```bash
    # Find what's using the port
    lsof -i :8003  # For rhetor port example
    # Kill if necessary
    kill -9 [PID]
    ```

- **Issue**: "Connection refused" errors
  - **Fix**: Component crashed, needs full restart
  - **Commands**:
    ```bash
    tekton stop [component]
    sleep 2
    tekton start [component]
    ```

- **Issue**: System feels sluggish
  - **Fix**: Check system load and resources
  - **Commands**:
    ```bash
    top -l 1 | head -n 10
    df -h
    tekton status --json | jq '.system.load'
    ```

## Success Verification
- [ ] All components show "running": `tekton status | grep -c running`
- [ ] No port conflicts: `tekton status --json | jq '.issues'`
- [ ] AI responding quickly: Time an AI ping < 2 seconds
- [ ] System load reasonable: Load average < number of CPUs

## Quick Reference Card
```bash
# The 10-second health check
alias health='tekton status --json | jq -r "if .healthy then \"✓ Healthy\" else \"✗ Issues: \" + (.issues | join(\", \")) end"'

# The thorough check  
alias health-full='tekton status && echo "---" && aish status && echo "---" && aish numa "health check"'

# The diagnostic dump
alias health-dump='tekton status --json > health_$(date +%s).json && aish status --json >> health_$(date +%s).json'
```

## Next Workflows
- If unhealthy: [Component Not Responding workflow]
- If healthy but slow: [Performance Tuning workflow]
- If all good: [Multi-Environment Testing workflow]

## Real Example
```bash
$ tekton status --json | jq -r '.system'
{
  "status": "healthy",
  "uptime": "4h 17m",
  "load": [1.2, 1.5, 1.3],
  "memory": {
    "used": "8.2GB",
    "free": "7.8GB"
  }
}

$ tekton status
System Status: Healthy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Component     Status    Port   Uptime
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
rhetor        running   8003   4h 17m
terma         running   8300   4h 17m  
numa          running   8316   4h 15m
apollo        running   8312   4h 15m
...

$ aish numa "ping"
Numa is operational and ready to assist.
```

## Notes
- Health checks should be fast - if slow, that's a symptom
- The `--json` flag enables automation and scripting
- Regular health checks prevent mysterious issues
- Casey's wisdom: "Trust but verify - especially before important work"
- A healthy system responds in milliseconds, not seconds