"""Rich terminal output: panels, tables, progress bars, histograms."""

from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text

from ftml.models import ConvertStats, Issue, Severity, ValidationResult

console = Console()


def print_header(from_format: str, to_format: str, filename: str, quiet: bool = False) -> None:
    """Print the ftml header panel."""
    if quiet:
        return
    text = Text()
    text.append("ftml", style="bold cyan")
    text.append(" · LLM dataset format converter\n", style="dim")
    text.append(f"{from_format}", style="bold")
    text.append(" → ", style="dim")
    text.append(f"{to_format}", style="bold")
    text.append(f"  ·  {filename}", style="dim")
    console.print(Panel(text, border_style="cyan"))


def create_progress(quiet: bool = False) -> Progress:
    """Create a Rich progress bar for conversion."""
    if quiet:
        return Progress(disable=True)
    return Progress(
        TextColumn("[bold blue]Processing"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def print_fix_log(issues: list[Issue], quiet: bool = False) -> None:
    """Print the fix/skip/warn log table."""
    if quiet:
        return
    fix_issues = [i for i in issues if i.severity in (Severity.FIX, Severity.SKIP, Severity.WARNING)]
    if not fix_issues:
        return

    table = Table(title="Fixes Applied", border_style="yellow", show_lines=False)
    table.add_column("Type", style="bold", width=8)
    table.add_column("Count", justify="right", width=6)
    table.add_column("Description")

    from collections import Counter
    counts: Counter[tuple[Severity, str]] = Counter()
    for issue in fix_issues:
        counts[(issue.severity, issue.message)] += 1

    style_map = {
        Severity.FIX: "green",
        Severity.SKIP: "yellow",
        Severity.WARNING: "bold yellow",
    }
    for (severity, message), count in counts.most_common():
        style = style_map.get(severity, "")
        tag = f"[{severity.value.upper()}]"
        table.add_row(f"[{style}]{tag}[/{style}]", str(count), message)

    console.print(table)


def print_validation_table(results: list[ValidationResult], quiet: bool = False) -> None:
    """Print the validation results table."""
    if quiet:
        return

    table = Table(title="Validation Results", border_style="blue")
    table.add_column("Check", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Count", justify="right")

    for result in results:
        if result.passed:
            status = "[bold green]✓ pass[/bold green]"
        else:
            status = "[bold red]✗ fail[/bold red]"
        count_str = str(result.count) if result.count > 0 else ""
        table.add_row(result.check_name, status, count_str)

    console.print(table)


def print_stats_summary(
    total: int,
    avg_tokens: float,
    min_tokens: int,
    max_tokens: int,
    pct_system: float,
    pct_multiturn: float,
    quiet: bool = False,
) -> None:
    """Print the dataset stats summary panel."""
    if quiet:
        return
    table = Table(show_header=False, border_style="green", padding=(0, 2))
    table.add_column("Key", style="bold")
    table.add_column("Value", justify="right")
    table.add_column("Key", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Examples", f"{total:,}", "Avg tokens", f"{avg_tokens:.0f}")
    table.add_row("Min tokens", f"{min_tokens:,}", "Max tokens", f"{max_tokens:,}")
    table.add_row("With system", f"{pct_system:.0f}%", "Multi-turn", f"{pct_multiturn:.0f}%")

    console.print(Panel(table, title="Dataset Stats", border_style="green"))


def print_token_histogram(buckets: list[tuple[str, float]], quiet: bool = False) -> None:
    """Print an ASCII token distribution histogram."""
    if quiet:
        return
    console.print("\n[bold]Token distribution[/bold]")
    max_pct = max(pct for _, pct in buckets) if buckets else 1
    for label, pct in buckets:
        bar_len = int((pct / max_pct) * 30) if max_pct > 0 else 0
        bar = "▓" * bar_len
        console.print(f"  {label:>8s}  {bar}  {pct:.0f}%")
    console.print()


def print_status(stats: ConvertStats, output_path: str, quiet: bool = False) -> None:
    """Print the final status line."""
    if quiet and not stats.issues:
        return
    warning_count = sum(1 for i in stats.issues if i.severity == Severity.WARNING)
    error_count = sum(1 for i in stats.issues if i.severity == Severity.ERROR)

    if error_count > 0:
        console.print(
            f"[bold red]✗[/bold red] Conversion completed with {error_count} error(s). "
            f"Run with --fix to auto-repair."
        )
    elif warning_count > 0:
        console.print(
            f"[bold green]✓[/bold green] Converted {stats.total_written:,} examples → "
            f"{output_path}  ({warning_count} warning(s))"
        )
    else:
        console.print(
            f"[bold green]✓[/bold green] Converted {stats.total_written:,} examples → {output_path}"
        )
