import _bootstrap  # noqa: F401
import unittest

from lingualint.config import Config
from lingualint.engine import Linter


def lint(text, language="en", **cfg):
    c = Config.from_dict(cfg) if cfg else Config()
    return Linter(c).lint_text(text, language=language)


class CommonRuleTests(unittest.TestCase):
    def test_trailing_whitespace(self):
        r = lint("hello   \nworld")
        self.assertTrue(any(i.rule_id == "COM001" for i in r.issues))

    def test_multiple_blank_lines(self):
        r = lint("a\n\n\n\nb")
        self.assertTrue(any(i.rule_id == "COM002" for i in r.issues))

    def test_multiple_spaces(self):
        r = lint("a  b")
        self.assertTrue(any(i.rule_id == "COM003" for i in r.issues))

    def test_space_before_punct(self):
        r = lint("word ,")
        self.assertTrue(any(i.rule_id == "COM004" for i in r.issues))

    def test_zero_width(self):
        r = lint("a\u200bb")
        issue = next(i for i in r.issues if i.rule_id == "COM005")
        self.assertEqual(issue.severity, "error")

    def test_repeated_punctuation(self):
        r1 = lint("wow!!!")
        self.assertTrue(any(i.rule_id == "COM006" for i in r1.issues))
        r2 = lint("真的吗？？", language="zh")
        self.assertTrue(any(i.rule_id == "COM006" for i in r2.issues))
        self.assertFalse(any(i.rule_id == "COM006" for i in lint("and...").issues))

    def test_unmatched_quotes(self):
        r = lint("“only left quote")
        self.assertTrue(any(i.rule_id == "COM007" for i in r.issues))

    def test_long_line(self):
        r = lint("x" * 30, max_line_length=10)
        self.assertTrue(any(i.rule_id == "COM008" for i in r.issues))

    def test_url_protected(self):
        r = lint("see https://example.com/a,b for details")
        self.assertFalse(any(i.rule_id == "COM004" for i in r.issues))


if __name__ == "__main__":
    unittest.main()
