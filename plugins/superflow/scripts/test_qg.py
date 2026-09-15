#!/usr/bin/env python3
import copy
import json
import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from superflow_qg import render, render_embed


class QGTests(unittest.TestCase):
    def record(self, identifier, **changes):
        value = {
            "id": identifier,
            "title": "Spec " + identifier,
            "status": "pending",
            "path": "specs/" + identifier,
            "summary": "Uma descrição permanente da entrega.",
            "relations": [],
            "body_md": "",
            "parent_id": None,
        }
        value.update(changes)
        return value

    def feed(self, records, diagnostics=None):
        return {
            "schema_version": "superflow.feed.v4",
            "generated_at": "2026-09-13T12:00:00Z",
            "snapshot_id": "fixture",
            "source_revision": None,
            "records": records,
            "diagnostics": diagnostics or [],
        }

    def embedded(self, page):
        match = re.search(r'<script type="application/json" id="qg-snapshot">(.*?)</script>', page, re.S)
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def test_renderer_preserves_snapshot_without_private_surfaces(self):
        source = self.feed([self.record("one", body_md="# Retrato\nCompleto")])
        before = copy.deepcopy(source)
        page = render(source)
        self.assertEqual(self.embedded(page), before)
        self.assertNotIn("qg-links", page)
        for forbidden in ('id="tasks"', 'id="files"', "task_evidence", "record_paths"):
            self.assertNotIn(forbidden, page)

    def test_html_has_minimal_views_hierarchy_and_drawer(self):
        page = render(self.feed([]))
        for required in (
            'data-view="open"', 'data-view="done"', 'id="drawer"',
            'box.className="children"', 'class="spec-card"', 'id="search"',
            'return self||(children.get(r.id)||[]).some(matches)',
            'filter(ownHit?familyInView:matches)',
            "Nenhuma spec nesta visão.",
        ):
            self.assertIn(required, page)

    def test_summary_and_relations_survive_projection(self):
        records = [self.record("one", summary="Tema sem estado de execução.",
                               relations=[{"id": "two", "reason": "Contexto compartilhado"}]),
                   self.record("two", status="done")]
        actual = self.embedded(render(self.feed(records)))["records"]
        self.assertEqual(actual, records)
        self.assertEqual(actual[1]["relations"], [])

    def test_hostile_content_stays_inside_inert_json(self):
        hostile = '</script><img src=x onerror="alert(1)">'
        page = render(self.feed([self.record("bad", title=hostile, summary=hostile, relations=[{"id": "other", "reason": hostile}], body_md=hostile)]))
        self.assertNotIn(hostile, page)
        self.assertIn("\\u003c/script\\u003e", page)

    def test_parent_child_and_thousand_records_are_embedded(self):
        records = [self.record("base", status="done")]
        records.append(self.record("child", path="specs/base/minispecs/child", parent_id="base"))
        records.extend(self.record("item-%04d" % index) for index in range(998))
        page = render(self.feed(records))
        self.assertEqual(len(self.embedded(page)["records"]), 1000)
        self.assertIn("mini-label", page)

    def test_embed_is_isolated_and_preserves_host_navigation(self):
        fragment = render_embed(self.feed([self.record("one", body_md="</script><img>")]))
        self.assertIn('attachShadow({mode:"open"})', fragment)
        self.assertIn('})(shadow,false);', fragment)
        self.assertNotIn('<iframe', fragment)
        self.assertNotIn('</script><img>', fragment)
        self.assertEqual(fragment.count('</script>'), 1)

    def test_renderer_has_no_filesystem_or_network_behavior(self):
        source = Path(__file__).with_name("superflow_qg.py").read_text(encoding="utf-8")
        template = Path(__file__).parents[1] / "assets/qg.html"
        html = template.read_text(encoding="utf-8")
        for forbidden in ("subprocess", "urlparse", "safe_link", "read_sources"):
            self.assertNotIn(forbidden, source)
        for forbidden in ("fetch(", "XMLHttpRequest", "fonts.googleapis.com", "localStorage", "sessionStorage"):
            self.assertNotIn(forbidden, html)


if __name__ == "__main__":
    unittest.main()
