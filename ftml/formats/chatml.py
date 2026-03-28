"""ChatML format reader and writer.

Supports two sub-formats:
- JSONL with {"text": "<|im_start|>role\ncontent<|im_end|>\n..."}
- Plain text with ChatML tokens (conversations separated by blank lines)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterator

from ftml.formats.base import FormatReader, FormatWriter
from ftml.models import ConversationExample, Issue, Severity, Turn

_TURN_PATTERN = re.compile(
    r"<\|im_start\|>(\w+)\n(.*?)<\|im_end\|>",
    re.DOTALL,
)


def _parse_chatml_text(text: str) -> ConversationExample:
    """Parse a ChatML-formatted string into a ConversationExample."""
    system = None
    turns = []
    for match in _TURN_PATTERN.finditer(text):
        role = match.group(1)
        content = match.group(2).strip()
        if role == "system":
            system = content
        elif role in ("user", "assistant"):
            turns.append(Turn(role=role, content=content))
    return ConversationExample(system=system, turns=turns)


class ChatMLReader(FormatReader):
    def read(self, path: Path) -> Iterator[ConversationExample]:
        raw = path.read_bytes()
        stripped = raw.lstrip()
        if stripped and stripped[0:1] == b"{":
            yield from self._read_jsonl(path)
        else:
            yield from self._read_plain_text(path)

    def _read_jsonl(self, path: Path) -> Iterator[ConversationExample]:
        with open(path, encoding="utf-8") as f:
            for line_num, raw_line in enumerate(f, 1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    self.errors.append(Issue(line=line_num, severity=Severity.SKIP, message=f"Malformed JSON: {e}"))
                    continue
                text = data.get("text", "")
                example = _parse_chatml_text(text)
                example.metadata.update({
                    "source_format": "chatml", "line_number": line_num, "source_file": str(path),
                })
                yield example

    def _read_plain_text(self, path: Path) -> Iterator[ConversationExample]:
        content = path.read_text(encoding="utf-8")
        chunks = re.split(r"\n\s*\n", content)
        for idx, chunk in enumerate(chunks, 1):
            chunk = chunk.strip()
            if not chunk or "<|im_start|>" not in chunk:
                continue
            example = _parse_chatml_text(chunk)
            example.metadata.update({
                "source_format": "chatml", "line_number": idx, "source_file": str(path),
            })
            yield example


def _render_chatml(example: ConversationExample) -> str:
    """Render a ConversationExample as a ChatML string."""
    parts = []
    if example.system is not None:
        parts.append(f"<|im_start|>system\n{example.system}<|im_end|>")
    for turn in example.turns:
        parts.append(f"<|im_start|>{turn.role}\n{turn.content}<|im_end|>")
    return "\n".join(parts)


class ChatMLWriter(FormatWriter):
    def write(self, examples: Iterator[ConversationExample], path: Path) -> int:
        count = 0
        with open(path, "w", encoding="utf-8") as f:
            for example in examples:
                text = _render_chatml(example)
                f.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")
                count += 1
        return count
