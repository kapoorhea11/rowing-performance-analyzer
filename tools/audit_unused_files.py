"""
Find project Python files that are not imported, directly or indirectly,
by main.py or dashboard/app.py.

This is a static audit. Review flagged files before deleting them because
Python can also load files dynamically.
"""

import ast
from pathlib import Path
from typing import Dict, Set


PROJECT_ROOT = Path(__file__).resolve().parent

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    ".venv-1",
    "venv",
    "env",
    "archive",
    "outputs",
    "__pycache__",
}

ENTRY_MODULES = {
    "main",
    "dashboard.app",
}


def should_ignore(path: Path) -> bool:
    """Return True when a path is inside an ignored directory."""
    return any(part in IGNORED_DIRECTORIES for part in path.parts)


def path_to_module(path: Path) -> str:
    """Convert a Python file path to its dotted module name."""
    relative_path = path.relative_to(PROJECT_ROOT)

    if relative_path.name == "__init__.py":
        parts = relative_path.parent.parts
    else:
        parts = relative_path.with_suffix("").parts

    return ".".join(parts)


def find_python_files() -> Dict[str, Path]:
    """Return all project Python modules and their paths."""
    modules = {}

    for path in PROJECT_ROOT.rglob("*.py"):
        if should_ignore(path):
            continue

        if path.name == "audit_unused_files.py":
            continue

        module_name = path_to_module(path)

        if module_name:
            modules[module_name] = path

    return modules


def resolve_relative_import(
    current_module: str,
    imported_module: str,
    level: int,
) -> str:
    """Resolve a relative import into an absolute project module."""
    current_parts = current_module.split(".")

    # A normal Python file is considered inside its containing package.
    package_parts = current_parts[:-1]

    if level > 0:
        keep_count = len(package_parts) - level + 1
        keep_count = max(keep_count, 0)
        base_parts = package_parts[:keep_count]
    else:
        base_parts = []

    imported_parts = (
        imported_module.split(".")
        if imported_module
        else []
    )

    return ".".join(base_parts + imported_parts)


def parse_imports(
    module_name: str,
    file_path: Path,
    known_modules: Set[str],
) -> Set[str]:
    """Find project modules imported by one Python file."""
    imports = set()

    try:
        source = file_path.read_text(encoding="utf-8")
        syntax_tree = ast.parse(source, filename=str(file_path))
    except (OSError, SyntaxError, UnicodeDecodeError) as error:
        print(f"Could not inspect {file_path}: {error}")
        return imports

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_name = alias.name

                for known_module in known_modules:
                    if (
                        known_module == imported_name
                        or known_module.startswith(
                            imported_name + "."
                        )
                    ):
                        imports.add(known_module)

        elif isinstance(node, ast.ImportFrom):
            imported_base = node.module or ""

            if node.level:
                imported_base = resolve_relative_import(
                    current_module=module_name,
                    imported_module=imported_base,
                    level=node.level,
                )

            if imported_base in known_modules:
                imports.add(imported_base)

            for alias in node.names:
                possible_module = ".".join(
                    part
                    for part in [
                        imported_base,
                        alias.name,
                    ]
                    if part
                )

                if possible_module in known_modules:
                    imports.add(possible_module)

    return imports


def find_reachable_modules(
    dependency_graph: Dict[str, Set[str]],
) -> Set[str]:
    """Find every module reachable from the entry modules."""
    reachable = set()
    stack = [
        module
        for module in ENTRY_MODULES
        if module in dependency_graph
    ]

    while stack:
        current_module = stack.pop()

        if current_module in reachable:
            continue

        reachable.add(current_module)

        for dependency in dependency_graph.get(
            current_module,
            set(),
        ):
            if dependency not in reachable:
                stack.append(dependency)

    return reachable


def main() -> None:
    modules = find_python_files()
    known_modules = set(modules)

    dependency_graph = {
        module_name: parse_imports(
            module_name=module_name,
            file_path=file_path,
            known_modules=known_modules,
        )
        for module_name, file_path in modules.items()
    }

    reachable = find_reachable_modules(
        dependency_graph
    )

    unreachable = sorted(
        known_modules - reachable
    )

    print("\n" + "=" * 70)
    print("ENTRY POINTS")
    print("=" * 70)

    for module in sorted(ENTRY_MODULES):
        status = (
            "found"
            if module in known_modules
            else "NOT FOUND"
        )
        print(f"{module}: {status}")

    print("\n" + "=" * 70)
    print("FILES USED BY MAIN.PY OR DASHBOARD/APP.PY")
    print("=" * 70)

    for module in sorted(reachable):
        print(modules[module].relative_to(PROJECT_ROOT))

    print("\n" + "=" * 70)
    print("FILES NOT REACHED FROM EITHER ENTRY POINT")
    print("=" * 70)

    if not unreachable:
        print("None found.")
    else:
        for module in unreachable:
            print(modules[module].relative_to(PROJECT_ROOT))

    print("\nImportant:")
    print(
        "A listed file is a candidate for review, "
        "not automatic proof that it is safe to delete."
    )


if __name__ == "__main__":
    main()