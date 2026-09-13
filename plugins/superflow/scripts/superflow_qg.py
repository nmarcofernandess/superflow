#!/usr/bin/env python3
"""Render the immutable ``superflow.feed.v2`` snapshot as offline QG HTML.

This module deliberately has no command-line interface and no knowledge of the
spec discovery model. ``superflow.py qg`` owns reading/writing and passes the
already validated feed here. Keeping this boundary small makes an old HTML
snapshot safe to keep when generating a new one fails.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlparse


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = SCRIPT_DIR.parent / "assets" / "qg.html"
SNAPSHOT_TOKEN = "__QG_SNAPSHOT__"
LINKS_TOKEN = "__QG_LINKS__"


def script_safe_dumps(value: Any) -> str:
    """Serialize JSON without allowing data to terminate its script element."""

    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
    except ValueError:
        return False
    return True


def _existing_file_url(candidate: Path) -> Optional[str]:
    """Return a file URI only when the explicit local target exists."""

    try:
        resolved = candidate.expanduser().resolve()
    except OSError:
        return None
    if not resolved.exists():
        return None
    return resolved.as_uri()


def _relative_file_url(candidate: Path, root: Path) -> Optional[str]:
    """Resolve a relative reference without letting it leave the project root."""

    try:
        resolved = candidate.resolve()
        allowed_root = root.expanduser().resolve()
    except OSError:
        return None
    if not _is_within(resolved, allowed_root):
        return None
    return _existing_file_url(resolved)


def safe_link(value: Any, root: Path) -> Optional[str]:
    """Return a deliberately small allowlist of clickable URL targets.

    The original text is always rendered as text by the browser. This only
    determines whether it may also become an ``href``.
    """

    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    parsed = urlparse(raw)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return raw
    if parsed.scheme == "file":
        explicit_file = re.match(r"^file://(?:localhost)?/", raw, re.IGNORECASE)
        target = Path(unquote(parsed.path))
        if not explicit_file or parsed.netloc not in {"", "localhost"} or not target.is_absolute():
            return None
        return _existing_file_url(target)
    if parsed.scheme:
        return None
    candidate = Path(raw)
    if candidate.is_absolute() or raw.startswith("~"):
        return None
    return _relative_file_url(root / candidate, root)


def _link_data(feed: Dict[str, Any], root: Path) -> Dict[str, List[Any]]:
    records = feed.get("records")
    if not isinstance(records, list):
        return {"record_paths": [], "evidence": [], "task_evidence": []}
    record_paths: List[Optional[str]] = []
    evidence_links: List[List[Optional[str]]] = []
    task_evidence_links: List[List[List[Optional[str]]]] = []
    for record in records:
        if not isinstance(record, dict):
            record_paths.append(None)
            evidence_links.append([])
            task_evidence_links.append([])
            continue
        record_paths.append(safe_link(record.get("path"), root))
        evidence = record.get("evidence")
        if not isinstance(evidence, list):
            evidence_links.append([])
        else:
            evidence_links.append([safe_link(item, root) for item in evidence])
        tasks = record.get("tasks")
        if not isinstance(tasks, list):
            task_evidence_links.append([])
        else:
            task_evidence_links.append([
                [safe_link(item, root) for item in task.get("evidence", [])]
                if isinstance(task, dict) and isinstance(task.get("evidence"), list) else []
                for task in tasks
            ])
    return {
        "record_paths": record_paths,
        "evidence": evidence_links,
        "task_evidence": task_evidence_links,
    }


def _read_template() -> str:
    try:
        template = TEMPLATE.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError("assets/qg.html não pôde ser lido") from exc
    if template.count(SNAPSHOT_TOKEN) != 1 or template.count(LINKS_TOKEN) != 1:
        raise RuntimeError("assets/qg.html precisa conter os dois marcadores do renderer uma vez")
    return template


def render(feed: dict, root: Path) -> str:
    """Return a complete, self-contained QG page for one feed photograph.

    ``feed`` is intentionally embedded unchanged. A separate inert JSON block
    carries only pre-authorized link targets derived from ``root``; visual code
    never reads files, calls the CLI, or reinterprets status documents.
    """

    if not isinstance(feed, dict):
        raise TypeError("feed precisa ser um objeto")
    if not isinstance(root, Path):
        root = Path(root)
    template = _read_template()
    snapshot = script_safe_dumps(feed)
    links = script_safe_dumps(_link_data(feed, root))
    return template.replace(SNAPSHOT_TOKEN, snapshot).replace(LINKS_TOKEN, links)
