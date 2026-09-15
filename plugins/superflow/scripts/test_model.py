#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from superflow_model import (
    ContentError, SourceError, build_snapshot, ensure_unchanged,
    parse_status, read_sources, validate_plan, validate_spec,
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
        data = {"id": name.replace("/", "-"), "title": name, "summary": "Descrição permanente da entrega", "status": "pending"}
        data.update(fields)
        (directory / "status.md").write_text(
            "---\n" + json.dumps(data) + "\n---\n" + body, encoding="utf-8"
        )
        return directory

    def snapshot(self):
        return build_snapshot(self.root)[0]

    def assert_has_diagnostics(self, snapshot):
        self.assertTrue(snapshot["diagnostics"])
        self.assertTrue(all(item["severity"] == "warning" for item in snapshot["diagnostics"]))

    def test_minimum_and_free_body(self):
        self.spec(body="# Qualquer título\n\nTexto real.")
        snapshot = self.snapshot()
        self.assertFalse(snapshot["diagnostics"])
        self.assertIn("Qualquer título", snapshot["records"][0]["body_md"])

    def test_only_binary_status_and_known_fields(self):
        for value in ("in_progress", "paused", "cancelled", "execute", "qa"):
            self.spec(status=value)
            self.assert_has_diagnostics(self.snapshot())
        self.spec(state="pending")
        self.assert_has_diagnostics(self.snapshot())

    def test_yaml_extensions_and_duplicate_keys_are_rejected(self):
        for text in ("id: a\nid: b", "id: &x a\ntitle: *x", "id: !!str a"):
            with self.subTest(text=text), self.assertRaises(ContentError):
                parse_status("---\n" + text + "\n---\n")

    def test_relations_require_id_reason_and_existing_target(self):
        for relations in (["other"], [{"id": "other", "reason": ""}],
                          [{"id": "one", "reason": "Self"}],
                          [{"id": "missing", "reason": "Context"}]):
            self.spec(relations=relations)
            self.assert_has_diagnostics(self.snapshot())
        self.spec(relations=[{"id": "other", "reason": "Contrato relacionado"}])
        self.spec("other")
        self.assertFalse(self.snapshot()["diagnostics"])

    def test_relations_allow_cycles_and_done_to_pending(self):
        self.spec(status="done", relations=[{"id": "other", "reason": "Contexto"}])
        self.spec("other", relations=[{"id": "one", "reason": "História"}])
        snapshot = self.snapshot()
        self.assertFalse(snapshot["diagnostics"])
        self.assertEqual(snapshot["schema_version"], "superflow.feed.v4")
        self.assertNotIn("blockers", snapshot["records"][0])

    def test_summary_is_required_and_nonempty(self):
        for value in (None, "", "  ", []):
            self.spec(summary=value)
            self.assert_has_diagnostics(self.snapshot())

    def test_duplicate_relations_rejected(self):
        self.spec("other")
        self.spec(relations=[{"id": "other", "reason": "A"}, {"id": "other", "reason": "B"}])
        self.assert_has_diagnostics(self.snapshot())

    def test_done_parent_with_pending_minispec(self):
        self.spec("base", status="done")
        self.spec("base/minispecs/extra")
        snapshot = self.snapshot()
        self.assertFalse(snapshot["diagnostics"])
        child = next(r for r in snapshot["records"] if r["id"] != "base")
        self.assertEqual(child["parent_id"], "base")

    def test_projection_reads_only_status(self):
        directory = self.spec()
        for name in ("PRD.md", "SPEC.md", "plan.json", "progress.md", "private-notes.md"):
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

    def test_spec_validates_conditional_artifacts_independently(self):
        directory = self.spec()
        with self.assertRaisesRegex(ContentError, "PRD.md"):
            validate_spec(self.root, "one")
        (directory / "PRD.md").write_text("# Promessa", encoding="utf-8")
        self.assertEqual(validate_spec(self.root, "one"), directory.resolve())
        (directory / "plan.json").write_text(json.dumps({"tasks": []}), encoding="utf-8")
        self.assertEqual(validate_spec(self.root, "one"), directory.resolve())
        (directory / "plan.json").write_text("invalid", encoding="utf-8")
        with self.assertRaises(ContentError):
            validate_spec(self.root, "one")
        (directory / "plan.json").unlink()
        (directory / "SPEC.md").write_text("# Arquitetura", encoding="utf-8")
        self.assertEqual(validate_spec(self.root, "one"), directory.resolve())
        (directory / "SPEC.md").write_text("", encoding="utf-8")
        with self.assertRaises(ContentError):
            validate_spec(self.root, "one")

    def test_spec_checks_relation_targets(self):
        directory = self.spec(relations=[{"id": "missing", "reason": "Contexto"}])
        (directory / "PRD.md").write_text("# Promessa", encoding="utf-8")
        with self.assertRaisesRegex(ContentError, "Destino"):
            validate_spec(self.root, "one")

    def test_spec_rejects_ambiguous_relation_target(self):
        directory = self.spec(relations=[{"id": "other", "reason": "Contexto"}])
        (directory / "PRD.md").write_text("# Promessa", encoding="utf-8")
        self.spec("first", id="other")
        self.spec("second", id="other")
        with self.assertRaisesRegex(ContentError, "ambíguo"):
            validate_spec(self.root, "one")

    def test_spec_counts_known_id_from_editorially_invalid_status(self):
        directory = self.spec()
        (directory / "PRD.md").write_text("# Promessa", encoding="utf-8")
        self.spec("other", id="one", summary=None)
        with self.assertRaisesRegex(ContentError, "ID repetido"):
            validate_spec(self.root, "one")

    def test_source_removal_and_path_rename_update_snapshot(self):
        directory = self.spec()
        self.spec("other", relations=[{"id": "one", "reason": "Contexto"}])
        directory.rename(directory.with_name("renamed"))
        snapshot = self.snapshot()
        self.assertFalse(snapshot["diagnostics"])
        record = next(r for r in snapshot["records"] if r["id"] == "one")
        self.assertEqual(record["path"], "specs/renamed")
        (directory.with_name("renamed") / "status.md").unlink()
        snapshot = self.snapshot()
        self.assertEqual(len(snapshot["records"]), 1)
        self.assertEqual(snapshot["diagnostics"][0]["code"], "INVALID_RELATION")

    def test_task_cycles_still_rejected(self):
        tasks = [{"id": name, "task": name, "status": "pending",
                  "depends_on": [other], "acceptance": ["Works"]}
                 for name, other in (("a", "b"), ("b", "a"))]
        with self.assertRaisesRegex(ContentError, "Ciclo"):
            validate_plan({"tasks": tasks})


if __name__ == "__main__":
    unittest.main()
