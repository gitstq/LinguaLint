"""Issue data model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

SEVERITIES = ("error", "warning", "suggestion", "info")
SEVERITY_WEIGHT = {"error": 10, "warning": 4, "suggestion": 1, "info": 0}
SEVERITY_ORDER = {"error": 0, "warning": 1, "suggestion": 2, "info": 3}


@dataclass
class Issue:
    """A single finding.

    Positions are character offsets into the source text.  Line/column are
    attached later by :class:`lingualint.engine.LintResult`.
    """

    rule_id: str
    start: int
    end: int
    message: str
    severity: str = "warning"
    category: str = "general"
    suggestion: Optional[str] = None
    autofixable: bool = False
    line: int = 0
    col: int = 0
    source: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"unknown severity: {self.severity}")
        if self.end < self.start:
            raise ValueError("issue end offset before start offset")
