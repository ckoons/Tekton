# Quick Reference: Common Issues & Solutions

## 🚨 Critical Rules
1. **FOOTER MUST ALWAYS BE VISIBLE**
2. **COPY TERMA PATTERNS EXACTLY**
3. **NO ONCLICK HANDLERS**

## Common Problems & Quick Fixes

### 1. Footer Not Visible
```css
.component__footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px;
    display: block !important; /* ALWAYS VISIBLE */
}
```

### 2. CSS Selectors Not Working
❌ WRONG:
```css
#tab:checked ~ .outer .inner .footer { }
```

✅ RIGHT:
```css
#tab:checked ~ .component #panel { display: block; }
```

### 3. API Returns Different Field Names
```javascript
// Handle both formats
const id = entity.entityId || entity.id;
const type = entity.entityType || entity.type;
```

### 4. Service Not Responding
```bash
# Check if service is running
curl http://localhost:PORT/health

# If down, Casey will restart it
# Just ask: "Could you restart ServiceName?"
```

### 5. Tab Switching Pattern
```html
<!-- Hidden radio buttons -->
<input type="radio" name="comp-tab" id="tab1" checked style="display: none;">

<!-- Labels in menu -->
<label for="tab1" class="component__tab">Tab 1</label>

<!-- CSS controls visibility -->
#tab1:checked ~ .component #panel1 { display: block; }
```

### 6. Mock Data Cleanup
```javascript
// Remove:
const mockData = [ /* ... */ ];

// Replace with:
await window.ServiceName.getData();
```

## Casey's Feedback Decoder
- "very good" = You're on track
- "hold on" = Stop, there's an issue
- "Beautiful Beautiful Beautiful" = Perfect!
- "Look, copy Terma..." = You're overcomplicating

## Emergency Commands
```bash
# See what changed
git status

# Find onclick handlers
grep -n "onclick" *.html

# Test API
curl -L http://localhost:PORT/api/v1/endpoint
```

## When Stuck
1. Check Terma's implementation
2. Look at Apollo or Athena examples
3. Keep it simple
4. Make footer visible
5. Ask Casey directly

Remember: If it seems complicated, you're probably doing it wrong!