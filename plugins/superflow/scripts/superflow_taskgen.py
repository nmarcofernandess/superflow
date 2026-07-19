#!/usr/bin/env python3
"""Create Superflow PRD packages or issue-ready PRD bodies."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_ROOT / "assets" / "templates"


RISK_KEYWORDS = {
    "schema",
    "migration",
    "migracao",
    "database",
    "banco",
    "auth",
    "permissao",
    "permission",
    "security",
    "seguranca",
    "billing",
    "pagamento",
    "cache",
    "fila",
    "queue",
    "async",
    "concorrencia",
    "race",
    "cross-module",
    "arquitetura",
    "refactor",
    "refatorar",
    "api",
}

BUG_KEYWORDS = {
    "bug",
    "erro",
    "falha",
    "quebra",
    "crash",
    "investigar",
    "descobrir",
    "porque",
    "por que",
}

ANALYST_KEYWORDS = {
    "pensar",
    "analisa",
    "analyst",
    "ambiguidade",
    "produto",
    "fluxo",
    "jornada",
    "regra",
    "dominio",
}


def slugify(text: str, max_words: int = 7) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[a-zA-Z0-9]+", ascii_text.lower())
    stop = {"a", "o", "os", "as", "de", "do", "da", "dos", "das", "e", "para"}
    useful = [word for word in words if word not in stop][:max_words]
    return "-".join(useful) or "superflow-task"


def titleize(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return "Superflow task"
    if len(cleaned) <= 80:
        return cleaned[0].upper() + cleaned[1:]
    words = cleaned.split()[:10]
    return " ".join(words)[0:90].rstrip(" .,;:") + "..."


def extract_markdown_title(text: str) -> str | None:
    for line in text.splitlines():
        match = re.match(r"^#\s+(?:PRD:\s*)?(.+?)\s*$", line.strip(), re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def contains_any(text: str, needles: set[str]) -> bool:
    lower = text.lower()
    return any(needle in lower for needle in needles)


def has_bug_signal(text: str) -> bool:
    lower = text.lower()
    sanitized = lower
    for phrase in ["sem quebrar", "nao quebrar", "não quebrar", "sem quebra", "nao quebra", "não quebra"]:
        sanitized = sanitized.replace(phrase, "")
    return contains_any(sanitized, BUG_KEYWORDS)


def score_maturity(text: str) -> int:
    lower = text.lower()
    score = 0
    word_count = len(re.findall(r"\w+", text))

    if word_count >= 14:
        score += 1
    if any(k in lower for k in ["quero", "precisa", "deve", "implementar", "criar", "corrigir"]):
        score += 1
    if any(k in lower for k in ["usuario", "user", "cliente", "admin", "nutri", "operador"]):
        score += 1
    if any(k in lower for k in ["tela", "modal", "botao", "button", "form", "api", "endpoint", "relatorio", "dashboard"]):
        score += 1
    if re.search(r"[/\\][\w.-]+|src/|app/|docs/|specs/|issue\s+#?\d+", lower):
        score += 1
    if any(k in lower for k in ["criterio", "aceite", "done", "validar", "teste", "qa"]):
        score += 1
    if any(k in lower for k in ["nao deve", "fora de escopo", "sem mexer", "sem alterar", "preservar", "constraint", "limite"]):
        score += 1
    if any(k in lower for k in ["dados", "api", "estado", "status", "contrato", "arquivo", "csv", "exportar", "filtro"]):
        score += 1

    return min(score, 7)


def score_risk(text: str) -> int:
    lower = text.lower()
    score = 0
    for keyword in RISK_KEYWORDS:
        if keyword in lower:
            score += 1
    if has_bug_signal(lower):
        score += 1
    if any(k in lower for k in ["varios modulos", "multi-modulo", "shared", "primitivo"]):
        score += 1
    return min(score, 8)


def classify(text: str, mode: str, explicit_route: str | None) -> dict:
    maturity = score_maturity(text)
    risk = score_risk(text)
    lower = text.lower()

    if explicit_route:
        route = explicit_route
    elif mode == "issue":
        route = "inbox_only" if maturity <= 2 else "inbox_prd"
    elif has_bug_signal(lower) and maturity <= 4:
        route = "investigate_first"
    elif contains_any(lower, ANALYST_KEYWORDS) and maturity <= 4:
        route = "analyst_prd"
    elif risk >= 4:
        route = "build_plan_execute"
    elif mode == "local" and maturity < 5:
        route = "local_prd"
    elif maturity <= 2:
        route = "inbox_only"
    elif maturity <= 4:
        route = "inbox_prd"
    elif risk >= 2:
        route = "prd_plan_execute"
    else:
        route = "prd_execute"

    if route in {"inbox_only", "inbox_prd"}:
        phase_budget = "capture"
    elif route in {"prd_execute", "local_prd"} and risk <= 1 and maturity >= 5:
        phase_budget = "lean"
    elif route in {"prd_plan_execute", "local_prd"}:
        phase_budget = "standard"
    elif route in {"analyst_prd", "build_plan_execute"}:
        phase_budget = "deep"
    elif route == "investigate_first":
        phase_budget = "forensic"
    else:
        phase_budget = "standard"

    if maturity >= 5 and risk <= 2:
        confidence = "high"
    elif maturity >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    if route == "prd_execute":
        next_phase = "execute"
        skipped = ["analyst", "build", "plan"]
    elif route == "prd_plan_execute":
        next_phase = "plan"
        skipped = ["analyst", "build"]
    elif route == "build_plan_execute":
        next_phase = "build"
        skipped = []
    elif route == "analyst_prd":
        next_phase = "analyst"
        skipped = []
    elif route == "investigate_first":
        next_phase = "analyst"
        skipped = []
    elif route in {"inbox_only", "inbox_prd"}:
        next_phase = "promote when mature"
        skipped = ["analyst", "build", "plan", "execute", "qa"]
    else:
        next_phase = "route review"
        skipped = []

    return {
        "maturity_score": maturity,
        "risk_score": risk,
        "route": route,
        "phase_budget": phase_budget,
        "confidence": confidence,
        "next_phase": next_phase,
        "skipped_phases": skipped,
    }


def read_template(name: str) -> str:
    return (TEMPLATE_DIR / name).read_text(encoding="utf-8")


def render(template_name: str, values: dict) -> str:
    template = read_template(template_name)
    safe_values = {key: str(value) for key, value in values.items()}
    return template.format(**safe_values)


def next_spec_dir(root: Path, specs_dir: str, slug: str) -> Path:
    specs_root = root / specs_dir
    specs_root.mkdir(parents=True, exist_ok=True)
    highest = 0
    for child in specs_root.iterdir():
        if child.is_dir():
            match = re.match(r"^(\d{3})-", child.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return specs_root / f"{highest + 1:03d}-{slug}"


def phase_status(route: str) -> dict:
    phases = {
        "inbox": "skipped",
        "analyst": "skipped",
        "taskgen": "complete",
        "build": "skipped",
        "critic": "skipped",
        "plan": "skipped",
        "execute": "pending",
        "qa": "pending",
    }
    if route in {"inbox_only", "inbox_prd"}:
        phases.update({"inbox": "complete", "execute": "skipped", "qa": "skipped"})
    elif route == "analyst_prd":
        phases.update({"analyst": "pending", "execute": "skipped", "qa": "skipped"})
    elif route == "build_plan_execute":
        phases.update({"build": "pending", "plan": "pending"})
    elif route == "prd_plan_execute":
        phases.update({"plan": "pending"})
    elif route == "investigate_first":
        phases.update({"analyst": "pending", "execute": "skipped", "qa": "skipped"})
    return phases


def current_phase(classification: dict) -> str:
    next_phase = classification["next_phase"]
    if next_phase == "promote when mature":
        return "inbox"
    if next_phase == "route review":
        return "taskgen"
    return str(next_phase)


def decision_payload(classification: dict) -> dict:
    """Scaffold-time decision only. The script never promotes a PRD:
    prd_status is always "gathering". Promotion to "ready" (or "blocked"/
    "superseded") is an act of the skill that wrote or reviewed the PRD
    content against the PRD contract — never of a keyword score."""
    route = classification["route"]
    if route in {"inbox_only", "inbox_prd"}:
        verdict = "inbox"
        reason = "Captured for inbox/backlog; not committed to local execution."
        prd_path = None
    elif route == "analyst_prd":
        verdict = "needs_analysis"
        reason = "Product/domain ambiguity must be resolved before PRD promotion."
        prd_path = "PRD.md"
    elif route == "investigate_first":
        verdict = "needs_analysis"
        reason = "Bug or behavior lacks proven cause; Analyst must investigate before the fix is scoped."
        prd_path = "PRD.md"
    else:
        verdict = "prd_draft"
        reason = "Scaffolded by taskgen; the PRD-owning skill must review the content and promote gathering -> ready."
        prd_path = "PRD.md"

    return {
        "verdict": verdict,
        "prd_status": "gathering",
        "reason": reason,
        "prd_path": prd_path,
        "discard_path": None,
    }


def build_values(args: argparse.Namespace, classification: dict) -> dict:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    title = args.title or extract_markdown_title(args.description) or titleize(args.description)
    source = args.source_type
    return {
        "title": title,
        "source": source,
        "confidence": classification["confidence"],
        "route": classification["route"],
        "phase_budget": classification["phase_budget"],
        "execution_strategy": args.execution_strategy,
        "created_at": now,
        "problem": args.description.strip(),
        "goal": "Turn the request into a durable, verifiable workflow artifact.",
        "actor": "User or operator named by the PRD author",
        "user_story": (
            "As the user or operator named by this request, I want the requested "
            "outcome to be captured and routed so the work can be verified instead "
            "of rediscovered."
        ),
        "technical_story": (
            "As the implementing agent, I need a durable PRD, correct phase route, "
            "status updates, and evidence artifacts so execution can proceed without "
            "hidden context."
        ),
        "in_scope": "Define the intended behavior and route it through the selected Superflow phases.",
        "out_of_scope": "Do not expand beyond the described request without explicit approval.",
        "expected_behavior": "The final implementation or artifact satisfies the acceptance criteria and preserves existing behavior outside scope.",
        "current_behavior": "Not proven yet. The next phase must ground existing-system claims before implementation.",
        "desired_behavior": "The requested outcome is delivered through the selected Superflow route with traceable artifacts.",
        "system_pattern": "Use repository-native patterns and record evidence before marking implementation phases complete.",
        "acceptance_criteria": "The selected next phase can verify this PRD against concrete evidence.",
        "definition_of_complete": "All acceptance criteria have matching evidence and required Superflow artifacts are current.",
        "technical_context": "To be filled from repository inspection when the next phase runs.",
        "data_contracts": "No data contract identified yet.",
        "ux_states": "No UX states identified yet.",
        "risks": "Risk score: {risk_score}. Review before execution.".format(**classification),
        "open_questions": "None recorded yet.",
        "next_phase": classification["next_phase"],
        "local_package": "none",
        "skipped_phases": "\n".join(f"- {phase}" for phase in classification["skipped_phases"]) or "- none",
        "notes": "Generated by Superflow taskgen.",
    }


def write_local_package(args: argparse.Namespace, classification: dict, values: dict) -> Path:
    root = Path(args.root).expanduser().resolve()
    slug = args.slug or slugify(values["title"])
    spec_dir = next_spec_dir(root, args.specs_dir, slug)
    if spec_dir.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing spec dir: {spec_dir}")
    spec_dir.mkdir(parents=True, exist_ok=True)
    values = dict(values)
    values["local_package"] = str(spec_dir.relative_to(root))

    (spec_dir / "PRD.md").write_text(render("PRD.md", values), encoding="utf-8")
    (spec_dir / "progress.md").write_text(render("progress.md", values), encoding="utf-8")
    if args.with_warlog:
        (spec_dir / "WARLOG.md").write_text(render("WARLOG.md", values), encoding="utf-8")

    status = {
        "schema_version": "superflow.status.v1",
        "id": spec_dir.name,
        "title": values["title"],
        "route": classification["route"],
        "phase_budget": classification["phase_budget"],
        "execution_strategy": args.execution_strategy,
        "source": {
            "type": args.source_type,
            "github_issue": args.github_issue,
            "file": args.source_file,
        },
        "confidence": classification["confidence"],
        "current_phase": current_phase(classification),
        "decision": decision_payload(classification),
        "scores": {
            "maturity": classification["maturity_score"],
            "risk": classification["risk_score"],
        },
        "phases": phase_status(classification["route"]),
        "artifacts": {
            "prd": "PRD.md",
            "analysis": None,
            "blueprint": None,
            "progress": "progress.md",
            "warlog": "WARLOG.md" if args.with_warlog else None,
            "plan": None,
            "implementation_log": None,
            "qa": None,
        },
        "task_source": {
            "type": "none",
            "path": None,
            "progress": None,
        },
        "updated_at": values["created_at"],
    }
    (spec_dir / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return spec_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("description", nargs="?", help="Idea, task, PRD seed, or issue summary.")
    parser.add_argument("--root", default=".", help="Repository root for local packages.")
    parser.add_argument("--specs-dir", default="specs", help="Specs directory relative to root.")
    parser.add_argument("--mode", choices=["auto", "local", "issue"], default="auto")
    parser.add_argument("--route", default=None, help="Force a Superflow route.")
    parser.add_argument("--title", default=None)
    parser.add_argument("--slug", default=None)
    parser.add_argument("--source-type", default="inline")
    parser.add_argument("--source-file", default=None)
    parser.add_argument("--github-issue", default=None)
    parser.add_argument("--promote-issue", default=None, help="Promote an issue number/body into a local package.")
    parser.add_argument("--from-file", default=None, help="Read description/issue body from a file. Use '-' for stdin.")
    parser.add_argument("--execution-strategy", choices=["single", "per_unit", "manual"], default="single")
    parser.add_argument("--with-warlog", action="store_true", help="Create WARLOG.md and status artifact link.")
    parser.add_argument("--output", default=None, help="Write issue body to this path in issue mode.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    parser.add_argument("--classify-only", action="store_true", help="Only classify route/budget; do not write files.")
    args = parser.parse_args()

    if args.from_file == "-":
        args.description = sys.stdin.read()
    elif args.from_file:
        args.description = Path(args.from_file).expanduser().read_text(encoding="utf-8")
        args.source_file = args.from_file
    if not args.description:
        parser.error("description is required unless --from-file is used")

    if args.promote_issue:
        args.mode = "local"
        args.source_type = "github_issue"
        args.github_issue = args.promote_issue

    classification = classify(args.description, args.mode, args.route)
    values = build_values(args, classification)

    if args.classify_only:
        payload = {
            "mode": "classify",
            "title": values["title"],
            "classification": classification,
            "source": {
                "type": args.source_type,
                "github_issue": args.github_issue,
                "file": args.source_file,
            },
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Titulo: {payload['title']}")
            print(f"Rota sugerida: {classification['route']}")
            print(f"Budget de fases: {classification['phase_budget']}")
            print(f"Confianca: {classification['confidence']}")
            print(f"Proxima fase: {classification['next_phase']}")
        return 0

    if args.mode == "issue" or classification["route"] in {"inbox_only", "inbox_prd"} and args.mode != "local":
        body = render("ISSUE_PRD.md", values)
        if args.output:
            Path(args.output).expanduser().write_text(body, encoding="utf-8")
        if args.json:
            print(json.dumps({"mode": "issue", "classification": classification}, indent=2))
        else:
            print(body)
        return 0

    spec_dir = write_local_package(args, classification, values)
    result = {
        "mode": "local",
        "spec_dir": str(spec_dir),
        "classification": classification,
        "next_command": f"/superflow --resume {spec_dir.name[:3]}",
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"PRD criado: {spec_dir}")
        print(f"Rota sugerida: {classification['route']}")
        print(f"Budget de fases: {classification['phase_budget']}")
        print(f"Proximo passo: {result['next_command']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
