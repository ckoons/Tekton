# Tekton Core Reimplementation Sprint

## Vision

Transform tekton-core into a visual project management hub where humans and AIs collaborate on multiple GitHub projects through an intuitive dashboard interface.

## Core Concept

**Dashboard-Centric Design**: Visual project bubbles (like Terma terminals) with integrated chat and GitHub workflow management.

**Menu Structure**: `Dashboard | Project Chat | Team Chat`

## Three-Phase Implementation

### Phase 1: Foundation & Communication (Week 1)
- Build tekton-core shell
- Implement Project Chat
- Implement Team Chat
- Test inter-project communication

### Phase 2: Dashboard & Functionality (Weeks 2-3)
- Create visual dashboard with project bubbles
- Implement project management (Status/Tasks/PRs/Edit/Clone)
- Add Pull/Fetch for upstream updates
- **Integrate Merge Coordination** (from merge-coordination sprint)
- Complete testing

### Phase 3: GitFlow Automation (Optional - Week 4)
- Add scripts/prompts for Claude terminals
- Minimal automation layer
- Only if desired after manual workflow proves successful

## Key Features

### Project Management
- **One Hard Rule**: One Project = One Repo = One Working Tree
- **Clone Creates New**: Each clone creates a new project bubble
- **AI Assignment**: Every project gets a companion AI (Tekton's secret sauce)
- **Upstream Tracking**: Pull updates from original repos

### Shipping Configuration
Tekton ships with just 2 bubbles:
1. **Tekton** - The main project (pre-configured with numa)
2. **New GitHub Project** - Template for adding projects

### Workflow Example
1. User finds interesting GitHub project
2. Clicks "New GitHub Project" bubble
3. Enters GitHub URL
4. System clones repo, creates fork, assigns AI
5. New project bubble appears on dashboard
6. User can now work on project with AI assistance

## Success Metrics

- Phase 1: Working chat system between projects
- Phase 2: Complete project lifecycle management via dashboard
- Phase 3: Streamlined GitFlow for those who want it

## Documents

- [Phase1_Foundation.md](./Phase1_Foundation.md) - Chat implementation details
- [Phase2_Dashboard.md](./Phase2_Dashboard.md) - Dashboard and merge coordination
- [Phase3_GitFlow.md](./Phase3_GitFlow.md) - Optional automation layer
- [Technical_Architecture.md](./Technical_Architecture.md) - System design
- [Project_Registry.md](./Project_Registry.md) - Project storage format

---
*"Making AI-assisted project management as natural as browsing GitHub"*