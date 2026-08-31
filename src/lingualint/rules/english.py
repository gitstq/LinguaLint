"""English grammar, typography and style rules.

Rules favour precision over recall: every pattern is either a hard typo or
a clearly documented heuristic.
"""
from __future__ import annotations

import re
from typing import Iterable, List, Tuple

from .base import Document, Rule


class EnglishRule(Rule):
    """Marker base: English rules only run on English-context documents."""
    languages = ("en",)

# --- lexical resources ----------------------------------------------------

# Grammatically legitimate repeated words ("had had", "that that").
REPEAT_ALLOWLIST = {"that", "had"}

# "a"/"an" exceptions based on pronunciation.
AN_BEFORE = {"hour", "honest", "honor", "honour", "heir", "honorable",
             "honourable", "mb", "mp", "fbi", "llm", "sms", "http", "api"}
A_BEFORE = {"university", "unique", "unit", "united", "user", "european",
            "one", "once", "useful", "utility", "universal", "uk", "us",
            "euro", "eulogy", "euphemism"}

# Abbreviations after which a lowercase sentence start is legitimate.
ABBREVIATIONS = ("e.g.", "i.e.", "vs.", "etc.", "mr.", "mrs.", "ms.",
                 "dr.", "st.", "a.m.", "p.m.", "no.", "fig.", "vol.",
                 "inc.", "ltd.", "jr.", "sr.", "approx.")

# High-confidence misspellings (safe to auto-fix).
SPELLING_FIX = {
    "seperate": "separate",
    "definately": "definitely",
    "occured": "occurred",
    "recieve": "receive",
    "teh": "the",
    "neccessary": "necessary",
    "accomodate": "accommodate",
    "occurence": "occurrence",
    "untill": "until",
    "wether": "whether",
    "wich": "which",
    "becuase": "because",
    "adress": "address",
    "enviroment": "environment",
    "goverment": "government",
    "begining": "beginning",
    "similiar": "similar",
}

# Contextual confusables: (regex, 1-based group index to replace, replacement, hint).
CONFUSABLES: List[Tuple[re.Pattern, int, str, str]] = [
    (re.compile(r"\b(its)(\s+)(going|gonna|gotta|not|ok|okay|fine|about|been|"
                r"time|also|just|really|very|a|an|the)\b", re.I),
     1, "it's",
     'Possessive “its” followed by a verb/particle; did you mean “it’s”?'),
    (re.compile(r"\b(your)(\s+)(going|gonna|not|welcome|right|kidding|joking)\b", re.I),
     1, "you're",
     'Possessive “your” used where “you’re” (you are) fits.'),
    (re.compile(r"\b(?:more|less|other|rather|different|bigger|smaller|faster|"
                r"slower|better|worse|older|newer|easier|harder|greater|"
                r"larger|higher|lower)\s+(then)\b", re.I),
     1, "than", 'Comparisons use “than”, not “then”.'),
    (re.compile(r"\b(?:to|will|would|cannot|can't|don't|dont|you|we|they|i|he|she)\s+(loose)\b", re.I),
     1, "lose", '“loose” is an adjective; the verb is “lose”.'),
    (re.compile(r"\ban?\s+(affect)\b", re.I),
     1, "effect", 'After an article the noun “effect” is expected.'),
    (re.compile(r"\b(loose)(\s+)weight\b", re.I),
     1, "lose", 'The idiom is “lose weight”.'),
]

WEAK_WORDS = {
    "very": "weak intensifier; use a precise word instead",
    "really": "weak intensifier; consider removing it",
    "just": "filler word; it usually adds nothing",
    "quite": "softener; consider a direct statement",
    "rather": "softener; consider a direct statement",
    "somewhat": "vague qualifier; quantify or remove",
    "basically": "filler word; it usually adds nothing",
    "actually": "filler word; it usually adds nothing",
    "literally": "often-misused intensifier",
    "simply": "filler word; it usually adds nothing",
    "obviously": "weasel word; avoid assuming it is obvious",
    "clearly": "weasel word; let the evidence speak",
}

# -ed words after be-verbs that are usually adjectives, not passives.
PASSIVE_ALLOWLIST = {
    "tired", "excited", "bored", "pleased", "disappointed", "scared",
    "married", "crowded", "related", "located", "based", "interested",
    "surprised", "amazed", "confused", "embarrassed", "frustrated",
    "satisfied", "covered", "closed", "devoted", "dedicated", "addicted",
    "connected", "equipped", "involved", "included", "limited", "required",
    "designed", "expected", "allowed", "supposed", "used",
}

_REPEATED_WORD = re.compile(r"\b([A-Za-z]+)(\s+)\1\b", re.I)
_A_OR_AN = re.compile(r"\b(a|an)(\s+)([A-Za-z][A-Za-z'-]*)\b", re.I)
_SENT_START = re.compile(r"([.!?])([ \t]+)([a-z])")
_NO_SPACE_AFTER_COMMA = re.compile(r"(?<=[A-Za-z]),(?=[A-Za-z])")
_PASSIVE = re.compile(r"\b(am|is|are|was|were|be|been|being)\s+([A-Za-z]+ed)\b", re.I)
_WORD = re.compile(r"[A-Za-z]+")


def _replace_group(match: re.Match, group_index: int, replacement: str) -> str:
    """Rebuild match text replacing one captured group, preserving case."""
    g = match.group(group_index)
    rendered = replacement.capitalize() if g[:1].isupper() else replacement
    gs, ge = match.start(group_index) - match.start(), match.end(group_index) - match.start()
    return match.group(0)[:gs] + rendered + match.group(0)[ge:]


class RepeatedWordRule(EnglishRule):
    id = "ENG001"
    category = "grammar"
    severity = "error"
    autofixable = True
    title = "Repeated word"
    description = "相邻重复单词（合法叠词白名单除外）。"

    def check(self, doc: Document) -> Iterable:
        for m in _REPEATED_WORD.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            if m.group(1).lower() in REPEAT_ALLOWLIST:
                continue
            yield self.make_issue(
                m.start(), m.end(), f"Repeated word “{m.group(1)}”.", m.group(1))


class ArticleRule(EnglishRule):
    id = "ENG002"
    category = "grammar"
    severity = "warning"
    autofixable = True
    title = "a / an mismatch"
    description = "不定冠词 a/an 与后续单词发音不匹配。"

    def check(self, doc: Document) -> Iterable:
        for m in _A_OR_AN.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            article, sep, word = m.group(1), m.group(2), m.group(3)
            wl = word.lower()
            starts_vowel = word[0].lower() in "aeiou"
            want = "an" if (starts_vowel and wl not in A_BEFORE) or wl in AN_BEFORE else "a"
            if article.lower() != want:
                rendered = want.capitalize() if article[:1].isupper() else want
                yield self.make_issue(
                    m.start(), m.end(),
                    f"Use “{want}” before “{word}”, not “{article}”.",
                    rendered + sep + word)


class SentenceStartCapRule(EnglishRule):
    id = "ENG003"
    category = "capitalization"
    severity = "suggestion"
    autofixable = True
    title = "Sentence starts lowercase"
    description = "句首单词应大写（常见缩写除外）。"

    def check(self, doc: Document) -> Iterable:
        issues = []
        for m in _SENT_START.finditer(doc.text):
            start = m.start(3)
            if doc.is_protected(start):
                continue
            tail = doc.text[max(0, m.start() - 8):m.start() + 1].lower()
            if any(tail.endswith(ab) for ab in ABBREVIATIONS):
                continue
            repl = m.group(1) + m.group(2) + m.group(3).upper()
            issues.append(self.make_issue(
                m.start(), m.end(), "Sentence should start with a capital letter.",
                repl))
        return issues


class CommaSpaceRule(EnglishRule):
    id = "ENG004"
    category = "typography"
    severity = "warning"
    autofixable = True
    title = "Missing space after comma"
    description = "逗号后缺少空格。"

    def check(self, doc: Document) -> Iterable:
        for m in _NO_SPACE_AFTER_COMMA.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            yield self.make_issue(m.start(), m.end(),
                                  "Missing a space after the comma.", ", ")


class ConfusableRule(EnglishRule):
    id = "ENG005"
    category = "grammar"
    severity = "warning"
    autofixable = True
    title = "Commonly confused words"
    description = "its/it's、than/then、lose/loose 等易混词上下文启发式检查。"

    def check(self, doc: Document) -> Iterable:
        issues = []
        for rx, group_idx, repl, hint in CONFUSABLES:
            for m in rx.finditer(doc.text):
                if doc.protected_at_span(m.start(), m.end()):
                    continue
                fixed = _replace_group(m, group_idx, repl)
                issues.append(self.make_issue(m.start(), m.end(), hint, fixed))
        return issues


class SpellingRule(EnglishRule):
    id = "ENG006"
    category = "spelling"
    severity = "error"
    autofixable = True
    title = "Common misspelling"
    description = "高置信常见拼写错误自动修正，支持配置自定义错词表。"

    def check(self, doc: Document) -> Iterable:
        issues = []
        ignore = {w.lower() for w in self.config.ignore_words}
        pairs = dict(SPELLING_FIX)
        pairs.update({k.lower(): v for k, v in self.config.typo_pairs.items()})
        for wrong, right in pairs.items():
            for m in re.finditer(rf"\b{re.escape(wrong)}\b", doc.text, re.I):
                if doc.protected_at_span(m.start(), m.end()):
                    continue
                if m.group(0).lower() in ignore:
                    continue
                repl = right[:1].upper() + right[1:] if m.group(0)[:1].isupper() else right
                issues.append(self.make_issue(
                    m.start(), m.end(),
                    f"“{m.group(0)}” looks misspelled; did you mean “{right}”?",
                    repl))
        return issues


class PassiveVoiceRule(EnglishRule):
    id = "ENG007"
    category = "style"
    severity = "suggestion"
    autofixable = False
    title = "Possible passive voice"
    description = "be + 过去分词构成的被动语态（风格建议，形容词化 -ed 白名单除外）。"

    def check(self, doc: Document) -> Iterable:
        issues = []
        for m in _PASSIVE.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            if m.group(2).lower() in PASSIVE_ALLOWLIST:
                continue
            issues.append(self.make_issue(
                m.start(), m.end(),
                f"Possible passive voice “{m.group(0)}”; prefer active voice."))
        return issues


class WeakWordRule(EnglishRule):
    id = "ENG008"
    category = "style"
    severity = "suggestion"
    autofixable = False
    title = "Weak / filler word"
    description = "very/really/just 等弱化词与填充词（风格建议）。"

    def check(self, doc: Document) -> Iterable:
        issues = []
        for m in _WORD.finditer(doc.text):
            wl = m.group(0).lower()
            if wl not in WEAK_WORDS or doc.is_protected(m.start()):
                continue
            issues.append(self.make_issue(
                m.start(), m.end(),
                f"“{m.group(0)}” is a {WEAK_WORDS[wl]}."))
        return issues


ENGLISH_RULES = [
    RepeatedWordRule,
    ArticleRule,
    SentenceStartCapRule,
    CommaSpaceRule,
    ConfusableRule,
    SpellingRule,
    PassiveVoiceRule,
    WeakWordRule,
]
