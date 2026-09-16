"""Publish one QG component for live feeds and self-contained exports."""
from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from superflow_model import SourceError

ASSETS = Path(__file__).resolve().parents[1] / "assets"
TEMPLATE = ASSETS / "qg.html"


def script_safe_dumps(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def component_script():
    page = TEMPLATE.read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
    body = re.search(r"<body>(.*?)</body>", page, re.S).group(1)
    markup, script = body.rsplit("<script>", 1)
    markup = re.sub(r'<script type="application/json" id="qg-snapshot">.*?</script>', "", markup, flags=re.S)
    script = script.rsplit("</script>", 1)[0].strip().removesuffix("();")
    css = css.replace(":root{", ":host{").replace("html,body{", ".qg-root{")
    markup = '<style>:host{display:block;all:initial}' + css + '</style><div class="qg-root">' + markup + '</div>'
    return (ASSETS / "qg-component.js").read_text(encoding="utf-8").replace(
        "__QG_MARKUP__", script_safe_dumps(markup)
    ).replace("__QG_RENDER__", script)


def snapshot_element(feed):
    return '<script type="application/json" data-superflow-snapshot>' + script_safe_dumps(feed) + '</script>'


def runtime_element():
    return '<script data-superflow-runtime>\n' + component_script() + '\n</script>'


def render_embed(feed, source=None, sync_hash=False):
    attributes = ' sync-hash' if sync_hash else ''
    if source is not None:
        attributes += ' src="' + html.escape(source, quote=True) + '"'
    return ('<superflow-qg' + attributes + '>' + snapshot_element(feed)
            + '</superflow-qg>\n' + runtime_element() + '\n')


def render(feed, root=None, source=None):
    return ('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Superflow QG</title><style>body{margin:0}</style></head><body>\n'
            + render_embed(feed, source, sync_hash=True) + '</body></html>\n')


class Slots(HTMLParser):
    """Locate only contract-owned elements; keep all host bytes outside them."""
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.lines = [0] + [match.end() for match in re.finditer("\n", text)]
        self.components, self.runtimes = [], []
        self.component = self.runtime = None
        self.feed(text)
        self.close()
        if self.component is not None or self.runtime is not None:
            raise SourceError("Elemento Superflow sem fechamento no HTML.")

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag == 'superflow-qg':
            if self.component is not None:
                raise SourceError("Componentes Superflow não podem ser aninhados.")
            self.component = (self.position(), attrs)
        elif tag == 'script' and 'data-superflow-runtime' in dict(attrs):
            if self.component is not None:
                raise SourceError("O runtime deve ficar fora do componente Superflow.")
            self.runtime = self.position()

    def handle_endtag(self, tag):
        end = self.text.find('>', self.position()) + 1
        if tag == 'superflow-qg' and self.component is not None:
            start, attrs = self.component
            self.components.append((start, end, attrs))
            self.component = None
        elif tag == 'script' and self.runtime is not None:
            self.runtimes.append((self.runtime, end))
            self.runtime = None


def refresh_html(text, feed, source=None):
    """Update portable snapshots, retaining source, scope and refresh settings."""
    slots = Slots(text)
    edits = []
    for start, end, attrs in slots.components:
        if source is not None and dict(attrs).get('src') != source:
            continue
        attrs = [(key, value) for key, value in attrs if key != 'data-snapshot-id']
        opening = '<superflow-qg' + ''.join(
            ' ' + key + ('="' + html.escape(value, quote=True) + '"' if value is not None else '')
            for key, value in attrs
        ) + '>'
        edits.append((start, end, opening + snapshot_element(feed) + '</superflow-qg>'))
    if not edits:
        raise SourceError("Nenhum componente corresponde à fonte indicada; use --source para componentes com src.")
    # One runtime serves every component on the page, including other online sources.
    for i, (start, end) in enumerate(slots.runtimes):
        edits.append((start, end, runtime_element() if i == 0 else ''))
    if not slots.runtimes:
        raise SourceError("HTML sem <script data-superflow-runtime>; use a receita de incorporação.")
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text
