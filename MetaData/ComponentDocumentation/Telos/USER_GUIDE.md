# Telos User Guide

## Introduction

Telos is the comprehensive requirements management and tracing system for the Tekton ecosystem. This guide will help you get started with Telos and show you how to use its key features to document, organize, track, and validate project requirements.

## Getting Started

### Installation

There are multiple ways to install Telos:

#### From Source

```bash
# Clone the repository
git clone https://github.com/example/tekton.git
cd tekton/Telos

# Install Telos and its dependencies
pip install -e .
```

#### With Tekton Installer

```bash
# Run the Tekton installer
./tekton-install.sh --components telos
```

### Starting Telos

You can start Telos in several ways:

```bash
# Start the Telos API server directly
telos-api

# Start with Tekton launcher
./scripts/tekton-launch --components telos

# Register with Hermes (required for full ecosystem integration)
python -m Telos/register_with_hermes.py
```

### Accessing Telos

Once started, Telos is available at:

- **API**: `http://localhost:8008/api`
- **WebSocket**: `ws://localhost:8008/ws`
- **Web UI**: Access through Hephaestus UI at `http://localhost:8080`

## Projects

Projects in Telos are containers for requirements and serve as the top-level organizational unit.

### Creating a Project

#### Using the Web UI

1. Navigate to the Telos component in Hephaestus
2. Click "New Project"
3. Enter project details:
   - **Name**: A descriptive name for your project
   - **Description**: A brief overview of the project
   - **Metadata**: Optional additional information
4. Click "Create Project"

#### Using the CLI

```bash
# Create a new project
telos project create --name "My Project" --description "Project description"
```

#### Using the API

```python
import requests

# Base URL
base_url = "http://localhost:8008"

# Create a project
response = requests.post(f"{base_url}/api/projects", json={
    "name": "API Project",
    "description": "Created via API"
})
project_id = response.json()["data"]["project_id"]
```

### Managing Projects

#### Listing Projects

```bash
# List all projects
telos project list
```

#### Viewing a Project

```bash
# View project details
telos project view --project-id <project_id>
```

#### Updating a Project

```bash
# Update project details
telos project update --project-id <project_id> --name "Updated Name" --description "Updated description"
```

#### Deleting a Project

```bash
# Delete a project
telos project delete --project-id <project_id>
```

## Requirements

Requirements are the core elements in Telos, representing individual user needs, features, or constraints.

### Creating Requirements

#### Using the Web UI

1. Navigate to your project in the Telos component
2. Click "Add Requirement"
3. Enter requirement details:
   - **Title**: A clear, concise title
   - **Description**: Detailed description of the requirement
   - **Type**: Functional, non-functional, constraint, etc.
   - **Priority**: Low, medium, high, critical
   - **Status**: New, in progress, completed, etc.
   - **Tags**: Optional keywords for categorization
   - **Parent**: Optional parent requirement for hierarchical organization
   - **Dependencies**: Optional requirements this one depends on
4. Click "Save Requirement"

#### Using the CLI

```bash
# Add a requirement
telos requirement add \
  --project-id <project_id> \
  --title "User Authentication" \
  --description "The system must authenticate users with username and password" \
  --type functional \
  --priority high
```

#### Using the API

```python
# Add a requirement
response = requests.post(f"{base_url}/api/projects/{project_id}/requirements", json={
    "title": "API Feature",
    "description": "This requirement was created via the API",
    "requirement_type": "functional",
    "priority": "high",
    "status": "new",
    "tags": ["api", "feature"]
})
requirement_id = response.json()["data"]["requirement_id"]
```

### Managing Requirements

#### Listing Requirements

```bash
# List all requirements in a project
telos requirement list --project-id <project_id>

# Filter requirements
telos requirement list --project-id <project_id> --status "new" --priority "high"
```

#### Viewing a Requirement

```bash
# View requirement details
telos requirement view --project-id <project_id> --requirement-id <requirement_id>
```

#### Updating a Requirement

```bash
# Update a requirement
telos requirement update \
  --project-id <project_id> \
  --requirement-id <requirement_id> \
  --title "Updated Title" \
  --status "in_progress"
```

#### Deleting a Requirement

```bash
# Delete a requirement
telos requirement delete --project-id <project_id> --requirement-id <requirement_id>
```

### Organizing Requirements

#### Hierarchical Structure

Telos supports hierarchical organization of requirements through parent-child relationships:

```bash
# Create a parent requirement
parent_id=$(telos requirement add \
  --project-id <project_id> \
  --title "User Management" \
  --description "User management capabilities" \
  --return-id)

# Create a child requirement
telos requirement add \
  --project-id <project_id> \
  --title "User Registration" \
  --description "Allow users to register accounts" \
  --parent-id $parent_id
```

#### Dependencies

Requirements can depend on other requirements:

```bash
# Create a dependency between requirements
telos trace add \
  --project-id <project_id> \
  --source-id <source_requirement_id> \
  --target-id <target_requirement_id> \
  --trace-type "depends_on" \
  --description "Feature A depends on Feature B"
```

#### Tagging

Tags provide flexible categorization:

```bash
# Add tags to a requirement
telos requirement update \
  --project-id <project_id> \
  --requirement-id <requirement_id> \
  --tags "security,user-management,critical"
```

### Validating Requirements

Telos can validate requirements for quality characteristics:

```bash
# Validate requirements
telos requirement validate \
  --project-id <project_id> \
  --requirement-id <requirement_id> \
  --types "completeness,clarity,testability"
```

The validation checks for common issues like:
- **Completeness**: Missing information, vague requirements
- **Clarity**: Ambiguous language, unclear objectives
- **Testability**: Verifiability, measurable criteria
- **Consistency**: Conflicts with other requirements

## Tracing and Relationships

Telos provides powerful tracing capabilities to maintain relationships between requirements.

### Creating Traces

#### Using the Web UI

1. Navigate to your project in the Telos component
2. Select a requirement
3. Click "Add Trace"
4. Select the target requirement
5. Choose the trace type (depends_on, implements, related_to, etc.)
6. Add an optional description
7. Click "Create Trace"

#### Using the CLI

```bash
# Create a trace
telos trace add \
  --project-id <project_id> \
  --source-id <source_requirement_id> \
  --target-id <target_requirement_id> \
  --trace-type "implements" \
  --description "Feature implements requirement"
```

#### Using the API

```python
# Create a trace
response = requests.post(f"{base_url}/api/projects/{project_id}/traces", json={
    "source_id": source_requirement_id,
    "target_id": target_requirement_id,
    "trace_type": "implements",
    "description": "Feature implements requirement"
})
trace_id = response.json()["data"]["trace_id"]
```

### Managing Traces

#### Listing Traces

```bash
# List all traces in a project
telos trace list --project-id <project_id>

# Filter traces
telos trace list --project-id <project_id> --trace-type "depends_on"
```

#### Updating Traces

```bash
# Update a trace
telos trace update \
  --project-id <project_id> \
  --trace-id <trace_id> \
  --trace-type "related_to" \
  --description "Updated description"
```

#### Deleting Traces

```bash
# Delete a trace
telos trace delete --project-id <project_id> --trace-id <trace_id>
```

### Visualization

Telos provides visualization tools for requirements and their relationships:

```bash
# Generate a relationship graph
telos viz requirements \
  --project-id <project_id> \
  --output requirements.png \
  --format png \
  --include-dependencies
```

## Planning Integration

Telos integrates with Prometheus for planning and execution.

### Analyzing Requirements for Planning

```bash
# Analyze requirements for planning readiness
telos planning analyze \
  --project-id <project_id> \
  --output analysis.json
```

### Creating a Plan from Requirements

```bash
# Create a plan from requirements
telos planning create-plan \
  --project-id <project_id> \
  --plan-name "Implementation Plan" \
  --requirements <requirement_id1>,<requirement_id2> \
  --start-date "2025-05-01"
```

### Tracking Requirement Implementation

```bash
# Get implementation status
telos planning status \
  --project-id <project_id> \
  --requirement-id <requirement_id>
```

## Export and Import

Telos supports exporting and importing requirements in various formats.

### Exporting Projects

```bash
# Export a project to JSON
telos project export \
  --project-id <project_id> \
  --format json \
  --output project_export.json

# Export requirements to CSV
telos requirement export \
  --project-id <project_id> \
  --format csv \
  --output requirements.csv
```

### Importing Projects

```bash
# Import a project from JSON
telos project import \
  --input project_export.json

# Import requirements from CSV
telos requirement import \
  --project-id <project_id> \
  --input requirements.csv
```

## Collaboration Features

Telos supports real-time collaboration on requirements.

### WebSocket Updates

Connect to the WebSocket interface for real-time updates:

```javascript
const ws = new WebSocket("ws://localhost:8008/ws");

// Listen for messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Received:", data);
};

// Register client
ws.send(JSON.stringify({
    type: "REGISTER",
    source: "client",
    target: "server",
    timestamp: Date.now(),
    payload: {}
}));

// Subscribe to project updates
ws.send(JSON.stringify({
    type: "PROJECT_SUBSCRIBE",
    source: "client",
    target: "server",
    timestamp: Date.now(),
    payload: {
        project_id: "your-project-id"
    }
}));
```

### Collaborative Editing

The Telos UI in Hephaestus supports collaborative editing of requirements:

1. Multiple users can edit the same project simultaneously
2. Changes are broadcast in real-time to all connected clients
3. Conflicts are resolved using operational transformation
4. User presence indicators show who is currently viewing or editing requirements

## LLM-Powered Features

Telos integrates with Rhetor for LLM-powered requirement refinement.

### Requirement Refinement

```bash
# Refine a requirement using LLM
telos refine requirement \
  --project-id <project_id> \
  --requirement-id <requirement_id> \
  --feedback "Make it more specific and testable"
```

### Quality Suggestions

```bash
# Get quality improvement suggestions
telos refine suggest \
  --project-id <project_id> \
  --requirement-id <requirement_id>
```

### Auto-Generation

```bash
# Generate requirements from a high-level description
telos refine generate \
  --project-id <project_id> \
  --description "A user authentication system with registration, login, and password reset" \
  --count 5
```

## Advanced Features

### Custom Fields

Add custom fields to requirements for project-specific information:

```bash
# Add a custom field definition
telos admin add-custom-field \
  --project-id <project_id> \
  --field-name "regulatory_compliance" \
  --field-type "string" \
  --required false

# Set a custom field value
telos requirement update \
  --project-id <project_id> \
  --requirement-id <requirement_id> \
  --metadata '{"regulatory_compliance": "GDPR Article 17"}'
```

### Webhooks

Configure webhooks for integration with external systems:

```bash
# Register a webhook
telos admin register-webhook \
  --url "https://example.com/webhook" \
  --events "requirement.created,requirement.updated" \
  --secret "webhook_secret"
```

### Bulk Operations

Perform operations on multiple requirements at once:

```bash
# Update multiple requirements
telos requirement bulk-update \
  --project-id <project_id> \
  --requirements <req_id1>,<req_id2>,<req_id3> \
  --status "in_progress" \
  --priority "high"

# Delete multiple requirements
telos requirement bulk-delete \
  --project-id <project_id> \
  --requirements <req_id1>,<req_id2>,<req_id3>
```

## Best Practices

### Writing Good Requirements

1. **Be Specific**: Avoid vague terms like "user-friendly" or "fast"
2. **Be Measurable**: Include concrete criteria (e.g., "response time < 200ms")
3. **Be Testable**: Ensure requirements can be verified
4. **Use Simple Language**: Avoid complex jargon when possible
5. **Be Consistent**: Use uniform terminology across requirements
6. **Be Atomic**: Each requirement should describe a single capability
7. **Include Rationale**: Explain why a requirement exists
8. **Be Feasible**: Ensure requirements are technically possible

### Organization Tips

1. **Use Hierarchy**: Group related requirements under parent requirements
2. **Apply Consistent Tags**: Develop a tagging system for easy filtering
3. **Track Dependencies**: Explicitly link related requirements
4. **Use Status Fields**: Keep requirement status up-to-date
5. **Validate Regularly**: Run validation checks to ensure quality
6. **Review Periodically**: Schedule requirement reviews
7. **Maintain Traceability**: Link requirements to designs, code, and tests

## Troubleshooting

### Common Issues

1. **Connection Problems**:
   - Check that the Telos server is running
   - Verify the port is correct (default: 8008)
   - Ensure network connectivity

2. **Permission Errors**:
   - Verify you have the correct permissions
   - Check that you're authenticated if authentication is enabled

3. **Data Not Saving**:
   - Ensure the storage directory is writable
   - Check that the file format is correct
   - Verify that required fields are provided

4. **Real-time Updates Not Working**:
   - Check WebSocket connection
   - Ensure you're subscribed to the correct project
   - Verify that the message format is correct

### Getting Help

If you encounter issues not covered in this guide:

1. Check the logs:
   ```bash
   # View Telos logs
   tail -f logs/telos.log
   ```

2. Enable debug mode:
   ```bash
   # Run with debug logging
   TELOS_LOG_LEVEL=DEBUG telos-api
   ```

3. Contact support or open an issue in the Tekton repository

## Command Reference

Below is a quick reference of commonly used Telos CLI commands:

### Project Commands

```bash
telos project create --name <name> --description <description>
telos project list
telos project view --project-id <project_id>
telos project update --project-id <project_id> --name <name> --description <description>
telos project delete --project-id <project_id>
telos project export --project-id <project_id> --format <format> --output <file>
telos project import --input <file>
```

### Requirement Commands

```bash
telos requirement add --project-id <project_id> --title <title> --description <description>
telos requirement list --project-id <project_id> [--status <status>] [--priority <priority>]
telos requirement view --project-id <project_id> --requirement-id <requirement_id>
telos requirement update --project-id <project_id> --requirement-id <requirement_id> --title <title>
telos requirement delete --project-id <project_id> --requirement-id <requirement_id>
telos requirement validate --project-id <project_id> --requirement-id <requirement_id>
telos requirement export --project-id <project_id> --format <format> --output <file>
telos requirement import --project-id <project_id> --input <file>
```

### Trace Commands

```bash
telos trace add --project-id <project_id> --source-id <source_id> --target-id <target_id> --trace-type <type>
telos trace list --project-id <project_id> [--trace-type <type>]
telos trace view --project-id <project_id> --trace-id <trace_id>
telos trace update --project-id <project_id> --trace-id <trace_id> --trace-type <type>
telos trace delete --project-id <project_id> --trace-id <trace_id>
```

### Planning Commands

```bash
telos planning analyze --project-id <project_id> --output <file>
telos planning create-plan --project-id <project_id> --plan-name <name> --requirements <req_ids>
telos planning status --project-id <project_id> --requirement-id <requirement_id>
```

### Refinement Commands

```bash
telos refine requirement --project-id <project_id> --requirement-id <requirement_id> --feedback <feedback>
telos refine suggest --project-id <project_id> --requirement-id <requirement_id>
telos refine generate --project-id <project_id> --description <description> --count <count>
```

### Visualization Commands

```bash
telos viz requirements --project-id <project_id> --output <file> --format <format>
telos viz traces --project-id <project_id> --output <file> --format <format>
telos viz hierarchy --project-id <project_id> --output <file> --format <format>
```

## Conclusion

Telos provides a comprehensive system for managing requirements throughout the project lifecycle. By following this guide, you should be able to effectively document, organize, track, and validate your requirements, ensuring they serve as a reliable foundation for your project's success.

For more detailed information, refer to the [Technical Documentation](./TECHNICAL_DOCUMENTATION.md), [API Reference](./API_REFERENCE.md), and [Integration Guide](./INTEGRATION_GUIDE.md).