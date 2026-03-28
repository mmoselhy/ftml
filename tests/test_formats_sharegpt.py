import json
from pathlib import Path

import pytest

from ftml.formats.sharegpt import ShareGPTReader, ShareGPTWriter
from ftml.models import ConversationExample, Turn


class TestShareGPTReader:
    def test_read_basic(self, sharegpt_path):
        reader = ShareGPTReader()
        examples = list(reader.read(sharegpt_path))
        assert len(examples) == 5

    def test_role_normalization(self, sharegpt_path):
        reader = ShareGPTReader()
        ex = next(iter(reader.read(sharegpt_path)))
        assert ex.turns[0].role == "user"
        assert ex.turns[1].role == "assistant"

    def test_system_message_extracted(self, sharegpt_path):
        reader = ShareGPTReader()
        examples = list(reader.read(sharegpt_path))
        ex = examples[1]
        assert ex.system == "You are a helpful translator."
        assert ex.turns[0].role == "user"

    def test_multi_turn(self, sharegpt_path):
        reader = ShareGPTReader()
        examples = list(reader.read(sharegpt_path))
        ex = examples[2]
        assert len(ex.turns) == 4

    def test_metadata(self, sharegpt_path):
        reader = ShareGPTReader()
        ex = next(iter(reader.read(sharegpt_path)))
        assert ex.metadata["source_format"] == "sharegpt"


class TestShareGPTWriter:
    def test_write_basic(self, tmp_path):
        examples = [
            ConversationExample(
                turns=[Turn(role="user", content="Hi"), Turn(role="assistant", content="Hello")],
            ),
        ]
        out = tmp_path / "out.jsonl"
        writer = ShareGPTWriter()
        count = writer.write(iter(examples), out)
        assert count == 1
        data = json.loads(out.read_text().strip())
        assert data["conversations"][0] == {"from": "human", "value": "Hi"}
        assert data["conversations"][1] == {"from": "gpt", "value": "Hello"}

    def test_write_with_system(self, tmp_path):
        examples = [
            ConversationExample(
                system="Be helpful.",
                turns=[Turn(role="user", content="Hi"), Turn(role="assistant", content="Hey")],
            ),
        ]
        out = tmp_path / "out.jsonl"
        writer = ShareGPTWriter()
        writer.write(iter(examples), out)
        data = json.loads(out.read_text().strip())
        assert data["conversations"][0] == {"from": "system", "value": "Be helpful."}

    def test_roundtrip(self, sharegpt_path, tmp_path):
        reader = ShareGPTReader()
        originals = list(reader.read(sharegpt_path))
        out = tmp_path / "rt.jsonl"
        writer = ShareGPTWriter()
        writer.write(iter(originals), out)
        reader2 = ShareGPTReader()
        roundtripped = list(reader2.read(out))
        for orig, rt in zip(originals, roundtripped):
            assert orig.system == rt.system
            assert len(orig.turns) == len(rt.turns)
            for ot, rtt in zip(orig.turns, rt.turns):
                assert ot.content == rtt.content
