#!/usr/bin/env python3
"""Behavioral tests for the handbook contract (H0-H9).

Um handbook é o retrato operável de uma spec: o que ela é, do que depende e
qual é o próximo trabalho útil. Ele só vale se estiver ancorado no código e se
o veredito nascer campo — prosa raspada por regex já provou errar.

Estes testes provam que o gate falha onde precisa falhar: seção ausente, seção
placeholder, Estado real sem âncoras, enum inválido, elegibilidade gravada,
fase fora do vocabulário, ratchet stale e filho órfão de campanha.
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
FIXTURE = SCRIPT_DIR.parent / "assets" / "fixtures" / "campaign" / "001-foundation"

HANDBOOK_OK = """# HANDBOOK — fixture

## Intenção
A fixture existe para provar que o contrato do handbook falha onde precisa
falhar, e não apenas onde é cômodo. Ela não descreve produto.

## Estado real
O gate vive em `plugins/superflow/scripts/validate_superflow.py:1` e a fixture
base em `plugins/superflow/assets/fixtures/campaign/001-foundation/status.json:1`.
O motor de campanha que consome o selo está em
`plugins/superflow/scripts/superflow_campaign.py:1`.

## Rastro
Nasceu junto do gate, na mesma fatia, sem PR anterior.

## Dificuldade e impacto
Baixa: é uma fixture de teste, sem consumidor de produto.

## Testes
Este proprio arquivo, executado por `python3 test_handbook_contract.py`.

## O que a linha não comporta
Não cobre render de HTML nem agregação entre repositórios.

## Relatório de leitura
Lidos: o validador inteiro e o motor de campanha. Não encontrado: consumidor de
painel — ele ainda não existe.
"""

HANDBOOK_BLOCK = {
    "read_at": "2026-09-09",
    "read_base": "chore/handbook-schema-e-gate@0000000",
    "index_action": "confirm_pending",
    "selo": "in_flight",
    "archivable": "no",
    "archive_debts": [],
    "open_decisions": [],
    "next_useful": [{"id": "N1", "kind": "implementation", "blocked_by": []}],
    "unanswered": [],
    "children_rollup": None,
}


def run(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATE), str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def expect_ok(path: Path, why: str) -> None:
    result = run(path)
    if result.returncode != 0:
        raise AssertionError(f"{why}: expected OK, got:\n{result.stdout}")


def expect_fail(path: Path, needle: str, why: str) -> None:
    result = run(path)
    if result.returncode == 0:
        raise AssertionError(f"{why}: expected FAIL, got OK:\n{result.stdout}")
    if needle.lower() not in result.stdout.lower():
        raise AssertionError(
            f"{why}: failure must name {needle!r}; got:\n{result.stdout}"
        )


def write_status(pkg: Path, **fields) -> None:
    path = pkg / "status.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(fields)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="superflow-handbook.") as tmp:
        root = Path(tmp)

        def fresh(name: str, *, handbook: str | None = HANDBOOK_OK, block=HANDBOOK_BLOCK) -> Path:
            pkg = root / name
            shutil.copytree(FIXTURE, pkg)
            if handbook is not None:
                (pkg / "HANDBOOK.md").write_text(handbook, encoding="utf-8")
                data = json.loads((pkg / "status.json").read_text(encoding="utf-8"))
                data["artifacts"]["handbook"] = "HANDBOOK.md"
                if block is not None:
                    data["handbook"] = json.loads(json.dumps(block))
                (pkg / "status.json").write_text(
                    json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
                )
            return pkg

        # H0 — o caminho feliz continua verde
        expect_ok(fresh("h0-happy"), "H0 handbook completo")
        expect_ok(fresh("h0-none", handbook=None), "H0 pacote sem handbook")

        # H1 — secao obrigatoria ausente
        pkg = fresh("h1-missing", handbook=HANDBOOK_OK.replace("## Testes", "## Provinha"))
        expect_fail(pkg, "## Testes", "H1 seção ausente")

        # H2 — secao placeholder
        pkg = fresh(
            "h2-placeholder",
            handbook=HANDBOOK_OK.replace(
                "Baixa: é uma fixture de teste, sem consumidor de produto.", "TBD"
            ),
        )
        expect_fail(pkg, "placeholder", "H2 seção placeholder")

        # H3 — Estado real sem as tres ancoras arquivo:linha
        pkg = fresh(
            "h3-anchors",
            handbook=HANDBOOK_OK.replace(
                "`plugins/superflow/scripts/superflow_campaign.py:1`",
                "o motor de campanha",
            ).replace(
                "`plugins/superflow/assets/fixtures/campaign/001-foundation/status.json:1`",
                "a fixture base",
            ),
        )
        expect_fail(pkg, "âncora", "H3 Estado real sem evidência")

        # H4 — ponteiro e bloco
        pkg = fresh("h4-no-pointer")
        data = json.loads((pkg / "status.json").read_text(encoding="utf-8"))
        data["artifacts"]["handbook"] = None
        (pkg / "status.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        expect_fail(pkg, "artifacts.handbook", "H4 handbook sem ponteiro")

        pkg = fresh("h4-no-block", block=None)
        expect_fail(pkg, "bloco `handbook`", "H4 handbook sem bloco no status")

        for field, bad in [("selo", "fechada"), ("index_action", "arquivar"), ("archivable", "?")]:
            pkg = fresh(f"h4-enum-{field}", block={**HANDBOOK_BLOCK, field: bad})
            expect_fail(pkg, f"handbook.{field}", f"H4 enum {field}")

        # H5 — elegibilidade e derivada, nunca gravada
        pkg = fresh(
            "h5-derived",
            block={
                **HANDBOOK_BLOCK,
                "next_useful": [
                    {"id": "N1", "kind": "implementation", "blocked_by": [], "eligible": True}
                ],
            },
        )
        expect_fail(pkg, "DERIVADA", "H5 elegibilidade gravada")

        pkg = fresh("h5-tasks", block={**HANDBOOK_BLOCK, "tasks": [{"id": "T1"}]})
        expect_fail(pkg, "implementation_plan.json", "H5 tasks no handbook")

        # H6 — vocabulario de fases, em ratchet
        pkg = fresh("h6-vocab", handbook=None)
        write_status(pkg, phases={**json.loads((pkg / "status.json").read_text())["phases"], "qa": "done"})
        expect_fail(pkg, "fora do vocabulário", "H6 grafia fora do vocabulário")

        pkg = fresh("h6-superseded", handbook=None)
        write_status(
            pkg,
            current_phase="execute",
            phases={
                **json.loads((pkg / "status.json").read_text())["phases"],
                "execute": "complete",
                "qa": "superseded",
            },
        )
        expect_ok(pkg, "H6 superseded é canônico")

        # H7 — filho (ancestral com status.json) precisa do campaign derivado
        mother = root / "h7-mother"
        shutil.copytree(FIXTURE, mother)
        write_status(mother, id="h7-mother", campaign="h7-mother")
        child = mother / "minispecs" / "01-filho"
        child.parent.mkdir()
        shutil.copytree(FIXTURE, child)
        write_status(child, id="01-filho", campaign=None)
        expect_fail(child, "campaign", "H7 filho sem campaign")
        write_status(child, campaign="outra-campanha")
        expect_fail(child, "valor derivado", "H7 filho de outra campanha")
        write_status(child, campaign="h7-mother")
        expect_ok(child, "H7 filho alinhado ao pai")

        # H8 — children_source e o rollup cacheado
        write_status(
            mother,
            children_source={"glob": "minispecs/*/status.json", "campaign": "h7-mother"},
        )
        expect_ok(mother, "H8 pacote-mae com filho alinhado")
        write_status(child, campaign="fixture-campaign")
        expect_fail(mother, "órfão", "H8 filho órfão derruba o pai")

    ratchet_stale_shrinks_only()

    print("OK: superflow handbook contract tests")
    return 0


def ratchet_stale_shrinks_only() -> None:
    """H9 — entrada de FLOOR que não viola mais precisa falhar.

    Ratchet que só avisa vira allowlist eterna. Como o FLOOR é keyed pelo path
    relativo a `specs/`, este caso é testado em processo: o subprocess não tem
    como plantar um pacote dentro do FLOOR congelado.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("validate_superflow", VALIDATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    canonical = {"phases": {"qa": "complete"}}
    floor = {"fixture-stale": ("qa",)}
    try:
        module.validate_phase_vocabulary(
            canonical, label="fixture", floor_key="fixture-stale", floor=floor
        )
    except SystemExit:
        pass
    else:
        raise AssertionError("H9: FLOOR stale deve falhar; o ratchet só encolhe")

    legacy = {"phases": {"qa": "done"}}
    module.validate_phase_vocabulary(
        legacy, label="fixture", floor_key="fixture-stale", floor=floor
    )

    module.validate_phase_vocabulary(
        {"phases": None}, label="fixture", floor_key="fixture-stale"
    )


if __name__ == "__main__":
    raise SystemExit(main())
