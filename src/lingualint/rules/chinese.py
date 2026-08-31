"""Chinese (Simplified) typography, typo and style rules."""
from __future__ import annotations

import re
from typing import Iterable, List, Tuple

from .base import Document, Rule
from ..textutils import is_cjk_ideograph


class ChineseRule(Rule):
    """Marker base: Chinese rules only run on Chinese-context documents."""
    languages = ("zh",)

# Half-width -> full-width punctuation mapping.
HALF_TO_FULL = {
    ",": "，",
    ".": "。",
    "?": "？",
    "!": "！",
    ";": "；",
    ":": "：",
}
_HALF_PUNCT = re.compile(r"[,.?!;:]")

# CJK ideograph <-> latin/digit boundary.
_CJK_LATIN = re.compile(r"([一-鿿])([A-Za-z0-9])")
_LATIN_CJK = re.compile(r"([A-Za-z0-9])([一-鿿])")

# Function particles accidentally doubled (legit reduplication excluded).
_DOUBLE_PARTICLE = re.compile(r"([的了是在和就都也与及着吗呢吧啊])\1")

# High-confidence idiom / word typos (safe to auto-fix).
IDIOM_TYPOS = {
    "按装": "安装",
    "迫不急待": "迫不及待",
    "再接再励": "再接再厉",
    "谈笑风声": "谈笑风生",
    "一诺千斤": "一诺千金",
    "走头无路": "走投无路",
    "出奇不意": "出其不意",
    "自抱自弃": "自暴自弃",
    "甘败下风": "甘拜下风",
    "一愁莫展": "一筹莫展",
    "蛛丝蚂迹": "蛛丝马迹",
    "萎糜不振": "萎靡不振",
    "名信片": "明信片",
    "追朔": "追溯",
    "渲泄": "宣泄",
    "痉孪": "痉挛",
    "膺品": "赝品",
    "装祯": "装帧",
    "幅射": "辐射",
    "松驰": "松弛",
    "穿流不息": "川流不息",
    "针贬时弊": "针砭时弊",
    "鼎立相助": "鼎力相助",
    "额首称庆": "额手称庆",
    "馨竹难书": "罄竹难书",
    "入场卷": "入场券",
    "水笼头": "水龙头",
    "沤心沥血": "呕心沥血",
    "凭添": "平添",
    "弦律": "旋律",
}

# Semantic redundancy (fixed phrases, safe to auto-fix).
REDUNDANCY_FIX = {
    "涉及到": "涉及",
    "免费赠送": "赠送",
    "过分溺爱": "溺爱",
    "目前的现状": "现状",
    "目的是为了": "目的是",
    "的原因是因为": "原因是",
    "凯旋归来": "凯旋",
    "悬殊很大": "悬殊",
    "一致共识": "共识",
    "大约左右": "左右",
}

# Span redundancy patterns: non-autofixable suggestions.
REDUNDANCY_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"大约([^，。！？；：]{0,10}?)左右"),
     "“大约”和“左右”语义重复，保留其一。"),
    (re.compile(r"超过([^，。！？；：]{0,8}?)以上"),
     "“超过”和“以上”语义重复，保留其一。"),
    (re.compile(r"几乎([^，。！？；：]{0,8}?)差不多"),
     "“几乎”和“差不多”语义重复，保留其一。"),
]

_SENT_SPLIT = re.compile(r"[。！？；…\n]")


class HalfWidthPunctuationRule(ChineseRule):
    id = "ZH001"
    category = "typography"
    severity = "warning"
    autofixable = True
    title = "半角标点出现在中文语境"
    description = "中文句子中的 , . ? ! ; : 应使用全角标点（数字小数/时间除外）。"

    def check(self, doc: Document) -> Iterable:
        text = doc.text
        issues = []
        for m in _HALF_PUNCT.finditer(text):
            i = m.start()
            if doc.is_protected(i):
                continue
            prev_ch = text[i - 1] if i > 0 else ""
            next_ch = text[i + 1] if i + 1 < len(text) else ""
            # Numbers: decimals (3.14), time (12:30), thousands (1,000).
            if prev_ch.isdigit() and next_ch.isdigit():
                continue
            cjk_near_before = any(is_cjk_ideograph(c)
                                  for c in text[max(0, i - 12):i])
            prev_cjk = is_cjk_ideograph(prev_ch)
            next_cjk = is_cjk_ideograph(next_ch)
            if prev_cjk or (next_cjk and cjk_near_before):
                full = HALF_TO_FULL[m.group(0)]
                issues.append(self.make_issue(
                    i, i + 1,
                    f"中文语境应使用全角标点“{full}”，而非“{m.group(0)}”。",
                    full))
        return issues


class CjkLatinSpacingRule(ChineseRule):
    id = "ZH002"
    category = "typography"
    severity = "suggestion"
    autofixable = True
    title = "中英文之间缺少空格"
    description = "中文与拉丁字母/数字之间建议保留一个半角空格。"

    def check(self, doc: Document) -> Iterable:
        if not self.config.zh_latin_spacing:
            return ()
        issues = []
        for rx in (_CJK_LATIN, _LATIN_CJK):
            for m in rx.finditer(doc.text):
                if doc.protected_at_span(m.start(), m.end()):
                    continue
                issues.append(self.make_issue(
                    m.start(), m.end(), "中文与英文/数字之间建议加空格。",
                    f"{m.group(1)} {m.group(2)}"))
        issues.sort(key=lambda x: x.start)
        return issues


class DoubledParticleRule(ChineseRule):
    id = "ZH003"
    category = "typo"
    severity = "error"
    autofixable = True
    title = "功能助词重复"
    description = "的/了/是/在 等功能助词误重复（合法叠词如“慢慢”不在此列）。"

    def check(self, doc: Document) -> Iterable:
        for m in _DOUBLE_PARTICLE.finditer(doc.text):
            if doc.protected_at_span(m.start(), m.end()):
                continue
            yield self.make_issue(
                m.start(), m.end(),
                f"助词“{m.group(1)}”疑似重复。", m.group(1))


class IdiomTypoRule(ChineseRule):
    id = "ZH004"
    category = "spelling"
    severity = "error"
    autofixable = True
    title = "成语/常用词错别字"
    description = "高置信成语与常用词错别字修正。"

    def check(self, doc: Document) -> Iterable:
        issues = []
        pairs = dict(IDIOM_TYPOS)
        pairs.update(self.config.typo_pairs)
        for wrong, right in pairs.items():
            if re.fullmatch(r"[A-Za-z0-9' -]+", wrong):
                continue  # latin pairs belong to ENG006
            start = 0
            while True:
                idx = doc.text.find(wrong, start)
                if idx < 0:
                    break
                if not doc.protected_at_span(idx, idx + len(wrong)):
                    issues.append(self.make_issue(
                        idx, idx + len(wrong),
                        f"“{wrong}”为错别字，正确写法是“{right}”。", right))
                start = idx + len(wrong)
        issues.sort(key=lambda x: x.start)
        return issues


class RedundancyRule(ChineseRule):
    id = "ZH005"
    category = "style"
    severity = "suggestion"
    autofixable = True
    title = "语义重复/赘余"
    description = "“涉及到、免费赠送、大约…左右”等语义重复表达。"

    def check(self, doc: Document) -> Iterable:
        issues: List = []
        for wrong, right in REDUNDANCY_FIX.items():
            start = 0
            while True:
                idx = doc.text.find(wrong, start)
                if idx < 0:
                    break
                if not doc.protected_at_span(idx, idx + len(wrong)):
                    issues.append(self.make_issue(
                        idx, idx + len(wrong),
                        f"“{wrong}”语义赘余，建议改为“{right}”。", right,
                        autofixable=True))
                start = idx + len(wrong)
        for rx, hint in REDUNDANCY_PATTERNS:
            for m in rx.finditer(doc.text):
                if doc.protected_at_span(m.start(), m.end()):
                    continue
                issues.append(self.make_issue(
                    m.start(), m.end(), hint, autofixable=False))
        issues.sort(key=lambda x: x.start)
        return issues


class LongChineseSentenceRule(ChineseRule):
    id = "ZH006"
    category = "readability"
    severity = "info"
    autofixable = False
    title = "中文长句"
    description = "单句 CJK 字符数超过阈值（默认 60），建议断句。"

    def check(self, doc: Document) -> Iterable:
        threshold = self.config.long_zh_sentence
        if not threshold or threshold <= 0:
            return ()
        issues = []
        bounds = [(m.start(), m.end()) for m in _SENT_SPLIT.finditer(doc.text)]
        bounds.append((len(doc.text), len(doc.text)))  # trailing segment
        cursor = 0
        for seg_end, next_cursor in bounds:
            seg = doc.text[cursor:seg_end]
            cjk_count = sum(1 for c in seg if is_cjk_ideograph(c))
            if cjk_count >= threshold and not doc.protected_at_span(cursor, seg_end):
                issues.append(self.make_issue(
                    cursor, seg_end,
                    f"该句含 {cjk_count} 个汉字，超过 {threshold} 字阈值，建议拆分。",
                    severity=self.effective_severity()))
            cursor = next_cursor
        return issues


CHINESE_RULES = [
    HalfWidthPunctuationRule,
    CjkLatinSpacingRule,
    DoubledParticleRule,
    IdiomTypoRule,
    RedundancyRule,
    LongChineseSentenceRule,
]
