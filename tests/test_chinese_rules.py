import _bootstrap  # noqa: F401
import unittest

from lingualint.config import Config
from lingualint.engine import Linter


def lint(text, **cfg):
    return Linter(Config.from_dict(cfg) if cfg else Config()).lint_text(text, language="zh")


def ids(result):
    return [i.rule_id for i in result.issues]


class ChineseRuleTests(unittest.TestCase):
    def test_half_width_punct_in_chinese(self):
        r = lint("然后,继续")
        issue = next(i for i in r.issues if i.rule_id == "ZH001")
        self.assertEqual(issue.suggestion, "，")

    def test_half_width_punct_numbers_exempt(self):
        self.assertNotIn("ZH001", ids(lint("数值是3.14，时间12:30")))

    def test_half_width_punct_pure_english_exempt(self):
        self.assertNotIn("ZH001", ids(lint("hello, world. This is fine.")))

    def test_cjk_latin_spacing(self):
        r = lint("使用Python编写代码")
        spacing = [i for i in r.issues if i.rule_id == "ZH002"]
        self.assertEqual(len(spacing), 2)
        r2 = lint("使用Python", zh_latin_spacing=False)
        self.assertNotIn("ZH002", ids(r2))

    def test_doubled_particle(self):
        issue = next(i for i in lint("我的的书").issues if i.rule_id == "ZH003")
        self.assertEqual(issue.suggestion, "的")
        self.assertNotIn("ZH003", ids(lint("慢慢走就好")))

    def test_idiom_typo(self):
        issue = next(i for i in lint("我迫不急待").issues if i.rule_id == "ZH004")
        self.assertEqual(issue.suggestion, "迫不及待")

    def test_redundancy_fixed(self):
        issue = next(i for i in lint("这涉及到隐私").issues if i.rule_id == "ZH005")
        self.assertEqual(issue.suggestion, "涉及")

    def test_redundancy_pattern(self):
        r = lint("大约五十人左右参加")
        hints = [i for i in r.issues if i.rule_id == "ZH005" and not i.autofixable]
        self.assertEqual(len(hints), 1)

    def test_long_sentence(self):
        long_sent = "我们" + "持续推进各项工作" * 8  # > 60 CJK chars
        r = lint(long_sent)
        self.assertIn("ZH006", ids(r))
        r2 = lint(long_sent, long_zh_sentence=500)
        self.assertNotIn("ZH006", ids(r2))

    def test_protected_code_span(self):
        self.assertNotIn("ZH004", ids(lint("代码 `迫不急待` 在反引号中")))


if __name__ == "__main__":
    unittest.main()
