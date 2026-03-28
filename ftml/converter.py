"""Pipeline orchestration: read → fix → validate → write."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterator, Optional

from ftml.formats import get_reader, get_writer
from ftml.models import ConversationExample, ConvertStats, Issue, Severity


def convert(
    input_path: Path,
    output_path: Path,
    *,
    from_format: str,
    to_format: str,
    fix: bool = False,
    validate: bool = False,
    platform: Optional[str] = None,
    dry_run: bool = False,
    on_progress: Optional[Callable[[int], None]] = None,
) -> ConvertStats:
    """Convert a dataset from one format to another."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.is_dir():
        raise IsADirectoryError(f"Input is a directory, not a file: {input_path}")

    reader = get_reader(from_format)
    stats = ConvertStats()

    def read_and_track() -> Iterator[ConversationExample]:
        for example in reader.read(input_path):
            stats.total_read += 1
            if on_progress:
                on_progress(stats.total_read)
            yield example

    stream: Iterator[ConversationExample] = read_and_track()

    if fix:
        stream = _apply_fixes(stream, stats)

    if validate:
        stream = _apply_validation(stream, stats, platform=platform)

    if dry_run:
        for _ in stream:
            pass
        stats.issues.extend(reader.errors)
        return stats

    writer = get_writer(to_format)
    stats.total_written = writer.write(stream, output_path)
    stats.total_skipped = stats.total_read - stats.total_written
    stats.issues.extend(reader.errors)
    return stats


def _apply_fixes(
    stream: Iterator[ConversationExample],
    stats: ConvertStats,
) -> Iterator[ConversationExample]:
    """Apply auto-fixes. Placeholder until fixer.py exists."""
    yield from stream


def _apply_validation(
    stream: Iterator[ConversationExample],
    stats: ConvertStats,
    *,
    platform: Optional[str] = None,
) -> Iterator[ConversationExample]:
    """Apply validation. Placeholder until validator.py exists."""
    yield from stream
