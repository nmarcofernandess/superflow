#!/usr/bin/env python3
"""Sync this Superflow plugin source into the personal marketplace plugin path."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PLUGIN_NAME = "superflow"
SOURCE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = Path.home() / "plugins" / PLUGIN_NAME
MARKETPLACE = "personal"


def copy_tree(source: Path, target: Path) -> None:
    ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store")
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True, ignore=ignore)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(DEFAULT_TARGET))
    parser.add_argument("--install", action="store_true", help="Run codex plugin add after sync.")
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    copy_tree(SOURCE_ROOT, target)

    if not args.skip_validation:
        run([sys.executable, str(target / "scripts" / "validate_superflow.py"), str(target), "--mermaid"])
        run([sys.executable, str(target / "scripts" / "test_superflow_routes.py")])
        run([sys.executable, str(target / "scripts" / "forward_test_superflow.py")])

    if args.install:
        run(["codex", "plugin", "add", f"{PLUGIN_NAME}@{MARKETPLACE}"])

    print(f"OK: synced {SOURCE_ROOT} -> {target}")
    if args.install:
        print(f"OK: installed {PLUGIN_NAME}@{MARKETPLACE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
