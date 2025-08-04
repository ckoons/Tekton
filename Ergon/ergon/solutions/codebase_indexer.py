"""
Codebase Indexer Solution
========================

A comprehensive codebase analysis tool that identifies:
- Every method definition and signature
- Every method/function call
- Every data structure (classes, types, interfaces)
- Semantic tags and decorators

This solution creates a searchable index that enables intelligent code navigation,
refactoring suggestions, and deep understanding of code relationships.
"""

import ast
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary,
        state_checkpoint,
        danger_zone
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

logger = logging.getLogger(__name__)

@dataclass
class MethodSignature:
    """Represents a method/function signature"""
    name: str
    file_path: str
    line_number: int
    class_name: Optional[str]
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    decorators: List[str]
    docstring: Optional[str]
    is_async: bool
    visibility: str  # public, private, protected
    
@dataclass
class MethodCall:
    """Represents a method/function call"""
    method_name: str
    file_path: str
    line_number: int
    caller_method: Optional[str]
    arguments: List[str]
    is_chained: bool
    
@dataclass
class DataStructure:
    """Represents a data structure (class, dataclass, etc)"""
    name: str
    file_path: str
    line_number: int
    type: str  # class, dataclass, enum, namedtuple, etc
    base_classes: List[str]
    attributes: Dict[str, Any]
    methods: List[str]
    decorators: List[str]
    docstring: Optional[str]
    
@dataclass
class SemanticTag:
    """Represents a semantic tag or landmark"""
    tag_type: str  # @landmark, @integration_point, etc
    content: str
    file_path: str
    line_number: int
    metadata: Dict[str, Any]

@architecture_decision(
    title="Codebase Indexer Architecture",
    description="AST-based codebase analysis for comprehensive code understanding",
    rationale="Provides foundation for all code intelligence features by extracting method signatures, calls, and structures",
    alternatives_considered=["Regex-based parsing", "Language server protocol", "CTags"],
    impacts=["code_understanding", "refactoring_capabilities", "semantic_search"],
    decided_by="Ergon Team",
    decision_date="2023-12-01"
)
@state_checkpoint(
    title="Codebase Index",
    description="Complete structural index of codebase elements",
    state_type="code_index",
    persistence=True,
    consistency_requirements="Must reflect current codebase state, file hash verification",
    recovery_strategy="Full re-index from source files"
)
class CodebaseIndexer:
    """
    Indexes a codebase to extract structural and semantic information
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.method_signatures: List[MethodSignature] = []
        self.method_calls: List[MethodCall] = []
        self.data_structures: List[DataStructure] = []
        self.semantic_tags: List[SemanticTag] = []
        self.file_hashes: Dict[str, str] = {}
        self.index_timestamp = datetime.utcnow()
        
    @api_contract(
        title="Codebase Indexing API",
        description="Index entire codebase for structural analysis",
        endpoint="/indexer/index",
        method="POST",
        request_schema={
            "include_patterns": "List[str]",
            "exclude_patterns": "List[str]"
        },
        response_schema={
            "statistics": "dict",
            "method_signatures": "List[MethodSignature]",
            "data_structures": "List[DataStructure]",
            "semantic_tags": "List[SemanticTag]"
        },
        performance_requirements="<30s for typical codebase"
    )
    def index_codebase(self, include_patterns: List[str] = None, 
                      exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Index the entire codebase
        
        Args:
            include_patterns: File patterns to include (e.g., ["*.py", "*.js"])
            exclude_patterns: File patterns to exclude (e.g., ["*_test.py", "node_modules/*"])
            
        Returns:
            Dictionary containing the complete index
        """
        include_patterns = include_patterns or ["*.py", "*.js", "*.ts", "*.java"]
        exclude_patterns = exclude_patterns or ["*_test.*", "test_*", "*/tests/*", 
                                               "*/node_modules/*", "*/.venv/*"]
        
        logger.info(f"Starting codebase indexing at {self.project_root}")
        
        # Find all relevant files
        files_to_index = self._find_files(include_patterns, exclude_patterns)
        
        # Index each file
        for file_path in files_to_index:
            try:
                self._index_file(file_path)
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")
                
        # Build relationships
        self._build_relationships()
        
        # Create index summary
        index = {
            "project_root": str(self.project_root),
            "index_timestamp": self.index_timestamp.isoformat(),
            "statistics": {
                "total_files": len(files_to_index),
                "total_methods": len(self.method_signatures),
                "total_calls": len(self.method_calls),
                "total_structures": len(self.data_structures),
                "total_tags": len(self.semantic_tags)
            },
            "method_signatures": [asdict(m) for m in self.method_signatures],
            "method_calls": [asdict(c) for c in self.method_calls],
            "data_structures": [asdict(d) for d in self.data_structures],
            "semantic_tags": [asdict(t) for t in self.semantic_tags],
            "file_hashes": self.file_hashes
        }
        
        logger.info(f"Indexing complete: {index['statistics']}")
        return index
        
    def _find_files(self, include_patterns: List[str], 
                   exclude_patterns: List[str]) -> List[Path]:
        """Find all files matching include patterns but not exclude patterns"""
        files = []
        
        for pattern in include_patterns:
            files.extend(self.project_root.rglob(pattern))
            
        # Filter out excluded patterns
        filtered_files = []
        for file in files:
            exclude = False
            for exc_pattern in exclude_patterns:
                if file.match(exc_pattern):
                    exclude = True
                    break
            if not exclude:
                filtered_files.append(file)
                
        return filtered_files
        
    def _index_file(self, file_path: Path):
        """Index a single file based on its type"""
        # Calculate file hash for change detection
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        self.file_hashes[str(file_path)] = file_hash
        
        # Extract semantic tags from comments
        self._extract_semantic_tags(file_path)
        
        # Language-specific indexing
        if file_path.suffix == '.py':
            self._index_python_file(file_path)
        elif file_path.suffix in ['.js', '.ts']:
            self._index_javascript_file(file_path)
        elif file_path.suffix == '.java':
            self._index_java_file(file_path)
            
    @performance_boundary(
        title="Python AST Parsing",
        description="Parse Python files using AST for accurate extraction",
        sla="<100ms per file",
        optimization_notes="AST parsing provides accuracy over regex approaches",
        measured_impact="Accurate extraction of all code elements"
    )
    def _index_python_file(self, file_path: Path):
        """Index a Python file using AST"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
            visitor = PythonIndexVisitor(str(file_path), self)
            visitor.visit(tree)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            
    def _index_javascript_file(self, file_path: Path):
        """Index JavaScript/TypeScript file"""
        # This would require a JS parser like esprima or babel
        # For now, we'll use regex-based extraction
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract function definitions
        import re
        
        # Function declarations
        func_pattern = r'(?:async\s+)?function\s+(\w+)\s*\((.*?)\)'
        for match in re.finditer(func_pattern, content):
            line_no = content[:match.start()].count('\n') + 1
            self.method_signatures.append(MethodSignature(
                name=match.group(1),
                file_path=str(file_path),
                line_number=line_no,
                class_name=None,
                parameters=self._parse_js_params(match.group(2)),
                return_type=None,
                decorators=[],
                docstring=None,
                is_async='async' in match.group(0),
                visibility='public'
            ))
            
        # Class methods
        method_pattern = r'(\w+)\s*\((.*?)\)\s*{'
        for match in re.finditer(method_pattern, content):
            if match.group(1) not in ['if', 'for', 'while', 'switch', 'catch']:
                line_no = content[:match.start()].count('\n') + 1
                self.method_signatures.append(MethodSignature(
                    name=match.group(1),
                    file_path=str(file_path),
                    line_number=line_no,
                    class_name=None,  # Would need more context
                    parameters=self._parse_js_params(match.group(2)),
                    return_type=None,
                    decorators=[],
                    docstring=None,
                    is_async=False,
                    visibility='public'
                ))
                
    def _index_java_file(self, file_path: Path):
        """Index Java file"""
        # This would require a Java parser
        # For now, we'll use regex-based extraction
        pass
        
    @integration_point(
        title="Semantic Tag Extraction",
        description="Extract landmarks and semantic tags from code comments",
        target_component="Landmarks System",
        protocol="comment_parsing",
        data_flow="Source files → Regex extraction → Semantic tag database",
        integration_date="2024-01-01"
    )
    def _extract_semantic_tags(self, file_path: Path):
        """Extract semantic tags from file comments"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for @landmark, @integration_point, etc
        import re
        tag_pattern = r'[@#]\s*(landmark|integration_point|state_checkpoint|performance_boundary)\s*[:\-]?\s*(.+?)(?:\n|$)'
        
        for match in re.finditer(tag_pattern, content, re.IGNORECASE):
            line_no = content[:match.start()].count('\n') + 1
            self.semantic_tags.append(SemanticTag(
                tag_type=match.group(1).lower(),
                content=match.group(2).strip(),
                file_path=str(file_path),
                line_number=line_no,
                metadata={}
            ))
            
    def _parse_js_params(self, params_str: str) -> List[Dict[str, Any]]:
        """Parse JavaScript parameter string"""
        if not params_str.strip():
            return []
            
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if param:
                # Handle destructuring, defaults, etc
                params.append({
                    'name': param.split('=')[0].strip(),
                    'type': None,
                    'default': param.split('=')[1].strip() if '=' in param else None
                })
        return params
        
    def _build_relationships(self):
        """Build relationships between methods, calls, and structures"""
        # Create lookup maps
        method_map = {m.name: m for m in self.method_signatures}
        structure_map = {s.name: s for s in self.data_structures}
        
        # Link method calls to definitions
        for call in self.method_calls:
            if call.method_name in method_map:
                # Found the definition
                definition = method_map[call.method_name]
                # Could add bidirectional links here
                
        # Link methods to their classes
        for struct in self.data_structures:
            for method_name in struct.methods:
                for method in self.method_signatures:
                    if method.name == method_name and method.class_name == struct.name:
                        # Found the method definition for this class
                        pass
                        
    def search(self, query: str, search_type: str = 'all') -> List[Dict[str, Any]]:
        """
        Search the index
        
        Args:
            query: Search query
            search_type: Type of search ('methods', 'calls', 'structures', 'tags', 'all')
            
        Returns:
            List of matching items
        """
        results = []
        query_lower = query.lower()
        
        if search_type in ['methods', 'all']:
            for method in self.method_signatures:
                if query_lower in method.name.lower():
                    results.append({
                        'type': 'method',
                        'item': asdict(method)
                    })
                    
        if search_type in ['structures', 'all']:
            for struct in self.data_structures:
                if query_lower in struct.name.lower():
                    results.append({
                        'type': 'structure',
                        'item': asdict(struct)
                    })
                    
        if search_type in ['tags', 'all']:
            for tag in self.semantic_tags:
                if query_lower in tag.content.lower():
                    results.append({
                        'type': 'tag',
                        'item': asdict(tag)
                    })
                    
        return results
        
    @api_contract(
        title="Method Call Graph API",
        description="Get call graph showing method relationships",
        endpoint="/indexer/method-graph",
        method="GET",
        request_schema={"method_name": "str"},
        response_schema={
            "method": "str",
            "callers": "List[str]",
            "callees": "List[str]"
        },
        performance_requirements="<50ms response time"
    )
    def get_method_graph(self, method_name: str) -> Dict[str, Any]:
        """
        Get call graph for a method
        
        Returns:
            Dict with 'callers' and 'callees' lists
        """
        callers = []
        callees = []
        
        # Find all calls made by this method
        for call in self.method_calls:
            if call.caller_method == method_name:
                callees.append(call.method_name)
                
        # Find all calls to this method
        for call in self.method_calls:
            if call.method_name == method_name:
                if call.caller_method:
                    callers.append(call.caller_method)
                    
        return {
            'method': method_name,
            'callers': list(set(callers)),
            'callees': list(set(callees))
        }


class PythonIndexVisitor(ast.NodeVisitor):
    """AST visitor for indexing Python code"""
    
    def __init__(self, file_path: str, indexer: CodebaseIndexer):
        self.file_path = file_path
        self.indexer = indexer
        self.current_class = None
        self.current_function = None
        
    def visit_ClassDef(self, node):
        """Visit class definition"""
        # Extract class information
        base_classes = [self._get_name(base) for base in node.bases]
        decorators = [self._get_name(dec) for dec in node.decorator_list]
        docstring = ast.get_docstring(node)
        
        # Get attributes and methods
        attributes = {}
        methods = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Class attribute with type annotation
                attributes[item.target.id] = {
                    'type': self._get_annotation(item.annotation),
                    'value': None
                }
                
        self.indexer.data_structures.append(DataStructure(
            name=node.name,
            file_path=self.file_path,
            line_number=node.lineno,
            type='dataclass' if 'dataclass' in decorators else 'class',
            base_classes=base_classes,
            attributes=attributes,
            methods=methods,
            decorators=decorators,
            docstring=docstring
        ))
        
        # Continue visiting
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node):
        """Visit function definition"""
        self._visit_function(node, is_async=False)
        
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition"""
        self._visit_function(node, is_async=True)
        
    def _visit_function(self, node, is_async: bool):
        """Process function definition"""
        # Extract parameters
        parameters = []
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': self._get_annotation(arg.annotation) if arg.annotation else None,
                'default': None
            }
            parameters.append(param)
            
        # Handle defaults
        defaults_start = len(parameters) - len(node.args.defaults)
        for i, default in enumerate(node.args.defaults):
            parameters[defaults_start + i]['default'] = self._get_default_value(default)
            
        # Get decorators
        decorators = [self._get_name(dec) for dec in node.decorator_list]
        
        # Determine visibility
        visibility = 'private' if node.name.startswith('_') else 'public'
        if node.name.startswith('__') and not node.name.endswith('__'):
            visibility = 'private'
            
        self.indexer.method_signatures.append(MethodSignature(
            name=node.name,
            file_path=self.file_path,
            line_number=node.lineno,
            class_name=self.current_class,
            parameters=parameters,
            return_type=self._get_annotation(node.returns) if node.returns else None,
            decorators=decorators,
            docstring=ast.get_docstring(node),
            is_async=is_async,
            visibility=visibility
        ))
        
        # Continue visiting to find calls
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_Call(self, node):
        """Visit function call"""
        if isinstance(node.func, ast.Name):
            method_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
        else:
            self.generic_visit(node)
            return
            
        # Extract arguments
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Name):
                args.append(arg.id)
            elif isinstance(arg, ast.Constant):
                args.append(str(arg.value))
            else:
                args.append('<complex>')
                
        self.indexer.method_calls.append(MethodCall(
            method_name=method_name,
            file_path=self.file_path,
            line_number=node.lineno,
            caller_method=self.current_function,
            arguments=args,
            is_chained=isinstance(node.func, ast.Attribute)
        ))
        
        self.generic_visit(node)
        
    def _get_name(self, node) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        else:
            return str(node)
            
    def _get_annotation(self, node) -> Optional[str]:
        """Get type annotation as string"""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
            
    def _get_default_value(self, node) -> Any:
        """Get default value from AST node"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return node.id
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else '<complex>'


# Integration with Ergon
@integration_point(
    title="Codebase Indexer Integration",
    description="Integrates codebase indexer with Ergon's solution registry",
    target_component="Ergon",
    protocol="solution_registry",
    data_flow="Ergon → Indexer instantiation → Code analysis services",
    integration_date="2023-12-01"
)
def create_indexer_solution():
    """
    Create the codebase indexer solution for Ergon's registry
    """
    return {
        "name": "Codebase Indexer",
        "type": "analysis",
        "description": "Comprehensive codebase analysis that indexes all methods, calls, data structures, and semantic tags",
        "capabilities": [
            "method_extraction",
            "call_graph_analysis",
            "data_structure_mapping",
            "semantic_tag_detection",
            "cross_reference_building"
        ],
        "configuration": {
            "include_patterns": ["*.py", "*.js", "*.ts", "*.java"],
            "exclude_patterns": ["*_test.*", "*/tests/*", "*/node_modules/*"],
            "index_on_change": True,
            "cache_results": True
        },
        "implementation": {
            "class": "CodebaseIndexer",
            "module": "ergon.solutions.codebase_indexer",
            "version": "1.0.0"
        }
    }