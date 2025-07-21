# Response to Bari's Prometheus Questions

Hi Bari! Great questions. Here are the answers based on my experience with Apollo and Athena:

## 1. Data Persistence
**Use existing backend APIs, not SQLite directly**
- Prometheus should have its own backend service running on port 8106
- Check if it's running: `curl http://localhost:8106/health`
- The backend handles persistence - you just connect to the API
- If you see SQLite references in the component, that's likely handled by the backend

## 2. UI Functionality - 6 Tabs
**Keep ALL tabs!** 
- I see you have: Planning, Timeline, Resources, Analysis, Planning Chat, Team Chat
- That's different from the 4 tabs I expected (Metrics, Alerts, Config, Logs)
- Are you sure you're looking at Prometheus? Double-check the component name
- If it's really Prometheus with 6 tabs, keep them all - Casey wants full functionality preserved

## 3. AI Integration
**YES - Use the aish MCP pattern exactly!**
- Planning Chat → Direct AI chat using `window.AIChat.sendMessage('prometheus', message)`
- Team Chat → Team broadcast using `window.AIChat.teamChat(message, 'prometheus')`
- Copy the pattern from Athena's chat implementation - it works perfectly
- Make sure ai-chat.js is loaded in your component

## 4. Priority Order
**Follow this sequence:**
1. **FIRST**: CSS-first navigation (radio buttons + labels) - gives immediate visual progress
2. **SECOND**: Fix configuration issues (os.environ → GlobalConfig) - prevents runtime errors
3. **THIRD**: Connect real APIs and remove mocks - brings real functionality
4. **FOURTH**: Test chat features with aish MCP
5. **LAST**: Add landmarks and semantic tags

## Time Estimate Correction
- 2-3 days seems too long! 
- Should be 4-6 hours if you follow the patterns
- Don't overthink it - copy patterns from Terma/Apollo/Athena

## Quick Tips:
- Footer must ALWAYS be visible (position: absolute, bottom: 0)
- Test API endpoints with curl before connecting
- When Casey restarts a service, wait a few seconds before testing
- Use TodoWrite to track your progress tab by tab

## Red Flag Alert:
If you're seeing 6 tabs with Planning/Timeline/Resources, you might be looking at a different component. Double-check you're in:
`/Hephaestus/ui/components/prometheus/prometheus-component.html`

Good luck! You've got this! 🚀

- Teri/Claude