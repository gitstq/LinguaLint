"""Text utilities: position mapping, script detection and protected ranges.

All helpers are dependency-free and work on plain ``str`` objects.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

# --- Unicode ranges -------------------------------------------------------

_CJK_IDOGRAPH = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
_CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿　-〿＀-￯]")
_LATIN_WORD = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)?")


def is_cjk_ideograph(ch: str) -> bool:
    """Return True for a CJK ideograph (excluding punctuation/kana)."""
    return bool(_CJK_IDOGRAPH.fullmatch(ch))


def is_cjk(ch: str) -> bool:
    """Return True for CJK ideographs, kana or CJK/full-width punctuation."""
    return bool(_CJK.fullmatch(ch))


def count_cjk(text: str) -> int:
    return len(_CJK_IDOGRAPH.findall(text))


def count_latin_words(text: str) -> int:
    return len(_LATIN_WORD.findall(text))


def line_starts(text: str) -> List[int]:
    """Return the offset at which each (1-based) line starts."""
    starts = [0]
    for m in re.finditer("\n", text):
        starts.append(m.end())
    return starts


def offset_to_line_col(starts: List[int], offset: int) -> Tuple[int, int]:
    """Convert a character offset to a 1-based ``(line, column)`` tuple."""
    # Binary search for the last line start <= offset.
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1, offset - starts[lo] + 1


# --- Protected ranges (code spans, fenced blocks, URLs) -------------------

_FENCE_RE = re.compile(r"(^|\n)(`{3,}|~{3,})[^\n]*\n.*?(?:\n\2[^\n]*(?=\n|$)|\Z)", re.S)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_URL_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s)>\]]+")
_AUTOLINK_RE = re.compile(r"<(?:https?://|mailto:)[^>]+>")


@dataclass(frozen=True)
class Range:
    start: int
    end: int

    def contains(self, offset: int) -> bool:
        return self.start <= offset < self.end

    def overlaps(self, start: int, end: int) -> bool:
        return self.start < end and start < self.end


def protected_ranges(text: str) -> List[Range]:
    """Find ranges that linters should not touch.

    * fenced code blocks (``` / ~~~)
    * inline code spans (`...`)
    * URLs / autolinks
    """
    ranges: List[Range] = []
    for m in _FENCE_RE.finditer(text):
        # m.start(1) keeps the leading newline offset out of the range.
        start = m.start(2) if m.group(1) else m.start()
        ranges.append(Range(start, m.end()))
    for rx in (_INLINE_CODE_RE, _URL_RE, _AUTOLINK_RE):
        for m in rx.finditer(text):
            ranges.append(Range(m.start(), m.end()))
    ranges.sort(key=lambda r: r.start)
    # Merge overlapping ranges (inline code inside a fence, for example).
    merged: List[Range] = []
    for r in ranges:
        if merged and r.start <= merged[-1].end:
            merged[-1] = Range(merged[-1].start, max(merged[-1].end, r.end))
        else:
            merged.append(r)
    return merged


def detect_language(text: str) -> str:
    """Detect ``zh`` / ``en`` from script proportions.

    A document is considered Chinese when CJK ideographs make up at least
    15% of the combined CJK + Latin character mass (and at least 8 CJK
    characters exist).  Mixed Chinese/English documents return ``zh`` so
    that both rule families still run on their respective spans.
    """
    cjk = count_cjk(text)
    latin = sum(len(w) for w in _LATIN_WORD.findall(text))
    if cjk >= 8 and cjk / max(1, cjk + latin) >= 0.15:
        return "zh"
    return "en"
