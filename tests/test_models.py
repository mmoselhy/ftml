from ftml.models import Turn, ConversationExample, Issue, Severity


class TestTurn:
    def test_create_user_turn(self):
        turn = Turn(role="user", content="Hello")
        assert turn.role == "user"
        assert turn.content == "Hello"

    def test_create_assistant_turn(self):
        turn = Turn(role="assistant", content="Hi there")
        assert turn.role == "assistant"
        assert turn.content == "Hi there"

    def test_invalid_role_rejected(self):
        import pytest
        with pytest.raises(ValueError):
            Turn(role="invalid", content="Hello")


class TestConversationExample:
    def test_minimal_example(self):
        ex = ConversationExample(
            turns=[
                Turn(role="user", content="Hi"),
                Turn(role="assistant", content="Hello"),
            ]
        )
        assert ex.system is None
        assert len(ex.turns) == 2
        assert ex.metadata == {}

    def test_with_system_prompt(self):
        ex = ConversationExample(
            system="You are helpful.",
            turns=[Turn(role="user", content="Hi")],
        )
        assert ex.system == "You are helpful."

    def test_with_metadata(self):
        ex = ConversationExample(
            turns=[Turn(role="user", content="Hi")],
            metadata={"source_format": "alpaca", "line_number": 1},
        )
        assert ex.metadata["source_format"] == "alpaca"
        assert ex.metadata["line_number"] == 1

    def test_immutable_copy(self):
        ex = ConversationExample(
            system="Be helpful.",
            turns=[Turn(role="user", content="Hi")],
        )
        ex2 = ex.model_copy(update={"system": "Be concise."})
        assert ex.system == "Be helpful."
        assert ex2.system == "Be concise."


class TestIssue:
    def test_create_error_issue(self):
        issue = Issue(line=42, severity=Severity.ERROR, message="Missing field")
        assert issue.line == 42
        assert issue.severity == Severity.ERROR

    def test_create_fix_issue(self):
        issue = Issue(line=10, severity=Severity.FIX, message="Stripped whitespace")
        assert issue.severity == Severity.FIX
