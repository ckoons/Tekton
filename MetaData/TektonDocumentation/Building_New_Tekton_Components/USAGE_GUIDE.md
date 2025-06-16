# Building New Tekton Components - Usage Guide

This guide explains how to use the Building_New_Tekton_Components documentation set to create a new component for the Tekton ecosystem.

## Quick Start

**Goal**: Build a new Tekton component from scratch

**Time Required**: 2-4 hours for basic component, 1-2 days for full implementation

**Prerequisites**:
- Python 3.8+
- Basic understanding of FastAPI
- Familiarity with async/await patterns
- Access to Tekton codebase

## ⚠️ CRITICAL UPDATE: Shared Utilities Are Now Mandatory

As of the Shared Utilities Sprint, all new components MUST use the shared utilities. Key changes:

1. **No more optional imports** - All `shared.utils.*` imports are required
2. **Lifespan pattern is mandatory** - No `@app.on_event` decorators
3. **Use shared logging** - `setup_component_logging()` not `logging.getLogger()`
4. **Never hardcode ports** - Always use `get_component_config()`
5. **Socket release delay required** - 0.5s delay after shutdown

**Start with [Shared_Patterns_Reference.md](./Shared_Patterns_Reference.md) to see all requirements!**

## Documentation Overview

The documentation is organized in a logical progression from concept to implementation:

```
1. README.md                        # Start here - Overview and philosophy
2. Component_Architecture_Guide.md  # Understand the architecture
3. Step_By_Step_Tutorial.md        # Follow complete example
4. Backend_Implementation_Guide.md  # Build your backend
5. UI_Implementation_Guide.md       # Create your UI
6. UI_Styling_Standards.md         # Apply styling standards
7. Shared_Patterns_Reference.md    # ⚠️ CRITICAL - Required patterns
8. Testing_Guide.md                # Write and run tests
9. Documentation_Requirements.md    # Document your component
```

## Step-by-Step Process

### Phase 1: Planning (30 minutes)

1. **Read the Overview** ([README.md](./README.md))
   - Understand the "semper progresso" philosophy
   - Review what makes a Tekton component
   - Note the latest patterns to follow

2. **Study the Architecture** ([Component_Architecture_Guide.md](./Component_Architecture_Guide.md))
   - Understand Single Port Architecture
   - Learn about service layers
   - Review communication patterns

3. **Choose Your Port**
   - Check [Shared_Patterns_Reference.md](./Shared_Patterns_Reference.md#port-configuration) 
   - Find an available port (8015-8099 range)
   - Update port assignments when claiming

### Phase 2: Learning by Example (1 hour)

4. **Follow the Tutorial** ([Step_By_Step_Tutorial.md](./Step_By_Step_Tutorial.md))
   - Work through the "Nexus" example
   - Understand each implementation phase
   - See how components fit together
   - Use as a template for your component

### Phase 3: Backend Implementation (2-3 hours)

5. **Set Up Your Project**
   ```bash
   # From Tekton root
   mkdir -p YourComponent/{yourcomponent,tests,ui,examples}
   cd YourComponent
   ```

6. **Implement the Backend** ([Backend_Implementation_Guide.md](./Backend_Implementation_Guide.md))
   - Create setup.py and requirements.txt
   - Build API server with FastAPI
   - Implement MCP endpoints
   - Create CLI interface
   - Add core business logic

7. **Use Shared Patterns** ([Shared_Patterns_Reference.md](./Shared_Patterns_Reference.md))
   - Environment configuration
   - Hermes registration
   - Health checks
   - Error handling
   - Logging setup

### Phase 4: UI Implementation (2-3 hours)

8. **Create UI Component** ([UI_Implementation_Guide.md](./UI_Implementation_Guide.md))
   - Build HTML structure
   - Implement JavaScript controller
   - Add WebSocket support
   - Integrate with Hephaestus

9. **Apply Styling Standards** ([UI_Styling_Standards.md](./UI_Styling_Standards.md))
   - Use BEM naming convention
   - Apply component colors
   - Follow accessibility guidelines
   - Ensure responsive design

### Phase 5: Testing (1-2 hours)

10. **Write Tests** ([Testing_Guide.md](./Testing_Guide.md))
    - Set up test structure
    - Write unit tests
    - Add integration tests
    - Test MCP endpoints
    - Run test suite

### Phase 6: Documentation (1 hour)

11. **Document Your Component** ([Documentation_Requirements.md](./Documentation_Requirements.md))
    - Create README.md
    - Write API reference
    - Add user guide
    - Document integration points
    - Include MCP tool descriptions

### Phase 7: Integration (30 minutes)

12. **Final Integration Steps**
    - Test with `tekton-launch`
    - Verify Hermes registration
    - Check UI in Hephaestus
    - Update port assignments
    - Create PR

## Common Workflows

### Creating a Simple Component

If you just need a basic component without complex features:

1. Copy the structure from Step_By_Step_Tutorial.md
2. Modify the business logic in core/
3. Update MCP tools for your use case
4. Simplify the UI to show basic status
5. Skip advanced features initially

### Adding to Existing Component

When extending an existing component:

1. Study the component's current structure
2. Follow its established patterns
3. Add new endpoints to existing routers
4. Extend UI tabs rather than restructuring
5. Update documentation incrementally

### Debugging Common Issues

**Port Already in Use**
- Check `lsof -i :PORT`
- Verify port assignments
- Use a different port if needed

**Hermes Registration Fails**
- Ensure Hermes is running (port 8001)
- Check network connectivity
- Verify registration payload

**UI Not Loading**
- Component must be registered with Hermes
- Check browser console for errors
- Verify WebSocket connection

**Import Errors**
- Run setup.sh to install dependencies
- Check PYTHONPATH includes Tekton
- Verify shared utilities are available

## Best Practices Checklist

Before considering your component complete:

- [ ] **Architecture**
  - [ ] Single port for all services
  - [ ] Proper service separation
  - [ ] Clean dependency management

- [ ] **Backend**
  - [ ] FastAPI server running
  - [ ] MCP endpoints implemented
  - [ ] CLI commands working
  - [ ] Hermes registration successful
  - [ ] Health endpoint responding

- [ ] **UI**
  - [ ] Component loads in Hephaestus
  - [ ] All tabs functioning
  - [ ] WebSocket connected
  - [ ] Responsive design working
  - [ ] BEM naming used consistently

- [ ] **Quality**
  - [ ] Tests passing
  - [ ] Documentation complete
  - [ ] Code under file size limits (where possible)
  - [ ] Errors handled gracefully
  - [ ] Logging implemented

- [ ] **Integration**
  - [ ] Works with tekton-launch
  - [ ] Appears in tekton-status
  - [ ] Interacts with other components
  - [ ] Follows Tekton patterns

## Getting Help

### Documentation Questions

If something in the documentation is unclear:
1. Check the specific guide's examples
2. Look at existing components for patterns
3. Review the Step_By_Step_Tutorial for complete context

### Implementation Issues

For implementation problems:
1. Check Shared_Patterns_Reference for common solutions
2. Look at similar existing components
3. Verify you're using the latest patterns
4. Ensure environment is set up correctly

### Advanced Topics

These guides focus on getting started. For advanced topics:
- Performance optimization
- Complex MCP tool chains  
- Advanced UI visualizations
- Cross-component orchestration

Look at mature components like Athena or Ergon for examples.

## Summary

Building a Tekton component is straightforward when you:
1. Follow the established patterns
2. Keep implementations simple
3. Focus on your component's core purpose
4. Integrate properly with the ecosystem

Remember the philosophy: **"semper progresso"** - always progress, always improve. Don't worry about perfection on the first pass. Build something that works, then iterate and improve.

The documentation provides everything you need. Work through it systematically, and you'll have a working component integrated into Tekton within a day.

---

*Start with the [README.md](./README.md) and begin your journey!*