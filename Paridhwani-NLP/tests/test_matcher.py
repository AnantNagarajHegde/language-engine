import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from matcher import AnswerMatcher


def make_matcher():
    return AnswerMatcher(str(ROOT / "data"))


def test_matcher_initializes():
    matcher = make_matcher()
    assert matcher is not None


def test_known_answer_does_not_crash():
    matcher = make_matcher()
    result = matcher.evaluate("q1_2", "q1_2_a", "Chaha beku")
    assert isinstance(result, dict)
    assert "outcome" in result


def test_empty_answer_does_not_crash():
    matcher = make_matcher()
    result = matcher.evaluate("q1_2", "q1_2_a", "")
    assert isinstance(result, dict)
    assert "outcome" in result


def test_unknown_answer_does_not_crash():
    matcher = make_matcher()
    result = matcher.evaluate("q1_2", "q1_2_a", "xyzqwerty unknown")
    assert isinstance(result, dict)
    assert "outcome" in result
