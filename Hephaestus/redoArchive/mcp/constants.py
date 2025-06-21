"""
UI DevTools Constants and Configuration

Contains all constants, component definitions, and custom exceptions
used by the UI DevTools MCP system.
"""

# Import configuration properly
from shared.utils.global_config import GlobalConfig

# The MAIN UI is always Hephaestus at port 8080
global_config = GlobalConfig.get_instance()
HEPHAESTUS_PORT = global_config.config.hephaestus.port
HEPHAESTUS_URL = f"http://localhost:{HEPHAESTUS_PORT}"

# Component areas within Hephaestus UI
UI_COMPONENTS = {
    "hephaestus": {
        "description": "Main Hephaestus UI container",
        "selectors": ["body", "#app", ".main-container"]
    },
    "rhetor": {
        "description": "Rhetor LLM component area",
        "selectors": ["#rhetor-component", ".rhetor-content", "[data-component='rhetor']"]
    },
    "hermes": {
        "description": "Hermes messaging component area", 
        "selectors": ["#hermes-component", ".hermes-content", "[data-component='hermes']"]
    },
    "athena": {
        "description": "Athena knowledge component area",
        "selectors": ["#athena-component", ".athena-content", "[data-component='athena']"]
    },
    "engram": {
        "description": "Engram memory component area",
        "selectors": ["#engram-component", ".engram-content", "[data-component='engram']"]
    },
    "apollo": {
        "description": "Apollo prediction component area",
        "selectors": ["#apollo-component", ".apollo-content", "[data-component='apollo']"]
    },
    "prometheus": {
        "description": "Prometheus planning component area",
        "selectors": ["#prometheus-component", ".prometheus-content", "[data-component='prometheus']"]
    },
    "ergon": {
        "description": "Ergon agents component area",
        "selectors": ["#ergon-component", ".ergon-content", "[data-component='ergon']"]
    },
    "metis": {
        "description": "Metis workflow component area",
        "selectors": ["#metis-component", ".metis-content", "[data-component='metis']"]
    },
    "navigation": {
        "description": "Main navigation area",
        "selectors": ["#left-nav", ".navigation", "nav", ".sidebar"]
    },
    "content": {
        "description": "Main content area",
        "selectors": ["#center-content", ".content-area", "main", ".main-content"]
    },
    "panel": {
        "description": "Right panel area",
        "selectors": ["#right-panel", ".panel-right", ".sidebar-right"]
    },
    "footer": {
        "description": "Footer area",
        "selectors": ["#footer", ".footer", "footer", ".bottom-bar"]
    }
}

# Dangerous patterns to detect and prevent
DANGEROUS_PATTERNS = {
    "frameworks": [
        r"import\s+React",
        r"import\s+\{.*\}\s+from\s+['\"](react|vue|angular)",
        r"Vue\.(component|createApp)",
        r"angular\.(module|component)",
        r"webpack",
        r"babel",
        r"npm\s+install.*react",
        r"yarn\s+add.*vue",
        r"<script.*src=.*react",
        r"<script.*src=.*vue"
    ],
    "build_tools": [
        r"webpack\.config",
        r"rollup\.config",
        r"vite\.config",
        r"parcel",
        r"esbuild"
    ],
    "complex_patterns": [
        r"class\s+\w+\s+extends\s+(React\.)?Component",
        r"function\s+\w+\s*\(\s*props\s*\)",
        r"const\s+\[\s*\w+\s*,\s*set\w+\s*\]\s*=\s*useState"
    ]
}


# Custom Exceptions
class UIToolsError(Exception):
    """Base exception for UI tools"""
    pass


class ComponentNotFoundError(UIToolsError):
    """Raised when a component area cannot be found"""
    pass


class FrameworkDetectedError(UIToolsError):
    """Raised when a framework is detected in changes"""
    pass