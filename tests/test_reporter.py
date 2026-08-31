import _bootstrap  # noqa: F401
import json
import unittest

from lingualint.config import Config
from lingualint.engine import Linter
from lingualint.reporter import (
    render_html, render_json, render_markdown, render_text, aggregate,
)


class ReporterTests(unittest.TestCase):
    def setUp(self):
        linter = Linter(Config())
        self.items = [
            ("a.md", linter.lint_text("definately bad", language="en")),
            ("b.md", linter.lint_text("A clean sentence.", language="en")),
        ]

    def test_aggregate(self):
        agg = aggregate(self.items)
        self.assertEqual(agg["files"], 2)
        self.assertGreaterEqual(agg["error"], 1)

    def test_text(self):
        out = render_text(self.items, use_color=False)
        self.assertIn("a.md", out)
        self.assertIn("ENG006", out)
        self.assertIn("Totals", out)

    def test_json(self):
        payload = json.loads(render_json(self.items))
        self.assertEqual(payload["summary"]["files"], 2)
        self.assertEqual(len(payload["results"]), 2)

    def test_markdown(self):
        out = render_markdown(self.items)
        self.assertIn("# LinguaLint Report", out)
        self.assertIn("ENG006", out)

    def test_html_self_contained_and_escaped(self):
        out = render_html(self.items)
        self.assertTrue(out.startswith("<!DOCTYPE html>"))
        self.assertIn("<style>", out)
        self.assertNotIn("http://", out.replace("<!DOCTYPE", ""))

    def test_html_escapes_content(self):
        linter = Linter(Config())
        items = [("a<b>.md", linter.lint_text("very good", language="en"))]
        out = render_html(items)
        self.assertIn("a&lt;b&gt;.md", out)


if __name__ == "__main__":
    unittest.main()
