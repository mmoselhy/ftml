import json
from pathlib import Path

import pytest

from ftml.formats.alpaca import AlpacaReader, AlpacaWriter
from ftml.models import ConversationExample, Turn


class TestAlpacaReader:
    def test_read_basic_examples(self, alpaca_path):
        reader = AlpacaReader()
        examples = list(reader.read(alpaca_path))
        assert len(examples) == 5

    def test_first_example_structure(self, alpaca_path):
        reader = AlpacaReader()
        ex = next(iter(reader.read(alpaca_path)))
        assert ex.system is None
        assert len(ex.turns) == 2
        assert ex.turns[0].role == "user"
        assert ex.turns[0].content == "What is the capital of France?"
        assert ex.turns[1].role == "assistant"
        assert ex.turns[1].content == "The capital of France is Paris."

    def test_example_with_input_field(self, alpaca_path):
        reader = AlpacaReader()
        examples = list(reader.read(alpaca_path))
        ex = examples[1]  # Second example has input="Hello, how are you?"
        assert "Hello, how are you?" in ex.turns[0].content
        assert "Translate the following to Spanish." in ex.turns[0].content
        assert ex.metadata["alpaca_input"] == "Hello, how are you?"

    def test_metadata_has_line_number(self, alpaca_path):
        reader = AlpacaReader()
        examples = list(reader.read(alpaca_path))
        assert examples[0].metadata["line_number"] == 1
        assert examples[1].metadata["line_number"] == 2

    def test_metadata_has_source_format(self, alpaca_path):
        reader = AlpacaReader()
        ex = next(iter(reader.read(alpaca_path)))
        assert ex.metadata["source_format"] == "alpaca"

    def test_malformed_json_skipped(self, tmp_path):
        path = tmp_path / "bad.jsonl"
        path.write_text(
            '{"instruction": "Good", "input": "", "output": "Fine"}\n'
            "not valid json\n"
            '{"instruction": "Also good", "input": "", "output": "OK"}\n'
        )
        reader = AlpacaReader()
        examples = list(reader.read(path))
        assert len(examples) == 2
        assert len(reader.errors) == 1
        assert reader.errors[0].line == 2

    def test_empty_file(self, tmp_path):
        path = tmp_path / "empty.jsonl"
        path.write_text("")
        reader = AlpacaReader()
        examples = list(reader.read(path))
        assert len(examples) == 0

    def test_blank_lines_skipped(self, tmp_path):
        path = tmp_path / "blanks.jsonl"
        path.write_text(
            '{"instruction": "Hi", "input": "", "output": "Hello"}\n'
            "\n"
            "\n"
            '{"instruction": "Bye", "input": "", "output": "Goodbye"}\n'
        )
        reader = AlpacaReader()
        examples = list(reader.read(path))
        assert len(examples) == 2


class TestAlpacaWriter:
    def test_write_basic(self, tmp_path):
        examples = [
            ConversationExample(
                turns=[
                    Turn(role="user", content="Hi"),
                    Turn(role="assistant", content="Hello"),
                ],
            ),
        ]
        out = tmp_path / "out.jsonl"
        writer = AlpacaWriter()
        count = writer.write(iter(examples), out)
        assert count == 1
        data = json.loads(out.read_text().strip())
        assert data["instruction"] == "Hi"
        assert data["input"] == ""
        assert data["output"] == "Hello"

    def test_write_preserves_system(self, tmp_path):
        examples = [
            ConversationExample(
                system="Be helpful.",
                turns=[
                    Turn(role="user", content="Hi"),
                    Turn(role="assistant", content="Hello"),
                ],
            ),
        ]
        out = tmp_path / "out.jsonl"
        writer = AlpacaWriter()
        writer.write(iter(examples), out)
        data = json.loads(out.read_text().strip())
        assert data.get("system") == "Be helpful."

    def test_write_restores_input_from_metadata(self, tmp_path):
        examples = [
            ConversationExample(
                turns=[
                    Turn(role="user", content="Translate.\n\nHello"),
                    Turn(role="assistant", content="Hola"),
                ],
                metadata={"alpaca_input": "Hello"},
            ),
        ]
        out = tmp_path / "out.jsonl"
        writer = AlpacaWriter()
        writer.write(iter(examples), out)
        data = json.loads(out.read_text().strip())
        assert data["instruction"] == "Translate."
        assert data["input"] == "Hello"

    def test_roundtrip_preserves_content(self, alpaca_path, tmp_path):
        reader = AlpacaReader()
        originals = list(reader.read(alpaca_path))
        out = tmp_path / "roundtrip.jsonl"
        writer = AlpacaWriter()
        writer.write(iter(originals), out)
        reader2 = AlpacaReader()
        roundtripped = list(reader2.read(out))
        assert len(originals) == len(roundtripped)
        for orig, rt in zip(originals, roundtripped):
            assert orig.turns[0].content == rt.turns[0].content
            assert orig.turns[1].content == rt.turns[1].content
            assert orig.system == rt.system
