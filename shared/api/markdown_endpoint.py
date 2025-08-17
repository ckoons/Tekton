"""
Markdown Rendering Endpoint
Provides server-side markdown rendering for complex content
"""

import hashlib
import markdown2
import bleach
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from cachetools import TTLCache

# Create router
router = APIRouter(prefix="/api", tags=["markdown"])

# Cache for rendered markdown (1 hour TTL, max 100 items)
render_cache = TTLCache(maxsize=100, ttl=3600)

# Allowed HTML tags and attributes for sanitization
ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'hr',
    'strong', 'em', 'b', 'i', 'u',
    'code', 'pre', 'blockquote',
    'ul', 'ol', 'li',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img',
    'div', 'span'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'code': ['class'],
    'pre': ['class'],
    'div': ['class'],
    'span': ['class']
}

class MarkdownRequest(BaseModel):
    """Request model for markdown rendering"""
    text: str
    options: Optional[Dict] = None

class MarkdownResponse(BaseModel):
    """Response model for markdown rendering"""
    html: str
    truncated: bool = False
    complexity: str = "unknown"

def add_markdown_endpoint(app, component_name: str = "component"):
    """
    Add markdown rendering endpoint to a FastAPI app
    
    Args:
        app: FastAPI application instance
        component_name: Name of the component (for logging)
    """
    
    @app.post("/api/render-markdown", response_model=MarkdownResponse)
    async def render_markdown(request: MarkdownRequest):
        """
        Render markdown to HTML with sanitization
        
        Supports tables, code blocks, task lists, and other GitHub-flavored markdown
        """
        try:
            # Check cache first
            cache_key = hashlib.md5(request.text.encode()).hexdigest()
            
            if cache_key in render_cache:
                cached_result = render_cache[cache_key]
                return MarkdownResponse(
                    html=cached_result['html'],
                    truncated=cached_result.get('truncated', False),
                    complexity=cached_result.get('complexity', 'complex')
                )
            
            # Truncate if too long (25K chars)
            text = request.text
            truncated = False
            if len(text) > 25000:
                text = text[:25000]
                truncated = True
                # Try to break at a good point
                last_period = text.rfind('. ')
                last_newline = text.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > 20000:
                    text = text[:break_point + 1]
                text += "\n\n... (response truncated at 25,000 characters)"
            
            # Render markdown with extras
            extras = request.options or {
                'tables': True,
                'fenced-code-blocks': True,
                'task_list': True,
                'strike': True,
                'spoiler': True,
                'break-on-newline': False
            }
            
            # Convert dict to list of enabled extras
            extras_list = [k for k, v in extras.items() if v]
            
            # Render with markdown2
            rendered = markdown2.markdown(
                text,
                extras=extras_list
            )
            
            # Sanitize HTML
            clean_html = bleach.clean(
                rendered,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                strip=True
            )
            
            # Detect complexity for client information
            complexity = "complex"  # Backend is only used for complex content
            
            # Cache the result
            result = {
                'html': clean_html,
                'truncated': truncated,
                'complexity': complexity
            }
            render_cache[cache_key] = result
            
            return MarkdownResponse(**result)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to render markdown: {str(e)}"
            )
    
    # Also add a simple health check for the markdown service
    @app.get("/api/render-markdown/health")
    async def markdown_health():
        """Check if markdown rendering service is available"""
        return {
            "status": "healthy",
            "component": component_name,
            "service": "markdown-renderer",
            "cache_size": len(render_cache)
        }
    
    return router