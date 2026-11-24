import re
import unicodedata


def canonical_words(values):
    """Put rule lexicons in the same representation as normalized input."""
    return {normalize_text(value) for value in values}


def normalize_text(text):
    """Normalize text for matching while preserving Kannada and digits."""
    if text is None:
        return ""

    text = unicodedata.normalize("NFKC", str(text)).lower().strip()

    cleaned = []
    for char in text:
        category = unicodedata.category(char)
        if category[0] in ("L", "M", "N") or char.isspace():
            cleaned.append(char)
        else:
            cleaned.append(" ")

    text = "".join(cleaned)
    text = re.sub(r"\s+", " ", text).strip()

    # Reduce long repeated characters: bekuuuuu -> bekuu
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)

    # Normalize repeated vowels in Romanized words:
    # dhanyavaadaa -> dhanyavada
    # chaaha -> chaha
    # bekuu -> beku
    # saakuuu -> saku
    text = re.sub(r"([aeiou])\1+", r"\1", text)

    return text
