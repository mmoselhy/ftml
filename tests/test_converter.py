import json
from pathlib import Path

import pytest

from ftml.converter import convert
from ftml.models import ConvertStats


class TestConvert:
    def test_alpaca_to_openai_chat(self, alpaca_path, tmp_path):
        out = tmp_path / "output.jsonl"
        stats = convert(alpaca_path, out, from_format="alpaca", to_format="openai-chat")
        assert stats.total_read == 5
        assert stats.total_written == 5
        assert out.exists()
        lines = out.read_text().strip().split("\n")
        assert len(lines) == 5
        first = json.loads(lines[0])
        assert "messages" in first

    def test_openai_chat_to_alpaca(self, openai_chat_path, tmp_path):
        out = tmp_path / "output.jsonl"
        stats = convert(openai_chat_path, out, from_format="openai-chat", to_format="alpaca")
        assert stats.total_read == 5
        assert stats.total_written == 5
        first = json.loads(out.read_text().strip().split("\n")[0])
        assert "instruction" in first
        assert "output" in first

    def test_returns_convert_stats(self, alpaca_path, tmp_path):
        out = tmp_path / "output.jsonl"
        stats = convert(alpaca_path, out, from_format="alpaca", to_format="openai-chat")
        assert isinstance(stats, ConvertStats)

    def test_nonexistent_input_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            convert(tmp_path / "nope.jsonl", tmp_path / "out.jsonl", from_format="alpaca", to_format="openai-chat")

    def test_unknown_format_raises(self, alpaca_path, tmp_path):
        with pytest.raises(ValueError, match="Unknown input format"):
            convert(alpaca_path, tmp_path / "out.jsonl", from_format="nonexistent", to_format="openai-chat")

    def test_dry_run_does_not_write(self, alpaca_path, tmp_path):
        out = tmp_path / "output.jsonl"
        stats = convert(alpaca_path, out, from_format="alpaca", to_format="openai-chat", dry_run=True)
        assert stats.total_read == 5
        assert stats.total_written == 0
        assert not out.exists()
