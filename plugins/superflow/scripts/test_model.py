#!/usr/bin/env python3
"""Behavioral tests for source validation and relationship semantics."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from superflow_model import (ContentError, SourceError, build_snapshot, ensure_unchanged,
                             find_cycles, has_errors, parse_status, reference_path)


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def spec(self, name="one", **fields):
        directory = self.root / "specs" / name
        directory.mkdir(parents=True, exist_ok=True)
        value = {"id": name.replace("/", "-"), "title": name, "phase": "inbox",
                 "state": "pending", "prd": "gathering", "updated_at": "2026-09-13T12:00:00Z"}
        value.update(fields)
        if value["phase"] in {"done", "cancelled"}:
            value.pop("state", None)
        (directory / "status.md").write_text("---\n" + json.dumps(value) + "\n---\n")
        return directory

    def ready(self, name="one", **fields):
        p = self.spec(name, prd="ready", **fields)
        (p / "PRD.md").write_text("# Problem\nImport expenses.\n# Acceptance\nAC01: import a row.")
        return p

    def snapshot(self):
        return build_snapshot(self.root)[0]

    def test_ticket_without_body_or_prd(self):
        self.spec()
        snap = self.snapshot()
        self.assertFalse(has_errors(snap))
        self.assertEqual(len(snap["records"]), 1)
        self.assertEqual(snap["records"][0]["body_md"], "")

    def test_ready_requires_prd(self):
        self.spec(prd="ready")
        self.assertTrue(has_errors(self.snapshot()))

    def test_invalid_yaml_is_diagnostic_not_hidden(self):
        p = self.spec()
        (p / "status.md").write_text("---\nid: [bad\n---\n")
        snap = self.snapshot()
        self.assertEqual(snap["records"], [])
        self.assertEqual(snap["diagnostics"][0]["path"], "specs/one/status.md")

    def test_duplicate_keys_and_yaml_extensions(self):
        for text in ["id: first\nid: second", "id: &x first\ntitle: *x",
                     "id: !!str first", "id: first\n<<: {title: other}"]:
            with self.subTest(text=text), self.assertRaises((ContentError, ValueError)):
                parse_status("---\n" + text + "\n---\n")

    def test_wrong_types_are_content_errors(self):
        for field, value in [("state", []), ("archived", "false"), ("depends_on", "x"),
                             ("prd", False), ("updated_at", "2026-09-13"),
                             ("title", ""), ("surprise", "field")]:
            with self.subTest(field=field):
                self.spec(**{field: value})
                self.assertTrue(has_errors(self.snapshot()))

    def test_duplicate_id(self):
        self.spec("a", id="same")
        self.spec("b", id="same")
        self.assertIn("DUPLICATE_ID", [d["code"] for d in self.snapshot()["diagnostics"]])

    def test_done_parent_with_open_complement(self):
        self.ready("base", phase="done", evidence=["https://example.org/pr/1"])
        self.ready("base/minispecs/extra", depends_on=["base"])
        snap = self.snapshot()
        self.assertFalse(has_errors(snap))
        child = next(r for r in snap["records"] if r["id"] != "base")
        self.assertEqual(child["parent_id"], "base")
        self.assertEqual(child["blockers"], [])

    def test_archived_done_dependency_satisfies(self):
        self.ready("a", phase="done", archived=True, evidence=["https://example.org/1"])
        self.ready("b", phase="done", depends_on=["a"], evidence=["https://example.org/2"])
        self.assertFalse(has_errors(self.snapshot()))

    def test_cancelled_does_not_satisfy_delivery(self):
        self.spec("a", phase="cancelled", evidence=["https://example.org/decision"])
        self.ready("b", phase="done", depends_on=["a"], evidence=["https://example.org/2"])
        self.assertTrue(has_errors(self.snapshot()))

    def test_mixed_cycle_and_missing_targets(self):
        self.spec("a", absorbed_by="b")
        self.spec("b", depends_on=["a"])
        self.assertIn("RELATION_CYCLE", [d["code"] for d in self.snapshot()["diagnostics"]])
        self.spec("b", depends_on=["missing"])
        self.assertIn("INVALID_RELATION", [d["code"] for d in self.snapshot()["diagnostics"]])

    def test_absorber_done_does_not_close_source(self):
        self.spec("a", absorbed_by="b")
        self.ready("b", phase="done", evidence=["https://example.org/1"])
        snap = self.snapshot()
        self.assertFalse(has_errors(snap))
        self.assertEqual(next(r for r in snap["records"] if r["id"] == "a")["phase"], "inbox")

    def test_invalid_active_wait_and_archive(self):
        for extra in [{"waiting_for": "Human QA"}, {"archived": True}, {"absorbed_by": "b"}]:
            self.spec("b")
            self.spec("a", state="in_progress", **extra)
            self.assertTrue(has_errors(self.snapshot()))

    def test_local_evidence_and_safe_urls(self):
        self.ready(phase="done", evidence=["missing.txt"])
        self.assertTrue(has_errors(self.snapshot()))
        (self.root / "missing.txt").write_text("Real fixture evidence")
        self.assertFalse(has_errors(self.snapshot()))
        for ref in [
            "javascript:alert(1)", "data:text/html,x", "../outside", "/etc/passwd",
            "file:../../../../etc/passwd", "file:/etc/passwd", "file://example.test/etc/passwd",
        ]:
            with self.subTest(ref=ref), self.assertRaises(ContentError):
                reference_path(self.root, ref)
        with tempfile.NamedTemporaryFile(prefix="superflow-file-uri-proof.", delete=False) as stream:
            stream.write(b"proof")
            external = Path(stream.name)
        try:
            self.assertEqual(reference_path(self.root, external.as_uri()), external)
            self.assertEqual(reference_path(self.root, "file://localhost" + external.as_posix()), external)
        finally:
            external.unlink()

    def test_source_change_prevents_publication(self):
        self.spec()
        _, sources = build_snapshot(self.root)
        self.spec("new")
        with self.assertRaisesRegex(SourceError, "SOURCE_CHANGED"):
            ensure_unchanged(self.root, sources)

    def test_symlink_source_rejected(self):
        p = self.spec()
        (p / "status.md").unlink()
        (self.root / "outside.md").write_text("external")
        (p / "status.md").symlink_to(self.root / "outside.md")
        with self.assertRaises(SourceError):
            self.snapshot()

    def test_config_outside_root(self):
        p = self.root / ".superflow"
        p.mkdir()
        (p / "config.json").write_text('{"specs_root":"../outside"}')
        with self.assertRaises(SourceError):
            self.snapshot()

    def test_documents_without_registry_are_visible_candidates(self):
        p = self.root / "specs" / "report"
        p.mkdir(parents=True)
        (p / "SPEC.md").write_text("# Historical report")
        snap = self.snapshot()
        self.assertEqual(snap["records"], [])
        self.assertEqual(snap["diagnostics"][0]["code"], "UNREGISTERED_DOCUMENTS")
        self.assertEqual(snap["diagnostics"][0]["severity"], "warning")

    def test_large_graph_without_recursive_stack(self):
        graph = {str(i): [str(i + 1)] for i in range(1500)}
        self.assertEqual(find_cycles(graph), [])
        graph["1499"] = ["0"]
        self.assertEqual(len(find_cycles(graph)), 1)

    def task(self, **fields):
        return dict({"id": "t1", "behavior": "Import a row", "files": ["import.py"],
                     "depends_on": [], "acceptance": ["AC01"], "status": "pending",
                     "evidence": []}, **fields)

    def plan(self, tasks, **fields):
        p = self.ready(phase="execute", **fields)
        (p / "plan.json").write_text(json.dumps({"tasks": tasks}))

    def test_task_done_requires_evidence_and_acceptance(self):
        self.plan([self.task(status="done")])
        self.assertTrue(has_errors(self.snapshot()))
        self.plan([self.task(status="done", evidence=["https://example.org/1"])])
        self.assertFalse(has_errors(self.snapshot()))
        self.plan([self.task(acceptance=["NONEXISTENT"])])
        self.assertTrue(has_errors(self.snapshot()))

    def test_task_wrong_type_is_diagnostic(self):
        self.plan([self.task(status=[])])
        self.assertTrue(has_errors(self.snapshot()))

    def test_reopened_predecessor_invalidates_done_task(self):
        self.plan([self.task(), self.task(id="t2", depends_on=["t1"], status="done",
                                         evidence=["https://example.org/2"])])
        self.assertTrue(has_errors(self.snapshot()))

    def test_active_task_only_in_active_execution(self):
        self.plan([self.task(status="in_progress")])
        self.assertTrue(has_errors(self.snapshot()))
        self.plan([self.task(status="in_progress")], state="in_progress")
        self.assertFalse(has_errors(self.snapshot()))

    def test_skip_requires_reason_and_absorption_closes_open_tasks(self):
        self.spec("b")
        self.plan([self.task()], absorbed_by="b")
        self.assertTrue(has_errors(self.snapshot()))
        self.plan([self.task(status="skipped", skip_reason="Remaining scope assumed by b")], absorbed_by="b")
        self.assertFalse(has_errors(self.snapshot()))


if __name__ == "__main__":
    unittest.main()
