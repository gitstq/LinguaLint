import _bootstrap  # noqa: F401
import unittest

from lingualint.config import Config
from lingualint.engine import Linter


def lint(text, **cfg):
    return Linter(Config.from_dict(cfg) if cfg else Config()).lint_text(text, language="en")


def ids(result):
    return [i.rule_id for i in result.issues]


class EnglishRuleTests(unittest.TestCase):
    def test_repeated_word(self):
        r = lint("the the house")
        self.assertIn("ENG001", ids(r))
        fix = next(i for i in r.issues if i.rule_id == "ENG001")
        self.assertEqual(fix.suggestion, "the")

    def test_repeated_word_allowlist(self):
        self.assertNotIn("ENG001", ids(lint("I had had enough.")))
        self.assertNotIn("ENG001", ids(lint("I think that that is fine.")))

    def test_articles(self):
        r = lint("a apple and an university")
        sug = [i.suggestion for i in r.issues if i.rule_id == "ENG002"]
        self.assertEqual(len(sug), 2)
        self.assertIn("an apple", sug)
        self.assertIn("a university", sug)

    def test_article_pronunciation_exceptions(self):
        self.assertNotIn("ENG002", ids(lint("an hour later")))
        self.assertNotIn("ENG002", ids(lint("a European user")))
        self.assertNotIn("ENG002", ids(lint("a cat sleeps")))

    def test_sentence_capitalization(self):
        self.assertIn("ENG003", ids(lint("Stop. go now.")))
        self.assertNotIn("ENG003", ids(lint("buy it, e.g. apples")))

    def test_comma_space(self):
        r = lint("hello,world")
        issue = next(i for i in r.issues if i.rule_id == "ENG004")
        self.assertEqual(issue.suggestion, ", ")

    def test_confusables(self):
        cases = {
            "its going home": "it's going",
            "Its going home": "It's going",
            "better then that": "better than",
            "you will loose data": "will lose",
            "an affect": "an effect",
            "loose weight now": "lose weight",
            "your welcome": "you're welcome",
        }
        for text, want in cases.items():
            r = lint(text)
            fixes = [i for i in r.issues if i.rule_id == "ENG005"]
            self.assertTrue(fixes, text)
            self.assertEqual(fixes[0].suggestion, want)

    def test_spelling(self):
        r = lint("definately seperate")
        spell = [i for i in r.issues if i.rule_id == "ENG006"]
        self.assertEqual(len(spell), 2)
        r2 = lint("definately", ignore_words=["definately"])
        self.assertNotIn("ENG006", ids(r2))
        r3 = lint("foobar", typo_pairs={"foobar": "fixed"})
        self.assertEqual(next(i for i in r3.issues if i.rule_id == "ENG006").suggestion, "fixed")

    def test_passive_voice(self):
        self.assertIn("ENG007", ids(lint("The house was constructed in 1990.")))
        self.assertNotIn("ENG007", ids(lint("She was tired.")))

    def test_weak_words(self):
        self.assertIn("ENG008", ids(lint("it was very good")))
        self.assertNotIn("ENG008", ids(lint("it was good")))


if __name__ == "__main__":
    unittest.main()
