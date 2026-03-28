import pytest

from ftml.models import ConversationExample, Turn, ValidationResult
from ftml.validator import validate_example, validate_dataset


class TestValidateExample:
    def test_valid_example_passes(self):
        ex = ConversationExample(
            turns=[Turn(role="user", content="Hi"), Turn(role="assistant", content="Hello")],
        )
        results = validate_example(ex)
        assert all(r.passed for r in results)

    def test_empty_content_fails(self):
        ex = ConversationExample(
            turns=[Turn(role="user", content=""), Turn(role="assistant", content="OK")],
        )
        results = validate_example(ex)
        failed = [r for r in results if not r.passed and "empty content" in r.check_name.lower()]
        assert len(failed) > 0

    def test_no_user_turn_fails(self):
        ex = ConversationExample(
            turns=[Turn(role="assistant", content="Unsolicited")],
        )
        results = validate_example(ex)
        failed = [r for r in results if not r.passed]
        assert len(failed) > 0

    def test_no_assistant_turn_fails(self):
        ex = ConversationExample(
            turns=[Turn(role="user", content="Question?")],
        )
        results = validate_example(ex)
        failed = [r for r in results if not r.passed]
        assert len(failed) > 0


class TestPlatformValidation:
    def test_openai_min_examples(self, alpaca_path):
        results = validate_dataset(alpaca_path, format_name="alpaca", platform="openai")
        min_check = [r for r in results if "minimum" in r.check_name.lower()]
        assert min_check and not min_check[0].passed

    def test_openai_valid_structure(self, openai_chat_path):
        results = validate_dataset(openai_chat_path, format_name="openai-chat")
        struct_check = [r for r in results if "json structure" in r.check_name.lower()]
        assert struct_check and struct_check[0].passed
