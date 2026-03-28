import pytest

from ftml.stats import compute_stats, DatasetStats


class TestComputeStats:
    def test_basic_stats(self, alpaca_path):
        stats = compute_stats(alpaca_path, format_name="alpaca")
        assert stats.total_examples == 5
        assert stats.min_tokens > 0
        assert stats.max_tokens >= stats.min_tokens
        assert stats.mean_tokens > 0
        assert stats.median_tokens > 0

    def test_system_prompt_percentage(self, openai_chat_path):
        stats = compute_stats(openai_chat_path, format_name="openai-chat")
        # 2 out of 5 examples have system prompts
        assert stats.pct_with_system == pytest.approx(40.0)

    def test_multiturn_percentage(self, sharegpt_path):
        stats = compute_stats(sharegpt_path, format_name="sharegpt")
        # 1 out of 5 has more than 2 turns
        assert stats.pct_multiturn > 0

    def test_turn_distribution(self, sharegpt_path):
        stats = compute_stats(sharegpt_path, format_name="sharegpt")
        assert stats.turn_distribution  # non-empty dict

    def test_token_histogram(self, alpaca_path):
        stats = compute_stats(alpaca_path, format_name="alpaca")
        assert stats.token_histogram  # non-empty list of (label, pct) tuples
