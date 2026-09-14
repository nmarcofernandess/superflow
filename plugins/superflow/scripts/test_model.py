#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from superflow_model import (
    ContentError, SourceError, build_snapshot, ensure_unchanged, has_errors,
    parse_status, read_sources, validate_plan, validate_ready,
)


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def spec(self, name="one", body="", **fields):
        directory = self.root / "specs" / name
        directory.mkdir(parents=True, exist_ok=True)
        data = {"id": name.replace("/", "-"), "title": name, "status": "pending"}
        data.update(fields)
        (directory / "status.md").write_text(
            "---\n" + json.dumps(data) + "\n---\n" + body, encoding="utf-8"
        )
        return directory

    def snapshot(self):
        return build_snapshot(self.root)[0]

    def test_minimum_and_free_body(self):
        self.spec(body="# Qualquer título\n\nTexto real.")
        snapshot = self.snapshot()
        self.assertFalse(has_errors(snapshot))
        self.assertIn("Qualquer título", snapshot["records"][0]["body_md"])

    def test_only_binary_status_and_known_fields(self):
        for value in ("in_progress", "paused", "cancelled", "execute", "qa"):
            self.spec(status=value)
            self.assertTrue(has_errors(self.snapshot()), value)
        self.spec(state="pending")
        self.assertTrue(has_errors(self.snapshot()))

    def test_yaml_extensions_and_duplicate_keys_are_rejected(self):
        for text in ("id: a\nid: b", "id: &x a\ntitle: *x", "id: !!str a"):
            with self.subTest(text=text), self.assertRaises(ContentError):
                parse_status("---\n" + text + "\n---\n")

    def test_dependency_requires_id_and_reason(self):
        self.spec(depends_on=["other"])
        self.assertTrue(has_errors(self.snapshot()))
        self.spec(depends_on=[{"id": "other", "reason": "Contrato necessário"}])
        self.spec("other")
        self.assertFalse(has_errors(self.snapshot()))

    def test_waiting_is_not_dependency(self):
        self.spec(waiting_for="Marco responder")
        record = self.snapshot()["records"][0]
        self.assertEqual(record["waiting_for"], "Marco responder")
        self.assertEqual(record["depends_on"], [])

    def test_done_cannot_wait_or_depend_on_pending(self):
        self.spec(status="done", waiting_for="Resposta")
        self.assertTrue(has_errors(self.snapshot()))
        self.spec(status="done", depends_on=[{"id": "other", "reason": "Precisa"}])
        self.spec("other")
        self.assertTrue(has_errors(self.snapshot()))

    def test_done_parent_with_pending_minispec(self):
        self.spec("base", status="done")
        self.spec("base/minispecs/extra")
        snapshot = self.snapshot()
        self.assertFalse(has_errors(snapshot))
        child = next(r for r in snapshot["records"] if r["id"] != "base")
        self.assertEqual(child["parent_id"], "base")

    def test_projection_reads_only_status(self):
        directory = self.spec()
        for name in ("PRD.md", "SPEC.md", "plan.json", "progress.md", "HANDBOOK.md"):
            (directory / name).write_text("SECRET_" + name, encoding="utf-8")
        sources = read_sources(self.root)
        self.assertEqual(
            sorted(Path(path).name for path in sources if path != ".superflow/config.json"),
            ["status.md"],
        )
        encoded = json.dumps(self.snapshot())
        self.assertNotIn("SECRET_", encoded)

    def test_source_change_prevents_publication(self):
        directory = self.spec()
        sources = read_sources(self.root)
        (directory / "status.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(SourceError, "SOURCE_CHANGED"):
            ensure_unchanged(self.root, sources)

    def test_plan_contract(self):
        task = {"id": "T01", "task": "Fazer", "status": "pending",
                "depends_on": [], "acceptance": ["Funciona"]}
        self.assertEqual(validate_plan({"tasks": [task]})[0]["id"], "T01")
        for change in ({"status": "in_progress"}, {"evidence": []}):
            invalid = dict(task)
            invalid.update(change)
            with self.assertRaises(ContentError):
                validate_plan({"tasks": [invalid]})

    def test_ready_boundary_requires_four_files(self):
        directory = self.spec()
        (directory / "PRD.md").write_text("# Promessa", encoding="utf-8")
        with self.assertRaisesRegex(ContentError, "SPEC.md"):
            validate_ready(self.root, "one")
        (directory / "SPEC.md").write_text("# Arquitetura", encoding="utf-8")
        (directory / "plan.json").write_text(json.dumps({"tasks": []}), encoding="utf-8")
        self.assertEqual(validate_ready(self.root, "one"), directory.resolve())


if __name__ == "__main__":
    unittest.main()
