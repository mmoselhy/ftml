# ftml

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)

**The missing ffmpeg for LLM fine-tuning data.**

Convert, validate, and fix LLM training datasets between any format — alpaca, sharegpt, openai-chat, chatml, csv — with a single command.

<!-- [DEMO GIF PLACEHOLDER] Record with `asciinema rec` or `vhs` -->

## Install

```bash
pip install ftml
```

## Quick Start

```bash
# Convert alpaca to OpenAI format
ftml convert data.jsonl --from alpaca --to openai-chat

# Auto-detect format, fix issues, validate for OpenAI
ftml convert data.jsonl --to openai-chat --validate --fix --platform openai

# Validate a dataset
ftml validate data.jsonl --platform openai

# Auto-detect format
ftml detect data.jsonl

# View dataset stats
ftml stats data.jsonl
```

## Supported Formats

| Format | Direction | Key Fields | Used By |
|--------|-----------|-----------|---------|
| `alpaca` | input/output | `instruction`, `input`, `output` | Stanford Alpaca, Dolly |
| `sharegpt` | input/output | `conversations[{from, value}]` | ShareGPT, FastChat, Vicuna |
| `openai-chat` | input/output | `messages[{role, content}]` | OpenAI Fine-tuning API |
| `chatml` | input/output | `<\|im_start\|>role\ncontent<\|im_end\|>` | ChatML, Qwen, Yi |
| `csv` | input only | `instruction`, `input`, `output` columns | Spreadsheets, custom |
| `together` | output only | `messages[{role, content}]` | Together AI API |

## Platform Rules

| Platform | Accepted Formats | Min Examples | Max Tokens | Notes |
|----------|-----------------|-------------|-----------|-------|
| `openai` | openai-chat | 10 | 16,384 | Requires user + assistant roles |
| `together` | openai-chat | 1 | 8,192 | System prompt optional |
| `axolotl` | alpaca, sharegpt, openai-chat | 1 | - | System prompt recommended |
| `unsloth` | alpaca, openai-chat | 1 | 4,096 (warn) | Default 4k context |
| `huggingface` | any | 1 | - | Validates JSONL + Unicode |

## CLI Reference

### `ftml convert`

```
ftml convert <input_file> [OPTIONS]

Options:
  --from FORMAT          Source format (auto-detect if omitted)
  --to FORMAT            Target format (default: openai-chat)
  --output, -o PATH      Output file path
  --validate             Validate after converting
  --fix                  Auto-fix fixable issues
  --platform PLATFORM    Platform-specific validation
  --token-model MODEL    Tokenizer (default: cl100k_base)
  --max-tokens INT       Max tokens per example
  --split FLOAT          Train/eval split ratio (e.g., 0.9)
  --quiet, -q            Suppress rich output
  --dry-run              Parse and validate only
```

### `ftml validate`

```
ftml validate <input_file> [OPTIONS]

Options:
  --format FORMAT        Declare format explicitly
  --platform PLATFORM    Platform-specific rules
  --token-model MODEL    Tokenizer model
  --max-tokens INT       Per-example token limit
  --strict               Treat warnings as errors
```

### `ftml detect`

```
ftml detect <input_file>
```

### `ftml stats`

```
ftml stats <input_file> [OPTIONS]

Options:
  --format FORMAT        Declare format explicitly
  --token-model MODEL    Tokenizer model
```

### `ftml formats`

Prints a table of all supported formats and platform rules.

## Contributing

### Adding a New Format

1. Create `ftml/formats/your_format.py` with a `YourFormatReader(FormatReader)` and `YourFormatWriter(FormatWriter)`
2. Register it in `ftml/formats/__init__.py` by adding entries to `_READER_REGISTRY` and `_WRITER_REGISTRY`
3. Add sample data in `tests/sample_data/` and roundtrip tests in `tests/test_roundtrip.py`

## License

MIT
