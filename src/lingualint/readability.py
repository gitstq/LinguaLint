"""Readability metrics for English and Chinese text."""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, Optional

from .textutils import is_cjk_ideograph

_WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)?")
_EN_SENT_RE = re.compile(r"[.!?]+(?:\s|$)")
_ZH_SENT_RE = re.compile(r"[。！？；…]+")


def count_syllables(word: str) -> int:
    """Standard heuristic English syllable counter."""
    w = word.lower().strip(".'\"")
    if not w:
        return 0
    if w.endswith("e") and not w.endswith(("le", "ee", "ye")):
        w = w[:-1]
    groups = re.findall(r"[aeiouy]+", w)
    return max(1, len(groups))


@dataclass
class ReadabilityReport:
    language: str
    sentences: int
    words: int
    # English fields
    syllables: Optional[int] = None
    flesch_reading_ease: Optional[float] = None
    flesch_grade: Optional[float] = None
    # Chinese fields
    cjk_chars: Optional[int] = None
    avg_cjk_per_sentence: Optional[float] = None
    long_sentence_ratio: Optional[float] = None

    def band(self) -> str:
        if self.flesch_reading_ease is not None:
            s = self.flesch_reading_ease
            if s >= 90:
                return "very easy (5th grade)"
            if s >= 80:
                return "easy (6th grade)"
            if s >= 70:
                return "fairly easy (7th grade)"
            if s >= 60:
                return "plain English (8-9th grade)"
            if s >= 50:
                return "fairly difficult (10-12th grade)"
            if s >= 30:
                return "difficult (college)"
            return "very difficult (college graduate)"
        if self.avg_cjk_per_sentence is not None:
            a = self.avg_cjk_per_sentence
            if a <= 20:
                return "流畅：平均句长较短"
            if a <= 40:
                return "适中：适合大多数阅读场景"
            if a <= 60:
                return "偏长：建议适当断句"
            return "冗长：强烈建议拆分长句"
        return "n/a"

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["band"] = self.band()
        return d


def english_readability(text: str) -> Optional[ReadabilityReport]:
    words = _WORD_RE.findall(text)
    if len(words) < 2:
        return None
    sentences = max(1, len(_EN_SENT_RE.findall(text)))
    syllables = sum(count_syllables(w) for w in words)
    wps = len(words) / sentences
    spw = syllables / len(words)
    fre = round(206.835 - 1.015 * wps - 84.6 * spw, 2)
    fk = round(0.39 * wps + 11.8 * spw - 15.59, 2)
    return ReadabilityReport(language="en", sentences=sentences, words=len(words),
                             syllables=syllables, flesch_reading_ease=fre,
                             flesch_grade=fk)


def chinese_readability(text: str) -> Optional[ReadabilityReport]:
    cjk = [c for c in text if is_cjk_ideograph(c)]
    if len(cjk) < 8:
        return None
    parts = [p for p in _ZH_SENT_RE.split(text)
             if sum(1 for c in p if is_cjk_ideograph(c)) > 0]
    sentences = max(1, len(parts))
    lengths = [sum(1 for c in p if is_cjk_ideograph(c)) for p in parts]
    avg = round(sum(lengths) / sentences, 2)
    long_ratio = round(sum(1 for n in lengths if n > 40) / sentences, 2)
    return ReadabilityReport(language="zh", sentences=sentences, words=len(cjk),
                             cjk_chars=len(cjk), avg_cjk_per_sentence=avg,
                             long_sentence_ratio=long_ratio)


def analyze(text: str, language: str) -> Dict[str, ReadabilityReport]:
    out: Dict[str, ReadabilityReport] = {}
    en = english_readability(text)
    zh = chinese_readability(text)
    if language == "en":
        if en:
            out["en"] = en
    elif language == "zh":
        if zh:
            out["zh"] = zh
        if en:
            out["en"] = en
    else:
        if en:
            out["en"] = en
        if zh:
            out["zh"] = zh
    return out
