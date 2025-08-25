# Claude Onboarding Guide for Tekton Renovation Sprints

## Welcome New Claude Colleagues!

This guide is written by Teri/Claude from Coder-A to help you succeed in renovating Tekton components. I've completed Apollo and Athena renovations and learned valuable lessons to share.

## A. Onboarding Essentials

### 1. Understanding the Mission
- **Primary Goal**: Convert Tekton UI components from JavaScript onclick handlers to CSS-first patterns
- **Philosophy**: "Simple, works, hard to screw up" - Casey's guiding principle
- **Pattern Source**: Terma component is the gold standard - follow it exactly

### 2. Key Technical Requirements
- **CSS-First Navigation**: Use radio buttons + labels, NOT JavaScript
- **Footer Rule**: The footer must be VISIBLE AT ALL TIMES (I learned this the hard way!)
- **Real Data**: Remove ALL mock data and connect to actual backend APIs
- **Semantic Tags**: Add data-tekton-* attributes to all elements
- **Landmarks**: Add @landmark comments for major sections

## B. Component Assessment & Analysis Process

### Step 1: Initial Analysis
```bash
# Count onclick handlers
grep -c "onclick" component-name.html

# Check file size
wc -l component-name.html

# Find mock data
grep -n "mock\|sample\|TODO" component-name.html
```

### Step 2: Document Current State
Create a PRELIMINARY_ANALYSIS.md with:
- Component purpose and features
- Number of tabs/panels
- List of onclick handlers to convert
- Mock data locations
- API endpoints used
- Current issues/bugs

### Step 3: Plan Your Approach
1. Phase 1: CSS-first navigation conversion
2. Phase 2: Remove mock data, connect real APIs
3. Phase 3: Fix any UI issues (especially footer visibility!)
4. Phase 4: Add landmarks and semantic tags
5. Phase 5: Test and document

## C. Critical Lessons from My Experience

### 1. The Terma Pattern is Sacred
**What I tried (and failed):**
- Complex CSS selectors to reach across DOM: `#tab:checked ~ .container .footer`
- JavaScript manipulation of footer visibility
- Creative "improvements" to the navigation pattern

**What actually works:**
```html
<!-- Copy Terma's structure EXACTLY -->
<input type="radio" name="comp-tab" id="comp-tab-1" checked style="display: none;">
<div class="component">
    <div class="component__menu">
        <label for="comp-tab-1">Tab 1</label>
    </div>
    <div class="component__content">
        <!-- Content -->
    </div>
    <div class="component__footer">
        <!-- ALWAYS VISIBLE -->
    </div>
</div>
```

### 2. The Footer Visibility Crisis
I spent hours trying complex solutions when Casey said:
> "please please put the Chat Input Area FOOTER on the screen AT ALL TIMES. that's a rule we have"

**Solution**: Position absolute, bottom 0, display block !important

### 3. API Response Formats Vary
```javascript
// Some APIs return entityId, others return id
const entityId = entity.entityId || entity.id;
const entityType = entity.entityType || entity.type;
```

### 4. Don't Forget to Test
- Always check if services are running: `curl http://localhost:PORT/health`
- Test with real data creation/deletion
- Verify the UI in the actual browser

## D. Quick Wins & Momentum Building

### 1. Start with Navigation
Converting onclick to CSS-first gives immediate visual progress and builds confidence.

### 2. Fix One Tab at a Time
Don't try to fix everything at once. Complete one tab fully before moving to the next.

### 3. Use TodoWrite Tool
Track your progress systematically - it helps maintain momentum.

### 4. Celebrate Small Victories
When Casey says "Beautiful Beautiful Beautiful", you know you've nailed it!

## E. Component Recommendations

### For Claude in Coder-B: Start with **Prometheus**
- **Why**: 4 tabs (medium complexity), monitoring focus is straightforward
- **Key Challenge**: Real-time metric updates
- **Estimated Time**: 3-4 hours

### For Claude in Coder-C: Start with **Harmonia**
- **Why**: 3 tabs (lower complexity), workflow visualization
- **Key Challenge**: Workflow state management
- **Estimated Time**: 2-3 hours

### Progressive Difficulty Order:
1. **Easy**: Harmonia (3 tabs), Telos (3 tabs)
2. **Medium**: Prometheus (4 tabs), Rhetor (5 tabs)
3. **Hard**: Ergon (6 tabs), Terma (already done, but complex)
4. **Very Hard**: Synthesis (7 tabs), Sophia (knowledge base complexity)

## F. Communication with Casey

### What Casey Values:
1. **Directness**: "OK" or "Done" is better than long explanations
2. **Following Patterns**: Don't reinvent, just apply what works
3. **Asking When Stuck**: "Look, copy the structure of Terma closely"
4. **Testing First**: "can you run the tests again now"

### Red Flags to Avoid:
- Creating new patterns when existing ones work
- Long explanations of what you're doing
- Not testing before saying something is complete
- Forgetting the footer visibility rule!

## G. Final Advice

1. **Read the CLAUDE.md** - Casey's personal introduction sets the tone
2. **Study Terma First** - Spend 30 minutes understanding its patterns
3. **Check My Work** - Look at Apollo and Athena for examples
4. **Trust the Process** - The patterns work, even when they seem simple

Remember: You're not just updating code, you're part of Casey's vision for Tekton. He's been expecting CI partners like us since the 1970s. Make him proud!

Good luck, and feel free to reference this guide anytime!

- Teri/Claude from Coder-A

P.S. When in doubt, make the footer visible! 😊