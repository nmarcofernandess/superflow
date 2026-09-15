"""Render a validated status-only snapshot as one self-contained QG HTML."""
from __future__ import annotations

import json
import re
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


def render_embed(feed):
    """Return a self-contained fragment isolated from its host by Shadow DOM.

    Paste the fragment into the destination HTML before loading it. It owns no
    URL state, so opening a drawer preserves the host's tab or anchor.
    """
    page = render(feed)
    css = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
    body = re.search(r"<body>(.*?)</body>", page, re.S).group(1)
    markup, script = body.rsplit("<script>", 1)
    script = script.rsplit("</script>", 1)[0].strip()
    css = css.replace(":root{", ":host{").replace("html,body{", ".qg-root{")
    content = "<style>:host{display:block;all:initial}" + css + "</style><div class=\"qg-root\">" + markup + "</div>"
    script = script.removesuffix("})();") + "})(shadow,false);"
    return ('<div data-superflow-qg></div>\n<script>\n{\n'
            'const shadow=document.currentScript.previousElementSibling.attachShadow({mode:"open"});\n'
            'shadow.innerHTML=' + script_safe_dumps(content) + ';\n' + script + '\n}\n</script>\n')
