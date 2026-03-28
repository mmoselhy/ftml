import json
from pathlib import Path

import pytest

from ftml.formats.openai_chat import OpenAIChatReader, OpenAIChatWriter
from ftml.models import ConversationExample, Turn


class TestOpenAIChatReader:
    def test_read_basic_examples(self, openai_chat_path):
        reader = OpenAIChatReader()
        examples = list(reader.read(openai_chat_path))
        assert len(examples) == 5

    def test_example_without_system(self, openai_chat_path):
        reader = OpenAIChatReader()
        ex = next(iter(reader.read(openai_chat_path)))
        assert ex.system is None
        assert len(ex.turns) == 2
        assert ex.turns[0].role == "user"
        assert ex.turns[1].role == "assistant"

    def test_example_with_system(self, openai_chat_path):
        reader = OpenAIChatReader()
        examples = list(reader.read(openai_chat_path))
        ex = examples[1]
        assert ex.system == "You are a helpful translator."
        assert len(ex.turns) == 2
        assert ex.turns[0].role == "user"

    def test_metadata(self, openai_chat_path):
        reader = OpenAIChatReader()
        ex = next(iter(reader.read(openai_chat_path)))
        assert ex.metadata["source_format"] == "openai-chat"
        assert ex.metadata["line_number"] == 1

    def test_malformed_json_skipped(self, tmp_path):
        path = tmp_path / "bad.jsonl"
        path.write_text(
            '{"messages": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hey"}]}\n'
            "broken json line\n"
        )
        reader = OpenAIChatReader()
        examples = list(reader.read(path))
        assert len(examples) == 1
        assert len(reader.errors) == 1


class TestOpenAIChatWriter:
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
        writer = OpenAIChatWriter()
        count = writer.write(iter(examples), out)
        assert count == 1
        data = json.loads(out.read_text().strip())
        assert len(data["messages"]) == 2
        assert data["messages"][0] == {"role": "user", "content": "Hi"}
        assert data["messages"][1] == {"role": "assistant", "content": "Hello"}

    def test_write_with_system(self, tmp_path):
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
        writer = OpenAIChatWriter()
        writer.write(iter(examples), out)
        data = json.loads(out.read_text().strip())
        assert data["messages"][0] == {"role": "system", "content": "Be helpful."}
        assert len(data["messages"]) == 3

    def test_roundtrip(self, openai_chat_path, tmp_path):
        reader = OpenAIChatReader()
        originals = list(reader.read(openai_chat_path))
        out = tmp_path / "roundtrip.jsonl"
        writer = OpenAIChatWriter()
        writer.write(iter(originals), out)
        reader2 = OpenAIChatReader()
        roundtripped = list(reader2.read(out))
        assert len(originals) == len(roundtripped)
        for orig, rt in zip(originals, roundtripped):
            assert orig.system == rt.system
            assert len(orig.turns) == len(rt.turns)
            for ot, rtt in zip(orig.turns, rt.turns):
                assert ot.role == rtt.role
                assert ot.content == rtt.content
