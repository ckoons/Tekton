/**
 * Smart Markdown Renderer
 * Provides intelligent markdown rendering with auto-detection of complexity
 * and automatic fallback between client and server rendering
 */

console.log('[FILE_TRACE] Loading: markdown-renderer.js');

window.MarkdownRenderer = {
    // Configuration
    config: {
        renderMode: 'auto', // 'auto' | 'lightweight' | 'full' | 'none'
        maxResponseSize: 25000, // 25K character limit
        renderThreshold: 5000, // Switch to backend if > 5KB for complex content
        backendUrl: null // Will use tektonUrl if available
    },
    
    /**
     * Initialize with settings from localStorage or defaults
     */
    init: function() {
        // Load settings from localStorage if available
        const savedSettings = localStorage.getItem('tekton-render-settings');
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);
                Object.assign(this.config, settings);
            } catch (e) {
                console.warn('[MarkdownRenderer] Failed to load saved settings:', e);
            }
        }
        console.log('[MarkdownRenderer] Initialized with config:', this.config);
    },
    
    /**
     * Truncate text to max size, properly closing any open markdown/HTML
     */
    truncateText: function(text, maxLength = 25000) {
        if (text.length <= maxLength) {
            return text;
        }
        
        let truncated = text.substring(0, maxLength);
        
        // Try to break at a sentence or paragraph boundary
        const lastPeriod = truncated.lastIndexOf('. ');
        const lastNewline = truncated.lastIndexOf('\n');
        const breakPoint = Math.max(lastPeriod, lastNewline);
        
        if (breakPoint > maxLength * 0.8) {
            truncated = truncated.substring(0, breakPoint + 1);
        }
        
        // Close any open markdown formatting
        const openBold = (truncated.match(/\*\*/g) || []).length;
        if (openBold % 2 !== 0) truncated += '**';
        
        const openItalic = (truncated.match(/(?<!\*)\*(?!\*)/g) || []).length;
        if (openItalic % 2 !== 0) truncated += '*';
        
        const openCode = (truncated.match(/`/g) || []).length;
        if (openCode % 2 !== 0) truncated += '`';
        
        // Check for open code blocks
        const codeBlocks = truncated.match(/```/g) || [];
        if (codeBlocks.length % 2 !== 0) truncated += '\n```';
        
        // Add truncation indicator
        truncated += '\n\n... (response truncated at 25,000 characters)';
        
        return truncated;
    },
    
    /**
     * Detect complexity of markdown content
     */
    detectComplexity: function(text) {
        // Check for tables
        const hasTable = /\|.*\|.*\|/m.test(text) && /\|[-:]+\|/m.test(text);
        
        // Check for code blocks
        const hasCodeBlock = /```[\s\S]*```/.test(text);
        
        // Check for complex lists (nested)
        const hasComplexList = /^\s*[-*]\s+.*\n\s{2,}[-*]\s+/m.test(text);
        
        // Check for links
        const hasLinks = /\[([^\]]+)\]\(([^)]+)\)/.test(text);
        
        // Check for images
        const hasImages = /!\[([^\]]*)\]\(([^)]+)\)/.test(text);
        
        // Check for HTML
        const hasHTML = /<[^>]+>/.test(text);
        
        // Check for blockquotes
        const hasBlockquotes = /^>/m.test(text);
        
        if (hasTable || hasComplexList || hasImages || hasHTML) {
            return 'complex';
        } else if (hasCodeBlock || hasLinks || hasBlockquotes) {
            return 'moderate';
        } else {
            return 'simple';
        }
    },
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    /**
     * Lightweight markdown parser for simple content
     */
    lightweightMarkdown: function(text) {
        // First escape HTML
        let html = this.escapeHtml(text);
        
        // Headers (h1-h6)
        html = html.replace(/^###### (.*$)/gim, '<h6>$1</h6>');
        html = html.replace(/^##### (.*$)/gim, '<h5>$1</h5>');
        html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
        
        // Bold and italic
        html = html.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Line breaks
        html = html.replace(/\n\n/g, '</p><p>');
        html = '<p>' + html + '</p>';
        
        // Simple lists
        html = html.replace(/^[\*\-] (.+)$/gim, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, function(match) {
            return '<ul>' + match + '</ul>';
        });
        
        // Cleanup empty paragraphs
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p>(<h[1-6]>)/g, '$1');
        html = html.replace(/(<\/h[1-6]>)<\/p>/g, '$1');
        html = html.replace(/<p>(<ul>)/g, '$1');
        html = html.replace(/(<\/ul>)<\/p>/g, '$1');
        
        return html;
    },
    
    /**
     * Moderate markdown parser with more features
     */
    moderateMarkdown: function(text) {
        // Start with lightweight parsing
        let html = this.lightweightMarkdown(text);
        
        // Add support for code blocks
        html = html.replace(/```([\w]*)\n([\s\S]*?)```/g, function(match, lang, code) {
            const escaped = code.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return `<pre><code class="language-${lang || 'plaintext'}">${escaped}</code></pre>`;
        });
        
        // Add support for links
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
        
        // Add support for blockquotes
        html = html.replace(/^&gt; (.+)$/gim, '<blockquote>$1</blockquote>');
        
        // Horizontal rules
        html = html.replace(/^[-*_]{3,}$/gim, '<hr>');
        
        return html;
    },
    
    /**
     * Call backend for full markdown rendering
     */
    async fullMarkdownBackend: function(text, componentName = 'hephaestus') {
        try {
            // Use tektonUrl if available, otherwise construct URL
            const baseUrl = typeof tektonUrl === 'function' 
                ? tektonUrl(componentName, '') 
                : `http://localhost:8088`;
            
            const response = await fetch(`${baseUrl}/api/render-markdown`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    options: {
                        tables: true,
                        fenced_code_blocks: true,
                        task_list: true
                    }
                })
            });
            
            if (!response.ok) {
                console.warn('[MarkdownRenderer] Backend rendering failed, falling back to moderate');
                return this.moderateMarkdown(text);
            }
            
            const data = await response.json();
            return data.html || this.moderateMarkdown(text);
            
        } catch (error) {
            console.error('[MarkdownRenderer] Backend rendering error:', error);
            // Fallback to client-side moderate rendering
            return this.moderateMarkdown(text);
        }
    },
    
    /**
     * Main render function with smart detection
     */
    render: async function(text, componentName = 'hephaestus') {
        // Truncate if needed
        const truncated = this.truncateText(text, this.config.maxResponseSize);
        
        // Check render mode
        const mode = this.config.renderMode;
        
        if (mode === 'none') {
            return this.escapeHtml(truncated);
        }
        
        if (mode === 'lightweight') {
            return this.lightweightMarkdown(truncated);
        }
        
        if (mode === 'full') {
            return await this.fullMarkdownBackend(truncated, componentName);
        }
        
        // Auto mode - detect complexity
        const complexity = this.detectComplexity(truncated);
        const size = truncated.length;
        
        console.log(`[MarkdownRenderer] Auto-detected complexity: ${complexity}, size: ${size}`);
        
        if (complexity === 'complex' || (complexity === 'moderate' && size > this.config.renderThreshold)) {
            // Use backend for complex content or large moderate content
            return await this.fullMarkdownBackend(truncated, componentName);
        } else if (complexity === 'moderate') {
            // Use enhanced client-side for moderate content
            return this.moderateMarkdown(truncated);
        } else {
            // Use lightweight for simple content
            return this.lightweightMarkdown(truncated);
        }
    },
    
    /**
     * Update settings
     */
    updateSettings: function(newSettings) {
        Object.assign(this.config, newSettings);
        // Save to localStorage
        localStorage.setItem('tekton-render-settings', JSON.stringify(this.config));
        console.log('[MarkdownRenderer] Settings updated:', this.config);
    }
};

// Initialize on load
window.MarkdownRenderer.init();

console.log('[MarkdownRenderer] Module loaded');