from ftml.platforms.base import PlatformRules

RULES = PlatformRules(
    name="huggingface",
    accepted_formats=["alpaca", "sharegpt", "openai-chat", "chatml", "csv"],
    notes="Any format acceptable. Validates JSONL structure and Unicode encoding.",
)
