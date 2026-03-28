"""Platform validation rules registry."""

from __future__ import annotations

from ftml.platforms.base import PlatformRules

_PLATFORM_REGISTRY: dict[str, str] = {
    "openai": "ftml.platforms.openai",
    "together": "ftml.platforms.together",
    "axolotl": "ftml.platforms.axolotl",
    "unsloth": "ftml.platforms.unsloth",
    "huggingface": "ftml.platforms.huggingface",
}

SUPPORTED_PLATFORMS = list(_PLATFORM_REGISTRY.keys())


def get_platform_rules(platform: str) -> PlatformRules:
    if platform not in _PLATFORM_REGISTRY:
        raise ValueError(
            f"Unknown platform: {platform!r}. Supported: {', '.join(SUPPORTED_PLATFORMS)}"
        )
    import importlib
    module = importlib.import_module(_PLATFORM_REGISTRY[platform])
    return module.RULES
