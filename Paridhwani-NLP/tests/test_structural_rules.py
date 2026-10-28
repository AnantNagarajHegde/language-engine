import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from structural_rules import match_structural_rule, diagnose_unmatched_answer


def test_unknown_quest_does_not_crash():
    result = match_structural_rule("unknown_quest", "unknown_step", "random text")
    assert result is None or isinstance(result, dict)


def test_unmatched_diagnosis_does_not_crash():
    result = diagnose_unmatched_answer("unknown_quest", "unknown_step", "random text")
    assert result is None or isinstance(result, dict)
