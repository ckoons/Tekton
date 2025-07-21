# Prometheus Renovation Sprint

## Overview
This is a **template sprint** that should be copied and applied to each Tekton component that needs renovation. The goal is to bring all components up to current standards and patterns.

## How to Use This Template

1. **Copy this directory** to create a component-specific sprint:
   ```bash
   cp -r Renovate_Template_Sprint Prometheus_Renovation_Sprint
   ```

2. **Replace [COMPONENT]** with the actual component name in all files

3. **Follow the checklist** in order - each item builds on previous ones

4. **Update DAILY_LOG.md** as you work through the checklist

5. **Use HANDOFF.md** when switching sessions

## Components Needing Renovation

### Priority 1 - Core Infrastructure
- [ ] Apollo - Attention/prediction 
- [ ] Athena - Knowledge management
- [ ] Hermes - Message bus
- [ ] Rhetor - AI orchestration

### Priority 2 - User-Facing
- [ ] Numa - Main orchestrator
- [ ] Prometheus - Planning
- [ ] Telos - Project goals
- [ ] Metis - Workflows

### Priority 3 - Support Systems
- [ ] Harmonia - Integration
- [ ] Synthesis - Synthesis  
- [ ] Sophia - Learning
- [ ] Noesis - Discovery
- [ ] Engram - Memory
- [ ] Ergon - Agents
- [ ] Penia - Budget
- [ ] Terma - Terminals
- [ ] Tekton-Core - Projects

## Standard Patterns to Apply

1. **Configuration**: Use TektonEnviron exclusively
2. **URLs**: Use tekton_url() helper
3. **Ports**: No hardcoding - use environment
4. **Testing**: Organized in tests/[component]/
5. **UI**: Real data only, no mocks
6. **MCP**: All AI communication through aish MCP
7. **Errors**: Consistent error handling
8. **Logging**: Proper log levels and formatting

## Success Metrics

Each renovated component should:
- Pass all tests (old and new)
- Work with current main branch
- Follow all standard patterns
- Have updated documentation
- Show real data in UI
- Use aish MCP for AI communication
