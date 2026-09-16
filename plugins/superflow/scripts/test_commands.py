#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parent / "superflow.py"


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--root", str(self.root), *args],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

    def test_qg_publishes_one_feed_and_refreshes_hosts_without_reformatting(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas")
        first, second = self.root / "first.html", self.root / "second.html"
        self.assertEqual(self.run_cli("qg", "--output", str(first)).returncode, 0)
        self.assertTrue((self.root / ".superflow/qg.js").is_file())
        prefix = '<!-- Host \u2028 -->\r\n<header>Preservar</header>\r\n'
        content = first.read_text().replace('<body>', '<body>' + prefix)
        first.write_bytes(content.encode("utf-8"))
        second.write_bytes(content.encode("utf-8"))
        status = self.root / "specs/alpha/status.md"
        status.write_text(status.read_text().replace("title: Alpha", "title: Atualizado"))
        result = self.run_cli("qg", "--refresh", str(first), str(second))
        self.assertEqual(result.returncode, 0, result.stderr)
        feed = json.loads((self.root / ".superflow/feed.json").read_text())
        for output in (first, second):
            raw = output.read_bytes()
            self.assertIn(prefix.encode("utf-8"), raw)
            self.assertIn(feed["snapshot_id"].encode(), raw)
            self.assertIn(b'Atualizado', raw)

    def test_refresh_prepares_all_destinations_before_writing(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas")
        first, invalid = self.root / "first.html", self.root / "invalid.html"
        self.run_cli("qg", "--output", str(first))
        before = first.read_bytes()
        feed = (self.root / ".superflow/feed.json").read_bytes()
        invalid.write_text("<h1>Host sem componente</h1>")
        result = self.run_cli("qg", "--refresh", str(first), str(invalid))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(first.read_bytes(), before)
        self.assertEqual((self.root / ".superflow/feed.json").read_bytes(), feed)

    def test_refresh_uses_configured_outputs_relative_to_project(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas")
        first = self.root / "panels/one.html"
        second = self.root / "two.html"
        for destination in (first, second):
            self.assertEqual(self.run_cli("qg", "--online", "http://localhost:8000/feed.json", "--output", str(destination)).returncode, 0)
        (self.root / ".superflow/config.json").write_text(json.dumps({"specs_root":"specs", "qg_outputs":["panels/one.html", str(second)]}))
        self.assertEqual(self.run_cli("qg", "--refresh").returncode, 0)
        feed = json.loads((self.root / ".superflow/feed.json").read_text())
        for destination in (first, second):
            text = destination.read_text()
            self.assertIn(feed["snapshot_id"], text)
            self.assertIn('src="http://localhost:8000/feed.json"', text)
            self.assertNotIn('<superflow-qg offline', text)

    def test_refresh_skips_missing_outputs_and_preserves_config(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas")
        present = self.root / "present.html"
        self.run_cli("qg", "--output", str(present))
        config = self.root / ".superflow/config.json"
        config.write_text(json.dumps({"qg_outputs": ["missing.html", "present.html", "gone/panel.html"]}))
        before = config.read_bytes()
        result = self.run_cli("qg", "--refresh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("HTMLs atualizados: 1; destinos não encontrados: 2", result.stdout)
        for name in ("missing.html", "gone/panel.html"):
            self.assertIn(str(self.root / name) + ": OUTPUT_NOT_FOUND", result.stderr)
            self.assertFalse((self.root / name).exists())
        self.assertEqual(config.read_bytes(), before)
        feed = json.loads((self.root / ".superflow/feed.json").read_text())
        self.assertIn(feed["snapshot_id"], present.read_text())

    def test_refresh_all_missing_still_publishes_feed_with_explicit_zero(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas")
        missing = self.root / "missing.html"
        result = self.run_cli("qg", "--refresh", str(missing))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("HTMLs atualizados: 0; destinos não encontrados: 1", result.stdout)
        self.assertIn("OUTPUT_NOT_FOUND", result.stderr)
        self.assertFalse(missing.exists())
        feed = json.loads((self.root / ".superflow/feed.json").read_text())
        self.assertEqual(feed["records"][0]["id"], "alpha")
        self.assertTrue((self.root / ".superflow/qg.js").is_file())

    def test_refresh_existing_directory_is_an_operational_error(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas")
        directory = self.root / "panel.html"
        directory.mkdir()
        result = self.run_cli("qg", "--refresh", str(directory))
        self.assertEqual(result.returncode, 2)
        self.assertIn("operational_error:", result.stderr)
        self.assertNotIn("OUTPUT_NOT_FOUND", result.stderr)
        self.assertFalse((self.root / ".superflow/feed.json").exists())

    def test_new_creates_only_prd_and_status(self):
        result = self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas de uma planilha")
        self.assertEqual(result.returncode, 0, result.stderr)
        names = sorted(path.name for path in (self.root / "specs/alpha").iterdir())
        self.assertEqual(names, ["PRD.md", "status.md"])
        status = (self.root / "specs/alpha/status.md").read_text()
        self.assertIn("status: pending", status)
        self.assertNotIn("phase:", status)

    def test_new_requires_human_summary_before_writing(self):
        result = self.run_cli("new", "alpha", "--title", "Alpha")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "specs/alpha").exists())
        result = self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "  ")
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.root / "specs/alpha").exists())

    def test_feed_and_qg_never_copy_private_sources(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas de uma planilha")
        directory = self.root / "specs/alpha"
        for name in ("PRD.md", "SPEC.md", "plan.json", "progress.md", "private-notes.md"):
            (directory / name).write_text("SECRET_" + name, encoding="utf-8")
        feed = self.run_cli("feed")
        qg = self.run_cli("qg")
        self.assertEqual(feed.returncode, 0, feed.stderr)
        self.assertEqual(qg.returncode, 0, qg.stderr)
        self.assertNotIn("SECRET_", (self.root / ".superflow/feed.json").read_text())
        self.assertNotIn("SECRET_", (self.root / ".superflow/qg.html").read_text())

    def test_check_spec_accepts_optional_artifacts(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas de uma planilha")
        self.assertEqual(self.run_cli("check", "spec", "alpha").returncode, 0)
        directory = self.root / "specs/alpha"
        (directory / "SPEC.md").write_text("# Arquitetura", encoding="utf-8")
        (directory / "plan.json").write_text(json.dumps({"tasks": []}), encoding="utf-8")
        self.assertEqual(self.run_cli("check", "spec", "alpha").returncode, 0)
        self.assertEqual(self.run_cli("check", "status").returncode, 0)

    def test_invalid_status_is_advisory_for_check_feed_and_qg(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas de uma planilha")
        (self.root / "specs/alpha/status.md").write_text("---\nid: [bad\n---\n")
        status = self.run_cli("check", "status")
        feed = self.run_cli("feed")
        qg = self.run_cli("qg")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(feed.returncode, 0, feed.stderr)
        self.assertEqual(qg.returncode, 0, qg.stderr)
        self.assertIn("warning: specs/alpha/status.md: INVALID_STATUS", status.stderr)
        data = json.loads((self.root / ".superflow/feed.json").read_text())
        self.assertEqual(data["diagnostics"][0]["code"], "INVALID_STATUS")
        self.assertEqual(data["diagnostics"][0]["severity"], "warning")
        self.assertIn("INVALID_STATUS", (self.root / ".superflow/qg.html").read_text())

    def test_invalid_target_spec_is_advisory_without_validity_claim(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas de uma planilha")
        (self.root / "specs/alpha/PRD.md").unlink()
        result = self.run_cli("check", "spec", "alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("warning: alpha: INVALID_SPEC", result.stderr)
        self.assertIn("Spec com diagnóstico", result.stdout)
        self.assertNotIn("sem diagnósticos", result.stdout)

    def test_new_ignores_unrelated_diagnostics_but_preserves_collision_safety(self):
        broken = self.root / "specs/broken"
        broken.mkdir(parents=True)
        (broken / "status.md").write_text("---\nid: [bad\n---\n", encoding="utf-8")
        created = self.run_cli(
            "new", "alpha", "--title", "Alpha", "--summary", "Importar despesas de uma planilha"
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertIn("warning: specs/broken/status.md: INVALID_STATUS", created.stderr)
        self.assertIn("1 diagnóstico existente", created.stdout)
        duplicate_id = self.root / "specs/elsewhere"
        duplicate_id.mkdir()
        (duplicate_id / "status.md").write_text(
            "---\nid: known\ntitle: Known\nstatus: pending\n---\n",
            encoding="utf-8",
        )
        known = self.run_cli(
            "new", "known", "--title", "Known", "--summary", "Outro cadastro"
        )
        self.assertEqual(known.returncode, 1)
        self.assertIn("ID já cadastrado", known.stderr)
        occupied = self.root / "specs/occupied"
        occupied.mkdir()
        collision = self.run_cli(
            "new", "occupied", "--title", "Occupied", "--summary", "Outro cadastro"
        )
        self.assertEqual(collision.returncode, 1)
        self.assertIn("Destino já existe", collision.stderr)

    def test_output_cannot_overwrite_canonical_file(self):
        self.run_cli("new", "alpha", "--title", "Alpha", "--summary", "Importar despesas de uma planilha")
        target = self.root / "specs/alpha/PRD.md"
        before = target.read_text()
        result = self.run_cli("feed", "--output", str(target))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(target.read_text(), before)

    def test_source_failure_remains_operational(self):
        config = self.root / ".superflow/config.json"
        config.parent.mkdir()
        for content in ("not json", '{"specs_root": ""}'):
            config.write_text(content, encoding="utf-8")
            result = self.run_cli("check", "status")
            self.assertEqual(result.returncode, 2)
            self.assertIn("operational_error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
