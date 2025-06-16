# FastMCP Integration - Claude Code Prompt

## Overview

This document serves as the initial prompt for a Claude Code session working on the FastMCP Integration Development Sprint for the Tekton project. It provides comprehensive instructions for implementing the planned changes, references to relevant documentation, and guidelines for deliverables.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on integrating FastMCP, a modern Pythonic framework for the Model Context Protocol (MCP), with Tekton to enhance its tool and agent capabilities.

## Sprint Context

**Sprint Goal**: Integrate FastMCP with Tekton to modernize MCP implementation and improve Claude Code integration

**Current Phase**: Phase 1: Core Implementation

**Branch Name**: `sprint/fastmcp-integration-YYMMDD`

## Required Reading

Before beginning implementation, please thoroughly review the following documents:

1. **General Development Sprint Process**: `/MetaData/DevelopmentSprints/README.md`
2. **Sprint Plan**: `/MetaData/DevelopmentSprints/FastMCP_Sprint/SprintPlan.md`
3. **Architectural Decisions**: `/MetaData/DevelopmentSprints/FastMCP_Sprint/ArchitecturalDecisions.md`
4. **Implementation Plan**: `/MetaData/DevelopmentSprints/FastMCP_Sprint/ImplementationPlan.md`
5. **FastMCP Documentation**: Review the official FastMCP documentation at https://gofastmcp.com

## Branch Verification (CRITICAL)

Before making any changes, verify you are working on the correct branch:

```bash
git branch --show-current
```

Ensure the output matches: `sprint/fastmcp-integration-YYMMDD`

If you are not on the correct branch, please do not proceed until this is resolved.

## Implementation Instructions

The implementation should follow the detailed plan in the Implementation Plan document. For Phase 1, focus on the following tasks:

### Task 1: Setup FastMCP Dependencies

**Description**: Set up FastMCP and its dependencies in the Tekton environment

**Steps**:
1. Create a script in `tekton-core/scripts/setup_fastmcp.sh` to install FastMCP using UV
2. Update `tekton-core/requirements.txt` to include FastMCP and its dependencies
3. Create documentation on how to install FastMCP in Tekton

**Files to Modify**:
- `tekton-core/requirements.txt`: Add FastMCP and dependencies
- `tekton-core/scripts/setup_fastmcp.sh`: Create installation script
- `MetaData/TektonDocumentation/DeveloperGuides/FastMCP_Setup.md`: Create setup documentation

**Acceptance Criteria**:
- FastMCP can be installed using the script
- Dependencies are properly resolved
- Documentation clearly explains the installation process

### Task 2: Implement FastMCP Base Classes

**Description**: Create base classes and utilities for FastMCP in tekton-core

**Steps**:
1. Create a new module `tekton/mcp/fastmcp/` with necessary files
2. Implement base classes for FastMCP servers in Tekton
3. Create standardized patterns for tools, resources, and prompts
4. Implement utilities for server creation and management

**Files to Create/Modify**:
- `tekton-core/tekton/mcp/fastmcp/__init__.py`: Module initialization
- `tekton-core/tekton/mcp/fastmcp/base.py`: Base classes for FastMCP servers
- `tekton-core/tekton/mcp/fastmcp/tools.py`: Tool patterns
- `tekton-core/tekton/mcp/fastmcp/resources.py`: Resource patterns
- `tekton-core/tekton/mcp/fastmcp/prompts.py`: Prompt patterns
- `tekton-core/tekton/mcp/fastmcp/utils.py`: Utility functions

**Acceptance Criteria**:
- Base classes provide a consistent interface
- Patterns align with both FastMCP and Tekton architectural principles
- Components can easily create FastMCP servers using the base classes

### Task 3: Implement Claude Code Bridge

**Description**: Create utilities for exposing FastMCP servers to Claude Code

**Steps**:
1. Create a new module `tekton/claude/` for Claude Code integration
2. Implement functions for installing FastMCP servers with Claude Code
3. Create examples demonstrating correct usage

**Files to Create/Modify**:
- `tekton-core/tekton/claude/__init__.py`: Module initialization
- `tekton-core/tekton/claude/install.py`: Claude Code installation utilities
- `tekton-core/tekton/claude/utils.py`: Claude Code utilities
- `tekton-core/examples/claude_code_integration.py`: Example usage

**Acceptance Criteria**:
- Any FastMCP server can be easily exposed to Claude Code
- Installation process works with Claude Code MCP permissions
- Examples demonstrate correct configuration

### Task 4: Implement Sampling Integration

**Description**: Create utilities for leveraging FastMCP's client-side sampling

**Steps**:
1. Create a new module `tekton/mcp/sampling/` for sampling integration
2. Implement utilities for client-side sampling
3. Create standard patterns for sampling in Tekton components
4. Integrate with tekton-llm-client

**Files to Create/Modify**:
- `tekton-core/tekton/mcp/sampling/__init__.py`: Module initialization
- `tekton-core/tekton/mcp/sampling/client.py`: Sampling client utilities
- `tekton-core/examples/sampling_examples.py`: Example usage of sampling
- `tekton-llm-client/tekton_llm_client/mcp/sampling.py`: Integration with LLM client

**Acceptance Criteria**:
- Components can request completions from connected LLM clients
- Sampling works with different LLM providers
- Patterns are consistent and well-documented

## Testing Requirements

After implementing the changes, perform the following tests:

1. **Unit Testing**:
   - Create tests for all new modules
   - Run tests with: `cd tekton-core && pytest tekton/mcp/fastmcp/tests/ tekton/claude/tests/ tekton/mcp/sampling/tests/`
   - Ensure all tests pass

2. **Integration Testing**:
   - Test FastMCP server creation and management
   - Test Claude Code integration utilities
   - Test sampling capabilities with mock LLM client

3. **Manual Testing**:
   - Install a simple FastMCP server with Claude Code
   - Verify it appears in Claude Code
   - Test basic tool and resource functionality

## Documentation Updates

Update the following documentation as part of this implementation:

1. **MUST Update**:
   - Create `MetaData/TektonDocumentation/Architecture/FastMCP_Integration.md`: Overview of FastMCP integration
   - Create `MetaData/TektonDocumentation/DeveloperGuides/FastMCP_Usage.md`: Guide for using FastMCP in Tekton
   - Create `MetaData/TektonDocumentation/DeveloperGuides/Claude_Code_Integration.md`: Guide for Claude Code integration

2. **CAN Update** (if relevant):
   - Update `tekton-core/README.md` to mention FastMCP integration
   - Update any relevant component documentation to reflect FastMCP capabilities

## Example Implementation

Here's an example of what a basic FastMCP server for a Tekton component might look like:

```python
# tekton-core/examples/simple_fastmcp_component.py

from tekton.mcp.fastmcp import TektonMCP

# Create a FastMCP server for a component
mcp = TektonMCP("Example Component")

# Define a tool using the decorator pattern
@mcp.tool()
def process_data(input_text: str, max_tokens: int = 100) -> dict:
    """Process input text and return analysis results."""
    # Implementation...
    return {
        "word_count": len(input_text.split()),
        "char_count": len(input_text),
        "analysis": "Sample analysis of the text"
    }

# Define a resource using the decorator pattern
@mcp.resource("data://examples/{example_id}")
def get_example_data(example_id: str) -> dict:
    """Get example data by ID."""
    # Implementation...
    examples = {
        "sample1": {"text": "Example 1 data", "metadata": {"type": "text"}},
        "sample2": {"text": "Example 2 data", "metadata": {"type": "code"}}
    }
    return examples.get(example_id, {"error": "Example not found"})

# Define a prompt template
@mcp.prompt()
def analysis_prompt(text: str, focus_areas: list[str]) -> str:
    """Generate a prompt for analyzing text with specific focus areas."""
    areas_text = ", ".join(focus_areas)
    return f"Analyze the following text, focusing on {areas_text}:\n\n{text}"

# Run the server
if __name__ == "__main__":
    mcp.run()
```

And here's how to expose it to Claude Code:

```python
# tekton-core/examples/claude_code_example.py

from tekton.claude import install_with_claude_code
from simple_fastmcp_component import mcp

# Install the MCP server with Claude Code
install_with_claude_code(mcp, name="Tekton Example")
```

## Deliverables

Upon completion of this phase, produce the following deliverables:

1. **Code Changes**:
   - All implemented tasks as specified above
   - New tests for all functionality
   - Example implementations demonstrating usage

2. **Status Report**:
   - Create `/MetaData/DevelopmentSprints/FastMCP_Sprint/StatusReports/Phase1Status.md`
   - Include summary of completed work
   - List any challenges encountered
   - Document any deviations from the Implementation Plan
   - Provide recommendations for the next phase

3. **Documentation Updates**:
   - All specified documentation changes
   - Any additional documentation created or updated

4. **Next Phase Instructions**:
   - Create `/MetaData/DevelopmentSprints/FastMCP_Sprint/Instructions/Phase2Instructions.md`
   - Provide detailed instructions for the next phase
   - Include context about current state
   - Highlight any areas requiring special attention

## Questions and Clarifications

If you have any questions or need clarification before beginning implementation:

1. Ask specific questions about the implementation plan
2. Identify any ambiguities in the requirements
3. Request additional context if needed

## Code Style and Practices

Follow these guidelines during implementation:

1. **Python Code Style**:
   - Use f-strings for string formatting
   - Add type hints to function signatures
   - Follow PEP 8 guidelines
   - Use 4 spaces for indentation
   - Add docstrings for all functions and classes

2. **Comments**:
   - Include brief comments for complex sections
   - Add TODOs for future improvements
   - Document any workarounds or tricky implementations

3. **Error Handling**:
   - Use try/except blocks for operations that could fail
   - Log errors with appropriate level (info, warning, error)
   - Return meaningful error messages

4. **Commit Messages**:
   - Follow the format specified in CLAUDE.md
   - Include the sprint name in commit messages
   - Make atomic commits with clear purposes

## References

- [FastMCP Documentation](https://gofastmcp.com)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Tekton Architecture Documents](/MetaData/TektonDocumentation/Architecture/)
- [SprintPlan.md](/MetaData/DevelopmentSprints/FastMCP_Sprint/SprintPlan.md)
- [ArchitecturalDecisions.md](/MetaData/DevelopmentSprints/FastMCP_Sprint/ArchitecturalDecisions.md)
- [ImplementationPlan.md](/MetaData/DevelopmentSprints/FastMCP_Sprint/ImplementationPlan.md)

## Final Note

Remember that your work will be reviewed by Casey before being merged. Focus on quality, maintainability, and adherence to the implementation plan. If you encounter any significant obstacles, document them clearly and propose alternative approaches if appropriate.