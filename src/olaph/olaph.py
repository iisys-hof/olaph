import regex as re
import string
import logging
from pathlib import Path
from typing import Dict, List, Optional
import unicodedata

import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex

from lingua import Language, LanguageDetectorBuilder
from num2words import num2words

from .german_normalizer import Normalizer
from .english_normalizer import normalize_text as normalize_english

TONE_MAP = {
    "¹": "˩",
    "²": "˨",
    "³": "˧",
    "⁴": "˦",
    "⁵": "˥",
    "⁷": "˥",
}
_TONE_TABLE = str.maketrans(TONE_MAP)


class NoGuessingRefusal(ValueError):
    """Raised by phonemize_word(..., guessing=False) when the word cannot be
    phonemized from the target-language dictionary alone and guessing would
    be required."""


class Olaph:
    """
    OLaPh phonemizer supporting DE, EN, FR, ES, PL.
    You should not have to use any function besides phonemize_text.
    """

    def __init__(self):
        print("Initializing OLaPh...")
        self.base_dir = Path(__file__).resolve().parent
        self.langs = ("en", "de", "fr", "es", "pl")
        self.normalizer = Normalizer()

        self.lang_dict: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.all_lang_word_dict: Dict[str, Dict[str, str]] = {}
        self.all_lang_word_source: Dict[str, str] = {}
        self.lang_letter_dict: Dict[str, Dict[str, str]] = {}
        self.lang_abbreviations_dict: Dict[str, Dict[str, str]] = {}
        self.lang_replacements_dict: Dict[str, Dict[str, str]] = {}
        self.all_lang_replacements_dict: Dict[str, str] = {}
        self.word_probabilities: Dict[str, Dict[str, int]] = {}

        self.failed_words: List[str] = []
        self.refused_words: List[str] = []
        self.good_splits: List[str] = []
        self.bad_splits: List[str] = []

        self.nlps = {
            "de": spacy.load("de_core_news_sm"),
            "en": spacy.load("en_core_web_sm"),
            "fr": spacy.load("fr_core_news_sm"),
            "es": spacy.load("es_core_news_sm"),
            "pl" : spacy.load("pl_core_news_sm"),
        }
        #tokenizer fix
        APOSTROPHE_TOKEN_RE = re.compile(
            r"^\p{L}+(?:['’`]\p{L}+)*['’`]?$",
            re.UNICODE
        )
        for lang, nlp in self.nlps.items():
            nlp = self.nlps[lang]
            nlp.tokenizer = Tokenizer(
                nlp.vocab,
                rules={},
                prefix_search=nlp.tokenizer.prefix_search,
                suffix_search=nlp.tokenizer.suffix_search,
                infix_finditer=compile_infix_regex(nlp.Defaults.infixes).finditer,
                token_match=APOSTROPHE_TOKEN_RE.match,
            )
            #sentencizer fix
        for nlp in self.nlps.values():
            if "parser" in nlp.pipe_names:
                nlp.disable_pipes("parser")
            nlp.add_pipe("sentencizer")
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
                    self.lang_dict[lang].setdefault(grapheme, {})
                    if pos not in self.lang_dict[lang][grapheme]:
                        self.lang_dict[lang][grapheme][pos] = phoneme

                    if grapheme not in self.all_lang_word_dict:
                        self.all_lang_word_dict[grapheme] = {"base": phoneme}
                        self.all_lang_word_source[grapheme] = lang

    def _load_general(self):
        path = self.base_dir / "dictionaries/general.txt"
        with open(path, encoding="utf-8") as rf:
            for line in rf:
                grapheme, phoneme = line.strip().split("\t")
                phoneme = phoneme.split(",")[0].replace("/", "")
                key = grapheme.lower()
                if key not in self.all_lang_word_dict:
                    self.all_lang_word_dict[key] = {"base": phoneme}
                    self.all_lang_word_source[key] = "general"

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

    def _lookup_all_lang(self, word: str, pos: Optional[str], tense: Optional[str], lang: str) -> Optional[str]:
        """Look up word in all_lang_word_dict, but only return a hit if the entry
        originated from the target language or from the language-independent general dict.
        This prevents e.g. an English entry for "largent" masking the correct French
        splitting of "l" + "argent"."""
        source = self.all_lang_word_source.get(word)
        if source is None or (source != lang and source != "general"):
            return None
        return self._lookup(word, self.all_lang_word_dict, pos, tense)

    def _lookup(self, word: str, dictionary: dict, pos: Optional[str], tense: Optional[str]) -> Optional[str]:
        entry = dictionary.get(word)
        #print(word, entry, pos, tense)
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

    def _get_splits(self, word, dictionary, memo=None, connecting_s=True):
        if memo is None:
            memo = {}

        if word in memo:
            return memo[word]

        if word in dictionary:
            memo[word] = ([word], [word], None)
            return memo[word]

        best_prefix_split = None
        best_suffix_split = None
        best_connecting_s_split = None

        for i in range(len(word), 0, -1):
            prefix = word[:i]
            suffix = word[i:]
            if prefix in dictionary:
                if suffix == "":
                    memo[word] = ([prefix], [prefix], None)
                    return memo[word]
                result = self._get_splits(suffix, dictionary, memo)
                if result is not None and result[0] is not None:
                    current_split = [prefix] + result[0]
                    if best_prefix_split is None or len(current_split) < len(best_prefix_split):
                        best_prefix_split = current_split

        for i in range(len(word), 0, -1):
            suffix = word[-i:]
            prefix = word[:-i]
            if suffix in dictionary:
                if prefix == "":
                    memo[word] = ([suffix], [suffix], None)
                    return memo[word]
                result = self._get_splits(prefix, dictionary, memo)
                if result is not None and result[1] is not None:
                    current_split = result[1] + [suffix]
                    if best_suffix_split is None or len(current_split) < len(best_suffix_split):
                        best_suffix_split = current_split

        if connecting_s:
            for i in range(1, len(word)-1):
                if word[i] == "s":
                    prefix = word[:i]
                    suffix = word[i+1:]
                    if self._get_splits(prefix, dictionary, memo) and self._get_splits(suffix, dictionary, memo):
                        split_prefix = self._get_splits(prefix, dictionary, memo)[0]
                        split_suffix = self._get_splits(suffix, dictionary, memo)[1]
                        if split_prefix is not None and split_suffix is not None:
                            current_split = split_prefix + ["s"] + split_suffix
                            if best_connecting_s_split is None or len(current_split) <= len(best_connecting_s_split):
                                best_connecting_s_split = current_split
                        else:
                            best_connecting_s_split = None
        memo[word] = (best_prefix_split, best_suffix_split, best_connecting_s_split)
        return memo[word]

    def _get_probability(self, word, max_length, lang, alpha=15):
        if word not in self.word_probabilities[lang]:
            return 0
        else:
            freq = self.word_probabilities[lang][word]
            length_weight = (len(word) / max_length) ** alpha
            if len(word) == 1:
                length_penalty = 0.1
            elif len(word) == 2:
                length_penalty = 0.5
            else:
                length_penalty = 1
            return freq * length_weight * length_penalty

    def _get_probabilities(self, words, lang="de"):
        probability = 0
        if not words:
            return 0
        for word in words:
            probability += self._get_probability(word, len("".join(words)), lang)

        word_count_penalty = (1 / len(words)) ** 15
        return probability * word_count_penalty

    def _get_best_part_words(self, part_words, lang="de"):
        probabilities = [self._get_probabilities(x, lang) for x in part_words if x is not None]
        if len(probabilities) > 0:
            best_index = max((v, i) for i, v in enumerate(probabilities))[1]
            best_index = probabilities.index(max(probabilities))
            return part_words[best_index]
        return None


    def phonemize_word(self, word: str, lang: str, pos: Optional[str] = None, tense: Optional[str] = None, guessing: bool = True) -> str:
        if not word or word.isdigit():
            return ""

        for candidate in self._transformations(word):
            phoneme = self._lookup(candidate, self.lang_dict[lang], pos, tense)
            if phoneme:
                return phoneme

        if guessing:
            for candidate in self._transformations(word):
                phoneme = self._lookup_all_lang(candidate, pos, tense, lang)
                if phoneme:
                    return phoneme

        cleaned = re.sub(r"[^\w\s]", "", word)
        phoneme = self._lookup(cleaned, self.lang_dict[lang], pos, tense)
        if not phoneme and guessing:
            phoneme = self._lookup_all_lang(cleaned, pos, tense, lang)
        if phoneme:
            return phoneme

        if guessing:
            #language detection fallback
            try:
                detected = self.detector.detect_language_of(word)
                detected_lang = detected.iso_code_639_1.name.lower()
                if detected_lang in self.langs and detected_lang != lang:
                    for candidate in self._transformations(word):
                        phoneme = self._lookup(candidate, self.lang_dict[detected_lang], pos, tense)
                        if phoneme:
                            return phoneme
            except Exception:
                pass

        part_words = self._get_best_part_words(self._get_splits(cleaned, self.lang_dict[lang]), lang)
        if not part_words:
            cleaned_word = re.sub(r'[^\w\s]', '', cleaned)
            part_words = self._get_best_part_words(self._get_splits(cleaned_word, self.lang_dict[lang]), lang)
        if not part_words and guessing:
            part_words = self._get_best_part_words(self._get_splits(cleaned_word, self.all_lang_word_dict), lang)
        if not part_words:
            if not guessing:
                self.refused_words.append(word)
                raise NoGuessingRefusal(f"Word not in target-language dictionary: {word}")
            self.failed_words.append(word)
            raise ValueError(f"Phonemization failed for word: {word}")
        word_phonemized = ""

        for part_word in part_words:
            part_lookup = self._lookup(part_word, self.lang_dict[lang], None, None)
            if not part_lookup and guessing:
                part_lookup = self._lookup_all_lang(part_word, None, None, lang)
            if not part_lookup:
                if not guessing:
                    self.refused_words.append(word)
                    raise NoGuessingRefusal(f"Word not in target-language dictionary: {word}")
                self.failed_words.append(f"{part_word}\t{lang}")
            else:
                word_phonemized += part_lookup

        if not word_phonemized:
            if not guessing:
                self.refused_words.append(word)
                raise NoGuessingRefusal(f"Word not in target-language dictionary: {word}")
            raise ValueError(f"Phonemization failed for word: {word}")
        return word_phonemized

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

    def _detect_foreign_entities(self, sentence: str, lang: str) -> Dict[str, str]:
        foreign_entities: Dict[str, str] = {}
        doc = self.nlps[lang](sentence)
        for ent in doc.ents:
            if ent.label_ != "ORG":
                continue
            try:
                detected = self.detector.detect_language_of(ent.text)
                ent_lang = detected.iso_code_639_1.name.lower()
            except Exception:
                continue
            if ent_lang not in self.langs or ent_lang == lang:
                continue
            for word in ent.text.split():
                word_clean = re.sub(r'[^\w\s]', '', word).strip()
                if not word_clean:
                    continue
                try:
                    foreign_entities[word_clean] = self.phonemize_word(word_clean, ent_lang)
                except Exception:
                    continue
        return foreign_entities

    def _preprocess_sentence(self, sentence: str, lang: str) -> str:
        sentence = sentence.replace("-", " ").replace("’", "'")
        sentence = re.sub(r" +", " ", sentence)
        for k, v in self.lang_replacements_dict.get(lang, {}).items():
            pattern = rf"(?<!\w){re.escape(k)}(?!\w)"
            sentence = re.sub(pattern, f" {v} ", sentence)

        for k, v in self.all_lang_replacements_dict.items():
            pattern = rf"(?<!\w){re.escape(k)}(?!\w)"
            sentence = re.sub(pattern, f" {v} ", sentence)

        sentence = re.sub(r" +", " ", sentence).strip()

        if lang == "de":
            sentence = self.normalizer.normalize(sentence)
        elif lang == "en":
            sentence = normalize_english(sentence)
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

    def _postprocess_sentence(self, phonemized_sentence:str, lang:str):
        #EN: dfferentiate pronunciation of the if the following word starts with a vowel phoneme. Does NOT catch special cases like "unit"
        phonemized_sentence_corrected= []
        phonemized_sentence_split = phonemized_sentence.split()

        for idx, word in enumerate(phonemized_sentence_split):
            phonemized_sentence_corrected.append(word)
            if idx > 0:
                if phonemized_sentence_split[idx-1] == "ðə" and re.sub(r"[ˈˌ]", "", word)[0] in "iyɨʉɯuɪʏʊeøɘɵɤoe̞ø̞əɤ̞o̞ɛœɜɞʌɔæɐaɶäɑɒ":
                    phonemized_sentence_corrected[idx-1] = "ði"
        return " ".join(phonemized_sentence_corrected).strip()

    def _phonemize_sentence(self, sentence: str, lang: str, foreign_entities: Optional[Dict[str, str]] = None, guessing: bool = True) -> str:
        """Phonemize one sentence, fixing punctuation and spacing."""
        doc = self.nlps[lang](sentence)
        tokens = []

        for token in doc:
            raw = token.text
            if raw in string.punctuation:
                tokens.append(raw)
                continue

            # acronym or abbr
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

            # foreign entity (NER)
            if foreign_entities:
                clean = re.sub(r'[^\w\s]', '', raw).strip()
                if clean in foreign_entities:
                    tokens.append(foreign_entities[clean])
                    continue

            try:
                tense_list = token.morph.get("Tense")
                tense = tense_list[0] if tense_list else None
                phoneme = self.phonemize_word(raw.lower(), lang, pos=token.pos_, tense=tense, guessing=guessing)
                tokens.append(phoneme)
            except NoGuessingRefusal:
                tokens.append(raw)
            except Exception as ex:
                logging.error(f"Could not phonemize '{raw}': {ex}")
                self.failed_words.append(raw)
                tokens.append(raw)

        out = " ".join(tokens).strip()
        # spacing cleanup
        out = re.sub(r"\s+([,.!?;:])", r"\1", out)
        out = re.sub(r"([(\[{])\s+", r"\1", out)
        out = re.sub(r"\s+([)\]}])", r"\1", out)
        return out


    def phonemize_text(self, text: str, lang: str = "de", normalize: bool = False, guessing: bool = True) -> str:
        """
        Phonemize text into a phoneme string.
        Handles sentence segmentation, abbreviation resolution, normalization,
        and punctuation spacing.

        Args:
            normalize: If True, strip all punctuation from the output and do not
                       append a trailing sentence-final period.
            guessing: If False, refuse to guess pronunciations for words not found
                    in the target-language dictionary.  Words that would require
                    cross-language or statistical fallbacks are left as-is in the
                    output and recorded in ``self.refused_words``.
        """
        nlp = self.nlps[lang]
        sentences = [s.text for s in nlp(text).sents]
        results = []

        for sentence in sentences:
            foreign_entities = self._detect_foreign_entities(sentence, lang)
            processed = self._preprocess_sentence(sentence, lang)
            phonemized = self._phonemize_sentence(processed, lang, foreign_entities, guessing=guessing)
            phonemized_postprocessed = self._postprocess_sentence(phonemized, lang)
            if phonemized_postprocessed:
                results.append(phonemized_postprocessed)

        final_text = " ".join(results).strip()
        final_text = final_text.translate(_TONE_TABLE)

        if normalize:
            final_text = final_text.translate(str.maketrans("", "", string.punctuation))
        else:
            final_text = re.sub(r"\s+([,.!?;:])", r"\1", final_text)
            if not re.search(r"[.!?]\s*$", final_text):
                final_text += "."

        final_text = unicodedata.normalize("NFC", final_text)
        return final_text.strip()
