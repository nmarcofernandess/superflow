#!/usr/bin/env python3
"""Validate a Superflow skill folder or generated package."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
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
    "skills/review/SKILL.md",
    "skills/campaign/SKILL.md",
    "skills/qa/SKILL.md",
    "skills/audit/SKILL.md",
    "skills/explain-clearly/SKILL.md",
    "skills/writing-clearly-and-concisely/SKILL.md",
    "skills/writing-clearly-and-concisely/elements-of-style.md",
    "skills/grill-me/SKILL.md",
    "skills/grill-with-docs/SKILL.md",
    "skills/grill-with-docs/CONTEXT-FORMAT.md",
    "skills/grill-with-docs/ADR-FORMAT.md",
    "skills/gauntlet-loop/SKILL.md",
    "assets/references/analyst-protocol.md",
    "assets/references/code-recon-protocol.md",
    "assets/references/technical-blueprint-protocol.md",
    "assets/references/build-protocol.md",
    "assets/references/routing-protocol.md",
    "assets/references/prd-contract.md",
    "assets/references/github-issue-contract.md",
    "assets/references/execution-contract.md",
    "assets/references/tdd-contract.md",
    "assets/references/review-contract.md",
    "assets/references/campaign-contract.md",
    "assets/references/feature-mindset-contract.md",
    "assets/references/reuse-guard-protocol.md",
    "assets/references/mermaid-contract.md",
    "assets/references/warlog-contract.md",
    "assets/references/status-schema.md",
    "assets/references/lifecycle-contract.md",
    "assets/fixtures/mindset/coverage.json",
    "assets/templates/PRD.md",
    "assets/templates/ISSUE_PRD.md",
    "assets/templates/analysis.md",
    "assets/templates/progress.md",
    "assets/templates/implementation_plan.json",
    "assets/templates/implementation_plan.md",
    "assets/templates/implementation_log.json",
    "assets/templates/review_log.json",
    "assets/templates/SPEC.md",
    "assets/templates/WARLOG.md",
    "assets/templates/qa_report.md",
    "assets/task-board/board.html",
    "assets/task-board/board-data.example.js",
    "scripts/superflow_taskgen.py",
    "scripts/superflow_github.py",
    "scripts/superflow_audit.py",
    "scripts/superflow_warlog.py",
    "scripts/superflow_campaign.py",
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
    "review",
    "campaign",
    "qa",
    "audit",
    "writing-clearly-and-concisely",
]

# Callable with /name. Not Superflow phases. No Mermaid/status contract.
STANDALONE_PLUGIN_SKILLS = [
    "explain-clearly",
    "grill-me",
    "grill-with-docs",
    "gauntlet-loop",
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
    "validate_superflow.py",
    "path-to-package",
    "path:line",
    "Síntese",
    "Recode Log",
    "strings-safadas",
    "Reuse Guard",
    "reuse",
    "behavior names",
]

BUILD_REQUIRED_MARKERS = [
    "build-protocol.md",
    "feature-mindset-contract.md",
    "reuse-guard-protocol.md",
    "code-recon-protocol.md",
    "technical-blueprint-protocol.md",
    "Ready Gate",
    "validate_superflow.py",
    "path-to-package",
    "Synthesis",
    "facetas",
    "Copy",
    "Cross-facet",
    "tdd-contract.md",
    "Reuse Guard",
    "behavior names",
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
    "Critério de pronto",
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
    "validate_superflow.py",
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

WARLOG_CONTRACT_MARKERS = [
    "campaign board",
    "mergeable",
    "Budget",
    "direct",
    "plan",
    "spec",
    "Green contract",
    "Mermaid only",
    "PlantUML",
    "Sprints",
    "Next Action",
    "warlog-minimal",
]

WARLOG_SKILL_MARKERS = [
    "warlog-contract.md",
    "campaign board",
    "Sprint cards",
    "direct",
    "plan",
    "spec",
    "Green contract",
    "PlantUML",
    "Ready Gate",
    "validate_superflow.py",
]

WARLOG_TEMPLATE_MARKERS = [
    "## Mission",
    "## Scope",
    "## Campaign map",
    "## Sprints",
    "### S1 —",
    "Budget:",
    "Green contract:",
    "## Event Log",
    "## Next Action",
    "```mermaid",
]

WARLOG_PACKAGE_HEADINGS = [
    "## Mission",
    "## Sprints",
    "## Event Log",
    "## Next Action",
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
    "## TL;DR",
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

# --- Handbook: o retrato operável da spec ---------------------------------
# O HANDBOOK.md responde "o que esta spec é, do que ela depende e qual é o
# próximo trabalho útil" para quem chega sem contexto. A prosa mora no arquivo;
# o veredito (selo, arquivabilidade, ação de índice) mora em status.json#handbook,
# porque veredito raspado de prosa por regex já provou errar (agregador de 2026-09).
# Conventional template name only. Not an allowlist — artifacts.handbook is free.

# (canônico, aliases aceitos no heading). O canônico é o que a mensagem de erro
# cobra; os aliases existem só para grafia sem acento.
HANDBOOK_REQUIRED_HEADINGS = [
    ("Intenção", ["Intenção", "Intencao"]),
    ("Estado real", ["Estado real"]),
    ("Rastro", ["Rastro"]),
    ("Dificuldade e impacto", ["Dificuldade e impacto"]),
    ("Testes", ["Testes"]),
    ("O que a linha não comporta", ["O que a linha não comporta", "O que a linha nao comporta"]),
    ("Relatório de leitura", ["Relatório de leitura", "Relatorio de leitura"]),
]

# A seção que precisa provar leitura de código, e o piso de provas.
HANDBOOK_EVIDENCE_SECTION = "Estado real"
HANDBOOK_MIN_EVIDENCE_ANCHORS = 3

HANDBOOK_SELOS = [
    "closed",
    "merged_dev",
    "in_flight",
    "pending_work",
    "needs_marco",
    "stale_doc",
    "dormant",
    "superseded",
]
HANDBOOK_INDEX_ACTIONS = ["archive", "new_line", "confirm_pending", "backlog"]
HANDBOOK_ARCHIVABLE = ["no", "status_only", "yes"]
HANDBOOK_NEXT_KINDS = [
    "investigation",
    "preparation",
    "plan",
    "implementation",
    "human",
]

# Elegibilidade de execução é DERIVADA (kind != human && blocked_by == []) e
# nunca gravada: campo gravado envelhece calado e passa a mentir sobre o que
# está liberado. Estes nomes são recusados dentro de next_useful.
HANDBOOK_DERIVED_ONLY_KEYS = [
    "eligible",
    "elegivel",
    "elegível",
    "executable",
    "runnable",
    "ready",
    "actionable",
    "unblocked",
]

# Vocabulário fechado de phases.*. `superseded` entra como sétimo valor: cobre
# "outro pacote fez isso" — que `skipped` (decidiu-se não fazer) não descreve.
# Os três não colapsam. Ship não é oitavo valor.
PHASE_VOCABULARY = [
    "pending",
    "running",
    "complete",
    "skipped",
    "blocked",
    "failed",
    "superseded",
]

STATUS_SCHEMA_VERSION = "superflow.status.v1"
CONFIG_SCHEMA_VERSION = "superflow.config.v1"

CURRENT_PHASE_NAMES = [
    "inbox",
    "taskgen",
    "analyst",
    "build",
    "review",
    "plan",
    "execute",
    "qa",
]

GATHERING_PHASES = {"inbox", "taskgen", "analyst"}
POINTER_PHASE_STATES = {"pending", "running", "complete", "blocked", "failed"}
READY_PRD_STATUSES = {"ready", "complete"}
# G20 default. ready is a verdict about the PRD document, so the document
# must exist. Flip this to False if the owner answers G20 the other way.
# Phases (complete/skipped/superseded) never read this flag.
READY_REQUIRES_PRD_DOCUMENT = True
NESTED_CHILD_FOLDERS = {"minispecs", "subspecs", "units", "plans", "crystallize"}

PHASE_NAME_ALIASES = {
    "discovery": "analyst",
    "critic": "review",
    "code": "execute",
    "units": "execute",
}

# Grafias medidas (D4). Serve para derivar e para diagnosticar — não para
# aceitar no disco sem FLOOR do consumidor.
PHASE_STATE_ALIASES = {
    "pending": "pending",
    "running": "running",
    "complete": "complete",
    "skipped": "skipped",
    "blocked": "blocked",
    "failed": "failed",
    "superseded": "superseded",
    "in_progress": "running",
    "in-progress": "running",
    "done": "complete",
    "not_applicable": "skipped",
    "implemented": "complete",
    "cancelled": "skipped",
    "complete_via_spec_105": "superseded",
    "complete_via_105_05": "superseded",
    "approved": "complete",
    "absorbed": "superseded",
    "complete_baseline": "complete",
    "retry_pending": "pending",
    "skipped_prompt_provided_discovery": "skipped",
    "complete-with-codex-amendments": "complete",
    "partial": "running",
    "pending_migration_tests_review": "pending",
    "layout_approved_functional_pending": "pending",
    "artifacts_complete_external_review_pending": "pending",
    "parts_0_to_6_shipped": "complete",
    "dev_and_prod_schema_verified": "complete",
    "passed": "complete",
    "verification_delegated_to_attestation": "complete",
    "outlined": "pending",
    "passed-subagent-static-production-proof-and-chart-header-closeout": "complete",
    "durable-copy-under-specs": "complete",
    "dormant": "pending",
    "completed": "complete",
}

CURRENT_PHASE_READS_AS = {
    "inbox": "inbox",
    "taskgen": "taskgen",
    "analyst": "analyst",
    "build": "build",
    "review": "review",
    "plan": "plan",
    "execute": "execute",
    "qa": "qa",
    "discovery": "analyst",
    "critic": "review",
    "code": "execute",
    "units": "execute",
    "done": "qa",
    "closed": "qa",
    "qa_final": "qa",
    "build_final": "build",
    "followup_spec_pending": "qa",
    "prd": "taskgen",
    "coordinate": "execute",
    "delivery": "qa",
    "b11_f10_t1_t7_complete_ready_for_block_frontier": "qa",
    "FASE_2_FRONTEIRA": "qa",
    "cohort_sealed_gates_green_amendments_proposed": "qa",
    "ship_complete_backlog_D": "qa",
    "vibe": "qa",
    "delivery_merged_installed_cleaned": "qa",
    "qa_and_ship": "qa",
}

DEFAULT_CONFIG = {
    "schema_version": CONFIG_SCHEMA_VERSION,
    "specs": "specs",
    "destination": None,
    "floors": {"phase_vocabulary": "phase-vocabulary-floor.json"},
    "qg": "qg",
    "sprints": "sprints",
}


class SuperflowConfig:
    """Resolved `.superflow/` for this run. Empty floors when none found."""

    def __init__(self) -> None:
        self.superflow_dir: Path | None = None
        self.specs_root: Path | None = None
        self.destination: Path | None = None
        self.phase_floor: dict[str, tuple[str, ...]] = {}
        self.raw: dict = dict(DEFAULT_CONFIG)


CONFIG = SuperflowConfig()


class ValidationFailure(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


_COLLECT_FAILURES = False



def fail(message: str) -> None:
    if _COLLECT_FAILURES:
        raise ValidationFailure(message)
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_phase_floor(path: Path) -> dict[str, tuple[str, ...]]:
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        fail(f"{path}: phase-vocabulary-floor must be a JSON object")
    floor: dict[str, tuple[str, ...]] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or "\\" in key or key.startswith("/") or key.startswith("specs/"):
            fail(
                f"{path}: floor key {key!r} must be POSIX relative to the specs root, "
                "without specs/ prefix and without an absolute path"
            )
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            fail(f"{path}: floor[{key!r}] must be a list of phase names")
        floor[key] = tuple(value)
    return floor


def resolve_superflow_dir(start: Path, cli_dir: str | None = None) -> Path | None:
    if cli_dir:
        return Path(cli_dir).expanduser()
    env = os.environ.get("SUPERFLOW_DIR")
    if env:
        return Path(env).expanduser()
    cursor = start.resolve()
    for cur in [cursor, *cursor.parents]:
        candidate = cur / ".superflow"
        if (candidate / "config.json").is_file() or candidate.is_dir():
            return candidate
    return None


def load_superflow_config(start: Path, cli_dir: str | None = None) -> SuperflowConfig:
    """CLI → env → walk-up → defaults. No DietFlow path is baked in."""
    cfg = SuperflowConfig()
    superflow_dir = resolve_superflow_dir(start, cli_dir)
    data = dict(DEFAULT_CONFIG)
    if superflow_dir is not None:
        cfg.superflow_dir = superflow_dir
        config_path = superflow_dir / "config.json"
        if config_path.is_file():
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                fail(f"{config_path}: config.json must be an object")
            data.update(loaded)
            floors = dict(DEFAULT_CONFIG["floors"])
            if isinstance(loaded.get("floors"), dict):
                floors.update(loaded["floors"])
            data["floors"] = floors
        cfg.raw = data
        repo_root = superflow_dir.parent
        specs = data.get("specs") or "specs"
        specs_path = Path(str(specs))
        cfg.specs_root = specs_path if specs_path.is_absolute() else (repo_root / specs_path)
        dest = data.get("destination")
        if dest in (None, ""):
            cfg.destination = superflow_dir
        else:
            dest_path = Path(str(dest))
            cfg.destination = dest_path if dest_path.is_absolute() else (superflow_dir / dest_path)
        floor_name = (data.get("floors") or {}).get("phase_vocabulary") or "phase-vocabulary-floor.json"
        cfg.phase_floor = _load_phase_floor(superflow_dir / str(floor_name))
        return cfg

    cwd = Path.cwd()
    default_specs = cwd / "specs"
    if start.name == "specs" and not (start / "status.json").exists():
        cfg.specs_root = start
    elif default_specs.is_dir():
        cfg.specs_root = default_specs
    return cfg


def apply_superflow_config(cfg: SuperflowConfig) -> SuperflowConfig:
    global CONFIG
    CONFIG = cfg
    return cfg


def spec_documents_in(path: Path) -> list[str]:
    """Any markdown in the folder. Not an allowlist of spec names.

    ANALYST.md, HANDBOOK.md, GOAL.md and any other ótica count. A closed
    set of filenames is what made 13 corpus folders disappear from the QG.
    """
    if not path.is_dir():
        return []
    return sorted(
        child.name
        for child in path.iterdir()
        if child.is_file() and child.suffix.lower() == ".md"
    )


def format_unregistered_spec_documents(rel: str, docs: list[str]) -> str:
    listed = ", ".join(docs)
    return (
        f"unregistered_spec_documents: {rel}\n"
        f"  tem {listed} e não tem status.json\n"
        f"  se esta pasta é um pacote, escreva status.json aqui\n"
        f"    (id, route, phase_budget, confidence, current_phase, decision.prd_status=gathering)\n"
        f"  se é acervo de outro pacote, não registre — o registro mora na pasta da mãe\n"
        f"  se é dossiê no lugar errado, não registre; o status.json é o que a torna pacote"
    )


def find_unregistered_spec_documents(specs_root: Path) -> list[tuple[str, list[str]]]:
    found: list[tuple[str, list[str]]] = []
    for directory in [specs_root, *sorted(p for p in specs_root.rglob("*") if p.is_dir())]:
        if (directory / "status.json").exists():
            continue
        docs = spec_documents_in(directory)
        if not docs:
            continue
        rel = (
            "."
            if directory == specs_root
            else directory.relative_to(specs_root).as_posix()
        )
        found.append((rel, docs))
    return found


def extract_phase_string(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("status", "state"):
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                return raw
        if value.get("lastRun") is not None:
            return "complete"
    return None


def normalize_phase_state(value: str | None) -> str | None:
    if not value:
        return None
    if value in PHASE_VOCABULARY:
        return value
    if value in PHASE_STATE_ALIASES:
        return PHASE_STATE_ALIASES[value]
    if value.startswith("complete —") or value.startswith("complete -"):
        return "complete"
    if value.startswith("complete_deployed_dev"):
        return "complete"
    return None


def map_phase_name(name: str) -> str:
    return PHASE_NAME_ALIASES.get(name, name)


def phases_map(status: dict) -> dict:
    phases = status.get("phases")
    return phases if isinstance(phases, dict) else {}


def last_canonical_complete(phases: dict) -> str | None:
    for name in reversed(CURRENT_PHASE_NAMES):
        raw = extract_phase_string(phases.get(name))
        if normalize_phase_state(raw) == "complete":
            return name
        for alias, canonical in PHASE_NAME_ALIASES.items():
            if canonical != name:
                continue
            raw_alias = extract_phase_string(phases.get(alias))
            if normalize_phase_state(raw_alias) == "complete":
                return name
    return None


def derive_current_phase(status: dict) -> str:
    """Value to write when current_phase is missing. Never written by the validator."""
    phases = phases_map(status)
    running = []
    for name, value in phases.items():
        if normalize_phase_state(extract_phase_string(value)) == "running":
            running.append(map_phase_name(name))
    if len(running) == 1 and running[0] in CURRENT_PHASE_NAMES:
        return running[0]
    return last_canonical_complete(phases) or "inbox"


def reads_as_current_phase(raw: str, status: dict) -> str | None:
    if raw in CURRENT_PHASE_NAMES:
        return raw
    if raw == "complete":
        phases = phases_map(status)
        qa = normalize_phase_state(extract_phase_string(phases.get("qa")))
        if qa in {None, "complete"}:
            return "qa"
        return last_canonical_complete(phases) or "qa"
    return CURRENT_PHASE_READS_AS.get(raw)


def find_immediate_mother(path: Path) -> Path | None:
    for parent in path.resolve().parents:
        if (parent / "status.json").exists():
            return parent
    return None


def is_campaign_mother(path: Path, status: dict) -> bool:
    if isinstance(status.get("children_source"), dict):
        return True
    for child in path.rglob("status.json"):
        if child.parent == path:
            continue
        try:
            parts = child.parent.relative_to(path).parts
        except ValueError:
            continue
        if any(part in NESTED_CHILD_FOLDERS for part in parts):
            return True
    return False


def derive_expected_campaign(path: Path, status: dict | None = None) -> str | None:
    """Consumer path: the campaign value this package should write.

    Child: immediate mother's campaign, or her id when she has none.
    Root mother: her own id. Standalone package: None.
    """
    path = path.resolve()
    data = status
    if data is None and (path / "status.json").exists():
        data = json.loads((path / "status.json").read_text(encoding="utf-8"))
    mother = find_immediate_mother(path)
    if mother is not None:
        mother_status = json.loads((mother / "status.json").read_text(encoding="utf-8"))
        mother_campaign = mother_status.get("campaign")
        if isinstance(mother_campaign, str) and mother_campaign.strip():
            return mother_campaign
        mother_id = mother_status.get("id") or mother.name
        return str(mother_id)
    if data is not None and is_campaign_mother(path, data):
        return str(data.get("id") or path.name)
    return None


def is_prd_ready(decision: dict) -> bool:
    return str(decision.get("prd_status") or "").lower() in READY_PRD_STATUSES


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
    for marker in (
        "validate_superflow.py",
        "path-to-package",
        "feature-mindset-contract.md",
        "tdd-contract.md",
        "reuse-guard-protocol.md",
    ):
        if marker not in skill:
            fail(f"skills/superflow/SKILL.md missing production marker: {marker}")
    for skill_name in EXPECTED_PLUGIN_SKILLS:
        skill_path = root / "skills" / skill_name / "SKILL.md"
        skill_text = read(skill_path)
        if not skill_text.startswith("---\n"):
            fail(f"skills/{skill_name}/SKILL.md missing YAML frontmatter")
        if f"name: {skill_name}" not in skill_text:
            fail(f"skills/{skill_name}/SKILL.md frontmatter must include name: {skill_name}")
        if skill_name not in {"audit", "writing-clearly-and-concisely"} and "mermaid" not in skill_text.lower():
            fail(f"skills/{skill_name}/SKILL.md must mention Mermaid contract")
    for skill_name in STANDALONE_PLUGIN_SKILLS:
        skill_path = root / "skills" / skill_name / "SKILL.md"
        skill_text = read(skill_path)
        if not skill_text.startswith("---\n"):
            fail(f"skills/{skill_name}/SKILL.md missing YAML frontmatter")
        if f"name: {skill_name}" not in skill_text:
            fail(f"skills/{skill_name}/SKILL.md frontmatter must include name: {skill_name}")
        if "description:" not in skill_text:
            fail(f"skills/{skill_name}/SKILL.md frontmatter missing description")

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
    validate_prd_tldr(prd_template, label="assets/templates/PRD.md", require_filled=False)
    validate_prd_tldr(issue_template, label="assets/templates/ISSUE_PRD.md", require_filled=False)
    explain_skill = read(root / "skills" / "explain-clearly" / "SKILL.md")
    for marker in (
        "Semantic reconstruction",
        "The source artifact is evidence",
        "`CONFIRMED`",
        "`IN_FLIGHT`",
        "Reasonable-objection gate",
        "Closed-book paraphrase gate",
        "Rewrite from the semantic model",
        "ASCII",
        "Mermaid",
    ):
        if marker not in explain_skill:
            fail(f"skills/explain-clearly/SKILL.md missing semantic marker: {marker}")
    prd_contract = read(root / "assets" / "references" / "prd-contract.md")
    for marker in ("REQUIRED SUB-SKILL", "explain-clearly", "written"):
        if marker not in prd_contract:
            fail(f"assets/references/prd-contract.md missing TL;DR integration marker: {marker}")
    for label, template in (
        ("assets/templates/PRD.md", prd_template),
        ("assets/templates/ISSUE_PRD.md", issue_template),
    ):
        for marker in ("familiar situation", "isn't that desired?", "ASCII sketch or Mermaid"):
            if marker not in template:
                fail(f"{label} missing causal TL;DR prompt: {marker}")

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

    warlog_contract = read(root / "assets" / "references" / "warlog-contract.md")
    for marker in WARLOG_CONTRACT_MARKERS:
        if marker not in warlog_contract:
            fail(f"assets/references/warlog-contract.md missing marker: {marker}")
    if "plantuml" in warlog_contract.lower() and "forbidden" not in warlog_contract.lower():
        # PlantUML may appear only as forbidden word
        pass
    if "@startuml" in warlog_contract or "@startmindmap" in warlog_contract:
        fail("assets/references/warlog-contract.md must not embed PlantUML")

    warlog_skill = read(root / "skills" / "warlog" / "SKILL.md")
    for marker in WARLOG_SKILL_MARKERS:
        if marker not in warlog_skill:
            fail(f"skills/warlog/SKILL.md missing marker: {marker}")

    warlog_template = read(root / "assets" / "templates" / "WARLOG.md")
    for marker in WARLOG_TEMPLATE_MARKERS:
        if marker not in warlog_template:
            fail(f"assets/templates/WARLOG.md missing marker: {marker}")
    if "@startuml" in warlog_template or "plantuml" in warlog_template.lower():
        fail("assets/templates/WARLOG.md must stay Mermaid-only")

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
    # A body that is only a markdown table: header alone, or rows with no content
    if lines and all(ln.startswith("|") for ln in lines):
        rows = [
            [c.strip() for c in ln.strip("|").split("|")]
            for ln in lines
            if not set(ln) <= set("|-: ")  # drop the |---|---| separator
        ]
        if len(rows) <= 1:
            return True
        empty_cell = {"", "-", "—", "...", "…", "tbd", "todo", "pending", "n/a"}
        for row in rows[1:]:
            if any(c and c.lower() not in empty_cell for c in row):
                return False
        return True
    return False


def validate_prd_tldr(text: str, *, label: str, require_filled: bool) -> None:
    """Validate TL;DR placement and reject placeholders in ready PRDs."""
    lines = text.splitlines()
    title_indexes = [i for i, line in enumerate(lines) if re.match(r"^#\s+\S", line)]
    tldr_indexes = [
        i for i, line in enumerate(lines) if re.match(r"^##\s+TL;DR(?:\s|$)", line, re.I)
    ]
    h2_indexes = [i for i, line in enumerate(lines) if re.match(r"^##\s+\S", line)]
    if not title_indexes:
        fail(f"{label}: PRD needs an H1 title before TL;DR")
    if not tldr_indexes:
        fail(f"{label}: PRD missing ## TL;DR")

    title_index = title_indexes[0]
    tldr_index = tldr_indexes[0]
    if tldr_index <= title_index:
        fail(f"{label}: ## TL;DR must come after the PRD title")
    if h2_indexes and tldr_index != h2_indexes[0]:
        fail(f"{label}: ## TL;DR must be the first section after the title")

    body = _section_body(text, "## TL;DR")
    if not require_filled:
        return

    low = body.lower()
    placeholder_markers = (
        "{tldr}",
        "a ser escrito",
        "write the tldr",
        "write after",
        "to be written",
    )
    if _is_placeholder_body(body) or any(marker in low for marker in placeholder_markers):
        fail(
            f"{label}: ready PRD needs a filled TL;DR; semantic clarity "
            "requires the causal/paraphrase review"
        )


# path:line evidence — backticks alone do not count
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
# "morta" and "morte" are the same verdict for a mock string.
_DEST_OK_RE = re.compile(r"\b(invariante|estrutura|mort[ae]s?)\b", re.I)
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


# Where a package decides UI copy. Outside these, prose is analysis, not copy.
COPY_SCOPE_HEADINGS = (
    "## Faceta — Copy",
    "## Faceta - Copy",
    "### Copy",
    "## Copy",
)

# A claim that some text already IS the shipped copy, made outside the facet.
# A denied claim ("não aprovada como UI copy") is the opposite of a claim.
_APPROVAL_CLAIM_RE = re.compile(
    r"(?<!n[ãa]o )(?<!not )(?<!never )"
    r"\b(copy\s+aprovad\w*|ui\s+copy\s+aprovad\w*|aprovad\w*\s+como\s+(?:ui\s+)?copy)\b",
    re.I,
)


def _copy_scopes(text: str) -> list[tuple[str, str]]:
    """Bodies of the Copy facet (analysis `## Faceta — Copy`, SPEC `### Copy`)."""
    scopes: list[tuple[str, str]] = []
    seen: set[str] = set()
    for heading in COPY_SCOPE_HEADINGS:
        if heading not in text:
            continue
        body = _section_body(text, heading)
        if body and body not in seen:
            seen.add(body)
            scopes.append((heading, body))
    return scopes


def _iter_decision_blocks(blob: str):
    """One block per decision: a table row, or a prose paragraph."""
    paragraph: list[str] = []
    for ln in blob.splitlines():
        s = ln.strip()
        if s.startswith("|"):
            if paragraph:
                yield " ".join(paragraph)
                paragraph = []
            if set(s) <= set("|-: "):
                continue
            yield s
            continue
        if not s:
            if paragraph:
                yield " ".join(paragraph)
                paragraph = []
            continue
        paragraph.append(s)
    if paragraph:
        yield " ".join(paragraph)


def _reject_strings_safadas_approved(text: str, *, label: str) -> None:
    """Instance prose must not survive as system UI copy.

    Scope is the Copy facet, where copy is decided. A date in a sprint table or
    a geometry word in a schema note is data, not copy. Inside the facet both
    table rows and free prose count — the sin is the sentence, not the markdown
    shape. A block is honest when it routes the sample to
    invariante|estrutura|morte.

    Outside the facet, only text claiming to already BE approved copy is judged.
    """
    scopes = _copy_scopes(text)
    for heading, blob in scopes:
        for block in _iter_decision_blocks(blob):
            if not _text_looks_safada_instance(block):
                continue
            if _DEST_OK_RE.search(block):
                continue
            fail(
                f"{label}: strings-safadas — instance-form copy in {heading} "
                "without invariante|estrutura|morte destination "
                f"(block: {block[:120]})"
            )

    copy_bodies = [body for _, body in scopes]
    for block in _iter_decision_blocks(text):
        if any(block in body for body in copy_bodies):
            continue
        if not _APPROVAL_CLAIM_RE.search(block):
            continue
        if _text_looks_safada_instance(block) and not _DEST_OK_RE.search(block):
            fail(
                f"{label}: strings-safadas — instance prose marked as approved UI copy "
                f"(block: {block[:120]})"
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


# `new` as a declared decision — a table cell, or prose that decides it.
# "the new modal reuses X" is narration; "decisão: new" is a fork.
_NEW_DECISION_RE = re.compile(
    r"\|\s*new\s*\|"
    r"|\bdecis(?:ão|ao|ion)\w*\s*(?:é|e|=|:|->|→|is)?\s*[`\"'*]*new\b"
    r"|\bnew\b\s*(?:->|→|:)\s*(?:criar|create|build)"
    r"|\b(?:criar|create)\b[^.\n]{0,40}\bnew\b",
    re.I,
)


def _declares_new_decision(frontend: str) -> bool:
    return bool(_NEW_DECISION_RE.search(frontend))


def _require_frontend_decision(frontend: str, *, label: str, depth: str) -> None:
    if depth == "docs" and "skip_reason" in frontend.lower():
        return
    low = frontend.lower()
    has_reuse = bool(re.search(r"\breuse\b", low))
    has_mode = bool(re.search(r"\bmode\b", low))
    has_new = bool(re.search(r"\bnew\b", low))
    if not (has_reuse or has_mode or has_new):
        fail(f"{label}: Frontend facet needs reuse|mode|new decision")
    # A declared `new` always needs the guard table. Saying `reuse` elsewhere in
    # the section is not a substitute — the guard IS where reuse gets proven.
    if _declares_new_decision(frontend) and not _has_reuse_guard_table(frontend):
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

    # Always-on strings-safadas (every depth)
    _reject_strings_safadas_approved(text, label=label)

    if depth == "docs":
        if "## Recode Log" in text:
            recode = _section_body(text, "## Recode Log")
            _require_recode_honest(recode, label=label, depth=depth)
        return

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

    _reject_strings_safadas_approved(text, label=label)

    if depth == "docs":
        if "## Recode Log" in text:
            recode = _section_body(text, "## Recode Log")
            _require_recode_honest(recode, label=label, depth=depth)
        return

    for h in ("## Synthesis", "### Product", "### Backend", "### Frontend", "### Copy"):
        if h not in text:
            fail(f"{label}: missing SPEC mindset heading {h}")
    synthesis = _section_body(text, "## Synthesis")
    if _is_placeholder_body(synthesis):
        fail(f"{label}: SPEC Synthesis empty/placeholder")

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
        subtasks = phase.get("subtasks") or phase.get("tasks")
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
    if "tdd" not in subtask and "behavior" not in subtask:
        return False
    verification = subtask.get("verification") if isinstance(subtask.get("verification"), dict) else {}
    vtype = str(verification.get("type") or "").lower()
    if vtype == "manual" and not subtask.get("files_to_modify") and not subtask.get("files_to_create"):
        return False
    return True


def validate_plan_tdd(plan: dict, *, label: str) -> None:
    if plan.get("schema_version") != "superflow.plan.v1":
        fail(f"{label}: unexpected schema_version (expected superflow.plan.v1)")
    plan_body = plan.get("plan") if isinstance(plan.get("plan"), dict) else plan
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


REVIEW_SEVERITIES = {"blocker", "major", "minor", "nit"}
REVIEW_VERDICTS = {"pending", "accepted", "rejected", "deferred"}
REVIEW_PROOF_SEVERITIES = {"blocker", "major"}

# Agreement wearing the clothes of an argument. Measured by residue: strip the
# agreement phrases and the punctuation, and see whether an argument remains.
_PERFORMATIVE_TOKENS_RE = re.compile(
    r"("
    r"boa\s+(?:observa\w*|coloca\w*|pegada)|voc[eê]\s+tem\s+raz\w*|tem\s+raz\w*|"
    r"concordo|de\s+acordo|isso\s+mesmo|exatamente|exato|perfeito|verdade|"
    r"good\s+catch|nice\s+catch|great\s+point|makes\s+sense|fair\s+enough|agreed|"
    r"obrigad\w*|thanks|valeu|ok|okay|sim|yes|certo"
    r")",
    re.I,
)


def _is_performative_reason(text: str) -> bool:
    residue = _PERFORMATIVE_TOKENS_RE.sub(" ", text)
    residue = re.sub(r"[^\w\s]", " ", residue)
    residue = re.sub(r"\s+", " ", residue).strip()
    return len(residue) < 12


def validate_review_log(review: dict, *, label: str) -> None:
    """R2–R4: findings carry verdicts, verdicts carry arguments, fixes carry proof."""
    if review.get("schema_version") != "superflow.review.v1":
        fail(f"{label}: unexpected schema_version (expected superflow.review.v1)")
    rounds = review.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        fail(f"{label}: rounds must be a non-empty list")

    for rnd in rounds:
        if not isinstance(rnd, dict):
            fail(f"{label}: each round must be an object")
        rid = str(rnd.get("id") or "<missing-id>")
        kind = str(rnd.get("kind") or "").strip().lower()
        if kind not in {"spec", "code"}:
            fail(f"{label}: round {rid} kind must be spec or code")
        if not str(rnd.get("target") or "").strip():
            fail(f"{label}: round {rid} missing target (SPEC.md, task id, or diff)")
        if not str(rnd.get("reviewer") or "").strip():
            fail(f"{label}: round {rid} missing reviewer")

        findings = rnd.get("findings")
        if not isinstance(findings, list):
            fail(f"{label}: round {rid} findings must be a list")
        if not findings:
            reason = str(rnd.get("no_findings_reason") or "").strip()
            if len(reason) < 24:
                fail(
                    f"{label}: round {rid} has no findings and no no_findings_reason — "
                    "a silent empty round is a review that never happened"
                )
            if _is_performative_reason(reason):
                fail(f"{label}: round {rid} no_findings_reason is agreement, not an argument")
            continue

        for finding in findings:
            if not isinstance(finding, dict):
                fail(f"{label}: round {rid} findings must be objects")
            fid = str(finding.get("id") or "<missing-id>")
            severity = str(finding.get("severity") or "").strip().lower()
            if severity not in REVIEW_SEVERITIES:
                fail(
                    f"{label}: finding {fid} severity must be one of "
                    f"{sorted(REVIEW_SEVERITIES)}"
                )
            claim = str(finding.get("claim") or "").strip()
            if len(claim) < 12:
                fail(f"{label}: finding {fid} needs a claim saying what is wrong and where")
            verdict = str(finding.get("verdict") or "").strip().lower()
            if verdict not in REVIEW_VERDICTS:
                fail(
                    f"{label}: finding {fid} verdict must be one of "
                    f"{sorted(REVIEW_VERDICTS)}"
                )

            reason = str(finding.get("reason") or "").strip()
            if verdict in {"rejected", "deferred"}:
                if len(reason) < 12:
                    fail(
                        f"{label}: finding {fid} {verdict} without reason — "
                        "say what the reviewer got wrong, or who owns it later"
                    )
            if reason and _is_performative_reason(reason):
                fail(
                    f"{label}: finding {fid} reason is performative agreement, not an argument"
                )

            if verdict == "accepted":
                proof = finding.get("proof") if isinstance(finding.get("proof"), dict) else None
                task_id = str(finding.get("task_id") or "").strip()
                if severity in REVIEW_PROOF_SEVERITIES:
                    if proof is None:
                        fail(
                            f"{label}: accepted {severity} finding {fid} needs proof "
                            "(command + excerpt) that the fix holds"
                        )
                elif proof is None and not task_id:
                    fail(f"{label}: accepted finding {fid} needs task_id or proof")
                if proof is not None:
                    cmd = str(proof.get("command") or "").strip()
                    excerpt = str(proof.get("excerpt") or "").strip()
                    if not cmd or not excerpt:
                        fail(
                            f"{label}: finding {fid} proof needs command and excerpt — "
                            "a boolean is not evidence"
                        )
                    if proof.get("ok") is not True:
                        fail(f"{label}: finding {fid} proof.ok is not true")


def require_review_when_code_shipped(
    review: dict | None, log: dict | None, *, workflow_type: str, qa_complete: bool, label: str
) -> None:
    """R1: code that reached a complete QA must have been reviewed."""
    if workflow_type in DOCS_WORKFLOW_TYPES:
        return
    if not qa_complete or not isinstance(log, dict):
        return
    tasks = log.get("tasks") if isinstance(log.get("tasks"), list) else []
    shipped = [
        t
        for t in tasks
        if isinstance(t, dict) and str(t.get("status") or "").upper().startswith("DONE")
    ]
    if not shipped:
        return
    if review is None:
        fail(
            f"{label}: QA complete over shipped code with no review_log.json — "
            "code review is a phase, not a courtesy (review-contract.md)"
        )
    rounds = review.get("rounds") if isinstance(review.get("rounds"), list) else []
    if not any(str(r.get("kind") or "").lower() == "code" for r in rounds if isinstance(r, dict)):
        fail(f"{label}: review_log.json has no kind='code' round for shipped code")
    for rnd in rounds:
        if not isinstance(rnd, dict):
            continue
        for finding in rnd.get("findings") or []:
            if not isinstance(finding, dict):
                continue
            if str(finding.get("verdict") or "").lower() == "pending":
                fail(
                    f"{label}: finding {finding.get('id')} still pending — "
                    "QA cannot close over an unanswered review verdict"
                )


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


def validate_package_warlog(text: str, *, label: str) -> None:
    """When WARLOG.md exists, require campaign-board shape (not diary-only)."""
    for h in WARLOG_PACKAGE_HEADINGS:
        if h not in text:
            fail(f"{label}: missing required WARLOG heading {h}")
    if "### S1" not in text and "### S1 —" not in text:
        # accept ### S1 — title or ### S1)
        if not re.search(r"^###\s+S\d+", text, re.M):
            fail(f"{label}: WARLOG needs at least one sprint card (### S1 — …)")
    if "Budget:" not in text and "budget:" not in text.lower():
        fail(f"{label}: sprint card needs Budget (direct|plan|spec)")
    if "Green contract" not in text and "green contract" not in text.lower():
        fail(f"{label}: sprint card needs Green contract")
    if "```mermaid" not in text:
        fail(f"{label}: campaign map requires a mermaid fence")
    low = text.lower()
    if "@startuml" in low or "@startmindmap" in low or "@startwbs" in low:
        fail(f"{label}: PlantUML is forbidden in WARLOG (Mermaid only)")
    if "```plantuml" in low or "```puml" in low:
        fail(f"{label}: PlantUML fences are forbidden in WARLOG")


def _has_heading(text: str, heading: str) -> bool:
    """True when a markdown heading line starts with `heading`.

    Aceita detalhe no fim do título (`## Estado real — dev@abc`), como o
    `_section_body` já faz, e recusa heading que só contém a palavra no meio.
    """
    return re.search(rf"^{re.escape(heading)}(?:\s*$|[\s—:(])", text, re.M) is not None


def _parse_iso_instant(raw: str):
    """Parse ISO-8601 tolerante ao que as specs realmente gravam.

    Python 3.9 não aceita `Z` nem offset sem dois-pontos (`-0300`); ambos
    aparecem nos status.json vivos. Devolve None quando não dá para comparar,
    porque comparar string ISO com offset diferente mente.
    """
    value = (raw or "").strip()
    if not value:
        return None
    if value.endswith(("Z", "z")):
        value = value[:-1] + "+00:00"
    value = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", value)
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _package_floor_key(path: Path, specs_root: Path | None = None) -> str:
    """POSIX path relative to the consumer specs root. No machine path, no specs/ prefix."""
    root = specs_root if specs_root is not None else CONFIG.specs_root
    resolved = path.resolve()
    if root is not None:
        try:
            return resolved.relative_to(root.resolve()).as_posix()
        except ValueError:
            pass
    return path.name


def _render_phase_value(value) -> str:
    if isinstance(value, str):
        return value if len(value) <= 48 else value[:45] + "..."
    return f"<{type(value).__name__}>"


def validate_phase_vocabulary(
    status: dict,
    *,
    label: str,
    floor_key: str,
    floor: dict[str, tuple[str, ...]] | None = None,
) -> None:
    """D3 tipo string + D4 enum. FLOOR mora no consumidor, nunca no plugin."""
    phases = status.get("phases")
    if phases is None:
        phases = {}
    elif not isinstance(phases, dict):
        fail(f"{label}: phases must be an object of string values, got {type(phases).__name__}")

    type_offenders = []
    vocab_offenders = []
    for name, value in phases.items():
        if not isinstance(value, str):
            extracted = extract_phase_string(value)
            mapped = normalize_phase_state(extracted)
            extra = ""
            if extracted is not None:
                extra = f"; extracted {extracted!r} reads as {mapped or 'unknown'} — migrate then vocabulary applies"
            type_offenders.append((name, value, extra))
            continue
        if value not in PHASE_VOCABULARY:
            vocab_offenders.append(name)

    if type_offenders:
        detail = "; ".join(
            f"phases.{name} must be string, got {type(value).__name__}{extra}"
            for name, value, extra in type_offenders
        )
        fail(f"{label}: {detail}")

    floor_map = CONFIG.phase_floor if floor is None else floor
    allowed = floor_map.get(floor_key, ())

    fresh = [name for name in vocab_offenders if name not in allowed]
    if fresh:
        detail = "; ".join(f"{name}={_render_phase_value(phases[name])}" for name in fresh)
        fail(
            f"{label}: fase fora do vocabulário ({detail}) — "
            f"canônico: {', '.join(PHASE_VOCABULARY)}"
        )

    stale = [name for name in allowed if name not in vocab_offenders]
    if stale:
        fail(
            f"{label}: entrada stale no FLOOR de fases ({', '.join(stale)}) — "
            f"o ratchet só encolhe; remova {floor_key!r} de "
            f".superflow/phase-vocabulary-floor.json"
        )


def _validate_handbook_block(block: dict, *, label: str) -> None:
    """O bloco `handbook` do status.json: enums fechados e nada derivável gravado."""
    for key in ["read_at", "read_base", "index_action", "selo", "archivable"]:
        if key not in block:
            fail(f"{label}: status.json handbook missing {key}")

    read_at = str(block.get("read_at") or "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", read_at):
        fail(f"{label}: handbook.read_at must be YYYY-MM-DD, got {read_at!r}")
    if not str(block.get("read_base") or "").strip():
        fail(f"{label}: handbook.read_base must name the base that was read (ex. 'dev@fed5faf18')")

    for key, allowed in [
        ("index_action", HANDBOOK_INDEX_ACTIONS),
        ("selo", HANDBOOK_SELOS),
        ("archivable", HANDBOOK_ARCHIVABLE),
    ]:
        value = block.get(key)
        if value not in allowed:
            fail(f"{label}: handbook.{key}={value!r} is not in {allowed}")

    for key in ["archive_debts", "unanswered"]:
        value = block.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            fail(f"{label}: handbook.{key} must be a list of strings")

    decisions = block.get("open_decisions", [])
    if not isinstance(decisions, list):
        fail(f"{label}: handbook.open_decisions must be a list")
    for item in decisions:
        if not isinstance(item, dict):
            fail(f"{label}: handbook.open_decisions entries must be objects")
        for key in ["id", "question", "owner"]:
            if not str(item.get(key) or "").strip():
                fail(f"{label}: handbook.open_decisions entry missing {key}")

    next_useful = block.get("next_useful", [])
    if not isinstance(next_useful, list):
        fail(f"{label}: handbook.next_useful must be a list")
    for item in next_useful:
        if not isinstance(item, dict):
            fail(f"{label}: handbook.next_useful entries must be objects")
        if not str(item.get("id") or "").strip():
            fail(f"{label}: handbook.next_useful entry missing id")
        if item.get("kind") not in HANDBOOK_NEXT_KINDS:
            fail(
                f"{label}: handbook.next_useful[{item.get('id')!r}].kind="
                f"{item.get('kind')!r} is not in {HANDBOOK_NEXT_KINDS}"
            )
        blocked_by = item.get("blocked_by", [])
        if not isinstance(blocked_by, list) or any(
            not isinstance(dep, str) for dep in blocked_by
        ):
            fail(
                f"{label}: handbook.next_useful[{item.get('id')!r}].blocked_by "
                "must be a list of strings"
            )
        written = [key for key in HANDBOOK_DERIVED_ONLY_KEYS if key in item]
        if written:
            fail(
                f"{label}: handbook.next_useful[{item.get('id')!r}] grava "
                f"{', '.join(written)} — elegibilidade é DERIVADA "
                "(kind != human && blocked_by == []), nunca gravada"
            )

    if "tasks" in block:
        fail(
            f"{label}: handbook.tasks is forbidden — task executável mora em "
            "implementation_plan.json (status-schema invariante 10)"
        )

    rollup = block.get("children_rollup")
    if rollup is not None:
        if not isinstance(rollup, dict):
            fail(f"{label}: handbook.children_rollup must be an object or null")
        for key in ["derived_at", "derived_from", "counts"]:
            if key not in rollup:
                fail(f"{label}: handbook.children_rollup missing {key}")
        if not isinstance(rollup.get("counts"), dict):
            fail(f"{label}: handbook.children_rollup.counts must be an object")


def validate_handbook(text: str, status: dict, *, label: str) -> None:
    """As sete seções de prosa, sem placeholder, com o Estado real ancorado.

    A exigência de âncoras `arquivo:linha` no Estado real é o que liga o retrato
    ao código: sem ela o handbook vira prosa bonita sobre um sistema que ninguém
    abriu — exatamente o defeito que ele existe para corrigir.
    """
    for canonical, aliases in HANDBOOK_REQUIRED_HEADINGS:
        matched = next(
            (alias for alias in aliases if _has_heading(text, f"## {alias}")), None
        )
        if matched is None:
            fail(f"{label}: missing required section: ## {canonical}")
        body = _section_body(text, f"## {matched}")
        if _is_placeholder_body(body):
            fail(
                f"{label}: section ## {canonical} is empty or a placeholder — "
                "handbook sem conteúdo é pior que handbook ausente"
            )
        if canonical == HANDBOOK_EVIDENCE_SECTION:
            anchors = sorted(set(PATH_LINE_RE.findall(body)))
            if len(anchors) < HANDBOOK_MIN_EVIDENCE_ANCHORS:
                fail(
                    f"{label}: ## {canonical} tem {len(anchors)} âncora(s) "
                    f"arquivo:linha; o contrato exige {HANDBOOK_MIN_EVIDENCE_ANCHORS} "
                    "(backtick sozinho não conta)"
                )

    block = status.get("handbook")
    if not isinstance(block, dict):
        fail(
            f"{label}: status.json precisa do bloco `handbook` — "
            "o veredito nasce campo, nunca raspado da prosa"
        )
    _validate_handbook_block(block, label=label)


def warn_stale_handbook_base(path: Path, status: dict, *, label: str) -> None:
    """Retrato velho é dívida visível, não bloqueio.

    Se `read_base` não for ancestral do HEAD, o handbook descreve um estado que
    já andou. Isso avisa; não falha. Travar PR aqui garantiria que ninguém
    escreve o segundo handbook.
    """
    block = status.get("handbook")
    if not isinstance(block, dict):
        return
    base = str(block.get("read_base") or "").strip()
    sha = base.rsplit("@", 1)[-1] if "@" in base else base
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha):
        return
    result = subprocess.run(
        ["git", "-C", str(path), "merge-base", "--is-ancestor", sha, "HEAD"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode in (0, 128):
        # 0 = ancestral; 128 = fora de repo git ou sha desconhecido (não dá para julgar)
        return
    print(
        f"WARN: {label}: read_base {base} não é ancestral do HEAD — "
        "retrato envelhecido (dívida visível, não bloqueio)",
        file=sys.stderr,
    )


def validate_children_rollup(path: Path, status: dict, *, label: str) -> None:
    """`children_source` declara pacote-mãe; o rollup gravado precisa ser fresco.

    O pai não copia estado do filho: ele declara onde os filhos estão e o
    `superflow_campaign.py` deriva na hora. Se alguém cachear o resultado em
    `handbook.children_rollup`, o cache tem de ser mais novo que o filho mais
    novo — cache sem gate de frescor é a mentira que o status do pai já contava.
    """
    source = status.get("children_source")
    if source is None:
        return
    if not isinstance(source, dict):
        fail(f"{label}: children_source must be an object")
    glob = source.get("glob")
    if not isinstance(glob, str) or not glob.strip():
        fail(f"{label}: children_source.glob must be a non-empty glob")
    package_id = status.get("id")
    if source.get("campaign") != package_id:
        fail(
            f"{label}: children_source.campaign={source.get('campaign')!r} "
            f"must equal this package id ({package_id!r})"
        )

    newest = None
    for child in sorted(path.glob(glob)):
        try:
            child_status = json.loads(read(child))
        except json.JSONDecodeError as exc:
            fail(f"{label}: child {child} is not valid JSON: {exc}")
        if child_status.get("campaign") != package_id:
            fail(
                f"{label}: child {child} declares campaign="
                f"{child_status.get('campaign')!r}; the mother package is "
                f"{package_id!r} — filho órfão não entra no rollup"
            )
        stamp = _parse_iso_instant(str(child_status.get("updated_at") or ""))
        if stamp is not None and (newest is None or stamp > newest):
            newest = stamp

    block = status.get("handbook") if isinstance(status.get("handbook"), dict) else {}
    rollup = block.get("children_rollup")
    if not isinstance(rollup, dict) or newest is None:
        return
    derived_at = _parse_iso_instant(str(rollup.get("derived_at") or ""))
    if derived_at is None:
        fail(f"{label}: handbook.children_rollup.derived_at is not a parseable timestamp")
    if derived_at < newest:
        fail(
            f"{label}: handbook.children_rollup.derived_at={rollup.get('derived_at')!r} "
            f"is older than the newest child updated_at ({newest.isoformat()}) — "
            "cache stale não vale como rollup"
        )


def validate_campaign_membership(path: Path, status: dict, *, label: str) -> None:
    """D6: mãe auto-adesiva por campaign==id; filho por ancestral com status.json.

    O guard parent.name == minispecs morreu. Não existe FLOOR de adesão:
    o valor deriva da árvore e o diagnóstico o nomeia.
    """
    expected = derive_expected_campaign(path, status)
    campaign = status.get("campaign")
    mother = find_immediate_mother(path)
    if mother is not None:
        if not isinstance(campaign, str) or not campaign.strip():
            fail(
                f"{label}: filho exige campaign={expected!r} "
                f"(campaign da mãe imediata {mother.name} se ela tiver; senão o id dela)"
            )
        if expected is not None and campaign != expected:
            fail(
                f"{label}: campaign={campaign!r} não bate com o valor derivado "
                f"{expected!r} (campaign da mãe imediata se ela tiver; senão o id dela)"
            )
        return
    if is_campaign_mother(path, status):
        package_id = status.get("id") or path.name
        if campaign != package_id:
            fail(
                f"{label}: mãe exige campaign={package_id!r} "
                "(auto-adesão pelo campo campaign, nunca por depends_on)"
            )


def validate_current_phase(status: dict, *, label: str) -> None:
    """D5: ponteiro ∈ oito nomes. Ausente falha com o valor derivável."""
    raw = status.get("current_phase")
    phases = phases_map(status)
    derived = derive_current_phase(status)
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        fail(
            f"{label}: current_phase is required — derive {derived!r} "
            f"(running phase if any; else last canonical complete; else inbox) "
            f"and write that value; the validator does not fill it"
        )
    if not isinstance(raw, str):
        fail(f"{label}: current_phase must be a string, got {type(raw).__name__}")
    if raw not in CURRENT_PHASE_NAMES:
        mapped = reads_as_current_phase(raw, status)
        if mapped:
            fail(
                f"{label}: current_phase={raw!r} is not one of {CURRENT_PHASE_NAMES} — "
                f"lê-se {mapped!r}; write current_phase={mapped}"
            )
        fail(
            f"{label}: current_phase={raw!r} is not one of {CURRENT_PHASE_NAMES}"
        )

    running = [
        map_phase_name(name)
        for name, value in phases.items()
        if normalize_phase_state(extract_phase_string(value)) == "running"
    ]
    running = [name for name in running if name in CURRENT_PHASE_NAMES]
    if len(running) > 1:
        fail(f"{label}: at most one phases.* may be running, found {running}")
    if len(running) == 1 and raw != running[0]:
        fail(
            f"{label}: current_phase={raw!r} must be the running phase {running[0]!r}"
        )

    pointer_value = extract_phase_string(phases.get(raw))
    pointer_state = normalize_phase_state(pointer_value) if pointer_value is not None else None
    if pointer_state in {"skipped", "superseded"}:
        fail(
            f"{label}: current_phase={raw!r} cannot point at phases.{raw}={pointer_value!r} "
            f"({pointer_state} is not a live pointer)"
        )
    if pointer_state is not None and pointer_state not in POINTER_PHASE_STATES:
        fail(
            f"{label}: phases[{raw}]={pointer_value!r} must be one of {sorted(POINTER_PHASE_STATES)}"
        )

    decision = status.get("decision") if isinstance(status.get("decision"), dict) else {}
    prd_status = str(decision.get("prd_status") or "").lower()
    if prd_status == "gathering" and raw not in GATHERING_PHASES:
        fail(
            f"{label}: decision.prd_status=gathering forbids current_phase={raw!r} "
            f"(invariant 14: stay in {sorted(GATHERING_PHASES)} or promote via the PRD-owning skill)"
        )


def validate_registration(path: Path, status: dict, *, label: str) -> None:
    """Condição A — cadastro. Packagehood + campos de nascimento. Não exige PRD."""
    schema = status.get("schema_version")
    if schema in (None, ""):
        schema = STATUS_SCHEMA_VERSION
    elif schema != STATUS_SCHEMA_VERSION:
        fail(
            f"{path}/status.json has unexpected schema_version={schema!r} "
            f"(lazy absent reads as {STATUS_SCHEMA_VERSION})"
        )
    for key in ["id", "decision"]:
        if key not in status:
            fail(f"{path}/status.json missing {key}")
    for key in ["route", "phase_budget", "confidence", "artifacts", "task_source"]:
        if key not in status:
            fail(f"{path}/status.json missing {key}")
    decision = status.get("decision")
    if not isinstance(decision, dict):
        fail(f"{path}/status.json decision must be an object")
    for key in ["verdict", "prd_status"]:
        if key not in decision:
            fail(f"{path}/status.json decision missing {key}")
    for key in ["reason", "prd_path", "discard_path"]:
        if key not in decision:
            fail(f"{path}/status.json decision missing {key}")
    validate_current_phase(status, label=label)
    validate_phase_vocabulary(status, label=label, floor_key=_package_floor_key(path))
    validate_campaign_membership(path, status, label=label)


def validate_prd_maturity(path: Path, status: dict, decision: dict) -> None:
    """Condição B — ready. O contrato inteiro do PRD. Não promove gathering."""
    if not is_prd_ready(decision):
        return
    prd_path = path / "PRD.md"
    if not prd_path.exists():
        if READY_REQUIRES_PRD_DOCUMENT:
            fail(
                f"{path}: decision.prd_status={decision.get('prd_status')!r} exige PRD.md "
                "(READY_REQUIRES_PRD_DOCUMENT / G20 default)"
            )
        return
    prd_text = read(prd_path)
    validate_prd_tldr(prd_text, label=f"{path}/PRD.md", require_filled=True)
    for heading in PRD_REQUIRED_HEADINGS:
        if heading not in prd_text:
            fail(f"{path}/PRD.md missing heading: {heading}")
    core_prd_aliases = [
        ("State / Header", ["State", "Estado", "A promessa", "Contexto", "PRD", "Cabeçalho", "Correção", "O que esta minispec"]),
        ("Problem / Motivation / Journey", ["Problem", "Problema", "Por que", "O que esta spec resolve", "O veto", "jornada", "O que o produto", "Contexto"]),
        ("Goal / Promise", ["Goal", "Objetivo", "Promessa", "A promessa", "O que esta spec resolve", "O que esta entrega", "O que esta minispec"]),
        ("Scope / Contract / Invariants", ["Scope", "Escopo", "O que o contrato", "As nove minispecs", "O que muda", "O terreno", "Configuração", "Invariantes", "Matriz", "Os dez decretos", "O modelo mental", "E3"]),
        ("Acceptance / Done Criteria", ["Acceptance Criteria", "Critérios de Aceite", "Critérios de pronto", "Definition of Complete", "Definition of Done", "DoD"]),
    ]
    for section_name, aliases in core_prd_aliases:
        matched = False
        for line in prd_text.splitlines():
            if line.startswith("#"):
                if any(alias.lower() in line.lower() for alias in aliases):
                    matched = True
                    break
        if not matched:
            fail(f"{path}/PRD.md missing core section: {section_name}")
    validate_dod_derived_children(path, status, prd_text, label=f"{path}/PRD.md")


def validate_dod_derived_children(path: Path, status: dict, prd_text: str, *, label: str) -> None:
    """DoD cannot name a child the glob finds. Greppable only — not semantic proof."""
    source = status.get("children_source")
    if not isinstance(source, dict):
        return
    glob = source.get("glob")
    if not isinstance(glob, str) or not glob.strip():
        return
    section = _section_body(prd_text, "## Definition of Complete")
    if not section:
        return
    hits: list[str] = []
    for child_file in sorted(path.glob(glob)):
        child_dir = child_file.parent if child_file.name == "status.json" else child_file
        tokens = {child_dir.name}
        try:
            child_status = json.loads(read(child_file if child_file.suffix == ".json" else child_dir / "status.json"))
        except (OSError, json.JSONDecodeError):
            child_status = {}
        child_id = child_status.get("id")
        if isinstance(child_id, str) and child_id.strip():
            tokens.add(child_id)
        for token in sorted(tokens):
            if token and token in section:
                hits.append(token)
    if hits:
        fail(
            f"{label}: ## Definition of Complete names child package(s) {sorted(set(hits))} "
            f"found by children_source.glob={glob!r} — DoD describes the mother's own scope, "
            "never a handwritten list of child state. "
            "This gate catches the greppable violation only; it does not prove semantic "
            "correctness of the DoD and does not recognize paraphrase."
        )


def validate_package(path: Path) -> None:
    """D1: packagehood is status.json. Spec docs without it are not a package."""
    analysis_path = path / "analysis.md"
    spec_path = path / "SPEC.md"
    if not (path / "status.json").exists():
        docs = spec_documents_in(path)
        if docs:
            rel = path.name
            if CONFIG.specs_root is not None:
                try:
                    rel = path.resolve().relative_to(CONFIG.specs_root.resolve()).as_posix()
                except ValueError:
                    rel = path.name
            fail(format_unregistered_spec_documents(rel, docs))
        return

    status = json.loads(read(path / "status.json"))
    label = f"{path}/status.json"
    validate_registration(path, status, label=label)

    artifacts = status.get("artifacts") if isinstance(status.get("artifacts"), dict) else {}
    decision = status["decision"]

    progress_artifact = artifacts.get("progress")
    if progress_artifact and not (path / progress_artifact).exists():
        fail(f"{path}/status.json points to missing progress artifact")

    if is_prd_ready(decision):
        prd_artifact = artifacts.get("prd")
        if prd_artifact and not (path / prd_artifact).exists():
            fail(f"{path}/status.json points to missing PRD artifact")

    # Handbook: broken pointer fails. File on disk without pointer does not
    # force the field. The pointed name is free — not an allowlist of HANDBOOK.md.
    handbook_artifact = artifacts.get("handbook")
    if handbook_artifact:
        handbook_path = path / str(handbook_artifact)
        if not handbook_path.exists():
            fail(f"{path}/status.json points to missing handbook artifact")
        validate_handbook(
            read(handbook_path), status, label=f"{path}/{handbook_artifact}"
        )
        warn_stale_handbook_base(path, status, label=f"{path}/{handbook_artifact}")
    validate_children_rollup(path, status, label=label)
    validate_prd_maturity(path, status, decision)

    plan_artifact = artifacts.get("plan")
    task_source = status.get("task_source") or {}
    if plan_artifact and task_source.get("path") != plan_artifact:
        fail(f"{path}/status.json task_source.path must match artifacts.plan")

    plan_data: dict | None = None
    plan_path = path / "implementation_plan.json"
    if plan_path.exists():
        plan_data = json.loads(read(plan_path))
        validate_plan_tdd(plan_data, label=str(plan_path))

    log_data: dict | None = None
    log_path = path / "implementation_log.json"
    if log_path.exists():
        log_data = json.loads(read(log_path))
        validate_log_tdd(log_data, plan_data, label=str(log_path))

    review_data: dict | None = None
    review_path = path / "review_log.json"
    if review_path.exists():
        review_data = json.loads(read(review_path))
        validate_review_log(review_data, label=str(review_path))

    workflow_type = str(status.get("workflow_type") or "").strip().lower()
    qa_complete = str(phases_map(status).get("qa") or "").lower() == "complete"
    require_review_when_code_shipped(
        review_data,
        log_data,
        workflow_type=workflow_type,
        qa_complete=qa_complete,
        label=str(path),
    )

    depth = derive_mindset_depth(status)
    marker = path / "mindset-depth.txt"
    if marker.exists():
        raw = read(marker).strip().lower()
        if raw == "skip":
            fail(f"{path}/mindset-depth.txt: 'skip' is forbidden (no mindset escape hatch)")
        if raw == "trap" and depth == "deep":
            depth = "trap"

    if analysis_path.exists():
        validate_analysis_mindset(read(analysis_path), label=str(analysis_path), depth=depth)

    if spec_path.exists():
        validate_spec_mindset(read(spec_path), label=str(spec_path), depth=depth)

    warlog_path = path / "WARLOG.md"
    if warlog_path.exists():
        validate_package_warlog(read(warlog_path), label=str(warlog_path))


def validate_specs_root(root: Path) -> None:
    """Repo mode: every typed package plus unregistered_spec_documents."""
    global _COLLECT_FAILURES
    failures = 0
    _COLLECT_FAILURES = True
    try:
        for status_file in sorted(root.rglob("status.json")):
            try:
                validate_package(status_file.parent)
            except ValidationFailure as exc:
                print(f"FAIL: {exc.message}", file=sys.stderr)
                failures += 1
        for rel, docs in find_unregistered_spec_documents(root):
            print(f"FAIL: {format_unregistered_spec_documents(rel, docs)}", file=sys.stderr)
            failures += 1
    finally:
        _COLLECT_FAILURES = False
    if failures:
        raise SystemExit(1)


def _is_specs_root(root: Path) -> bool:
    if (root / "status.json").exists():
        return False
    if CONFIG.specs_root is not None and root.resolve() == CONFIG.specs_root.resolve():
        return True
    if root.name == "specs" and any(root.rglob("status.json")):
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Superflow skill root or generated specs/NNN folder.")
    parser.add_argument("--mermaid", action="store_true", help="Render Mermaid blocks with mmdc.")
    parser.add_argument(
        "--superflow-dir",
        help="Directory containing config.json (runtime path; never a versioned machine path).",
    )
    parser.add_argument(
        "--derive-campaign",
        action="store_true",
        help="Print the derived campaign value and exit. Does not write status.json.",
    )
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        fail(f"path does not exist: {root}")

    apply_superflow_config(load_superflow_config(root, args.superflow_dir))

    if args.derive_campaign:
        if (root / "status.json").exists():
            print(derive_expected_campaign(root) or "")
            return 0
        for status_file in sorted(root.rglob("status.json")):
            pkg = status_file.parent
            rel = pkg.name
            if CONFIG.specs_root is not None:
                try:
                    rel = pkg.resolve().relative_to(CONFIG.specs_root.resolve()).as_posix()
                except ValueError:
                    rel = pkg.name
            print(f"{rel}\t{derive_expected_campaign(pkg) or ''}")
        return 0

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
    elif _is_specs_root(root):
        validate_specs_root(root)
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
