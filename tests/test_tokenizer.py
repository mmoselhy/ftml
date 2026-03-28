import pytest

from ftml.tokenizer import count_tokens, get_token_counter
from ftml.models import ConversationExample, Turn


class TestTokenCounter:
    def test_cl100k_base(self):
        counter = get_token_counter("cl100k_base")
        count = counter("Hello, world!")
        assert isinstance(count, int)
        assert count > 0

    def test_heuristic_fallback(self):
        counter = get_token_counter("llama3")
        count = counter("Hello, world!")
        assert isinstance(count, int)
        assert count > 0

    def test_count_tokens_on_example(self):
        ex = ConversationExample(
            system="You are helpful.",
            turns=[
                Turn(role="user", content="Hello"),
                Turn(role="assistant", content="Hi there!"),
            ],
        )
        count = count_tokens(ex, model="cl100k_base")
        assert count > 0

    def test_empty_content(self):
        counter = get_token_counter("cl100k_base")
        assert counter("") == 0
