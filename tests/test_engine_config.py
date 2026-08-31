import _bootstrap  # noqa: F401
import unittest

from lingualint.config import Config
from lingualint.engine import Linter
from lingualint.textutils import (
    detect_language, offset_to_line_col, protected_ranges, line_starts,
)


class EngineConfigTests(unittest.TestCase):
    def test_language_detection(self):
        self.assertEqual(detect_language("pure english text here"), "en")
        self.assertEqual(detect_language("这是一段中文内容，包含不少汉字"), "zh")

    def test_force_language_filters_rules(self):
        text = "它非常good"
        zh = Linter(Config()).lint_text(text, language="zh")
        en = Linter(Config()).lint_text(text, language="en")
        self.assertTrue(any(i.rule_id.startswith("ZH") for i in zh.issues))
        self.assertFalse(any(i.rule_id.startswith("ZH") for i in en.issues))

    def test_disable_rule(self):
        cfg = Config.from_dict({"rules": {"ENG008": False}})
        r = Linter(cfg).lint_text("it was very good", language="en")
        self.assertFalse(any(i.rule_id == "ENG008" for i in r.issues))

    def test_severity_override(self):
        cfg = Config.from_dict({"rules": {"ENG008": "error"}})
        r = Linter(cfg).lint_text("very good", language="en")
        issue = next(i for i in r.issues if i.rule_id == "ENG008")
        self.assertEqual(issue.severity, "error")

    def test_unknown_config_key_rejected(self):
        with self.assertRaises(ValueError):
            Config.from_dict({"nope": 1})

    def test_line_col_mapping(self):
        text = "ab\ncdef\ng"
        starts = line_starts(text)
        self.assertEqual(offset_to_line_col(starts, 0), (1, 1))
        self.assertEqual(offset_to_line_col(starts, 5), (2, 3))
        self.assertEqual(offset_to_line_col(starts, 8), (3, 1))

    def test_protected_ranges_inline_and_fence(self):
        text = "ok `very` text\n```\nvery\n```\n"
        ranges = protected_ranges(text)
        self.assertTrue(any(r.contains(text.find("very", 3)) for r in ranges))

    def test_score_decreases(self):
        clean = Linter(Config()).lint_text("A perfectly clean sentence.", language="en")
        dirty = Linter(Config()).lint_text("definately very bad ,", language="en")
        self.assertEqual(clean.score, 100)
        self.assertLess(dirty.score, clean.score)

    def test_line_col_attached(self):
        r = Linter(Config()).lint_text("ok definately", language="en")
        issue = next(i for i in r.issues if i.rule_id == "ENG006")
        self.assertGreaterEqual(issue.line, 1)
        self.assertEqual(issue.source, "definately")

    def test_to_dict_serializable(self):
        r = Linter(Config()).lint_text("definately", language="en")
        d = r.to_dict()
        self.assertEqual(d["counts"]["error"], 1)
        self.assertEqual(d["issues"][0]["rule_id"], "ENG006")


if __name__ == "__main__":
    unittest.main()
