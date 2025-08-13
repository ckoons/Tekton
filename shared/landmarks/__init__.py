#!/usr/bin/env python3
"""
Shared Landmark System for Work Product Enrichment

Provides automatic landmark insertion for all Tekton workflows.
Both deterministic code and CIs use this to spread breadcrumbs.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

class LandmarkType(Enum):
    """Types of landmarks that can be inserted"""
    # Structural (code-generated)
    PROPOSAL_CREATED = "proposal_created"
    SPRINT_INITIATED = "sprint_initiated" 
    PHASE_TRANSITION = "phase_transition"
    WORKFLOW_CHECKPOINT = "workflow_checkpoint"
    
    # Semantic (CI-added)
    PATTERN_REFERENCE = "pattern_reference"
    COACHING_MOMENT = "coaching_moment"
    EXAMPLE_NEEDED = "example_needed"
    CI_ATTENTION = "ci_attention"
    DECISION_POINT = "decision_point"
    COMPLEXITY_FLAG = "complexity_flag"
    EVOLUTION_POINT = "evolution_point"
    CONTEXT_BRIDGE = "context_bridge"


class LandmarkInserter:
    """Automatically inserts landmarks into work products"""
    
    @staticmethod
    def add_to_markdown(content: str, landmark_type: str, context: str = "") -> str:
        """Add landmark to markdown content"""
        landmark = f"<!-- @{landmark_type}: {context} -->"
        
        # Smart insertion based on content structure
        if "# " in content[:50]:  # Has a title
            # Insert after title
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    lines.insert(i + 1, landmark)
                    break
            return '\n'.join(lines)
        else:
            # Insert at beginning
            return f"{landmark}\n{content}"
    
    @staticmethod
    def add_to_json(data: Dict, landmark_type: str, context: Any) -> Dict:
        """Add landmark to JSON structure"""
        if "@landmarks" not in data:
            data["@landmarks"] = []
        
        data["@landmarks"].append({
            "type": landmark_type,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        return data
    
    @staticmethod
    def add_to_python(content: str, landmark_type: str, context: str = "") -> str:
        """Add landmark comment to Python code"""
        landmark = f"# @{landmark_type}: {context}"
        
        # Add after imports if present
        if "import " in content or "from " in content:
            lines = content.split('\n')
            last_import = 0
            for i, line in enumerate(lines):
                if line.startswith(('import ', 'from ')):
                    last_import = i
            lines.insert(last_import + 1, f"\n{landmark}")
            return '\n'.join(lines)
        else:
            return f"{landmark}\n{content}"


class WorkflowLandmarks:
    """Landmark insertion for specific workflows"""
    
    @staticmethod
    def proposal_creation(proposal_path: Path, proposal_data: Dict) -> None:
        """Add landmarks when proposal is created"""
        # Add to JSON
        proposal_data = LandmarkInserter.add_to_json(
            proposal_data,
            LandmarkType.PROPOSAL_CREATED.value,
            {"created_by": "workflow", "triggers": ["Telos", "Prometheus"]}
        )
        
        # Write back
        with open(proposal_path, 'w') as f:
            json.dump(proposal_data, f, indent=2)
    
    @staticmethod
    def sprint_conversion(sprint_dir: Path, proposal_name: str) -> None:
        """Add landmarks during sprint conversion"""
        # Add to SPRINT_PLAN.md
        sprint_plan = sprint_dir / "SPRINT_PLAN.md"
        if sprint_plan.exists():
            content = sprint_plan.read_text()
            content = LandmarkInserter.add_to_markdown(
                content,
                LandmarkType.SPRINT_INITIATED.value,
                f"converted from {proposal_name}"
            )
            
            # Add CI attention landmarks for Planning Team
            content = LandmarkInserter.add_to_markdown(
                content,
                LandmarkType.CI_ATTENTION.value,
                "Telos, extract UI requirements"
            )
            content = LandmarkInserter.add_to_markdown(
                content,
                LandmarkType.CI_ATTENTION.value,
                "Prometheus, suggest phases"
            )
            content = LandmarkInserter.add_to_markdown(
                content,
                LandmarkType.CI_ATTENTION.value,
                "Metis, decompose tasks"
            )
            
            sprint_plan.write_text(content)
        
        # Add to DAILY_LOG.md
        daily_log = sprint_dir / "DAILY_LOG.md"
        if daily_log.exists():
            content = daily_log.read_text()
            content = LandmarkInserter.add_to_markdown(
                content,
                LandmarkType.WORKFLOW_CHECKPOINT.value,
                "sprint initialized"
            )
            daily_log.write_text(content)
    
    @staticmethod
    def phase_transition(daily_log_path: Path, from_phase: str, to_phase: str) -> None:
        """Add landmarks at phase transitions"""
        if daily_log_path.exists():
            content = daily_log_path.read_text()
            
            # Add phase transition landmark
            landmark_text = f"\n<!-- @{LandmarkType.PHASE_TRANSITION.value}: {from_phase} → {to_phase} -->\n"
            
            # Find today's entry and add landmark
            today = datetime.now().strftime("## Day")
            if today in content:
                # Insert after today's header
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if today in line:
                        lines.insert(i + 1, landmark_text)
                        break
                content = '\n'.join(lines)
            else:
                # Append to end
                content += landmark_text
            
            daily_log_path.write_text(content)
    
    @staticmethod
    def code_generation(file_path: Path, pattern_refs: List[str] = None) -> None:
        """Add landmarks to generated code"""
        if not file_path.exists():
            return
            
        content = file_path.read_text()
        
        # Add pattern references if provided
        if pattern_refs:
            for pattern in pattern_refs:
                if file_path.suffix == '.py':
                    content = LandmarkInserter.add_to_python(
                        content,
                        LandmarkType.PATTERN_REFERENCE.value,
                        pattern
                    )
                elif file_path.suffix == '.md':
                    content = LandmarkInserter.add_to_markdown(
                        content,
                        LandmarkType.PATTERN_REFERENCE.value,
                        pattern
                    )
        
        file_path.write_text(content)


class LandmarkRegistry:
    """Central registry for all landmarks"""
    
    _landmarks: Dict[str, List[Dict]] = {}
    
    @classmethod
    def fire(cls, landmark_type: str, context: Dict = None) -> None:
        """Fire a landmark, triggering cascades"""
        landmark_event = {
            "type": landmark_type,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in registry
        if landmark_type not in cls._landmarks:
            cls._landmarks[landmark_type] = []
        cls._landmarks[landmark_type].append(landmark_event)
        
        # Log it (this would trigger CI attention)
        print(f"🏔️ Landmark fired: {landmark_type}")
        if context:
            print(f"   Context: {context}")
        
        # Trigger CI cascade if specified
        if context and "triggers" in context:
            cls._trigger_ci_cascade(context["triggers"], landmark_type, context)
    
    @classmethod
    def _trigger_ci_cascade(cls, ci_list: List[str], landmark_type: str, context: Dict) -> None:
        """Notify CIs about landmark (would integrate with aish)"""
        for ci in ci_list:
            # This would send actual notifications via aish
            print(f"   → Notifying {ci} about {landmark_type}")
    
    @classmethod
    def query(cls, pattern: str = None, landmark_type: str = None) -> List[Dict]:
        """Query landmarks by pattern or type"""
        results = []
        
        if landmark_type:
            results.extend(cls._landmarks.get(landmark_type, []))
        
        if pattern:
            # Search all landmarks for pattern in context
            for landmarks in cls._landmarks.values():
                for landmark in landmarks:
                    if pattern.lower() in str(landmark).lower():
                        results.append(landmark)
        
        return results
    
    @classmethod
    def suggest_emergent(cls) -> List[str]:
        """Suggest new landmark types based on patterns"""
        # This would analyze repeated phrases in work products
        # For now, return placeholder
        return ["@performance_bottleneck", "@security_consideration"]


# Convenience functions for use in code
def add_landmark(file_path: Path, landmark_type: str, context: str = "") -> None:
    """Quick function to add landmark to any file"""
    if not file_path.exists():
        return
    
    content = file_path.read_text()
    
    if file_path.suffix == '.md':
        content = LandmarkInserter.add_to_markdown(content, landmark_type, context)
    elif file_path.suffix == '.py':
        content = LandmarkInserter.add_to_python(content, landmark_type, context)
    elif file_path.suffix == '.json':
        data = json.loads(content)
        data = LandmarkInserter.add_to_json(data, landmark_type, context)
        content = json.dumps(data, indent=2)
    
    file_path.write_text(content)
    LandmarkRegistry.fire(landmark_type, {"file": str(file_path), "context": context})


# Export main components
__all__ = [
    'LandmarkType',
    'LandmarkInserter', 
    'WorkflowLandmarks',
    'LandmarkRegistry',
    'add_landmark'
]