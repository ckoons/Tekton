#!/usr/bin/env python3
"""
Bulk find/replace script with sed-like regex support.

Usage:
    find . -name "*.py" | sed_files.py --find "pattern" --replace "replacement"
    find . -name "*.py" | sed_files.py --find "pattern" --replace "replacement" --apply
    sed_files.py --file list.txt --find "old" --replace "new"
    
Default is dry-run mode. Use --apply to make actual changes.
"""

import os
import sys
import re
import argparse
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
import difflib
import mimetypes

def is_binary_file(filepath: str) -> bool:
    """Check if file is binary."""
    try:
        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type and mime_type.startswith('text'):
            return False
        
        # Check first 8192 bytes for null bytes
        with open(filepath, 'rb') as f:
            chunk = f.read(8192)
            if b'\0' in chunk:
                return True
                
        return False
    except Exception:
        return True

def parse_sed_pattern(pattern_str: str) -> Tuple[str, str]:
    """
    Parse sed-style flags from pattern.
    Returns (pattern, flags_string)
    
    Examples:
        "pattern/gi" -> ("pattern", "gi")
        "pattern" -> ("pattern", "")
    """
    # Check if pattern ends with flags (like /g, /i, /gi)
    if '/' in pattern_str and pattern_str.rindex('/') > 0:
        last_slash = pattern_str.rindex('/')
        pattern = pattern_str[:last_slash]
        flags = pattern_str[last_slash + 1:]
        return pattern, flags
    return pattern_str, ""

def apply_sed_flags(regex, flags: str):
    """Convert sed flags to Python regex flags."""
    re_flags = 0
    if 'i' in flags:
        re_flags |= re.IGNORECASE
    if 'm' in flags:
        re_flags |= re.MULTILINE
    if 's' in flags:
        re_flags |= re.DOTALL
    return re_flags

def apply_replacement(line: str, find_pattern: str, replace_str: str, 
                     word_boundary: bool = False) -> Tuple[str, bool]:
    """
    Apply find/replace to a line.
    Returns (new_line, was_changed)
    """
    pattern, flags = parse_sed_pattern(find_pattern)
    
    # Add word boundaries if requested
    if word_boundary:
        pattern = r'\b' + pattern + r'\b'
    
    re_flags = apply_sed_flags(pattern, flags)
    
    # Check if global flag is set (replace all occurrences)
    count = 0 if 'g' in flags else 1
    
    try:
        compiled_pattern = re.compile(pattern, re_flags)
        new_line = compiled_pattern.sub(replace_str, line, count=count)
        return new_line, (new_line != line)
    except re.error as e:
        print(f"Error: Invalid regex pattern: {e}", file=sys.stderr)
        sys.exit(1)

def process_file(filepath: str, find_pattern: str, replace_str: str,
                apply_changes: bool, backup_dir: Optional[Path],
                word_boundary: bool, verbose: bool) -> Tuple[int, List[str]]:
    """
    Process a single file.
    Returns (lines_changed, diff_output)
    """
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}", file=sys.stderr)
        return 0, []
    
    if is_binary_file(filepath):
        if verbose:
            print(f"Skipping binary file: {filepath}", file=sys.stderr)
        return 0, []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
    except Exception as e:
        print(f"Warning: Cannot read {filepath}: {e}", file=sys.stderr)
        return 0, []
    
    # Apply replacements
    new_lines = []
    lines_changed = 0
    for line in original_lines:
        new_line, changed = apply_replacement(line, find_pattern, replace_str, word_boundary)
        new_lines.append(new_line)
        if changed:
            lines_changed += 1
    
    if lines_changed == 0:
        return 0, []
    
    # Generate diff output
    diff_output = list(difflib.unified_diff(
        original_lines, new_lines,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
        lineterm='',
        n=3
    ))
    
    if apply_changes:
        # Create backup
        if backup_dir and not args.no_backup:
            backup_path = backup_dir / os.path.basename(filepath)
            # Add number suffix if file exists
            if backup_path.exists():
                i = 1
                while True:
                    backup_path = backup_dir / f"{os.path.basename(filepath)}.{i}"
                    if not backup_path.exists():
                        break
                    i += 1
            
            shutil.copy2(filepath, backup_path)
            if verbose:
                print(f"Backed up: {filepath} -> {backup_path}", file=sys.stderr)
        
        # Write changes
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    
    return lines_changed, diff_output

def main():
    parser = argparse.ArgumentParser(
        description='Bulk find/replace with sed-like patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  find . -name "*.py" | %(prog)s --find "old_var" --replace "new_var"
  %(prog)s --file list.txt --find "pattern" --replace "replacement" --apply
  %(prog)s --find "(?i)todo" --replace "FIXED" --file list.txt
  %(prog)s --find "word/gi" --replace "WORD" --word-boundary --apply
        """
    )
    
    # Input source
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('-f', '--file', help='File containing list of files to process')
    input_group.add_argument('files', nargs='*', help='Files to process (or stdin if none)')
    
    # Find/Replace patterns
    parser.add_argument('--find', required=True, help='Pattern to find (regex with optional /flags)')
    parser.add_argument('--replace', required=True, help='Replacement string')
    
    # Modes
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (default)')
    
    # Options
    parser.add_argument('-w', '--word-boundary', action='store_true', 
                       help='Match whole words only')
    parser.add_argument('--backup-dir', type=Path,
                       help='Backup directory (default: /tmp/sed_files_TIMESTAMP)')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backups (use with caution!)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show verbose output')
    
    global args
    args = parser.parse_args()
    
    # Validate mode
    if args.dry_run and args.apply:
        print("Error: Cannot specify both --dry-run and --apply", file=sys.stderr)
        sys.exit(1)
    
    # Default is dry-run
    apply_mode = args.apply
    
    # Get list of files
    file_list = []
    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_list = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading file list: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.files:
        file_list = args.files
    else:
        # Read from stdin
        file_list = [line.strip() for line in sys.stdin if line.strip()]
    
    if not file_list:
        print("Error: No files to process", file=sys.stderr)
        sys.exit(1)
    
    # Validate files exist
    valid_files = []
    for filepath in file_list:
        if os.path.exists(filepath):
            valid_files.append(filepath)
        else:
            print(f"Warning: File not found, skipping: {filepath}", file=sys.stderr)
    
    if not valid_files:
        print("Error: No valid files to process", file=sys.stderr)
        sys.exit(1)
    
    # Setup backup directory if applying changes
    backup_dir = None
    if apply_mode and not args.no_backup:
        if args.backup_dir:
            backup_dir = args.backup_dir
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = Path(f'/tmp/sed_files_{timestamp}')
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"Backup directory: {backup_dir}", file=sys.stderr)
    
    # Process files
    total_files_changed = 0
    total_lines_changed = 0
    
    for filepath in valid_files:
        lines_changed, diff_output = process_file(
            filepath, args.find, args.replace,
            apply_mode, backup_dir, args.word_boundary, args.verbose
        )
        
        if lines_changed > 0:
            total_files_changed += 1
            total_lines_changed += lines_changed
            
            # Show diff in dry-run mode or verbose
            if not apply_mode or args.verbose:
                print('\n'.join(diff_output))
    
    # Show summary
    print(f"\n{'='*60}", file=sys.stderr)
    if apply_mode:
        print(f"APPLIED: Changed {total_lines_changed} lines in {total_files_changed} files", file=sys.stderr)
        if backup_dir and not args.no_backup:
            print(f"Backups saved to: {backup_dir}", file=sys.stderr)
    else:
        print(f"DRY RUN: Would change {total_lines_changed} lines in {total_files_changed} files", file=sys.stderr)
        print(f"Use --apply to make changes", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    
    return 0 if total_files_changed > 0 else 1

if __name__ == '__main__':
    sys.exit(main())