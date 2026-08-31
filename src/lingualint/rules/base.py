"""Rule base class and document model passed to rules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from ..config import Config
from ..issues import Issue
from ..textutils import Range, line_starts, protected_ranges


@dataclass
class Document:
    text: str
    language: str  # detected/forced document language: en | zh
    starts: List[int]
    protected: List[Range]

    @classmethod
    def build(cls, text: str, language: str) -> "Document":
        return cls(text=text, language=language, starts=line_starts(text),
                   protected=protected_ranges(text))

    def is_protected(self, offset: int) -> bool:
        for r in self.protected:
            if r.start <= offset < r.end:
                return True
            if r.start > offset:
                break
        return False

    def protected_at_span(self, start: int, end: int) -> bool:
        for r in self.protected:
            if r.overlaps(start, end):
                return True
            if r.start >= end:
                break
        return False


class Rule:
    """Base class for all lint rules."""

    id: str = ""
    category: str = "general"
    severity: str = "warning"
    languages: Tuple[str, ...] = ("en", "zh")  # run on these doc languages
    autofixable: bool = False
    title: str = ""
    description: str = ""

    def __init__(self, config: Config) -> None:
        self.config = config

    def effective_severity(self) -> str:
        return self.config.rule_severity(self.id, self.severity)

    def make_issue(self, start: int, end: int, message: str,
                   suggestion: Optional[str] = None,
                   severity: Optional[str] = None,
                   autofixable: Optional[bool] = None) -> Issue:
        return Issue(
            rule_id=self.id,
            start=start,
            end=end,
            message=message,
            severity=severity or self.effective_severity(),
            category=self.category,
            suggestion=suggestion,
            autofixable=self.autofixable if autofixable is None else autofixable,
        )

    def check(self, doc: Document) -> Iterable[Issue]:  # pragma: no cover
        raise NotImplementedError
