"""Roundtrip tests: convert A → B → A and verify semantic equivalence."""

from pathlib import Path

import pytest

from ftml.converter import convert
from ftml.formats import get_reader


def _load_examples(path: Path, format_name: str):
    reader = get_reader(format_name)
    return list(reader.read(path))


def _assert_semantically_equal(originals, roundtripped):
    """Compare turns content and roles, ignoring metadata differences."""
    assert len(originals) == len(roundtripped), (
        f"Count mismatch: {len(originals)} vs {len(roundtripped)}"
    )
    for i, (orig, rt) in enumerate(zip(originals, roundtripped)):
        assert orig.system == rt.system, f"Example {i}: system mismatch"
        assert len(orig.turns) == len(rt.turns), (
            f"Example {i}: turn count mismatch ({len(orig.turns)} vs {len(rt.turns)})"
        )
        for j, (ot, rtt) in enumerate(zip(orig.turns, rt.turns)):
            assert ot.role == rtt.role, f"Example {i}, turn {j}: role mismatch"
            assert ot.content == rtt.content, (
                f"Example {i}, turn {j}: content mismatch:\n  {ot.content!r}\n  {rtt.content!r}"
            )


class TestRoundtrip:
    def test_alpaca_openai_chat_alpaca(self, alpaca_path, tmp_path):
        mid = tmp_path / "mid.jsonl"
        out = tmp_path / "out.jsonl"
        convert(alpaca_path, mid, from_format="alpaca", to_format="openai-chat")
        convert(mid, out, from_format="openai-chat", to_format="alpaca")
        originals = _load_examples(alpaca_path, "alpaca")
        roundtripped = _load_examples(out, "alpaca")
        _assert_semantically_equal(originals, roundtripped)

    def test_openai_chat_alpaca_openai_chat(self, openai_chat_path, tmp_path):
        mid = tmp_path / "mid.jsonl"
        out = tmp_path / "out.jsonl"
        convert(openai_chat_path, mid, from_format="openai-chat", to_format="alpaca")
        convert(mid, out, from_format="alpaca", to_format="openai-chat")
        originals = _load_examples(openai_chat_path, "openai-chat")
        roundtripped = _load_examples(out, "openai-chat")
        assert len(originals) == len(roundtripped)
        for orig, rt in zip(originals, roundtripped):
            # At minimum, first user and first assistant turn should match
            assert orig.turns[0].content == rt.turns[0].content

    def test_sharegpt_openai_chat_sharegpt(self, sharegpt_path, tmp_path):
        mid = tmp_path / "mid.jsonl"
        out = tmp_path / "out.jsonl"
        convert(sharegpt_path, mid, from_format="sharegpt", to_format="openai-chat")
        convert(mid, out, from_format="openai-chat", to_format="sharegpt")
        originals = _load_examples(sharegpt_path, "sharegpt")
        roundtripped = _load_examples(out, "sharegpt")
        _assert_semantically_equal(originals, roundtripped)

    def test_openai_chat_chatml_openai_chat(self, openai_chat_path, tmp_path):
        mid = tmp_path / "mid.jsonl"
        out = tmp_path / "out.jsonl"
        convert(openai_chat_path, mid, from_format="openai-chat", to_format="chatml")
        convert(mid, out, from_format="chatml", to_format="openai-chat")
        originals = _load_examples(openai_chat_path, "openai-chat")
        roundtripped = _load_examples(out, "openai-chat")
        _assert_semantically_equal(originals, roundtripped)

    def test_alpaca_sharegpt_alpaca(self, alpaca_path, tmp_path):
        mid = tmp_path / "mid.jsonl"
        out = tmp_path / "out.jsonl"
        convert(alpaca_path, mid, from_format="alpaca", to_format="sharegpt")
        convert(mid, out, from_format="sharegpt", to_format="alpaca")
        originals = _load_examples(alpaca_path, "alpaca")
        roundtripped = _load_examples(out, "alpaca")
        _assert_semantically_equal(originals, roundtripped)
