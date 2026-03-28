"""Dataset statistics computation."""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from pathlib import Path

from ftml.formats import get_reader
from ftml.tokenizer import count_tokens


@dataclass
class DatasetStats:
    total_examples: int = 0
    min_tokens: int = 0
    max_tokens: int = 0
    mean_tokens: float = 0.0
    median_tokens: float = 0.0
    pct_with_system: float = 0.0
    pct_multiturn: float = 0.0
    turn_distribution: dict[str, int] = field(default_factory=dict)
    token_histogram: list[tuple[str, float]] = field(default_factory=list)


def compute_stats(
    path: Path,
    format_name: str,
    token_model: str = "cl100k_base",
) -> DatasetStats:
    """Compute dataset statistics without conversion."""
    reader = get_reader(format_name)
    token_counts: list[int] = []
    system_count = 0
    multiturn_count = 0
    turn_counts: dict[int, int] = {}

    for example in reader.read(path):
        tokens = count_tokens(example, model=token_model)
        token_counts.append(tokens)

        if example.system is not None:
            system_count += 1

        n_turns = len(example.turns)
        if n_turns > 2:
            multiturn_count += 1

        turn_counts[n_turns] = turn_counts.get(n_turns, 0) + 1

    total = len(token_counts)
    if total == 0:
        return DatasetStats()

    turn_dist = {}
    for n, count in sorted(turn_counts.items()):
        if n <= 2:
            label = f"{n}-turn"
        else:
            label = "multi-turn"
            turn_dist[label] = turn_dist.get(label, 0) + count
            continue
        turn_dist[label] = count

    bucket_thresholds = [256, 512, 1024, 2048]
    labels = ["0-256", "257-512", "513-1k", "1k-2k", "2k+"]
    bucket_counts = [0] * 5
    for t in token_counts:
        if t <= 256:
            bucket_counts[0] += 1
        elif t <= 512:
            bucket_counts[1] += 1
        elif t <= 1024:
            bucket_counts[2] += 1
        elif t <= 2048:
            bucket_counts[3] += 1
        else:
            bucket_counts[4] += 1
    histogram = [(label, (c / total) * 100) for label, c in zip(labels, bucket_counts)]

    return DatasetStats(
        total_examples=total,
        min_tokens=min(token_counts),
        max_tokens=max(token_counts),
        mean_tokens=statistics.mean(token_counts),
        median_tokens=statistics.median(token_counts),
        pct_with_system=(system_count / total) * 100,
        pct_multiturn=(multiturn_count / total) * 100,
        turn_distribution=turn_dist,
        token_histogram=histogram,
    )
