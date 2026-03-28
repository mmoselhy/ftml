"""Platform rules dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlatformRules:
    name: str
    accepted_formats: list[str]
    min_examples: int = 1
    max_tokens_warn: int | None = None
    max_tokens_error: int | None = None
    require_user_turn: bool = True
    require_assistant_turn: bool = True
    require_system: bool = False
    warn_no_system: bool = False
    notes: str = ""
