"""
Generate API reference documentation from source code.

This script extracts docstrings and type hints from vmkis modules
and generates markdown documentation.
"""

import ast
import inspect
import os
from pathlib import Path
from typing import Any, List, Dict


def extract_module_info(module_path: Path) -> Dict[str, Any]:
    """Extract classes, functions, and their docstrings from a Python module."""
    with open(module_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node) or "(No docstring)"
            methods = []

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if not item.name.startswith("_"):  # Public methods only
                        method_doc = ast.get_docstring(item) or ""
                        methods.append({
                            "name": item.name,
                            "docstring": method_doc.split("\n")[0] if method_doc else ""
                        })

            classes.append({
                "name": node.name,
                "docstring": docstring,
                "methods": methods
            })

        elif isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):  # Public functions only
                docstring = ast.get_docstring(node) or "(No docstring)"
                functions.append({
                    "name": node.name,
                    "docstring": docstring
                })

    return {"classes": classes, "functions": functions}


def generate_markdown(modules: Dict[str, Dict[str, Any]]) -> str:
    """Generate markdown documentation from extracted module info."""
    md = ["# API Reference\n\n"]
    md.append("자동 생성된 API 레퍼런스 문서입니다.\n\n")
    md.append("---\n\n")
    md.append("## 목차\n\n")

    # Table of contents
    for module_name in sorted(modules.keys()):
        md.append(f"- [{module_name}](#{module_name.replace('.', '-')})\n")

    md.append("\n---\n\n")

    # Module details
    for module_name, info in sorted(modules.items()):
        md.append(f"## {module_name}\n\n")

        if info["classes"]:
            md.append("### Classes\n\n")
            for cls in info["classes"]:
                md.append(f"#### `{cls['name']}`\n\n")
                md.append(f"{cls['docstring']}\n\n")

                if cls["methods"]:
                    md.append("**Methods:**\n\n")
                    for method in cls["methods"]:
                        md.append(f"- `{method['name']}()`: {method['docstring']}\n")
                    md.append("\n")

        if info["functions"]:
            md.append("### Functions\n\n")
            for func in info["functions"]:
                md.append(f"#### `{func['name']}()`\n\n")
                md.append(f"{func['docstring']}\n\n")

        md.append("---\n\n")

    return "".join(md)


def main():
    """Main entry point for API reference generation."""
    repo_root = Path(__file__).parent.parent
    # src 레이아웃: 패키지는 repo_root/src/vmkis 에 있습니다.
    vmkis_dir = repo_root / "src" / "vmkis"

    # Target modules for API reference (public API only)
    target_files = [
        "kis.py",
        "simple.py",
        "helpers.py",
        "public_types.py",
        "client/auth.py",
    ]

    modules = {}

    for file_path in target_files:
        full_path = vmkis_dir / file_path
        if full_path.exists():
            module_name = f"vmkis.{file_path.replace('.py', '').replace('/', '.')}"
            modules[module_name] = extract_module_info(full_path)

    # Generate markdown
    md_content = generate_markdown(modules)

    # Write to file
    output_path = repo_root / "docs" / "generated" / "API_REFERENCE.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ API Reference generated: {output_path}")


if __name__ == "__main__":
    main()
