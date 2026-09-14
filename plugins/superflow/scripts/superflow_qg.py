"""Render a validated status-only snapshot as one self-contained QG HTML."""
from __future__ import annotations

import json
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "qg.html"
SNAPSHOT_TOKEN = "__QG_SNAPSHOT__"


def script_safe_dumps(value):
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render(feed, root=None):
    if not isinstance(feed, dict):
        raise TypeError("feed precisa ser um objeto")
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(SNAPSHOT_TOKEN) != 1:
        raise RuntimeError("assets/qg.html precisa conter o marcador do snapshot uma vez")
    return template.replace(SNAPSHOT_TOKEN, script_safe_dumps(feed))
