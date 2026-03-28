"""Abstract base classes for format readers and writers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator

from ftml.models import ConversationExample, Issue


class FormatReader(ABC):
    """Reads a dataset file and yields ConversationExample objects."""

    def __init__(self) -> None:
        self.errors: list[Issue] = []

    @abstractmethod
    def read(self, path: Path) -> Iterator[ConversationExample]:
        """Yield examples one at a time.

        Unparseable lines should be appended to self.errors and skipped.
        Each yielded example must have 'line_number' and 'source_format' in metadata.
        """
        ...


class FormatWriter(ABC):
    """Writes ConversationExample objects to a dataset file."""

    @abstractmethod
    def write(self, examples: Iterator[ConversationExample], path: Path) -> int:
        """Write examples to the output file. Returns the number of examples written."""
        ...
