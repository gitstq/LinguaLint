import _bootstrap  # noqa: F401
import unittest

from lingualint.readability import (
    analyze, chinese_readability, count_syllables, english_readability,
)


class ReadabilityTests(unittest.TestCase):
    def test_syllables(self):
        self.assertEqual(count_syllables("the"), 1)
        self.assertEqual(count_syllables("apple"), 2)
        self.assertEqual(count_syllables("because"), 2)
        self.assertGreaterEqual(count_syllables("international"), 4)

    def test_english_report(self):
        text = ("The cat sat on the mat. It looked at the warm sun and was "
                "happy. A small dog ran past quickly.")
        rep = english_readability(text)
        self.assertIsNotNone(rep)
        self.assertEqual(rep.language, "en")
        self.assertGreaterEqual(rep.flesch_reading_ease, 0)
        self.assertIn("grade", rep.band())

    def test_english_too_short(self):
        self.assertIsNone(english_readability("hi"))

    def test_chinese_report(self):
        text = "这是一个简单的测试句子。我们希望它足够通顺。阅读起来没有任何障碍。"
        rep = chinese_readability(text)
        self.assertIsNotNone(rep)
        self.assertGreater(rep.avg_cjk_per_sentence, 0)
        self.assertEqual(rep.sentences, 3)

    def test_analyze_mixed(self):
        text = ("这是中文句子，包含 English words inside. "
                "Another English sentence follows here closely.")
        out = analyze(text, "auto")
        self.assertIn("zh", out)

    def test_analyze_english_only(self):
        text = "Plain short words make texts easy to read. Most readers enjoy clear writing."
        out = analyze(text, "en")
        self.assertIn("en", out)
        self.assertNotIn("zh", out)


if __name__ == "__main__":
    unittest.main()
