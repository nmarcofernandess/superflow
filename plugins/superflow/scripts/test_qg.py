#!/usr/bin/env python3
import copy
import json
import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from superflow_qg import render, render_embed, component_script, refresh_html


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
        match = re.search(r'<script type="application/json" data-superflow-snapshot>(.*?)</script>', page, re.S)
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def test_refresh_preserves_host_scopes_and_other_sources(self):
        feed = self.feed([self.record("one")])
        host = '<header>Host</header>' + render_embed(feed, source="https://example.org/feed.json")
        host = host.replace('<superflow-qg src=', "<superflow-qg ids='[\"one\", \"missing\"]' src=")
        host += '<superflow-qg src="/other/feed.json"></superflow-qg><footer>End</footer>'
        updated = refresh_html(host, feed, "https://example.org/feed.json")
        self.assertTrue(updated.startswith('<header>Host</header>'))
        self.assertTrue(updated.endswith('<superflow-qg src="/other/feed.json"></superflow-qg><footer>End</footer>'))
        self.assertIn('ids="[&quot;one&quot;, &quot;missing&quot;]"', updated)
        self.assertEqual(self.embedded(updated), feed)
        self.assertEqual(refresh_html(updated, feed, "https://example.org/feed.json"), updated)

    def test_online_page_is_portable_and_contains_snapshot_and_runtime(self):
        feed = self.feed([self.record("one")])
        page = render(feed, source="https://example.org/specs/feed.json")
        self.assertIn('src="https://example.org/specs/feed.json"', page)
        self.assertNotIn('src="https://example.org/specs/qg.js"', page)
        self.assertEqual(self.embedded(page), feed)
        self.assertIn('customElements.define', page)

    def test_renderer_preserves_snapshot_without_private_surfaces(self):
        source = self.feed([self.record("one", body_md="# Retrato\nCompleto")])
        before = copy.deepcopy(source)
        page = render(source)
        self.assertEqual(self.embedded(page), before)
        self.assertNotIn("qg-links", page)
        for forbidden in ('id="tasks"', 'id="files"', "task_evidence", "record_paths"):
            self.assertNotIn(forbidden, page)

    def test_html_has_minimal_views_hierarchy_and_drawer(self):
        page = (Path(__file__).parents[1] / "assets/qg.html").read_text()
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
        self.assertIn('attachShadow({mode: "open"})', fragment)
        self.assertIn('<superflow-qg>', fragment)
        self.assertNotIn('sync-hash', fragment.split('</superflow-qg>')[0])
        self.assertNotIn('<iframe', fragment)
        self.assertNotIn('</script><img>', fragment)
        self.assertEqual(fragment.count('</script>'), 2)

    def test_template_renders_data_while_component_owns_feed_loading(self):
        source = Path(__file__).with_name("superflow_qg.py").read_text(encoding="utf-8")
        template = Path(__file__).parents[1] / "assets/qg.html"
        html = template.read_text(encoding="utf-8")
        for forbidden in ("subprocess", "urlparse", "safe_link", "read_sources"):
            self.assertNotIn(forbidden, source)
        for forbidden in ("fetch(", "XMLHttpRequest", "fonts.googleapis.com", "localStorage", "sessionStorage"):
            self.assertNotIn(forbidden, html)
        self.assertIn("fetch(url", component_script())


if __name__ == "__main__":
    unittest.main()
