"""Language-agnostic typography and whitespace rules."""
from __future__ import annotations

import re
from typing import Iterable, List

from .base import Document, Rule

_ZERO_WIDTH = re.compile(r"[​-‏‪-‮﻿]")
_TRAILING_WS = re.compile(r"[ \t]+(?=\n|$)")
_MULTI_BLANK = re.compile(r"\n{3,}")
_MULTI_SPACE = re.compile(r"(?<=\S) {2,}(?=\S)")
_SPACE_BEFORE_PUNCT = re.compile(r" +([,.!?:;])")
_LATIN_REPEAT_PUNCT = re.compile(r"([!,?:;,])\1+")
_DOT_REPEAT = re.compile(r"\.{2,}")
_CJK_REPEAT_PUNCT = re.compile(r"([。！？，；：])\1+")
_QUOTE_PAIRS = (("“", "”"), ("‘", "’"))


class TrailingWhitespaceRule(Rule):
    id = "COM001"
    category = "whitespace"
    severity = "warning"
    autofixable = True
    title = "Trailing whitespace"
    description = "行尾多余的空格或制表符。"

    def check(self, doc: Document) -> Iterable:
        for m in _TRAILING_WS.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            yield self.make_issue(m.start(), m.end(), "Trailing whitespace.", "")


class MultipleBlankLinesRule(Rule):
    id = "COM002"
    category = "whitespace"
    severity = "suggestion"
    autofixable = True
    title = "Consecutive blank lines"
    description = "超过一个连续空行。"

    def check(self, doc: Document) -> Iterable:
        for m in _MULTI_BLANK.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            yield self.make_issue(m.start(), m.end(),
                                  "More than one consecutive blank line.", "\n\n")


class MultipleSpacesRule(Rule):
    id = "COM003"
    category = "whitespace"
    severity = "warning"
    autofixable = True
    title = "Multiple spaces between words"
    description = "非缩进场景下的连续多个半角空格。"

    def check(self, doc: Document) -> Iterable:
        for m in _MULTI_SPACE.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            yield self.make_issue(m.start(), m.end(),
                                  "Multiple spaces where one is enough.", " ")


class SpaceBeforePunctuationRule(Rule):
    id = "COM004"
    category = "punctuation"
    severity = "warning"
    autofixable = True
    title = "Space before punctuation"
    description = "英文标点前不应有空格。"

    def check(self, doc: Document) -> Iterable:
        for m in _SPACE_BEFORE_PUNCT.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            yield self.make_issue(m.start(), m.end(),
                                  "Space before punctuation mark.", m.group(1))


class ZeroWidthCharRule(Rule):
    id = "COM005"
    category = "invisible"
    severity = "error"
    autofixable = True
    title = "Invisible / zero-width character"
    description = "零宽字符、BOM、双向控制符等不可见字符。"

    def check(self, doc: Document) -> Iterable:
        for m in _ZERO_WIDTH.finditer(doc.text):
            ch = m.group(0)
            yield self.make_issue(
                m.start(), m.end(),
                f"Invisible character U+{ord(ch):04X}; remove it.", "")


class RepeatedPunctuationRule(Rule):
    id = "COM006"
    category = "punctuation"
    severity = "suggestion"
    autofixable = True
    title = "Repeated punctuation"
    description = "重复的标点（省略号 …/... 除外）。"

    def check(self, doc: Document) -> Iterable:
        issues: List = []
        for m in _LATIN_REPEAT_PUNCT.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            issues.append(self.make_issue(m.start(), m.end(),
                                          f"Repeated punctuation “{m.group(0)}”.",
                                          m.group(1)))
        for m in _DOT_REPEAT.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            length = len(m.group(0))
            if length == 3:
                continue  # "..." is an accepted ellipsis
            issues.append(self.make_issue(m.start(), m.end(),
                                          "Repeated full stops; use an ellipsis “…”."
                                          if length >= 4 else "Repeated full stop.",
                                          "…" if length >= 4 else "."))
        for m in _CJK_REPEAT_PUNCT.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            issues.append(self.make_issue(m.start(), m.end(),
                                          f"重复标点“{m.group(0)}”。", m.group(1)))
        return issues


class UnmatchedQuoteRule(Rule):
    id = "COM007"
    category = "punctuation"
    severity = "warning"
    autofixable = False
    title = "Unmatched quotation mark"
    description = "成对引号数量不匹配。"

    def check(self, doc: Document) -> Iterable:
        issues = []
        for left, right in _QUOTE_PAIRS:
            lc = doc.text.count(left)
            rc = doc.text.count(right)
            if lc != rc:
                first = doc.text.find(left if lc > rc else right)
                issues.append(self.make_issue(
                    first, first + 1,
                    f"Unmatched quote: {lc} “{left}” vs {rc} “{right}”."))
        # Straight double quotes parity on each non-code line.
        for idx, line in enumerate(doc.text.split("\n")):
            n = line.count('"')
            if n % 2 == 1:
                off = doc.starts[idx] + line.find('"')
                if not doc.is_protected(off):
                    issues.append(self.make_issue(
                        off, off + 1, "Odd number of straight double quotes on line."))
        return issues


class LongLineRule(Rule):
    id = "COM008"
    category = "layout"
    severity = "info"
    autofixable = False
    title = "Line too long"
    description = "单行长度超过配置阈值（默认 200 字符）。"

    def check(self, doc: Document) -> Iterable:
        limit = self.config.max_line_length
        if not limit or limit <= 0:
            return ()
        issues = []
        for idx, line in enumerate(doc.text.split("\n")):
            if len(line) > limit:
                off = doc.starts[idx] + limit
                issues.append(self.make_issue(
                    off, off + 1,
                    f"Line is {len(line)} chars long (limit {limit}).",
                    severity=self.effective_severity()))
        return issues


COMMON_RULES = [
    TrailingWhitespaceRule,
    MultipleBlankLinesRule,
    MultipleSpacesRule,
    SpaceBeforePunctuationRule,
    ZeroWidthCharRule,
    RepeatedPunctuationRule,
    UnmatchedQuoteRule,
    LongLineRule,
]
