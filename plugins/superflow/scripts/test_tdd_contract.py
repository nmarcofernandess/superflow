#!/usr/bin/env python3
"""Unit tests for Superflow TDD plan/log validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATE = SCRIPT_DIR / "validate_superflow.py"
PLUGIN_ROOT = SCRIPT_DIR.parent


def run_validate(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATE), str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def write_min_package(root: Path) -> Path:
    spec = root / "specs" / "001-tdd"
    spec.mkdir(parents=True)
    (spec / "PRD.md").write_text(
        "\n".join(
            [
                "# PRD",
                "## State",
                "gathering",
                "## Problem",
                "x",
                "## Goal",
                "x",
                "## Users / Actors",
                "x",
                "## Story de Usuario",
                "x",
                "## Story Tecnica",
                "x",
                "## Scope",
                "x",
                "## Expected Behavior",
                "x",
                "## Current Behavior / Bug",
                "x",
                "## Desired Behavior",
                "x",
                "## System Pattern / Contract",
                "x",
                "## Acceptance Criteria",
                "- rejects empty email",
                "## Definition of Complete",
                "x",
                "## Technical Context",
                "x",
                "## Data / Contracts",
                "x",
                "## UX / States",
                "x",
                "## Risks",
                "x",
                "## Open Questions",
                "x",
                "## Next Phase",
                "plan",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (spec / "progress.md").write_text("# Progress\n", encoding="utf-8")
    (spec / "status.json").write_text(
        json.dumps(
            {
                "schema_version": "superflow.status.v1",
                "id": "001-tdd",
                "title": "TDD fixture",
                "route": "prd_plan_execute",
                "phase_budget": "standard",
                "execution_strategy": "single",
                "source": {"type": "inline", "github_issue": None, "file": None},
                "confidence": "high",
                "current_phase": "plan",
                "decision": {
                    "verdict": "prd_ready",
                    "prd_status": "ready",
                    "reason": "fixture",
                    "prd_path": "PRD.md",
                    "discard_path": None,
                },
                "phases": {
                    "inbox": "skipped",
                    "analyst": "skipped",
                    "taskgen": "complete",
                    "build": "skipped",
                    "critic": "skipped",
                    "plan": "complete",
                    "execute": "pending",
                    "qa": "pending",
                },
                "artifacts": {
                    "prd": "PRD.md",
                    "analysis": None,
                    "blueprint": None,
                    "progress": "progress.md",
                    "warlog": None,
                    "plan": "implementation_plan.json",
                    "implementation_log": None,
                    "qa": None,
                },
                "task_source": {
                    "type": "plan",
                    "path": "implementation_plan.json",
                    "progress": None,
                },
                "updated_at": "2026-07-28T00:00:00Z",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return spec


def good_plan() -> dict:
    return {
        "schema_version": "superflow.plan.v1",
        "status": "complete",
        "source": {"prd": "PRD.md", "blueprint": None, "spec": None},
        "plan": {
            "feature": "email validation",
            "workflow_type": "feature",
            "strategy": "single",
            "tdd_contract": "assets/references/tdd-contract.md",
            "preconditions": ["PRD reviewed"],
            "phases": [
                {
                    "id": "phase-1",
                    "name": "Implementation",
                    "description": "Validate email",
                    "depends_on": [],
                    "subtasks": [
                        {
                            "id": "subtask-1-1",
                            "description": "Reject empty email",
                            "behavior": "Empty email is rejected with Email required",
                            "files_to_modify": ["src/form.ts"],
                            "files_to_create": ["src/form.test.ts"],
                            "patterns_from": [],
                            "tdd": {
                                "required": True,
                                "skip_reason": None,
                                "red": {
                                    "test_file": "src/form.test.ts",
                                    "test_name": "rejects empty email",
                                    "command": "npm test -- form.test.ts -t 'rejects empty email'",
                                    "expected_failure": "expected 'Email required', got undefined",
                                },
                                "green": {
                                    "command": "npm test -- form.test.ts -t 'rejects empty email'",
                                    "expected": "PASS",
                                },
                                "negatives": ["empty string"],
                            },
                            "verification": {
                                "type": "test",
                                "command": "npm test -- form.test.ts -t 'rejects empty email'",
                                "expected": "PASS",
                            },
                            "acceptance_criteria": ["rejects empty email"],
                            "owner": "main_agent",
                            "status": "pending",
                        }
                    ],
                }
            ],
            "summary": {
                "total_phases": 1,
                "total_subtasks": 1,
                "estimated_complexity": "standard",
            },
        },
        "done_criteria": ["AC evidenced"],
    }


def bad_plan_missing_red() -> dict:
    plan = good_plan()
    plan["plan"]["phases"][0]["subtasks"][0]["tdd"]["red"]["command"] = ""
    plan["plan"]["phases"][0]["subtasks"][0]["tdd"]["red"]["expected_failure"] = ""
    return plan


def good_log() -> dict:
    return {
        "schema_version": "superflow.log.v1",
        "source_plan": "implementation_plan.json",
        "updated_at": "2026-07-28T00:00:00Z",
        "tasks": [
            {
                "id": "subtask-1-1",
                "status": "DONE",
                "files_touched": ["src/form.ts", "src/form.test.ts"],
                "red": {
                    "command": "npm test -- form.test.ts -t 'rejects empty email'",
                    "excerpt": "FAIL: expected 'Email required', got undefined",
                    "ok": True,
                },
                "green": {
                    "command": "npm test -- form.test.ts -t 'rejects empty email'",
                    "excerpt": "PASS",
                    "ok": True,
                },
                "notes": "",
                "self_critique": "",
            }
        ],
        "remaining": [],
    }


def bad_log_missing_red() -> dict:
    log = good_log()
    log["tasks"][0]["red"] = {"command": "", "excerpt": "", "ok": True}
    return log


def main() -> int:
    plugin = run_validate(PLUGIN_ROOT)
    if plugin.returncode != 0:
        raise AssertionError(f"plugin root must validate:\n{plugin.stdout}")

    with tempfile.TemporaryDirectory(prefix="superflow-tdd.") as tmp:
        root = Path(tmp)

        # Good plan package
        good = write_min_package(root / "good")
        (good / "implementation_plan.json").write_text(
            json.dumps(good_plan(), indent=2) + "\n", encoding="utf-8"
        )
        ok = run_validate(good)
        if ok.returncode != 0:
            raise AssertionError(f"good plan package should pass:\n{ok.stdout}")

        # Bad plan missing RED
        bad = write_min_package(root / "bad-plan")
        (bad / "implementation_plan.json").write_text(
            json.dumps(bad_plan_missing_red(), indent=2) + "\n", encoding="utf-8"
        )
        bad_run = run_validate(bad)
        if bad_run.returncode == 0:
            raise AssertionError("plan missing RED must fail validation")
        if "tdd.red" not in bad_run.stdout and "missing tdd.red" not in bad_run.stdout:
            raise AssertionError(f"expected RED error, got:\n{bad_run.stdout}")

        # Good plan + good log
        good_log_pkg = write_min_package(root / "good-log")
        (good_log_pkg / "implementation_plan.json").write_text(
            json.dumps(good_plan(), indent=2) + "\n", encoding="utf-8"
        )
        (good_log_pkg / "implementation_log.json").write_text(
            json.dumps(good_log(), indent=2) + "\n", encoding="utf-8"
        )
        status = json.loads((good_log_pkg / "status.json").read_text(encoding="utf-8"))
        status["artifacts"]["implementation_log"] = "implementation_log.json"
        (good_log_pkg / "status.json").write_text(
            json.dumps(status, indent=2) + "\n", encoding="utf-8"
        )
        ok_log = run_validate(good_log_pkg)
        if ok_log.returncode != 0:
            raise AssertionError(f"good plan+log should pass:\n{ok_log.stdout}")

        # DONE without RED evidence
        bad_log_pkg = write_min_package(root / "bad-log")
        (bad_log_pkg / "implementation_plan.json").write_text(
            json.dumps(good_plan(), indent=2) + "\n", encoding="utf-8"
        )
        (bad_log_pkg / "implementation_log.json").write_text(
            json.dumps(bad_log_missing_red(), indent=2) + "\n", encoding="utf-8"
        )
        status2 = json.loads((bad_log_pkg / "status.json").read_text(encoding="utf-8"))
        status2["artifacts"]["implementation_log"] = "implementation_log.json"
        (bad_log_pkg / "status.json").write_text(
            json.dumps(status2, indent=2) + "\n", encoding="utf-8"
        )
        bad_log_run = run_validate(bad_log_pkg)
        if bad_log_run.returncode == 0:
            raise AssertionError("DONE without RED evidence must fail")
        if "red" not in bad_log_run.stdout.lower():
            raise AssertionError(f"expected red evidence error, got:\n{bad_log_run.stdout}")

        # Docs skip is allowed with skip_reason
        docs = write_min_package(root / "docs")
        docs_plan = good_plan()
        docs_plan["plan"]["workflow_type"] = "docs"
        docs_plan["plan"]["phases"][0]["subtasks"][0] = {
            "id": "subtask-1-1",
            "description": "Update README",
            "behavior": "README documents export button",
            "files_to_modify": ["README.md"],
            "files_to_create": [],
            "patterns_from": [],
            "tdd": {
                "required": False,
                "skip_reason": "docs-only markdown change",
                "red": {"test_file": "", "test_name": "", "command": "", "expected_failure": ""},
                "green": {"command": "", "expected": ""},
                "negatives": [],
            },
            "verification": {
                "type": "manual",
                "command": "read README.md",
                "expected": "export documented",
            },
            "acceptance_criteria": ["docs mention export"],
            "owner": "main_agent",
            "status": "pending",
        }
        (docs / "implementation_plan.json").write_text(
            json.dumps(docs_plan, indent=2) + "\n", encoding="utf-8"
        )
        docs_run = run_validate(docs)
        if docs_run.returncode != 0:
            raise AssertionError(f"docs skip plan should pass:\n{docs_run.stdout}")

    print("OK: superflow tdd contract tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
