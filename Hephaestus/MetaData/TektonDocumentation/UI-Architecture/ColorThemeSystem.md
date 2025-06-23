# Tekton UI Color Theme System

## Overview
The Tekton UI uses a simple, robust theme system based on CSS variables and HTML data attributes. This system allows instant theme switching across the entire application.

## How It Works

### 1. Theme CSS Files
Located in `/ui/styles/themes/`:
- `theme-pure-black.css` - True OLED black theme
- `theme-dark.css` - Dark gray theme  
- `theme-light.css` - Light theme
- `theme-base.css` - Base theme definitions

### 2. CSS Variable Structure
Each theme file defines CSS variables using attribute selectors:

```css
[data-theme-base="pure-black"] {
  --color-bg-base: #000000;
  --color-bg-panel: #0a0a0a;
  --color-bg-card: #141414;
  --color-text-primary: #ffffff;
  --color-text-secondary: #b0b0b0;
  --color-accent: #007bff;
  /* ... etc */
}
```

### 3. Main CSS Usage
The main CSS (`/ui/styles/main.css`) uses these variables:

```css
:root {
  --bg-primary: var(--color-bg-base, #000000);
  --text-primary: var(--color-text-primary, #ffffff);
  /* ... etc */
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}
```

### 4. Theme Switching Mechanism
The Settings component changes themes by setting a single HTML attribute:

```javascript
// This line changes the entire app's theme
document.documentElement.setAttribute('data-theme-base', 'pure-black');
```

When this attribute changes, CSS automatically applies the new theme variables throughout the app.

## Theme Application Flow

1. **User clicks theme button** in Settings
2. **JavaScript sets data-theme-base** attribute on document root
3. **CSS selectors activate** the corresponding theme file variables
4. **Entire app updates** instantly using the new CSS variables

## Key Benefits

- **Simple**: One attribute controls everything
- **Fast**: No complex DOM manipulation or style injection
- **Reliable**: Pure CSS cascading, hard to break
- **Extensible**: New themes just need new CSS files

## Adding New Themes

1. Create new CSS file: `/ui/styles/themes/theme-{name}.css`
2. Define variables with `[data-theme-base="{name}"]` selector
3. Add theme option to Settings component
4. Theme automatically works across entire app

## Debugging Theme Issues

Check in browser DevTools:
1. **Document attribute**: `<html data-theme-base="pure-black">`
2. **CSS variables**: `:root` should show active theme variables
3. **Console logs**: Settings component logs theme changes

## Current Themes

- **pure-black**: True #000000 black for OLED displays
- **dark**: Dark gray (#1a1a1a) theme
- **light**: White background theme

## Accent Colors

Accent colors work the same way using `data-theme-color` attribute:
- blue (#007bff)
- green (#28a745) 
- purple (#6f42c1)
- orange (#fd7e14)