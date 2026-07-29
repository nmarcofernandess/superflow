#!/usr/bin/env python3
"""Structural tests for Superflow feature-mindset (Analyst/Build faceted truth)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
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
    if (
        "Síntese" not in empty.stdout
        and "placeholder" not in empty.stdout.lower()
        and "empty" not in empty.stdout.lower()
    ):
        raise AssertionError(f"empty-headings fail message unexpected:\n{empty.stdout}")

    with tempfile.TemporaryDirectory(prefix="superflow-mindset.") as tmp:
        root = Path(tmp)

        # 1) default-deep package with approved instance prose MUST fail
        bad_deep = root / "bad-deep-safada"
        shutil.copytree(FIXTURES / "deep", bad_deep)
        (bad_deep / "mindset-depth.txt").write_text("deep\n", encoding="utf-8")
        analysis = (bad_deep / "analysis.md").read_text(encoding="utf-8")
        analysis = analysis.replace(
            "| Drawer body | “Continua Retorno por R$ 180,00, como foi combinado.” | prosa-instância | **morte** → estrutura label “Valor” + valor formatado |",
            "| Drawer body | Continua Retorno por R$ 180,00, como foi combinado. | nenhum | UI copy aprovada |",
        )
        # also try curly-quote free fallback if first replace missed
        if "UI copy aprovada" not in analysis:
            analysis = analysis.replace(
                "**morte** → estrutura label “Valor” + valor formatado",
                "UI copy aprovada",
            )
            if "Continua Retorno por R$ 180" not in analysis:
                # inject a bad row
                analysis = analysis.replace(
                    "## Faceta — Copy (strings-safadas)",
                    "## Faceta — Copy (strings-safadas)\n\n"
                    "| Superfície | Texto | Pecado? | Destino |\n"
                    "|---|---|---|---|\n"
                    "| body | Continua Retorno por R$ 180,00, como foi combinado. | nenhum | UI copy aprovada |\n",
                )
        (bad_deep / "analysis.md").write_text(analysis, encoding="utf-8")
        bad_deep_run = run_validate(bad_deep)
        if bad_deep_run.returncode == 0:
            raise AssertionError(
                "default-deep package with approved instance prose must FAIL:\n"
                f"{bad_deep_run.stdout}"
            )
        if "safada" not in bad_deep_run.stdout.lower() and "aprovada" not in bad_deep_run.stdout.lower():
            raise AssertionError(f"expected safada/aprovada fail on deep:\n{bad_deep_run.stdout}")

        # 2) deep package with fake Recode N/A row only MUST fail
        bad_recode = root / "bad-deep-recode"
        shutil.copytree(FIXTURES / "deep", bad_recode)
        (bad_recode / "mindset-depth.txt").write_text("deep\n", encoding="utf-8")
        a2 = (bad_recode / "analysis.md").read_text(encoding="utf-8")
        # replace Recode Log section body with fake N/A row
        import re

        a2 = re.sub(
            r"(## Recode Log\n)([\s\S]*?)(\n## Product Promise)",
            r"\1\n| When | Trigger (evidence) | Facet that broke | What was recoded |\n"
            r"|---|---|---|---|\n"
            r"| T1 | N/A | N/A | nenhuma recode |\n\n\3",
            a2,
            count=1,
        )
        (bad_recode / "analysis.md").write_text(a2, encoding="utf-8")
        bad_recode_run = run_validate(bad_recode)
        if bad_recode_run.returncode == 0:
            raise AssertionError(
                "deep package with fake Recode N/A must FAIL:\n" + bad_recode_run.stdout
            )
        if "recode" not in bad_recode_run.stdout.lower() and "n/a" not in bad_recode_run.stdout.lower():
            raise AssertionError(f"expected recode fake fail:\n{bad_recode_run.stdout}")

        # 3) skip escape hatch MUST fail
        bad_skip = root / "bad-skip"
        shutil.copytree(FIXTURES / "empty-headings-fail", bad_skip)
        (bad_skip / "mindset-depth.txt").write_text("skip\n", encoding="utf-8")
        bad_skip_run = run_validate(bad_skip)
        if bad_skip_run.returncode == 0:
            raise AssertionError("mindset-depth skip must FAIL (no escape hatch)")
        if "skip" not in bad_skip_run.stdout.lower():
            raise AssertionError(f"expected skip forbidden message:\n{bad_skip_run.stdout}")

        # 4) trap depth still rejects approved safada
        bad_trap = root / "bad-trap"
        shutil.copytree(FIXTURES / "string-trap", bad_trap)
        (bad_trap / "mindset-depth.txt").write_text("trap\n", encoding="utf-8")
        a3 = (bad_trap / "analysis.md").read_text(encoding="utf-8")
        a3 = a3.replace(
            "| body | Continua Retorno por R$ 180,00, como foi combinado. | prosa-instância | **morte** → estrutura Valor + número |",
            "| body | Continua Retorno por R$ 180,00, como foi combinado. | nenhum | UI copy aprovada |",
        )
        (bad_trap / "analysis.md").write_text(a3, encoding="utf-8")
        bad_trap_run = run_validate(bad_trap)
        if bad_trap_run.returncode == 0:
            raise AssertionError("surviving instance prose must FAIL trap validation")

    print("OK: superflow feature mindset tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
