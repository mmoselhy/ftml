"""ShareGPT format reader and writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from ftml.formats.base import FormatReader, FormatWriter
from ftml.models import ConversationExample, Issue, Severity, Turn

_ROLE_TO_CANONICAL = {
    "human": "user",
    "user": "user",
    "prompter": "user",
    "gpt": "assistant",
    "assistant": "assistant",
    "bot": "assistant",
}

_CANONICAL_TO_SHAREGPT = {
    "user": "human",
    "assistant": "gpt",
}


class ShareGPTReader(FormatReader):
    def read(self, path: Path) -> Iterator[ConversationExample]:
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

                conversations = data.get("conversations", [])
                system = None
                turns = []
                for msg in conversations:
                    from_role = msg.get("from", "")
                    value = msg.get("value", "")
                    if from_role == "system":
                        system = value
                        continue
                    canonical = _ROLE_TO_CANONICAL.get(from_role)
                    if canonical is None:
                        self.errors.append(Issue(line=line_num, severity=Severity.WARNING, message=f"Unknown role: {from_role!r}"))
                        continue
                    turns.append(Turn(role=canonical, content=value))

                yield ConversationExample(
                    system=system, turns=turns,
                    metadata={"source_format": "sharegpt", "line_number": line_num, "source_file": str(path)},
                )


class ShareGPTWriter(FormatWriter):
    def write(self, examples: Iterator[ConversationExample], path: Path) -> int:
        count = 0
        with open(path, "w", encoding="utf-8") as f:
            for example in examples:
                conversations = []
                if example.system is not None:
                    conversations.append({"from": "system", "value": example.system})
                for turn in example.turns:
                    sharegpt_role = _CANONICAL_TO_SHAREGPT.get(turn.role, turn.role)
                    conversations.append({"from": sharegpt_role, "value": turn.content})
                f.write(json.dumps({"conversations": conversations}, ensure_ascii=False) + "\n")
                count += 1
        return count
