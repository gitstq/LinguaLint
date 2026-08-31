"""Core lint engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import Config
from .issues import Issue, SEVERITY_WEIGHT, SEVERITY_ORDER
from .readability import analyze
from .rules import ALL_RULE_CLASSES, Rule
from .rules.base import Document
from .textutils import detect_language, offset_to_line_col


@dataclass
class LintResult:
    path: str
    language: str
    issues: List[Issue] = field(default_factory=list)
    char_count: int = 0
    score: int = 100
    readability: Dict = field(default_factory=dict)

    def counts(self) -> Dict[str, int]:
        c = {k: 0 for k in SEVERITY_WEIGHT}
        for i in self.issues:
            c[i.severity] += 1
        return c

    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "language": self.language,
            "char_count": self.char_count,
            "score": self.score,
            "counts": self.counts(),
            "readability": {k: v.to_dict() for k, v in self.readability.items()},
            "issues": [
                {
                    "rule_id": i.rule_id,
                    "severity": i.severity,
                    "category": i.category,
                    "line": i.line,
                    "column": i.col,
                    "start": i.start,
                    "end": i.end,
                    "message": i.message,
                    "suggestion": i.suggestion,
                    "autofixable": i.autofixable,
                    "source": i.source,
                }
                for i in self.issues
            ],
        }


class Linter:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or Config()
        self.rules: List[Rule] = [cls(self.config) for cls in ALL_RULE_CLASSES]

    # -- core --------------------------------------------------------------
    def lint_text(self, text: str, language: Optional[str] = None,
                  path: str = "<text>") -> LintResult:
        requested = language or self.config.language
        auto = requested == "auto"
        lang = detect_language(text) if auto else requested
        # Auto-detected (often bilingual) documents run both rule families;
        # a forced language runs only that family.
        eligible = {"en", "zh"} if auto else {lang}
        doc = Document.build(text, lang)
        found: List[Issue] = []
        for rule in self.rules:
            if not self.config.rule_enabled(rule.id, True):
                continue
            if not any(lf in eligible for lf in rule.languages):
                continue
            try:
                found.extend(rule.check(doc))
            except Exception as exc:  # a broken rule must not crash the run
                found.append(Issue(
                    rule_id=rule.id, start=0, end=min(1, len(text)),
                    message=f"internal rule error: {exc}", severity="error",
                    category="internal"))
        # Attach line/col and source snippet.
        for issue in found:
            issue.line, issue.col = offset_to_line_col(doc.starts, issue.start)
            issue.source = text[issue.start:issue.end]
        found.sort(key=lambda i: (i.start, SEVERITY_ORDER[i.severity], i.rule_id))
        result = LintResult(path=path, language=lang, issues=found,
                            char_count=len(text),
                            readability=analyze(text, lang))
        result.score = self._score(found)
        return result

    @staticmethod
    def _score(issues: List[Issue]) -> int:
        deduction = sum(SEVERITY_WEIGHT[i.severity] for i in issues)
        return max(0, 100 - deduction)

    # -- autofix -----------------------------------------------------------
    @staticmethod
    def _select_non_overlapping(fixes):
        fixes.sort(key=lambda i: i.start)
        chosen = []
        cursor_end = -1
        for i in fixes:
            if i.start >= cursor_end:
                chosen.append(i)
                cursor_end = i.end
        return chosen

    def fix_text(self, text: str, language: Optional[str] = None):
        """Return ``(fixed_text, applied_count, remaining_result)``.

        Fixes run in rounds (bounded) so chains of overlapping corrections
        converge to a stable result in a single call.
        """
        out = text
        total = 0
        remaining = self.lint_text(out, language=language)
        for _ in range(5):
            fixes = [i for i in remaining.issues
                     if i.autofixable and i.suggestion is not None]
            chosen = self._select_non_overlapping(fixes)
            if not chosen:
                break
            for i in reversed(chosen):
                out = out[:i.start] + (i.suggestion or "") + out[i.end:]
            total += len(chosen)
            remaining = self.lint_text(out, language=language)
        return out, total, remaining
