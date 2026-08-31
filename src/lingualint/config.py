"""Configuration loading and defaults."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

DEFAULT_EXTENSIONS = (".md", ".markdown", ".txt", ".rst", ".text")
DEFAULT_EXCLUDES = (
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".idea",
    ".vscode",
)


@dataclass
class Config:
    """Runtime configuration.

    ``rules`` maps rule ids to ``False`` to disable or a severity string
    to override the default severity.  ``typo_pairs`` adds project-local
    find/replace pairs used by the spelling rules.
    """

    language: str = "auto"  # auto | en | zh
    extensions: List[str] = field(default_factory=lambda: list(DEFAULT_EXTENSIONS))
    exclude: List[str] = field(default_factory=lambda: list(DEFAULT_EXCLUDES))
    rules: Dict[str, Any] = field(default_factory=dict)
    ignore_words: List[str] = field(default_factory=list)
    typo_pairs: Dict[str, str] = field(default_factory=dict)
    zh_latin_spacing: bool = True
    max_line_length: int = 200
    long_zh_sentence: int = 60
    min_score: Optional[int] = None
    fail_severity: str = "warning"
    max_issues: int = 0

    # -- loading -----------------------------------------------------------
    @classmethod
    def from_file(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"unknown config keys: {sorted(unknown)}")
        cfg = cls()
        for key in known & set(data):
            setattr(cfg, key, data[key])
        return cfg

    @classmethod
    def discover(cls, start_dir: str = ".") -> Optional[str]:
        """Find a ``.lingualint.json`` by walking upwards from ``start_dir``."""
        cur = os.path.abspath(start_dir)
        while True:
            candidate = os.path.join(cur, ".lingualint.json")
            if os.path.isfile(candidate):
                return candidate
            parent = os.path.dirname(cur)
            if parent == cur:
                return None
            cur = parent

    # -- rule queries ------------------------------------------------------
    def rule_enabled(self, rule_id: str, default: bool = True) -> bool:
        setting = self.rules.get(rule_id, default)
        return setting is not False

    def rule_severity(self, rule_id: str, default: str) -> str:
        setting = self.rules.get(rule_id, default)
        if isinstance(setting, str) and setting in ("error", "warning", "suggestion", "info"):
            return setting
        return default
