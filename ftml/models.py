"""Core data models for ftml's internal representation."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


VALID_ROLES = ("user", "assistant")


class Turn(BaseModel):
    """A single turn in a conversation."""

    role: Literal["user", "assistant"]
    content: str


class ConversationExample(BaseModel):
    """Internal representation of a single training example."""

    system: Optional[str] = None
    turns: list[Turn] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class Severity(str, Enum):
    """Severity level for validation issues and fix actions."""

    ERROR = "error"
    WARNING = "warning"
    FIX = "fix"
    SKIP = "skip"


class Issue(BaseModel):
    """A single validation issue, fix action, or skip event."""

    line: int
    severity: Severity
    message: str


class ValidationResult(BaseModel):
    """Result of a single validation check."""

    check_name: str
    passed: bool
    count: int = 0
    issues: list[Issue] = Field(default_factory=list)


class ConvertStats(BaseModel):
    """Statistics from a conversion run."""

    total_read: int = 0
    total_written: int = 0
    total_skipped: int = 0
    fixes_applied: int = 0
    issues: list[Issue] = Field(default_factory=list)
