#!/usr/bin/env python3
"""Compute the verdict of a Superflow campaign over its real packages.

The WARLOG narrates a campaign; this motor reads the packages and answers what
is actionable now and whether the campaign is actually finished.

Exit codes: 0 done, 10 next, 20 blocked, 1 contract error.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATE = SCRIPT_DIR / "validate_superflow.py"

EXIT_DONE = 0
EXIT_NEXT = 10
EXIT_BLOCKED = 20
EXIT_CONTRACT = 1

MAX_DEPTH = 3


class ContractError(Exception):
    """A campaign that cannot be computed: cycle, ghost dependency, or a lie."""


def discover_packages(root: Path) -> list[Path]:
    """Directories holding a status.json, nearest first."""
    found: list[Path] = []
    if (root / "status.json").exists():
        found.append(root)
    for depth in range(1, MAX_DEPTH + 1):
        for status in root.glob("/".join(["*"] * depth) + "/status.json"):
            pkg = status.parent
            if pkg not in found:
                found.append(pkg)
    return sorted(found)


def validate_package(pkg: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, str(VALIDATE), str(pkg)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode == 0, result.stdout.strip()


def read_package(pkg: Path) -> dict:
    try:
        status = json.loads((pkg / "status.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"{pkg}/status.json is not valid JSON: {exc}") from exc

    depends_on = status.get("depends_on") or []
    if not isinstance(depends_on, list) or any(not isinstance(d, str) for d in depends_on):
        raise ContractError(f"{pkg}/status.json depends_on must be a list of package ids")

    phases = status.get("phases") if isinstance(status.get("phases"), dict) else {}
    blocked_phases = [name for name, state in phases.items() if str(state).lower() == "blocked"]
    blocked_reason = str(status.get("blocked_reason") or "").strip()
    if blocked_phases and len(blocked_reason) < 12:
        raise ContractError(
            f"{pkg.name}: phase {blocked_phases[0]} is blocked without blocked_reason — "
            "a blocker nobody signed is an abandonment (campaign-contract.md C4)"
        )

    return {
        "id": pkg.name,
        "path": str(pkg),
        "campaign": status.get("campaign"),
        "depends_on": depends_on,
        "qa_complete": str(phases.get("qa") or "").lower() == "complete",
        "blocked_phases": blocked_phases,
        "blocked_reason": blocked_reason,
    }


def resolve_order(packages: list[dict]) -> None:
    """Raise on ghost dependencies and cycles."""
    by_id = {p["id"]: p for p in packages}
    for pkg in packages:
        for dep in pkg["depends_on"]:
            if dep not in by_id:
                raise ContractError(
                    f"{pkg['id']} depends on {dep}, which is not a package in this campaign"
                )

    visiting: set[str] = set()
    done: set[str] = set()

    def walk(pid: str, trail: list[str]) -> None:
        if pid in done:
            return
        if pid in visiting:
            cycle = " -> ".join(trail + [pid])
            raise ContractError(f"dependency cycle: {cycle}")
        visiting.add(pid)
        for dep in by_id[pid]["depends_on"]:
            walk(dep, trail + [pid])
        visiting.discard(pid)
        done.add(pid)

    for pkg in packages:
        walk(pkg["id"], [])


def compute(root: Path, campaign: str | None) -> tuple[str, dict]:
    packages = [read_package(p) for p in discover_packages(root)]
    if campaign:
        packages = [p for p in packages if p["campaign"] == campaign]
    if not packages:
        raise ContractError(
            f"no packages found under {root}"
            + (f" for campaign {campaign}" if campaign else "")
        )

    resolve_order(packages)

    # C3: closed is the validator's verdict, not the checkbox alone
    for pkg in packages:
        if not pkg["qa_complete"]:
            continue
        ok, output = validate_package(Path(pkg["path"]))
        if not ok:
            raise ContractError(
                f"{pkg['id']} claims qa complete but the validator refuses it:\n{output}"
            )
        pkg["state"] = "closed"

    closed_ids = {p["id"] for p in packages if p.get("state") == "closed"}
    for pkg in packages:
        if pkg.get("state") == "closed":
            continue
        if pkg["blocked_phases"]:
            pkg["state"] = "blocked"
        elif all(dep in closed_ids for dep in pkg["depends_on"]):
            pkg["state"] = "actionable"
        else:
            pkg["state"] = "waiting"

    report = {
        "root": str(root),
        "campaign": campaign,
        "packages": packages,
        "closed": sorted(closed_ids),
        "blocked": [
            {"id": p["id"], "reason": p["blocked_reason"]}
            for p in packages
            if p["state"] == "blocked"
        ],
    }

    actionable = [p for p in packages if p["state"] == "actionable"]
    if actionable:
        report["verdict"] = "next"
        report["next"] = actionable[0]
        return "next", report
    if len(closed_ids) == len(packages):
        report["verdict"] = "done"
        return "done", report
    report["verdict"] = "blocked"
    return "blocked", report


def render_text(verdict: str, report: dict) -> str:
    lines = [f"campaign: {report.get('campaign') or '(all packages)'}"]
    for pkg in report["packages"]:
        deps = ", ".join(pkg["depends_on"]) or "—"
        line = f"  [{pkg['state']:>10}] {pkg['id']}  deps: {deps}"
        if pkg["state"] == "blocked":
            line += f"\n               blocked: {pkg['blocked_reason']}"
        lines.append(line)
    if verdict == "next":
        lines.append(f"\nNEXT: {report['next']['id']} ({report['next']['path']})")
    elif verdict == "blocked":
        lines.append("\nBLOCKED: nothing actionable and the campaign is not finished.")
    else:
        lines.append("\nDONE: every package in scope is closed and validated.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Directory holding the campaign packages.")
    parser.add_argument("--campaign", help="Only packages carrying this campaign name.")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"CONTRACT: path does not exist: {root}", file=sys.stderr)
        return EXIT_CONTRACT

    try:
        verdict, report = compute(root, args.campaign)
    except ContractError as exc:
        if args.json:
            print(json.dumps({"verdict": "contract_error", "error": str(exc)}, indent=2))
        else:
            print(f"CONTRACT: {exc}", file=sys.stderr)
        return EXIT_CONTRACT

    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_text(verdict, report))
    return {"done": EXIT_DONE, "next": EXIT_NEXT, "blocked": EXIT_BLOCKED}[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
