import _bootstrap  # noqa: F401
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from lingualint import cli


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bad = os.path.join(self.tmp.name, "bad.md")
        with open(self.bad, "w", encoding="utf-8") as f:
            f.write("definately the the text ,")
        self.good = os.path.join(self.tmp.name, "good.md")
        with open(self.good, "w", encoding="utf-8") as f:
            f.write("A clean and readable English sentence.")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.run(argv)
        return code, out.getvalue(), err.getvalue()

    def test_lint_file_gate_fails(self):
        code, out, _ = self._run([self.bad, "--format", "json", "--no-color"])
        self.assertEqual(code, 1)
        payload = json.loads(out)
        self.assertGreaterEqual(payload["summary"]["error"], 1)

    def test_clean_file_passes(self):
        code, _, _ = self._run([self.good, "--no-color"])
        self.assertEqual(code, 0)

    def test_min_score_gate(self):
        code, _, _ = self._run([self.good, self.bad, "--min-score", "99",
                                "--no-color"])
        self.assertEqual(code, 1)

    def test_fix_rewrites_file(self):
        code, _, _ = self._run([self.bad, "--fix", "--no-color"])
        self.assertIn(code, (0, 1))
        with open(self.bad, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("definitely", content)
        self.assertNotIn("the the", content)

    def test_list_rules(self):
        code, out, _ = self._run(["--list-rules"])
        self.assertEqual(code, 0)
        self.assertIn("ENG001", out)
        self.assertIn("ZH001", out)

    def test_missing_path(self):
        code, _, err = self._run([os.path.join(self.tmp.name, "nope.md")])
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_directory_scan_and_output_file(self):
        report = os.path.join(self.tmp.name, "r.json")
        code, _, _ = self._run([self.tmp.name, "-f", "json", "-o", report,
                                "--no-color"])
        self.assertEqual(code, 1)
        with open(report, encoding="utf-8") as f:
            payload = json.load(f)
        self.assertEqual(payload["summary"]["files"], 2)

    def test_stdin_mode(self):
        fake = io.StringIO("definately")
        fake.isatty = lambda: False
        old = sys.stdin
        sys.stdin = fake
        try:
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli.run(["--format", "json"])
        finally:
            sys.stdin = old
        self.assertEqual(code, 1)
        self.assertIn("ENG006", out.getvalue())


if __name__ == "__main__":
    unittest.main()
