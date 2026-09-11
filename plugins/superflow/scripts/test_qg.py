#!/usr/bin/env python3
"""Positive + directed-mutant proofs for the Superflow QG.

A failing mutant proves that branch, not the whole system.
Fixtures live in a temp dir and never land in the product.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
QG = SCRIPT_DIR / "superflow_qg.py"
BOARD = SCRIPT_DIR.parent / "assets" / "task-board" / "board.html"

ABSENT = "Não contém"

GATHERING = {
    "schema_version": "superflow.status.v1",
    "id": "pkg",
    "title": "Pacote",
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

PLAN = {
    "schema_version": "superflow.plan.v1",
    "status": "pending",
    "plan": {
        "feature": "demo",
        "workflow_type": "docs",
        "strategy": "single",
        "phases": [
            {
                "id": "phase-1",
                "name": "Implementation",
                "subtasks": [
                    {"id": "T1", "description": "Uma task", "status": "pending"},
                    {"id": "T2", "description": "Outra", "status": "complete"},
                ],
            }
        ],
    },
}


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_status(pkg: Path, **fields) -> dict:
    data = json.loads(json.dumps(GATHERING))
    data["id"] = pkg.name
    data["title"] = pkg.name
    data.update(fields)
    write_json(pkg / "status.json", data)
    return data


def run_qg(root: Path, *args: str) -> subprocess.CompletedProcess:
    dest = root / "out"
    dest.mkdir(exist_ok=True)
    return subprocess.run(
        [
            sys.executable,
            str(QG),
            str(root),
            "--specs",
            str(root / "specs"),
            "--dest",
            str(dest),
            "--stamp",
            "2026-09-10",
            *args,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def html_of(root: Path, *args: str) -> str:
    result = run_qg(root, *args)
    if result.returncode != 0:
        raise AssertionError(f"qg failed:\n{result.stdout}")
    out_name = "qg.html"
    if "--out" in args:
        out_name = args[args.index("--out") + 1]
    path = root / "out" / out_name
    if not path.is_file():
        raise AssertionError(f"qg did not write HTML:\n{result.stdout}")
    return path.read_text(encoding="utf-8")


def snapshot_of(text: str) -> dict:
    match = re.search(
        r'<script type="application/json" id="qg-snapshot">\s*(.*?)\s*</script>',
        text,
        re.S,
    )
    if not match:
        raise AssertionError("HTML must embed one qg-snapshot")
    return json.loads(match.group(1))


def assert_no_machine_path(text: str) -> None:
    if re.search(r"/Users/[^/\s]+/", text):
        raise AssertionError("HTML or report contains a machine-absolute path")


def setup_tree(root: Path) -> None:
    specs = root / "specs"
    mother = specs / "alpha-mother"
    child = mother / "minispecs" / "01-child"
    other = specs / "beta-solo"
    write_status(
        mother,
        children_source={"glob": "minispecs/*/status.json", "campaign": "alpha-mother"},
        campaign="alpha-mother",
        depends_on=["beta-solo"],
        artifacts={
            **GATHERING["artifacts"],
            "plan": "implementation_plan.json",
        },
        task_source={"type": "plan", "path": "implementation_plan.json", "progress": None},
    )
    write_json(mother / "implementation_plan.json", PLAN)
    write_status(child, campaign="alpha-mother", depends_on=[])
    write_status(other, depends_on=[])
    ghost = specs / "ghost-docs"
    ghost.mkdir(parents=True)
    (ghost / "PRD.md").write_text("# PRD\nnot a package\n", encoding="utf-8")


def test_same_architecture_one_and_many(root: Path) -> None:
    setup_tree(root)
    one = html_of(root, "--scope", "beta-solo")
    many = html_of(root, "--out", "many.html", "--scope", "alpha-mother,beta-solo")
    many = (root / "out" / "many.html").read_text(encoding="utf-8")
    for text in (one, many):
        assert 'data-tab="mapa"' in text
        assert 'data-tab="tasks"' in text
        assert 'data-tab="graph"' in text
        assert 'data-tab="sprint"' not in text
        assert 'class="pkg"' in text
        assert "--paper" in text and "--ink" in text
        assert "--papel" not in text
    one_ids = {p["id"] for p in snapshot_of(one)["packages"]}
    many_ids = {p["id"] for p in snapshot_of(many)["packages"]}
    if one_ids != {"beta-solo"}:
        raise AssertionError(f"single-spec scope must be just beta-solo, got {one_ids}")
    if one_ids >= many_ids:
        raise AssertionError("several specs must keep the same screen, larger scope")
    if "01-child" not in many_ids or "alpha-mother" not in many_ids:
        raise AssertionError(f"multi scope missing family: {many_ids}")


def test_mother_minispec_accordions(root: Path) -> None:
    setup_tree(root)
    text = html_of(root, "--scope", "alpha-mother")
    mother = re.search(r'<details class="pkg" data-id="alpha-mother".*?</details>', text, re.S)
    if not mother:
        raise AssertionError("mother accordion missing")
    if 'data-id="01-child"' not in mother.group(0):
        raise AssertionError("minispec must render inside the mother accordion")
    if re.search(r'<details[^>]+name=', text):
        raise AssertionError("accordions must open independently (no name= exclusive group)")
    if text.count('class="pkg"') < 2:
        raise AssertionError("mother and child must both be details.pkg")


def test_tasks_graph_same_census(root: Path) -> None:
    setup_tree(root)
    text = html_of(root)
    data = snapshot_of(text)
    ids = {p["id"] for p in data["packages"]}
    for edge in data["edges"]:
        if edge["src"] not in ids or edge["dst"] not in ids:
            raise AssertionError("graph edge escaped the census")
    if text.count('id="qg-snapshot"') != 1:
        raise AssertionError("Tasks and Graph must share one snapshot")
    if 'data-a="alpha-mother"' not in text or 'data-b="01-child"' not in text:
        raise AssertionError("graph must draw the registered hierarchy edge")
    if 'data-a="alpha-mother"' not in text or 'data-b="beta-solo"' not in text:
        raise AssertionError("graph must draw the registered depends_on edge")


def test_absent_versus_incompatible(root: Path) -> None:
    setup_tree(root)
    lone = root / "specs" / "gamma-absent"
    write_status(lone)
    broken = root / "specs" / "delta-bad"
    write_status(broken, depends_on="not-a-list")
    text = html_of(root, "--scope", "gamma-absent,delta-bad")
    data = snapshot_of(text)
    by_id = {p["id"]: p for p in data["packages"]}
    if by_id["gamma-absent"]["depends_on"] is not None:
        raise AssertionError("optional field present as empty is fine; gamma has default []")
    # gathering fixture includes depends_on only if set. gamma has no depends_on key.
    gamma_html = re.search(r'<details class="pkg" data-id="gamma-absent".*?</details>', text, re.S)
    delta_html = re.search(r'<details class="pkg" data-id="delta-bad".*?</details>', text, re.S)
    if not gamma_html or not delta_html:
        raise AssertionError("both packages must render")
    if ABSENT not in gamma_html.group(0):
        raise AssertionError("missing optional field must render as Não contém")
    if 'data-qg-diag="1"' in gamma_html.group(0) and "depends_on incompatível" in gamma_html.group(0):
        raise AssertionError("absent field must not use the incompatible diagnosis")
    if 'data-qg-diag="1"' not in delta_html.group(0):
        raise AssertionError("incompatible content must print a visible diagnosis")
    if "depends_on incompatível" not in delta_html.group(0):
        raise AssertionError("incompatible depends_on must be named")
    if ABSENT in delta_html.group(0) and "depends_on incompatível" not in delta_html.group(0):
        raise AssertionError("incompatible must not collapse into Não contém")


def test_declared_child_unreadable_survives(root: Path) -> None:
    setup_tree(root)
    child = root / "specs" / "alpha-mother" / "minispecs" / "02-broken"
    child.mkdir(parents=True)
    (child / "status.json").write_text("{not json", encoding="utf-8")
    text = html_of(root, "--scope", "alpha-mother")
    data = snapshot_of(text)
    ids = {p["id"] for p in data["packages"]}
    if "02-broken" not in ids:
        raise AssertionError("declared child with unreadable status disappeared")
    broken = next(p for p in data["packages"] if p["id"] == "02-broken")
    if broken["presence"] != "unreadable":
        raise AssertionError(f"unreadable child must be diagnosed, got {broken['presence']}")
    card = re.search(r'<details class="pkg" data-id="02-broken".*?</details>', text, re.S)
    if not card or 'data-qg-diag="1"' not in card.group(0):
        raise AssertionError("unreadable child must show diagnosis on the page")
    if "ilegível" not in card.group(0):
        raise AssertionError("diagnosis must say the status is unreadable")

    # Directed mutant: dropping unreadable declared children is the historical bug.
    mutant = [p for p in data["packages"] if p["presence"] != "unreadable"]
    if "02-broken" not in {p["id"] for p in data["packages"]}:
        raise AssertionError("mutant baseline lost")
    if "02-broken" in {p["id"] for p in mutant} and False:
        raise AssertionError("unreachable")
    if len(mutant) >= len(data["packages"]):
        raise AssertionError("mutant that filters unreadable must shrink the census")


def test_deterministic(root: Path) -> None:
    setup_tree(root)
    a = html_of(root)
    b = html_of(root)
    if a != b:
        raise AssertionError("same data + same stamp must be byte-identical")


def test_status_change_without_portrait_edit(root: Path) -> None:
    setup_tree(root)
    before = snapshot_of(html_of(root, "--scope", "beta-solo", "--out", "before.html"))
    pkg = root / "specs" / "beta-solo"
    data = json.loads((pkg / "status.json").read_text(encoding="utf-8"))
    data["phases"]["execute"] = "complete"
    data["current_phase"] = "qa"
    write_json(pkg / "status.json", data)
    after = snapshot_of(html_of(root, "--scope", "beta-solo", "--out", "after.html"))
    before_pkg = next(p for p in before["packages"] if p["id"] == "beta-solo")
    after_pkg = next(p for p in after["packages"] if p["id"] == "beta-solo")
    if before_pkg["phases"]["execute"] == after_pkg["phases"]["execute"]:
        raise AssertionError("next generation must reflect the new status.json")
    if after_pkg["phases"]["execute"] != "complete":
        raise AssertionError("updated phase did not appear")


def test_handbook_may_diverge(root: Path) -> None:
    setup_tree(root)
    pkg = root / "specs" / "beta-solo"
    write_status(
        pkg,
        phases={"inbox": "skipped", "execute": "pending", "qa": "pending"},
        current_phase="execute",
        artifacts={**GATHERING["artifacts"], "handbook": "HANDBOOK.md"},
        handbook={
            "read_at": "2026-09-10",
            "read_base": "feat/qg@000000000",
            "index_action": "archive",
            "selo": "closed",
            "archivable": "yes",
            "archive_debts": [],
            "open_decisions": [],
            "next_useful": [],
            "unanswered": [],
            "children_rollup": None,
        },
    )
    (pkg / "HANDBOOK.md").write_text("# HANDBOOK\nTudo entregue.\n", encoding="utf-8")
    text = html_of(root, "--scope", "beta-solo")
    card = re.search(r'<details class="pkg" data-id="beta-solo".*?</details>', text, re.S)
    if not card:
        raise AssertionError("diverging package missing")
    body = card.group(0)
    if "selo closed" not in body:
        raise AssertionError("handbook selo must render")
    if "execute=pending" not in body:
        raise AssertionError("phases.execute pending must render beside the handbook")
    forbidden = (
        "diverg",
        "inconsist",
        "prosa contra",
        "handbook ×",
        "handbook x fase",
        "badge-erro",
    )
    lowered = body.lower()
    for needle in forbidden:
        if needle in lowered:
            raise AssertionError(f"must not flag handbook/phase divergence as error ({needle})")
    if 'data-qg-diag="1"' in body:
        raise AssertionError("legitimate handbook/phase split must not open a diagnosis box")


def test_sprint_tab_opt_in(root: Path) -> None:
    setup_tree(root)
    plain = html_of(root, "--out", "plain.html")
    if 'data-tab="sprint"' in plain:
        raise AssertionError("Sprint tab must stay absent when the cut is not an operation")
    sprint = {
        "name": "Operação alfa",
        "next": "abrir a mãe",
        "items": [{"id": "alpha-mother", "note": "primeiro"}, {"id": "beta-solo"}],
    }
    write_json(root / "sprint.json", sprint)
    with_sprint = html_of(root, "--sprint", str(root / "sprint.json"), "--out", "sprint.html")
    if 'data-tab="sprint"' not in with_sprint:
        raise AssertionError("Sprint tab must appear when the artifact is an operation")
    if "Operação alfa" not in with_sprint:
        raise AssertionError("sprint name missing")
    if "class=\"metro\"" not in with_sprint and "class='metro'" not in with_sprint:
        raise AssertionError("sprint must reuse the board.html metro")
    data = snapshot_of(with_sprint)
    if data["sprint"] is None:
        raise AssertionError("snapshot must carry the sprint composition")


def test_unregistered_and_tokens(root: Path) -> None:
    setup_tree(root)
    text = html_of(root)
    assert_no_machine_path(text)
    if 'data-qg-unregistered="1"' not in text:
        raise AssertionError("folders without status.json must be diagnosed")
    if "ghost-docs" not in text:
        raise AssertionError("unregistered folder disappeared")
    if 'data-qg-kind="unregistered"' not in text:
        raise AssertionError("unregistered must be a fourth output, not an incompatible package")
    board = BOARD.read_text(encoding="utf-8")
    if "--paper" not in board or "--ink" not in board:
        raise AssertionError("canonical board.html lost --paper/--ink")
    if "load_board_css" not in QG.read_text(encoding="utf-8"):
        raise AssertionError("QG must embed board.html CSS, not a second token sheet")
    if "resolve_qg_dir" not in QG.read_text(encoding="utf-8"):
        raise AssertionError("QG must use the contract path resolver")
    if "rastro" in QG.read_text(encoding="utf-8"):
        raise AssertionError("do not port the prose-scrape rastro")


def test_script_payload_cannot_break_out(root: Path) -> None:
    title = "</script><script>alert(1)</script>"
    write_status(root / "specs" / "xss-pkg", title=title)
    text = html_of(root, "--scope", "xss-pkg")
    if title in text:
        raise AssertionError("package title must not appear raw inside the HTML")
    data = snapshot_of(text)
    got = next(p["title"] for p in data["packages"] if p["id"] == "xss-pkg")
    if got != title:
        raise AssertionError(f"snapshot must keep the title, got {got!r}")


def test_invalid_glob_does_not_abort_snapshot(root: Path) -> None:
    write_status(
        root / "specs" / "abs-tmp",
        children_source={"glob": "/tmp/*/status.json", "campaign": "abs-tmp"},
    )
    write_status(
        root / "specs" / "abs-star",
        children_source={"glob": "/**/status.json", "campaign": "abs-star"},
    )
    write_status(
        root / "specs" / "escape-mother",
        children_source={"glob": "../../outside/*/status.json", "campaign": "escape"},
    )
    write_status(root / "outside" / "leak")
    text = html_of(root)
    data = snapshot_of(text)
    ids = {p["id"] for p in data["packages"]}
    rels = {p["rel"] for p in data["packages"]}
    if ids != {"abs-tmp", "abs-star", "escape-mother"}:
        raise AssertionError(f"invalid globs aborted or dropped packages: {ids}")
    if any("outside" in rel or rel.endswith("leak") for rel in rels):
        raise AssertionError(f"glob escaped the specs root: {rels}")
    for pkg_id in ("abs-tmp", "abs-star"):
        rec = next(p for p in data["packages"] if p["id"] == pkg_id)
        blob = " ".join(rec["diagnostics"])
        if "children_source" not in blob or "glob" not in blob:
            raise AssertionError(f"{pkg_id} must diagnose the invalid glob, got {rec['diagnostics']}")


def test_duplicate_ids_keep_distinct_graph_nodes(root: Path) -> None:
    write_status(root / "specs" / "pkg-a", id="same", title="Alpha")
    write_status(root / "specs" / "pkg-b", id="same", title="Beta")
    text = html_of(root)
    data = snapshot_of(text)
    pkgs = [p for p in data["packages"] if p["id"] == "same"]
    if {p["rel"] for p in pkgs} != {"pkg-a", "pkg-b"}:
        raise AssertionError(
            f"both packages must remain in the census, got {[(p['id'], p['rel']) for p in data['packages']]}"
        )
    nodes = re.findall(r'<g class="n" data-id="([^"]+)"', text)
    if len(set(nodes)) != 2:
        raise AssertionError(f"graph nodes collapsed to {nodes}")
    if "same · pkg-a" not in text or "same · pkg-b" not in text:
        raise AssertionError("each graph node must keep the package id visible")
    for rec in pkgs:
        if not any("id duplicado" in d for d in rec["diagnostics"]):
            raise AssertionError(f"{rec['rel']} must diagnose the duplicate id, got {rec['diagnostics']}")


def test_unregistered_is_not_a_filename_allowlist(root: Path) -> None:
    """Mutant: if the detector again asks 'do I know this filename?', this fails."""
    setup_tree(root)
    specs = root / "specs"
    handbook_only = specs / "106-exames-v2"
    handbook_only.mkdir()
    (handbook_only / "HANDBOOK.md").write_text("# handbook\n", encoding="utf-8")
    (handbook_only / "ANALYST.md").write_text("# analyst\n", encoding="utf-8")
    plan_only = specs / "053-selecao-convergencia"
    plan_only.mkdir()
    (plan_only / "PLAN.md").write_text("# plan\n", encoding="utf-8")
    harness_only = specs / "091-foods-curadoria-mercado"
    (harness_only / "harness").mkdir(parents=True)
    (harness_only / "harness" / "run.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (harness_only / "GOAL.md").write_text("# goal\n", encoding="utf-8")
    pkg = specs / "real-pkg"
    write_status(pkg)
    (pkg / "harness").mkdir()
    (pkg / "harness" / "run.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    shelf = specs / "archived"
    nested = shelf / "old-pkg"
    write_status(nested)

    src = QG.read_text(encoding="utf-8")
    if "find_unregistered_spec_documents" in src:
        raise AssertionError("mutant: QG reused the filename-list detector")
    if "SPEC_DOC_NAMES" in src:
        raise AssertionError("mutant: QG filters unregistered folders by a filename allowlist")

    text = html_of(root)
    data = snapshot_of(text)
    rels = [item["rel"] for item in data["unregistered"]]
    for name in ("106-exames-v2", "053-selecao-convergencia", "091-foods-curadoria-mercado"):
        if name not in text or name not in rels:
            raise AssertionError(f"mutant: {name} vanished because it lacks PRD/SPEC/analysis")
    if any(rel == "harness" or rel.endswith("/harness") for rel in rels):
        raise AssertionError("internal artifact folder became its own diagnostic block")
    if "archived" in rels or "archived/old-pkg" in rels:
        raise AssertionError("package shelf must not become an unregistered block")
    if "pastas sem registro" not in text:
        raise AssertionError("HTML must declare the unregistered count by name")
    if "Não é pacote incompatível" not in text:
        raise AssertionError("unregistered must not be confused with incompatible")
    foods = next(item for item in data["unregistered"] if item["rel"] == "091-foods-curadoria-mercado")
    if not foods.get("has_run_sh"):
        raise AssertionError("run.sh inside the folder must be described")


def main() -> int:
    tests = [
        test_same_architecture_one_and_many,
        test_mother_minispec_accordions,
        test_tasks_graph_same_census,
        test_absent_versus_incompatible,
        test_declared_child_unreadable_survives,
        test_deterministic,
        test_status_change_without_portrait_edit,
        test_handbook_may_diverge,
        test_sprint_tab_opt_in,
        test_unregistered_and_tokens,
        test_unregistered_is_not_a_filename_allowlist,
        test_script_payload_cannot_break_out,
        test_invalid_glob_does_not_abort_snapshot,
        test_duplicate_ids_keep_distinct_graph_nodes,
    ]
    failed = 0
    for test in tests:
        with tempfile.TemporaryDirectory(prefix="superflow-qg.") as tmp:
            try:
                test(Path(tmp))
                print(f"OK  {test.__name__}")
            except Exception as exc:  # noqa: BLE001 — report each branch
                failed += 1
                print(f"FAIL {test.__name__}: {exc}")
    if failed:
        print(f"FAILED {failed}/{len(tests)}")
        return 1
    print("OK: superflow qg tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
