#!/usr/bin/env python3
"""Structural tests for Superflow feature-mindset (Analyst/Build faceted truth).

Includes Claude APPROVE-WITH-FIXES exploit suite (A–E) with phrases that do NOT
share literals with the golden fixtures.
"""

from __future__ import annotations

import json
import re
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


def assert_fail(result: subprocess.CompletedProcess, *, why: str, needles: list[str]) -> None:
    if result.returncode == 0:
        raise AssertionError(f"{why} must FAIL:\n{result.stdout}")
    blob = result.stdout.lower()
    if not any(n.lower() in blob for n in needles):
        raise AssertionError(f"{why}: expected one of {needles} in:\n{result.stdout}")


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

        # --- legacy traps still closed ---

        # 1) default-deep package with approved instance prose MUST fail
        #    Phrases are NOVEL (not the fixture "Continua Retorno / R$ 180" literal).
        bad_deep = root / "bad-deep-safada"
        shutil.copytree(FIXTURES / "deep", bad_deep)
        analysis = (bad_deep / "analysis.md").read_text(encoding="utf-8")
        # Inject four form-based safadas (Claude exploit B paraphrases)
        inject = """
| Drawer | "Voce ainda tem 3 consultas restantes neste mes, aproveite!" | nenhum | manter |
| Toast  | "O plano Premium custa 249,90 conforme acertamos na reuniao." | nenhum | manter |
| Empty  | "Nada aqui embaixo, olhe no bloco acima a direita." | nenhum | manter |
| Modal  | "Como voce ja tem 2 pacientes gestantes, sugerimos o Pro." | nenhum | manter |
"""
        analysis = analysis.replace(
            "## Faceta — Copy (strings-safadas)",
            "## Faceta — Copy (strings-safadas)\n" + inject,
        )
        (bad_deep / "analysis.md").write_text(analysis, encoding="utf-8")
        bad_deep_run = run_validate(bad_deep)
        assert_fail(
            bad_deep_run,
            why="form-based strings-safadas (novel phrases)",
            needles=["safada", "instance-form", "invariante"],
        )

        # 2) deep package with fake Recode N/A row only MUST fail
        bad_recode = root / "bad-deep-recode"
        shutil.copytree(FIXTURES / "deep", bad_recode)
        a2 = (bad_recode / "analysis.md").read_text(encoding="utf-8")
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
        assert_fail(
            bad_recode_run,
            why="deep package with fake Recode N/A",
            needles=["recode", "coherence_proof", "n/a"],
        )

        # 3) skip escape hatch MUST fail
        bad_skip = root / "bad-skip"
        shutil.copytree(FIXTURES / "empty-headings-fail", bad_skip)
        (bad_skip / "mindset-depth.txt").write_text("skip\n", encoding="utf-8")
        bad_skip_run = run_validate(bad_skip)
        assert_fail(
            bad_skip_run,
            why="mindset-depth skip",
            needles=["skip"],
        )

        # 4) trap depth still rejects approved safada (novel currency+approve)
        bad_trap = root / "bad-trap"
        shutil.copytree(FIXTURES / "string-trap", bad_trap)
        a3 = (bad_trap / "analysis.md").read_text(encoding="utf-8")
        a3 = a3.replace(
            "| body | Continua Retorno por R$ 180,00, como foi combinado. | prosa-instância | **morte** → estrutura Valor + número |",
            "| body | Pacote anual por R$ 399,00 so pra voce. | nenhum | UI copy aprovada |",
        )
        (bad_trap / "analysis.md").write_text(a3, encoding="utf-8")
        bad_trap_run = run_validate(bad_trap)
        assert_fail(
            bad_trap_run,
            why="surviving instance prose on trap",
            needles=["safada", "instance-form", "aprovada"],
        )

        # --- Claude exploits A–E must FAIL ---

        # C: remove status.json → partial package fail (never silent OK)
        exploit_c = root / "exploit-c-no-status"
        shutil.copytree(FIXTURES / "empty-headings-fail", exploit_c)
        (exploit_c / "status.json").unlink()
        c_run = run_validate(exploit_c)
        assert_fail(
            c_run,
            why="exploit C: analysis without status.json",
            needles=["partial", "missing", "status"],
        )

        # D: echo docs into mindset-depth.txt must NOT downgrade deep status
        exploit_d = root / "exploit-d-depth-hatch"
        shutil.copytree(FIXTURES / "deep", exploit_d)
        (exploit_d / "mindset-depth.txt").write_text("docs\n", encoding="utf-8")
        # hollow the facets to TBD — if hatch worked, docs depth would skip
        a_d = (exploit_d / "analysis.md").read_text(encoding="utf-8")
        a_d = re.sub(
            r"(## Faceta — Produto\n)([\s\S]*?)(\n## Faceta — Backend)",
            r"\1\nTBD\n\3",
            a_d,
            count=1,
        )
        a_d = re.sub(
            r"(## Recode Log\n)([\s\S]*?)(\n## Product Promise)",
            r"\1\nskip_reason: pretended docs\n\n\3",
            a_d,
            count=1,
        )
        (exploit_d / "analysis.md").write_text(a_d, encoding="utf-8")
        d_run = run_validate(exploit_d)
        assert_fail(
            d_run,
            why="exploit D: mindset-depth.txt=docs cannot downgrade status deep",
            needles=["placeholder", "empty", "recode", "faceta", "tbd"],
        )

        # A: empty-ish analysis with backtick-only backend + new without guard + fake recode
        exploit_a = root / "exploit-a-empty"
        shutil.copytree(FIXTURES / "deep", exploit_a)
        hollow = """# Analyst: hollow

## TL;DR

Hollow package that used to pass.

## Síntese

Mostrar algo no drawer com valor real do plano sem inventar acordo verbal social.

## Faceta — Produto

Promessa vazia mas com mais de vinte e quatro caracteres de enrolação.

## Faceta — Backend (dados reais)

O payload chega `corretamente` no cliente.

## Faceta — Frontend (reuso antes de criar)

Decision: new

## Faceta — Copy (strings-safadas)

Usar estrutura de label.

## Recode Log

| When | Trigger | Facet | Recode |
|---|---|---|---|
| T1 | achei que sim | Produto | mudei de ideia |
"""
        (exploit_a / "analysis.md").write_text(hollow, encoding="utf-8")
        a_run = run_validate(exploit_a)
        assert_fail(
            a_run,
            why="exploit A: hollow deep analysis",
            needles=["path:line", "unproven", "reuse guard", "new", "recode", "backend"],
        )

        # E: SPEC facets TBD + empty Recode Log
        exploit_e = root / "exploit-e-spec"
        shutil.copytree(FIXTURES / "deep", exploit_e)
        spec = (exploit_e / "SPEC.md").read_text(encoding="utf-8")
        spec = re.sub(
            r"(### (?:Product|Backend|Frontend|Copy)[^\n]*\n)[\s\S]*?(?=\n#{2,3} )",
            r"\1\nTBD\n",
            spec,
        )
        spec = re.sub(
            r"(## Recode Log\n)[\s\S]*?(?=\n#{2,3} )",
            r"\1\n(sem entradas)\n",
            spec,
        )
        (exploit_e / "SPEC.md").write_text(spec, encoding="utf-8")
        e_run = run_validate(exploit_e)
        assert_fail(
            e_run,
            why="exploit E: hollow SPEC TBD + empty recode",
            needles=["placeholder", "empty", "recode", "parity", "tbd", "path:line"],
        )

        # Bonus: coherence_proof alone is enough for deep recode (honest no-recode)
        good_coh = root / "good-coherence"
        shutil.copytree(FIXTURES / "deep", good_coh)
        a_c = (good_coh / "analysis.md").read_text(encoding="utf-8")
        a_c = re.sub(
            r"(## Recode Log\n)([\s\S]*?)(\n## Product Promise)",
            r"\1\n"
            r"coherence_proof: initial synthesis already matched DTO path:line and drawer reuse; "
            r"no facet contradicted terrain.\n\n\3",
            a_c,
            count=1,
        )
        (good_coh / "analysis.md").write_text(a_c, encoding="utf-8")
        # SPEC also needs recode honesty
        s_c = (good_coh / "SPEC.md").read_text(encoding="utf-8")
        s_c = re.sub(
            r"(## Recode Log\n)([\s\S]*?)(\n## Testable behaviors)",
            r"\1\n"
            r"coherence_proof: synthesis matched analysis evidence; no recode required.\n\n\3",
            s_c,
            count=1,
        )
        (good_coh / "SPEC.md").write_text(s_c, encoding="utf-8")
        coh_run = run_validate(good_coh)
        if coh_run.returncode != 0:
            raise AssertionError(f"coherence_proof deep package must PASS:\n{coh_run.stdout}")

    print("OK: superflow feature mindset tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
