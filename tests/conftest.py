from pathlib import Path

import pytest

SAMPLE_DATA_DIR = Path(__file__).parent / "sample_data"


@pytest.fixture
def sample_data_dir() -> Path:
    return SAMPLE_DATA_DIR


@pytest.fixture
def alpaca_path() -> Path:
    return SAMPLE_DATA_DIR / "alpaca.jsonl"


@pytest.fixture
def openai_chat_path() -> Path:
    return SAMPLE_DATA_DIR / "openai_chat.jsonl"


@pytest.fixture
def sharegpt_path() -> Path:
    return SAMPLE_DATA_DIR / "sharegpt.jsonl"


@pytest.fixture
def chatml_path() -> Path:
    return SAMPLE_DATA_DIR / "chatml.jsonl"


@pytest.fixture
def csv_path() -> Path:
    return SAMPLE_DATA_DIR / "csv_basic.csv"
