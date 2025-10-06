import re
from num2words import num2words


def get_splits(word, dictionary, memo=None, connecting_s=True):
    if memo is None:
        memo = {}

    if word in memo:
        return memo[word]

    if word in dictionary:
        memo[word] = ([word], [word], None)
        return memo[word]

    best_prefix_split, best_suffix_split, best_connecting_s_split = None, None, None

    # prefix search
    for i in range(len(word), 0, -1):
        prefix, suffix = word[:i], word[i:]
        if prefix in dictionary:
            if not suffix:
                memo[word] = ([prefix], [prefix], None)
                return memo[word]
            result = get_splits(suffix, dictionary, memo)
            if result and result[0]:
                split = [prefix] + result[0]
                if not best_prefix_split or len(split) < len(best_prefix_split):
                    best_prefix_split = split

    # suffix search
    for i in range(len(word), 0, -1):
        suffix, prefix = word[-i:], word[:-i]
        if suffix in dictionary:
            if not prefix:
                memo[word] = ([suffix], [suffix], None)
                return memo[word]
            result = get_splits(prefix, dictionary, memo)
            if result and result[1]:
                split = result[1] + [suffix]
                if not best_suffix_split or len(split) < len(best_suffix_split):
                    best_suffix_split = split

    # connecting "s"
    if connecting_s:
        for i in range(1, len(word) - 1):
            if word[i] == "s":
                prefix, suffix = word[:i], word[i + 1:]
                if get_splits(prefix, dictionary, memo) and get_splits(suffix, dictionary, memo):
                    split_prefix = get_splits(prefix, dictionary, memo)[0]
                    split_suffix = get_splits(suffix, dictionary, memo)[1]
                    if split_prefix and split_suffix:
                        split = split_prefix + ["s"] + split_suffix
                        if not best_connecting_s_split or len(split) <= len(best_connecting_s_split):
                            best_connecting_s_split = split

    memo[word] = (best_prefix_split, best_suffix_split, best_connecting_s_split)
    return memo[word]


def get_probability(word, max_length, lang_probs, alpha=15):
    if word not in lang_probs:
        return 0
    freq = lang_probs[word]
    length_weight = (len(word) / max_length) ** alpha
    length_penalty = 0.1 if len(word) == 1 else 0.5 if len(word) == 2 else 1
    return freq * length_weight * length_penalty


def get_probabilities(words, lang_probs):
    if not words:
        return 0
    total = sum(get_probability(w, len("".join(words)), lang_probs) for w in words)
    return total * (1 / len(words)) ** 15


def get_best_part_words(part_words, lang_probs):
    scored = [(get_probabilities(x, lang_probs), x) for x in part_words if x]
    return max(scored, default=(0, None))[1]


def normalize_numbers(sentence, lang):
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
