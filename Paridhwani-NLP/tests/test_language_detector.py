import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from language_detector import LanguageDetector


def make_detector():
    return LanguageDetector(str(ROOT / "data" / "responses_train.csv"))


def test_detector_initializes():
    detector = make_detector()
    assert detector is not None


def test_detect_empty_input_does_not_crash():
    detector = make_detector()
    result = detector.detect("")
    assert result is not None


def test_detect_kannada_input_does_not_crash():
    detector = make_detector()
    result = detector.detect("ನಮಸ್ಕಾರ")
    assert result is not None


def test_detect_romanized_input_does_not_crash():
    detector = make_detector()
    result = detector.detect("chaha beku")
    assert result is not None


def test_detect_mixed_input_does_not_crash():
    detector = make_detector()
    result = detector.detect("please chaha beku")
    assert result is not None
