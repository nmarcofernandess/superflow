#!/usr/bin/env python3
"""Smoke-test Superflow route classification and generated packages."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TASKGEN = SCRIPT_DIR / "superflow_taskgen.py"
VALIDATE = SCRIPT_DIR / "validate_superflow.py"


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)


def assert_eq(actual: object, expected: object, context: str) -> None:
    if actual != expected:
        raise AssertionError(f"{context}: expected {expected!r}, got {actual!r}")


def run_case(root: Path, description: str, *, mode: str, expected_route: str, expected_budget: str) -> dict:
    result = run([
        sys.executable,
        str(TASKGEN),
        "--root",
        str(root),
        "--mode",
        mode,
        "--json",
        description,
    ])
    payload = json.loads(result.stdout)
    classification = payload["classification"]
    assert_eq(classification["route"], expected_route, description)
    assert_eq(classification["phase_budget"], expected_budget, description)
    if payload["mode"] == "local":
        spec_dir = Path(payload["spec_dir"])
        run([sys.executable, str(VALIDATE), str(spec_dir)])
    return payload


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="superflow-routes.") as tmp:
        root = Path(tmp)

        run_case(
            root,
            "ideia solta para melhorar onboarding depois",
            mode="issue",
            expected_route="inbox_only",
            expected_budget="capture",
        )

        lean = run_case(
            root,
            "implementar botao exportar CSV na tela de relatorios para usuario admin com teste validavel e sem alterar filtros existentes",
            mode="local",
            expected_route="prd_execute",
            expected_budget="lean",
        )
        assert_eq(lean["classification"]["skipped_phases"], ["analyst", "build", "plan"], "lean skipped phases")

        run_case(
            root,
            "migrar schema de pagamentos com auth, cache, api, relatorio e rollback sem quebrar dados existentes",
            mode="local",
            expected_route="build_plan_execute",
            expected_budget="deep",
        )

        run_case(
            root,
            "bug intermitente: exportacao mostra total divergente e ainda nao sabemos a causa",
            mode="auto",
            expected_route="investigate_first",
            expected_budget="forensic",
        )

        warlog = run([
            sys.executable,
            str(TASKGEN),
            "--root",
            str(root),
            "--mode",
            "local",
            "--with-warlog",
            "--json",
            "migrar schema de pagamentos com auth, cache, api, relatorio e rollback sem quebrar dados existentes",
        ])
        warlog_payload = json.loads(warlog.stdout)
        warlog_dir = Path(warlog_payload["spec_dir"])
        assert_eq((warlog_dir / "WARLOG.md").exists(), True, "warlog file exists")
        status = json.loads((warlog_dir / "status.json").read_text(encoding="utf-8"))
        assert_eq(status["artifacts"]["warlog"], "WARLOG.md", "warlog artifact")
        run([sys.executable, str(VALIDATE), str(warlog_dir), "--mermaid"])

    print("OK: superflow route tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
