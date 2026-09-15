#!/usr/bin/env python3
"""Exercise the versioned packed runtime in an isolated consumer."""

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
    if package.get("name") != PACKAGE_NAME or package.get("version") != "0.10.1":
        raise AssertionError("package.json não declara @superflow/runtime 0.10.1")
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
        if manifest.get("name") != "superflow" or manifest.get("version") != "0.10.1":
            raise AssertionError("{} não está na versão 0.10.1".format(relative_path))
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
        if entry.get("name") != "superflow" or entry.get("version") != "0.10.1":
            raise AssertionError("marketplace não está na versão 0.10.1")
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


def make_fixture_project(root: Path) -> Path:
    project = root / "project"
    package = project / "specs/demo"
    package.mkdir(parents=True)
    (package / "status.md").write_text(
        "---\n"
        "id: demo\n"
        "title: Demo\n"
        "summary: Demonstrar a organização de uma entrega.\n"
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
    if version != "0.10.1":
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
            "--summary",
            "Organizar uma segunda entrega independente",
        ],
        cwd=consumer,
    )
    run([sys.executable, "-I", str(runtime), "--root", str(project), "check", "status"], cwd=consumer)
    output = project / "qg.html"
    run(
        [sys.executable, "-I", str(runtime), "--root", str(project), "qg", "--output", str(output)],
        cwd=consumer,
    )
    if not output.is_file() or "superflow.feed.v4" not in output.read_text(encoding="utf-8"):
        raise AssertionError("qg do runtime instalado não gerou a projeção esperada")


def main() -> int:
    test_release_metadata()
    paths = packed_files()
    assert_pack_contract(paths)
    with tempfile.TemporaryDirectory(prefix="superflow-distribution-") as raw_workspace:
        workspace = Path(raw_workspace)
        test_packed_runtime(workspace)
    print("distribution: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
