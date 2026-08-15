#!/usr/bin/env python3
"""Behavioral tests for the Superflow review phase (R1–R4).

Review is the phase that was missing: the plan could name a `reviewer` owner
and the status could carry a `critic` slot, but nothing produced findings,
nothing forced a verdict on them, and QA closed regardless.
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
PLUGIN_ROOT = SCRIPT_DIR.parent
FIXTURE = PLUGIN_ROOT / "assets" / "fixtures" / "review" / "reviewed"


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


def mutate(pkg: Path, fn) -> Path:
    """Apply fn to the review log of a fresh copy of the fixture."""
    data = json.loads((pkg / "review_log.json").read_text(encoding="utf-8"))
    fn(data)
    (pkg / "review_log.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return pkg


def assert_contract_documented() -> None:
    contract = (PLUGIN_ROOT / "assets" / "references" / "review-contract.md").read_text(
        encoding="utf-8"
    )
    for marker in ("R1", "R2", "R3", "R4", "review_log.json", "verdict"):
        if marker not in contract:
            raise AssertionError(f"review-contract missing {marker}")

    skill = (PLUGIN_ROOT / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    for marker in ("review-contract.md", "review_log.json", "## Ready Gate"):
        if marker not in skill:
            raise AssertionError(f"review skill missing {marker}")

    qa = (PLUGIN_ROOT / "skills" / "qa" / "SKILL.md").read_text(encoding="utf-8")
    if "review_log.json" not in qa:
        raise AssertionError("qa skill must read review_log.json before closing")

    router = (PLUGIN_ROOT / "skills" / "superflow" / "SKILL.md").read_text(encoding="utf-8")
    if "review" not in router.lower():
        raise AssertionError("router must expose the review phase")


def main() -> int:
    plugin = run_validate(PLUGIN_ROOT)
    if plugin.returncode != 0:
        raise AssertionError(f"plugin root must validate:\n{plugin.stdout}")

    assert_contract_documented()

    golden = run_validate(FIXTURE)
    if golden.returncode != 0:
        raise AssertionError(f"review fixture must PASS:\n{golden.stdout}")

    with tempfile.TemporaryDirectory(prefix="superflow-review.") as tmp:
        root = Path(tmp)

        def fresh(name: str) -> Path:
            pkg = root / name
            shutil.copytree(FIXTURE, pkg)
            return pkg

        # R3.1 — a finding with no verdict blocks closure
        pending = mutate(
            fresh("pending-finding"),
            lambda d: d["rounds"][0]["findings"][0].update({"verdict": "pending"}),
        )
        assert_fail(
            run_validate(pending),
            why="finding left pending while QA is complete",
            needles=["pending", "verdict"],
        )

        # R3.2 — rejecting a finding requires a technical reason
        def _reject_empty(d):
            f = d["rounds"][0]["findings"][0]
            f.update({"verdict": "rejected", "reason": "", "task_id": None, "proof": None})

        no_reason = mutate(fresh("reject-no-reason"), _reject_empty)
        assert_fail(
            run_validate(no_reason),
            why="rejected finding without reason",
            needles=["reason", "rejected"],
        )

        # R3.3 — performative agreement is not a verdict
        def _performative(d):
            f = d["rounds"][0]["findings"][0]
            f.update(
                {
                    "verdict": "rejected",
                    "reason": "Boa observação, você tem razão!",
                    "task_id": None,
                    "proof": None,
                }
            )

        flattery = mutate(fresh("performative"), _performative)
        assert_fail(
            run_validate(flattery),
            why="performative agreement as a verdict reason",
            needles=["performative", "reason"],
        )

        # R4 — an accepted blocker needs proof that the fix holds
        def _accepted_no_proof(d):
            f = d["rounds"][0]["findings"][0]
            f.update({"verdict": "accepted", "severity": "blocker", "proof": None})

        unproven = mutate(fresh("accepted-no-proof"), _accepted_no_proof)
        assert_fail(
            run_validate(unproven),
            why="accepted blocker without re-verification proof",
            needles=["proof", "blocker"],
        )

        # R4.2 — a boolean is not proof
        def _boolean_proof(d):
            f = d["rounds"][0]["findings"][0]
            f.update({"verdict": "accepted", "proof": {"ok": True}})

        boolean = mutate(fresh("boolean-proof"), _boolean_proof)
        assert_fail(
            run_validate(boolean),
            why="proof without command and excerpt",
            needles=["proof", "command", "excerpt"],
        )

        # R2 — an empty review round must say why nothing was found
        def _silent_round(d):
            d["rounds"][0]["findings"] = []
            d["rounds"][0].pop("no_findings_reason", None)

        silent = mutate(fresh("silent-round"), _silent_round)
        assert_fail(
            run_validate(silent),
            why="review round with no findings and no reason",
            needles=["no_findings_reason", "findings"],
        )

        # R2.2 — declaring an honest empty round is allowed
        def _honest_empty(d):
            d["rounds"][0]["findings"] = []
            d["rounds"][0]["no_findings_reason"] = (
                "Diff limitado a strings de copy ja cobertas pelo gate de safada; "
                "nenhum caminho de execucao mudou."
            )

        honest = mutate(fresh("honest-empty"), _honest_empty)
        honest_run = run_validate(honest)
        if honest_run.returncode != 0:
            raise AssertionError(f"honest empty round must PASS:\n{honest_run.stdout}")

        # R1 — code shipped and QA closed without any code review at all
        no_review = fresh("no-review")
        (no_review / "review_log.json").unlink()
        status = json.loads((no_review / "status.json").read_text(encoding="utf-8"))
        status["artifacts"]["review"] = None
        status["phases"]["review"] = "pending"
        (no_review / "status.json").write_text(
            json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        assert_fail(
            run_validate(no_review),
            why="QA complete over finished code with no review round",
            needles=["review", "code"],
        )

    print("OK: superflow review contract tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
