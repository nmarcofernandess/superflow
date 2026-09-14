#!/usr/bin/env python3
"""Exercise the packed runtime and a safe upgrade of a fixture install."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence


ROOT = Path(__file__).resolve().parents[3]
PLUGIN = ROOT / "plugins/superflow"
PACKAGE_NAME = "@superflow/runtime"


def run(command: Sequence[str], cwd: Optional[Path] = None, expect: int = 0) -> str:
    result = subprocess.run(
        list(command),
        cwd=str(cwd) if cwd is not None else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != expect:
        raise AssertionError(
            "command failed (expected {}, got {}): {}\nstdout:\n{}\nstderr:\n{}".format(
                expect, result.returncode, " ".join(command), result.stdout, result.stderr
            )
        )
    return result.stdout if expect == 0 else result.stdout + result.stderr


def write_json(path: Path, value: Dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_json(relative_path: str) -> Dict:
    value = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError("{} não contém um objeto JSON".format(relative_path))
    return value


def test_release_metadata() -> None:
    package = read_json("package.json")
    if package.get("name") != PACKAGE_NAME or package.get("version") != "0.9.3":
        raise AssertionError("package.json não declara @superflow/runtime 0.9.3")
    if package.get("private") is not True:
        raise AssertionError("package.json deve permanecer privado")
    forbidden_package_fields = {"dependencies", "devDependencies", "optionalDependencies", "peerDependencies", "bin"}
    present = forbidden_package_fields & set(package)
    if present:
        raise AssertionError("package.json contém superfície npm indevida: {}".format(sorted(present)))
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict) or {"install", "prepare"} & set(scripts):
        raise AssertionError("package.json não pode executar install ou prepare")

    for relative_path in (
        "plugins/superflow/.codex-plugin/plugin.json",
        "plugins/superflow/.claude-plugin/plugin.json",
    ):
        manifest = read_json(relative_path)
        if manifest.get("name") != "superflow" or manifest.get("version") != "0.9.3":
            raise AssertionError("{} não está na versão 0.9.3".format(relative_path))
        if manifest.get("skills") != "./skills/":
            raise AssertionError("{} não aponta para skills".format(relative_path))

    codex_marketplace = read_json(".agents/plugins/marketplace.json")
    claude_marketplace = read_json(".claude-plugin/marketplace.json")
    for marketplace, source in (
        (codex_marketplace, {"source": "local", "path": "./plugins/superflow"}),
        (claude_marketplace, "./plugins/superflow"),
    ):
        entries = marketplace.get("plugins")
        if not isinstance(entries, list) or len(entries) != 1:
            raise AssertionError("marketplace deve conter exatamente Superflow")
        entry = entries[0]
        if entry.get("name") != "superflow" or entry.get("version") != "0.9.3":
            raise AssertionError("marketplace não está na versão 0.9.3")
        if entry.get("source") != source:
            raise AssertionError("marketplace aponta para source inesperada")


def packed_files() -> List[str]:
    output = run(["npm", "pack", "--dry-run", "--json"], cwd=ROOT)
    report = json.loads(output)
    if not isinstance(report, list) or len(report) != 1:
        raise AssertionError("npm pack --dry-run não retornou um pacote")
    files = report[0].get("files")
    if not isinstance(files, list):
        raise AssertionError("npm pack --dry-run não listou arquivos")
    paths = [item.get("path") for item in files if isinstance(item, dict)]
    if not all(isinstance(path, str) for path in paths):
        raise AssertionError("npm pack retornou caminho inválido")
    return paths


def assert_pack_contract(paths: List[str]) -> None:
    required = {
        "LICENSE",
        "package.json",
        "plugins/superflow/.codex-plugin/plugin.json",
        "plugins/superflow/assets/qg.html",
        "plugins/superflow/scripts/superflow.py",
        "plugins/superflow/scripts/superflow_model.py",
        "plugins/superflow/scripts/superflow_qg.py",
        "plugins/superflow/scripts/validate_superflow.py",
        "plugins/superflow/scripts/vendor/yaml/__init__.py",
    }
    missing = required - set(paths)
    if missing:
        raise AssertionError("pacote sem arquivos necessários: {}".format(sorted(missing)))
    forbidden = [
        path
        for path in paths
        if "/test_" in path
        or path.endswith("sync_personal_install.py")
        or "superflow_rota.py" in path
        or "/assets/task-board/" in path
        or "/assets/fixtures/" in path
        or "/assets/examples/" in path
    ]
    if forbidden:
        raise AssertionError("pacote incluiu superfície aposentada: {}".format(sorted(forbidden)))


def make_fixture_project(root: Path) -> Path:
    project = root / "project"
    package = project / "specs/demo"
    package.mkdir(parents=True)
    (package / "status.md").write_text(
        "---\n"
        "id: demo\n"
        "title: Demo\n"
        "status: pending\n"
        "---\n",
        encoding="utf-8",
    )
    return project


def test_packed_runtime(workspace: Path) -> None:
    pack_directory = workspace / "pack"
    pack_directory.mkdir()
    report = json.loads(
        run(
            ["npm", "pack", "--json", "--pack-destination", str(pack_directory)],
            cwd=ROOT,
        )
    )
    tarball = pack_directory / report[0]["filename"]
    if not tarball.is_file():
        raise AssertionError("tarball não foi criado")

    consumer = workspace / "consumer"
    consumer.mkdir()
    write_json(
        consumer / "package.json",
        {
            "name": "superflow-distribution-fixture",
            "version": "1.0.0",
            "private": True,
            "devDependencies": {PACKAGE_NAME: "file:" + str(tarball)},
        },
    )
    run(["npm", "install", "--package-lock-only", "--ignore-scripts"], cwd=consumer)
    run(["npm", "ci", "--ignore-scripts"], cwd=consumer)
    manifest_path = Path(
        run(
            ["node", "-p", "require.resolve('@superflow/runtime/package.json')"],
            cwd=consumer,
        ).strip()
    )
    runtime = manifest_path.parent / "plugins/superflow/scripts/superflow.py"
    if not runtime.is_file():
        raise AssertionError("runtime não foi resolvido a partir do pacote instalado")

    project = make_fixture_project(workspace)
    version = run([sys.executable, "-I", str(runtime), "--version"], cwd=consumer).strip()
    if version != "0.9.3":
        raise AssertionError("--version do runtime instalado retornou {!r}".format(version))
    run(
        [
            sys.executable,
            "-I",
            str(runtime),
            "--root",
            str(project),
            "new",
            "second",
            "--title",
            "Second",
        ],
        cwd=consumer,
    )
    run([sys.executable, "-I", str(runtime), "--root", str(project), "check", "status"], cwd=consumer)
    output = project / "qg.html"
    run(
        [sys.executable, "-I", str(runtime), "--root", str(project), "qg", "--output", str(output)],
        cwd=consumer,
    )
    if not output.is_file() or "superflow.feed.v3" not in output.read_text(encoding="utf-8"):
        raise AssertionError("qg do runtime instalado não gerou a projeção esperada")


def test_sync_upgrade(workspace: Path) -> None:
    target = workspace / "installed-plugin"
    (target / "custom").mkdir(parents=True)
    (target / "custom/local-note.md").write_text("preserve me\n", encoding="utf-8")
    (target / "skills/capture").mkdir(parents=True)
    (target / "skills/capture/SKILL.md").write_text("legacy\n", encoding="utf-8")
    (target / "scripts").mkdir(parents=True, exist_ok=True)
    (target / "scripts/superflow_rota.py").write_text("legacy\n", encoding="utf-8")
    (target / "assets/task-board").mkdir(parents=True)
    (target / "assets/task-board/board.html").write_text("legacy\n", encoding="utf-8")
    (target / "assets/fixtures/rota").mkdir(parents=True)
    (target / "assets/fixtures/rota/plano-valido.json").write_text("legacy\n", encoding="utf-8")
    (target / "assets/fixtures/custom").mkdir(parents=True)
    (target / "assets/fixtures/custom/keep.md").write_text("preserve me\n", encoding="utf-8")

    sync = PLUGIN / "scripts/sync_personal_install.py"
    run([sys.executable, "-I", str(sync), "--target", str(target)])
    if (target / "skills/capture/SKILL.md").exists():
        raise AssertionError("skill v1 permaneceu após atualização")
    if (target / "scripts/superflow_rota.py").exists():
        raise AssertionError("executor v1 permaneceu após atualização")
    if (target / "assets/task-board/board.html").exists():
        raise AssertionError("asset v1 permaneceu após atualização")
    if (target / "assets/fixtures/rota/plano-valido.json").exists():
        raise AssertionError("fixture v1 permaneceu após atualização")
    if (target / "custom/local-note.md").read_text(encoding="utf-8") != "preserve me\n":
        raise AssertionError("arquivo customizado foi perdido")
    if (target / "assets/fixtures/custom/keep.md").read_text(encoding="utf-8") != "preserve me\n":
        raise AssertionError("fixture customizado foi perdido")
    if not (target / "skills/superflow/SKILL.md").is_file():
        raise AssertionError("staging validado não substituiu a instalação ativa")
    backups = list(target.parent.glob(".installed-plugin-backup-*"))
    if len(backups) != 1 or not (backups[0] / "skills/capture/SKILL.md").is_file():
        raise AssertionError("conflito não preservou backup verificável")

    blocked = workspace / "blocked-plugin"
    blocked.mkdir()
    (blocked / "skills").write_text("custom collision\n", encoding="utf-8")
    output = run([sys.executable, "-I", str(sync), "--target", str(blocked)], expect=2)
    if "error:" not in output.lower() and not (blocked / "skills").is_file():
        raise AssertionError("falha de staging não foi explícita ou alterou arquivo desconhecido")
    if (blocked / "skills").read_text(encoding="utf-8") != "custom collision\n":
        raise AssertionError("falha removeu arquivo desconhecido")


def test_sync_rejects_symlinks(workspace: Path) -> None:
    sync = PLUGIN / "scripts/sync_personal_install.py"

    external_target = workspace / "external-target"
    external_target.mkdir()
    target_marker = external_target / "marker.txt"
    target_marker.write_text("outside target\n", encoding="utf-8")
    linked_target = workspace / "linked-plugin"
    linked_target.symlink_to(external_target, target_is_directory=True)
    run([sys.executable, "-I", str(sync), "--target", str(linked_target)], expect=2)
    if target_marker.read_text(encoding="utf-8") != "outside target\n":
        raise AssertionError("sync seguiu um destino symlink")
    if not linked_target.is_symlink():
        raise AssertionError("sync substituiu o symlink de destino")

    nested_target = workspace / "nested-plugin"
    nested_target.mkdir()
    external_assets = workspace / "external-assets"
    external_assets.mkdir()
    asset_marker = external_assets / "qg.html"
    asset_marker.write_text("outside assets\n", encoding="utf-8")
    (nested_target / "assets").symlink_to(external_assets, target_is_directory=True)
    run([sys.executable, "-I", str(sync), "--target", str(nested_target)], expect=2)
    if asset_marker.read_text(encoding="utf-8") != "outside assets\n":
        raise AssertionError("sync escreveu por um symlink ancestral")
    if not (nested_target / "assets").is_symlink():
        raise AssertionError("sync alterou o symlink ancestral original")


def main() -> int:
    test_release_metadata()
    paths = packed_files()
    assert_pack_contract(paths)
    with tempfile.TemporaryDirectory(prefix="superflow-distribution-") as raw_workspace:
        workspace = Path(raw_workspace)
        test_packed_runtime(workspace)
        test_sync_upgrade(workspace)
        test_sync_rejects_symlinks(workspace)
    print("distribution: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
