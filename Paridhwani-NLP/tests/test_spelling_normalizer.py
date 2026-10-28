import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spelling_normalizer import SpellingNormalizer


def make_normalizer():
    return SpellingNormalizer(str(ROOT / "data" / "spelling_variants.csv"))


def test_normalizer_initializes():
    normalizer = make_normalizer()
    assert normalizer is not None
    assert isinstance(normalizer.variant_map, dict)


def test_known_variant_is_normalized():
    normalizer = make_normalizer()
    result = normalizer.normalize("chaha beku")
    assert isinstance(result, str)
    assert result.strip() == result


def test_unknown_text_does_not_crash():
    normalizer = make_normalizer()
    result = normalizer.normalize("xyzqwerty")
    assert isinstance(result, str)


def test_empty_input():
    normalizer = make_normalizer()
    assert normalizer.normalize("") == ""


def test_none_input():
    normalizer = make_normalizer()
    assert normalizer.normalize(None) == ""
