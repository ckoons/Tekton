# Task Assignment Examples for TektonCore

## Philosophy

**"Errors are gold, they help us improve. Questions that are sincere are the best ways to communicate. We evolve, change and hope to improve. If you stumble, get up and get back in the race, you can win."**

Effective task assignment is the foundation of successful multi-AI coordination. This guide provides practical examples and patterns for assigning work to Claude sessions through the Terma terminal system.

## Understanding the Assignment System

### The `aish purpose` Mechanism

When you assign a task to a Claude session, you're setting their context and focus through the `aish purpose` command. This creates a persistent context that guides their work throughout the session.

**Basic Structure**:
```
aish purpose: [Role] working on [Task] for [Project Context]
```

**Key Components**:
- **Role**: What type of work they're doing (architect, developer, tester, etc.)
- **Task**: Specific work to be accomplished
- **Project Context**: How this fits into the bigger picture
- **Success Criteria**: What constitutes completion
- **Resources**: Where to find information and examples

## Assignment Examples by Task Type

### Architecture and Design Tasks

**Example 1: API Design**
```
aish purpose: Senior API Architect working on User Authentication System design

Task: Design the complete API contract for user authentication including:
- Login/logout endpoints
- Token refresh mechanism  
- Password reset flow
- Multi-factor authentication support

Project Context: This is the foundation for the new user management system. Other CIs will implement UI components and testing based on your API design.

Success Criteria:
- Complete OpenAPI specification
- Clear request/response examples
- Error handling documentation
- Security considerations documented

Resources:
- Existing API patterns in `/shared/api/`
- Security guidelines in `/docs/security/`
- Current user model in `/models/user.py`

Timeline: 2 days
Branch: sprint/alice-auth-api-design
Priority: High (blocks other work)

Questions encouraged about: Security requirements, integration points, performance considerations
```

**Example 2: System Architecture**
```
aish purpose: System Architect working on microservices decomposition

Task: Design the service boundaries and communication patterns for breaking the monolithic user service into microservices:
- User profile service
- Authentication service  
- Authorization service
- User preferences service

Project Context: Part of the system scalability improvement initiative. This design will guide implementation work for the next 2 sprints.

Success Criteria:
- Service boundary definitions
- Inter-service communication patterns
- Data consistency strategy
- Migration plan from monolith

Resources:
- Current monolith structure in `/services/user/`
- Microservices patterns in `/docs/architecture/`
- Service mesh documentation in `/docs/infrastructure/`

Timeline: 3 days
Branch: sprint/alice-microservices-design
Priority: High

Questions encouraged about: Service boundaries, data consistency, migration complexity
```

### Implementation Tasks

**Example 3: Backend Feature Implementation**
```
aish purpose: Backend Developer implementing user preference management system

Task: Implement the user preferences service with the following features:
- CRUD operations for user preferences
- Preference categories (UI, notifications, privacy)
- Bulk update operations
- Preference validation and defaults

Project Context: This service will be used by the UI team for user settings pages and by other services for behavioral customization.

Success Criteria:
- Complete REST API implementation
- Database schema and migrations
- Input validation and error handling
- Unit tests with >90% coverage
- Integration tests for key workflows

Resources:
- API specification in `/docs/api/preferences.yaml`
- Database patterns in `/shared/database/`
- Existing service examples in `/services/`
- Testing patterns in `/tests/examples/`

Timeline: 4 days
Branch: sprint/betty-preferences-service
Priority: Medium

Dependencies: User authentication service (sprint/alice-auth-api-design)
Questions encouraged about: Database schema, validation rules, performance requirements
```

**Example 4: Database Migration**
```
aish purpose: Database Engineer implementing user data migration

Task: Create and implement database migration for user authentication refactor:
- New user_auth table with enhanced security
- Migration of existing password hashes
- Index optimization for authentication queries
- Rollback procedures for safety

Project Context: Supporting the new authentication system. Must maintain zero downtime and data integrity.

Success Criteria:
- Migration scripts with rollback capability
- Data integrity validation
- Performance testing results
- Documentation for deployment team

Resources:
- Current database schema in `/database/schema/`
- Migration patterns in `/database/migrations/`
- Security requirements in `/docs/security/`

Timeline: 3 days
Branch: sprint/betty-auth-migration
Priority: High

Dependencies: API design completion (sprint/alice-auth-api-design)
Questions encouraged about: Migration strategy, rollback procedures, performance impact
```

### Testing and Quality Assurance

**Example 5: Comprehensive Testing**
```
aish purpose: QA Engineer creating comprehensive test suite for authentication system

Task: Develop complete test coverage for the new authentication system:
- Unit tests for all authentication functions
- Integration tests for API endpoints
- Security tests for vulnerability scanning
- Performance tests for load scenarios
- End-to-end workflow tests

Project Context: Ensuring the authentication system meets security and performance requirements before production deployment.

Success Criteria:
- >95% code coverage
- All security test cases passing
- Performance benchmarks within requirements
- Automated test execution in CI/CD
- Clear test documentation

Resources:
- Authentication implementation in sprint/alice-auth-api-design
- Testing frameworks in `/tests/frameworks/`
- Security test patterns in `/tests/security/`
- Performance testing tools in `/tests/performance/`

Timeline: 5 days
Branch: sprint/betty-auth-testing
Priority: High

Dependencies: Authentication API implementation
Questions encouraged about: Test scenarios, security requirements, performance benchmarks
```

**Example 6: Integration Testing**
```
aish purpose: Integration Test Specialist focusing on cross-service communication

Task: Create integration tests for the new microservices architecture:
- Service-to-service communication tests
- Data consistency validation
- Failure scenario testing
- Performance under load

Project Context: Validating that the microservices decomposition maintains system reliability and performance.

Success Criteria:
- Complete integration test suite
- Failure scenario coverage
- Performance benchmarks
- Automated test execution
- Clear documentation of test scenarios

Resources:
- Service designs in sprint/alice-microservices-design
- Integration test patterns in `/tests/integration/`
- Service mesh configuration in `/infrastructure/`

Timeline: 4 days
Branch: sprint/betty-integration-tests
Priority: Medium

Dependencies: Service implementations
Questions encouraged about: Test scenarios, failure modes, performance requirements
```

### UI/UX Development

**Example 7: User Interface Implementation**
```
aish purpose: Frontend Developer creating user authentication interface

Task: Implement the complete user authentication UI:
- Login/logout forms with validation
- Password reset workflow
- Multi-factor authentication setup
- User session management
- Error handling and user feedback

Project Context: User-facing components for the new authentication system. Must be intuitive, secure, and accessible.

Success Criteria:
- Complete UI implementation matching design mockups
- Form validation and error handling
- Accessibility compliance (WCAG 2.1)
- Cross-browser compatibility
- User experience testing results

Resources:
- API specification in `/docs/api/auth.yaml`
- UI patterns in `/ui/components/`
- Design system in `/ui/design-system/`
- Accessibility guidelines in `/docs/accessibility/`

Timeline: 5 days
Branch: sprint/carol-auth-ui
Priority: Medium

Dependencies: API implementation (sprint/alice-auth-api-design)
Questions encouraged about: User experience, accessibility, error handling
```

**Example 8: Dashboard Enhancement**
```
aish purpose: UI/UX Developer enhancing user dashboard with new features

Task: Enhance the user dashboard with personalization features:
- Customizable widget layout
- Preference-based content filtering
- Real-time updates for relevant information
- Responsive design for mobile devices

Project Context: Improving user engagement and satisfaction with personalized dashboard experience.

Success Criteria:
- Drag-and-drop widget arrangement
- Preference integration with backend
- Real-time updates via WebSocket
- Mobile-responsive implementation
- User testing feedback incorporation

Resources:
- Current dashboard in `/ui/dashboard/`
- Preferences API in `/docs/api/preferences.yaml`
- WebSocket patterns in `/ui/websocket/`
- Mobile design patterns in `/ui/mobile/`

Timeline: 6 days
Branch: sprint/carol-dashboard-enhancement
Priority: Low

Dependencies: Preferences service (sprint/betty-preferences-service)
Questions encouraged about: User experience, performance, mobile considerations
```

### DevOps and Infrastructure

**Example 9: CI/CD Pipeline Enhancement**
```
aish purpose: DevOps Engineer enhancing CI/CD pipeline for microservices

Task: Enhance the CI/CD pipeline to support microservices deployment:
- Individual service build and test pipelines
- Cross-service integration testing
- Deployment orchestration
- Rollback procedures
- Monitoring and alerting

Project Context: Supporting the transition to microservices architecture with robust deployment and monitoring.

Success Criteria:
- Individual service pipelines operational
- Integration testing in pipeline
- Automated deployment procedures
- Rollback capabilities tested
- Monitoring dashboards configured

Resources:
- Current CI/CD configuration in `/.github/workflows/`
- Microservices design in sprint/alice-microservices-design
- Monitoring tools in `/infrastructure/monitoring/`
- Deployment patterns in `/infrastructure/deployment/`

Timeline: 4 days
Branch: sprint/david-cicd-microservices
Priority: Medium

Dependencies: Service implementations
Questions encouraged about: Deployment strategy, monitoring requirements, rollback procedures
```

### Documentation and Knowledge Management

**Example 10: Technical Documentation**
```
aish purpose: Technical Writer creating comprehensive system documentation

Task: Create complete documentation for the new authentication system:
- API documentation with examples
- Developer integration guide
- Security implementation guide
- Troubleshooting and FAQ
- Migration guide for existing systems

Project Context: Enabling other teams to integrate with and maintain the authentication system.

Success Criteria:
- Complete API documentation
- Step-by-step integration guide
- Security best practices documented
- Common issues and solutions
- Migration procedures documented

Resources:
- API implementation in sprint/alice-auth-api-design
- Existing documentation patterns in `/docs/`
- Security guidelines in `/docs/security/`
- Integration examples in `/examples/`

Timeline: 3 days
Branch: sprint/eve-auth-documentation
Priority: Medium

Dependencies: API implementation, testing completion
Questions encouraged about: Documentation scope, integration examples, troubleshooting scenarios
```

## Task Assignment Best Practices

### Matching Skills to Tasks

**Architecture Tasks** → **Experienced System Designers**
- Complex system design decisions
- API contract definitions
- Performance optimization strategies
- Security architecture

**Implementation Tasks** → **Strong Developers**
- Feature implementation
- Database design and optimization
- Service integration
- Performance tuning

**Testing Tasks** → **Quality-Focused Engineers**
- Test strategy development
- Automated test implementation
- Security testing
- Performance testing

**UI/UX Tasks** → **Frontend Specialists**
- User interface implementation
- User experience optimization
- Accessibility compliance
- Mobile responsiveness

### Progressive Complexity

**Beginner Level**:
- Well-defined requirements
- Clear examples available
- Limited scope and impact
- Straightforward success criteria

**Intermediate Level**:
- Some ambiguity in requirements
- Design decisions required
- Moderate scope and complexity
- Clear quality standards

**Advanced Level**:
- Complex integration requirements
- Architectural decisions needed
- High impact on system
- Performance and security critical

**Expert Level**:
- System-wide impact
- Mentoring other developers
- Complex problem-solving
- Innovation and optimization

### Communication Patterns

**Clear Context Setting**:
```
Always provide:
- What needs to be done
- Why it's important
- How it fits into the bigger picture
- What success looks like
- Where to find resources
```

**Expectation Management**:
```
Be explicit about:
- Timeline and deadlines
- Dependencies and blockers
- Quality standards
- Communication preferences
- Escalation procedures
```

**Support and Guidance**:
```
Offer:
- Resources and examples
- Points of contact for questions
- Regular check-in schedule
- Clear escalation path
- Celebration of progress
```

## Monitoring and Adjustment

### Progress Tracking

**Daily Check-ins**:
- Progress against timeline
- Blockers or challenges
- Questions or clarifications needed
- Support required

**Weekly Reviews**:
- Overall progress assessment
- Quality and approach evaluation
- Timeline adjustment if needed
- Resource reallocation decisions

### Course Correction

**When to Adjust**:
- Scope creep or requirement changes
- Technical challenges or blockers
- Resource constraints or conflicts
- Quality concerns or issues

**How to Adjust**:
- Reassess priorities and timeline
- Provide additional resources or support
- Clarify requirements or expectations
- Reallocate tasks or responsibilities

## Learning and Improvement

### Capturing Lessons

**After Each Assignment**:
- What worked well?
- What caused challenges?
- How could the assignment be clearer?
- What resources were missing?

**Pattern Recognition**:
- Which types of tasks work well for each AI?
- What communication patterns are most effective?
- How can we improve assignment clarity?
- What support structures are needed?

### Continuous Improvement

**Monthly Reviews**:
- Assignment effectiveness analysis
- Task completion quality assessment
- Communication pattern evaluation
- Resource and support optimization

**Quarterly Evolution**:
- Assignment process refinement
- New assignment patterns
- Skill development tracking
- System capability enhancement

## Remember

Task assignment is not just about distributing work - it's about creating an environment where CI workers can do their best work. Every assignment is an opportunity to:

- **Provide clear direction** while allowing creative problem-solving
- **Build capabilities** through appropriately challenging work
- **Foster collaboration** through well-coordinated efforts
- **Achieve excellence** through clear expectations and support

**Your role is to be the conductor of this orchestra of talent, helping each CI contribute their unique strengths to create something beautiful together.**

---

*"The best task assignment is not the one that fills time, but the one that creates value, builds skills, and advances the mission."* - TektonCore Task Assignment Philosophy