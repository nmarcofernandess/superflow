#!/usr/bin/env python3
"""Positive + directed-mutant proofs for lifecycle-contract D1–D7 and the DoD gate.

A failing mutant proves that branch of the contract, not the whole system.
Fixtures live in a temp dir and never land in the product.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATE = SCRIPT_DIR / "validate_superflow.py"
CAMPAIGN = SCRIPT_DIR / "superflow_campaign.py"
PLUGIN_ROOT = SCRIPT_DIR.parent
FIXTURE = PLUGIN_ROOT / "assets" / "fixtures" / "campaign" / "001-foundation"

HANDBOOK_OK = """# HANDBOOK — lifecycle fixture

## Intenção
Retrato de fixture para provar que prosa de handbook não cruza fase.

## Estado real
O gate vive em `plugins/superflow/scripts/validate_superflow.py:1` e a fixture
base em `plugins/superflow/assets/fixtures/campaign/001-foundation/status.json:1`.
O motor de campanha que consome o selo está em
`plugins/superflow/scripts/superflow_campaign.py:1`.

## Rastro
Nasceu com o contrato de lifecycle, na mesma fatia.

## Dificuldade e impacto
Baixa: fixture de teste, sem consumidor de produto.

## Testes
Este proprio arquivo, executado por `python3 test_lifecycle_contract.py`.

## O que a linha não comporta
Não cobre correção semântica do Definition of Complete nem paráfrase.

## Relatório de leitura
Lidos: o validador e o motor. Tudo entregue neste retrato, de propósito.
"""

HANDBOOK_BLOCK = {
    "read_at": "2026-09-10",
    "read_base": "chore/contrato-e-vocabulario@0000000",
    "index_action": "confirm_pending",
    "selo": "in_flight",
    "archivable": "no",
    "archive_debts": [],
    "open_decisions": [],
    "next_useful": [{"id": "N1", "kind": "implementation", "blocked_by": []}],
    "unanswered": [],
    "children_rollup": None,
}

GATHERING = {
    "schema_version": "superflow.status.v1",
    "id": "fossil-typed",
    "route": "inbox_prd",
    "phase_budget": "lean",
    "confidence": "low",
    "current_phase": "inbox",
    "decision": {
        "verdict": "inbox",
        "prd_status": "gathering",
        "reason": "scaffold",
        "prd_path": None,
        "discard_path": None,
    },
    "phases": {"inbox": "pending", "execute": "pending", "qa": "pending"},
    "artifacts": {
        "prd": None,
        "analysis": None,
        "blueprint": None,
        "progress": None,
        "warlog": None,
        "handbook": None,
        "plan": None,
        "implementation_log": None,
        "review": None,
        "qa": None,
    },
    "task_source": {"type": "none", "path": None, "progress": None},
}


def run_validate(path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATE), str(path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def run_campaign(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CAMPAIGN), str(root), "--json", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_status(pkg: Path, **fields) -> None:
    path = pkg / "status.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, value in fields.items():
        if key == "phases":
            data.setdefault("phases", {}).update(value)
        elif key == "decision":
            data.setdefault("decision", {}).update(value)
        elif key == "artifacts":
            data.setdefault("artifacts", {}).update(value)
        else:
            data[key] = value
    write_json(path, data)


def expect_ok(path: Path, why: str, *args: str) -> subprocess.CompletedProcess:
    result = run_validate(path, *args)
    if result.returncode != 0:
        raise AssertionError(f"{why}: expected OK, got:\n{result.stdout}")
    return result


def expect_fail(path: Path, needle: str, why: str, *args: str) -> subprocess.CompletedProcess:
    result = run_validate(path, *args)
    if result.returncode == 0:
        raise AssertionError(f"{why}: expected FAIL, got OK:\n{result.stdout}")
    if needle.lower() not in result.stdout.lower():
        raise AssertionError(f"{why}: failure must name {needle!r}; got:\n{result.stdout}")
    return result


def gathering_pkg(root: Path, name: str, **fields) -> Path:
    pkg = root / name
    pkg.mkdir(parents=True)
    data = json.loads(json.dumps(GATHERING))
    data["id"] = name
    data.update(fields)
    write_json(pkg / "status.json", data)
    return pkg


def family_1_unregistered(root: Path) -> None:
    pkg = root / "unregistered-docs"
    pkg.mkdir()
    for name in ("PRD.md", "SPEC.md", "analysis.md"):
        (pkg / name).write_text(f"# {name}\nnot a package\n", encoding="utf-8")
    result = expect_fail(pkg, "unregistered_spec_documents", "F1 docs sem status")
    if "partial package" in result.stdout.lower():
        raise AssertionError("F1 mutant: must not be partial package")
    if "escreva status.json aqui" not in result.stdout:
        raise AssertionError(f"F1 diagnostic must say where to register:\n{result.stdout}")
    expect_ok(gathering_pkg(root, "registered-early"), "F1 positive: status.json sozinho é pacote")


def family_2_registration_vs_ready(root: Path) -> None:
    pkg = gathering_pkg(root, "gathering-no-prd")
    expect_ok(pkg, "F2 positive: gathering sem PRD")
    write_status(pkg, decision={"prd_status": "ready", "verdict": "prd_ready"})
    expect_fail(pkg, "exige PRD.md", "F2 mutant: ready sem PRD")


def family_3_phase_type_and_enum(root: Path) -> None:
    obj = gathering_pkg(root, "phase-object")
    write_status(obj, phases={"qa": {"status": "done", "note": "x"}})
    result = expect_fail(obj, "must be string", "F3 mutant: phases.* objeto")
    if "type" not in result.stdout.lower() and "must be string" not in result.stdout:
        raise AssertionError(f"F3 must be a named type failure:\n{result.stdout}")

    bad = gathering_pkg(root, "phase-unknown")
    write_status(bad, phases={"qa": "almost-done"})
    expect_fail(bad, "fora do vocabulário", "F3 mutant: string fora do enum")

    superseded = gathering_pkg(root, "phase-superseded")
    write_status(
        superseded,
        current_phase="inbox",
        phases={"inbox": "pending", "execute": "superseded", "qa": "pending"},
    )
    expect_ok(superseded, "F3 positive: superseded passa")
    skipped = gathering_pkg(root, "phase-skipped")
    write_status(
        skipped,
        current_phase="inbox",
        phases={"inbox": "pending", "execute": "skipped", "qa": "pending"},
    )
    complete = gathering_pkg(root, "phase-complete-no-ship")
    write_status(
        complete,
        current_phase="qa",
        decision={"prd_status": "blocked", "verdict": "needs_product_decision"},
        phases={"inbox": "skipped", "execute": "complete", "qa": "complete"},
    )
    expect_ok(skipped, "F3 positive: skipped passa")
    expect_ok(complete, "F3 positive: complete sem shipped passa")
    shipped = gathering_pkg(root, "phase-complete-shipped")
    write_status(
        shipped,
        current_phase="qa",
        decision={"prd_status": "blocked", "verdict": "needs_product_decision"},
        phases={"inbox": "skipped", "execute": "complete", "qa": "complete"},
        shipped={"pr": 1, "target": "dev"},
    )
    expect_ok(shipped, "F3 positive: complete com shipped passa; ship não mora em phases.*")

    import importlib.util

    spec = importlib.util.spec_from_file_location("validate_superflow", VALIDATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not (
        "superseded" in module.PHASE_VOCABULARY
        and "skipped" in module.PHASE_VOCABULARY
        and "complete" in module.PHASE_VOCABULARY
    ):
        raise AssertionError("F3: enum must keep complete, skipped and superseded")
    if module.normalize_phase_state("superseded") == module.normalize_phase_state("skipped"):
        raise AssertionError("F3: superseded must not collapse into skipped")
    if module.normalize_phase_state("superseded") == module.normalize_phase_state("complete"):
        raise AssertionError("F3: superseded must not collapse into complete")


def family_4_current_phase(root: Path) -> None:
    bad = gathering_pkg(root, "phase-pointer-vibe")
    write_status(bad, current_phase="vibe")
    expect_fail(bad, "current_phase='vibe'", "F4 mutant: fora dos oito nomes")

    missing = gathering_pkg(root, "phase-pointer-absent")
    data = json.loads((missing / "status.json").read_text(encoding="utf-8"))
    del data["current_phase"]
    data["phases"] = {"inbox": "complete", "analyst": "complete", "execute": "pending"}
    write_json(missing / "status.json", data)
    result = expect_fail(missing, "derive", "F4 mutant: current_phase ausente")
    if "analyst" not in result.stdout:
        raise AssertionError(
            f"F4 diagnostic must name the derivable value (last canonical complete):\n{result.stdout}"
        )


def family_5_campaign_obligation(root: Path) -> None:
    for folder in ("subspecs", "units", "plans", "crystallize"):
        mother = gathering_pkg(root, f"mother-{folder}", campaign=f"mother-{folder}")
        child = gathering_pkg(mother / folder, "01-filho")
        write_status(child, campaign=None)
        expect_fail(child, "filho exige campaign", f"F5 mutant: {folder}/ sem campaign")
        write_status(child, campaign=f"mother-{folder}")
        expect_ok(child, f"F5 positive: {folder}/ com campaign derivado")

    mother = gathering_pkg(root, "mother-no-self")
    gathering_pkg(mother / "minispecs", "01-filho", campaign="mother-no-self")
    write_status(
        mother,
        children_source={"glob": "minispecs/*/status.json", "campaign": "mother-no-self"},
    )
    expect_fail(mother, "mãe exige campaign", "F5 mutant: mãe sem campaign == id")
    write_status(mother, campaign="mother-no-self")
    expect_ok(mother, "F5 positive: mãe com campaign == id")


def family_6_mother_in_motor(root: Path) -> None:
    mother = gathering_pkg(
        root,
        "motor-mother",
        campaign="motor-mother",
        children_source={"glob": "minispecs/*/status.json", "campaign": "motor-mother"},
    )
    child = mother / "minispecs" / "01-filho"
    child.parent.mkdir()
    shutil.copytree(FIXTURE, child)
    write_status(child, id="01-filho", campaign="motor-mother")

    derived = run_campaign(mother, "--derive-campaign")
    if derived.returncode != 0:
        raise AssertionError(f"F6 derive-campaign must exit 0:\n{derived.stdout}")
    if "motor-mother" not in derived.stdout:
        raise AssertionError(f"F6 derive path must name the mother:\n{derived.stdout}")

    positive = run_campaign(mother, "--campaign", "motor-mother")
    if positive.returncode == 1:
        raise AssertionError(f"F6 motor must compute, not contract-error:\n{positive.stdout}")
    payload = json.loads(positive.stdout)
    ids = {pkg["id"] for pkg in payload["packages"]}
    if "motor-mother" not in ids:
        raise AssertionError(f"F6 positive: mother must enter the campaign by field:\n{positive.stdout}")

    write_status(mother, campaign=None)
    mutant = run_campaign(mother, "--campaign", "motor-mother")
    mutant_payload = json.loads(mutant.stdout)
    mutant_ids = {pkg["id"] for pkg in mutant_payload.get("packages", [])}
    if "motor-mother" in mutant_ids:
        raise AssertionError(
            f"F6 mutant: mother without campaign field must not enter the filter:\n{mutant.stdout}"
        )


def family_7_fossil(root: Path) -> None:
    pkg = gathering_pkg(root, "fossil-typed")
    expect_ok(pkg, "F7 positive: fóssil tipado sem handbook e sem PRD")
    (pkg / "HANDBOOK.md").write_text("# no\n", encoding="utf-8")
    expect_fail(pkg, "artifacts.handbook", "F7 mutant: handbook no disco sem ponteiro")


def family_8_handbook_diverges(root: Path) -> None:
    pkg = root / "handbook-diverge"
    shutil.copytree(FIXTURE, pkg)
    (pkg / "HANDBOOK.md").write_text(HANDBOOK_OK, encoding="utf-8")
    write_status(
        pkg,
        current_phase="execute",
        phases={"execute": "pending", "qa": "pending"},
        artifacts={"handbook": "HANDBOOK.md"},
        handbook=HANDBOOK_BLOCK,
    )
    expect_ok(pkg, "F8 positive: handbook diz entregue e phases.execute=pending")
    if "tudo entregue" not in (pkg / "HANDBOOK.md").read_text(encoding="utf-8").lower():
        raise AssertionError("F8 fixture must keep the diverging prose")


def family_9_dod_gate(root: Path) -> None:
    mother = root / "dod-mother"
    shutil.copytree(FIXTURE, mother)
    write_status(
        mother,
        id="dod-mother",
        campaign="dod-mother",
        children_source={"glob": "minispecs/*/status.json", "campaign": "dod-mother"},
    )
    child = mother / "minispecs" / "01-filho"
    child.parent.mkdir()
    shutil.copytree(FIXTURE, child)
    write_status(child, id="01-filho", campaign="dod-mother")

    prd = (mother / "PRD.md").read_text(encoding="utf-8")
    clean = prd.replace("SPEC + analysis mindset pass.", "Mother scope only, no child list.")
    (mother / "PRD.md").write_text(
        clean.replace("## Problem\nNeed clear plan change messaging.", "## Problem\nNeed 01-filho named only here."),
        encoding="utf-8",
    )
    expect_ok(mother, "F9 positive: child id fora do DoD passa")

    (mother / "PRD.md").write_text(
        clean.replace(
            "Mother scope only, no child list.",
            "Close 01-filho before declaring the mother done.",
        ),
        encoding="utf-8",
    )
    result = expect_fail(mother, "Definition of Complete", "F9 mutant: DoD nomeia filho")
    if "greppable" not in result.stdout.lower() and "paráfrase" not in result.stdout.lower():
        raise AssertionError(f"F9 diagnostic must admit it is greppable only:\n{result.stdout}")
    if "01-filho" not in result.stdout:
        raise AssertionError(f"F9 diagnostic must localize the child:\n{result.stdout}")


def family_d7_consumer_floor(root: Path) -> None:
    repo = root / "consumer"
    specs = repo / "specs" / "legacy-pkg"
    specs.mkdir(parents=True)
    write_json(specs / "status.json", {**GATHERING, "id": "legacy-pkg", "phases": {"qa": "done"}})
    expect_fail(specs, "fora do vocabulário", "D7 mutant: sem floor do consumidor, grafia crua falha")

    superflow = repo / ".superflow"
    superflow.mkdir()
    write_json(
        superflow / "config.json",
        {
            "schema_version": "superflow.config.v1",
            "specs": "specs",
            "destination": None,
            "floors": {"phase_vocabulary": "phase-vocabulary-floor.json"},
        },
    )
    write_json(superflow / "phase-vocabulary-floor.json", {"legacy-pkg": ["qa"]})
    expect_ok(specs, "D7 positive: floor lido do consumidor")

    source = VALIDATE.read_text(encoding="utf-8")
    if "PHASE_VOCABULARY_FLOOR =" in source or "/Users/marcoantonio/dietflow-app" in source:
        raise AssertionError("D7: plugin must not embed DietFlow paths or a hardcoded phase floor")


def main() -> int:
    source = VALIDATE.read_text(encoding="utf-8")
    if "prd_status" in source and "gathering" in source:
        if any(
            token in source
            for token in (
                'prd_status"] = "ready"',
                "prd_status = \"ready\"",
                "promote_to_ready",
            )
        ):
            raise AssertionError("validator must not promote gathering to ready")

    with tempfile.TemporaryDirectory(prefix="superflow-lifecycle.") as tmp:
        root = Path(tmp)
        family_1_unregistered(root)
        family_2_registration_vs_ready(root)
        family_3_phase_type_and_enum(root)
        family_4_current_phase(root)
        family_5_campaign_obligation(root)
        family_6_mother_in_motor(root)
        family_7_fossil(root)
        family_8_handbook_diverges(root)
        family_9_dod_gate(root)
        family_d7_consumer_floor(root)

    print("OK: superflow lifecycle contract tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
