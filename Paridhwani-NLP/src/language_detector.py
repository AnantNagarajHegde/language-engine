
import re
import pandas as pd
from pathlib import Path
from normalizer import normalize_text


class LanguageDetector:
    def __init__(self, training_csv):
        self.training_csv = Path(training_csv)
        self.kanglish_words = set()
        self.hindi_words = set()
        self.english_words = set()
        self.load_vocabulary()

    def load_vocabulary(self):
        if not self.training_csv.exists():
            raise FileNotFoundError(self.training_csv)

        df = pd.read_csv(self.training_csv).fillna("")

        for _, row in df.iterrows():
            form = str(row["input_form"]).strip().lower()
            text = normalize_text(row["input_text"])
            words = set(re.findall(r"[a-z]+", text))

            if form == "kanglish":
                self.kanglish_words.update(words)
            elif form == "hindi_roman":
                self.hindi_words.update(words)
            elif form == "english":
                self.english_words.update(words)

        self.kanglish_words -= (
            self.hindi_words | self.english_words
        )

    def detect(self, text):
        if text is None or not str(text).strip():
            return "noise"

        text = str(text).strip()
        normalized = normalize_text(text)

        kannada_count = sum(
            1 for c in text
            if 0x0C80 <= ord(c) <= 0x0CFF and c.isalpha()
        )
        latin_words = re.findall(r"[a-z]+", normalized)
        has_latin = bool(latin_words)
        has_digits = any(c.isdigit() for c in text)

        if has_digits and not has_latin and not kannada_count:
            return "digits"
        if kannada_count and has_latin:
            return "mixed"
        if kannada_count:
            return "kannada"
        if not has_latin:
            return "noise"

        hindi_hits = sum(w in self.hindi_words for w in latin_words)
        kanglish_hits = sum(w in self.kanglish_words for w in latin_words)
        english_hits = sum(w in self.english_words for w in latin_words)

        if hindi_hits > kanglish_hits and hindi_hits > english_hits:
            return "hindi_roman"
        if kanglish_hits > 0 and kanglish_hits >= english_hits:
            return "kanglish"
        if english_hits > 0:
            return "english"

        return "noise"
