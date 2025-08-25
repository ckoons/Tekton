# Workflow: Feature Development

## When to Use
- Starting new feature implementation
- Adding functionality to existing code
- Creating new commands or tools
- Implementing sprint tasks

## Prerequisites
- [ ] Clean git status (commit or stash changes)
- [ ] System health verified
- [ ] Know which environment you're in
- [ ] Have sprint/task documentation ready

## Steps

1. Pre-flight check → Ensure clean start
   ```bash
   # Check system health
   tekton status --json | jq -r '.healthy' || tekton status
   
   # Verify git state  
   git status
   
   # Confirm environment
   echo "Working in: $(basename $TEKTON_ROOT)"
   ```

2. Set up CI assistance → Configure forwarding for development
   ```bash
   # Get your terminal name
   TERMINAL=$(aish whoami)
   
   # Forward relevant CIs for development
   aish forward numa $TERMINAL      # General assistance
   aish forward metis $TERMINAL     # Code analysis
   aish forward synthesis $TERMINAL # Integration help
   ```

3. Understand the codebase → Use CI to explore
   ```bash
   # Find relevant files
   find . -name "*.py" -path "*/commands/*" -type f | head -20
   
   # Understand code structure
   aish metis "analyze the command structure in $(pwd)"
   
   # Get integration points
   aish synthesis "how do new commands integrate with the shell?"
   ```

4. Implement incrementally → Build in small steps
   ```bash
   # Create feature branch
   git checkout -b feature/new-command
   
   # Start with minimal implementation
   touch new_feature.py
   
   # Get CI help with structure
   aish --capture numa "create skeleton for aish command that does X"
   
   # Implement core logic
   # Test frequently
   python new_feature.py
   ```

5. Test as you go → Verify each piece works
   ```bash
   # Unit test
   python -m pytest tests/test_new_feature.py -v
   
   # Integration test  
   aish introspect NewFeatureClass
   
   # End-to-end test
   aish new-command "test input"
   ```

6. Capture important decisions → Document as you work
   ```bash
   # Capture design decisions
   aish --capture numa "explain why we chose approach X over Y"
   
   # Save to documentation
   cat $TEKTON_ROOT/.tekton/aish/captures/last_output.txt >> \
       docs/design_decisions.md
   ```

## Development Patterns

### Exploration First Pattern
```bash
# Before coding, understand the landscape
aish context existing_module.py
aish introspect ExistingClass
aish numa "show me how similar features are implemented"
```

### Test-Driven Pattern
```bash
# Write test first
aish --capture numa "write test for feature that does X"
# Save test
cat $TEKTON_ROOT/.tekton/aish/captures/last_output.txt > test_x.py
# Implement to pass test
aish numa "implement code to pass this test: $(cat test_x.py)"
```

### Incremental Integration Pattern
```bash
# Start standalone
python new_feature.py

# Integrate partially  
from new_feature import core_function
core_function("test")

# Full integration
aish reload  # If such command exists
aish new-feature "test"
```

### CI Pair Programming Pattern
```bash
# The "whisper" pattern Casey mentioned
# Have specialist CI enhance your work
aish numa "implement basic cache"
# Get optimization insights (the 'tee' concept) 
aish apollo "optimize this cache implementation: [paste code]"
# Merge insights back
aish synthesis "integrate these optimization suggestions"
```

## Common Issues

- **Issue**: Can't find where to add new code
  - **Fix**: Use CI to explore codebase
  - **Commands**:
    ```bash
    aish numa "where do aish commands live?"
    find . -name "*.py" -path "*command*"
    grep -r "def handle_.*_command" .
    ```

- **Issue**: Import errors when testing
  - **Fix**: Check Python path and imports
  - **Commands**:
    ```bash
    echo $PYTHONPATH
    python -c "import sys; print('\n'.join(sys.path))"
    # Add to path if needed
    export PYTHONPATH=$PYTHONPATH:$(pwd)
    ```

- **Issue**: Changes not taking effect
  - **Fix**: Reload or restart components
  - **Commands**:
    ```bash
    # For shell scripts
    hash -r
    # For Python modules
    tekton restart [component]
    ```

- **Issue**: Tests failing mysteriously
  - **Fix**: Check environment and dependencies
  - **Commands**:
    ```bash
    # Verify test environment
    which python
    pip list | grep -E "(pytest|mock)"
    # Run with debug
    pytest -vvs tests/test_feature.py
    ```

## Success Verification
- [ ] Feature works in isolation: Direct Python execution succeeds
- [ ] Integration tests pass: `pytest tests/integration/`
- [ ] End-to-end works: Command runs from shell
- [ ] No regressions: Existing tests still pass
- [ ] CI can explain it: `aish numa "explain how X works"`

## Documentation Pattern
```bash
# As you develop, document
echo "## Feature: X" >> feature_notes.md
echo "### Decision: Use approach Y because..." >> feature_notes.md

# Capture CI explanations
aish --capture numa "document how feature X works"

# Create user documentation
aish numa "write user guide for feature X" > docs/feature_x_guide.md
```

## Next Workflows
- If tests fail: [Bug Investigation workflow]
- If integration issues: [Integration Debugging workflow]  
- If complete: [Code Review Preparation workflow]

## Real Example
```bash
$ cd ~/projects/github/Coder-C
$ git checkout -b feature/aish-explain-command

$ aish forward numa $(aish whoami)
Forwarding numa messages to Casey_Terminal

$ find . -name "*.py" -path "*/commands/*" | grep -v __pycache__
./shared/aish/src/commands/forward.py
./shared/aish/src/commands/purpose.py
./shared/aish/src/commands/terma.py

$ aish numa "show me the pattern for adding a new aish command"
[Numa explains the command pattern with examples]

$ cat > shared/aish/src/commands/explain.py << 'EOF'
def explain_command(args, shell):
    """Explain Python errors and concepts."""
    # Implementation here
    return "Explanation: ..."
EOF

$ # Test it
$ cd shared/aish
$ python -c "from src.commands.explain import explain_command; print(explain_command(['test'], None))"
Explanation: ...

$ # Integrate with main shell
$ # Edit aish to add explain command routing...

$ # Test end-to-end
$ aish explain "NameError: name 'foo' is not defined"
The NameError occurs when Python encounters a name that hasn't been defined...
```

## Notes
- Small, tested increments are faster than big changes
- Use CI throughout, not just when stuck
- Capture key decisions and explanations as you go
- Test in isolation before integration
- Casey's wisdom: "Let the CI see your code early and often"
- The best features are discovered during implementation