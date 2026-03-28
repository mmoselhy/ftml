"""Format readers and writers registry."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftml.formats.base import FormatReader, FormatWriter

# Lazy imports to avoid circular dependencies.
_READER_REGISTRY: dict[str, tuple[str, str]] = {
    "alpaca": ("ftml.formats.alpaca", "AlpacaReader"),
    "sharegpt": ("ftml.formats.sharegpt", "ShareGPTReader"),
    "openai-chat": ("ftml.formats.openai_chat", "OpenAIChatReader"),
    "chatml": ("ftml.formats.chatml", "ChatMLReader"),
    "csv": ("ftml.formats.csv_format", "CSVReader"),
}

_WRITER_REGISTRY: dict[str, tuple[str, str]] = {
    "alpaca": ("ftml.formats.alpaca", "AlpacaWriter"),
    "sharegpt": ("ftml.formats.sharegpt", "ShareGPTWriter"),
    "openai-chat": ("ftml.formats.openai_chat", "OpenAIChatWriter"),
    "chatml": ("ftml.formats.chatml", "ChatMLWriter"),
    "together": ("ftml.formats.openai_chat", "OpenAIChatWriter"),
}

SUPPORTED_INPUT_FORMATS = list(_READER_REGISTRY.keys())
SUPPORTED_OUTPUT_FORMATS = list(_WRITER_REGISTRY.keys())


def _import_class(module_path: str, class_name: str):
    """Dynamically import a class from a module."""
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_reader(format_name: str) -> "FormatReader":
    """Get an instantiated reader for the given format."""
    if format_name not in _READER_REGISTRY:
        raise ValueError(
            f"Unknown input format: {format_name!r}. "
            f"Supported: {', '.join(SUPPORTED_INPUT_FORMATS)}"
        )
    module_path, class_name = _READER_REGISTRY[format_name]
    cls = _import_class(module_path, class_name)
    return cls()


def get_writer(format_name: str) -> "FormatWriter":
    """Get an instantiated writer for the given format."""
    if format_name not in _WRITER_REGISTRY:
        raise ValueError(
            f"Unknown output format: {format_name!r}. "
            f"Supported: {', '.join(SUPPORTED_OUTPUT_FORMATS)}"
        )
    module_path, class_name = _WRITER_REGISTRY[format_name]
    cls = _import_class(module_path, class_name)
    return cls()
