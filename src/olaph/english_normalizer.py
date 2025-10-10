import re
import inflect

inflect_engine = inflect.engine()

def _number_to_words(num: int, is_ordinal=False, is_year=False) -> str:
    if is_ordinal:
        # inflect 7.x pattern for ordinal words
        words = inflect_engine.number_to_words(inflect_engine.ordinal(num), andword="", zero="zero")
    elif is_year and 1500 <= num <= 1999:
        # year style: 1994 -> nineteen ninety four
        first, second = divmod(num, 100)
        first_part = inflect_engine.number_to_words(first, andword="", zero="zero")
        second_part = inflect_engine.number_to_words(second, andword="", zero="zero")
        words = f"{first_part} {second_part}"
    else:
        words = inflect_engine.number_to_words(num, andword="", zero="zero")

    words = words.replace("-", " ").replace(",", " ")
    return re.sub(r"\s+", " ", words).strip()

def _normalize_token(token: str) -> str:
    had_comma = "," in token
    clean = token.replace(",", "")

    m = re.match(r"^(\d+)(st|nd|rd|th)$", clean, flags=re.IGNORECASE)
    if m:
        return _number_to_words(int(m.group(1)), is_ordinal=True)

    if clean.isdigit():
        num = int(clean)
        return _number_to_words(num, is_year=(not had_comma and 1500 <= num <= 1999))

    return token

def normalize_text(text: str) -> str:
    pattern = r"\b(?:\d{1,3}(?:,\d{3})+|\d+)(?:st|nd|rd|th)?\b"
    return re.sub(pattern, lambda m: _normalize_token(m.group(0)), text)