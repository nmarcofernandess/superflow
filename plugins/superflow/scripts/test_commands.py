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

    def test_new_creates_only_prd_and_status(self):
        result = self.run_cli("new", "alpha", "--title", "Alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        names = sorted(path.name for path in (self.root / "specs/alpha").iterdir())
        self.assertEqual(names, ["PRD.md", "status.md"])
        status = (self.root / "specs/alpha/status.md").read_text()
        self.assertIn("status: pending", status)
        self.assertNotIn("phase:", status)

    def test_feed_and_qg_never_copy_private_sources(self):
        self.run_cli("new", "alpha", "--title", "Alpha")
        directory = self.root / "specs/alpha"
        for name in ("PRD.md", "SPEC.md", "plan.json", "progress.md", "HANDBOOK.md"):
            (directory / name).write_text("SECRET_" + name, encoding="utf-8")
        feed = self.run_cli("feed")
        qg = self.run_cli("qg")
        self.assertEqual(feed.returncode, 0, feed.stderr)
        self.assertEqual(qg.returncode, 0, qg.stderr)
        self.assertNotIn("SECRET_", (self.root / ".superflow/feed.json").read_text())
        self.assertNotIn("SECRET_", (self.root / ".superflow/qg.html").read_text())

    def test_check_ready_uses_explicit_four_file_boundary(self):
        self.run_cli("new", "alpha", "--title", "Alpha")
        self.assertEqual(self.run_cli("check", "ready", "alpha").returncode, 1)
        directory = self.root / "specs/alpha"
        (directory / "SPEC.md").write_text("# Arquitetura", encoding="utf-8")
        (directory / "plan.json").write_text(json.dumps({"tasks": []}), encoding="utf-8")
        self.assertEqual(self.run_cli("check", "ready", "alpha").returncode, 0)
        self.assertEqual(self.run_cli("check", "status").returncode, 0)

    def test_invalid_status_produces_diagnostic_and_nonzero(self):
        self.run_cli("new", "alpha", "--title", "Alpha")
        (self.root / "specs/alpha/status.md").write_text("---\nid: [bad\n---\n")
        result = self.run_cli("feed")
        self.assertEqual(result.returncode, 1)
        data = json.loads((self.root / ".superflow/feed.json").read_text())
        self.assertEqual(data["diagnostics"][0]["code"], "INVALID_STATUS")

    def test_output_cannot_overwrite_canonical_file(self):
        self.run_cli("new", "alpha", "--title", "Alpha")
        target = self.root / "specs/alpha/PRD.md"
        before = target.read_text()
        result = self.run_cli("feed", "--output", str(target))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(target.read_text(), before)


if __name__ == "__main__":
    unittest.main()
