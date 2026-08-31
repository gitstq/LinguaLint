import _bootstrap  # noqa: F401
import unittest

from lingualint.config import Config
from lingualint.engine import Linter


class AutofixTests(unittest.TestCase):
    def setUp(self):
        self.linter = Linter(Config())

    def test_english_autofix_chain(self):
        fixed, n, remaining = self.linter.fix_text(
            "definately the the best ,", language="en")
        self.assertIn("definitely", fixed)
        self.assertIn("the best", fixed)
        self.assertGreaterEqual(n, 3)
        self.assertLess(len(remaining.issues), 4)

    def test_chinese_mixed_autofix(self):
        fixed, n, _ = self.linter.fix_text("使用Python,然后", language="zh")
        self.assertEqual(fixed, "使用 Python，然后")
        self.assertGreaterEqual(n, 2)

    def test_idiom_autofix(self):
        fixed, _, _ = self.linter.fix_text("迫不急待出发", language="zh")
        self.assertIn("迫不及待", fixed)

    def test_non_fixable_remains(self):
        fixed, n, remaining = self.linter.fix_text("very good", language="en")
        self.assertEqual(fixed, "very good")
        self.assertEqual(n, 0)
        self.assertTrue(any(i.rule_id == "ENG008" for i in remaining.issues))

    def test_idempotent(self):
        once, _, _ = self.linter.fix_text("hello,world  ,,", language="en")
        twice, n2, _ = self.linter.fix_text(once, language="en")
        self.assertEqual(once, twice)
        self.assertEqual(n2, 0)


if __name__ == "__main__":
    unittest.main()
