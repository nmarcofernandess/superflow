#!/usr/bin/env python3
"""Structural tests for Superflow feature-mindset (Analyst/Build faceted truth)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATE = SCRIPT_DIR / "validate_superflow.py"
PLUGIN_ROOT = SCRIPT_DIR.parent
FIXTURES = PLUGIN_ROOT / "assets" / "fixtures" / "mindset"
COVERAGE = FIXTURES / "coverage.json"
REQUIRED_IDS = [
    "F1", "F2", "F3", "F4", "F5", "F6", "F7",
    "T1", "T2", "T3", "T4", "T5", "T6", "T7",
    "S1", "S2", "S3", "S4", "S5", "S6",
    "B1", "B2", "B3", "B4", "B5", "B6",
    "H1", "H2", "H3", "H4",
    "D1", "D2",
]


def run_validate(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATE), str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    plugin = run_validate(PLUGIN_ROOT)
    if plugin.returncode != 0:
        raise AssertionError(f"plugin root must validate:\n{plugin.stdout}")

    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    units = {u["id"]: u for u in coverage["units"]}
    for uid in REQUIRED_IDS:
        if uid not in units:
            raise AssertionError(f"coverage missing {uid}")
        if units[uid].get("estado_atual") != "present":
            raise AssertionError(f"coverage {uid} not present")
        if not units[uid].get("gate_type"):
            raise AssertionError(f"coverage {uid} missing gate_type")

    deep = run_validate(FIXTURES / "deep")
    if deep.returncode != 0:
        raise AssertionError(f"deep fixture must PASS:\n{deep.stdout}")

    docs = run_validate(FIXTURES / "docs-only")
    if docs.returncode != 0:
        raise AssertionError(f"docs-only fixture must PASS:\n{docs.stdout}")

    trap = run_validate(FIXTURES / "string-trap")
    if trap.returncode != 0:
        raise AssertionError(f"string-trap compliant package must PASS:\n{trap.stdout}")

    empty = run_validate(FIXTURES / "empty-headings-fail")
    if empty.returncode == 0:
        raise AssertionError("empty-headings package must FAIL validation")
    if "Síntese" not in empty.stdout and "placeholder" not in empty.stdout.lower() and "empty" not in empty.stdout.lower():
        raise AssertionError(f"empty-headings fail message unexpected:\n{empty.stdout}")

    # Explicit trap: if we inject surviving safada without death, must fail
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory(prefix="superflow-safada.") as tmp:
        bad = Path(tmp) / "bad-trap"
        shutil.copytree(FIXTURES / "string-trap", bad)
        (bad / "mindset-depth.txt").write_text("trap\n", encoding="utf-8")
        analysis = (bad / "analysis.md").read_text(encoding="utf-8")
        # Approve instance prose as system copy (no morte/estrutura)
        analysis = analysis.replace(
            "| body | Continua Retorno por R$ 180,00, como foi combinado. | prosa-instância | **morte** → estrutura Valor + número |",
            "| body | Continua Retorno por R$ 180,00, como foi combinado. | nenhum | UI copy aprovada |",
        )
        # Also poison synthesis to keep phrase without death markers nearby
        analysis = analysis.replace(
            "sem prosa que\ninvente acordo social",
            "mostra Continua Retorno por R$ 180,00, como foi combinado na UI",
        )
        (bad / "analysis.md").write_text(analysis, encoding="utf-8")
        bad_run = run_validate(bad)
        if bad_run.returncode == 0:
            raise AssertionError("surviving instance prose must FAIL trap validation")
        if "safada" not in bad_run.stdout.lower() and "instance" not in bad_run.stdout.lower() and "180" not in bad_run.stdout:
            raise AssertionError(f"expected safada fail, got:\n{bad_run.stdout}")

    print("OK: superflow feature mindset tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
