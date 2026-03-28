import pytest

from ftml.fixer import apply_fixes
from ftml.models import ConversationExample, Issue, Severity, Turn


class TestStripWhitespace:
    def test_strips_leading_trailing(self):
        ex = ConversationExample(
            turns=[
                Turn(role="user", content="  Hello  "),
                Turn(role="assistant", content="\tWorld\n"),
            ],
        )
        fixed, issues = apply_fixes(ex, line=1)
        assert fixed.turns[0].content == "Hello"
        assert fixed.turns[1].content == "World"
        assert any("whitespace" in i.message.lower() for i in issues)

    def test_no_change_when_clean(self):
        ex = ConversationExample(
            turns=[Turn(role="user", content="Clean"), Turn(role="assistant", content="OK")],
        )
        fixed, issues = apply_fixes(ex, line=1)
        assert len([i for i in issues if i.severity == Severity.FIX]) == 0


class TestEmptySystemPrompt:
    def test_whitespace_system_becomes_none(self):
        ex = ConversationExample(
            system="   ",
            turns=[Turn(role="user", content="Hi"), Turn(role="assistant", content="Hey")],
        )
        fixed, issues = apply_fixes(ex, line=1)
        assert fixed.system is None


class TestMergeConsecutiveRoles:
    def test_merge_consecutive_user_turns(self):
        ex = ConversationExample(
            turns=[
                Turn(role="user", content="First"),
                Turn(role="user", content="Second"),
                Turn(role="assistant", content="Response"),
            ],
        )
        fixed, issues = apply_fixes(ex, line=1)
        assert len(fixed.turns) == 2
        assert fixed.turns[0].content == "First\n\nSecond"
        assert fixed.turns[0].role == "user"

    def test_no_merge_when_alternating(self):
        ex = ConversationExample(
            turns=[Turn(role="user", content="Q"), Turn(role="assistant", content="A")],
        )
        fixed, issues = apply_fixes(ex, line=1)
        assert len(fixed.turns) == 2


class TestTrailingUserTurn:
    def test_removes_trailing_user_turn(self):
        ex = ConversationExample(
            turns=[
                Turn(role="user", content="Q"),
                Turn(role="assistant", content="A"),
                Turn(role="user", content="Dangling"),
            ],
        )
        fixed, issues = apply_fixes(ex, line=1)
        assert len(fixed.turns) == 2
        assert fixed.turns[-1].role == "assistant"


class TestWarnings:
    def test_single_punctuation_response(self):
        ex = ConversationExample(
            turns=[Turn(role="user", content="Hi"), Turn(role="assistant", content=".")],
        )
        fixed, issues = apply_fixes(ex, line=1)
        assert any(i.severity == Severity.WARNING and "single character" in i.message.lower() for i in issues)

    def test_instruction_equals_output(self):
        ex = ConversationExample(
            turns=[Turn(role="user", content="Same"), Turn(role="assistant", content="Same")],
        )
        fixed, issues = apply_fixes(ex, line=1)
        assert any(i.severity == Severity.WARNING and "identical" in i.message.lower() for i in issues)
