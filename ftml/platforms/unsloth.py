from ftml.platforms.base import PlatformRules

RULES = PlatformRules(
    name="unsloth",
    accepted_formats=["alpaca", "openai-chat"],
    max_tokens_warn=4096,
    notes="Default context window 4096 for many unsloth configs.",
)
