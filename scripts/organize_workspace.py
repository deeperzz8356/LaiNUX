from __future__ import annotations

import argparse
import shutil
from pathlib import Path


# Files that should stay in the repository root.
ROOT_KEEP_FILES = {
    ".env",
    ".gitignore",
    ".python-version",
    "README.md",
    "agent_memory.db",
    "deep",
}

# Known target folders in the organized layout.
TARGET_DIRS = {
    "scripts": "Utility and helper Python scripts",
    "docs": "Documentation and notes",
    "config": "Container and deployment configuration",
    "tmp": "Temporary and runtime-generated files",
}

# Explicit file mapping to avoid accidental moves.
FILE_DESTINATION_MAP = {
    # scripts/
    "check_models.py": "scripts",
    "durgesh.py": "scripts",
    "fix_file_tools.py": "scripts",
    "input_parser.py": "scripts",
    "monitor_session.py": "scripts",
    "peek_model.py": "scripts",
    "prime_number.py": "scripts",
    "secure_delete.py": "scripts",
    "test_mimic_os.py": "scripts",
    "test_model.py": "scripts",
    "test_port.py": "scripts",
    "test_uvicorn.py": "scripts",
    "zip_tool.py": "scripts",
    # docs/
    "ARCHITECTURE_WALKTHROUGH.md": "docs",
    "memory_wisdom_nuggets.json": "docs",
    "Wisdom_Nuggets.txt": "docs",
    "wisdom_nuggets_ai_trends.txt": "docs",
    # config/
    "Dockerfile": "config",
    "docker-compose.yml": "config",
    # tmp/
    "debug_log.txt": "tmp",
    "error_log.txt": "tmp",
    "secure_deletion_test.txt": "tmp",
    "temp.txt": "tmp",
}


def move_file(src: Path, dst_dir: Path, dry_run: bool) -> str:
    dst = dst_dir / src.name
    if src.resolve() == dst.resolve():
        return f"SKIP {src} (already in correct location)"

    if dst.exists():
        return f"SKIP {src} (destination exists: {dst})"

    if dry_run:
        return f"DRY  {src} -> {dst}"

    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return f"MOVE {src} -> {dst}"


def ensure_dirs(root: Path, dry_run: bool) -> list[str]:
    logs: list[str] = []
    for dirname in TARGET_DIRS:
        target = root / dirname
        if target.exists():
            logs.append(f"SKIP {target} (already exists)")
            continue
        if dry_run:
            logs.append(f"DRY  create {target}")
        else:
            target.mkdir(parents=True, exist_ok=True)
            logs.append(f"MAKE {target}")
    return logs


def organize(root: Path, dry_run: bool) -> list[str]:
    logs = ensure_dirs(root, dry_run)

    # Keep os_root directory and all existing project folders untouched.
    protected_dirs = {
        ".git",
        ".github",
        ".vscode",
        ".venv310",
        "venv",
        "agentic_os",
        "os_root",
        "logs",
        "tests",
        "sandbox",
        "scripts",
        "docs",
        "config",
        "tmp",
        "__pycache__",
        ".pytest_cache",
    }

    for item in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if item.is_dir():
            if item.name in protected_dirs:
                continue
            logs.append(f"SKIP {item} (unmapped directory)")
            continue

        if item.name in ROOT_KEEP_FILES:
            logs.append(f"KEEP {item}")
            continue

        target_name = FILE_DESTINATION_MAP.get(item.name)
        if not target_name:
            logs.append(f"SKIP {item} (no mapping)")
            continue

        target_dir = root / target_name
        logs.append(move_file(item, target_dir, dry_run))

    return logs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create and enforce LaiNUX folder organization."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Workspace root path. Defaults to parent of this script.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without moving files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve() if args.root else Path(__file__).resolve().parent.parent

    if not root.exists() or not root.is_dir():
        print(f"ERROR: Invalid root path: {root}")
        return 1

    print(f"Workspace root: {root}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'APPLY'}")
    print("-" * 60)

    logs = organize(root, args.dry_run)
    for line in logs:
        print(line)

    print("-" * 60)
    moved = sum(1 for line in logs if line.startswith("MOVE"))
    created = sum(1 for line in logs if line.startswith("MAKE"))
    print(f"Summary: moved={moved}, dirs_created={created}, actions={len(logs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
