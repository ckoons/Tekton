# Tekton UI Update Sprint - Handoff Document

## Current Status: Phase 2 - Engram UI Update (Starting Fresh)

### Completed Work

#### Phase 1: Hermes UI Update ✅
- Successfully updated Hermes UI from 6 tabs to 4 tabs
- Implemented card-based displays for all views
- Fixed component registration issues (all 17 components now register correctly)
- Fixed hardcoded port issues throughout the codebase (changed from 8001 to 8101)
- All Hermes functionality tested and working

### Next Phase: Engram UI Update

#### Context for New Claude
You are starting fresh on the Engram UI update. The previous attempt has been reverted, so you have a clean slate to work with.

#### Requirements for Engram UI

**Core Requirements:**
1. Rebuild Engram UI with exactly 6 tabs:
   - Browse (for browsing existing memories)
   - Create (for creating new memories with file support)
   - Search (for searching memories)
   - Insights (with emotional analysis)
   - Memory Chat (chat with memory-aware AI)
   - Team Chat (team collaboration)

2. **Technical Constraints:**
   - CSS-first approach using radio buttons for navigation
   - NO DOM manipulation in JavaScript
   - Simple HTML injection pattern
   - BEM naming convention for CSS classes

3. **Features to Implement:**
   - File upload support for .txt, .md, .json files
   - Sharing options: private, shared (no "shared with specific users" option)
   - Emotional analysis showing: joy, frustration, confusion, insight
   - Card-based display similar to Terma for browse view
   - Integration with backend APIs for all operations

4. **Button Styling:**
   - Clear button should be green (#4CAF50)
   - Save button should be blue (#2196F3)
   - Clear button should be on the left, Save button on the right

5. **Insights System:**
   - Read insights configuration from `.tekton/engram/insights.md`
   - Each line in the file defines an insight with keywords
   - Format: `insight_name keyword1 keyword2 keyword3...`
   - Create cards for each insight showing matching memory counts

#### Important Notes:
- The Engram component is located at `/Hephaestus/ui/components/engram/`
- Backend API server is at `/Engram/engram/api/server.py`
- Component should register with Hermes on port 8101
- Follow the established Tekton patterns seen in other components

#### Files to Focus On:
- `/Hephaestus/ui/components/engram/engram-component.html` - Main UI file
- `/Hephaestus/ui/styles/engram/engram-component.css` - Styles (if separate)
- `/Engram/engram/api/server.py` - Backend API endpoints
- `/.tekton/engram/insights.md` - Insights configuration

#### Testing Checklist:
- [ ] All 6 tabs display correctly
- [ ] Browse tab loads and displays memories
- [ ] Create tab saves memories successfully
- [ ] File upload works for .txt, .md, .json
- [ ] Search functionality returns results
- [ ] Insights tab shows statistics and emotional analysis
- [ ] Both chat tabs show input field and send messages
- [ ] Component registers with Hermes
- [ ] All API endpoints respond correctly

### Additional Context:
- Casey prefers the term "Companion Intelligence (CI)" over "AI"
- The user values simple, working solutions that are "Hard to Screw Up"
- Focus on CSS-first navigation without JavaScript DOM manipulation
- Ensure all UI elements properly communicate with the backend

Good luck with the Engram UI update!