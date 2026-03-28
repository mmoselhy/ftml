"""Format auto-detection logic."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DetectionResult:
    format_name: str
    confidence: float
    evidence: str


def detect_format(path: Path) -> DetectionResult:
    """Auto-detect the format of a dataset file."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() == ".csv":
        return DetectionResult("csv", 0.95, "File extension is .csv")

    # Read only the first few lines for detection
    sample_lines: list[str] = []
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if line:
                sample_lines.append(line)
            if len(sample_lines) >= 5:
                break

    if not sample_lines:
        raise ValueError(f"File is empty: {path}")

    # Check for ChatML tokens
    first_chunk = "\n".join(sample_lines)
    if "<|im_start|>" in first_chunk and "<|im_end|>" in first_chunk:
        return DetectionResult("chatml", 0.95, 'Found <|im_start|> and <|im_end|> tokens')

    scores: dict[str, tuple[float, str]] = {}
    json_objects = []

    for line in sample_lines:
        try:
            obj = json.loads(line)
            json_objects.append(obj)
        except json.JSONDecodeError:
            continue

    if not json_objects:
        if "," in sample_lines[0]:
            first_fields = [f.strip().lower() for f in sample_lines[0].split(",")]
            if "instruction" in first_fields or "output" in first_fields:
                return DetectionResult("csv", 0.85, "Comma-separated with instruction/output headers")
            return DetectionResult("csv", 0.5, "Comma-separated data (low confidence)")
        raise ValueError(f"Could not detect format of {path}. Use --from to specify the format explicitly.")

    obj = json_objects[0]

    if "instruction" in obj and "output" in obj:
        scores["alpaca"] = (0.95, 'Found "instruction" and "output" keys')

    if "messages" in obj and isinstance(obj["messages"], list):
        msgs = obj["messages"]
        if msgs and isinstance(msgs[0], dict) and "role" in msgs[0] and "content" in msgs[0]:
            scores["openai-chat"] = (0.95, 'Found "messages" key with "role"/"content" structure')

    if "conversations" in obj and isinstance(obj["conversations"], list):
        convs = obj["conversations"]
        if convs and isinstance(convs[0], dict) and "from" in convs[0] and "value" in convs[0]:
            scores["sharegpt"] = (0.95, 'Found "conversations" key with "from"/"value" structure')

    if "text" in obj and isinstance(obj["text"], str):
        if "<|im_start|>" in obj["text"]:
            scores["chatml"] = (0.95, 'Found "text" key containing ChatML tokens')

    if not scores:
        raise ValueError(f"Could not detect format of {path}. Use --from to specify the format explicitly.")

    best_format = max(scores, key=lambda k: scores[k][0])
    confidence, evidence = scores[best_format]
    return DetectionResult(best_format, confidence, evidence)
