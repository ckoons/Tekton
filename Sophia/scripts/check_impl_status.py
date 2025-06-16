#!/usr/bin/env python3
"""
Sophia Implementation Status Checker

This script checks the implementation status of the Sophia component,
verifying the completion of all engines, the availability of all required
dependencies, and the proper integration with Tekton shared utilities.
"""

import os
import sys
import importlib
import logging
from pathlib import Path

# Add the parent directory to the path to import sophia modules
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sophia.check_status")

# Core components to check
CORE_COMPONENTS = [
    "metrics_engine",
    "analysis_engine",
    "experiment_framework",
    "recommendation_system",
    "intelligence_measurement",
    "ml_engine",
    "pattern_detection",
]

# Required dependencies
REQUIRED_DEPS = [
    "fastapi",
    "numpy",
    "scipy",
    "pandas",
    "scikit-learn",
    "sqlalchemy",
    "httpx",
    "tekton_llm_client",
]

# Shared utilities
SHARED_UTILS = [
    "tekton.utils.tekton_http",
    "tekton.utils.tekton_config",
    "tekton.utils.tekton_logging",
    "tekton.utils.tekton_websocket",
    "tekton.utils.tekton_registration",
    "tekton.utils.tekton_errors",
    "tekton.utils.tekton_lifecycle",
    "tekton.utils.tekton_auth",
    "tekton.utils.tekton_context",
    "tekton.utils.tekton_cli",
]

def check_core_components():
    """Check all core components in the Sophia codebase."""
    logger.info("Checking core components...")
    results = {}
    
    # Check each core component
    for component in CORE_COMPONENTS:
        try:
            module_path = f"sophia.core.{component}"
            module = importlib.import_module(module_path)
            
            # Check if the module has expected functions
            class_name = "".join(word.capitalize() for word in component.split('_'))
            has_class = hasattr(module, class_name)
            
            # Check for core methods
            has_start = hasattr(module, "start") or (has_class and hasattr(getattr(module, class_name), "start"))
            has_stop = hasattr(module, "stop") or (has_class and hasattr(getattr(module, class_name), "stop"))
            
            results[component] = {
                "imported": True,
                "has_class": has_class,
                "has_start": has_start,
                "has_stop": has_stop,
                "status": "complete" if (has_class and has_start and has_stop) else "partial"
            }
            
            logger.info(f"Component {component}: {results[component]['status']}")
        except ImportError:
            results[component] = {
                "imported": False,
                "has_class": False,
                "has_start": False,
                "has_stop": False,
                "status": "missing"
            }
            logger.warning(f"Component {component}: missing")
    
    return results

def check_dependencies():
    """Check all required dependencies."""
    logger.info("Checking dependencies...")
    results = {}
    
    for dep in REQUIRED_DEPS:
        try:
            importlib.import_module(dep)
            results[dep] = {"status": "installed"}
            logger.info(f"Dependency {dep}: installed")
        except ImportError:
            results[dep] = {"status": "missing"}
            logger.warning(f"Dependency {dep}: missing")
    
    return results

def check_shared_utilities():
    """Check Tekton shared utilities."""
    logger.info("Checking Tekton shared utilities...")
    results = {}
    
    for util in SHARED_UTILS:
        try:
            importlib.import_module(util)
            results[util] = {"status": "available"}
            logger.info(f"Utility {util}: available")
        except ImportError:
            results[util] = {"status": "unavailable"}
            logger.warning(f"Utility {util}: unavailable")
    
    return results

def check_sophia_utils():
    """Check Sophia's utility integration."""
    logger.info("Checking Sophia utility integration...")
    results = {}
    
    utils = [
        "tekton_utils",
        "llm_integration",
    ]
    
    for util in utils:
        try:
            module_path = f"sophia.utils.{util}"
            module = importlib.import_module(module_path)
            results[util] = {"status": "implemented"}
            logger.info(f"Utility {util}: implemented")
        except ImportError:
            results[util] = {"status": "missing"}
            logger.warning(f"Utility {util}: missing")
    
    return results

def check_ui_components():
    """Check UI component implementation."""
    logger.info("Checking UI components...")
    results = {}
    
    ui_dir = Path(__file__).parent.parent / "ui"
    
    # Check for HTML component
    component_html = ui_dir / "sophia-component.html"
    results["component_html"] = {
        "status": "implemented" if component_html.exists() else "missing"
    }
    logger.info(f"UI component HTML: {results['component_html']['status']}")
    
    # Check for JavaScript files
    scripts_dir = ui_dir / "scripts"
    scripts = {
        "sophia-component.js": {"path": scripts_dir / "sophia-component.js"},
        "sophia-charts.js": {"path": scripts_dir / "sophia-charts.js"},
        "sophia-recommendations.js": {"path": scripts_dir / "sophia-recommendations.js"},
    }
    
    for script_name, script_info in scripts.items():
        path = script_info["path"]
        status = "implemented" if path.exists() else "missing"
        results[script_name] = {"status": status}
        logger.info(f"UI script {script_name}: {status}")
    
    # Check for CSS
    styles_dir = ui_dir / "styles"
    sophia_css = styles_dir / "sophia.css"
    results["sophia.css"] = {
        "status": "implemented" if sophia_css.exists() else "missing"
    }
    logger.info(f"UI styles: {results['sophia.css']['status']}")
    
    return results

def print_summary(components, dependencies, shared_utils, sophia_utils, ui_components):
    """Print an overall summary of the implementation status."""
    print("\n" + "="*80)
    print("SOPHIA IMPLEMENTATION STATUS SUMMARY")
    print("="*80)
    
    # Count complete components
    complete_components = sum(1 for c in components.values() if c["status"] == "complete")
    print(f"\nCore Components: {complete_components}/{len(components)} complete")
    for component, status in components.items():
        print(f"  - {component}: {status['status']}")
    
    # Count installed dependencies
    installed_deps = sum(1 for d in dependencies.values() if d["status"] == "installed")
    print(f"\nDependencies: {installed_deps}/{len(dependencies)} installed")
    if installed_deps < len(dependencies):
        print("  Missing dependencies:")
        for dep, status in dependencies.items():
            if status["status"] == "missing":
                print(f"    - {dep}")
    
    # Count available shared utilities
    available_utils = sum(1 for u in shared_utils.values() if u["status"] == "available")
    print(f"\nShared Utilities: {available_utils}/{len(shared_utils)} available")
    
    # Count implemented Sophia utilities
    implemented_sophia_utils = sum(1 for u in sophia_utils.values() if u["status"] == "implemented")
    print(f"\nSophia Utilities: {implemented_sophia_utils}/{len(sophia_utils)} implemented")
    
    # Count implemented UI components
    implemented_ui = sum(1 for u in ui_components.values() if u["status"] == "implemented")
    print(f"\nUI Components: {implemented_ui}/{len(ui_components)} implemented")
    
    # Overall status
    print("\n" + "-"*80)
    core_complete = complete_components == len(components)
    deps_complete = installed_deps == len(dependencies)
    sophia_utils_complete = implemented_sophia_utils == len(sophia_utils)
    ui_complete = implemented_ui == len(ui_components)
    
    if core_complete and deps_complete and sophia_utils_complete and ui_complete:
        print("STATUS: FULLY IMPLEMENTED")
    elif core_complete and deps_complete:
        print("STATUS: CORE FUNCTIONALITY COMPLETE, UTILITIES AND UI INCOMPLETE")
    else:
        print("STATUS: INCOMPLETE")
    
    print("-"*80)
    
    # Next steps
    print("\nNext Steps:")
    if not core_complete:
        print("  - Complete core component implementation")
    if not deps_complete:
        print("  - Install missing dependencies")
    if available_utils < len(shared_utils):
        print("  - Install Tekton shared utilities")
    if not sophia_utils_complete:
        print("  - Implement Sophia utility integration")
    if not ui_complete:
        print("  - Complete UI component implementation")
    
    print("="*80)

def main():
    """Run the implementation status check."""
    try:
        # Check core components
        components = check_core_components()
        
        # Check dependencies
        dependencies = check_dependencies()
        
        # Check shared utilities
        shared_utils = check_shared_utilities()
        
        # Check Sophia utilities
        sophia_utils = check_sophia_utils()
        
        # Check UI components
        ui_components = check_ui_components()
        
        # Print summary
        print_summary(components, dependencies, shared_utils, sophia_utils, ui_components)
        
        return 0
    except Exception as e:
        logger.error(f"Error checking implementation status: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())