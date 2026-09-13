#!/usr/bin/env python3
"""CLI checks exercise filesystem effects, exit codes and snapshot consistency."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from superflow import atomic_write
from superflow_model import SourceError, build_snapshot

CLI = Path(__file__).with_name("superflow.py")


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(CLI), "--root", str(self.root), *args],
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_new_creates_only_status_and_prd_without_overwriting(self):
        out = self.run_cli("new", "one", "--title", "Expense import")
        self.assertEqual(out.returncode, 0, out.stderr)
        folder = self.root / "specs/one"
        self.assertEqual(sorted(p.name for p in folder.iterdir()), ["PRD.md", "status.md"])
        before = {p.name: p.read_bytes() for p in folder.iterdir()}
        self.assertEqual(self.run_cli("new", "one", "--title", "Changed").returncode, 1)
        self.assertEqual(before, {p.name: p.read_bytes() for p in folder.iterdir()})
        self.assertEqual(self.run_cli("check").returncode, 0)

    def test_new_rejects_path_escape(self):
        out = self.run_cli("new", "../escape", "--title", "No")
        self.assertEqual(out.returncode, 1)
        self.assertFalse((self.root / "escape").exists())

    def test_new_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "specs").mkdir()
            (self.root / "specs/link").symlink_to(outside, target_is_directory=True)
            out = self.run_cli("new", "link/escape", "--title", "No")
            self.assertEqual(out.returncode, 1, out.stderr)
            self.assertFalse((Path(outside) / "escape").exists())

    def test_check_is_read_only_and_commands_never_execute_project_hooks(self):
        config = self.root / ".superflow"
        config.mkdir()
        (config / "config.json").write_text(json.dumps({
            "proof_cmd": "touch NEVER_EXECUTE", "ship_cmd": "touch NEVER_EXECUTE"}))
        self.assertEqual(self.run_cli("new", "one", "--title", "One").returncode, 0)
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.run_cli("check").returncode, 0)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        for cmd in ("feed", "qg"):
            result = self.run_cli(cmd)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "NEVER_EXECUTE").exists())

    def test_invalid_source_is_published_as_diagnostic_with_exit_one(self):
        self.run_cli("new", "one", "--title", "One")
        (self.root / "specs/one/status.md").write_text("---\nid: [broken\n---\n")
        out = self.run_cli("feed")
        self.assertEqual(out.returncode, 1)
        feed = json.loads((self.root / ".superflow/feed.json").read_text())
        self.assertEqual(feed["records"], [])
        self.assertEqual(feed["diagnostics"][0]["code"], "INVALID_SPEC")
        self.assertEqual(self.run_cli("qg").returncode, 1)
        self.assertTrue((self.root / ".superflow/qg.html").exists())

    def test_source_changed_does_not_replace_previous_output(self):
        self.run_cli("new", "one", "--title", "One")
        _, sources = build_snapshot(self.root)
        target = self.root / "view.html"
        target.write_text("old")
        (self.root / "specs/one/PRD.md").write_text("changed")
        with self.assertRaisesRegex(SourceError, "SOURCE_CHANGED"):
            atomic_write(target, "new", self.root, sources)
        self.assertEqual(target.read_text(), "old")
        self.assertEqual(list(self.root.glob(".view.html.*")), [])

    def test_operational_failure_preserves_previous_html(self):
        target = self.root / "view.html"
        target.write_text("previous")
        (self.root / ".superflow").mkdir()
        (self.root / ".superflow/config.json").write_text('{"specs_root":"/elsewhere"}')
        out = self.run_cli("qg", "--output", str(target))
        self.assertEqual(out.returncode, 2)
        self.assertEqual(target.read_text(), "previous")

    def test_output_cannot_overwrite_source(self):
        self.run_cli("new", "one", "--title", "One")
        target = self.root / "specs/one/status.md"
        before = target.read_bytes()
        out = self.run_cli("feed", "--output", str(target))
        self.assertEqual(out.returncode, 2)
        self.assertEqual(target.read_bytes(), before)

    def test_explicit_output_works_without_side_feed(self):
        self.run_cli("new", "one", "--title", "One")
        out = self.run_cli("qg", "--output", str(self.root / "custom.html"))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertTrue((self.root / "custom.html").exists())
        self.assertFalse((self.root / ".superflow/feed.json").exists())


if __name__ == "__main__":
    unittest.main()

