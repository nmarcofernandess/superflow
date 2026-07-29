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
    "assets/references/tdd-contract.md",
    "assets/references/feature-mindset-contract.md",
    "assets/references/reuse-guard-protocol.md",
    "assets/references/mermaid-contract.md",
    "assets/references/warlog-contract.md",
    "assets/references/status-schema.md",
    "assets/fixtures/mindset/coverage.json",
    "assets/templates/PRD.md",
    "assets/templates/ISSUE_PRD.md",
    "assets/templates/analysis.md",
    "assets/templates/progress.md",
    "assets/templates/implementation_plan.json",
    "assets/templates/implementation_plan.md",
    "assets/templates/implementation_log.json",
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

PLAN_TDD_MARKERS = [
    "tdd-contract.md",
    "tdd.red",
    "tdd.green",
    "expected_failure",
    "Ready Gate",
]

EXECUTE_TDD_MARKERS = [
    "tdd-contract.md",
    "Iron law",
    "RED",
    "GREEN",
    "implementation_log.json",
]

QA_TDD_MARKERS = [
    "tdd-contract.md",
    "acceptance matrix",
    "red+green",
    "Ready Gate",
]

TDD_CONTRACT_MARKERS = [
    "I1",
    "I2",
    "I3",
    "Iron law",
    "expected_failure",
    "implementation_log.json",
]

DOCS_WORKFLOW_TYPES = {"docs", "docs_only"}
PLACEHOLDER_VERIFICATION = (
    "write tests later",
    "add unit tests",
    "add tests later",
    "tbd",
    "todo",
    "test later",
)

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
    "feature-mindset-contract.md",
    "reuse-guard-protocol.md",
    "code-recon-protocol.md",
    "technical-blueprint-protocol.md",
    "Phase 0 grill",
    "Evidence Matrix",
    "Implementation Map",
    "Blueprint Handoff",
    "Ready Gate",
    "path:line",
    "Síntese",
    "Recode Log",
    "strings-safadas",
    "Reuse Guard",
    "reuse",
]

BUILD_REQUIRED_MARKERS = [
    "build-protocol.md",
    "feature-mindset-contract.md",
    "reuse-guard-protocol.md",
    "code-recon-protocol.md",
    "technical-blueprint-protocol.md",
    "Ready Gate",
    "Synthesis",
    "facetas",
    "Copy",
    "Cross-facet",
    "tdd-contract.md",
    "Reuse Guard",
]

ANALYSIS_TEMPLATE_HEADINGS = [
    "## State",
    "## TL;DR",
    "## Síntese",
    "## Phase 0 Grill",
    "## Source And Scope",
    "## Faceta — Produto",
    "## Faceta — Backend",
    "## Faceta — Frontend",
    "## Faceta — Copy",
    "## Recode Log",
    "## Product Promise",
    "## Story de Usuario",
    "## Story Tecnica",
    "## Current Terrain",
    "## Evidence Matrix",
    "## Implementation Map",
    "## Entities And State",
    "## Runtime / Data Flow",
    "## Rules And Invariants",
    "## Blueprint Handoff",
    "## Grill Verdict",
    "## Open Questions",
    "## Recommended Next Phase",
]

MINDSET_CONTRACT_MARKERS = [
    "Fatality",
    "facetas",
    "waterfall",
    "Recode",
    "Síntese",
    "strings-safadas",
    "cartesiano",
    "path:line",
    "UNPROVEN",
    "Ready gates",
    "Proporcionalidade",
    "reuse-guard-protocol.md",
    "crystallize-guard",
]

REUSE_GUARD_MARKERS = [
    "Anti-fork",
    "Tier-2",
    "Reuse, don't fork",
    "stale",
    "grep",
    "new",
]

SPEC_TEMPLATE_MARKERS = [
    "## Synthesis",
    "### Product",
    "### Backend",
    "### Frontend",
    "### Copy",
    "Cross-facet",
    "Recode Log",
    "Testable behaviors",
    "Coherence check",
]

COVERAGE_REQUIRED_IDS = [
    "F1", "F2", "F3", "F4", "F5", "F6", "F7",
    "T1", "T2", "T3", "T4", "T5", "T6", "T7",
    "S1", "S2", "S3", "S4", "S5", "S6",
    "B1", "B2", "B3", "B4", "B5", "B6",
    "H1", "H2", "H3", "H4",
    "D1", "D2",
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
    for marker in [
        "schema_version",
        "superflow.plan.v1",
        "subtasks",
        "verification",
        "status",
        "tdd",
        "expected_failure",
        "behavior",
        "tdd_contract",
    ]:
        if marker not in plan_template:
            fail(f"assets/templates/implementation_plan.json missing marker: {marker}")

    log_template = read(root / "assets" / "templates" / "implementation_log.json")
    for marker in ["superflow.log.v1", "red", "green", "excerpt", "command"]:
        if marker not in log_template:
            fail(f"assets/templates/implementation_log.json missing marker: {marker}")

    tdd_contract = read(root / "assets" / "references" / "tdd-contract.md")
    for marker in TDD_CONTRACT_MARKERS:
        if marker not in tdd_contract:
            fail(f"assets/references/tdd-contract.md missing marker: {marker}")

    plan_skill = read(root / "skills" / "plan" / "SKILL.md")
    for marker in PLAN_TDD_MARKERS:
        if marker not in plan_skill:
            fail(f"skills/plan/SKILL.md missing TDD marker: {marker}")

    execute_skill = read(root / "skills" / "execute" / "SKILL.md")
    for marker in EXECUTE_TDD_MARKERS:
        if marker not in execute_skill:
            fail(f"skills/execute/SKILL.md missing TDD marker: {marker}")

    qa_skill = read(root / "skills" / "qa" / "SKILL.md")
    for marker in QA_TDD_MARKERS:
        if marker not in qa_skill:
            fail(f"skills/qa/SKILL.md missing TDD marker: {marker}")

    execution_contract = read(root / "assets" / "references" / "execution-contract.md")
    for marker in ["tdd-contract.md", "I1", "I2", "I3", "red+green"]:
        if marker not in execution_contract:
            fail(f"assets/references/execution-contract.md missing TDD marker: {marker}")

    mindset = read(root / "assets" / "references" / "feature-mindset-contract.md")
    for marker in MINDSET_CONTRACT_MARKERS:
        if marker not in mindset:
            fail(f"assets/references/feature-mindset-contract.md missing marker: {marker}")

    reuse_guard = read(root / "assets" / "references" / "reuse-guard-protocol.md")
    for marker in REUSE_GUARD_MARKERS:
        if marker not in reuse_guard:
            fail(f"assets/references/reuse-guard-protocol.md missing marker: {marker}")

    spec_template = read(root / "assets" / "templates" / "SPEC.md")
    for marker in SPEC_TEMPLATE_MARKERS:
        if marker not in spec_template:
            fail(f"assets/templates/SPEC.md missing mindset marker: {marker}")

    coverage_path = root / "assets" / "fixtures" / "mindset" / "coverage.json"
    coverage = json.loads(read(coverage_path))
    units = coverage.get("units")
    if not isinstance(units, list):
        fail("coverage.json units must be a list")
    by_id = {u.get("id"): u for u in units if isinstance(u, dict)}
    for uid in COVERAGE_REQUIRED_IDS:
        if uid not in by_id:
            fail(f"coverage.json missing unit id {uid}")
        if by_id[uid].get("estado_atual") != "present":
            fail(f"coverage.json unit {uid} must be present (got {by_id[uid].get('estado_atual')})")
        if not by_id[uid].get("gate_type"):
            fail(f"coverage.json unit {uid} missing gate_type")


def _section_body(text: str, heading: str) -> str:
    """Return body after a markdown heading until the next same-or-higher heading.

    Heading may be a prefix (e.g. ``## Faceta — Backend`` matches
    ``## Faceta — Backend (dados reais)``).
    """
    # Exact line or prefix before optional trailing title detail
    pattern = re.compile(
        rf"^{re.escape(heading)}(?:\s|$|[—(])",
        re.M,
    )
    m = pattern.search(text)
    if not m:
        # fallback: line that starts with heading
        pattern2 = re.compile(rf"^{re.escape(heading)}.*$", re.M)
        m = pattern2.search(text)
    if not m:
        return ""
    rest = text[m.end() :]
    next_h = re.search(r"^#{1,3}\s+\S", rest, re.M)
    body = rest[: next_h.start()] if next_h else rest
    return body.strip()


def _is_placeholder_body(body: str) -> bool:
    if not body or len(body) < 24:
        return True
    low = body.lower().strip()
    # Whole-body placeholders only (avoid matching "substituir a frase" in real prose)
    if low in {"tbd", "todo", "pending", "n/a", "unproven", "-", "—", "...", "…"}:
        return True
    if low.startswith("tbd") and len(low) < 40:
        return True
    if low.startswith("replace with") or low.startswith("substituir por"):
        return True
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    # Only a markdown table with empty/placeholder cells
    if len(lines) <= 3 and all(
        ln.startswith("|") or set(ln) <= {"|", "-", ":", " "} for ln in lines
    ):
        cell_text = " ".join(lines).lower()
        if "unproven" in cell_text or cell_text.count("|") > 4 and len(cell_text) < 120:
            # header-only or stub table
            if "high" not in cell_text and "path" in cell_text and "88" not in cell_text:
                return True
    return False


# path:line evidence — backticks alone do NOT count (Claude exploit A)
PATH_LINE_RE = re.compile(r"\b[\w./-]+\.\w{1,10}:\d+\b")

# Form-based strings-safadas (not fixture literals)
_SAFADA_CURRENCY_RE = re.compile(r"r\$\s*[\d.,]+|\b\d{1,3}(?:[.,]\d{3})*[.,]\d{2}\b", re.I)
_SAFADA_COUNT_RE = re.compile(
    r"\b\d+\s*(?:consultas?|pacientes?|itens?|restantes?|dias?|meses?|planos?|registros?)\b",
    re.I,
)
_SAFADA_DATE_RE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")
_SAFADA_GEOMETRY_RE = re.compile(
    r"\b("
    r"acima|abaixo|embaixo|em\s+baixo|"
    r"à\s+direita|a\s+direita|à\s+esquerda|a\s+esquerda|"
    r"no\s+bloco\s+(?:anterior|acima|abaixo|seguinte)|"
    r"olhe\s+no|veja\s+(?:acima|abaixo|embaixo)|"
    r"ao\s+lado|no\s+canto"
    r")\b",
    re.I,
)
_SAFADA_SECOND_PERSON_RE = re.compile(
    r"\b(voc[eê]|voce|vc)\b.{0,40}\b("
    r"tem|ainda|j[aá]|aproveite|sugerimos|restantes|pode|deve"
    r")\b|"
    r"\b(aproveite|sugerimos|conforme\s+acertamos|como\s+foi\s+combinado|"
    r"como\s+combinado|ainda\s+tem)\b",
    re.I,
)
_DEST_OK_RE = re.compile(r"\b(invariante|estrutura|morte)\b", re.I)
_DEST_APPROVE_RE = re.compile(
    r"\b(aprovad\w*|manter|nenhum|copy\s+de\s+sistema|usar\s+como\s+copy|ui\s+copy)\b",
    re.I,
)


def _text_looks_safada_instance(text: str) -> bool:
    """Detect instance prose by form: currency, counts, dates, geometry, 2nd-person promise."""
    if _SAFADA_CURRENCY_RE.search(text):
        return True
    if _SAFADA_COUNT_RE.search(text):
        return True
    if _SAFADA_DATE_RE.search(text):
        return True
    if _SAFADA_GEOMETRY_RE.search(text):
        return True
    if _SAFADA_SECOND_PERSON_RE.search(text):
        return True
    return False


def _reject_strings_safadas_approved(text: str, *, label: str) -> None:
    """Always-on: instance prose must not be approved as system UI copy.

    Form-based (not fixture-literal): currency/count/date/geometry/2nd-person
    in a table row whose destination is not invariante|estrutura|morte → fail.
    """
    low = text.lower()
    # Free-prose approval phrases still catch obvious traps
    if "ui copy aprovada" in low or "copy aprovada" in low:
        if _text_looks_safada_instance(text) or "prosa-inst" in low or "como foi combinado" in low:
            fail(f"{label}: strings-safadas — instance prose marked as approved UI copy")
        if "aprovada" in low and _SAFADA_CURRENCY_RE.search(low):
            fail(f"{label}: strings-safadas — currency instance prose approved as UI copy")

    for ln in text.splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if "---" in s:
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        joined = " ".join(cells)
        joined_low = joined.lower()
        # Skip header rows
        if any(
            h in joined_low
            for h in (
                "superfície",
                "superficie",
                "pecado",
                "destino",
                "string / key",
                "invariant prose",
                "forbidden",
                "texto candidato",
            )
        ):
            continue

        dest = cells[-1]
        body = " ".join(cells[1:-1]) if len(cells) > 2 else cells[0]
        # Honest kill/structure/invariant destination is OK even with instance sample
        if _DEST_OK_RE.search(dest):
            continue
        # Form looks like instance prose and is not routed to morte/estrutura/invariante
        if _text_looks_safada_instance(body) or _text_looks_safada_instance(joined):
            if _DEST_APPROVE_RE.search(dest) or _DEST_APPROVE_RE.search(joined) or not _DEST_OK_RE.search(joined):
                fail(
                    f"{label}: strings-safadas — instance-form prose in table row "
                    "without invariante|estrutura|morte destination "
                    f"(row: {s[:120]})"
                )


def _recode_rows_real(recode: str) -> list[str]:
    """Return non-header Recode Log table rows that are not fake N/A stubs."""
    fake_tokens = {
        "n/a",
        "n.a.",
        "nenhuma recode",
        "nenhum recode",
        "none",
        "no recode",
        "—",
        "-",
        "tbd",
        "todo",
        "placeholder",
        "",
    }
    rows: list[str] = []
    for ln in recode.splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if "---" in s:
            continue
        if re.search(r"\|\s*when\s*\|", s, re.I) or re.search(r"\|\s*trigger\s*\|", s, re.I):
            continue
        low = s.lower()
        if re.search(r"\|\s*t\d+\s*\|\s*n/a\s*\|\s*n/a\s*\|", low):
            continue
        if "nenhuma recode" in low and "n/a" in low:
            continue
        if re.search(r"n/a.*n/a.*nenhuma", low):
            continue
        # Fake invent trigger without substance
        if re.search(r"mudei de ideia|achei que sim", low) and len(low) < 80:
            continue
        cells = [c.strip().lower() for c in s.strip("|").split("|")]
        meaningful = [
            c
            for c in cells
            if c
            and c not in fake_tokens
            and c
            not in {
                "when",
                "trigger",
                "facet",
                "recode",
                "facet that broke",
                "what was recoded",
            }
        ]
        # Require a real trigger-like cell (not only ids like t1)
        non_id = [c for c in meaningful if not re.fullmatch(r"t\d+", c)]
        if len(non_id) < 2:
            continue
        rows.append(s)
    return rows


def _has_coherence_proof(recode: str) -> bool:
    """Honest alternative to ≥1 recode: synthesis already matched terrain."""
    return bool(re.search(r"coherence_proof\s*:", recode, re.I))


def _has_reuse_guard_table(frontend: str) -> bool:
    """True if Frontend section has Need|Source|Decision|path-style guard table."""
    if "|" not in frontend:
        return False
    low = frontend.lower()
    header_ok = False
    decision_row = False
    for ln in frontend.splitlines():
        s = ln.strip().lower()
        if not s.startswith("|"):
            continue
        if "---" in s:
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 3:
            continue
        # Header: need + (source|guard) + decision + (path|evidence)
        if "need" in s and ("source" in s or "guard" in s or "grep" in s or "graph" in s):
            if "decision" in s or re.search(r"reuse|mode|new", s):
                if "path" in s or "evidence" in s or "canônic" in s or "canonic" in s:
                    header_ok = True
        # Data row with decision reuse|mode|new
        if re.search(r"\|\s*(reuse|mode|new)\s*\|", s) and len(cells) >= 4:
            decision_row = True
    if header_ok and decision_row:
        return True
    # Fallback: section documents all four columns + a decision cell
    if (
        re.search(r"\bneed\b", low)
        and re.search(r"\b(source|guard source|grep|graph)\b", low)
        and re.search(r"\bdecision\b", low)
        and re.search(r"\b(path|evidence|canônic|canonic)\b", low)
        and re.search(r"\|\s*(reuse|mode|new)\s*\|", low)
    ):
        return True
    return False


def _require_backend_evidence(backend: str, *, label: str, depth: str) -> None:
    if depth == "docs" and "skip_reason" in backend.lower():
        return
    if PATH_LINE_RE.search(backend) or re.search(r"\bUNPROVEN\b", backend):
        return
    fail(
        f"{label}: Backend facet needs path:line (e.g. file.ts:12) or UNPROVEN — "
        "backticks alone do not count"
    )


def _require_frontend_decision(frontend: str, *, label: str, depth: str) -> None:
    if depth == "docs" and "skip_reason" in frontend.lower():
        return
    low = frontend.lower()
    has_reuse = bool(re.search(r"\breuse\b", low))
    has_mode = bool(re.search(r"\bmode\b", low))
    has_new = bool(re.search(r"\bnew\b", low))
    if not (has_reuse or has_mode or has_new):
        fail(f"{label}: Frontend facet needs reuse|mode|new decision")
    # Decision 'new' (word present without reuse/mode primary, or pure new) requires guard table
    if has_new and not (has_reuse or has_mode):
        if not _has_reuse_guard_table(frontend):
            fail(
                f"{label}: Frontend decision 'new' requires Reuse Guard table "
                "(Need|Source|Decision|path) in the same section"
            )
    elif has_new and re.search(r"\|\s*new\s*\|", low):
        if not _has_reuse_guard_table(frontend):
            fail(
                f"{label}: Frontend decision 'new' requires Reuse Guard table "
                "(Need|Source|Decision|path) in the same section"
            )


def _require_recode_honest(recode: str, *, label: str, depth: str) -> None:
    """≥1 real recode row, or skip_reason (docs), or coherence_proof (deep allowed)."""
    if depth == "docs":
        if "skip_reason" in recode.lower() or "skip" in recode.lower() or "docs" in recode.lower():
            return
        if _recode_rows_real(recode):
            return
        if _has_coherence_proof(recode):
            return
        fail(f"{label}: docs-only Recode Log needs skip_reason or honest skip")
        return

    # deep / trap
    if _recode_rows_real(recode):
        return
    if _has_coherence_proof(recode):
        # Must have non-empty proof text after the marker
        m = re.search(r"coherence_proof\s*:\s*(\S.+)", recode, re.I)
        if m and len(m.group(1).strip()) >= 12:
            return
        fail(f"{label}: coherence_proof present but empty/too short")
    # skip_reason alone does NOT waive deep recode (closes hatch D)
    fail(
        f"{label}: deep Recode Log needs ≥1 real entry "
        "or coherence_proof: <why initial synthesis already matched terrain> "
        "(fake N/A / empty section / skip_reason-only do not count)"
    )


def derive_mindset_depth(status: dict) -> str:
    """Depth from status.json — never from agent-written mindset-depth.txt hatch.

    docs  ← phase_budget docs/docs_only OR workflow_type docs* OR
            (lean|capture) with non-build routes (prd_execute, inbox, local_prd)
    deep  ← everything else (standard/deep/forensic, build_* routes)
    trap  ← phase_budget trap (adversarial fixture alias of deep gates)
    """
    budget = str(status.get("phase_budget") or "").lower().strip()
    route = str(status.get("route") or "").lower().strip()
    workflow = str(status.get("workflow_type") or "").lower().strip()

    if budget == "skip" or workflow == "skip":
        fail("status.json: phase_budget/workflow_type 'skip' is forbidden (no mindset escape hatch)")

    if budget == "trap":
        return "trap"

    if budget in {"docs", "docs_only"} or workflow in DOCS_WORKFLOW_TYPES:
        return "docs"

    docs_routes = {
        "prd_execute",
        "inbox_prd",
        "local_prd",
        "capture",
    }
    if budget in {"lean", "capture"} and route in docs_routes:
        return "docs"

    if budget in {"lean", "capture"} and "build" not in route and route not in {
        "build_plan_execute",
        "analyst_prd",
        "prd_plan_execute",
        "investigate_first",
    }:
        return "docs"

    return "deep"


def validate_analysis_mindset(text: str, *, label: str, depth: str = "deep") -> None:
    """depth: deep | docs | trap — structural gates for analysis.md."""
    if depth == "skip":
        fail(f"{label}: mindset-depth 'skip' is not allowed (escape hatch removed)")

    required = [
        "## TL;DR",
        "## Síntese",
        "## Faceta — Produto",
        "## Faceta — Backend",
        "## Faceta — Frontend",
        "## Faceta — Copy",
        "## Recode Log",
    ]
    for h in required:
        if h not in text:
            fail(f"{label}: missing required mindset heading {h}")

    synthesis = _section_body(text, "## Síntese")
    if _is_placeholder_body(synthesis):
        fail(f"{label}: Síntese empty or placeholder (ready ≠ filled headings)")

    # Always-on strings-safadas (every depth)
    _reject_strings_safadas_approved(text, label=label)

    if depth == "docs":
        recode = _section_body(text, "## Recode Log")
        _require_recode_honest(recode, label=label, depth=depth)
        return

    if depth in {"deep", "trap"}:
        for h in (
            "## Faceta — Produto",
            "## Faceta — Backend",
            "## Faceta — Frontend",
            "## Faceta — Copy",
        ):
            body = _section_body(text, h)
            if _is_placeholder_body(body):
                fail(f"{label}: {h} empty/placeholder (typographic completeness is not ready)")
        backend = _section_body(text, "## Faceta — Backend")
        _require_backend_evidence(backend, label=label, depth=depth)
        frontend = _section_body(text, "## Faceta — Frontend")
        _require_frontend_decision(frontend, label=label, depth=depth)
        copy = _section_body(text, "## Faceta — Copy")
        if "morte" not in copy.lower() and "estrutura" not in copy.lower() and "invariante" not in copy.lower():
            fail(f"{label}: Copy facet needs invariante|estrutura|morte")
        recode = _section_body(text, "## Recode Log")
        if _is_placeholder_body(recode) and not _has_coherence_proof(recode):
            fail(f"{label}: deep package needs Recode Log with real content or coherence_proof")
        _require_recode_honest(recode, label=label, depth=depth)


def validate_spec_mindset(text: str, *, label: str, depth: str = "deep") -> None:
    if depth == "skip":
        fail(f"{label}: mindset-depth 'skip' is not allowed (escape hatch removed)")

    for h in ("## Synthesis", "### Product", "### Backend", "### Frontend", "### Copy"):
        if h not in text:
            fail(f"{label}: missing SPEC mindset heading {h}")
    synthesis = _section_body(text, "## Synthesis")
    if _is_placeholder_body(synthesis):
        fail(f"{label}: SPEC Synthesis empty/placeholder")

    _reject_strings_safadas_approved(text, label=label)

    if depth == "docs":
        recode = _section_body(text, "## Recode Log") if "## Recode Log" in text else ""
        if recode:
            _require_recode_honest(recode, label=label, depth=depth)
        return

    if depth in {"deep", "trap"}:
        for h in ("### Product", "### Backend", "### Frontend", "### Copy"):
            body = _section_body(text, h)
            if _is_placeholder_body(body):
                fail(f"{label}: {h} empty/placeholder (SPEC/Analyst parity)")
        backend = _section_body(text, "### Backend")
        _require_backend_evidence(backend, label=label, depth=depth)
        frontend = _section_body(text, "### Frontend")
        _require_frontend_decision(frontend, label=label, depth=depth)
        if "## Cross-facet dependencies" not in text and "Cross-facet" not in text:
            fail(f"{label}: deep SPEC needs Cross-facet dependencies")
        if "## Recode Log" not in text:
            fail(f"{label}: deep SPEC needs Recode Log")
        recode = _section_body(text, "## Recode Log")
        _require_recode_honest(recode, label=label, depth=depth)
        if "Testable behaviors" not in text:
            fail(f"{label}: SPEC needs Testable behaviors handoff (no fake commands required)")


def iter_plan_subtasks(plan: dict) -> list[dict]:
    out: list[dict] = []
    plan_body = plan.get("plan") if isinstance(plan.get("plan"), dict) else plan
    phases = plan_body.get("phases") if isinstance(plan_body, dict) else None
    if not isinstance(phases, list):
        return out
    for phase in phases:
        if not isinstance(phase, dict):
            continue
        subtasks = phase.get("subtasks")
        if not isinstance(subtasks, list):
            continue
        for sub in subtasks:
            if isinstance(sub, dict):
                out.append(sub)
    return out


def tdd_required_for_subtask(subtask: dict, workflow_type: str) -> bool:
    tdd = subtask.get("tdd")
    if isinstance(tdd, dict) and "required" in tdd:
        return bool(tdd.get("required"))
    if workflow_type in DOCS_WORKFLOW_TYPES:
        return False
    verification = subtask.get("verification") if isinstance(subtask.get("verification"), dict) else {}
    vtype = str(verification.get("type") or "").lower()
    if vtype == "manual" and not subtask.get("files_to_modify") and not subtask.get("files_to_create"):
        return False
    return True


def validate_plan_tdd(plan: dict, *, label: str) -> None:
    if plan.get("schema_version") != "superflow.plan.v1":
        fail(f"{label}: unexpected schema_version (expected superflow.plan.v1)")
    plan_body = plan.get("plan")
    if not isinstance(plan_body, dict):
        fail(f"{label}: missing plan object")
    workflow_type = str(plan_body.get("workflow_type") or "feature").split("|")[0].strip()
    subtasks = iter_plan_subtasks(plan)
    if not subtasks:
        fail(f"{label}: plan has no subtasks")
    for sub in subtasks:
        sid = sub.get("id") or "<missing-id>"
        tdd = sub.get("tdd") if isinstance(sub.get("tdd"), dict) else {}
        required = tdd_required_for_subtask(sub, workflow_type)
        if not required:
            skip_reason = tdd.get("skip_reason")
            if tdd.get("required") is False and not skip_reason:
                fail(f"{label}: subtask {sid} has tdd.required=false without skip_reason")
            continue
        behavior = (sub.get("behavior") or "").strip()
        if not behavior or behavior.startswith("One-sentence") or behavior.startswith("Replace with"):
            # Template placeholders are only allowed in the plugin template file itself.
            if "assets/templates" not in label:
                fail(f"{label}: subtask {sid} missing concrete behavior for TDD")
        red = tdd.get("red") if isinstance(tdd.get("red"), dict) else {}
        green = tdd.get("green") if isinstance(tdd.get("green"), dict) else {}
        red_cmd = str(red.get("command") or "").strip()
        red_fail = str(red.get("expected_failure") or "").strip()
        green_cmd = str(green.get("command") or "").strip()
        if not red_cmd or red_cmd.startswith("repo-native"):
            if "assets/templates" not in label:
                fail(f"{label}: subtask {sid} missing tdd.red.command")
        if not red_fail or red_fail.startswith("feature missing"):
            if "assets/templates" not in label and red_fail == "":
                fail(f"{label}: subtask {sid} missing tdd.red.expected_failure")
            if "assets/templates" not in label and red_fail.startswith("feature missing or assertion"):
                # Template default phrase alone is not a concrete plan.
                if red_fail == "feature missing or assertion that proves the gap":
                    fail(f"{label}: subtask {sid} has placeholder tdd.red.expected_failure")
        if not green_cmd or green_cmd.startswith("same as") or green_cmd.startswith("same targeted"):
            if "assets/templates" not in label:
                fail(f"{label}: subtask {sid} missing tdd.green.command")
        verification = sub.get("verification") if isinstance(sub.get("verification"), dict) else {}
        vcmd = str(verification.get("command") or "").strip().lower()
        for bad in PLACEHOLDER_VERIFICATION:
            if bad in vcmd or bad in red_cmd.lower():
                fail(f"{label}: subtask {sid} has forbidden verification placeholder {bad!r}")


def validate_log_tdd(log: dict, plan: dict | None, *, label: str) -> None:
    if log.get("schema_version") != "superflow.log.v1":
        fail(f"{label}: unexpected schema_version (expected superflow.log.v1)")
    tasks = log.get("tasks")
    if not isinstance(tasks, list):
        fail(f"{label}: tasks must be a list")
    required_ids: set[str] = set()
    if plan is not None:
        plan_body = plan.get("plan") if isinstance(plan.get("plan"), dict) else {}
        workflow_type = str(plan_body.get("workflow_type") or "feature").split("|")[0].strip()
        for sub in iter_plan_subtasks(plan):
            if tdd_required_for_subtask(sub, workflow_type):
                sid = sub.get("id")
                if sid:
                    required_ids.add(str(sid))
    by_id = {}
    for entry in tasks:
        if not isinstance(entry, dict):
            continue
        tid = str(entry.get("id") or "")
        if tid:
            by_id[tid] = entry
        status = str(entry.get("status") or "").upper()
        if status not in {"DONE", "DONE_WITH_CONCERNS"}:
            continue
        tdd_needed = tid in required_ids if required_ids else True
        # Direct execution entries (direct-*) always need evidence when done as code.
        if tid.startswith("direct-"):
            tdd_needed = True
        if not tdd_needed:
            continue
        for gate in ("red", "green"):
            block = entry.get(gate)
            if not isinstance(block, dict):
                fail(f"{label}: task {tid} DONE without {gate} evidence object")
            cmd = str(block.get("command") or "").strip()
            excerpt = str(block.get("excerpt") or "").strip()
            if not cmd or not excerpt:
                fail(f"{label}: task {tid} DONE without {gate}.command and {gate}.excerpt")
            if block.get("ok") is not True:
                fail(f"{label}: task {tid} DONE but {gate}.ok is not true")
    if plan is not None:
        for sid in required_ids:
            entry = by_id.get(sid)
            if entry is None:
                continue
            status = str(entry.get("status") or "").upper()
            if status in {"DONE", "DONE_WITH_CONCERNS"}:
                # already validated above
                pass


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
                out = result.stdout or ""
                # Local machines without puppeteer chrome cannot render; do not
                # treat that as a Superflow contract failure unless forced.
                if (
                    "chrome-headless-shell" in out
                    or "Could not find chrome" in out
                    or "Browser was not found" in out
                ):
                    print(
                        f"WARN: Mermaid render skipped (browser missing) in {source} block {idx}",
                        file=sys.stderr,
                    )
                    continue
                fail(f"Mermaid failed in {source} block {idx}:\n{out}")


def validate_package(path: Path) -> None:
    required = ["PRD.md", "status.json", "progress.md"]
    missing = [rel for rel in required if not (path / rel).exists()]
    analysis_path = path / "analysis.md"
    spec_path = path / "SPEC.md"
    has_mindset = analysis_path.exists() or spec_path.exists()

    # Patch 1: never silent-OK when analysis/SPEC exist without the core trio
    if missing:
        if has_mindset:
            fail(
                f"{path}: partial package — analysis/SPEC present but missing "
                f"{', '.join(missing)} (never silent OK)"
            )
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

    plan_data: dict | None = None
    plan_path = path / "implementation_plan.json"
    if plan_path.exists():
        plan_data = json.loads(read(plan_path))
        validate_plan_tdd(plan_data, label=str(plan_path))
        # Prefer plan workflow_type when present for depth derivation
        plan_body = plan_data.get("plan") if isinstance(plan_data.get("plan"), dict) else {}
        if isinstance(plan_body, dict) and plan_body.get("workflow_type") and not status.get("workflow_type"):
            status = {**status, "workflow_type": plan_body.get("workflow_type")}

    log_path = path / "implementation_log.json"
    if log_path.exists():
        log_data = json.loads(read(log_path))
        validate_log_tdd(log_data, plan_data, label=str(log_path))
        log_artifact = status["artifacts"].get("implementation_log")
        if log_artifact and log_artifact != "implementation_log.json":
            fail(f"{path}/status.json artifacts.implementation_log must be implementation_log.json")

    # Patch 2: depth from status.json — mindset-depth.txt is NOT authority
    depth = derive_mindset_depth(status)
    marker = path / "mindset-depth.txt"
    if marker.exists():
        raw = read(marker).strip().lower()
        if raw == "skip":
            fail(f"{path}/mindset-depth.txt: 'skip' is forbidden (no mindset escape hatch)")
        # Legacy fixture alias: trap marker only allowed when status already deep
        if raw == "trap" and depth == "deep":
            depth = "trap"
        # Any other marker content is ignored (cannot downgrade deep → docs)

    if analysis_path.exists():
        validate_analysis_mindset(read(analysis_path), label=str(analysis_path), depth=depth)

    if spec_path.exists():
        validate_spec_mindset(read(spec_path), label=str(spec_path), depth=depth)


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
