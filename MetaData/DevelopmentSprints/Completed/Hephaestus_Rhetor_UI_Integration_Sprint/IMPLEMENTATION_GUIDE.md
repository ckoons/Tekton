# Hephaestus-Rhetor UI Integration - Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the chat routing functionality to connect Hephaestus UI with Rhetor's AI capabilities.

## Implementation Steps

### Step 1: Add Route Request Models to Rhetor

1. Copy the `RouteRequest.py` file to `/Rhetor/rhetor/api/models/` or add its contents to the existing models in `app.py`.

### Step 2: Add the /chat/route Endpoint to Rhetor

1. Open `/Rhetor/rhetor/api/app.py`
2. After the existing request models (around line 390), add:

```python
class RouteRequest(TektonBaseModel):
    component: str  # Component name or "team"
    message: str
    context_id: str
    user_id: Optional[str] = None

class RouteResponse(TektonBaseModel):
    success: bool
    component: str
    message: str
    speaker: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    participants: Optional[List[str]] = None
```

3. After the existing endpoints (around line 1835), add the chat route endpoint from `chat_route_endpoint.py`.

### Step 3: Update Hephaestus UI

1. Add the chat widget files:
   - `/Hephaestus/ui/components/shared/chat-widget.html`
   - `/Hephaestus/ui/scripts/chat-widget.js`
   - `/Hephaestus/ui/styles/chat-widget.css`

2. Include the chat widget CSS in `/Hephaestus/ui/index.html`:
```html
<link rel="stylesheet" href="styles/chat-widget.css">
```

3. Include the chat widget script:
```html
<script src="scripts/chat-widget.js"></script>
```

### Step 4: Integrate Chat Widget with Components

For each component in Hephaestus, update the component HTML to include the chat widget:

1. Add a container div at the bottom of the component content:
```html
<div id="chat-widget-container"></div>
```

2. Add initialization script:
```javascript
document.addEventListener('DOMContentLoaded', function() {
  fetch('/components/shared/chat-widget.html')
    .then(response => response.text())
    .then(html => {
      document.getElementById('chat-widget-container').innerHTML = html;
      if (window.ChatWidget) {
        window.ChatWidget.init('component-name-here');
      }
    });
});
```

### Step 5: Update Navigation Handler

In `/Hephaestus/ui/scripts/main.js`, update the navigation click handler:

```javascript
navItems.forEach(item => {
  item.addEventListener('click', function() {
    const componentId = this.getAttribute('data-component');
    if (!componentId) return;
    
    // ... existing navigation code ...
    
    // Update chat widget context
    if (window.ChatWidget) {
      window.ChatWidget.init(componentId);
    }
  });
});
```

### Step 6: Configure WebSocket Support

Update `/Hephaestus/ui/scripts/websocket.js` to handle chat responses:

```javascript
websocketManager.messageHandlers.COMPONENT_CHAT_RESPONSE = function(message) {
  const payload = message.payload;
  if (!payload || !window.ChatWidget) return;
  
  window.ChatWidget.hideTyping();
  
  const speaker = payload.component === 'team' ? 
    `Team-${payload.speaker || 'Rhetor'}` : 
    window.ChatWidget.capitalize(payload.component);
  
  window.ChatWidget.addMessage('ai', payload.message, speaker);
};
```

### Step 7: Test the Integration

1. Start Rhetor:
```bash
cd Rhetor
./run_rhetor.sh
```

2. Start Hephaestus:
```bash
cd Hephaestus
python -m http.server 8080
```

3. Open http://localhost:8080 in your browser
4. Navigate to any component
5. Test the chat interface

## Testing Checklist

- [ ] Chat widget appears in right panel footer
- [ ] Placeholder text updates when switching components
- [ ] Messages are sent to Rhetor successfully
- [ ] AI responses appear in the chat
- [ ] Team chat mode works when selected
- [ ] Chat history persists for each component
- [ ] Typing indicator shows during AI response
- [ ] Error messages display appropriately

## Troubleshooting

### Chat not appearing
- Check browser console for JavaScript errors
- Verify chat-widget.html is being loaded
- Ensure ChatWidget is initialized

### Messages not sending
- Check Rhetor is running on port 8003
- Verify CORS is enabled in Rhetor
- Check network tab for failed requests

### No AI responses
- Verify AI specialist manager is initialized in Rhetor
- Check Rhetor logs for errors
- Ensure at least one LLM provider is configured

## Next Steps

After basic integration is working:

1. Add streaming support for real-time responses
2. Implement chat history persistence settings
3. Add team chat moderation features
4. Enhance error handling and reconnection logic