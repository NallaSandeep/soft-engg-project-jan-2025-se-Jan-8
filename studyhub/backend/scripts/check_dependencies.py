#!/usr/bin/env python
"""
Script to analyze Python package dependencies usage in the codebase.
"""

import os
import ast
import sys
from pathlib import Path
import pkg_resources
import re
import codecs

def normalize_package_name(name):
    """Normalize package name to handle common variations."""
    name = name.lower().strip()
    name = re.sub(r'\[.*\]', '', name)  # Remove extras like [cryptography]
    name = name.replace('-', '_')  # Replace hyphens with underscores
    return name

def get_imports_from_file(file_path):
    """Extract all imports from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            print(f"Syntax error in {file_path}")
            return set()
        except UnicodeDecodeError:
            print(f"Encoding error in {file_path}")
            return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(normalize_package_name(name.name.split('.')[0]))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(normalize_package_name(node.module.split('.')[0]))
    return imports

def get_project_imports(directory):
    """Get all imports used in the project."""
    all_imports = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                all_imports.update(get_imports_from_file(file_path))
    return all_imports

def get_installed_packages():
    """Get all installed packages with their versions."""
    return {normalize_package_name(pkg.key): pkg.version for pkg in pkg_resources.working_set}

def read_requirements_file():
    """Read requirements.txt with different encoding attempts."""
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16le', 'utf-16be', 'ascii']
    
    for encoding in encodings:
        try:
            with open('requirements.txt', 'r', encoding=encoding) as file:
                return file.readlines()
        except UnicodeError:
            continue
    
    # If all encodings fail, try binary read and decode
    try:
        with open('requirements.txt', 'rb') as file:
            content = file.read()
            # Try to detect BOM and decode accordingly
            if content.startswith(codecs.BOM_UTF8):
                return content.decode('utf-8-sig').splitlines()
            elif content.startswith(codecs.BOM_UTF16_LE):
                return content.decode('utf-16le').splitlines()
            elif content.startswith(codecs.BOM_UTF16_BE):
                return content.decode('utf-16be').splitlines()
            # Try utf-8 as last resort
            return content.decode('utf-8').splitlines()
    except Exception as e:
        print(f"Error reading requirements.txt: {e}")
        return []

def get_requirements():
    """Read requirements from requirements.txt."""
    requirements = {}
    lines = read_requirements_file()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            try:
                if '==' in line:
                    package, version = line.split('==', 1)
                else:
                    package, version = line, None
                package = normalize_package_name(package)
                requirements[package] = version
            except ValueError:
                print(f"Warning: Could not parse requirement: {line}")
    return requirements

def get_package_dependencies(package_name):
    """Get dependencies of a package."""
    try:
        package = pkg_resources.working_set.by_key[package_name]
        return {normalize_package_name(req.name) for req in package.requires()}
    except Exception:
        return set()

def main():
    # Get project root (assuming script is in scripts directory)
    project_root = Path(__file__).parent.parent
    
    print("Analyzing imports...")
    # Check all Python files in the project, not just app directory
    used_imports = set()
    for directory in ['app', 'scripts', 'tests']:
        dir_path = project_root / directory
        if dir_path.exists():
            used_imports.update(get_project_imports(dir_path))
    
    installed_packages = get_installed_packages()
    requirements = get_requirements()

    # Get all dependencies of used packages
    all_dependencies = set()
    for imp in used_imports:
        all_dependencies.add(imp)
        all_dependencies.update(get_package_dependencies(imp))

    print("\nDirectly imported packages:")
    for imp in sorted(used_imports):
        if imp in installed_packages:
            print(f"- {imp} (version: {installed_packages[imp]}")

    print("\nPackages in requirements.txt that might be unused:")
    unused_packages = []
    for package in sorted(requirements.keys()):
        if package not in all_dependencies and package not in {
            'pip', 'setuptools', 'wheel', 'pytest', 'pytest_flask', 'black', 'flake8'  # Development tools
        }:
            unused_packages.append(f"- {package} (version: {requirements[package]}")
    
    if unused_packages:
        print("The following packages might be unused (but check carefully as they might be dependencies):")
        for pkg in unused_packages:
            print(pkg)
    else:
        print("No unused packages found!")

    print("\nSummary:")
    print(f"Total requirements: {len(requirements)}")
    print(f"Directly imported packages: {len(used_imports)}")
    print(f"Total dependencies (including indirect): {len(all_dependencies)}")

if __name__ == '__main__':
    main() 