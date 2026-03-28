"""Validation rules engine."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ftml.formats import get_reader
from ftml.models import ConversationExample, Issue, Severity, ValidationResult
from ftml.tokenizer import count_tokens


def validate_example(
    example: ConversationExample,
    *,
    max_tokens: Optional[int] = None,
    token_model: str = "cl100k_base",
) -> list[ValidationResult]:
    """Validate a single example against structural rules."""
    results = []

    roles = {t.role for t in example.turns}
    has_user = "user" in roles
    has_assistant = "assistant" in roles

    results.append(ValidationResult(
        check_name="Required roles present",
        passed=has_user and has_assistant,
        count=0 if (has_user and has_assistant) else 1,
    ))

    empty_count = sum(1 for t in example.turns if not t.content.strip())
    results.append(ValidationResult(
        check_name="No empty content fields",
        passed=empty_count == 0,
        count=empty_count,
    ))

    if example.turns:
        first_role = example.turns[0].role
        valid_start = first_role == "user"
        results.append(ValidationResult(
            check_name="Role sequence valid",
            passed=valid_start,
            count=0 if valid_start else 1,
        ))

    if max_tokens is not None:
        tokens = count_tokens(example, model=token_model)
        results.append(ValidationResult(
            check_name=f"Token limits (≤{max_tokens})",
            passed=tokens <= max_tokens,
            count=tokens if tokens > max_tokens else 0,
        ))

    return results


def validate_dataset(
    path: Path,
    format_name: str,
    *,
    platform: Optional[str] = None,
    max_tokens: Optional[int] = None,
    token_model: str = "cl100k_base",
    strict: bool = False,
) -> list[ValidationResult]:
    """Validate a dataset file. Returns aggregated validation results."""
    reader = get_reader(format_name)
    examples = list(reader.read(path))
    total = len(examples)

    json_valid = len(reader.errors) == 0
    results = [
        ValidationResult(check_name="JSON structure", passed=json_valid, count=len(reader.errors)),
    ]

    role_failures = 0
    empty_failures = 0
    sequence_failures = 0
    token_failures = 0

    for ex in examples:
        ex_results = validate_example(ex, max_tokens=max_tokens, token_model=token_model)
        for r in ex_results:
            if "Required roles" in r.check_name and not r.passed:
                role_failures += 1
            elif "empty content" in r.check_name.lower() and not r.passed:
                empty_failures += r.count
            elif "Role sequence" in r.check_name and not r.passed:
                sequence_failures += 1
            elif "Token limits" in r.check_name and not r.passed:
                token_failures += 1

    results.extend([
        ValidationResult(check_name="Required fields present", passed=role_failures == 0, count=role_failures),
        ValidationResult(check_name="Role sequence valid", passed=sequence_failures == 0, count=sequence_failures),
        ValidationResult(check_name="Empty content fields", passed=empty_failures == 0, count=empty_failures),
    ])

    if max_tokens is not None:
        results.append(ValidationResult(
            check_name=f"Token limits (≤{max_tokens})",
            passed=token_failures == 0,
            count=token_failures,
        ))

    if platform:
        from ftml.platforms import get_platform_rules
        rules = get_platform_rules(platform)

        results.append(ValidationResult(
            check_name=f"Minimum examples (≥{rules.min_examples})",
            passed=total >= rules.min_examples,
            count=total,
        ))

        if rules.max_tokens_error and max_tokens is None:
            over_limit = 0
            for ex in examples:
                tokens = count_tokens(ex, model=token_model)
                if tokens > rules.max_tokens_error:
                    over_limit += 1
            results.append(ValidationResult(
                check_name=f"Token limits (≤{rules.max_tokens_error})",
                passed=over_limit == 0,
                count=over_limit,
            ))

        if rules.warn_no_system:
            no_system = sum(1 for ex in examples if ex.system is None)
            results.append(ValidationResult(
                check_name="System prompt present",
                passed=no_system == 0,
                count=no_system,
            ))

    return results
