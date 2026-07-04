#!/usr/bin/env python3
"""Bridge Superflow PRD bodies with GitHub issues through the gh CLI."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TASKGEN = SCRIPT_DIR / "superflow_taskgen.py"


def require_gh() -> None:
    if not shutil.which("gh"):
        raise SystemExit("gh CLI not found. Install/auth gh or generate the body with superflow_taskgen.py.")


def run(cmd: list[str], *, check: bool = True, input_text: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


def read_description(args: argparse.Namespace) -> str:
    if getattr(args, "from_file", None) == "-":
        return sys.stdin.read()
    if getattr(args, "from_file", None):
        return Path(args.from_file).expanduser().read_text(encoding="utf-8")
    if getattr(args, "description", None):
        return args.description
    raise SystemExit("description is required unless --from-file is used")


def issue_body(description: str, title: str | None) -> str:
    cmd = [sys.executable, str(TASKGEN), "--mode", "issue"]
    if title:
        cmd.extend(["--title", title])
    cmd.append(description)
    return run(cmd).stdout


def create_issue(args: argparse.Namespace) -> int:
    body = issue_body(read_description(args), args.title)
    if args.body_output:
        Path(args.body_output).expanduser().write_text(body, encoding="utf-8")

    title = args.title or "Superflow inbox"
    cmd = ["gh", "issue", "create", "--title", title, "--body-file", "-"]
    for label in args.label or []:
        cmd.extend(["--label", label])
    if args.repo:
        cmd.extend(["--repo", args.repo])

    if args.dry_run:
        display_cmd = []
        previous = None
        for part in cmd:
            display_cmd.append("<stdin>" if previous == "--body-file" and part == "-" else part)
            previous = part
        print("DRY RUN:")
        print(" ".join(display_cmd))
        print()
        print(body)
        return 0

    require_gh()
    result = run(cmd, input_text=body)
    print(result.stdout, end="")
    return result.returncode


def fetch_issue(args: argparse.Namespace) -> int:
    require_gh()
    cmd = ["gh", "issue", "view", str(args.issue), "--json", "title,body,url"]
    if args.repo:
        cmd.extend(["--repo", args.repo])
    result = run(cmd)
    payload = json.loads(result.stdout)
    body = payload.get("body") or ""
    if args.output:
        Path(args.output).expanduser().write_text(body, encoding="utf-8")
    else:
        print(body)
    if args.json:
        print(json.dumps(payload, indent=2))
    return 0


def promote_issue(args: argparse.Namespace) -> int:
    require_gh()
    with tempfile.TemporaryDirectory(prefix="superflow-issue.") as tmp:
        body_path = Path(tmp) / f"issue-{args.issue}.md"
        fetch_args = argparse.Namespace(issue=args.issue, repo=args.repo, output=str(body_path), json=False)
        fetch_issue(fetch_args)
        cmd = [
            sys.executable,
            str(TASKGEN),
            "--root",
            args.root,
            "--from-file",
            str(body_path),
            "--promote-issue",
            str(args.issue),
        ]
        if args.title:
            cmd.extend(["--title", args.title])
        if args.json:
            cmd.append("--json")
        result = run(cmd)
        print(result.stdout, end="")
    return 0


def link_issue(args: argparse.Namespace) -> int:
    if args.body_file:
        body = Path(args.body_file).expanduser().read_text(encoding="utf-8")
    else:
        require_gh()
        cmd = ["gh", "issue", "view", str(args.issue), "--json", "body"]
        if args.repo:
            cmd.extend(["--repo", args.repo])
        payload = json.loads(run(cmd).stdout)
        body = payload.get("body") or ""

    if "Local package:" in body:
        lines = [
            f"Local package: {args.local_package}" if line.startswith("Local package:") else line
            for line in body.splitlines()
        ]
        updated = "\n".join(lines) + ("\n" if body.endswith("\n") else "")
    else:
        updated = f"Local package: {args.local_package}\n\n{body}"

    cmd = ["gh", "issue", "edit", str(args.issue), "--body-file", "-"]
    if args.repo:
        cmd.extend(["--repo", args.repo])

    if args.dry_run:
        display_cmd = []
        previous = None
        for part in cmd:
            display_cmd.append("<stdin>" if previous == "--body-file" and part == "-" else part)
            previous = part
        print("DRY RUN:")
        print(" ".join(display_cmd))
        print()
        print(updated)
        return 0

    require_gh()
    result = run(cmd, input_text=updated)
    print(result.stdout, end="")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a GitHub issue from a Superflow PRD body.")
    create.add_argument("description", nargs="?")
    create.add_argument("--from-file")
    create.add_argument("--title")
    create.add_argument("--repo")
    create.add_argument("--label", action="append")
    create.add_argument("--body-output")
    create.add_argument("--dry-run", action="store_true")
    create.set_defaults(func=create_issue)

    fetch = sub.add_parser("fetch", help="Fetch a GitHub issue body.")
    fetch.add_argument("issue")
    fetch.add_argument("--repo")
    fetch.add_argument("--output")
    fetch.add_argument("--json", action="store_true")
    fetch.set_defaults(func=fetch_issue)

    promote = sub.add_parser("promote", help="Promote a GitHub issue to a local PRD package.")
    promote.add_argument("issue")
    promote.add_argument("--repo")
    promote.add_argument("--root", default=".")
    promote.add_argument("--title")
    promote.add_argument("--json", action="store_true")
    promote.set_defaults(func=promote_issue)

    link = sub.add_parser("link", help="Update an issue body with the promoted local package path.")
    link.add_argument("issue")
    link.add_argument("--local-package", required=True)
    link.add_argument("--repo")
    link.add_argument("--body-file", help="Use a local issue body instead of fetching through gh.")
    link.add_argument("--dry-run", action="store_true")
    link.set_defaults(func=link_issue)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
