"""Token counting wrapper.

Uses tiktoken for OpenAI-compatible encodings, character-based heuristic for others.
"""

from __future__ import annotations

from typing import Callable

import tiktoken

from ftml.models import ConversationExample

_ENCODERS: dict[str, tiktoken.Encoding] = {}
_TIKTOKEN_ENCODINGS = {"cl100k_base", "o200k_base", "p50k_base", "r50k_base"}


def get_token_counter(model: str = "cl100k_base") -> Callable[[str], int]:
    """Return a token counting function for the given model/encoding."""
    if model in _TIKTOKEN_ENCODINGS:
        if model not in _ENCODERS:
            _ENCODERS[model] = tiktoken.get_encoding(model)
        enc = _ENCODERS[model]
        return lambda text: len(enc.encode(text))
    return lambda text: int(len(text) / 3.5) if text else 0


def count_tokens(example: ConversationExample, model: str = "cl100k_base") -> int:
    """Count tokens for a full conversation example."""
    counter = get_token_counter(model)
    total = 0
    if example.system:
        total += counter(example.system)
    for turn in example.turns:
        total += counter(turn.content)
    return total
