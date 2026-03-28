"""Alpaca format reader and writer.

Alpaca format: JSONL with {"instruction": str, "input": str, "output": str}
Optional "system" field is preserved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from ftml.formats.base import FormatReader, FormatWriter
from ftml.models import ConversationExample, Issue, Severity, Turn


class AlpacaReader(FormatReader):
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

                instruction = data.get("instruction", "")
                input_text = data.get("input", "")
                output_text = data.get("output", "")

                content = instruction
                if input_text:
                    content = f"{instruction}\n\n{input_text}"

                turns = [
                    Turn(role="user", content=content),
                    Turn(role="assistant", content=output_text),
                ]

                yield ConversationExample(
                    system=data.get("system"),
                    turns=turns,
                    metadata={
                        "source_format": "alpaca",
                        "line_number": line_num,
                        "source_file": str(path),
                        "alpaca_input": input_text,
                    },
                )


class AlpacaWriter(FormatWriter):
    def write(self, examples: Iterator[ConversationExample], path: Path) -> int:
        count = 0
        with open(path, "w", encoding="utf-8") as f:
            for example in examples:
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

                record: dict = {
                    "instruction": instruction,
                    "input": alpaca_input,
                    "output": assistant_content,
                }
                if example.system is not None:
                    record["system"] = example.system

                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
        return count
