"""Data models for UI DevTools"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ToolStatus(Enum):
    """Status of tool execution"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class SemanticTag:
    """Represents a single semantic tag"""
    name: str  # e.g., "area", "component", "action"
    value: str  # e.g., "rhetor", "chat-interface", "send-message"
    element: str  # e.g., "div", "button"
    attributes: Dict[str, str] = field(default_factory=dict)  # Other attributes on the element
    
    @property
    def full_name(self) -> str:
        """Get full data attribute name"""
        return f"data-tekton-{self.name}"


@dataclass
class ComponentInfo:
    """Information about a component"""
    name: str
    file_path: str
    exists: bool
    content: Optional[str] = None
    error: Optional[str] = None


@dataclass
class SemanticTagAnalysis:
    """Analysis of semantic tags in a component"""
    component_name: str
    source: str  # "code" or "browser"
    tags: List[SemanticTag] = field(default_factory=list)
    tag_summary: Dict[str, List[str]] = field(default_factory=dict)  # Tag name -> list of values
    total_count: int = 0
    
    def add_tag(self, tag: SemanticTag) -> None:
        """Add a tag to the analysis"""
        self.tags.append(tag)
        if tag.name not in self.tag_summary:
            self.tag_summary[tag.name] = []
        if tag.value not in self.tag_summary[tag.name]:
            self.tag_summary[tag.name].append(tag.value)
        self.total_count += 1
    
    def get_tag_names(self) -> List[str]:
        """Get all unique tag names"""
        return list(self.tag_summary.keys())
    
    def get_tag_values(self, tag_name: str) -> List[str]:
        """Get all values for a specific tag"""
        return self.tag_summary.get(tag_name, [])


@dataclass
class DiscrepancyInfo:
    """Information about discrepancies between code and browser"""
    component_name: str
    code_tags: SemanticTagAnalysis
    browser_tags: SemanticTagAnalysis
    in_code_only: List[str] = field(default_factory=list)  # Tag names only in code
    in_browser_only: List[str] = field(default_factory=list)  # Tag names only in browser
    diagnosis: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def analyze(self) -> None:
        """Analyze the discrepancies"""
        code_names = set(self.code_tags.get_tag_names())
        browser_names = set(self.browser_tags.get_tag_names())
        
        self.in_code_only = sorted(list(code_names - browser_names))
        self.in_browser_only = sorted(list(browser_names - code_names))
        
        # Generate diagnosis
        if self.code_tags.total_count > self.browser_tags.total_count:
            missing_count = self.code_tags.total_count - self.browser_tags.total_count
            self.diagnosis = f"{missing_count} semantic tags found in source but missing from DOM"
            
            # Add likely causes
            if self.in_code_only:
                self.recommendations.append("Check if component loader preserves data-* attributes")
                self.recommendations.append("Verify no sanitization removes data-tekton-* attributes")
                self.recommendations.append("Check timing - attributes may be added then removed")


@dataclass
class ToolResult:
    """Standard result format for all tools"""
    tool_name: str
    status: ToolStatus
    component: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "tool": self.tool_name,
            "status": self.status.value,
            "data": self.data
        }
        if self.component:
            result["component"] = self.component
        if self.error:
            result["error"] = self.error
        if self.warnings:
            result["warnings"] = self.warnings
        return result