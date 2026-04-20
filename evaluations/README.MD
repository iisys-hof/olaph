Evaluations for OLaPh, Gruut and espeak on the Wikipron dataset: https://github.com/CUNY-CL/wikipron

the "cleaned" results try to remove and replace symbols (for all framework outputs) in order to achieve better comparability between the framework outputs. Cleaning was conducted like this:

```python

exclude = "ʔʡʕʢʘǀǂǁǃˌˈʔˈːˈ  \u200B\u200C\u200D\uFEFF"

def clean_text(text, lang):
    if lang == "es":
        text = text.replace("β", "b").replace("ð", "d").replace("g", "x").replace("r", "ɾ")
        text = text.replace("oʊ", "əʊ")
    elif lang in ["en_uk", "en_us"]:
        text = text.replace("ɫ", "l").replace("oʊ", "əʊ").replace("aʊ", "ə").replace("ɐ", "ə")

    return text


phonemes = "boˈniːʁən"
phonemes = "".join(char for char in phonemes) if unicodedata.category(char) != "Cf" and char not in exclude)
phonemes = clean_text(phonemes, lang="de")
```