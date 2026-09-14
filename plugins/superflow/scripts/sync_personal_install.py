#!/usr/bin/env python3
"""Safely update a personal Superflow plugin install from this source tree."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


PLUGIN_NAME = "superflow"
SOURCE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = Path.home() / "plugins" / PLUGIN_NAME
MARKETPLACE = "personal"

# These are the only paths this installer writes from the source. Tests and
# retired executors never enter an installed plugin by accident.
MANAGED_FILES = (
    Path("README.md"),
    Path(".codex-plugin/plugin.json"),
    Path(".claude-plugin/plugin.json"),
    Path("assets/qg.html"),
    Path("scripts/superflow.py"),
    Path("scripts/superflow_model.py"),
    Path("scripts/superflow_qg.py"),
    Path("scripts/validate_superflow.py"),
    Path("scripts/sync_personal_install.py"),
)
MANAGED_TREES = (
    Path("skills"),
    Path("assets/playbooks"),
    Path("assets/references"),
    Path("assets/templates"),
    Path("scripts/vendor"),
)

# These were shipped by the former plugin and are safe to remove only because
# their exact paths identify them as managed residues. Unknown files survive.
LEGACY_MANAGED_PATHS = (
    Path("skills/audit/SKILL.md"),
    Path("skills/backlog-status/SKILL.md"),
    Path("skills/campaign/SKILL.md"),
    Path("skills/capture/SKILL.md"),
    Path("skills/execute/SKILL.md"),
    Path("skills/explain-clearly/SKILL.md"),
    Path("skills/gauntlet-loop/SKILL.md"),
    Path("skills/grill-me/SKILL.md"),
    Path("skills/grill-with-docs/ADR-FORMAT.md"),
    Path("skills/grill-with-docs/CONTEXT-FORMAT.md"),
    Path("skills/grill-with-docs/SKILL.md"),
    Path("skills/html-didatico/SKILL.md"),
    Path("skills/html-didatico/references/receita.md"),
    Path("skills/qa/SKILL.md"),
    Path("skills/qg/SKILL.md"),
    Path("skills/rota/SKILL.md"),
    Path("skills/taskgen/SKILL.md"),
    Path("skills/warlog/SKILL.md"),
    Path("skills/writing-clearly-and-concisely/SKILL.md"),
    Path("skills/writing-clearly-and-concisely/elements-of-style.md"),
    Path("assets/examples/capture-issue.md"),
    Path("assets/examples/deep-build-prd.md"),
    Path("assets/examples/forensic-investigation.md"),
    Path("assets/examples/lean-local-prd.md"),
    Path("assets/fixtures/campaign/001-foundation/PRD.md"),
    Path("assets/fixtures/campaign/001-foundation/progress.md"),
    Path("assets/fixtures/campaign/001-foundation/status.json"),
    Path("assets/fixtures/campaign/002-consumer/PRD.md"),
    Path("assets/fixtures/campaign/002-consumer/progress.md"),
    Path("assets/fixtures/campaign/002-consumer/status.json"),
    Path("assets/fixtures/campaign/003-polish/PRD.md"),
    Path("assets/fixtures/campaign/003-polish/progress.md"),
    Path("assets/fixtures/campaign/003-polish/status.json"),
    Path("assets/fixtures/mindset/coverage.json"),
    Path("assets/fixtures/mindset/deep/PRD.md"),
    Path("assets/fixtures/mindset/deep/SPEC.md"),
    Path("assets/fixtures/mindset/deep/analysis.md"),
    Path("assets/fixtures/mindset/deep/mindset-depth.txt"),
    Path("assets/fixtures/mindset/deep/progress.md"),
    Path("assets/fixtures/mindset/deep/status.json"),
    Path("assets/fixtures/mindset/docs-only/PRD.md"),
    Path("assets/fixtures/mindset/docs-only/SPEC.md"),
    Path("assets/fixtures/mindset/docs-only/analysis.md"),
    Path("assets/fixtures/mindset/docs-only/mindset-depth.txt"),
    Path("assets/fixtures/mindset/docs-only/progress.md"),
    Path("assets/fixtures/mindset/docs-only/status.json"),
    Path("assets/fixtures/mindset/empty-headings-fail/PRD.md"),
    Path("assets/fixtures/mindset/empty-headings-fail/SPEC.md"),
    Path("assets/fixtures/mindset/empty-headings-fail/analysis.md"),
    Path("assets/fixtures/mindset/empty-headings-fail/mindset-depth.txt"),
    Path("assets/fixtures/mindset/empty-headings-fail/progress.md"),
    Path("assets/fixtures/mindset/empty-headings-fail/status.json"),
    Path("assets/fixtures/mindset/string-trap/PRD.md"),
    Path("assets/fixtures/mindset/string-trap/SPEC.md"),
    Path("assets/fixtures/mindset/string-trap/analysis.md"),
    Path("assets/fixtures/mindset/string-trap/mindset-depth.txt"),
    Path("assets/fixtures/mindset/string-trap/progress.md"),
    Path("assets/fixtures/mindset/string-trap/status.json"),
    Path("assets/fixtures/review/reviewed/PRD.md"),
    Path("assets/fixtures/review/reviewed/implementation_log.json"),
    Path("assets/fixtures/review/reviewed/implementation_plan.json"),
    Path("assets/fixtures/review/reviewed/progress.md"),
    Path("assets/fixtures/review/reviewed/review_log.json"),
    Path("assets/fixtures/review/reviewed/status.json"),
    Path("assets/fixtures/rota/plano-valido.json"),
    Path("assets/fixtures/warlog/campaign/PRD.md"),
    Path("assets/fixtures/warlog/campaign/WARLOG.md"),
    Path("assets/fixtures/warlog/campaign/progress.md"),
    Path("assets/fixtures/warlog/campaign/status.json"),
    Path("assets/task-board/board-data.example.js"),
    Path("assets/task-board/board.html"),
    Path("assets/playbooks/README.md"),
    Path("assets/playbooks/grill-loop.md"),
    Path("assets/playbooks/jornada-superflow.md"),
    Path("assets/playbooks/migracao.md"),
    Path("assets/playbooks/pesquisa.md"),
    Path("assets/playbooks/revisao.md"),
    Path("assets/references/analyst-protocol.md"),
    Path("assets/references/backlog-status-protocol.md"),
    Path("assets/references/build-protocol.md"),
    Path("assets/references/campaign-contract.md"),
    Path("assets/references/code-recon-protocol.md"),
    Path("assets/references/execution-contract.md"),
    Path("assets/references/feature-mindset-contract.md"),
    Path("assets/references/github-issue-contract.md"),
    Path("assets/references/lifecycle-contract.md"),
    Path("assets/references/mermaid-contract.md"),
    Path("assets/references/prd-contract.md"),
    Path("assets/references/reuse-guard-protocol.md"),
    Path("assets/references/review-contract.md"),
    Path("assets/references/rota-contract.md"),
    Path("assets/references/routing-protocol.md"),
    Path("assets/references/status-schema.md"),
    Path("assets/references/tdd-contract.md"),
    Path("assets/references/technical-blueprint-protocol.md"),
    Path("assets/references/warlog-contract.md"),
    Path("assets/templates/ISSUE_PRD.md"),
    Path("assets/templates/analysis.md"),
    Path("assets/templates/technical_blueprint.md"),
    Path("assets/templates/WARLOG.md"),
    Path("assets/templates/implementation_log.json"),
    Path("assets/templates/implementation_plan.json"),
    Path("assets/templates/implementation_plan.md"),
    Path("assets/templates/plano.json"),
    Path("assets/templates/progress.md"),
    Path("assets/templates/qa_report.md"),
    Path("assets/templates/review_log.json"),
    Path("scripts/superflow_audit.py"),
    Path("scripts/superflow_campaign.py"),
    Path("scripts/superflow_github.py"),
    Path("scripts/superflow_rota.py"),
    Path("scripts/superflow_status.py"),
    Path("scripts/superflow_taskgen.py"),
    Path("scripts/superflow_warlog.py"),
    Path("scripts/forward_test_superflow.py"),
    Path("scripts/test_campaign_contract.py"),
    Path("scripts/test_feature_mindset.py"),
    Path("scripts/test_handbook_contract.py"),
    Path("scripts/test_lifecycle_contract.py"),
    Path("scripts/test_review_contract.py"),
    Path("scripts/test_rota_contract.py"),
    Path("scripts/test_superflow_routes.py"),
    Path("scripts/test_tdd_contract.py"),
    Path("scripts/test_warlog_contract.py"),
    Path("scripts/test_writing_contract.py"),
    Path("scripts/test_qg.py"),
)


class SyncError(RuntimeError):
    """An update could not safely replace the target."""


def normalize_target(path: Path) -> Path:
    """Make the target absolute without resolving or following a symlink."""

    expanded = path.expanduser()
    if ".." in expanded.parts:
        raise SyncError("Destino não pode conter '..': {}".format(path))
    if not expanded.is_absolute():
        expanded = Path.cwd() / expanded
    return Path(os.path.abspath(os.fspath(expanded)))


def reject_symlink_components(root: Path, relative_path: Path, description: str) -> None:
    """Fail before an operation could traverse a target-tree symlink."""

    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise SyncError("Caminho relativo inválido: {}".format(relative_path))
    current = root
    if current.is_symlink():
        raise SyncError("{} contém symlink não permitido: {}".format(description, current))
    for part in relative_path.parts:
        if part == ".":
            continue
        current /= part
        if current.is_symlink():
            raise SyncError("{} contém symlink não permitido: {}".format(description, current))


def reject_managed_symlink_ancestry(root: Path, relative_path: Path, description: str) -> None:
    """Protect writes and deletions from an inherited target-tree symlink."""

    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise SyncError("Caminho gerenciado inválido: {}".format(relative_path))
    reject_symlink_components(root, relative_path.parent, "ancestral de {}".format(relative_path))


def remove_declared_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def copy_declared_path(source: Path, destination: Path) -> None:
    if not source.exists():
        raise SyncError("Fonte gerenciada ausente: {}".format(source))
    remove_declared_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, symlinks=True)
    else:
        shutil.copy2(source, destination, follow_symlinks=False)


def managed_source_files() -> Iterable[Path]:
    for relative_path in MANAGED_FILES:
        yield relative_path
    for relative_tree in MANAGED_TREES:
        source_tree = SOURCE_ROOT / relative_tree
        if not source_tree.is_dir():
            raise SyncError("Diretório gerenciado ausente: {}".format(source_tree))
        for source_path in sorted(source_tree.rglob("*")):
            if source_path.is_file() or source_path.is_symlink():
                yield source_path.relative_to(SOURCE_ROOT)


def remove_if_empty(path: Path, stop_at: Path) -> None:
    current = path
    while current != stop_at and current.is_dir() and not current.is_symlink():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def prepare_stage(target: Path) -> Tuple[Path, Path]:
    reject_symlink_components(target, Path("."), "Destino")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(tempfile.mkdtemp(prefix=".superflow-stage-", dir=str(target.parent)))
    stage = temporary_root / PLUGIN_NAME
    try:
        if target.exists():
            if not target.is_dir() or target.is_symlink():
                raise SyncError("Destino deve ser um diretório real: {}".format(target))
            shutil.copytree(target, stage, symlinks=True)
        else:
            stage.mkdir()

        for relative_path in managed_source_files():
            reject_managed_symlink_ancestry(stage, relative_path, "Staging")
            copy_declared_path(SOURCE_ROOT / relative_path, stage / relative_path)
        for relative_path in LEGACY_MANAGED_PATHS:
            reject_managed_symlink_ancestry(stage, relative_path, "Staging")
            legacy_path = stage / relative_path
            remove_declared_path(legacy_path)
            remove_if_empty(legacy_path.parent, stage)
        return stage, temporary_root
    except Exception:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise


def tree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            digest.update(b"L\0" + relative + b"\0" + os.readlink(path).encode("utf-8"))
        elif path.is_dir():
            digest.update(b"D\0" + relative + b"\0")
        elif path.is_file():
            digest.update(b"F\0" + relative + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def validate_stage(stage: Path) -> None:
    command = [
        sys.executable,
        "-I",
        str(stage / "scripts/validate_superflow.py"),
        str(stage),
    ]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        raise SyncError("Staging inválido:\n{}".format(result.stdout.rstrip()))


def backup_path(target: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = target.parent / ".{}-backup-{}".format(target.name, stamp)
    suffix = 1
    while candidate.exists():
        candidate = target.parent / ".{}-backup-{}-{}".format(target.name, stamp, suffix)
        suffix += 1
    return candidate


def synchronize(target: Path, dry_run: bool = False) -> Tuple[bool, Optional[Path]]:
    """Stage, validate and replace only declared plugin files.

    Unknown target paths are copied into the stage untouched. A full backup is
    retained whenever a real target changes, including a known-file conflict.
    """

    target = normalize_target(target)
    stage, temporary_root = prepare_stage(target)
    try:
        validate_stage(stage)
        if target.exists() and tree_fingerprint(target) == tree_fingerprint(stage):
            return False, None
        if dry_run:
            return True, None

        backup = None
        if target.exists():
            backup = backup_path(target)
            shutil.copytree(target, backup, symlinks=True)
            previous = temporary_root / "previous"
            os.replace(str(target), str(previous))
            try:
                os.replace(str(stage), str(target))
            except Exception:
                os.replace(str(previous), str(target))
                raise
            shutil.rmtree(previous, ignore_errors=True)
        else:
            os.replace(str(stage), str(target))
        return True, backup
    finally:
        shutil.rmtree(temporary_root, ignore_errors=True)


def run_install() -> None:
    command = ["codex", "plugin", "add", "{}@{}".format(PLUGIN_NAME, MARKETPLACE)]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        raise SyncError("Instalação falhou:\n{}".format(result.stdout.rstrip()))
    print(result.stdout.rstrip())


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(DEFAULT_TARGET))
    parser.add_argument("--dry-run", action="store_true", help="Valida o staging sem alterar o destino.")
    parser.add_argument("--install", action="store_true", help="Instala no Codex somente depois do sync validado.")
    args = parser.parse_args(argv)
    if args.dry_run and args.install:
        parser.error("--install não pode ser usado com --dry-run")

    try:
        changed, backup = synchronize(Path(args.target), dry_run=args.dry_run)
        if args.dry_run:
            print("OK: staging validado; destino não foi alterado")
            return 0
        if changed:
            print("OK: plugin atualizado em {}".format(Path(args.target).expanduser()))
            if backup is not None:
                print("Backup preservado em {}".format(backup))
        else:
            print("OK: plugin já está atualizado")
        if args.install:
            run_install()
        return 0
    except (OSError, SyncError) as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
