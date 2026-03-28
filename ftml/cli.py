"""Typer CLI definitions for all ftml commands."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from ftml import __version__

app = typer.Typer(
    name="ftml",
    help="The universal format converter and validator for LLM fine-tuning datasets.",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"ftml {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", help="Show version and exit.", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """ftml — The missing ffmpeg for LLM fine-tuning datasets."""


@app.command()
def convert(
    input_file: Annotated[Path, typer.Argument(help="Path to input file (.jsonl, .json, .csv, .txt)")],
    from_format: Annotated[Optional[str], typer.Option("--from", help="Source format (auto-detect if omitted)")] = None,
    to_format: Annotated[str, typer.Option("--to", help="Target format")] = "openai-chat",
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path")] = None,
    validate: Annotated[bool, typer.Option("--validate", help="Validate after converting")] = False,
    fix: Annotated[bool, typer.Option("--fix", help="Auto-fix fixable issues")] = False,
    platform: Annotated[Optional[str], typer.Option("--platform", help="Platform-specific validation")] = None,
    token_model: Annotated[str, typer.Option("--token-model", help="Tokenizer model")] = "cl100k_base",
    max_tokens: Annotated[Optional[int], typer.Option("--max-tokens", help="Max tokens per example")] = None,
    split: Annotated[Optional[float], typer.Option("--split", help="Train/eval split ratio")] = None,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Suppress rich output")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Parse and validate only")] = False,
) -> None:
    """Convert a dataset from one format to another."""
    from ftml.converter import convert as do_convert
    from ftml.reporter import console, create_progress, print_header, print_fix_log, print_status

    # Validate input file
    if not input_file.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {input_file}")
        raise typer.Exit(code=2)
    if input_file.is_dir():
        console.print(
            f"[bold red]Error:[/bold red] {input_file} is a directory. "
            "Use ftml convert *.jsonl to process multiple files."
        )
        raise typer.Exit(code=2)

    # Auto-detect format if not specified
    if from_format is None:
        try:
            from ftml.detector import detect_format
            result = detect_format(input_file)
            from_format = result.format_name
            if not quiet:
                console.print(f"[dim]Auto-detected format: {from_format} (confidence: {result.confidence:.0%})[/dim]")
        except Exception:
            console.print(
                "[bold red]Error:[/bold red] Could not auto-detect format. Use --from to specify."
            )
            raise typer.Exit(code=3)

    # Determine output path
    if output is None:
        output = input_file.with_suffix(f".{to_format.replace('-', '_')}.jsonl")

    print_header(from_format, to_format, input_file.name, quiet=quiet)

    # Count lines for progress bar
    if not quiet:
        line_count = sum(1 for _ in open(input_file, encoding="utf-8"))
    else:
        line_count = 0

    progress = create_progress(quiet=quiet)
    with progress:
        task = progress.add_task("Converting", total=line_count)

        def on_progress(n: int) -> None:
            progress.update(task, completed=n)

        stats = do_convert(
            input_file,
            output,
            from_format=from_format,
            to_format=to_format,
            fix=fix,
            validate=validate,
            platform=platform,
            dry_run=dry_run,
            on_progress=on_progress,
        )

    # Print fix log if --fix was used
    if fix:
        print_fix_log(stats.issues, quiet=quiet)

    # Handle --split post-processing
    if split is not None and not dry_run and output.exists():
        _split_output(output, split, quiet=quiet)

    print_status(stats, str(output), quiet=quiet)

    # Exit code based on errors
    error_count = sum(1 for i in stats.issues if i.severity.value == "error")
    if error_count > 0:
        raise typer.Exit(code=1)


def _split_output(output_path: Path, ratio: float, quiet: bool = False) -> None:
    """Split an output file into train and eval sets."""
    from ftml.reporter import console

    lines = output_path.read_text(encoding="utf-8").strip().split("\n")
    split_idx = int(len(lines) * ratio)
    train_path = output_path.with_suffix(".train.jsonl")
    eval_path = output_path.with_suffix(".eval.jsonl")
    train_path.write_text("\n".join(lines[:split_idx]) + "\n", encoding="utf-8")
    eval_path.write_text("\n".join(lines[split_idx:]) + "\n", encoding="utf-8")
    if not quiet:
        console.print(f"[dim]Split: {split_idx} train, {len(lines) - split_idx} eval[/dim]")


@app.command()
def validate(
    input_file: Annotated[Path, typer.Argument(help="Path to input file")],
    format: Annotated[Optional[str], typer.Option("--format", help="Declare format explicitly")] = None,
    platform: Annotated[Optional[str], typer.Option("--platform", help="Platform-specific rules")] = None,
    token_model: Annotated[str, typer.Option("--token-model", help="Tokenizer model")] = "cl100k_base",
    max_tokens: Annotated[Optional[int], typer.Option("--max-tokens", help="Per-example token limit")] = None,
    strict: Annotated[bool, typer.Option("--strict", help="Treat warnings as errors")] = False,
) -> None:
    """Validate a dataset without converting it."""
    from ftml.detector import detect_format
    from ftml.reporter import console, print_validation_table
    from ftml.validator import validate_dataset

    if not input_file.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {input_file}")
        raise typer.Exit(code=2)

    if format is None:
        result = detect_format(input_file)
        format = result.format_name
        console.print(f"[dim]Auto-detected format: {format}[/dim]")

    results = validate_dataset(
        input_file,
        format,
        platform=platform,
        max_tokens=max_tokens,
        token_model=token_model,
        strict=strict,
    )
    print_validation_table(results)

    has_errors = any(not r.passed for r in results)
    if has_errors:
        console.print("[bold red]✗ Validation failed[/bold red]")
        raise typer.Exit(code=1)
    else:
        console.print("[bold green]✓ Validation passed[/bold green]")


@app.command()
def detect(
    input_file: Annotated[Path, typer.Argument(help="Path to input file")],
) -> None:
    """Auto-detect the format of a dataset file."""
    from ftml.detector import detect_format
    from ftml.reporter import console

    if not input_file.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {input_file}")
        raise typer.Exit(code=2)

    try:
        result = detect_format(input_file)
        console.print(
            f"Detected format: [bold]{result.format_name}[/bold] "
            f"(confidence: {result.confidence:.0%})"
        )
        console.print(f"Evidence: {result.evidence}")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=3)


@app.command()
def stats(
    input_file: Annotated[Path, typer.Argument(help="Path to input file")],
    format: Annotated[Optional[str], typer.Option("--format", help="Declare format explicitly")] = None,
    token_model: Annotated[str, typer.Option("--token-model", help="Tokenizer model")] = "cl100k_base",
) -> None:
    """Print dataset statistics."""
    from ftml.detector import detect_format
    from ftml.reporter import console, print_stats_summary, print_token_histogram
    from ftml.stats import compute_stats

    if not input_file.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {input_file}")
        raise typer.Exit(code=2)

    if format is None:
        result = detect_format(input_file)
        format = result.format_name
        console.print(f"[dim]Auto-detected format: {format}[/dim]")

    ds_stats = compute_stats(input_file, format, token_model=token_model)

    print_stats_summary(
        total=ds_stats.total_examples,
        avg_tokens=ds_stats.mean_tokens,
        min_tokens=ds_stats.min_tokens,
        max_tokens=ds_stats.max_tokens,
        pct_system=ds_stats.pct_with_system,
        pct_multiturn=ds_stats.pct_multiturn,
    )
    print_token_histogram(ds_stats.token_histogram)


@app.command()
def formats() -> None:
    """Print a table of all supported formats."""
    from rich.table import Table

    from ftml.reporter import console

    table = Table(title="Supported Formats", border_style="cyan")
    table.add_column("Format", style="bold")
    table.add_column("Direction")
    table.add_column("Key Fields")
    table.add_column("Used By")

    table.add_row("alpaca", "input/output", "instruction, input, output", "Stanford Alpaca, Dolly")
    table.add_row("sharegpt", "input/output", 'conversations[{from, value}]', "ShareGPT, FastChat, Vicuna")
    table.add_row("openai-chat", "input/output", 'messages[{role, content}]', "OpenAI Fine-tuning API")
    table.add_row("chatml", "input/output", "<|im_start|>role\\ncontent<|im_end|>", "ChatML, Qwen, Yi")
    table.add_row("csv", "input only", "instruction, input, output (columns)", "Spreadsheets, custom data")
    table.add_row("together", "output only", 'messages[{role, content}]', "Together AI API")

    console.print(table)

    ptable = Table(title="Platform Rules", border_style="blue")
    ptable.add_column("Platform", style="bold")
    ptable.add_column("Accepted Formats")
    ptable.add_column("Min Examples", justify="right")
    ptable.add_column("Max Tokens", justify="right")
    ptable.add_column("Notes")

    ptable.add_row("openai", "openai-chat", "10", "16,384", "Required: user + assistant roles")
    ptable.add_row("together", "openai-chat", "1", "8,192", "System prompt optional")
    ptable.add_row("axolotl", "alpaca, sharegpt, openai-chat", "1", "-", "System prompt recommended")
    ptable.add_row("unsloth", "alpaca, openai-chat", "1", "4,096 (warn)", "Default 4k context window")
    ptable.add_row("huggingface", "any", "1", "-", "Validates JSONL + Unicode")

    console.print(ptable)
