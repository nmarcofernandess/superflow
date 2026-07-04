#!/usr/bin/env python3
"""Audit a Superflow idea/PRD/issue without writing workflow artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from superflow_taskgen import classify, extract_markdown_title, titleize


CHECKS = [
    {
        "id": "problem",
        "label": "Problem is explicit",
        "patterns": [r"##\s+Problem", r"problema", r"dor", r"falha"],
        "gap": "State the concrete problem or pain.",
    },
    {
        "id": "goal",
        "label": "Goal is explicit",
        "patterns": [r"##\s+Goal", r"objetivo", r"goal", r"quer(o|emos)", r"deve"],
        "gap": "State the desired outcome.",
    },
    {
        "id": "actor",
        "label": "Actor/user is named",
        "patterns": [r"usuario", r"usuário", r"user", r"admin", r"cliente", r"operador", r"nutri"],
        "gap": "Name who benefits or operates the workflow.",
    },
    {
        "id": "scope",
        "label": "Scope boundary exists",
        "patterns": [r"##\s+Scope", r"fora de escopo", r"out of scope", r"sem alterar", r"nao deve", r"não deve"],
        "gap": "Define in-scope and out-of-scope boundaries.",
    },
    {
        "id": "acceptance",
        "label": "Acceptance criteria are testable",
        "patterns": [r"##\s+Acceptance Criteria", r"- \[ \]", r"criterio", r"critério", r"teste", r"validavel", r"validável"],
        "gap": "Add observable acceptance criteria.",
    },
    {
        "id": "technical_context",
        "label": "Technical context is named",
        "patterns": [r"##\s+Technical Context", r"src/", r"app/", r"api", r"schema", r"banco", r"database", r"arquivo"],
        "gap": "Name known files, systems, APIs, or data contracts.",
    },
    {
        "id": "risk",
        "label": "Risks are acknowledged",
        "patterns": [r"##\s+Risks", r"risco", r"risk", r"migracao", r"migração", r"auth", r"cache", r"security"],
        "gap": "List risks or state why risk is low.",
    },
]


def read_input(args: argparse.Namespace) -> tuple[str, str]:
    if args.from_file == "-":
        return sys.stdin.read(), "stdin"
    if args.from_file:
        path = Path(args.from_file).expanduser()
        return path.read_text(encoding="utf-8"), str(path)
    if args.text:
        return args.text, "inline"
    raise SystemExit("text is required unless --from-file is used")


def has_pattern(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.MULTILINE) for pattern in patterns)


def audit(text: str, source: str, mode: str) -> dict:
    classification = classify(text, mode, None)
    title = extract_markdown_title(text) or titleize(text)
    checks = []
    gaps = []
    for check in CHECKS:
        passed = has_pattern(text, check["patterns"])
        checks.append({
            "id": check["id"],
            "label": check["label"],
            "status": "pass" if passed else "gap",
        })
        if not passed:
            gaps.append(check["gap"])

    confidence = classification["confidence"]
    route = classification["route"]
    next_actions: list[str] = []
    if gaps:
        next_actions.append("Improve PRD gaps before execution.")
    if confidence == "low":
        next_actions.append("Keep as inbox or run analyst/discovery.")
    if route == "prd_execute" and not gaps:
        next_actions.append("Execute directly with QA.")
    elif route == "prd_execute":
        next_actions.append("Lean route is possible after closing gaps.")
    elif route == "prd_plan_execute":
        next_actions.append("Write implementation plan before execution.")
    elif route == "build_plan_execute":
        next_actions.append("Write technical blueprint before plan/execution.")
    elif route == "investigate_first":
        next_actions.append("Run discovery before defining fix.")
    elif route in {"inbox_only", "inbox_prd"}:
        next_actions.append("Store as GitHub issue; promote when mature.")

    return {
        "schema_version": "superflow.audit.v1",
        "title": title,
        "source": source,
        "classification": classification,
        "checks": checks,
        "gaps": gaps,
        "next_actions": next_actions,
    }


def render_markdown(payload: dict) -> str:
    classification = payload["classification"]
    lines = [
        f"# Superflow Audit: {payload['title']}",
        "",
        "## Route",
        "",
        f"- Route: `{classification['route']}`",
        f"- Phase budget: `{classification['phase_budget']}`",
        f"- Confidence: `{classification['confidence']}`",
        f"- Maturity score: `{classification['maturity_score']}`",
        f"- Risk score: `{classification['risk_score']}`",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        marker = "x" if check["status"] == "pass" else " "
        lines.append(f"- [{marker}] {check['label']}")
    lines.extend(["", "## Gaps", ""])
    if payload["gaps"]:
        lines.extend(f"- {gap}" for gap in payload["gaps"])
    else:
        lines.append("- none")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in payload["next_actions"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?")
    parser.add_argument("--from-file")
    parser.add_argument("--mode", choices=["auto", "local", "issue"], default="auto")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--output")
    args = parser.parse_args()

    text, source = read_input(args)
    payload = audit(text, source, args.mode)
    output = json.dumps(payload, indent=2) + "\n" if args.format == "json" else render_markdown(payload)
    if args.output:
        Path(args.output).expanduser().write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
