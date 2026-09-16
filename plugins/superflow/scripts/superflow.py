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
    ensure_unchanged, parse_json, read_sources, resolve_specs_root, status_id_counts,
    validate_spec, yaml,
)

PLUGIN = Path(__file__).resolve().parents[1]


def emit_diagnostics(items):
    for item in items:
        print("{severity}: {path}: {code}: {message}".format(**item), file=sys.stderr)


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
    if slug in status_id_counts(sources):
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
    return target, snapshot["diagnostics"]


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
        if name == "qg":
            command.add_argument("--online", metavar="FEED_URL", help="Gerar HTML que consulta um feed HTTP(S).")
            command.add_argument("--refresh", type=Path, nargs="+", metavar="HTML", help="Atualizar componentes de HTMLs existentes como exports offline.")
            command.add_argument("--source", help="Selecionar os componentes pelo src exato durante --refresh.")
            command.add_argument("--embed", action="store_true", help="Gerar fragmento HTML isolado com Shadow DOM.")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    if args.command == "qg":
        if args.refresh and (args.output or args.embed or args.online):
            parser.error("--refresh não combina com --output, --embed ou --online.")
        if args.source is not None and not args.refresh:
            parser.error("--source seleciona componentes para --refresh.")
    try:
        if args.command == "new":
            target, diagnostics = create_spec(root, args.slug, args.title, args.summary)
            emit_diagnostics(diagnostics)
            print("Criado: " + str(target))
            if diagnostics:
                print("{} diagnóstico{} existente{}".format(
                    len(diagnostics), "" if len(diagnostics) == 1 else "s",
                    "" if len(diagnostics) == 1 else "s",
                ))
            return 0
        if args.command == "check" and args.check_scope == "spec":
            try:
                target = validate_spec(root, args.spec)
            except ContentError as exc:
                print(
                    "warning: {}: INVALID_SPEC: {}".format(args.spec, exc),
                    file=sys.stderr,
                )
                print("Spec com diagnóstico: " + str(args.spec))
                return 0
            print("Spec sem diagnósticos: " + str(target))
            return 0

        snapshot, sources = build_snapshot(root)
        if args.command in {"feed", "qg"}:
            from superflow_qg import component_script, refresh_html, render, render_embed
            feed_path = (args.output if args.command == "feed" else None) or root / ".superflow/feed.json"
            outputs = [(feed_path, json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"),
                       (feed_path.parent / "qg.js", component_script())]
            if args.command == "qg":
                if args.refresh:
                    for path in args.refresh:
                        path = path.expanduser().resolve()
                        outputs.append((path, refresh_html(path.read_bytes().decode("utf-8"), snapshot, args.source)))
                else:
                    output = args.output or root / ".superflow/qg.html"
                    renderer = render_embed if args.embed else render
                    outputs.append((output, renderer(snapshot, source=args.online)))
            paths = [path.expanduser().resolve() for path, _ in outputs]
            if len(paths) != len(set(paths)):
                raise SourceError("Destinos de saída precisam ser distintos.")
            for path in paths:
                if path.name in SOURCE_NAMES or path == root / CONFIG_PATH or path in {root / key for key in sources}:
                    raise SourceError("Saída não pode sobrescrever uma fonte.")
            for path, content in outputs:
                atomic_write(path, content, root, sources)
                print("Gerado: " + str(path))
        else:
            ensure_unchanged(root, sources)
        emit_diagnostics(snapshot["diagnostics"])
        print("{} specs; {} diagnósticos; snapshot {}".format(
            len(snapshot["records"]), len(snapshot["diagnostics"]), snapshot["snapshot_id"][:12]
        ))
        return 0
    except ContentError as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 1
    except (SourceError, OSError, UnicodeError) as exc:
        print("operational_error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
