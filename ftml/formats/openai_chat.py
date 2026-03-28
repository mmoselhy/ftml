"""OpenAI Chat format reader and writer.

OpenAI format: JSONL with {"messages": [{"role": str, "content": str}, ...]}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from ftml.formats.base import FormatReader, FormatWriter
from ftml.models import ConversationExample, Issue, Severity, Turn


class OpenAIChatReader(FormatReader):
    def read(self, path: Path) -> Iterator[ConversationExample]:
        with open(path, encoding="utf-8") as f:
            for line_num, raw_line in enumerate(f, 1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    self.errors.append(
                        Issue(line=line_num, severity=Severity.SKIP, message=f"Malformed JSON: {e}")
                    )
                    continue

                messages = data.get("messages", [])
                system = None
                turns = []

                for msg in messages:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if role == "system":
                        system = content
                    elif role in ("user", "assistant"):
                        turns.append(Turn(role=role, content=content))

                yield ConversationExample(
                    system=system,
                    turns=turns,
                    metadata={
                        "source_format": "openai-chat",
                        "line_number": line_num,
                        "source_file": str(path),
                    },
                )


class OpenAIChatWriter(FormatWriter):
    def write(self, examples: Iterator[ConversationExample], path: Path) -> int:
        count = 0
        with open(path, "w", encoding="utf-8") as f:
            for example in examples:
                messages = []
                if example.system is not None:
                    messages.append({"role": "system", "content": example.system})
                for turn in example.turns:
                    messages.append({"role": turn.role, "content": turn.content})
                f.write(json.dumps({"messages": messages}, ensure_ascii=False) + "\n")
                count += 1
        return count
