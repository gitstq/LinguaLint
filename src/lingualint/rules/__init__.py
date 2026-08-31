"""Rule registry."""
from __future__ import annotations

from typing import Dict, List, Type

from .base import Rule
from .common import COMMON_RULES
from .english import ENGLISH_RULES
from .chinese import CHINESE_RULES

ALL_RULE_CLASSES: List[Type[Rule]] = COMMON_RULES + ENGLISH_RULES + CHINESE_RULES
RULE_MAP: Dict[str, Type[Rule]] = {r.id: r for r in ALL_RULE_CLASSES}

__all__ = ["Rule", "ALL_RULE_CLASSES", "RULE_MAP",
           "COMMON_RULES", "ENGLISH_RULES", "CHINESE_RULES"]
