#!/usr/bin/env python3
"""Behavioral tests for the Superflow campaign motor (C1–C4).

The WARLOG is the human board of a campaign. It has sprint cards, dependencies
and a next action — and no motor: nothing reads the real packages and answers
"what is actually next, and is this campaign actually finished?".

The motor derives that from the packages themselves. It never declares done
while a package is open.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CAMPAIGN = SCRIPT_DIR / "superflow_campaign.py"
VALIDATE = SCRIPT_DIR / "validate_superflow.py"
PLUGIN_ROOT = SCRIPT_DIR.parent
FIXTURE = PLUGIN_ROOT / "assets" / "fixtures" / "campaign"

EXIT_DONE = 0
EXIT_NEXT = 10
EXIT_BLOCKED = 20
EXIT_CONTRACT = 1


def run_campaign(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CAMPAIGN), str(root), "--json", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def payload(result: subprocess.CompletedProcess) -> dict:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic path
        raise AssertionError(f"campaign motor must emit JSON:\n{result.stdout}") from exc


def set_status(pkg: Path, **fields) -> None:
    path = pkg / "status.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, value in fields.items():
        if key == "phases":
            data["phases"].update(value)
        else:
            data[key] = value
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def assert_contract_documented() -> None:
    contract = (PLUGIN_ROOT / "assets" / "references" / "campaign-contract.md").read_text(
        encoding="utf-8"
    )
    for marker in ("C1", "C2", "C3", "C4", "depends_on", "WARLOG"):
        if marker not in contract:
            raise AssertionError(f"campaign-contract missing {marker}")

    skill = (PLUGIN_ROOT / "skills" / "campaign" / "SKILL.md").read_text(encoding="utf-8")
    for marker in ("campaign-contract.md", "superflow_campaign.py", "## Ready Gate"):
        if marker not in skill:
            raise AssertionError(f"campaign skill missing {marker}")

    warlog = (PLUGIN_ROOT / "assets" / "references" / "warlog-contract.md").read_text(
        encoding="utf-8"
    )
    if "campaign-contract.md" not in warlog:
        raise AssertionError("warlog-contract must point at the motor, not fork it")


def main() -> int:
    assert_contract_documented()

    # C1/C2 — the fixture campaign: 001 closed, 002 actionable, 003 waiting on 002
    golden = run_campaign(FIXTURE)
    if golden.returncode != EXIT_NEXT:
        raise AssertionError(
            f"fixture campaign must report next (exit {EXIT_NEXT}), got {golden.returncode}:\n{golden.stdout}"
        )
    data = payload(golden)
    if data.get("verdict") != "next":
        raise AssertionError(f"expected verdict next:\n{golden.stdout}")
    if data.get("next", {}).get("id") != "002-consumer":
        raise AssertionError(f"expected 002-consumer as next actionable:\n{golden.stdout}")
    waiting = {p["id"]: p for p in data["packages"]}
    if waiting["003-polish"]["state"] != "waiting":
        raise AssertionError(f"003 must wait on its dependency:\n{golden.stdout}")
    if waiting["001-foundation"]["state"] != "closed":
        raise AssertionError(f"001 must be closed:\n{golden.stdout}")

    with tempfile.TemporaryDirectory(prefix="superflow-campaign.") as tmp:
        root = Path(tmp)

        def fresh(name: str) -> Path:
            pkg = root / name
            shutil.copytree(FIXTURE, pkg)
            return pkg

        # C4 — a campaign is done only when every package is closed
        done = fresh("all-closed")
        for pkg in ("002-consumer", "003-polish"):
            set_status(done / pkg, phases={"qa": "complete"}, current_phase="qa")
        done_run = run_campaign(done)
        if done_run.returncode != EXIT_DONE:
            raise AssertionError(f"all packages closed must be done:\n{done_run.stdout}")
        if payload(done_run).get("verdict") != "done":
            raise AssertionError(f"expected verdict done:\n{done_run.stdout}")

        # C4 — one open package is enough to keep the campaign open
        almost = fresh("almost-done")
        set_status(almost / "002-consumer", phases={"qa": "complete"}, current_phase="qa")
        almost_run = run_campaign(almost)
        if almost_run.returncode == EXIT_DONE:
            raise AssertionError(
                f"campaign with an open package must not report done:\n{almost_run.stdout}"
            )

        # C2 — a dependency cycle is a contract error, not a stack overflow
        cyclic = fresh("cyclic")
        set_status(cyclic / "002-consumer", depends_on=["003-polish"])
        cyclic_run = run_campaign(cyclic)
        if cyclic_run.returncode != EXIT_CONTRACT:
            raise AssertionError(f"dependency cycle must fail:\n{cyclic_run.stdout}")
        if "cycle" not in cyclic_run.stdout.lower():
            raise AssertionError(f"cycle error must name the cycle:\n{cyclic_run.stdout}")

        # C2 — depending on a package that does not exist is a contract error
        ghost = fresh("ghost-dep")
        set_status(ghost / "002-consumer", depends_on=["009-does-not-exist"])
        ghost_run = run_campaign(ghost)
        if ghost_run.returncode != EXIT_CONTRACT:
            raise AssertionError(f"unknown dependency must fail:\n{ghost_run.stdout}")

        # C3 — closed by decree is not closed: the validator decides
        liar = fresh("liar")
        set_status(liar / "002-consumer", phases={"qa": "complete"}, current_phase="qa")
        (liar / "002-consumer" / "progress.md").unlink()
        liar_run = run_campaign(liar)
        if liar_run.returncode != EXIT_CONTRACT:
            raise AssertionError(
                f"package claiming qa complete while invalid must fail:\n{liar_run.stdout}"
            )
        if "validator" not in liar_run.stdout.lower():
            raise AssertionError(f"error must name the validator:\n{liar_run.stdout}")

        # C4 — everything open and blocked by a blocked dependency reports blocked
        blocked = fresh("blocked")
        set_status(blocked / "002-consumer", phases={"execute": "blocked"}, blocked_reason="")
        blocked_run = run_campaign(blocked)
        if blocked_run.returncode != EXIT_CONTRACT:
            raise AssertionError(
                f"blocked package without a reason must fail:\n{blocked_run.stdout}"
            )

        blocked_ok = fresh("blocked-with-reason")
        set_status(
            blocked_ok / "002-consumer",
            phases={"execute": "blocked"},
            blocked_reason="Aguardando decisao do humano sobre o formato do payload exportado",
        )
        blocked_ok_run = run_campaign(blocked_ok)
        if blocked_ok_run.returncode != EXIT_BLOCKED:
            raise AssertionError(
                f"blocked package with a reason must report blocked:\n{blocked_ok_run.stdout}"
            )
        blocked_payload = payload(blocked_ok_run)
        if blocked_payload.get("verdict") != "blocked":
            raise AssertionError(f"expected verdict blocked:\n{blocked_ok_run.stdout}")
        if not blocked_payload.get("blocked"):
            raise AssertionError(f"blocked verdict must list the blockers:\n{blocked_ok_run.stdout}")

        # C1 — campaign scope filters by name when packages carry one
        scoped = fresh("scoped")
        set_status(scoped / "003-polish", campaign="outra-campanha")
        scoped_run = run_campaign(scoped, "--campaign", "fixture-campaign")
        scoped_ids = {p["id"] for p in payload(scoped_run)["packages"]}
        if "003-polish" in scoped_ids:
            raise AssertionError(f"--campaign must filter foreign packages:\n{scoped_run.stdout}")

    print("OK: superflow campaign contract tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
