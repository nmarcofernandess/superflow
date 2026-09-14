#!/usr/bin/env python3
"""Validate the public Superflow plugin surface without reading a consumer repo."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Set
from urllib.parse import unquote, urlsplit


SKILLS = {
    "superflow",
    "prd",
    "analyst",
    "build",
    "plan",
    "review",
    "status",
}
PLAYBOOKS = {
    "capture.md",
    "feature.md",
    "retomar.md",
    "fechar.md",
    "reconciliar.md",
}
CONTRACTS = {
    "state-contract.md",
    "commands-contract.md",
    "quality-contract.md",
}
TEMPLATES = {
    "PRD.md",
    "status.md",
    "SPEC.md",
    "plan.json",
}
RUNTIME_FILES = {
    "scripts/superflow.py",
    "scripts/superflow_model.py",
    "scripts/superflow_qg.py",
    "scripts/validate_superflow.py",
    "scripts/sync_personal_install.py",
    "scripts/vendor/PyYAML-LICENSE",
    "scripts/vendor/PyYAML-SOURCE.json",
    "scripts/vendor/yaml/__init__.py",
    "assets/qg.html",
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def listed_names(path: Path, *, directories: bool) -> Set[str]:
    if not path.is_dir():
        return set()
    return {
        child.name
        for child in path.iterdir()
        if child.is_dir()
    } if directories else {
        child.name
        for child in path.iterdir()
        if child.is_file()
    }


def validate_expected_set(errors: List[str], path: Path, expected: Set[str], label: str, directories: bool) -> None:
    actual = listed_names(path, directories=directories)
    if actual != expected:
        errors.append(
            "{} deve conter exatamente {} (encontrado: {})".format(
                label,
                ", ".join(sorted(expected)),
                ", ".join(sorted(actual)) if actual else "vazio",
            )
        )


def validate_json(path: Path, errors: List[str]) -> Optional[dict]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append("JSON inválido em {}: {}".format(path, exc))
        return None
    if not isinstance(value, dict):
        errors.append("{} deve conter um objeto JSON".format(path))
        return None
    return value


def validate_manifest(plugin: Path, errors: List[str]) -> None:
    codex_path = plugin / ".codex-plugin/plugin.json"
    claude_path = plugin / ".claude-plugin/plugin.json"
    for path in (codex_path, claude_path):
        if not path.is_file():
            errors.append("Manifesto ausente: {}".format(path.relative_to(plugin)))
            continue
        manifest = validate_json(path, errors)
        if manifest is None:
            continue
        if manifest.get("name") != "superflow":
            errors.append("{} deve declarar name superflow".format(path.relative_to(plugin)))
        if manifest.get("version") != "0.9.3":
            errors.append("{} deve declarar version 0.9.3".format(path.relative_to(plugin)))
        if manifest.get("skills") != "./skills/":
            errors.append("{} deve apontar skills para ./skills/".format(path.relative_to(plugin)))


def local_link_target(source: Path, plugin: Path, raw_target: str) -> Optional[Path]:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if not target or target.startswith("#"):
        return None
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None
    path_text = unquote(target.split("#", 1)[0]).strip()
    if not path_text:
        return None
    candidate = (source.parent / path_text).resolve()
    try:
        candidate.relative_to(plugin.resolve())
    except ValueError as exc:
        raise ValueError("link fora do plugin: {}".format(raw_target)) from exc
    return candidate


def markdown_documents(plugin: Path) -> Iterable[Path]:
    for skill in sorted(SKILLS):
        yield plugin / "skills" / skill / "SKILL.md"
    for name in sorted(PLAYBOOKS):
        yield plugin / "assets/playbooks" / name
    for name in sorted(CONTRACTS):
        yield plugin / "assets/references" / name
    for name in sorted(TEMPLATES - {"plan.json"}):
        yield plugin / "assets/templates" / name


def validate_local_links(plugin: Path, errors: List[str]) -> None:
    for document in markdown_documents(plugin):
        if not document.is_file():
            continue
        try:
            text = document.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append("Não foi possível ler {}: {}".format(document.relative_to(plugin), exc))
            continue
        for raw_target in MARKDOWN_LINK.findall(text):
            try:
                target = local_link_target(document, plugin, raw_target)
            except ValueError as exc:
                errors.append("{}: {}".format(document.relative_to(plugin), exc))
                continue
            if target is not None and not target.exists():
                errors.append(
                    "{}: link relativo ausente: {}".format(
                        document.relative_to(plugin), raw_target
                    )
                )


def validate_plugin(plugin: Path) -> List[str]:
    plugin = plugin.expanduser().resolve()
    errors: List[str] = []
    if not plugin.is_dir():
        return ["Plugin inexistente: {}".format(plugin)]

    validate_manifest(plugin, errors)
    validate_expected_set(errors, plugin / "skills", SKILLS, "skills", directories=True)
    validate_expected_set(
        errors, plugin / "assets/playbooks", PLAYBOOKS, "assets/playbooks", directories=False
    )
    validate_expected_set(
        errors, plugin / "assets/references", CONTRACTS, "assets/references", directories=False
    )
    validate_expected_set(
        errors, plugin / "assets/templates", TEMPLATES, "assets/templates", directories=False
    )
    for relative_path in sorted(RUNTIME_FILES):
        if not (plugin / relative_path).is_file():
            errors.append("Arquivo runtime ausente: {}".format(relative_path))
    for skill in sorted(SKILLS):
        path = plugin / "skills" / skill / "SKILL.md"
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            errors.append("Skill ausente ou vazia: skills/{}/SKILL.md".format(skill))
    validate_local_links(plugin, errors)
    return errors


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin", type=Path, help="Diretório plugins/superflow")
    args = parser.parse_args(argv)
    errors = validate_plugin(args.plugin)
    if errors:
        print("Superflow inválido:", file=sys.stderr)
        for error in errors:
            print("- {}".format(error), file=sys.stderr)
        return 1
    print("Superflow structure: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
