<p align="center">
  <h1 align="center">ftml</h1>
  <p align="center"><strong>The missing ffmpeg for LLM fine-tuning data.</strong></p>
  <p align="center">
    <a href="https://pypi.org/project/ftml-cli/"><img src="https://img.shields.io/pypi/v/ftml-cli?color=%2334D058&label=pypi" alt="PyPI"></a>
    <a href="https://pypi.org/project/ftml-cli/"><img src="https://img.shields.io/pypi/pyversions/ftml-cli?color=%2334D058" alt="Python"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  </p>
</p>

---

Convert, validate, and auto-fix LLM training datasets between **any format** with a single command. Stop hand-editing JSONL files.

```
alpaca  <-->  openai-chat  <-->  sharegpt  <-->  chatml  <-->  csv
```

<!-- Record a demo: asciinema rec demo.cast && agg demo.cast demo.gif -->

## Why ftml?

You downloaded a dataset from HuggingFace. It's in ShareGPT format. Your fine-tuning provider wants OpenAI chat format. The fields don't match. Some rows are malformed. You write a throwaway Python script for the third time this week.

**ftml fixes this.** One tool that reads every common format, validates against platform rules, auto-fixes common issues, and writes clean output ready for training.

## Install

```bash
pip install ftml-cli
```

## 30-Second Quick Start

```bash
# Convert any format to OpenAI (auto-detects input)
ftml convert dataset.jsonl --to openai-chat

# Fix messy data + validate for OpenAI's API
ftml convert dataset.jsonl --to openai-chat --fix --validate --platform openai

# Just check if your data is valid
ftml validate dataset.jsonl --platform openai

# What format is this file?
ftml detect mystery_data.jsonl

# Get a quick overview of your dataset
ftml stats dataset.jsonl

# Split into train/eval
ftml convert dataset.jsonl --to openai-chat --split 0.9
```

## What It Looks Like

```
╭──────────────────────────────────────────────────────────╮
│ ftml · LLM dataset format converter                      │
│ alpaca → openai-chat  ·  train.jsonl                     │
╰──────────────────────────────────────────────────────────╯
Processing ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5,000/5,000 0:00:02

        Fixes Applied
┌──────────┬───────┬───────────────────────────────────────┐
│ Type     │ Count │ Description                           │
├──────────┼───────┼───────────────────────────────────────┤
│ [FIX]    │    42 │ Stripped whitespace from 1 field(s)   │
│ [FIX]    │     7 │ Normalized role "human" → "user"      │
│ [SKIP]   │     3 │ Malformed JSON                        │
│ [WARN]   │     2 │ Single character assistant response    │
└──────────┴───────┴───────────────────────────────────────┘

╭───────────────────── Dataset Stats ──────────────────────╮
│ Examples     4,997      Avg tokens    312                │
│ Min tokens   48         Max tokens    3,841              │
│ With system  63%        Multi-turn    28%                │
╰──────────────────────────────────────────────────────────╯

✓ Converted 4,997 examples → output.openai-chat.jsonl
```

## Supported Formats

| Format | Read | Write | Structure | Common Use |
|--------|:----:|:-----:|-----------|------------|
| **alpaca** | yes | yes | `{"instruction", "input", "output"}` | Stanford Alpaca, Dolly, many HF datasets |
| **sharegpt** | yes | yes | `{"conversations": [{"from", "value"}]}` | ShareGPT, FastChat, Vicuna, WizardLM |
| **openai-chat** | yes | yes | `{"messages": [{"role", "content"}]}` | OpenAI & Together fine-tuning APIs |
| **chatml** | yes | yes | `<\|im_start\|>role\ncontent<\|im_end\|>` | Qwen, Yi, many open models |
| **csv** | yes | yes | `instruction,input,output` columns | Spreadsheets, quick prototyping |
| **together** | -- | yes | Same as openai-chat | Together AI (with platform validation) |

All formats normalize to an internal representation, so **any input format converts to any output format** without data loss.

## Auto-Fix Engine

Pass `--fix` to automatically repair common issues:

| Issue | Action |
|-------|--------|
| Leading/trailing whitespace | Stripped |
| `"from": "human"` / `"gpt"` roles | Normalized to `"user"` / `"assistant"` |
| Missing `"input"` field in Alpaca | Set to `""` |
| Empty system prompt (whitespace only) | Removed |
| Duplicate consecutive role turns | Merged with `\n\n` |
| Conversation ending on user turn | Trailing user turn removed |
| Malformed JSON lines | Skipped with line number logged |

Issues that **can't be auto-fixed** are flagged as warnings:
- Single-punctuation assistant responses (e.g., `"."`)
- Instruction identical to output
- Conversations with 3+ consecutive assistant turns

## Platform Validation

Validate against the rules of your target platform with `--platform`:

```bash
ftml validate data.jsonl --platform openai
```

| Platform | Format | Min Examples | Max Tokens | Notes |
|----------|--------|:-----------:|:----------:|-------|
| **openai** | openai-chat | 10 | 16,384 | Requires user + assistant roles |
| **together** | openai-chat | 1 | 8,192 | System prompt optional |
| **axolotl** | alpaca, sharegpt, openai-chat | 1 | -- | Warns if no system prompt |
| **unsloth** | alpaca, openai-chat | 1 | 4,096 (warn) | Default 4k context |
| **huggingface** | any | 1 | -- | Validates JSONL + Unicode |

## CLI Reference

### `ftml convert`

```
ftml convert <input_file> [OPTIONS]

  --from FORMAT          Source format (auto-detect if omitted)
  --to FORMAT            Target format (default: openai-chat)
  --output, -o PATH      Output file path
  --validate             Validate after converting
  --fix                  Auto-fix common issues
  --platform PLATFORM    Validate against platform rules
  --token-model MODEL    Tokenizer for counting (default: cl100k_base)
  --max-tokens INT       Warn if any example exceeds this
  --split FLOAT          Train/eval split ratio (e.g., 0.9)
  --quiet, -q            Machine-friendly output (errors only)
  --dry-run              Parse and validate without writing
```

### `ftml validate`

```
ftml validate <input_file> [OPTIONS]

  --format FORMAT        Declare format (else auto-detect)
  --platform PLATFORM    Platform-specific rules
  --max-tokens INT       Per-example token limit
  --strict               Treat warnings as errors (exit 1)
```

### `ftml detect`

```
ftml detect <input_file>
```

### `ftml stats`

```
ftml stats <input_file> [OPTIONS]

  --format FORMAT        Declare format (else auto-detect)
  --token-model MODEL    Tokenizer for counting
```

### `ftml formats`

```
ftml formats              # Print all supported formats and platform rules
```

## Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Success |
| 1 | Validation errors found |
| 2 | Input file not found or unreadable |
| 3 | Format detection failed |

## Contributing

### Adding a New Format

Three files, three steps:

1. **Create** `ftml/formats/your_format.py` with `YourReader(FormatReader)` and `YourWriter(FormatWriter)`
2. **Register** in `ftml/formats/__init__.py` -- add entries to `_READER_REGISTRY` and `_WRITER_REGISTRY`
3. **Test** -- add sample data to `tests/sample_data/` and a roundtrip test to `tests/test_roundtrip.py`

```bash
# Run the test suite
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT
