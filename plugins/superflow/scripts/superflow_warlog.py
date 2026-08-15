#!/usr/bin/env python3
"""Create or update a Superflow WARLOG for a local package."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SCRIPT_ROOT / "assets" / "templates" / "WARLOG.md"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_title(package: Path, status: dict) -> str:
    if status.get("title"):
        return str(status["title"])
    prd = package / "PRD.md"
    if prd.exists():
        for line in prd.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line.removeprefix("# ").removeprefix("PRD: ").strip()
    return package.name


def sprint_budget_from_phase(phase_budget: str) -> str:
    """Map package phase_budget → sprint budget (direct|plan|spec)."""
    b = (phase_budget or "").lower().strip()
    if b in {"capture", "lean"}:
        return "direct"
    if b in {"standard"}:
        return "plan"
    if b in {"deep", "forensic"}:
        return "spec"
    return "plan"


def render_template(package: Path, status: dict, now: str) -> str:
    title = read_title(package, status)
    phase_budget = str(status.get("phase_budget", "unknown"))
    route = str(status.get("route", "unknown"))
    next_phase = next_pending_phase(status)
    classification = {
        "title": title,
        "mission": f"Deliver {title} as a durable Superflow campaign with mergeable sprints.",
        "scope_in": "This package’s product promise and its mergeable slices.",
        "scope_out": "Unrelated epics; microtask tracking (use Plan/log).",
        "created_at": now,
        "route": route,
        "phase_budget": phase_budget,
        "confidence": status.get("confidence", "unknown"),
        "source": status.get("source", {}).get("type", "unknown")
        if isinstance(status.get("source"), dict)
        else "unknown",
        "next_phase": next_phase,
        "first_sprint_title": f"First mergeable slice toward {title}",
        "sprint_budget": sprint_budget_from_phase(phase_budget),
        "risks": "Replace this shell with real sprint cards before claiming campaign ready.",
    }
    return TEMPLATE.read_text(encoding="utf-8").format(**classification)


def next_pending_phase(status: dict) -> str:
    phases = status.get("phases", {})
    if isinstance(phases, dict):
        for phase, state in phases.items():
            if state == "pending":
                return str(phase)
    return "review current status"


def append_event(path: Path, event: str, now: str, phase: str | None) -> None:
    text = path.read_text(encoding="utf-8")
    label = phase or "warlog"
    line = f"- {now} | {label} | {event}\n"
    marker = "## Event Log\n\n"
    if marker in text:
        text = text.replace(marker, marker + line, 1)
    else:
        text = text.rstrip() + "\n\n## Event Log\n\n" + line
    path.write_text(text, encoding="utf-8")


def update_status(status_path: Path, status: dict, now: str, phase: str | None, phase_state: str | None) -> None:
    artifacts = status.setdefault("artifacts", {})
    artifacts["warlog"] = "WARLOG.md"
    if phase and phase_state:
        phases = status.setdefault("phases", {})
        phases[phase] = phase_state
    status["updated_at"] = now
    write_json(status_path, status)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="Path to specs/NNN-slug package.")
    parser.add_argument("--event", default=None, help="Append an event to the WARLOG.")
    parser.add_argument("--phase", default=None, help="Phase name to update in status.json.")
    parser.add_argument(
        "--phase-state",
        choices=["pending", "running", "complete", "skipped", "blocked", "failed"],
        default=None,
        help="Phase state to write when --phase is provided.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    package = Path(args.package).expanduser().resolve()
    status_path = package / "status.json"
    if not status_path.exists():
        print(f"FAIL: missing status.json in {package}", file=sys.stderr)
        return 1

    status = read_json(status_path)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    warlog = package / "WARLOG.md"
    created = not warlog.exists()

    if args.dry_run:
        print(json.dumps({
            "package": str(package),
            "warlog": str(warlog),
            "would_create": created,
            "event": args.event,
            "phase": args.phase,
            "phase_state": args.phase_state,
        }, indent=2))
        return 0

    if created:
        warlog.write_text(render_template(package, status, now), encoding="utf-8")
    if args.event:
        append_event(warlog, args.event, now, args.phase)
    update_status(status_path, status, now, args.phase, args.phase_state)

    print(json.dumps({
        "package": str(package),
        "warlog": str(warlog),
        "created": created,
        "updated_status": str(status_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
