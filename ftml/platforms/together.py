from ftml.platforms.base import PlatformRules

RULES = PlatformRules(
    name="together",
    accepted_formats=["openai-chat"],
    min_examples=1,
    max_tokens_error=8192,
    notes="Same schema as OpenAI chat. System prompt allowed but not required.",
)
