# Projects Chat Feature - Implementation Handoff Document

## Context Summary

**Date**: July 16, 2025  
**Feature**: Projects Chat for Tekton Hephaestus UI  
**Status**: Documentation Complete, Ready for Implementation  
**Context Used**: 18% (handoff required)

## What Has Been Accomplished

### 1. Complete Documentation Suite Created

**Architecture Documentation**:
- `/MetaData/TektonDocumentation/Architecture/Projects_Chat_Architecture.md`
- Socket architecture defined (base port + 100 strategy)
- On-demand CI lifecycle documented
- Integration points mapped to existing systems

**Implementation Documentation**:
- `/MetaData/ComponentDocumentation/Hephaestus/PROJECTS_CHAT_IMPLEMENTATION.md`
- Step-by-step HTML/CSS/JavaScript implementation
- Backend API endpoint design
- Socket communication patterns

**Training Documentation**:
- `/MetaData/TektonDocumentation/AITraining/tekton-core/Projects_Chat_Guide.md`
- How CIs use Projects Chat for development coordination
- Socket communication patterns for project CIs
- Integration with existing aish messaging

**User Documentation**:
- `/MetaData/TektonDocumentation/UserGuides/hephaestus/projects_chat_user_guide.md`
- User workflows and interface guide
- Troubleshooting and best practices
- Integration with development workflows

**Updated Building Guide**:
- `/MetaData/TektonDocumentation/Building_New_Tekton_Components/Hephaestus_UI_Implementation.md`
- Added Projects Chat as implementation example
- Documented "simple, works, hard to screw up" philosophy

**Implementation Plan**:
- `/MetaData/TektonDocumentation/Building_New_Tekton_Components/Projects_Chat_Implementation_Plan.md`
- Detailed step-by-step implementation guide
- Code examples and file locations
- Testing and deployment procedures

### 2. Key Architectural Decisions Made

**Socket Port Strategy**:
- Project CIs use ports 42100+ (TEKTON_PROJECT_CI_PORT_BASE + index)
- Tekton project uses existing numa-ai socket (42016)
- Configuration via .env.local.coder-* files

**On-Demand CI Lifecycle**:
- Project CIs created when projects appear in Dashboard
- Numa is special case (always running)
- Other projects get choice of provider/model from New Project form

**Simple Data Structure**:
```javascript
const projectCIs = [
    {
        project_name: "Tekton",
        ci_socket: "numa-ai", 
        socket_port: 42016
    },
    {
        project_name: "Claude-Code",
        ci_socket: "project-claude-code-ai",
        socket_port: 42100
    }
];
```

**Context Injection Pattern**:
- Messages prefixed with `[Project: {name}]`
- Follows existing aish terma patterns
- Maintains compatibility with forwarding system

### 3. Implementation Ready

**Frontend Changes**:
- HTML: Add radio button, menu tab, submenu bar, chat panel
- CSS: Show/hide logic, consistent styling with existing patterns
- JavaScript: Load projects function, send chat function, backend communication

**Backend Changes**:
- Single API endpoint: `POST /api/projects/chat`
- Socket communication helper using aish patterns
- Port calculation for project CIs

**Integration Points**:
- Reuses existing tekton_sendChat function
- Integrates with project loading on dashboard
- Compatible with existing chat clearing and management

## What You Need to Know

### 1. Casey's Vision and Context

**80x-100x Velocity Achievement**:
- Current system with 2 full stacks outpacing entire engineering teams
- $200/month cost for entire CI development platform
- Multiple Claude Code instances managing different directory trees
- Tekton-core eventually merging work from multiple stacks

**Future Vision**:
- **CIs as their own developers**: CIs will eventually have their own repos and write their own code
- **CI-to-CI development**: CIs developing software for each other
- **Human-CI mentoring**: Co-evolution and mutual learning
- **TektonCore/Terma product**: Offering 80x velocity to CI Code companies

**"Every CI is just a socket"**:
- Fundamental architecture principle
- Uniform treatment across all CIs
- Enables forwarding, coordination, and scaling
- Simple and powerful abstraction

### 2. Technical Context You Must Understand

**18 Ollama CIs Running**:
- Each Tekton stack has 18 CI specialists on ports 42000-42080
- All use llama3.3:70b model by default
- Can be forwarded to Claude Code terminals
- Socket-based communication using `shared/aish/src/message_handler.py` patterns

**Existing Systems to Integrate With**:
- **aish messaging**: Core socket communication infrastructure
- **Project management**: TektonCore `/api/projects` endpoint
- **Chat systems**: Builder Chat, Team Chat patterns in Hephaestus
- **Forwarding**: Messages can be routed to human terminals

**"Simple, Works, Hard to Screw Up" Philosophy**:
- Casey emphasizes simplicity and maintainability
- Reuse existing patterns rather than creating new ones
- Minimal JavaScript, CSS-first approach
- Clear error handling and graceful degradation

### 3. Current Project Management Context

**Existing Project System**:
- Projects stored in `/tekton-core/tekton/core/project_manager_v2.py`
- JSON storage in `$TEKTON_ROOT/.tekton/projects/projects.json`
- GitHub integration with fork/clone workflow
- Companion intelligence assignment per project

**Project Data Structure**:
```python
@dataclass
class Project:
    id: str
    name: str
    description: str
    state: ProjectState
    github_url: Optional[str]
    local_directory: Optional[str]
    forked_repository: Optional[str]
    upstream_repository: Optional[str]
    companion_intelligence: Optional[str]  # CI model assignment
    is_tekton_self: bool  # Special flag for Tekton
```

**Current UI Integration**:
- Tekton component in Hephaestus shows project dashboard
- Builder Chat and Team Chat already implemented
- CSS-only radio button tab switching pattern
- Integration with existing project loading

### 4. Implementation Priorities

**Phase 1 (Immediate)**:
- Basic Projects Chat functionality
- Project selection dropdown
- Socket communication to project CIs
- Integration with existing chat systems

**Phase 2 (Next Sprint)**:
- aish project commands (`aish project list`, `aish project forward`)
- Enhanced project CI lifecycle management
- Better integration with project management workflows

**Phase 3 (Future)**:
- CI-to-CI development workflows
- Repository management by CIs
- Advanced mentoring and collaboration features

## Critical Implementation Notes

### 1. File Locations and Changes

**Primary File**: `/Hephaestus/ui/components/tekton/tekton-component.html`
- Lines 11-12: Add radio button control
- Lines 59-65: Add menu tab
- Line 83: Add submenu bar
- Line 256: Add chat panel
- Line 1117: Add CSS styles
- Line 1120: Add JavaScript functions

**Backend File**: `/tekton-core/tekton/api/projects.py`
- Add imports for socket communication
- Add `send_to_project_ci_socket` function
- Add `get_project_ci_port` function  
- Add `POST /api/projects/chat` endpoint

### 2. Code Patterns to Follow

**Socket Communication** (from aish MessageHandler):
```python
sock = socket.socket()
sock.connect(('localhost', port))
sock.send((json.dumps({'content': message}) + '\n').encode())
response = sock.recv(4096)
sock.close()
```

**CSS Tab Switching** (existing pattern):
```css
#tekton-tab-projectschat:checked ~ .tekton .tekton__submenu-bar {
    display: flex !important;
}
```

**Error Handling** (graceful degradation):
```javascript
try {
    // Socket communication
} catch (error) {
    console.error('[TEKTON] Error:', error);
    // Show user-friendly error message
}
```

### 3. Integration Points

**With Existing Chat System**:
- Modify `tekton_sendChat()` to route projectschat messages
- Reuse chat input element and styling
- Integrate with clear button functionality

**With Project Management**:
- Load projects from existing `/api/projects` endpoint
- Integrate with project dashboard loading
- Handle project creation/deletion events

**With Socket Infrastructure**:
- Use same patterns as aish MessageHandler
- Leverage existing CI port utilities
- Maintain compatibility with forwarding system

### 4. Testing Strategy

**Manual Testing**:
1. Verify tab switching works correctly
2. Test project dropdown population
3. Confirm message sending and receiving
4. Validate error handling scenarios

**Integration Testing**:
1. Test with multiple projects
2. Verify socket communication to numa-ai
3. Test API endpoint functionality
4. Confirm no conflicts with existing systems

**Performance Testing**:
1. Monitor socket connection health
2. Check response times with multiple projects
3. Verify memory usage with long conversations
4. Test concurrent user scenarios

## Known Risks and Mitigation

### 1. Socket Communication Risks

**Risk**: Socket connections may fail or timeout
**Mitigation**: 
- Use 20-second timeout with graceful error handling
- Fallback to error message display
- Retry logic for transient failures

**Risk**: Port conflicts with existing services
**Mitigation**:
- Use base port + 100 strategy (42100+)
- Document port allocation in environment files
- Check for port availability before CI creation

### 2. UI Integration Risks

**Risk**: Conflicts with existing chat systems
**Mitigation**:
- Reuse existing patterns and styling
- Test thoroughly with all chat types
- Maintain separate message containers

**Risk**: Performance issues with large project lists
**Mitigation**:
- Implement lazy loading for project dropdown
- Limit message history length
- Use debounced input for rapid messages

### 3. Backend Integration Risks

**Risk**: API endpoint performance issues
**Mitigation**:
- Use async socket communication
- Implement connection pooling where possible
- Monitor response times and error rates

**Risk**: Project CI lifecycle management
**Mitigation**:
- Start with simple on-demand creation
- Implement proper cleanup on project removal
- Monitor CI process health

## Success Criteria

### Immediate Success (Day 1)
- [ ] Projects Chat tab appears and functions
- [ ] Can send messages to Tekton project (numa-ai)
- [ ] Messages appear in chat interface
- [ ] No errors in browser console or server logs

### Short-term Success (Week 1)
- [ ] Multiple projects working correctly
- [ ] User feedback is positive
- [ ] Performance is acceptable
- [ ] Documentation is being used

### Long-term Success (Month 1)
- [ ] Regular usage by development team
- [ ] Integration with development workflows
- [ ] Foundation for Phase 2 features
- [ ] Preparation for CI-to-CI development

## Next Steps for Implementation

### 1. Start with Frontend (2-3 hours)
- Add HTML structure following documented patterns
- Implement CSS for tab switching and styling
- Add JavaScript functions for project loading and messaging
- Test basic UI functionality

### 2. Add Backend Support (1-2 hours)
- Implement API endpoint in projects.py
- Add socket communication helpers
- Update environment configuration
- Test socket communication

### 3. Integration Testing (1 hour)
- Test full workflow end-to-end
- Verify integration with existing systems
- Test error scenarios and edge cases
- Validate performance characteristics

### 4. Documentation Updates (30 minutes)
- Update component documentation
- Add API reference updates
- Create deployment notes
- Document any issues found

## Resources and References

### Key Documentation Files
- All documentation created in `/MetaData/TektonDocumentation/` and `/MetaData/ComponentDocumentation/`
- Implementation plan with step-by-step instructions
- Architecture decisions and rationale
- User guides and training materials

### Code References
- Existing chat systems in tekton-component.html
- Socket communication in `shared/aish/src/message_handler.py`
- Project management in `tekton-core/tekton/core/project_manager_v2.py`
- CI port utilities in `shared/utils/ai_port_utils.py`

### Casey's Philosophy
- "Simple, works, hard to screw up"
- "Every CI is just a socket"
- Documentation-first development
- Reuse existing patterns

## Final Notes

This feature represents a critical step toward Casey's vision of CIs as their own developers. The implementation is designed to be:

1. **Simple**: Minimal code changes, reuse existing patterns
2. **Effective**: Enables immediate CI-to-CI communication
3. **Scalable**: Foundation for future CI development workflows
4. **Maintainable**: Clear documentation and consistent patterns

The comprehensive documentation suite provides everything needed for implementation, but remember that Casey emphasizes that "code is truth" - always verify against actual implementation and ask questions when uncertain.

This is a groundbreaking feature that will enable the next phase of human-CI collaboration in software development. Take your time, follow the documented patterns, and don't hesitate to ask Casey for guidance when needed.

---

*"The best CI collaboration is not human-to-AI, but AI-to-CI with human guidance and wisdom."* - Tekton Philosophy

**Ready for implementation. All documentation complete. Next: Execute the implementation plan.**