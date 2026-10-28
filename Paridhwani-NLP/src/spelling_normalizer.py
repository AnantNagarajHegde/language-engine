
import pandas as pd
from pathlib import Path
from normalizer import normalize_text


class SpellingNormalizer:
    def __init__(self, variants_path):
        self.variants_path = Path(variants_path)
        self.variant_map = {}
        self.load_variants()

    def load_variants(self):
        if not self.variants_path.exists():
            raise FileNotFoundError(
                f"Spelling variants file not found: {self.variants_path}"
            )

        df = pd.read_csv(self.variants_path).fillna("")

        required = {"canonical_kanglish", "variant"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"Missing columns in spelling variants: {sorted(missing)}"
            )

        for _, row in df.iterrows():
            canonical = normalize_text(row["canonical_kanglish"])
            variant = normalize_text(row["variant"])

            if canonical and variant:
                self.variant_map[variant] = canonical

    def normalize(self, text):
        normalized = normalize_text(text)

        # First try the complete input as one known spelling variant.
        if normalized in self.variant_map:
            return self.variant_map[normalized]

        # Otherwise normalize individual words using known variants.
        words = normalized.split()
        normalized_words = [
            self.variant_map.get(word, word) for word in words
        ]

        return " ".join(normalized_words)
