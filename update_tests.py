#!/usr/bin/env python3
"""
Script to update all test files from old node("var", "Label") syntax 
to new node("Label", variable="var") syntax.
"""

import os
import re
import glob

def update_node_syntax(content):
    """Update node syntax from old to new format."""
    
    # Pattern 1: node("var", "Label") -> node("Label", variable="var") 
    # where var starts with lowercase and Label starts with uppercase
    pattern1 = r'node\("([a-z][a-zA-Z0-9_]*)",\s*"([A-Z][a-zA-Z0-9_]*)"\)'
    def replacement1(match):
        var_name = match.group(1)
        label_name = match.group(2)
        return f'node("{label_name}", variable="{var_name}")'
    updated_content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: node("var", "Label", params...) -> node("Label", variable="var", params...)
    pattern2 = r'node\("([a-z][a-zA-Z0-9_]*)",\s*"([A-Z][a-zA-Z0-9_]*)"(,\s*[^)]+)\)'
    def replacement2(match):
        var_name = match.group(1)
        label_name = match.group(2)
        params = match.group(3)
        return f'node("{label_name}", variable="{var_name}"{params})'
    updated_content = re.sub(pattern2, replacement2, updated_content)
    
    # Pattern 3: node("var:Label") -> node("Label", variable="var")
    # Handles cases like node("m:Movie")
    pattern3 = r'node\("([a-z][a-zA-Z0-9_]*):([A-Z][a-zA-Z0-9_]*)"\)'
    def replacement3(match):
        var_name = match.group(1)
        label_name = match.group(2)
        return f'node("{label_name}", variable="{var_name}")'
    updated_content = re.sub(pattern3, replacement3, updated_content)
    
    # Pattern 4: node("var") -> node(variable="var")
    # For variable-only nodes where var is lowercase (single letter usually)
    pattern4 = r'node\("([a-z])\")(?!\s*\.)'  # Negative lookahead to avoid matching node("n").method()
    def replacement4(match):
        var_name = match.group(1)
        return f'node(variable="{var_name}")'
    updated_content = re.sub(pattern4, replacement4, updated_content)
    
    return updated_content

def update_test_file(filepath):
    """Update a single test file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updated_content = update_node_syntax(content)
    
    if updated_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Updated: {filepath}")
        return True
    return False

def main():
    """Update all test files."""
    test_files = glob.glob('/Users/user/git/super-sniffle/tests/unit/test_*.py')
    
    updated_count = 0
    for filepath in test_files:
        if update_test_file(filepath):
            updated_count += 1
    
    print(f"\nUpdated {updated_count} files total.")

if __name__ == '__main__':
    main()