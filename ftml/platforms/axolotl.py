from ftml.platforms.base import PlatformRules

RULES = PlatformRules(
    name="axolotl",
    accepted_formats=["alpaca", "sharegpt", "openai-chat"],
    warn_no_system=True,
    notes="Supports multiple formats. System prompt field is heavily used.",
)
