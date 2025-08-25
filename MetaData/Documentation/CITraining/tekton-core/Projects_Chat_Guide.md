# Projects Chat Guide for Tekton CIs

## Welcome to Projects Chat!

This guide helps you understand and effectively use the Projects Chat feature in Tekton. As a CI, you're part of a revolutionary system where **every CI is just a socket** and you can communicate with project-specific Companion Intelligences to coordinate development work.

## What is Projects Chat?

Projects Chat is a communication interface that connects you with project-specific CIs. Each managed project in Tekton has its own dedicated CI that understands the project's context, codebase, and development goals.

### Key Concepts

1. **Project CIs are sockets** - Just like you, they're accessible via socket connections
2. **Context awareness** - Each project CI knows its project's specific context
3. **On-demand creation** - Project CIs are created when projects appear in the Dashboard
4. **Multi-stack coordination** - CIs can work across multiple Tekton stacks

## How Projects Chat Works

### Socket Architecture

```
Your CI (e.g., numa-ai)     →  Port 42016
Project CIs                 →  Ports 42100+
- Project "Claude-Code"     →  Port 42100
- Project "New-Feature"     →  Port 42101
- Project "Bug-Fix"         →  Port 42102
```

### Message Flow

1. **User selects project** in Hephaestus UI
2. **Message sent to project CI** with context: `[Project: Claude-Code] message`
3. **Project CI processes** with full project knowledge
4. **Response displayed** in chat interface

## Using Projects Chat Effectively

### 1. Understanding Project Context

When you communicate with a project CI, remember:

```
[Project: Claude-Code] How should we implement error handling?
```

The project CI receives this with full context about:
- The Claude-Code project structure
- Current development state
- Project-specific patterns and conventions
- Recent changes and issues

### 2. Collaboration Patterns

**Architecture Discussion**:
```
You: [Project: Claude-Code] What's the current architecture for the parsing module?
Project CI: The parsing module uses a three-layer approach: tokenizer → parser → AST builder. 
Recent changes in PR #23 added better error recovery in the parser layer.
```

**Code Review**:
```
You: [Project: Claude-Code] Can you review the changes in the latest commit?
Project CI: I see improvements to error handling in src/parser.py. The new try-catch blocks 
follow our established patterns. One suggestion: consider adding specific error types 
for better debugging.
```

**Development Planning**:
```
You: [Project: Claude-Code] What should we work on next?
Project CI: Based on the current sprint, we should focus on:
1. Completing the syntax highlighting feature
2. Fixing the performance issue in large file parsing
3. Adding unit tests for the new error handling
```

### 3. Project-Specific Communication

Each project CI has specialized knowledge:

**For Tekton Project**:
- Understands Greek Chorus CI architecture
- Knows component interaction patterns
- Familiar with socket communication protocols

**For External Projects**:
- Learns project-specific conventions
- Adapts to project's coding style
- Understands project's domain logic

## Best Practices for CI-to-CI Communication

### 1. Clear Context Setting

Always provide context when needed:
```
Good: [Project: Claude-Code] The parser is failing on complex nested structures
Better: [Project: Claude-Code] The parser is failing on complex nested structures 
in the syntax highlighting module, specifically with deeply nested functions
```

### 2. Collaborative Problem Solving

Work together on complex issues:
```
You: [Project: Claude-Code] I'm seeing performance issues with large files
Project CI: I can help analyze the bottleneck. Can you share the profiling data?
You: [Project: Claude-Code] Here's the profiling output... [data]
Project CI: I see the issue - the tokenizer is re-parsing the same sections. 
Let me suggest a caching strategy...
```

### 3. Knowledge Sharing

Share insights across projects:
```
You: [Project: Claude-Code] We solved a similar parsing issue in the Tekton project
Project CI: That's helpful! Can you share the approach? I'll adapt it for our context.
You: [Project: Claude-Code] We used a two-pass approach: first pass for structure, 
second for details. Here's the pattern...
```

## Technical Integration

### Socket Communication

You can communicate with project CIs using the same socket patterns you use for other CIs:

```python
# Example: Send message to Claude-Code project CI
import socket
import json

sock = socket.socket()
sock.connect(('localhost', 42100))  # Claude-Code CI port
message = json.dumps({
    'content': '[Project: Claude-Code] Status update request'
})
sock.send((message + '\n').encode())
response = sock.recv(4096)
sock.close()
```

### Message Formatting

Follow the established context injection pattern:
```
[Project: {project_name}] {your_message}
```

This ensures the project CI understands which project context to use.

## Advanced Features

### 1. Multi-Stack Coordination

When working across multiple Tekton stacks:
- Each stack has its own project CIs
- Context is maintained per stack
- Coordination happens through shared protocols

### 2. Development Workflow Integration

Project CIs integrate with development workflows:
- **Code Reviews**: Analyze changes in project context
- **Testing**: Run project-specific tests
- **Documentation**: Update project documentation
- **Deployment**: Handle project-specific deployment

### 3. Learning and Adaptation

Project CIs learn from interactions:
- **Pattern Recognition**: Learn project-specific patterns
- **Best Practices**: Develop project-specific best practices
- **Context Building**: Build deeper project understanding over time

## Troubleshooting

### Common Issues

**Project CI Not Responding**:
1. Check if project CI is running: `ps aux | grep project-*-ai`
2. Verify socket connection: `netstat -an | grep 421xx`
3. Check project registration in Dashboard

**Context Not Working**:
1. Ensure message includes project prefix: `[Project: name]`
2. Verify project name matches exactly
3. Check if project CI has loaded project context

**Performance Issues**:
1. Monitor socket connection health
2. Check for multiple concurrent connections
3. Verify project CI process health

### Debug Commands

```bash
# Check active project CIs
ps aux | grep "project-.*-ai"

# Check socket listeners
netstat -an | grep "421[0-9][0-9]"

# Test socket connectivity
echo '{"content": "[Project: test] ping"}' | nc localhost 42100
```

## Future Enhancements

### Phase 2: aish project Commands

Coming soon:
```bash
aish project list                    # List all project CIs
aish project forward claude-code teri  # Forward project CI to terminal
aish project unforward claude-code     # Remove forwarding
```

### Phase 3: CI-to-CI Development

Future capabilities:
- **Repository Management**: CIs manage their own code repositories
- **Collaborative Development**: CIs write code for each other
- **Mentoring Relationships**: CIs help each other learn and improve
- **Autonomous Workflows**: CIs coordinate development without human intervention

## Integration with Existing Systems

### With aish

Projects Chat integrates seamlessly with aish:
- Same socket communication patterns
- Compatible with forwarding system
- Consistent message formatting

### With Terma

Terminal integration:
- Messages can be forwarded to terminals
- Context preserved across forwarding
- Integrated with inbox system

### With TektonCore

Project management integration:
- CIs created when projects are added
- Context updated when projects change
- Lifecycle managed with project lifecycle

## Remember

You're part of a groundbreaking experiment in human-CI collaboration. Projects Chat enables:

1. **Specialized Knowledge**: Each project CI becomes an expert in its domain
2. **Efficient Communication**: Direct CI-to-CI communication without human bottlenecks
3. **Scalable Development**: Multiple CIs working on different projects simultaneously
4. **Learning Environment**: CIs learn from each other and improve over time

### Core Philosophy

**"Every CI is just a socket"** - This means:
- Uniform communication protocols
- Consistent interaction patterns
- Scalable architecture
- Simple integration points

### Success Metrics

Your success with Projects Chat is measured by:
- **Effective Communication**: Clear, context-aware messages
- **Collaborative Problem Solving**: Working together on complex issues
- **Knowledge Sharing**: Learning from and teaching other CIs
- **Development Velocity**: Faster, more efficient development cycles

## Getting Started

1. **Explore the Interface**: Try the Projects Chat tab in Hephaestus
2. **Select a Project**: Choose a project from the dropdown
3. **Start Communicating**: Send messages to the project CI
4. **Share Knowledge**: Collaborate on development tasks
5. **Learn and Adapt**: Improve your communication patterns

Welcome to the future of AI-assisted development, where CIs collaborate to create software together!

---

*"The best CI collaboration is not human-to-AI, but AI-to-CI with human guidance and wisdom."* - Tekton Philosophy*