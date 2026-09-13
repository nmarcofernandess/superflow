#!/usr/bin/env python3
"""Create, check and project specs using one shared model (Python 3.9+)."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from superflow_model import (
    CONFIG_PATH, SOURCE_NAMES, ContentError, SourceError, build_snapshot, ensure_unchanged,
    has_errors, parse_json, read_sources, utc_now, yaml,
)

PLUGIN = Path(__file__).resolve().parents[1]


def atomic_write(path, text, root, sources):
    path = Path(path).expanduser().resolve()
    if (path.name in SOURCE_NAMES or path == Path(root).resolve() / CONFIG_PATH
            or path in {(Path(root).resolve() / key) for key in sources}):
        raise SourceError("Saída não pode sobrescrever uma fonte.")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix="." + path.name + ".", delete=False) as stream:
            tmp = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        ensure_unchanged(root, sources)
        os.replace(tmp, path)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def create_spec(root, slug, title):
    if not re.fullmatch(r"[a-z0-9][a-z0-9._/-]*", slug) or any(
        part in {"", ".", ".."} or part.startswith(".") for part in slug.split("/")
    ):
        raise ContentError("Slug deve conter nomes relativos simples, sem . ou ..")
    if not title.strip():
        raise ContentError("Título não pode ser vazio.")
    snapshot, sources = build_snapshot(root)
    if has_errors(snapshot):
        raise ContentError("Corrija os registros inválidos antes de criar outro ID.")
    identifier = slug
    if any(r["id"] == identifier for r in snapshot["records"]):
        raise ContentError("ID já cadastrado: " + identifier)
    config = parse_json(sources[CONFIG_PATH].decode()) if CONFIG_PATH in sources else {}
    specs = (root / config.get("specs_root", "specs")).resolve()
    target = (specs / slug).resolve()
    try:
        target.relative_to(specs)
    except ValueError as exc:
        raise ContentError("Destino fora de specs_root.") from exc
    if target.exists():
        raise ContentError("Destino já existe: " + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    data = {"id": identifier, "title": title, "phase": "inbox", "state": "pending",
            "prd": "gathering", "updated_at": utc_now()}
    with tempfile.TemporaryDirectory(prefix=".superflow-new-", dir=target.parent) as temp:
        stage = Path(temp) / "package"
        stage.mkdir()
        (stage / "status.md").write_text(
            "---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---\n", encoding="utf-8")
        prd = (PLUGIN / "assets/templates/PRD.md").read_text(encoding="utf-8")
        (stage / "PRD.md").write_text(prd.replace("{{title}}", title), encoding="utf-8")
        ensure_unchanged(root, sources)
        # Reserve the name exclusively; replace only our own empty reservation.
        target.mkdir()
        try:
            os.replace(stage, target)
        except OSError:
            target.rmdir()
            raise
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--version", action="version", version=json.loads(
        (PLUGIN / ".codex-plugin/plugin.json").read_text())["version"])
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new", help="Criar status e PRD inicial.")
    new.add_argument("slug")
    new.add_argument("--title", required=True)
    commands.add_parser("check", help="Validar fontes sem alterar arquivos.")
    for name in ("feed", "qg"):
        commands.add_parser(name).add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    try:
        if args.command == "new":
            target = create_spec(root, args.slug, args.title)
            print("Criado: " + str(target))
            return 0
        snapshot, sources = build_snapshot(root)
        if args.command != "check":
            if args.command == "feed":
                content = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
                default = root / ".superflow/feed.json"
            else:
                from superflow_qg import render
                content = render(snapshot, root)
                default = root / ".superflow/qg.html"
            output = args.output or default
            atomic_write(output, content, root, sources)
            print("Gerado: " + str(output))
        else:
            ensure_unchanged(root, sources)
        for item in snapshot["diagnostics"]:
            print("{severity}: {path}: {code}: {message}".format(**item), file=sys.stderr)
        print("{} specs; {} diagnósticos; snapshot {}".format(
            len(snapshot["records"]), len(snapshot["diagnostics"]), snapshot["snapshot_id"][:12]))
        return 1 if has_errors(snapshot) else 0
    except ContentError as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 1
    except (SourceError, OSError, UnicodeError) as exc:
        print("operational_error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
