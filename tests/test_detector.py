from pathlib import Path

import pytest

from ftml.detector import detect_format, DetectionResult


class TestDetectFormat:
    def test_detect_alpaca(self, alpaca_path):
        result = detect_format(alpaca_path)
        assert result.format_name == "alpaca"
        assert result.confidence >= 0.8

    def test_detect_openai_chat(self, openai_chat_path):
        result = detect_format(openai_chat_path)
        assert result.format_name == "openai-chat"
        assert result.confidence >= 0.8

    def test_detect_sharegpt(self, sharegpt_path):
        result = detect_format(sharegpt_path)
        assert result.format_name == "sharegpt"
        assert result.confidence >= 0.8

    def test_detect_chatml(self, chatml_path):
        result = detect_format(chatml_path)
        assert result.format_name == "chatml"
        assert result.confidence >= 0.8

    def test_detect_csv(self, csv_path):
        result = detect_format(csv_path)
        assert result.format_name == "csv"
        assert result.confidence >= 0.8

    def test_detect_chatml_plain_text(self, tmp_path):
        path = tmp_path / "plain.txt"
        path.write_text("<|im_start|>user\nHi<|im_end|>\n<|im_start|>assistant\nHey<|im_end|>\n")
        result = detect_format(path)
        assert result.format_name == "chatml"

    def test_empty_file_raises(self, tmp_path):
        path = tmp_path / "empty.jsonl"
        path.write_text("")
        with pytest.raises(ValueError, match="empty"):
            detect_format(path)

    def test_result_has_evidence(self, alpaca_path):
        result = detect_format(alpaca_path)
        assert result.evidence
