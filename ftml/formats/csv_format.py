"""CSV format reader and writer.

CSV format: instruction,input,output columns (Alpaca-style CSV).
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Iterator

from ftml.formats.base import FormatReader, FormatWriter
from ftml.models import ConversationExample, Issue, Severity, Turn


class CSVReader(FormatReader):
    def read(self, path: Path) -> Iterator[ConversationExample]:
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        text = raw.decode("utf-8")

        reader = csv.DictReader(io.StringIO(text))
        for line_num, row in enumerate(reader, 2):
            instruction = row.get("instruction", "").strip()
            input_text = row.get("input", "").strip()
            output_text = row.get("output", "").strip()

            content = instruction
            if input_text:
                content = f"{instruction}\n\n{input_text}"

            turns = [
                Turn(role="user", content=content),
                Turn(role="assistant", content=output_text),
            ]

            yield ConversationExample(
                turns=turns,
                metadata={
                    "source_format": "csv",
                    "line_number": line_num,
                    "source_file": str(path),
                    "alpaca_input": input_text,
                },
            )


class CSVWriter(FormatWriter):
    def write(self, examples: Iterator[ConversationExample], path: Path) -> int:
        count = 0
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["instruction", "input", "output"])
            writer.writeheader()
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

                writer.writerow({
                    "instruction": instruction,
                    "input": alpaca_input,
                    "output": assistant_content,
                })
                count += 1
        return count
