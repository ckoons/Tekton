# Workflow: Multi-Environment Testing

## When to Use
- Testing changes across Coder-A, B, C environments
- Verifying environment-specific configurations
- Debugging environment-related issues
- Ensuring consistent behavior across setups

## Prerequisites
- [ ] Multiple Coder environments set up
- [ ] Understanding of `-c` flag for environment switching
- [ ] Knowledge of what differs between environments

## Steps

1. Check current environment → Know where you are
   ```bash
   echo $TEKTON_ROOT
   # Should show: /Users/cskoons/projects/github/Coder-[A|B|C]
   pwd
   # Verify you're in the right directory
   ```

2. Quick tour of all environments → Get status across systems
   ```bash
   # Check Coder-A
   tekton -c A status --json | jq -r '.environment.name'
   
   # Check Coder-B  
   tekton -c B status --json | jq -r '.environment.name'
   
   # Check Coder-C
   tekton -c C status --json | jq -r '.environment.name'
   ```

3. Test specific functionality → Verify consistent behavior
   ```bash
   # Test in current environment
   aish numa "test message"
   
   # Test in Coder-B (from anywhere)
   cd ~/projects/github/Coder-B
   source shared/.activate
   aish numa "test message"
   
   # Return to original
   cd ~/projects/github/Coder-C
   source shared/.activate
   ```

4. Compare configurations → Identify differences
   ```bash
   # Compare ports
   tekton -c A status --json | jq '.components[].port' > /tmp/ports_a.txt
   tekton -c B status --json | jq '.components[].port' > /tmp/ports_b.txt
   diff /tmp/ports_a.txt /tmp/ports_b.txt
   ```

5. Cross-environment testing → Verify isolation
   ```bash
   # Terminal 1: Coder-A
   cd ~/projects/github/Coder-A && source shared/.activate
   aish forward numa Terminal-A
   
   # Terminal 2: Coder-B  
   cd ~/projects/github/Coder-B && source shared/.activate
   aish forward numa Terminal-B
   
   # Each environment maintains separate forwarding
   ```

## Environment Patterns

### Quick Switch Pattern
```bash
# Create aliases for fast switching
alias coder-a='cd ~/projects/github/Coder-A && source shared/.activate && echo "→ Coder-A"'
alias coder-b='cd ~/projects/github/Coder-B && source shared/.activate && echo "→ Coder-B"'
alias coder-c='cd ~/projects/github/Coder-C && source shared/.activate && echo "→ Coder-C"'
```

### Parallel Testing Pattern
```bash
# Test same feature across environments
for env in A B C; do
  echo "Testing in Coder-$env:"
  tekton -c $env status --json | jq -r '.healthy'
done
```

### Environment Verification Pattern
```bash
# Ensure you're in the right environment
function verify_env() {
  local expected=$1
  local actual=$(echo $TEKTON_ROOT | grep -o 'Coder-[ABC]' | cut -d'-' -f2)
  if [ "$actual" != "$expected" ]; then
    echo "WARNING: Expected Coder-$expected but in Coder-$actual"
    return 1
  fi
  echo "✓ Confirmed in Coder-$expected"
}
```

## Common Issues

- **Issue**: Changes not visible in environment
  - **Fix**: Ensure you've sourced .activate
  - **Command**: `source shared/.activate`
  
- **Issue**: Wrong environment loaded
  - **Fix**: Check TEKTON_ROOT and re-source
  - **Commands**:
    ```bash
    echo $TEKTON_ROOT
    # If wrong, cd to correct dir
    cd ~/projects/github/Coder-[A|B|C]
    source shared/.activate
    ```

- **Issue**: Port conflicts between environments  
  - **Fix**: Each environment uses different port ranges
  - **Check**: `tekton -c [A|B|C] status --json | jq '.components[].port'`

- **Issue**: Shared state confusion
  - **Fix**: Remember each environment is isolated
  - **Note**: Forwarding, captures, history are per-environment

## Success Verification
- [ ] Can switch environments: `coder-a && echo $TEKTON_ROOT`
- [ ] Each shows correct root: Contains "Coder-A/B/C" as expected  
- [ ] Components isolated: Different ports per environment
- [ ] No cross-talk: Messages stay in their environment

## Advanced Multi-Env Patterns

### Development + Testing Pattern
```bash
# Develop in Coder-A
coder-a
# Make changes...

# Test in Coder-B (clean environment)
coder-b
# Run tests...

# Deploy to Coder-C (production-like)
coder-c
# Final verification...
```

### Comparison Pattern
```bash
# Run same command across all environments
function test_all() {
  local cmd="$*"
  for env in A B C; do
    echo "=== Coder-$env ==="
    (cd ~/projects/github/Coder-$env && \
     source shared/.activate && \
     eval "$cmd")
    echo
  done
}

# Usage
test_all aish status
test_all tekton status rhetor
```

### Environment Sync Pattern
```bash
# Copy configuration from A to B
cp ~/projects/github/Coder-A/.tekton/config/* \
   ~/projects/github/Coder-B/.tekton/config/

# But remember: each environment may need different ports
```

## Next Workflows
- If environment switching fails: [Environment Setup workflow]
- If ready to develop: [Feature Development workflow]
- If testing: [Integration Testing workflow]

## Real Example
```bash
$ echo $TEKTON_ROOT
/Users/cskoons/projects/github/Coder-C

$ tekton -c A status --json | jq -r '.environment.name'
"Coder-A"

$ tekton -c B status --json | jq -r '.environment.name'  
"Coder-B"

$ coder-a
→ Coder-A
$ echo $TEKTON_ROOT
/Users/cskoons/projects/github/Coder-A

$ aish forward list
numa → Terminal-A-1
apollo → Terminal-A-2

$ coder-b  
→ Coder-B
$ aish forward list
numa → Terminal-B-1
synthesis → Terminal-B-Test
```

## Notes
- Each environment is completely isolated
- Port ranges: A (8000s), B (9000s), C (7000s) typically
- Environment state persists in `.tekton/` directories
- Always verify environment before important operations
- Casey's pattern: "Develop in A, test in B, demo in C"
- The `-c` flag is powerful but affects only that command