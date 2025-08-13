#!/usr/bin/env python3
"""
Examples of integrating landmarks into existing Tekton workflows

Shows how deterministic code can spread breadcrumbs automatically.
"""

from pathlib import Path
from shared.landmarks import WorkflowLandmarks, LandmarkRegistry, add_landmark, LandmarkType

# =============================================================================
# PROPOSAL CREATION WORKFLOW
# =============================================================================

def create_proposal_with_landmarks(proposal_data: dict, proposals_dir: Path):
    """Example: Creating a proposal with automatic landmarks"""
    
    # 1. Create the proposal file
    proposal_name = proposal_data["name"]
    proposal_path = proposals_dir / f"{proposal_name}.json"
    
    # 2. Automatically add creation landmark
    WorkflowLandmarks.proposal_creation(proposal_path, proposal_data)
    
    # 3. Fire registry event (triggers CI attention)
    LandmarkRegistry.fire(
        LandmarkType.PROPOSAL_CREATED.value,
        {
            "proposal": proposal_name,
            "purpose": proposal_data.get("purpose"),
            "triggers": ["Telos", "Prometheus", "Metis"]  # CIs to notify
        }
    )
    
    print(f"✨ Proposal created with landmarks: {proposal_name}")


# =============================================================================
# SPRINT CONVERSION WORKFLOW  
# =============================================================================

def convert_proposal_to_sprint_with_landmarks(proposal_name: str, sprints_dir: Path):
    """Example: Converting proposal to sprint with breadcrumbs"""
    
    # 1. Create sprint directory structure
    sprint_dir = sprints_dir / f"{proposal_name}_Sprint"
    sprint_dir.mkdir(exist_ok=True)
    
    # Create standard files
    (sprint_dir / "SPRINT_PLAN.md").write_text(f"# {proposal_name} Sprint Plan\n")
    (sprint_dir / "DAILY_LOG.md").write_text(f"# Daily Log\n## Day 1\n")
    (sprint_dir / "HANDOFF.md").write_text(f"# Handoff Document\n")
    
    # 2. Add conversion landmarks automatically
    WorkflowLandmarks.sprint_conversion(sprint_dir, proposal_name)
    
    # 3. Fire cascade to Planning Team CIs
    LandmarkRegistry.fire(
        LandmarkType.SPRINT_INITIATED.value,
        {
            "sprint": proposal_name,
            "directory": str(sprint_dir),
            "triggers": ["Telos", "Prometheus", "Metis", "Harmonia"],
            "cascade_order": "sequential"  # CIs process in order
        }
    )
    
    print(f"🚀 Sprint created with landmark cascade: {proposal_name}")


# =============================================================================
# CODE GENERATION WORKFLOW
# =============================================================================

def generate_component_with_landmarks(component_name: str, component_dir: Path):
    """Example: Generating code with pattern references"""
    
    # 1. Generate the component file
    component_file = component_dir / f"{component_name.lower()}_component.py"
    
    component_code = f'''"""
{component_name} Component
Auto-generated with landmarks
"""

from shared.base import BaseComponent

class {component_name}Component(BaseComponent):
    """Main component class"""
    
    def __init__(self):
        super().__init__("{component_name.lower()}")
    
    def process(self, data):
        """Process incoming data"""
        # Implementation here
        pass
'''
    
    component_file.write_text(component_code)
    
    # 2. Add pattern references based on component type
    if "UI" in component_name:
        WorkflowLandmarks.code_generation(
            component_file,
            pattern_refs=["telos_ui_patterns", "css_first_architecture"]
        )
    elif "API" in component_name:
        WorkflowLandmarks.code_generation(
            component_file,
            pattern_refs=["fastapi_structure", "hermes_routing"]
        )
    
    # 3. Fire landmark for code review
    LandmarkRegistry.fire(
        LandmarkType.PATTERN_REFERENCE.value,
        {
            "component": component_name,
            "file": str(component_file),
            "triggers": ["Harmonia"],  # For code review
            "patterns_used": ["base_component", "standard_structure"]
        }
    )
    
    print(f"💻 Component generated with pattern landmarks: {component_name}")


# =============================================================================
# PHASE TRANSITION WORKFLOW
# =============================================================================

def transition_sprint_phase_with_landmarks(sprint_dir: Path, from_phase: str, to_phase: str):
    """Example: Phase transitions with automatic landmarks"""
    
    daily_log = sprint_dir / "DAILY_LOG.md"
    
    # 1. Add phase transition landmark
    WorkflowLandmarks.phase_transition(daily_log, from_phase, to_phase)
    
    # 2. Fire registry event with context
    LandmarkRegistry.fire(
        LandmarkType.PHASE_TRANSITION.value,
        {
            "sprint": sprint_dir.name,
            "from": from_phase,
            "to": to_phase,
            "triggers": self._get_phase_cis(to_phase)  # CIs for new phase
        }
    )
    
    # 3. Add coaching moment if entering complex phase
    if to_phase in ["implementation", "integration"]:
        add_landmark(
            daily_log,
            LandmarkType.COACHING_MOMENT.value,
            f"Entering {to_phase} - review patterns with team"
        )
    
    print(f"📊 Phase transition marked: {from_phase} → {to_phase}")


def _get_phase_cis(phase: str) -> list:
    """Determine which CIs should be notified for each phase"""
    phase_cis = {
        "planning": ["Telos", "Prometheus"],
        "design": ["Athena", "Rhetor"],
        "implementation": ["Ergon", "Harmonia"],
        "testing": ["Metis", "Synthesis"],
        "integration": ["Hermes", "TektonCore"]
    }
    return phase_cis.get(phase.lower(), ["Numa"])  # Numa as default


# =============================================================================
# DOCUMENTATION WORKFLOW
# =============================================================================

def generate_docs_with_landmarks(component_name: str, docs_dir: Path):
    """Example: Documentation generation with landmarks"""
    
    doc_file = docs_dir / f"{component_name}.md"
    
    # 1. Create documentation with initial landmark
    doc_content = f"""# {component_name} Documentation
<!-- @{LandmarkType.WORKFLOW_CHECKPOINT.value}: documentation generated -->
<!-- @{LandmarkType.CI_ATTENTION.value}: Noesis, enrich with examples -->

## Overview
Documentation for {component_name} component.

## Architecture
<!-- @{LandmarkType.PATTERN_REFERENCE.value}: standard_component_architecture -->

## Usage Examples
<!-- @{LandmarkType.EXAMPLE_NEEDED.value}: real-world usage patterns -->

## API Reference
<!-- @{LandmarkType.EVOLUTION_POINT.value}: replaces legacy API -->
"""
    
    doc_file.write_text(doc_content)
    
    # 2. Fire landmark for documentation review
    LandmarkRegistry.fire(
        LandmarkType.WORKFLOW_CHECKPOINT.value,
        {
            "document": component_name,
            "file": str(doc_file),
            "triggers": ["Noesis", "Sophia"],  # Documentation specialists
            "needs": ["examples", "review"]
        }
    )
    
    print(f"📚 Documentation created with landmarks: {component_name}")


# =============================================================================
# QUERY AND DISCOVERY
# =============================================================================

def discover_patterns():
    """Example: Discovering patterns through landmark queries"""
    
    # Query all pattern references
    patterns = LandmarkRegistry.query(landmark_type=LandmarkType.PATTERN_REFERENCE.value)
    print(f"\n🔍 Found {len(patterns)} pattern references")
    
    # Query all coaching moments
    coaching = LandmarkRegistry.query(landmark_type=LandmarkType.COACHING_MOMENT.value)
    print(f"👥 Found {len(coaching)} coaching moments")
    
    # Search for specific context
    ui_related = LandmarkRegistry.query(pattern="ui")
    print(f"🎨 Found {len(ui_related)} UI-related landmarks")
    
    # Suggest emergent patterns
    emergent = LandmarkRegistry.suggest_emergent()
    if emergent:
        print(f"✨ Suggested new landmark types: {', '.join(emergent)}")


if __name__ == "__main__":
    # Example usage
    print("🏔️ Landmark Integration Examples")
    print("=" * 50)
    
    # Show how landmarks flow through workflows
    test_dir = Path("/tmp/tekton_landmark_test")
    test_dir.mkdir(exist_ok=True)
    
    # Create proposal with landmarks
    proposal = {
        "name": "TestDashboard",
        "purpose": "Test landmark integration",
        "description": "Example proposal with automatic landmarks"
    }
    
    create_proposal_with_landmarks(proposal, test_dir)
    
    # Convert to sprint with cascade
    convert_proposal_to_sprint_with_landmarks("TestDashboard", test_dir)
    
    # Discover patterns
    discover_patterns()