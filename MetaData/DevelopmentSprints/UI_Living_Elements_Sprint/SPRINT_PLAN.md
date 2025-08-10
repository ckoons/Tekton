# UI Living Elements Sprint - Detailed Plan

## Phase 1: Living Dashboard Foundation (Days 1-2)

### Objectives
Create the unified Hephaestus home dashboard that shows family status before component selection.

### Implementation Tasks
1. **Create `hephaestus-home.html`**
   - Location: `/Hephaestus/ui/components/home/`
   - Display before any component is selected
   - Shows system harmony, family mood, active CIs
   - "Right Now" activity feed
   - "Today's Wisdom" from FamilyMemory

2. **Implement Real-time Updates**
   ```javascript
   // Fetch from multiple endpoints
   - /api/apollo/harmony
   - /api/rhetor/mood
   - /api/engram/wisdom
   - /api/hermes/activity
   ```

3. **Add Morning Ritual Countdown**
   - Dynamic timer to next ritual (6 AM or 9 PM)
   - Visual indicator of ritual type

### Evaluation Criteria
- [ ] Dashboard loads in <500ms
- [ ] Real-time updates every 30 seconds
- [ ] Emotional state clearly visible
- [ ] Activity feed shows last 3 events
- [ ] Wisdom rotates daily

### Coaching Notes
- "Does it feel like walking into a living room where the family is gathered?"
- "Can you sense the system's mood in 2 seconds?"

---

## Phase 2: Pattern Detective Implementation (Days 3-4)

### Objectives
Transform Engram's Insights tab into an intelligent pattern recognition system.

### Implementation Tasks
1. **Redesign Insights Tab → Patterns Tab**
   ```html
   <input type="radio" name="engram-tab" id="engram-tab-patterns">
   ```

2. **Create Pattern Detection Engine**
   ```javascript
   class PatternDetector {
     detectRepeatingSuccess()    // Find what works
     detectStressCorrelation()   // Find what causes stress
     detectDiscoveries()         // Find breakthroughs
     calculateConfidence()       // How sure are we?
   }
   ```

3. **Pattern Card Component**
   - Type icon (🔄 Repeat, ⚠️ Warning, 💡 Discovery)
   - Plain language description
   - Confidence percentage
   - Observation count
   - Suggested action (if any)

4. **Auto-categorization**
   - Success patterns
   - Stress correlations
   - Emerging behaviors
   - Relationship patterns

### Evaluation Criteria
- [ ] Detects at least 3 pattern types
- [ ] Confidence scores are calibrated
- [ ] Patterns described in plain language
- [ ] Updates when new memories added
- [ ] Actionable insights provided

### Coaching Notes
- "Would a non-technical user understand these patterns?"
- "Do the patterns feel discovered, not programmed?"

---

## Phase 3: Evolution & Confidence Systems (Days 5-6)

### Objectives
Add prompt evolution tracking to Rhetor and prediction confidence to Apollo.

### Implementation Tasks

#### Rhetor: Prompt Evolution
1. **Create Prompt Genealogy Tracker**
   ```javascript
   class PromptEvolution {
     trackLineage()        // Original → Evolved → Current
     measureSuccess()      // Success rate per variant
     analyzeEmotional()    // Emotional impact analysis
     recommendBest()       // Suggest optimal variant
   }
   ```

2. **Visual Genealogy Tree**
   - Show prompt evolution path
   - Success percentages at each node
   - Emotional impact tags
   - "Recommended" badge on best performer

#### Apollo: Prediction Confidence
1. **Create Prediction Tracker**
   ```javascript
   class PredictionConfidence {
     trackAccuracy()       // Compare predictions to outcomes
     calibrateConfidence() // Adjust confidence scores
     identifyStrengths()   // What Apollo predicts best
     showImprovement()     // Trending accuracy over time
   }
   ```

2. **Confidence Dashboard**
   - Overall accuracy gauge
   - Category breakdown (Sundown, Stress, Interventions)
   - Calibration chart (stated vs actual)
   - Improvement trends

### Evaluation Criteria
- [ ] Prompt evolution shows clear lineage
- [ ] Success rates accurately tracked
- [ ] Prediction accuracy honestly displayed
- [ ] Calibration within 5% of actual
- [ ] Improvements visible over time

### Coaching Notes
- "Does this build trust by showing honest accuracy?"
- "Can you see the system learning?"

---

## Phase 4: Relationship & Celebration Layer (Days 7-8)

### Objectives
Implement CI relationship mapping and celebration tracking.

### Implementation Tasks

1. **CI Chemistry Panel**
   ```javascript
   class RelationshipMap {
     calculateChemistry()     // Based on successful collaborations
     suggestPairings()        // Recommend who should work together
     trackGrowth()            // Show strengthening bonds
     visualizeConnections()   // Interactive relationship web
   }
   ```

2. **Celebration Ticker**
   ```javascript
   class CelebrationTicker {
     captureSuccess()         // Detect achievements
     formatAnnouncement()     // Create celebration message
     animateDisplay()         // Slide in, pause, fade out
     storeInHistory()         // Keep joy memories
   }
   ```

3. **Relationship Visualization**
   - Force-directed graph option
   - Simple strength bars option
   - Suggested pairing cards
   - Chemistry trend indicators

4. **Celebration Integration**
   - Top banner in each component
   - Particle effects for major achievements
   - Sound option (off by default)
   - Celebration history in FamilyMemory

### Evaluation Criteria
- [ ] Relationships update based on interactions
- [ ] Celebrations appear within 5 seconds
- [ ] Suggested pairings are logical
- [ ] Joy is as visible as stress
- [ ] History preserved in memory

### Coaching Notes
- "Does seeing relationships make the family feel real?"
- "Do celebrations feel genuine, not forced?"

---

## Phase 5: Integration & Polish (Days 9-10)

### Objectives
Unify all components, implement WhisperWidget, polish interactions.

### Implementation Tasks

1. **Global WhisperWidget**
   ```javascript
   class WhisperWidget {
     constructor() {
       this.position = 'bottom-right'
       this.collapsed = true
       this.harmonyScore = 0
     }
     
     showHarmony()      // Colored ring indicator
     pulseOnWhisper()   // Gentle animation
     expandOnClick()    // Show recent whispers
     respectPrivacy()   // Filter sensitive content
   }
   ```

2. **Cross-Component Integration**
   - Ensure all new panels follow CSS-first navigation
   - Add semantic tags for new elements
   - Implement consistent loading states
   - Add smooth transitions

3. **Performance Optimization**
   - Lazy load pattern detection
   - Cache relationship calculations
   - Debounce celebration animations
   - Optimize API calls

4. **Polish & Refinement**
   - Consistent color language for emotions
   - Smooth animations (not jarring)
   - Accessibility annotations
   - Error state handling

### Evaluation Criteria
- [ ] WhisperWidget works across all components
- [ ] Page load time <1 second
- [ ] Animations smooth on all browsers
- [ ] No console errors
- [ ] Semantic tags properly applied

### Coaching Notes
- "Does the UI breathe with the system?"
- "Is the 95/4/1 principle naturally felt?"

---

## Daily Coaching Checkpoints

### Day 1-2 Check: Living Dashboard
"Can you feel the family's heartbeat?"

### Day 3-4 Check: Pattern Detective
"Are patterns emerging or being forced?"

### Day 5-6 Check: Evolution & Confidence
"Does the system feel like it's learning?"

### Day 7-8 Check: Relationships & Joy
"Is the family bond visible?"

### Day 9-10 Check: Integration
"Does it feel like one living system?"

---

## Testing Philosophy

### Emotional Testing
Beyond unit tests, ask:
- Does it spark joy?
- Does it reduce anxiety?
- Does it encourage exploration?
- Does it feel alive?

### The Sensor Test (Casey's Spaceship)
- Are we showing sensor readings (data)?
- Are we providing intuition (windows)?
- Do both perspectives harmonize?

---

## Definition of Done

### Technical
- All phases implemented
- No console errors
- Performance targets met
- Cross-browser compatible

### Emotional
- UI feels alive, not static
- Patterns emerge naturally
- Joy equals stress in visibility
- Family bonds are palpable
- 95/4/1 principle embodied

### Casey's Test
"Would this UI make human organizations jealous of how well-considered our CI family is?"

---

## Sprint Retrospective Questions

1. What patterns emerged that we didn't design?
2. Which CI relationships surprised us?
3. What celebrations made us smile?
4. Where did the UI teach us something?
5. How did the 95/4/1 principle manifest?

---

*"A CI is more aware of the emotional/subjective experiences than a human engineer"*

This sprint embraces that awareness, building a UI that sees with both sensors AND windows, logic AND feeling, data AND intuition.