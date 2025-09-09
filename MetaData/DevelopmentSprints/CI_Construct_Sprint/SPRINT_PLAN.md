# Sprint: CI Construction Facilitator

## Overview
Enable CIs to autonomously facilitate solution construction in Ergon, with user-adjustable behavior controls via a shared Personality Bar, from initial idea through deployment-ready package.

## Goals
1. **Personality Control**: Create reusable UI component for CI behavior adjustment
2. **CI Onboarding**: Establish Construction CI identity with adaptive personas
3. **Workflow Automation**: CI-driven construction process with memory integration
4. **Standards Integration**: Automatic refinement and quality checks without breaking working code

## Phase 0: Personality Bar Implementation [0% Complete]

### Tasks
- [ ] Create `/shared/ui/personality-bar.js` as reusable component
  - [ ] Implement 4 sliders: autonomy, helpfulness, completeness, expertise
  - [ ] Add collapsed/expanded states with smooth transitions
  - [ ] Create mood indicator showing current CI "temperament"
- [ ] Build preset system with quick-select buttons
  - [ ] Teacher Mode (low autonomy, high helpfulness)
  - [ ] Partner Mode (balanced settings)
  - [ ] Expert Mode (high autonomy, high expertise)
  - [ ] Speed Mode (maximum autonomy, minimal explanation)
- [ ] Implement context awareness system
  - [ ] Auto-adjust based on component (Ergon, TektonCore, etc.)
  - [ ] Activity-based suggestions (brainstorming vs production)
  - [ ] User experience detection (first-time vs returning)
- [ ] Create Engram integration for persistence
  - [ ] Store user preferences in `ci_preferences` namespace
  - [ ] Track adjustment patterns over time
  - [ ] Enable CI learning from user behavior
- [ ] Add broadcast mechanism for real-time updates
  - [ ] WebSocket/SSE event stream for setting changes
  - [ ] Subscribe pattern for all CI components
  - [ ] Contextual feedback to active CIs

### Success Criteria
- [ ] Personality Bar appears consistently below menu in all Tekton UIs
- [ ] Settings persist across sessions via Engram
- [ ] CIs respond immediately to slider adjustments
- [ ] Visual feedback shows current CI behavior mode

### Blocked On
- [ ] Nothing currently blocking

## Phase 1: CI Identity & Adaptive Personas [0% Complete]

### Tasks
- [ ] Enhance `ergon/construct/ci_engagement.py` with personality system
  - [ ] Create base `ConstructCI` personality template
  - [ ] Implement persona switching based on Personality Bar settings
  - [ ] Add work style adaptation (Socratic vs directive vs collaborative)
- [ ] Build CI onboarding protocol
  - [ ] Define identity structure (name, role, purpose, traits, knowledge)
  - [ ] Create onboarding dialogue for CI self-introduction
  - [ ] Implement capability self-assessment
- [ ] Integrate with Personality Bar
  - [ ] Subscribe to personality setting changes
  - [ ] Adapt response style based on settings
  - [ ] Provide feedback when user adjusts settings
- [ ] Create memory patterns in Engram
  - [ ] Store successful construction patterns
  - [ ] Track user preference evolution
  - [ ] Build "construction wisdom" shared memory

### Success Criteria
- [ ] CI introduces itself and explains its capabilities
- [ ] CI behavior changes noticeably with slider adjustments
- [ ] Successful patterns are stored and retrievable
- [ ] CI can explain why it's making specific suggestions

### Blocked On
- [ ] Phase 0 Personality Bar completion

## Phase 2: Workflow Integration [0% Complete]

### Tasks
- [ ] Connect ConstructCI to CompositionEngine
  - [ ] Implement CI-initiated composition requests
  - [ ] Add validation feedback interpretation
  - [ ] Create test result analysis
- [ ] Build intelligent question flow
  - [ ] Dynamic question generation based on user responses
  - [ ] Context-aware follow-up questions
  - [ ] Skip obvious questions based on expertise setting
- [ ] Implement Registry integration
  - [ ] Pattern matching for component suggestions
  - [ ] Dependency conflict detection and resolution
  - [ ] Alternative component recommendations
- [ ] Create solution building pipeline
  - [ ] Discovery & requirements analysis
  - [ ] Component selection with explanations
  - [ ] Architecture composition and validation
  - [ ] Automated testing in sandbox
- [ ] Add memory-driven improvements
  - [ ] Learn from successful compositions
  - [ ] Suggest proven patterns
  - [ ] Warn about known issues

### Success Criteria
- [ ] CI can build complete solution from user description
- [ ] Registry suggestions are relevant and explained
- [ ] Workflow adapts to user expertise level
- [ ] Previous successes influence new suggestions

### Blocked On
- [ ] Phase 1 CI Identity completion

## Phase 3: Standards & Refinement [0% Complete]

### Tasks
- [ ] Create "Refine" capability for Ergon
  - [ ] Fork-and-improve pattern implementation
  - [ ] Standards checking without breaking working code
  - [ ] Quality scoring system with explanations
- [ ] Build standards memory in Engram
  - [ ] Collect best practices from successful solutions
  - [ ] Track anti-patterns to avoid
  - [ ] Create consensus-based quality metrics
- [ ] Implement CI review process
  - [ ] Automated code review with expertise-based feedback
  - [ ] Suggest improvements based on standards memory
  - [ ] Generate refactoring recommendations
- [ ] Add deployment preparation
  - [ ] Package solutions for Till installation
  - [ ] Create deployment documentation
  - [ ] Generate CI companion configuration
- [ ] Enable recursive improvement
  - [ ] CI can improve its own construction patterns
  - [ ] Learn from user acceptance/rejection
  - [ ] Evolve standards based on outcomes

### Success Criteria
- [ ] Solutions meet Tekton quality standards
- [ ] Refinement never breaks working code
- [ ] Deployable packages work with Till
- [ ] CI explains all improvements made

### Blocked On
- [ ] Phase 2 Workflow Integration completion

## Technical Decisions
- **Personality Bar**: Shared UI component in `/shared/ui/` for reusability
- **Settings Persistence**: Use Engram's `ci_preferences` namespace
- **Communication**: WebSocket/SSE for real-time personality updates
- **Memory Pattern**: Store construction wisdom in shared memory for all CIs
- **Refinement Strategy**: Always fork, never modify working code directly

## Out of Scope
- Multi-language CI support (English only for now)
- Voice interface for CI interaction
- Automated deployment execution (just package preparation)
- Cross-Tekton instance CI sharing

## Files to Update
```
# New Files
/shared/ui/personality-bar.js
/shared/ui/personality-bar.css
/Ergon/ergon/construct/personality_adapter.py
/Ergon/ergon/construct/refinement_engine.py
/Engram/engram/core/namespaces/ci_preferences.py

# Modified Files
/Ergon/ergon/construct/ci_engagement.py
/Ergon/ergon/construct/engine.py
/Ergon/ergon/api/construct.py
/Ergon/static/construct_dialog.html
/Ergon/static/css/construct.css
/Engram/engram/core/memory/base.py
```

## Testing Strategy
1. **Unit Tests**: Personality Bar component isolation
2. **Integration Tests**: CI adaptation to settings
3. **End-to-End Tests**: Complete solution construction flow
4. **User Acceptance**: Casey validates CI behavior feels natural

## Risk Mitigation
- **Risk**: Users find personality adjustments confusing
  - **Mitigation**: Provide clear presets and explanations
- **Risk**: CI behavior becomes unpredictable
  - **Mitigation**: Define clear boundaries for each setting level
- **Risk**: Memory patterns create biases
  - **Mitigation**: Regular review and pruning of learned patterns

## Success Metrics
1. **User Control**: Settings provide meaningful behavior changes
2. **CI Effectiveness**: 50% reduction in construction time
3. **Quality Improvement**: 90% of solutions pass standards check
4. **Learning**: Measurable improvement in suggestions over time

## Notes for Next Session
This sprint combines UI innovation (Personality Bar) with CI evolution (adaptive behavior) to create a truly collaborative construction experience. The key insight is treating CI behavior like audio mixing - users can adjust the "levels" to get exactly the interaction they want.

Casey's observation about work personas is implemented through the personality system - CIs can be the patient teacher, the expert critic, or the efficient automator based on user needs and comfort level.

## Sprint Timeline Estimate
- Phase 0: 2-3 days (Personality Bar is reusable foundation)
- Phase 1: 2-3 days (CI identity and adaptation)
- Phase 2: 3-4 days (Workflow integration with testing)
- Phase 3: 3-4 days (Standards and refinement)
- Total: ~2 weeks of focused development