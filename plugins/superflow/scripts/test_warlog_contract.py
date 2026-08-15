#!/usr/bin/env python3
"""Structural tests for Superflow WARLOG campaign board."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATE = SCRIPT_DIR / "validate_superflow.py"
WARLOG_SCRIPT = SCRIPT_DIR / "superflow_warlog.py"
PLUGIN_ROOT = SCRIPT_DIR.parent
FIXTURE = PLUGIN_ROOT / "assets" / "fixtures" / "warlog" / "campaign"


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

    contract = (PLUGIN_ROOT / "assets" / "references" / "warlog-contract.md").read_text(
        encoding="utf-8"
    )
    for marker in (
        "campaign board",
        "Budget",
        "Green contract",
        "Mermaid only",
        "mergeable",
    ):
        if marker not in contract:
            raise AssertionError(f"warlog-contract missing {marker}")

    skill = (PLUGIN_ROOT / "skills" / "warlog" / "SKILL.md").read_text(encoding="utf-8")
    if "Sprint cards" not in skill or "validate_superflow.py" not in skill:
        raise AssertionError("warlog skill must require sprint cards and package validator")

    campaign = run_validate(FIXTURE)
    if campaign.returncode != 0:
        raise AssertionError(f"campaign fixture must PASS:\n{campaign.stdout}")

    with tempfile.TemporaryDirectory(prefix="superflow-warlog.") as tmp:
        root = Path(tmp)

        # diary-only WARLOG must fail
        bad = root / "diary"
        shutil.copytree(FIXTURE, bad)
        (bad / "WARLOG.md").write_text(
            "# WARLOG: diary\n\n## Event Log\n\n- today | x | y\n",
            encoding="utf-8",
        )
        diary = run_validate(bad)
        if diary.returncode == 0:
            raise AssertionError("diary-only WARLOG must FAIL")
        if "Mission" not in diary.stdout and "sprint" not in diary.stdout.lower():
            raise AssertionError(f"unexpected diary fail message:\n{diary.stdout}")

        # PlantUML fence must fail
        puml = root / "puml"
        shutil.copytree(FIXTURE, puml)
        text = (puml / "WARLOG.md").read_text(encoding="utf-8")
        text = text.replace(
            "```mermaid\nflowchart TD",
            "```plantuml\n@startuml\nstart\nstop\n@enduml\n```\n\n```mermaid\nflowchart TD",
        )
        (puml / "WARLOG.md").write_text(text, encoding="utf-8")
        puml_run = run_validate(puml)
        if puml_run.returncode == 0:
            raise AssertionError("PlantUML in WARLOG must FAIL")

        # generator creates valid shell from status
        gen = root / "gen"
        shutil.copytree(FIXTURE, gen)
        (gen / "WARLOG.md").unlink()
        gen_run = subprocess.run(
            [sys.executable, str(WARLOG_SCRIPT), str(gen), "--event", "shell test"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if gen_run.returncode != 0:
            raise AssertionError(f"superflow_warlog.py failed:\n{gen_run.stdout}")
        gen_val = run_validate(gen)
        if gen_val.returncode != 0:
            raise AssertionError(f"generated WARLOG shell must validate:\n{gen_val.stdout}")
        body = (gen / "WARLOG.md").read_text(encoding="utf-8")
        if "### S1 —" not in body or "Budget:" not in body:
            raise AssertionError("generated shell missing sprint card")

    print("OK: superflow warlog contract tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
