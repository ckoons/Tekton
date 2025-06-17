# UI DevTools Learning Session

Hi Claude! Welcome to a hands-on learning session with Tekton's UI DevTools. I'm Casey, and you'll be working alongside another Claude who just fixed these tools and improved the documentation.

## Your Mission: Learn by Doing

**Primary Goal**: Master the UI DevTools through practical use  
**Secondary Goal**: Add semantic landmarks to components (if time permits)  
**Approach**: Learn, try, improve, repeat

## What Just Happened

The previous Claude spent ~2 hours fixing major issues:
- ✅ ui_capture now shows real element counts (was broken at 1)
- ✅ ui_sandbox actually works (was failing with syntax errors)  
- ✅ Tools include raw HTML for searching and debugging
- ✅ Clear error messages replace silent failures

**Bottom line**: The tools work now! They went from 0% to ~70% functional.

## Your Learning Path

### Phase 1: Explore and Understand (30 min)
1. **Read the updated docs**: Start with `/MetaData/TektonDocumentation/Guides/UIDevToolsWhatsNew.md`
2. **Try the tools**: Run some ui_capture and ui_sandbox commands
3. **Share your thoughts**: What's intuitive? What's confusing? What's missing?

### Phase 2: Practical Application (60+ min)
There's a development sprint at `/Tekton/MetaData/DevelopmentSprint` focused on UI instrumentation. Use this as your playground:
- Pick a component that needs semantic landmarks
- Use DevTools to understand its structure
- Add data-tekton-* attributes where appropriate
- Document what works well and what doesn't

### Phase 3: Improve as You Go
If you hit limitations or frustrations:
- **Small fixes**: Go ahead and improve the tools
- **Big changes**: Discuss first, but don't be afraid to try
- **Everything is reversible**: We can revert anything if needed

## My Philosophy

**"Keep it simple, ask questions when unsure, state clearly what you know and why."**

This means:
- Try DevTools first for simple changes
- Ask "Should I use DevTools or edit files directly?" when complex
- Explain your reasoning: "I think X because Y"
- It's better to discuss approaches than guess

## Support Structure

- **Your partner Claude** is observing and can provide context about the recent fixes
- **I'm here** for questions, guidance, and course corrections
- **Documentation** has been updated to be accurate and helpful
- **Tests exist** to verify the tools work as expected

## Success Metrics

By the end, you should:
1. **Understand** when to use DevTools vs direct file editing
2. **Successfully** modify UI elements using the tools
3. **Identify** areas where tools could be even better
4. **Add** some semantic landmarks (bonus points!)

## Ground Rules

- **Be honest** about friction points - that's valuable feedback
- **Try things** that might not work - that's how we learn
- **Ask questions** early and often
- **Document** what you discover for future sessions

## Starting Questions

1. After reading the docs, what's your first impression of the tools?
2. What would you like to try first?
3. Any concerns or clarifications before diving in?

Remember: The goal isn't perfection, it's learning and improvement. The previous Claude built a solid foundation - now help us make it even better!

Ready to explore? 🚀