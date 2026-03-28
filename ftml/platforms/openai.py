from ftml.platforms.base import PlatformRules

RULES = PlatformRules(
    name="openai",
    accepted_formats=["openai-chat"],
    min_examples=10,
    max_tokens_warn=4096,
    max_tokens_error=16384,
    require_user_turn=True,
    require_assistant_turn=True,
    notes="File must be .jsonl. Required roles: user and assistant.",
)
