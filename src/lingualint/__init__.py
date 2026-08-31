"""LinguaLint — offline, zero-dependency bilingual (EN/ZH) writing linter.

Public API
----------
>>> from lingualint import Linter, Config
>>> result = Linter(Config()).lint_text("This is is wrong.")
>>> result.score
"""
from __future__ import annotations

from .config import Config
from .engine import Linter, LintResult
from .issues import Issue

__version__ = "1.0.0"
__all__ = ["Linter", "LintResult", "Config", "Issue", "__version__"]
