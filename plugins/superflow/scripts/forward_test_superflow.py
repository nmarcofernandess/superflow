#!/usr/bin/env python3
"""Forward-test Superflow in a temporary git repository."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TASKGEN = SCRIPT_DIR / "superflow_taskgen.py"
VALIDATE = SCRIPT_DIR / "validate_superflow.py"
GITHUB = SCRIPT_DIR / "superflow_github.py"
AUDIT = SCRIPT_DIR / "superflow_audit.py"
WARLOG = SCRIPT_DIR / "superflow_warlog.py"


def run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="superflow-forward.") as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        run(["git", "init"], cwd=root)
        run(["git", "config", "user.name", "Superflow Test"], cwd=root)
        run(["git", "config", "user.email", "superflow@example.test"], cwd=root)
        write(root / "README.md", "# Fixture Repo\n")
        write(root / "src" / "reports.ts", "export function listReports() { return [] as string[]; }\n")
        run(["git", "add", "."], cwd=root)
        run(["git", "commit", "-m", "fixture"], cwd=root)

        classify = run([
            sys.executable,
            str(TASKGEN),
            "--root",
            str(root),
            "--mode",
            "local",
            "--classify-only",
            "--json",
            "implementar botao exportar CSV na tela de relatorios para usuario admin com teste validavel e sem alterar filtros existentes",
        ])
        classification = json.loads(classify.stdout)["classification"]
        if classification["route"] != "prd_execute" or classification["phase_budget"] != "lean":
            raise AssertionError(f"unexpected classify route: {classification}")

        audit = run([
            sys.executable,
            str(AUDIT),
            "--format",
            "json",
            "implementar botao exportar CSV na tela de relatorios para usuario admin com teste validavel e sem alterar filtros existentes",
        ])
        audit_payload = json.loads(audit.stdout)
        if audit_payload["classification"]["route"] != "prd_execute":
            raise AssertionError(f"unexpected audit route: {audit_payload}")
        if "Improve PRD gaps before execution." not in audit_payload["next_actions"]:
            raise AssertionError("audit should flag missing PRD details for raw inline request")

        local = run([
            sys.executable,
            str(TASKGEN),
            "--root",
            str(root),
            "--mode",
            "local",
            "--json",
            "implementar botao exportar CSV na tela de relatorios para usuario admin com teste validavel e sem alterar filtros existentes",
        ])
        local_payload = json.loads(local.stdout)
        spec_dir = Path(local_payload["spec_dir"])
        run([sys.executable, str(VALIDATE), str(spec_dir)])
        prd_text = (spec_dir / "PRD.md").read_text(encoding="utf-8")
        if "## Story de Usuario" not in prd_text or "## Story Tecnica" not in prd_text:
            raise AssertionError("generated PRD missing required story sections")
        status_payload = json.loads((spec_dir / "status.json").read_text(encoding="utf-8"))
        if status_payload["decision"]["prd_status"] != "complete":
            raise AssertionError(f"expected complete PRD decision, got {status_payload['decision']}")
        warlog = run([
            sys.executable,
            str(WARLOG),
            str(spec_dir),
            "--event",
            "Forward test created WARLOG evidence.",
            "--phase",
            "plan",
            "--phase-state",
            "complete",
        ])
        warlog_payload = json.loads(warlog.stdout)
        if not Path(warlog_payload["warlog"]).exists():
            raise AssertionError("warlog script did not create WARLOG.md")
        run([sys.executable, str(VALIDATE), str(spec_dir), "--mermaid"])

        issue_body = root / "issue-body.md"
        run([
            sys.executable,
            str(TASKGEN),
            "--mode",
            "issue",
            "--output",
            str(issue_body),
            "--title",
            "Ideia de onboarding",
            "ideia solta para melhorar onboarding depois",
        ])
        if not issue_body.read_text(encoding="utf-8").startswith("<!-- superflow:issue v1 -->"):
            raise AssertionError("issue body missing superflow header")

        promoted = run([
            sys.executable,
            str(TASKGEN),
            "--root",
            str(root),
            "--from-file",
            str(issue_body),
            "--promote-issue",
            "123",
            "--json",
        ])
        promoted_payload = json.loads(promoted.stdout)
        run([sys.executable, str(VALIDATE), promoted_payload["spec_dir"]])

        dry = run([
            sys.executable,
            str(GITHUB),
            "create",
            "--dry-run",
            "--title",
            "Ideia de onboarding",
            "--label",
            "sf:inbox",
            "ideia solta para melhorar onboarding",
        ])
        if "gh issue create" not in dry.stdout or "sf:inbox" not in dry.stdout:
            raise AssertionError("github dry-run output missing expected command")

        link = run([
            sys.executable,
            str(GITHUB),
            "link",
            "123",
            "--body-file",
            str(issue_body),
            "--local-package",
            "specs/001-promoted",
            "--dry-run",
        ])
        if "gh issue edit 123" not in link.stdout or "Local package: specs/001-promoted" not in link.stdout:
            raise AssertionError("github link dry-run missing expected local package update")

        status = run(["git", "status", "--short"], cwd=root).stdout
        if "specs/" not in status or "issue-body.md" not in status:
            raise AssertionError(f"forward repo did not receive expected artifacts:\n{status}")

    print("OK: superflow forward test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
