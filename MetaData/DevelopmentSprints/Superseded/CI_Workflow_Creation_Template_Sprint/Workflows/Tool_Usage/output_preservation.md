# Workflow: Output Preservation

## When to Use
- Need to save important CI responses
- Debugging requires reviewing past outputs  
- Building documentation from CI conversations
- Collecting examples for training/testing

## Prerequisites
- [ ] Know your TEKTON_ROOT location
- [ ] Have write access to .tekton directory

## Steps

1. Enable capture for important commands → Save output automatically
   ```bash
   aish --capture numa "design a caching system"
   ```
   Output saved to: `$TEKTON_ROOT/.tekton/aish/captures/`

2. Find your captures → Locate saved outputs
   ```bash
   # List recent captures
   ls -la $TEKTON_ROOT/.tekton/aish/captures/
   # View last capture
   cat $TEKTON_ROOT/.tekton/aish/captures/last_output.txt
   ```

3. Organize captures by session → Group related outputs
   ```bash
   # Create session directory
   mkdir -p $TEKTON_ROOT/.tekton/aish/captures/$(date +%Y%m%d)_feature_x
   # Move relevant captures
   mv $TEKTON_ROOT/.tekton/aish/captures/202501*.txt \
      $TEKTON_ROOT/.tekton/aish/captures/$(date +%Y%m%d)_feature_x/
   ```

4. Extract key information → Process captures for documentation
   ```bash
   # Search captures for specific content
   grep -r "class.*:" $TEKTON_ROOT/.tekton/aish/captures/
   # Find code blocks
   awk '/```/,/```/' $TEKTON_ROOT/.tekton/aish/captures/last_output.txt
   ```

## Capture Patterns

### Always Capture Pattern
For critical work, capture everything:
```bash
# Start capture session
export AISH_CAPTURE=1
# All commands now captured automatically
aish numa "analyze this"
aish apollo "predict that"
# Stop capturing
unset AISH_CAPTURE
```

### Selective Capture Pattern  
For normal work, capture key moments:
```bash
# Regular interaction
aish numa "quick question"
# Important response - capture it
aish --capture numa "critical design decision"
```

### Pipeline Capture Pattern
Capture complex workflows:
```bash
# Capture entire pipeline
aish --capture team-chat "architectural review needed"
```

## Common Issues

- **Error**: No captures directory
  - **Fix**: Create it manually
  - **Command**: `mkdir -p $TEKTON_ROOT/.tekton/aish/captures`

- **Error**: Disk space issues with captures
  - **Fix**: Archive old captures
  - **Commands**:
    ```bash
    cd $TEKTON_ROOT/.tekton/aish/captures
    tar -czf captures_$(date +%Y%m).tar.gz 202501*.txt
    rm 202501*.txt
    ```

- **Error**: Can't find specific capture
  - **Fix**: Use grep to search all captures
  - **Command**: `grep -r "search term" $TEKTON_ROOT/.tekton/aish/captures/`

## Success Verification
- [ ] Capture file exists: `ls -la $TEKTON_ROOT/.tekton/aish/captures/last_output.txt`
- [ ] Content is complete: Check for timestamp, CI name, full response
- [ ] Symlink updated: `last_output.txt` points to most recent

## Integration Tips

### With Git
```bash
# Add important captures to version control
git add .tekton/aish/captures/architecture_decision_*.txt
git commit -m "Captured CI architecture discussions"
```

### With Documentation
```bash
# Convert capture to markdown
cat $TEKTON_ROOT/.tekton/aish/captures/last_output.txt | \
  sed 's/^/> /' > design_notes.md
```

### With Testing
```bash
# Save test scenarios
aish --capture numa "test case: user login flow"
mv $TEKTON_ROOT/.tekton/aish/captures/last_output.txt \
   tests/ai_test_cases/login_flow.txt
```

## Next Workflows
- If capture failed: [Permission/Path Issues workflow]
- If successful: [System Health Check workflow]

## Real Example
```bash
$ aish --capture numa "explain message forwarding"
[numa responds with detailed explanation]

$ ls -la $TEKTON_ROOT/.tekton/aish/captures/
-rw-r--r--  20250119_143022_numa.txt
-rw-r--r--  20250119_143156_apollo.txt  
lrwxr-xr-x  last_output.txt -> 20250119_143156_apollo.txt

$ head $TEKTON_ROOT/.tekton/aish/captures/last_output.txt
Timestamp: 2025-01-19T14:31:56
AI: apollo
Message: explain message forwarding
============================================================
Response:
Message forwarding in Tekton allows...
```

## Notes
- Captures include timestamp, CI name, message, and response
- The `last_output.txt` symlink always points to most recent
- Captures persist across sessions and environments
- Consider periodic cleanup of old captures
- Casey says: "Capture everything important - memory is cheap, lost insights are expensive"