#!/usr/bin/env python3
"""Create, validate and project Superflow specs without running project work."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from superflow_model import (
    CONFIG_PATH, SOURCE_NAMES, ContentError, SourceError, build_snapshot,
    ensure_unchanged, has_errors, parse_json, read_sources, resolve_specs_root,
    validate_spec, yaml,
)

PLUGIN = Path(__file__).resolve().parents[1]


def atomic_write(path, text, root, sources):
    path = Path(path).expanduser().resolve()
    root = Path(root).resolve()
    if path.name in SOURCE_NAMES or path == root / CONFIG_PATH or path in {
        root / key for key in sources
    }:
        raise SourceError("Saída não pode sobrescrever uma fonte.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix="." + path.name + ".", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        ensure_unchanged(root, sources)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def create_spec(root, slug, title, summary):
    if not re.fullmatch(r"[a-z0-9][a-z0-9._/-]*", slug) or any(
        part in {"", ".", ".."} or part.startswith(".") for part in slug.split("/")
    ):
        raise ContentError("Slug deve conter nomes relativos simples, sem . ou ..")
    if not title.strip():
        raise ContentError("Título não pode ser vazio.")
    if not summary.strip():
        raise ContentError("Resumo não pode ser vazio.")
    root, specs, _ = resolve_specs_root(root)
    snapshot, sources = build_snapshot(root)
    if has_errors(snapshot):
        raise ContentError("Corrija os status inválidos antes de criar outro ID.")
    if any(record["id"] == slug for record in snapshot["records"]):
        raise ContentError("ID já cadastrado: " + slug)
    target = (specs / slug).resolve()
    try:
        target.relative_to(specs)
    except ValueError as exc:
        raise ContentError("Destino fora de specs_root.") from exc
    if target.exists():
        raise ContentError("Destino já existe: " + str(target))
    status = {"id": slug, "title": title.strip(), "summary": summary.strip(), "status": "pending"}
    prd_template = (PLUGIN / "assets/templates/PRD.md").read_text(encoding="utf-8")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".superflow-new-", dir=target.parent) as temp:
        stage = Path(temp) / "package"
        stage.mkdir()
        (stage / "status.md").write_text(
            "---\n" + yaml.safe_dump(status, allow_unicode=True, sort_keys=False) + "---\n",
            encoding="utf-8",
        )
        (stage / "PRD.md").write_text(
            prd_template.replace("{{title}}", title.strip()), encoding="utf-8",
        )
        ensure_unchanged(root, sources)
        target.mkdir()
        try:
            os.replace(stage, target)
        except OSError:
            target.rmdir()
            raise
    return target


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--version", action="version", version=json.loads(
        (PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )["version"])
    commands = parser.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="Criar PRD e status iniciais.")
    new.add_argument("slug")
    new.add_argument("--title", required=True)
    new.add_argument("--summary", required=True)

    check = commands.add_parser("check", help="Validar um limite explícito.")
    checks = check.add_subparsers(dest="check_scope", required=True)
    checks.add_parser("status", help="Validar somente a coleção de status.")
    spec = checks.add_parser("spec", help="Validar fontes obrigatórias e artefatos condicionais existentes.")
    spec.add_argument("spec")

    for name in ("feed", "qg"):
        command = commands.add_parser(name)
        command.add_argument("--output", type=Path)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = args.root.expanduser().resolve()
    try:
        if args.command == "new":
            print("Criado: " + str(create_spec(root, args.slug, args.title, args.summary)))
            return 0
        if args.command == "check" and args.check_scope == "spec":
            print("Spec válida: " + str(validate_spec(root, args.spec)))
            return 0

        snapshot, sources = build_snapshot(root)
        if args.command == "feed":
            output = args.output or root / ".superflow/feed.json"
            atomic_write(output, json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", root, sources)
            print("Gerado: " + str(output))
        elif args.command == "qg":
            from superflow_qg import render
            output = args.output or root / ".superflow/qg.html"
            atomic_write(output, render(snapshot), root, sources)
            print("Gerado: " + str(output))
        else:
            ensure_unchanged(root, sources)
        for item in snapshot["diagnostics"]:
            print("{severity}: {path}: {code}: {message}".format(**item), file=sys.stderr)
        print("{} specs; {} diagnósticos; snapshot {}".format(
            len(snapshot["records"]), len(snapshot["diagnostics"]), snapshot["snapshot_id"][:12]
        ))
        return 1 if has_errors(snapshot) else 0
    except ContentError as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 1
    except (SourceError, OSError, UnicodeError) as exc:
        print("operational_error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
