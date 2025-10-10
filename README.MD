# OLaPh — Optimal Language Phonemizer

[![PyPI version](https://img.shields.io/pypi/v/olaph.svg?logo=pypi)](https://pypi.org/project/olaph/)
[![Python versions](https://img.shields.io/pypi/pyversions/olaph.svg)](https://pypi.org/project/olaph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**OLaPh (Optimal Language Phonemizer)** is a multilingual phonemization framework that converts text into phonemes surpassing the quality of comparable frameworks.

---

## Overview

Traditional phonemizers rely on simple rule-based mappings or lexicon lookups.
Neural and hybrid approaches improve generalization but still struggle with:

- Names and foreign words
- Abbreviations and acronyms
- Loanwords and compounds
- Ambiguous homographs

**OLaPh** tackles these challenges by combining:

- Extensive **language-specific dictionaries**
- **Abbreviation, number, and letter normalization**
- **Compound resolution with probabilistic scoring**
- **Cross-language handling**
- **NLP-based preprocessing** via [spaCy](https://spacy.io) and [Lingua](https://github.com/pemistahl/lingua-py)

Evaluations in **German** and **English** show improved accuracy and robustness over existing phonemizers, including on challenging multilingual datasets.

---

## Features

- Multilingual phonemization (DE, EN, FR, ES)
- Abbreviation and letter pronunciation dictionaries
- Number normalization
- Cross-language acronym detection
- Compound splitting with probabilistic scoring
- Freely available lexica for research and development derived from wiktionary.org.

## Large Language Model
A LLM based on OLaPh output is also available. It is a GemmaX 2B Model trained on ~10M sentences derived from the FineWeb Corpus phonemized with the OLaPh framework.

Find it here on [huggingface](https://huggingface.co/iisys-hof/olaph)

---

## Installation

### From PyPI

```bash
pip install olaph
python -m spacy download de_core_news_sm
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download fr_core_news_sm

```

### From source

```bash
git clone https://github.com/iisys-hof/olaph.git
cd olaph
pip install -e .
python -m spacy download de_core_news_sm
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download fr_core_news_sm
```

## Example Usage

```python
from olaph import Olaph

phonemizer = Olaph()

output = phonemizer.phonemize_text("He ordered a Brezel and a beer in a tavern near München.", lang="en")

print(output)
```

---

## Dependencies

- [spaCy](https://spacy.io)
- [Lingua](https://github.com/pemistahl/lingua-py)
- [num2words](https://github.com/savoirfairelinux/num2words)
- [inflect](https://github.com/jaraco/inflect)

---

## Research Summary

Phonemization, the conversion of text into phonemes, is a key step in text-to-speech. Traditional approaches use rule-based transformations and lexicon lookups, while more advanced methods apply preprocessing techniques or neural networks for improved accuracy on out-of-domain vocabulary. However, all systems struggle with names, loanwords, abbreviations, and homographs. This work presents OLaPh (Optimal Language Phonemizer), a framework that combines large lexica, multiple NLP techniques, and compound resolution with a probabilistic scoring function. Evaluations in German and English show improved accuracy over previous approaches, including on a challenging dataset. To further address unresolved cases, we train a large language model on OLaPh-generated data, which achieves even stronger generalization and performance. Together, the framework and LLM improve phonemization consistency and provide a freely available resource for future research.

---

## Citation

If you use OLaPh in academic work, please cite:

```bibtex
@misc{wirth2025olaphoptimallanguagephonemizer,
      title={OLaPh: Optimal Language Phonemizer},
      author={Johannes Wirth},
      year={2025},
      eprint={2509.20086},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2509.20086},
}
```