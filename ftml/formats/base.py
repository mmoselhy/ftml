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


def extract_alpaca_fields(example: ConversationExample) -> tuple[str, str, str]:
    """Extract instruction, input, output from a ConversationExample.

    Used by AlpacaWriter and CSVWriter to avoid duplicated reconstruction logic.
    Reconstructs the original instruction/input split from metadata["alpaca_input"].
    """
    user_content = ""
    assistant_content = ""
    for turn in example.turns:
        if turn.role == "user" and not user_content:
            user_content = turn.content
        elif turn.role == "assistant" and not assistant_content:
            assistant_content = turn.content

    alpaca_input = example.metadata.get("alpaca_input", "")
    instruction = user_content
    if alpaca_input and instruction.endswith(f"\n\n{alpaca_input}"):
        instruction = instruction[: -(len(alpaca_input) + 2)]

    return instruction, alpaca_input, assistant_content
