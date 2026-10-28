import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from normalizer import normalize_text


def test_none_returns_empty_string():
    assert normalize_text(None) == ""


def test_lowercase_and_trim():
    assert normalize_text("  NAMASKARA  ") == "namaskara"


def test_punctuation_is_removed():
    assert normalize_text("Hello!!!") == "hello"


def test_multiple_spaces_are_collapsed():
    assert normalize_text("chaha    beku") == "chaha beku"


def test_repeated_characters_are_reduced():
    assert normalize_text("bekuuuu") == "beku"


def test_repeated_romanized_vowels_are_reduced():
    assert normalize_text("Dhanyavaadaa") == "dhanyavada"


def test_kannada_text_is_preserved():
    assert normalize_text("ನಮಸ್ಕಾರ") == "ನಮಸ್ಕಾರ"


def test_digits_are_preserved():
    assert normalize_text("test 123") == "test 123"


def test_empty_string():
    assert normalize_text("") == ""


def test_punctuation_only():
    assert normalize_text("!!!...") == ""
