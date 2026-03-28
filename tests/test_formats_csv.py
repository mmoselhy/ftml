import json
from pathlib import Path

import pytest

from ftml.formats.csv_format import CSVReader, CSVWriter
from ftml.models import ConversationExample, Turn


class TestCSVReader:
    def test_read_basic(self, csv_path):
        reader = CSVReader()
        examples = list(reader.read(csv_path))
        assert len(examples) == 5

    def test_structure(self, csv_path):
        reader = CSVReader()
        ex = next(iter(reader.read(csv_path)))
        assert ex.turns[0].role == "user"
        assert ex.turns[1].role == "assistant"
        assert "capital of France" in ex.turns[0].content

    def test_input_in_metadata(self, csv_path):
        reader = CSVReader()
        examples = list(reader.read(csv_path))
        ex = examples[1]
        assert ex.metadata.get("alpaca_input") == "Hello, how are you?"

    def test_empty_input_field(self, csv_path):
        reader = CSVReader()
        ex = next(iter(reader.read(csv_path)))
        assert ex.metadata.get("alpaca_input") == ""

    def test_handles_utf8_bom(self, tmp_path):
        path = tmp_path / "bom.csv"
        path.write_bytes(b"\xef\xbb\xbf" + b"instruction,input,output\nHi,,Hello\n")
        reader = CSVReader()
        examples = list(reader.read(path))
        assert len(examples) == 1
        assert examples[0].turns[0].content == "Hi"


class TestCSVWriter:
    def test_write_basic(self, tmp_path):
        examples = [
            ConversationExample(
                turns=[Turn(role="user", content="Hi"), Turn(role="assistant", content="Hello")],
            ),
        ]
        out = tmp_path / "out.csv"
        writer = CSVWriter()
        count = writer.write(iter(examples), out)
        assert count == 1
        lines = out.read_text().strip().split("\n")
        assert lines[0] == "instruction,input,output"
        assert "Hi" in lines[1]
        assert "Hello" in lines[1]
