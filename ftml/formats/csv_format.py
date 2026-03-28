"""CSV format reader and writer.

CSV format: instruction,input,output columns (Alpaca-style CSV).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from ftml.formats.base import FormatReader, FormatWriter, extract_alpaca_fields
from ftml.models import ConversationExample, Issue, Severity, Turn


class CSVReader(FormatReader):
    def read(self, path: Path) -> Iterator[ConversationExample]:
        # utf-8-sig handles BOM transparently
        f = open(path, encoding="utf-8-sig", newline="")
        reader = csv.DictReader(f)
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
                instruction, alpaca_input, assistant_content = extract_alpaca_fields(example)
                writer.writerow({
                    "instruction": instruction,
                    "input": alpaca_input,
                    "output": assistant_content,
                })
                count += 1
        return count
