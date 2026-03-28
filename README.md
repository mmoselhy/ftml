<p align="center">
  <img src="https://img.shields.io/badge/ftml-ffmpeg%20for%20fine--tuning%20data-black?style=for-the-badge&labelColor=black" alt="ftml">
</p>

<h3 align="center">Stop writing throwaway scripts to convert training data.</h3>

<p align="center">
  <a href="https://pypi.org/project/ftml-cli/"><img src="https://img.shields.io/pypi/v/ftml-cli?color=%2334D058&label=pypi" alt="PyPI"></a>
  <a href="https://pypi.org/project/ftml-cli/"><img src="https://img.shields.io/pypi/pyversions/ftml-cli?color=%2334D058" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

<p align="center">
  <code>pip install ftml-cli</code>
</p>

---

**You know the drill.** You download a dataset from HuggingFace. It's in ShareGPT format. OpenAI's API wants `messages`. Together wants the same thing but with different token limits. You spend 45 minutes writing a conversion script. Half the rows have trailing whitespace. Some have `"from": "human"` instead of `"role": "user"`. Three lines are malformed JSON.

**ftml converts, validates, and fixes all of it in one command:**

```bash
ftml convert dataset.jsonl --to openai-chat --fix --validate --platform openai
```

```
╭──────────────────────────────────────────────────────────╮
│ ftml · LLM dataset format converter                      │
│ sharegpt → openai-chat  ·  dataset.jsonl                 │
╰──────────────────────────────────────────────────────────╯
Processing ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5,000/5,000 0:00:02

┌──────────┬───────┬───────────────────────────────────────┐
│ [FIX]    │    42 │ Stripped whitespace from fields        │
│ [FIX]    │     7 │ Normalized role "human" → "user"       │
│ [SKIP]   │     3 │ Malformed JSON lines                   │
│ [WARN]   │     2 │ Single character assistant response     │
└──────────┴───────┴───────────────────────────────────────┘

╭───────────────────── Dataset Stats ──────────────────────╮
│ Examples     4,997      Avg tokens    312                │
│ Min tokens   48         Max tokens    3,841              │
│ With system  63%        Multi-turn    28%                │
╰──────────────────────────────────────────────────────────╯

✓ Converted 4,997 examples → dataset.openai_chat.jsonl
```

## What it does

```
                        ┌─────────────┐
  alpaca ──────┐        │             │        ┌──── openai-chat
  sharegpt ────┤        │             │        ├──── alpaca
  openai-chat ─┤───────>│    ftml     │───────>├──── sharegpt
  chatml ──────┤        │             │        ├──── chatml
  csv ─────────┘        │             │        └──── together
                        └─────────────┘
                     auto-detect + fix
                      + validate + stats
```

**Any input format. Any output format. Zero data loss.**

## Before ftml

```python
# convert_sharegpt_to_openai.py (your 3rd throwaway script this week)
import json

with open("data.jsonl") as f:
    for line in f:
        obj = json.loads(line)
        messages = []
        for turn in obj["conversations"]:
            role = "user" if turn["from"] == "human" else "assistant"
            messages.append({"role": role, "content": turn["value"]})
        # wait, what about system messages?
        # what about "gpt" vs "assistant"?
        # what about empty content?
        # what about the 47 malformed lines?
        # ...
```

## After ftml

```bash
ftml convert data.jsonl --to openai-chat --fix
```

That's it.

## Features

- **Auto-detection** -- don't even tell it the input format, it figures it out
- **Auto-fix** -- whitespace, role normalization, trailing turns, empty system prompts
- **Platform validation** -- validate against OpenAI, Together, Axolotl, Unsloth, HuggingFace rules before uploading
- **Token counting** -- know your dataset stats before you pay for a training run
- **Train/eval split** -- `--split 0.9` and you're done
- **Streaming** -- handles large files without loading everything into memory
- **Rich terminal UI** -- progress bars, colored tables, histograms
- **Lossless roundtrip** -- convert A to B to A without losing data

## Supported formats

| Format | Read | Write | Used by |
|--------|:----:|:-----:|---------|
| **alpaca** | :white_check_mark: | :white_check_mark: | Stanford Alpaca, Dolly, most HuggingFace instruction datasets |
| **sharegpt** | :white_check_mark: | :white_check_mark: | ShareGPT, FastChat, Vicuna, WizardLM |
| **openai-chat** | :white_check_mark: | :white_check_mark: | OpenAI fine-tuning API, Together AI |
| **chatml** | :white_check_mark: | :white_check_mark: | Qwen, Yi, many open-source models |
| **csv** | :white_check_mark: | :white_check_mark: | Spreadsheets, quick prototyping |
| **together** | | :white_check_mark: | Together AI (OpenAI format + Together-specific validation) |

## Platform validation

Know your data is valid **before** you upload and wait for a training run to fail:

```bash
ftml validate my_data.jsonl --platform openai
```

| Platform | Min Examples | Max Tokens | Key Rules |
|----------|:-----------:|:----------:|-----------|
| **OpenAI** | 10 | 16,384 | Must have user + assistant roles |
| **Together** | 1 | 8,192 | System prompt optional |
| **Axolotl** | 1 | -- | Warns if missing system prompt |
| **Unsloth** | 1 | 4,096 | Warns on default context overflow |
| **HuggingFace** | 1 | -- | JSONL structure + Unicode checks |

## Auto-fix engine

`--fix` automatically repairs these common issues:

| Problem | Fix |
|---------|-----|
| Trailing/leading whitespace | Stripped from all fields |
| `"human"` / `"gpt"` roles | Normalized to `"user"` / `"assistant"` |
| Empty system prompt | Removed (set to null) |
| Consecutive same-role turns | Merged |
| Conversation ending on user turn | Trailing turn removed |
| Malformed JSON lines | Skipped + logged with line number |

Unfixable issues are flagged as warnings so you can review them manually.

## Quick reference

```bash
# Convert (auto-detects input format)
ftml convert data.jsonl --to openai-chat

# Convert + fix + validate for a platform
ftml convert data.jsonl --to openai-chat --fix --validate --platform openai

# Just validate (no conversion)
ftml validate data.jsonl --platform together

# What format is this?
ftml detect mystery_file.jsonl

# Dataset overview
ftml stats data.jsonl

# Train/eval split
ftml convert data.jsonl --to openai-chat --split 0.9

# Dry run (validate without writing)
ftml convert data.jsonl --to openai-chat --fix --validate --dry-run
```

<details>
<summary><strong>Full CLI options</strong></summary>

### `ftml convert`

```
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
  --format FORMAT        Declare format (else auto-detect)
  --platform PLATFORM    Platform-specific rules
  --max-tokens INT       Per-example token limit
  --strict               Treat warnings as errors (exit 1)
```

### `ftml detect` / `ftml stats` / `ftml formats`

```
ftml detect <file>                    # Auto-detect format
ftml stats <file> [--format FORMAT]   # Dataset statistics
ftml formats                          # List all formats + platform rules
```

### Exit codes

| Code | Meaning |
|:----:|---------|
| 0 | Success |
| 1 | Validation errors |
| 2 | File not found |
| 3 | Detection failed |

</details>

## Contributing

Adding a new format is three steps:

1. Create `ftml/formats/your_format.py` with a `Reader` and `Writer`
2. Add it to the registry in `ftml/formats/__init__.py`
3. Add sample data + roundtrip test

```bash
pip install -e ".[dev]"
pytest tests/ -v   # 93 tests, all passing
```

## License

MIT -- do whatever you want with it.

---

<p align="center">
  <strong>If ftml saved you from writing another conversion script, <a href="https://github.com/mmoselhy/ftml">star the repo</a></strong> :star:
</p>
