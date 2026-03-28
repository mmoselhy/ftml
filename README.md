<p align="center">
  <br>
  <img src="https://img.shields.io/badge/ftml-v0.1.0-black?style=for-the-badge" alt="ftml">
  <br><br>
  <strong>Convert any LLM fine-tuning dataset to any format.</strong><br>
  One command. Auto-detect. Auto-fix. Validate.
  <br><br>
  <a href="https://pypi.org/project/ftml-cli/"><img src="https://img.shields.io/pypi/v/ftml-cli?color=%2334D058&label=pypi" alt="PyPI"></a>&nbsp;
  <a href="https://pypi.org/project/ftml-cli/"><img src="https://img.shields.io/pypi/pyversions/ftml-cli" alt="Python 3.10+"></a>&nbsp;
  <a href="LICENSE"><img src="https://img.shields.io/github/license/mmoselhy/ftml" alt="MIT License"></a>
</p>

---

```bash
pip install ftml-cli
```

```bash
ftml convert dataset.jsonl --to openai-chat --fix --validate --platform openai
```

```
╭──────────────────────────────────────────────────────────╮
│ ftml · LLM dataset format converter                      │
│ sharegpt → openai-chat  ·  dataset.jsonl                 │
╰──────────────────────────────────────────────────────────╯
Processing ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5,000/5,000 0:00:02

┌──────────┬───────┬────────────────────────────────────────┐
│ [FIX]    │    42 │ Stripped whitespace from fields         │
│ [FIX]    │     7 │ Normalized role "human" → "user"        │
│ [SKIP]   │     3 │ Malformed JSON lines                    │
└──────────┴───────┴────────────────────────────────────────┘

╭───────────────────── Dataset Stats ──────────────────────╮
│ Examples     4,997      Avg tokens    312                │
│ Min tokens   48         Max tokens    3,841              │
│ With system  63%        Multi-turn    28%                │
╰──────────────────────────────────────────────────────────╯

✓ Converted 4,997 examples → dataset.openai_chat.jsonl
```

## How it works

```
  alpaca ──────┐                       ┌──── openai-chat
  sharegpt ────┤                       ├──── alpaca
  openai-chat ─┤────>  ftml  ────>     ├──── sharegpt
  chatml ──────┤    detect / fix /     ├──── chatml
  csv ─────────┘    validate / stats   └──── together
```

Reads any format. Writes any format. Auto-detects the input. Fixes common issues. Validates against platform rules. No data loss.

## Formats

| Format | In | Out | Structure |
|--------|:--:|:---:|-----------|
| **alpaca** | :white_check_mark: | :white_check_mark: | `{"instruction", "input", "output"}` |
| **sharegpt** | :white_check_mark: | :white_check_mark: | `{"conversations": [{"from", "value"}]}` |
| **openai-chat** | :white_check_mark: | :white_check_mark: | `{"messages": [{"role", "content"}]}` |
| **chatml** | :white_check_mark: | :white_check_mark: | `<\|im_start\|>role\ncontent<\|im_end\|>` |
| **csv** | :white_check_mark: | :white_check_mark: | `instruction,input,output` columns |
| **together** | | :white_check_mark: | OpenAI format + Together validation |

## Commands

```bash
ftml convert data.jsonl --to openai-chat                # convert (auto-detects input)
ftml convert data.jsonl --to openai-chat --fix           # convert + auto-fix issues
ftml convert data.jsonl --to openai-chat --split 0.9     # convert + train/eval split
ftml validate data.jsonl --platform openai               # validate without converting
ftml detect data.jsonl                                   # identify the format
ftml stats data.jsonl                                    # dataset overview + token counts
ftml formats                                             # list all formats + platforms
```

## Auto-fix (`--fix`)

| Issue | Action |
|-------|--------|
| Trailing/leading whitespace | Stripped |
| `"human"` / `"gpt"` role names | Normalized to `"user"` / `"assistant"` |
| Empty system prompt | Removed |
| Consecutive same-role turns | Merged |
| Conversation ending on user turn | Trailing turn removed |
| Malformed JSON lines | Skipped + line number logged |

Unfixable issues (single-char responses, instruction = output) are flagged as warnings.

## Platform validation (`--platform`)

Validate before you upload. Catch errors before your training run fails.

| Platform | Min Examples | Max Tokens | Notes |
|----------|:-----------:|:----------:|-------|
| **openai** | 10 | 16,384 | Requires user + assistant roles |
| **together** | 1 | 8,192 | System prompt optional |
| **axolotl** | 1 | -- | Warns if missing system prompt |
| **unsloth** | 1 | 4,096 | Default context window warning |
| **huggingface** | 1 | -- | JSONL + Unicode validation |

<details>
<summary><strong>All CLI options</strong></summary>

### `ftml convert`

```
  --from FORMAT          Source format (auto-detect if omitted)
  --to FORMAT            Target format (default: openai-chat)
  --output, -o PATH      Output file path
  --validate             Validate after converting
  --fix                  Auto-fix common issues
  --platform PLATFORM    Validate against platform rules
  --token-model MODEL    Tokenizer (default: cl100k_base)
  --max-tokens INT       Per-example token limit
  --split FLOAT          Train/eval split ratio
  --quiet, -q            Errors only
  --dry-run              Validate without writing
```

### `ftml validate`

```
  --format FORMAT        Declare format (else auto-detect)
  --platform PLATFORM    Platform-specific rules
  --max-tokens INT       Per-example token limit
  --strict               Treat warnings as errors
```

### Other commands

```
ftml detect <file>                    # Detect format + confidence
ftml stats <file> [--format FORMAT]   # Token counts, turn distribution
ftml formats                          # List formats + platform rules
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

1. Add `ftml/formats/your_format.py` with a `Reader` and `Writer`
2. Register in `ftml/formats/__init__.py`
3. Add sample data + test in `tests/`

```bash
pip install -e ".[dev]" && pytest tests/ -v
```

## License

MIT
