import re
import inflect

inflect_engine = inflect.engine()

CURRENCY_UNITS = {
    "$": ("dollar", "cent"),
    "€": ("euro", "cent"),
    "£": ("pound", "pence"),
    "¥": ("yen", "sen"),
}

def _clean_style(s: str) -> str:
    s = s.replace("-", " ").replace(",", " ")
    return re.sub(r"\s+", " ", s).strip()

def _int_words(n: int) -> str:
    return _clean_style(inflect_engine.number_to_words(n, andword="", zero="zero"))

def _ordinal_words(n: int) -> str:
    return _clean_style(inflect_engine.number_to_words(inflect_engine.ordinal(n), andword="", zero="zero"))

def _year_words(n: int) -> str:
    first, second = divmod(n, 100)
    return _clean_style(
        f"{inflect_engine.number_to_words(first, andword='', zero='zero')} "
        f"{inflect_engine.number_to_words(second, andword='', zero='zero')}"
    )

def normalize_text(text: str) -> str:
    pattern = re.compile(
        r"""(?<![A-Za-z])
            (?P<cur>[$€£¥])?             # optional currency
            (?P<int>\d{1,3}(?:,\d{3})+|\d+)
            (?:\.(?P<frac>\d+))?         # optional decimal
            (?P<ord>st|nd|rd|th)?        # optional ordinal suffix
            (?P<unit>[A-Za-z%°]+)?       # optional unit like m, kg, km, %
        """,
        re.VERBOSE,
    )

    def repl(m: re.Match) -> str:
        cur = m.group("cur")
        int_part = m.group("int")
        frac = m.group("frac")
        ord_suffix = m.group("ord")
        unit = m.group("unit") or ""

        had_commas = "," in int_part
        n = int(int_part.replace(",", ""))

        if ord_suffix:
            words = _ordinal_words(n)

        elif cur:
            main_unit, sub_unit = CURRENCY_UNITS.get(cur, ("currency", "cent"))
            main_words = _int_words(n)
            main_unit = inflect_engine.plural(main_unit, n)

            if frac and not set(frac) == {"0"}:
                cents = int(frac[:2].ljust(2, "0"))
                cents_words = _int_words(cents)
                sub_unit = inflect_engine.plural(sub_unit, cents)
                words = f"{main_words} {main_unit} {cents_words} {sub_unit}"
            else:
                words = f"{main_words} {main_unit}"

        elif frac:
            if set(frac) == {"0"}:
                words = _int_words(n)
            else:
                words = _clean_style(
                    _int_words(n) + " point " + " ".join(_int_words(int(d)) for d in frac)
                )

        else:
            is_year = (1500 <= n <= 1999) and not had_commas
            words = _year_words(n) if is_year else _int_words(n)

        if unit:
            return f"{words} {unit}"
        return words

    return pattern.sub(repl, text)

# --- Example usage ---
if __name__ == "__main__":
    samples = [
        "I was born in 1994.",
        "The 31st person arrived 1,994 days later.",
        "In 2021, I came 2nd.",
        "He lived in 1899.",
        "However, my dad explains that my uncle still has $2,000.91 of debt owed towards our family.",
        "It costs about 2.5 times more now.",
        "I paid €1,500.00 for that.",
        "The car is 5m long.",
        "what about 1,365.2315"
    ]
    for s in samples:
        print(f"{s} -> {normalize_text(s)}")
