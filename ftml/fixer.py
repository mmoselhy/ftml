"""Auto-fix engine for dataset issues."""

from __future__ import annotations

from ftml.models import ConversationExample, Issue, Severity, Turn


def apply_fixes(example: ConversationExample, *, line: int) -> tuple[ConversationExample, list[Issue]]:
    """Apply all auto-fixes to an example. Returns (fixed_example, issues)."""
    issues: list[Issue] = []
    ex = example

    ex, new_issues = _strip_whitespace(ex, line=line)
    issues.extend(new_issues)

    ex, new_issues = _clean_empty_system(ex, line=line)
    issues.extend(new_issues)

    ex, new_issues = _merge_consecutive_roles(ex, line=line)
    issues.extend(new_issues)

    ex, new_issues = _remove_trailing_user_turn(ex, line=line)
    issues.extend(new_issues)

    issues.extend(_warn_single_punctuation_response(ex, line=line))
    issues.extend(_warn_identical_instruction_output(ex, line=line))

    return ex, issues


def _strip_whitespace(ex: ConversationExample, *, line: int) -> tuple[ConversationExample, list[Issue]]:
    issues = []
    new_turns = []
    stripped_count = 0
    for turn in ex.turns:
        stripped = turn.content.strip()
        if stripped != turn.content:
            stripped_count += 1
        new_turns.append(Turn(role=turn.role, content=stripped))
    if stripped_count > 0:
        issues.append(Issue(line=line, severity=Severity.FIX, message=f"Stripped whitespace from {stripped_count} field(s)"))
        ex = ex.model_copy(update={"turns": new_turns})
    return ex, issues


def _clean_empty_system(ex: ConversationExample, *, line: int) -> tuple[ConversationExample, list[Issue]]:
    issues = []
    if ex.system is not None and not ex.system.strip():
        ex = ex.model_copy(update={"system": None})
        issues.append(Issue(line=line, severity=Severity.FIX, message="Removed empty system prompt"))
    return ex, issues


def _merge_consecutive_roles(ex: ConversationExample, *, line: int) -> tuple[ConversationExample, list[Issue]]:
    if len(ex.turns) < 2:
        return ex, []
    merged = [ex.turns[0]]
    merge_count = 0
    for turn in ex.turns[1:]:
        if turn.role == merged[-1].role:
            merged[-1] = Turn(role=turn.role, content=f"{merged[-1].content}\n\n{turn.content}")
            merge_count += 1
        else:
            merged.append(turn)
    issues = []
    if merge_count > 0:
        issues.append(Issue(line=line, severity=Severity.FIX, message=f"Merged {merge_count} consecutive same-role turn(s)"))
        ex = ex.model_copy(update={"turns": merged})
    return ex, issues


def _remove_trailing_user_turn(ex: ConversationExample, *, line: int) -> tuple[ConversationExample, list[Issue]]:
    issues = []
    if len(ex.turns) >= 2 and ex.turns[-1].role == "user":
        ex = ex.model_copy(update={"turns": ex.turns[:-1]})
        issues.append(Issue(line=line, severity=Severity.FIX, message="Removed trailing user turn with no assistant reply"))
    return ex, issues


def _warn_single_punctuation_response(ex: ConversationExample, *, line: int) -> list[Issue]:
    issues = []
    for turn in ex.turns:
        if turn.role == "assistant" and len(turn.content) <= 1 and turn.content in ".!?,;:-":
            issues.append(Issue(line=line, severity=Severity.WARNING, message=f"Single character assistant response: {turn.content!r}"))
    return issues


def _warn_identical_instruction_output(ex: ConversationExample, *, line: int) -> list[Issue]:
    user_turns = [t for t in ex.turns if t.role == "user"]
    assistant_turns = [t for t in ex.turns if t.role == "assistant"]
    if user_turns and assistant_turns and user_turns[0].content == assistant_turns[0].content:
        return [Issue(line=line, severity=Severity.WARNING, message="Instruction is identical to output")]
    return []
