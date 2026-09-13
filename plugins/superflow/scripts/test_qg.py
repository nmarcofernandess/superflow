#!/usr/bin/env python3
"""Focused proofs for the feed-v2 QG renderer.

Run with ``python3 -I plugins/superflow/scripts/test_qg.py``. The explicit
import bootstrap below is intentional: isolated mode must not inherit a local
PYTHONPATH or a globally installed Superflow package.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_DIR = Path(__file__).resolve().parent
QG_PATH = SCRIPT_DIR / "superflow_qg.py"
TEMPLATE = SCRIPT_DIR.parent / "assets" / "qg.html"


def load_renderer():
    spec = importlib.util.spec_from_file_location("superflow_qg_under_test", QG_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("não foi possível carregar superflow_qg.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


QG = load_renderer()


def record(identifier: str, **changes: Any) -> Dict[str, Any]:
    value: Dict[str, Any] = {
        "id": identifier,
        "title": "Ticket " + identifier,
        "path": "specs/" + identifier,
        "phase": "plan",
        "state": "pending",
        "prd": "ready",
        "archived": False,
        "depends_on": [],
        "absorbed_by": None,
        "waiting_for": None,
        "parent_id": None,
        "evidence": [],
        "updated_at": "2026-09-13T12:00:00Z",
        "body_md": "",
        "tasks": [],
        "blockers": [],
    }
    value.update(changes)
    return value


def feed(records: List[Dict[str, Any]], diagnostics: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "schema_version": "superflow.feed.v2",
        "generated_at": "2026-09-13T12:00:00Z",
        "snapshot_id": "fixture-qg",
        "source_revision": None,
        "records": records,
        "diagnostics": diagnostics if diagnostics is not None else [],
    }


def embedded(page: str, identifier: str) -> Any:
    pattern = r'<script type="application/json" id="' + re.escape(identifier) + r'">(.*?)</script>'
    match = re.search(pattern, page, re.S)
    if not match:
        raise AssertionError("bloco JSON ausente: " + identifier)
    return json.loads(match.group(1))


def test_renderer_is_a_template_only_boundary(root: Path) -> None:
    source = QG_PATH.read_text(encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")
    for forbidden in ("argparse", "subprocess", "superflow_status", "validate_superflow", "task-board"):
        if forbidden in source:
            raise AssertionError("renderer ainda depende de " + forbidden)
    for forbidden in ("task-board", "board-data", "localStorage", "sessionStorage", "fetch(", "XMLHttpRequest", "fonts.googleapis.com"):
        if forbidden in template:
            raise AssertionError("template QG reteve dependência proibida: " + forbidden)
    if template.count("__QG_SNAPSHOT__") != 1 or template.count("__QG_LINKS__") != 1:
        raise AssertionError("template precisa de um marcador para snapshot e links")
    before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())
    page = QG.render(feed([]), root)
    after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())
    if before != after:
        raise AssertionError("render não pode escrever no projeto")
    if "<html" not in page.lower() or "qg-snapshot" not in page:
        raise AssertionError("render precisa devolver uma página HTML completa")


def test_zero_one_and_thousand_records(root: Path) -> None:
    zero = QG.render(feed([]), root)
    if embedded(zero, "qg-snapshot")["records"] != []:
        raise AssertionError("QG vazio deve conservar feed vazio")
    if "Nenhum ticket foi encontrado nesta fotografia." not in zero:
        raise AssertionError("QG vazio não explica a ausência de tickets")

    long_title = "Título longo " + ("muito útil para verificar quebra de linha " * 14)
    one_input = feed([record("um", title=long_title)])
    one_before = copy.deepcopy(one_input)
    one = QG.render(one_input, root)
    if embedded(one, "qg-snapshot") != one_before:
        raise AssertionError("o renderer precisa preservar a fotografia recebida")
    if long_title not in one:
        raise AssertionError("título longo perdeu dados no snapshot")

    thousand_records = [record("ticket-%04d" % index, title="Ticket de teste %04d" % index) for index in range(1000)]
    thousand = QG.render(feed(thousand_records), root)
    snapshot = embedded(thousand, "qg-snapshot")
    if len(snapshot["records"]) != 1000:
        raise AssertionError("QG deve embutir todos os mil tickets")
    if 'value="50"' not in thousand or 'value="1000"' not in thousand:
        raise AssertionError("QG precisa oferecer paginação de 50 e 1.000 itens")


def test_links_and_untrusted_text_are_safe(root: Path) -> None:
    spec_path = root / "specs" / "alpha"
    proof_path = root / "proofs" / "alpha-proof.html"
    spec_path.mkdir(parents=True)
    proof_path.parent.mkdir(parents=True)
    proof_path.write_text("proof\n", encoding="utf-8")
    malicious = '</script><img src=x onerror="window.qgPwned=1">'
    with tempfile.TemporaryDirectory(prefix="superflow-qg-external.") as external_dir:
        external_proof = Path(external_dir) / "proof.png"
        external_proof.write_text("image placeholder\n", encoding="utf-8")
        item = record(
            "alpha",
            title=malicious,
            path="specs/alpha",
            body_md=malicious,
            evidence=["proofs/alpha-proof.html", external_proof.as_uri(), "https://ci.example.test/run/7", "javascript:alert(1)", malicious],
        )
        page = QG.render(feed([item]), root)
        if QG.safe_link(str(external_proof), root) is not None:
            raise AssertionError("arquivo externo exige referência file:/// explícita")
        if QG.safe_link(external_proof.as_uri(), root) != external_proof.resolve().as_uri():
            raise AssertionError("file:/// externo e existente precisa permanecer navegável")

    if malicious in page:
        raise AssertionError("texto hostil não pode sair do JSON inerte")
    if "\\u003c/script\\u003e" not in page:
        raise AssertionError("fechamento de script precisa ser escapado")
    if 'href="javascript:' in page.lower():
        raise AssertionError("URL hostil virou atributo executável")
    links = embedded(page, "qg-links")
    if links["record_paths"] != [spec_path.resolve().as_uri()]:
        raise AssertionError("caminho existente do ticket deve virar link local seguro")
    expected = [proof_path.resolve().as_uri(), external_proof.resolve().as_uri(), "https://ci.example.test/run/7", None, None]
    if links["evidence"] != [expected]:
        raise AssertionError("só URLs permitidas e arquivos existentes podem virar links")
    if QG.safe_link("../fora-do-root", root) is not None:
        raise AssertionError("referência relativa não pode escapar do root")
    if QG.safe_link("file://example.test/etc/passwd", root) is not None:
        raise AssertionError("host remoto em file:// não pode virar link")
    if QG.safe_link("file:../../../../etc/passwd", root) is not None:
        raise AssertionError("file relativo não pode escapar do root")
    if QG.safe_link("file:/etc/passwd", root) is not None:
        raise AssertionError("file absoluto exige três barras")
    if QG.safe_link("data:text/html,boom", root) is not None:
        raise AssertionError("data URL não pode virar link")


def test_relationships_and_diagnostics_are_preserved(root: Path) -> None:
    parent = record("base", title="Base concluída", phase="done", state=None)
    child = record(
        "complemento",
        title="Complemento aberto",
        parent_id="base",
        depends_on=["base", "fora-do-filtro"],
        waiting_for="Validação humana do aceite",
        blockers=[
            {"kind": "dependency", "ref": "fora-do-filtro", "reason": "Ainda não entregue."},
            {"kind": "human", "ref": None, "reason": "Aguarda decisão."},
        ],
        body_md="",
        tasks=[{"id": "T01", "behavior": "Mostrar relações", "status": "in_progress", "acceptance": "AC02"}],
    )
    unrelated = record("fora-do-filtro", phase="analyst", state="paused", archived=True)
    diagnostics = [{"path": "specs/conflito/status.md", "code": "ID_DUPLICADO", "message": "ID em conflito: <alpha>", "severity": "error"}]
    page = QG.render(feed([parent, child, unrelated], diagnostics), root)
    if "ID em conflito: <alpha>" in page:
        raise AssertionError("diagnóstico hostil não pode sair do JSON inerte")
    if "Nenhuma seleção salva" in page:
        raise AssertionError("QG não deve introduzir seleção persistida")
    snapshot = embedded(page, "qg-snapshot")
    if snapshot["diagnostics"] != diagnostics:
        raise AssertionError("diagnóstico precisa permanecer na fotografia")
    if snapshot["records"][1]["parent_id"] != "base" or snapshot["records"][1]["depends_on"] != ["base", "fora-do-filtro"]:
        raise AssertionError("relações foram alteradas durante a projeção")


def jsdom_path() -> Path:
    candidates = [
        Path(os.environ.get("QG_JSDOM", "__missing_jsdom__")),
        SCRIPT_DIR.parent.parent.parent / "node_modules" / "jsdom",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def test_browser_dom_smoke(root: Path) -> None:
    if shutil.which("node") is None or jsdom_path() is None:
        print("SKIP test_browser_dom_smoke: node/jsdom local indisponível")
        return
    parent = record("base", title="Base concluída", phase="done", state=None)
    child = record("complemento", parent_id="base", depends_on=["base"], phase="plan", state="pending")
    records = [parent, child]
    records.extend(record("ticket-%04d" % index, title="Ticket de teste %04d" % index) for index in range(2, 1000))
    page = QG.render(feed(records), root)
    with tempfile.TemporaryDirectory(prefix="superflow-qg-dom.") as temp_dir:
        page_path = Path(temp_dir) / "qg.html"
        page_path.write_text(page, encoding="utf-8")
        script = r'''
const fs = require("fs");
const { JSDOM } = require(process.env.QG_JSDOM);
const dom = new JSDOM(fs.readFileSync(process.argv[1], "utf8"), {
  runScripts: "dangerously", url: "file:///qg.html"
});
const w = dom.window;
const d = w.document;
function fail(message) { throw new Error(message); }
if (d.querySelectorAll("[data-qg-record]").length !== 50) fail("initial page needs 50 records");
if (d.querySelector("#qg-archived").value !== "all") fail("archived must start included");
const search = d.querySelector("#qg-search");
search.value = "ticket-0999";
search.dispatchEvent(new w.Event("input", { bubbles: true }));
if (d.querySelectorAll("[data-qg-record]").length !== 1) fail("search must inspect all 1000 records");
w.location.hash = "#base";
w.dispatchEvent(new w.Event("hashchange"));
if (d.querySelector("#qg-detail").getAttribute("data-qg-detail-id") !== "base") fail("hash must select detail by ID");
const phase = d.querySelector("#qg-phase");
phase.value = "plan";
phase.dispatchEvent(new w.Event("change", { bubbles: true }));
if (d.querySelector("#qg-outside-filter").hidden) fail("detail outside filter needs an explicit notice");
const noScript = Array.from(d.querySelectorAll("script")).every((node) => node.src === "");
if (!noScript) fail("QG must not require an external script");
dom.window.close();
'''
        environment = dict(os.environ)
        environment["QG_JSDOM"] = str(jsdom_path())
        result = subprocess.run(
            ["node", "-e", script, str(page_path)],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
    if result.returncode:
        raise AssertionError("DOM smoke failed:\n" + result.stdout + result.stderr)


def main() -> int:
    tests = [
        test_renderer_is_a_template_only_boundary,
        test_zero_one_and_thousand_records,
        test_links_and_untrusted_text_are_safe,
        test_relationships_and_diagnostics_are_preserved,
        test_browser_dom_smoke,
    ]
    failed = 0
    for test in tests:
        with tempfile.TemporaryDirectory(prefix="superflow-qg.") as temp_dir:
            try:
                test(Path(temp_dir))
                print("OK  " + test.__name__)
            except Exception as exc:  # noqa: BLE001 - each proof should report independently
                failed += 1
                print("FAIL " + test.__name__ + ": " + str(exc))
    if failed:
        print("FAILED %d/%d" % (failed, len(tests)))
        return 1
    print("OK: superflow qg tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
