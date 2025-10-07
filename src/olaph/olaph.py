import re
import string
import logging
from pathlib import Path
from typing import Dict, List, Optional

import spacy
from lingua import Language, LanguageDetectorBuilder
from num2words import num2words
import requests
import zipfile
import io

from .german_normalizer import Normalizer


class Olaph:
    """
    OLaPh phonemizer supporting DE, EN, FR, ES.
    You should not have to use any function besides phonemize_text.
    """

    def __init__(self):
        print("Initializing OLaPh...")
        self.base_dir = Path(__file__).resolve().parent
        self.langs = ("en", "de", "fr", "es")
        self.normalizer = Normalizer()

        self.dictionary_path = self.base_dir / "dictionaries"
        if not self.dictionary_path.exists():
            #download dictionaries from opendata
            print("Dictionaries do not exist locally. Downloading...")
            response = requests.get("https://opendata.iisys.de/opendata/Datasets/olaph/dictionaries.zip")
            response.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(self.base_dir)

        self.lang_dict: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.all_lang_word_dict: Dict[str, Dict[str, str]] = {}
        self.lang_letter_dict: Dict[str, Dict[str, str]] = {}
        self.lang_abbreviations_dict: Dict[str, Dict[str, str]] = {}
        self.lang_replacements_dict: Dict[str, Dict[str, str]] = {}
        self.all_lang_replacements_dict: Dict[str, str] = {}
        self.word_probabilities: Dict[str, Dict[str, int]] = {}

        self.failed_words: List[str] = []
        self.good_splits: List[str] = []
        self.bad_splits: List[str] = []

        self.nlps = {
            "de": spacy.load("de_core_news_sm"),
            "en": spacy.load("en_core_web_sm"),
            "fr": spacy.load("fr_core_news_sm"),
            "es": spacy.load("es_core_news_sm"),
        }
        self.detector = LanguageDetectorBuilder.from_languages(
            Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH
        ).with_minimum_relative_distance(0.6).build()

        self._load_dictionaries()
        self._load_general()
        self._load_replacements()
        self._load_abbreviations()
        self._load_letter_dictionaries()
        self._load_probabilities()

        print("OLaPh initialized!")

    def _load_dictionaries(self):
        for lang in self.langs:
            self.lang_dict[lang] = {}
            dict_path = self.base_dir / "dictionaries" / lang / f"{lang}.txt"
            with open(dict_path, encoding="utf-8") as rf:
                for line in rf:
                    parts = line.strip().split("\t")
                    grapheme, phoneme = parts[:2]
                    pos = parts[2] if len(parts) > 2 else "base"
                    phoneme = phoneme.split(",")[0].replace("/", "")
                    grapheme = grapheme.lower()
                    self.lang_dict[lang].setdefault(grapheme, {})[pos] = phoneme
                    self.all_lang_word_dict.setdefault(grapheme, {"base": phoneme})

    def _load_general(self):
        path = self.base_dir / "dictionaries/general.txt"
        with open(path, encoding="utf-8") as rf:
            for line in rf:
                grapheme, phoneme = line.strip().split("\t")
                phoneme = phoneme.split(",")[0].replace("/", "")
                self.all_lang_word_dict.setdefault(grapheme.lower(), {"base": phoneme})

    def _load_replacements(self):
        general_path = self.base_dir / "dictionaries/general_replacements.txt"
        with open(general_path, encoding="utf-8") as rf:
            for line in rf:
                grapheme, replacement = line.strip().split("\t")
                self.all_lang_replacements_dict[grapheme] = replacement

        for lang in self.langs:
            path = self.base_dir / f"dictionaries/{lang}/{lang}_replacements.txt"
            self.lang_replacements_dict[lang] = {}
            if not path.exists():
                continue
            with open(path, encoding="utf-8") as rf:
                for line in rf:
                    grapheme, replacement = line.strip().split("\t")
                    self.lang_replacements_dict[lang][grapheme] = replacement

    def _load_abbreviations(self):
        for lang in self.langs:
            self.lang_abbreviations_dict[lang] = {}
            path = self.base_dir / f"dictionaries/{lang}/{lang}_abbreviations.txt"
            if not path.exists():
                continue
            with open(path, encoding="utf-8") as rf:
                for line in rf:
                    grapheme, phoneme = line.strip().split("\t")
                    self.lang_abbreviations_dict[lang][grapheme] = phoneme.replace("/", "")

    def _load_letter_dictionaries(self):
        for lang in self.langs:
            self.lang_letter_dict[lang] = {}
            path = self.base_dir / f"dictionaries/{lang}/{lang}_capitals.txt"
            if not path.exists():
                continue
            with open(path, encoding="utf-8") as rf:
                for line in rf:
                    letter, phoneme = line.strip().split("\t")
                    self.lang_letter_dict[lang][letter] = phoneme.replace("/", "")

    def _load_probabilities(self):
        for lang in self.langs:
            self.word_probabilities[lang] = {}
            path = self.base_dir / f"word_probabilities/word_probabilities_{lang}.txt"
            if not path.exists():
                continue
            with open(path, encoding="utf-8") as rf:
                for line in rf:
                    word, count = line.strip().split("\t")
                    self.word_probabilities[lang][word] = int(count)

    def _lookup(self, word: str, dictionary: dict, pos: Optional[str], tense: Optional[str]) -> Optional[str]:
        entry = dictionary.get(word)
        if not entry:
            return None
        key = (pos or "") + (tense or "")
        return entry.get(key) or entry.get(pos) or entry.get("base")

    def _transformations(self, word: str):
        """Generate common word variants for fallback lookups."""
        yield word
        if word:
            yield word[0].lower() + word[1:]
        yield word.capitalize()
        yield word.replace("-", "")
        yield word.replace("ß", "ss")
        yield word.replace("ß", "ss").replace("-", "")

    def phonemize_word(self, word: str, lang: str, pos: Optional[str] = None, tense: Optional[str] = None) -> str:
        if not word or word.isdigit():
            return ""

        for candidate in self._transformations(word):
            phoneme = self._lookup(candidate, self.lang_dict[lang], pos, tense)
            if phoneme:
                return phoneme

        for candidate in self._transformations(word):
            phoneme = self._lookup(candidate, self.all_lang_word_dict, pos, tense)
            if phoneme:
                return phoneme

        cleaned = re.sub(r"[^\w\s]", "", word)
        phoneme = self._lookup(cleaned, self.lang_dict[lang], pos, tense) or self._lookup(
            cleaned, self.all_lang_word_dict, pos, tense
        )
        if phoneme:
            return phoneme

        self.failed_words.append(word)
        return word

    def _normalize_acronym(self, text: str) -> str:
        if re.fullmatch(r"(?:[A-Z]\.){2,}[A-Z]\.?", text):
            return text.replace(".", "")
        return text

    def _spell_letters(self, text: str, lang: str) -> Optional[str]:
        letters = self.lang_letter_dict.get(lang, {})
        if not letters:
            return None
        spelled = " ".join(letters.get(ch, "") for ch in text if ch.isalpha())
        return spelled.strip() if spelled else None

    def _resolve_abbreviation(self, text: str, lang: str) -> Optional[str]:
        if text in self.lang_abbreviations_dict.get(lang, {}):
            return self.lang_abbreviations_dict[lang][text]

        if text in self.lang_abbreviations_dict.get("en", {}):
            return self.lang_abbreviations_dict["en"][text]

        for other in self.langs:
            if other in (lang, "en"):
                continue
            if text in self.lang_abbreviations_dict.get(other, {}):
                return self.lang_abbreviations_dict[other][text]

        return self._spell_letters(text, lang) or self._spell_letters(text, "en")

    def _preprocess_sentence(self, sentence: str, lang: str) -> str:
        sentence = sentence.replace("’", "").replace("-", " ")
        sentence = re.sub(r" +", " ", sentence)
        for k, v in self.lang_replacements_dict.get(lang, {}).items():
            pattern = rf"\b{re.escape(k)}\b"
            sentence = re.sub(pattern, f" {v} ", sentence)

        for k, v in self.all_lang_replacements_dict.items():
            pattern = rf"\b{re.escape(k)}\b"
            sentence = re.sub(pattern, f" {v} ", sentence)

        sentence = re.sub(r" +", " ", sentence).strip()

        if lang == "de":
            sentence = self.normalizer.normalize(sentence)
        else:
            sentence = self._normalize_numbers(sentence, lang)
            sentence = re.sub(r"\d", "", sentence)

        return sentence.strip()

    def _normalize_numbers(self, sentence: str, lang: str) -> str:
        """Replace numbers in text with words."""
        if lang in ["fr", "es"]:
            number_pattern = r"\b\d+(,\d+)?%?|\$\d+(,\d+)?|\d+\.\d+"
            decimal_separator = ","
        else:
            number_pattern = r"\b\d+(\.\d+)?%?|\$\d+(\.\d+)?|\d+,\d+"
            decimal_separator = "."

        def replace_number(match):
            num_str = match.group()
            try:
                if num_str.endswith("%"):
                    number = float(num_str[:-1].replace(decimal_separator, "."))
                    return num2words(number, lang=lang) + " percent"
                elif num_str.startswith("$"):
                    number = float(num_str[1:].replace(",", "").replace(decimal_separator, "."))
                    return "dollars " + num2words(number, lang=lang)
                elif decimal_separator in num_str:
                    return num2words(float(num_str.replace(decimal_separator, ".")), lang=lang)
                elif "," in num_str and lang == "en":
                    return num2words(int(num_str.replace(",", "")), lang=lang)
                else:
                    return num2words(int(num_str), lang=lang)
            except ValueError:
                return num_str

        return re.sub(number_pattern, replace_number, sentence)

    def _phonemize_sentence(self, sentence: str, lang: str) -> str:
        """Phonemize one sentence, fixing punctuation and spacing."""
        doc = self.nlps[lang](sentence)
        tokens = []

        for token in doc:
            raw = token.text

            # Punctuation: keep tight
            if raw in string.punctuation:
                tokens.append(raw)
                continue

            # Acronym or abbreviation detection
            norm = self._normalize_acronym(raw)
            is_acronym = (
                len(norm) > 1
                and not norm.isdigit()
                and any(c.isalpha() for c in norm)
                and all(c.isupper() or c.isdigit() for c in norm)
            )

            if is_acronym:
                resolved = self._resolve_abbreviation(norm, lang)
                tokens.append(resolved if resolved else raw)
                continue

            # Regular words
            try:
                tense_list = token.morph.get("Tense")
                tense = tense_list[0] if tense_list else None
                phoneme = self.phonemize_word(raw.lower(), lang, pos=token.pos_, tense=tense)
                tokens.append(phoneme)
            except Exception as ex:
                logging.error(f"Could not phonemize '{raw}': {ex}")
                self.failed_words.append(raw)
                tokens.append(raw)

        out = " ".join(tokens).strip()
        # spacing cleanup only
        out = re.sub(r"\s+([,.!?;:])", r"\1", out)
        out = re.sub(r"([(\[{])\s+", r"\1", out)
        out = re.sub(r"\s+([)\]}])", r"\1", out)
        return out


    def phonemize_text(self, text: str, lang: str = "de") -> str:
        """
        Phonemize text into a phoneme string.
        Handles sentence segmentation, abbreviation resolution, normalization,
        and punctuation spacing.
        """
        nlp = self.nlps[lang]
        sentences = [s.text for s in nlp(text).sents]
        results = []

        for sentence in sentences:
            processed = self._preprocess_sentence(sentence, lang)
            phonemized = self._phonemize_sentence(processed, lang)
            if phonemized:
                results.append(phonemized)

        # join all phonemized sentences
        final_text = " ".join(results).strip()
        final_text = re.sub(r"\s+([,.!?;:])", r"\1", final_text)

        # ✅ Only add one period if the whole text has none
        if not re.search(r"[.!?]\s*$", final_text):
            final_text += "."

        return final_text
