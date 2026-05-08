# OLaPh — Optimal Language Phonemizer

[![PyPI version](https://img.shields.io/pypi/v/olaph.svg?logo=pypi)](https://pypi.org/project/olaph/)
[![Python versions](https://img.shields.io/pypi/pyversions/olaph.svg)](https://pypi.org/project/olaph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**OLaPh (Optimal Language Phonemizer)** is a multilingual phonemization framework that converts text into phonemes surpassing the quality of comparable frameworks.

---

## NEWS

05/2026: A new version of OLaPhLLM is available [here](https://huggingface.co/iisys-hof/OLaPhLLM_v2)

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

- Multilingual phonemization (DE, EN-US, EN-UK, FR, ES, NL, SV, DA, PL, IT, FI)
- Abbreviation and letter pronunciation dictionaries
- Number normalization
- Cross-language acronym detection
- Compound splitting with statistical scoring
- Freely available lexica for research and development derived from wiktionary.org.

## Large Language Model
A LLM based on OLaPh output is also available. It is a GemmaX 2B Model trained on ~10M sentences derived from the FineWeb Corpus phonemized with the OLaPh framework.

Find it here on [huggingface](https://huggingface.co/iisys-hof/olaph) (Needs to be updated for the additional languages)

---

## Installation

### From PyPI

```bash
pip install olaph
```

spaCy models are downloaded on demand.

### From source

```bash
git clone https://github.com/iisys-hof/olaph.git
cd olaph
pip install -e .
```

## Example Usage

```python
from olaph import Olaph

phonemizer = Olaph()

output = phonemizer.phonemize_text("He ordered a Brezel and a beer in a tavern near München.", lang="en-us")

print(output)
```

---

## Dependencies

- [spaCy](https://spacy.io)
- [Lingua](https://github.com/pemistahl/lingua-py)
- [num2words](https://github.com/savoirfairelinux/num2words)
- [inflect](https://github.com/jaraco/inflect)

---

## Dictionars Sources

- [Wiktionary Dumps](https://dumps.wikimedia.org/backup-index.html)
- [Neurlang Dataset](https://github.com/neurlang/dataset)


## Research Summary

Phonemization is a critical component in text-to-speech synthesis. Traditional approaches rely on deterministic transformations and lexica, while neural methods offer potential for higher generalization on out-of-vocabulary (OOV) terms. This work introduces OLaPh (Optimal Language Phonemizer), a hybrid framework that integrates extensive multilingual lexica with advanced NLP techniques and a statistical subword segmentation function. Evaluations on the WikiPron benchmark show that the OLaPh framework significantly outperforms established baselines in overall accuracy and maintains robustness on OOV data through advanced fallback mechanisms. To further explore neural generalization, we utilize the framework to synthesize a high-consistency training corpus for an instruction-tuned Large Language Model (LLM). While the deterministic framework remains more accurate overall, the LLM demonstrates strong generalization, matching or partly exceeding the framework’s performance. This suggests that the LLM successfully internalized phonetic intuitions from the synthetic data that transcend the framework’s capabilities. Together, these tools provide a comprehensive, open-source resource for multilingual G2P research.

---

## Citation

If you use OLaPh in academic work, please cite:

```bibtex
@misc{wirth2026olaphoptimallanguagephonemizer,
      title={OLaPh: Optimal Language Phonemizer}, 
      author={Johannes Wirth},
      year={2026},
      eprint={2509.20086},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2509.20086}, 
}
```