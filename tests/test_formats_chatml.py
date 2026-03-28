import json
from pathlib import Path

import pytest

from ftml.formats.chatml import ChatMLReader, ChatMLWriter
from ftml.models import ConversationExample, Turn


class TestChatMLReader:
    def test_read_jsonl_format(self, chatml_path):
        reader = ChatMLReader()
        examples = list(reader.read(chatml_path))
        assert len(examples) == 5

    def test_parses_roles_correctly(self, chatml_path):
        reader = ChatMLReader()
        ex = next(iter(reader.read(chatml_path)))
        assert ex.turns[0].role == "user"
        assert ex.turns[1].role == "assistant"

    def test_system_message(self, chatml_path):
        reader = ChatMLReader()
        examples = list(reader.read(chatml_path))
        ex = examples[1]
        assert ex.system == "You are a helpful translator."

    def test_plain_text_format(self, tmp_path):
        path = tmp_path / "plain.txt"
        path.write_text(
            "<|im_start|>user\nHello<|im_end|>\n"
            "<|im_start|>assistant\nHi there<|im_end|>\n"
        )
        reader = ChatMLReader()
        examples = list(reader.read(path))
        assert len(examples) == 1
        assert examples[0].turns[0].content == "Hello"
        assert examples[0].turns[1].content == "Hi there"

    def test_plain_text_multiple_conversations(self, tmp_path):
        path = tmp_path / "multi.txt"
        path.write_text(
            "<|im_start|>user\nFirst<|im_end|>\n"
            "<|im_start|>assistant\nResponse1<|im_end|>\n"
            "\n"
            "<|im_start|>user\nSecond<|im_end|>\n"
            "<|im_start|>assistant\nResponse2<|im_end|>\n"
        )
        reader = ChatMLReader()
        examples = list(reader.read(path))
        assert len(examples) == 2


class TestChatMLWriter:
    def test_write_jsonl(self, tmp_path):
        examples = [
            ConversationExample(
                turns=[Turn(role="user", content="Hi"), Turn(role="assistant", content="Hello")],
            ),
        ]
        out = tmp_path / "out.jsonl"
        writer = ChatMLWriter()
        count = writer.write(iter(examples), out)
        assert count == 1
        data = json.loads(out.read_text().strip())
        text = data["text"]
        assert "<|im_start|>user\nHi<|im_end|>" in text
        assert "<|im_start|>assistant\nHello<|im_end|>" in text

    def test_write_with_system(self, tmp_path):
        examples = [
            ConversationExample(
                system="Be helpful.",
                turns=[Turn(role="user", content="Hi"), Turn(role="assistant", content="Hey")],
            ),
        ]
        out = tmp_path / "out.jsonl"
        writer = ChatMLWriter()
        writer.write(iter(examples), out)
        data = json.loads(out.read_text().strip())
        assert "<|im_start|>system\nBe helpful.<|im_end|>" in data["text"]

    def test_roundtrip_jsonl(self, chatml_path, tmp_path):
        reader = ChatMLReader()
        originals = list(reader.read(chatml_path))
        out = tmp_path / "rt.jsonl"
        writer = ChatMLWriter()
        writer.write(iter(originals), out)
        reader2 = ChatMLReader()
        roundtripped = list(reader2.read(out))
        assert len(originals) == len(roundtripped)
        for orig, rt in zip(originals, roundtripped):
            assert orig.system == rt.system
            assert len(orig.turns) == len(rt.turns)
