#!/usr/bin/env python3
"""Validate a Superflow skill folder or generated package."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


REQUIRED_SKILL_FILES = [
    "SKILL.md",
    "references/routing-protocol.md",
    "references/prd-contract.md",
    "references/github-issue-contract.md",
    "references/execution-contract.md",
    "references/mermaid-contract.md",
    "references/status-schema.md",
    "assets/templates/PRD.md",
    "assets/templates/ISSUE_PRD.md",
    "assets/templates/progress.md",
    "scripts/superflow_taskgen.py",
    "scripts/superflow_github.py",
    "scripts/superflow_audit.py",
]

REQUIRED_PLUGIN_FILES = [
    ".codex-plugin/plugin.json",
    "skills/superflow/SKILL.md",
    "skills/capture/SKILL.md",
    "skills/taskgen/SKILL.md",
    "skills/analyst/SKILL.md",
    "skills/build/SKILL.md",
    "skills/plan/SKILL.md",
    "skills/warlog/SKILL.md",
    "skills/execute/SKILL.md",
    "skills/qa/SKILL.md",
    "skills/audit/SKILL.md",
    "assets/references/analyst-protocol.md",
    "assets/references/code-recon-protocol.md",
    "assets/references/technical-blueprint-protocol.md",
    "assets/references/build-protocol.md",
    "assets/references/routing-protocol.md",
    "assets/references/prd-contract.md",
    "assets/references/github-issue-contract.md",
    "assets/references/execution-contract.md",
    "assets/references/mermaid-contract.md",
    "assets/references/warlog-contract.md",
    "assets/references/status-schema.md",
    "assets/templates/PRD.md",
    "assets/templates/ISSUE_PRD.md",
    "assets/templates/analysis.md",
    "assets/templates/progress.md",
    "assets/templates/implementation_plan.json",
    "assets/templates/implementation_plan.md",
    "assets/templates/SPEC.md",
    "assets/templates/WARLOG.md",
    "assets/templates/qa_report.md",
    "assets/task-board/board.html",
    "assets/task-board/board-data.example.js",
    "scripts/superflow_taskgen.py",
    "scripts/superflow_github.py",
    "scripts/superflow_audit.py",
    "scripts/superflow_warlog.py",
]

EXPECTED_PLUGIN_SKILLS = [
    "superflow",
    "capture",
    "taskgen",
    "analyst",
    "build",
    "plan",
    "warlog",
    "execute",
    "qa",
    "audit",
]

FORBIDDEN_DIAGRAM_TOKENS = [
    "```" + "plan" + "tuml",
    "@start" + "uml",
    "@start" + "mindmap",
    "@start" + "wbs",
]

ANALYST_REQUIRED_MARKERS = [
    "analyst-protocol.md",
    "code-recon-protocol.md",
    "technical-blueprint-protocol.md",
    "Phase 0 grill",
    "Evidence Matrix",
    "Implementation Map",
    "Entities And State",
    "Blueprint Handoff",
    "Ready Gate",
    "path:line",
]

BUILD_REQUIRED_MARKERS = [
    "build-protocol.md",
    "code-recon-protocol.md",
    "technical-blueprint-protocol.md",
    "Product -> Backend -> Frontend",
    "Ready Gate",
]

ANALYSIS_TEMPLATE_HEADINGS = [
    "## State",
    "## TL;DR",
    "## Phase 0 Grill",
    "## Source And Scope",
    "## Product Promise",
    "## Story de Usuario",
    "## Story Tecnica",
    "## Current Terrain",
    "## Evidence Matrix",
    "## Implementation Map",
    "## Entities And State",
    "## Runtime / Data Flow",
    "## Rules And Invariants",
    "## Architecture Risks",
    "## Blueprint Handoff",
    "## Acceptance Criteria",
    "## Open Questions",
    "## Grill Verdict",
    "## Recommended Next Phase",
]

PRD_REQUIRED_HEADINGS = [
    "## State",
    "## Problem",
    "## Goal",
    "## Users / Actors",
    "## Story de Usuario",
    "## Story Tecnica",
    "## Scope",
    "## Expected Behavior",
    "## Current Behavior / Bug",
    "## Desired Behavior",
    "## System Pattern / Contract",
    "## Acceptance Criteria",
    "## Definition of Complete",
    "## Technical Context",
    "## Data / Contracts",
    "## UX / States",
    "## Risks",
    "## Open Questions",
    "## Next Phase",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_skill_root(root: Path) -> None:
    for rel in REQUIRED_SKILL_FILES:
        if not (root / rel).exists():
            fail(f"missing required file: {rel}")

    skill = read(root / "SKILL.md")
    if not skill.startswith("---\n"):
        fail("SKILL.md missing YAML frontmatter")
    if "name: superflow" not in skill:
        fail("SKILL.md frontmatter must include name: superflow")
    if "description:" not in skill:
        fail("SKILL.md frontmatter missing description")


def validate_plugin_root(root: Path) -> None:
    for rel in REQUIRED_PLUGIN_FILES:
        if not (root / rel).exists():
            fail(f"missing required plugin file: {rel}")
    manifest = json.loads(read(root / ".codex-plugin" / "plugin.json"))
    if manifest.get("name") != "superflow":
        fail("plugin manifest name must be superflow")
    if manifest.get("skills") != "./skills/":
        fail("plugin manifest must expose ./skills/")
    skill = read(root / "skills" / "superflow" / "SKILL.md")
    if not skill.startswith("---\n"):
        fail("skills/superflow/SKILL.md missing YAML frontmatter")
    if "name: superflow" not in skill:
        fail("skills/superflow/SKILL.md frontmatter must include name: superflow")
    for skill_name in EXPECTED_PLUGIN_SKILLS:
        skill_path = root / "skills" / skill_name / "SKILL.md"
        skill_text = read(skill_path)
        if not skill_text.startswith("---\n"):
            fail(f"skills/{skill_name}/SKILL.md missing YAML frontmatter")
        if f"name: {skill_name}" not in skill_text:
            fail(f"skills/{skill_name}/SKILL.md frontmatter must include name: {skill_name}")
        if skill_name != "audit" and "mermaid" not in skill_text.lower():
            fail(f"skills/{skill_name}/SKILL.md must mention Mermaid contract")

    analyst_text = read(root / "skills" / "analyst" / "SKILL.md")
    if len(analyst_text.splitlines()) < 80:
        fail("skills/analyst/SKILL.md is too thin for the Superflow analyst contract")
    for marker in ANALYST_REQUIRED_MARKERS:
        if marker not in analyst_text:
            fail(f"skills/analyst/SKILL.md missing analyst marker: {marker}")

    build_text = read(root / "skills" / "build" / "SKILL.md")
    for marker in BUILD_REQUIRED_MARKERS:
        if marker not in build_text:
            fail(f"skills/build/SKILL.md missing build marker: {marker}")

    analysis_template = read(root / "assets" / "templates" / "analysis.md")
    for heading in ANALYSIS_TEMPLATE_HEADINGS:
        if heading not in analysis_template:
            fail(f"assets/templates/analysis.md missing heading: {heading}")

    prd_template = read(root / "assets" / "templates" / "PRD.md")
    issue_template = read(root / "assets" / "templates" / "ISSUE_PRD.md")
    for heading in PRD_REQUIRED_HEADINGS:
        if heading not in prd_template:
            fail(f"assets/templates/PRD.md missing heading: {heading}")
        if heading not in issue_template:
            fail(f"assets/templates/ISSUE_PRD.md missing heading: {heading}")

    plan_template = read(root / "assets" / "templates" / "implementation_plan.json")
    for marker in ["schema_version", "superflow.plan.v1", "subtasks", "verification", "status"]:
        if marker not in plan_template:
            fail(f"assets/templates/implementation_plan.json missing marker: {marker}")


def scan_forbidden_diagrams(root: Path) -> None:
    for file in root.rglob("*.md"):
        text = read(file)
        for token in FORBIDDEN_DIAGRAM_TOKENS:
            if token.lower() in text.lower():
                fail(f"forbidden diagram token {token!r} in {file}")


def extract_mermaid(root: Path) -> list[tuple[Path, str]]:
    blocks: list[tuple[Path, str]] = []
    pattern = re.compile(r"```mermaid\n([\s\S]*?)```", re.MULTILINE)
    for file in root.rglob("*.md"):
        text = read(file)
        for match in pattern.finditer(text):
            blocks.append((file, match.group(1)))
    return blocks


def validate_mermaid(root: Path) -> None:
    blocks = extract_mermaid(root)
    if not blocks:
        return
    with tempfile.TemporaryDirectory(prefix="superflow-mermaid.") as tmp:
        tmpdir = Path(tmp)
        for idx, (source, body) in enumerate(blocks, start=1):
            mmd = tmpdir / f"{idx:03d}.mmd"
            svg = tmpdir / f"{idx:03d}.svg"
            mmd.write_text(body, encoding="utf-8")
            result = subprocess.run(
                ["npx", "-y", "@mermaid-js/mermaid-cli", "-i", str(mmd), "-o", str(svg)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if result.returncode != 0:
                fail(f"Mermaid failed in {source} block {idx}:\n{result.stdout}")


def validate_package(path: Path) -> None:
    required = ["PRD.md", "status.json", "progress.md"]
    if not all((path / rel).exists() for rel in required):
        return
    status = json.loads(read(path / "status.json"))
    if status.get("schema_version") != "superflow.status.v1":
        fail(f"{path}/status.json has unexpected schema_version")
    for key in ["id", "route", "phase_budget", "confidence", "current_phase", "decision", "phases", "artifacts", "task_source"]:
        if key not in status:
            fail(f"{path}/status.json missing {key}")
    if status["artifacts"].get("prd") and not (path / status["artifacts"]["prd"]).exists():
        fail(f"{path}/status.json points to missing PRD artifact")
    decision = status.get("decision")
    if not isinstance(decision, dict):
        fail(f"{path}/status.json decision must be an object")
    for key in ["verdict", "prd_status", "reason", "prd_path", "discard_path"]:
        if key not in decision:
            fail(f"{path}/status.json decision missing {key}")
    plan_artifact = status["artifacts"].get("plan")
    task_source = status.get("task_source") or {}
    if plan_artifact:
        if plan_artifact != "implementation_plan.json":
            fail(f"{path}/status.json artifacts.plan must point to implementation_plan.json")
        if task_source.get("path") != plan_artifact:
            fail(f"{path}/status.json task_source.path must match artifacts.plan")
    prd_text = read(path / "PRD.md")
    for heading in PRD_REQUIRED_HEADINGS:
        if heading not in prd_text:
            fail(f"{path}/PRD.md missing heading: {heading}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Superflow skill root or generated specs/NNN folder.")
    parser.add_argument("--mermaid", action="store_true", help="Render Mermaid blocks with mmdc.")
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        fail(f"path does not exist: {root}")

    if (root / ".codex-plugin" / "plugin.json").exists():
        validate_plugin_root(root)
        scan_forbidden_diagrams(root)
        if args.mermaid:
            validate_mermaid(root)
    elif (root / "SKILL.md").exists():
        validate_skill_root(root)
        scan_forbidden_diagrams(root)
        if args.mermaid:
            validate_mermaid(root)
    else:
        validate_package(root)
        scan_forbidden_diagrams(root)
        if args.mermaid:
            validate_mermaid(root)

    print(f"OK: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
