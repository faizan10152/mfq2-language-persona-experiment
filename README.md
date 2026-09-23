# Language vs. persona in LLM moral-foundation responses

Term paper, *Advanced Topics in Computational Text and Media Sciences #2*,
M.Sc. NLP, University of Trier.

Empirical mini-experiment: five Spanish-speaking countries (Argentina, Chile,
Colombia, Mexico, Peru) × two prompt languages (English, Spanish) × open-weight
LLMs answering the MFQ-2, compared against the human Study-2 data of
Atari et al. (2023).

## Status

- [x] Human data verified and baselines computed (`src/load_human.py`)
- [x] Item mapping resolved against the authors' own analysis code (`src/item_map.py`)
- [x] EN/ES questionnaire text extracted (`src/parse_docx.py`)
- [x] Prompt templates (`prompts/templates.json`, `src/build_prompts.py`) — Spanish wording UNVERIFIED, see `prompts/TRANSLATION_LOG.md`
- [x] Runner written (`src/run_models.py`) — awaiting model pulls, then smoke test
- [x] All three models: 1,800 administrations, 100% parsed
- [x] Analysis (`src/analyze.py`) — 9 tidy tables
- [ ] Figures (`src/plots.py`)

## Reproduce

The raw data is **not** tracked in this repository (see below). Download it first,
then:

```bash
python3 -m venv .venv
./.venv/bin/pip install pandas numpy scipy python-docx matplotlib requests
./.venv/bin/python src/parse_docx.py     # -> prompts/items_en.json, prompts/items_es.json
./.venv/bin/python src/load_human.py     # -> data/processed/*.csv, prints the verification report
./.venv/bin/python src/build_prompts.py  # -> prompts/rendered/*.txt, prompts/prompt_index.json
```

## Design

12 cells = 2 prompt languages (English, Spanish) x 6 persona conditions
(none + 5 countries), identical across models. Official MFQ-2 text is never
paraphrased; all other prompt wording lives in `prompts/templates.json`.

## Data provenance

The human data and questionnaire translations come from the OSF project of
Atari et al. (2023), <https://osf.io/srtxn/>. They are **not redistributed here**;
download them into `data/raw/` yourself:

| OSF path | Save as |
|---|---|
| `Data / Study 2 / Study_2_raw_dat.csv` | `data/raw/Study_2_raw_dat.csv` |
| `Materials / MFQ-2 Translations/` (all files) | `data/raw/MFQ2_Translations/` |

`data/processed/human_respondents.csv` is per-respondent data derived from that
file and is likewise untracked; `src/load_human.py` regenerates it in seconds.
The aggregate statistics (`human_country_stats.csv`, `human_pooled_stats.csv`)
are tracked.

The authors' analysis script `Code / Study 2 / Code_Study2.R` was consulted (and
is not redistributed here) to fix the MFQ-2 scoring key; the resulting mapping,
with full provenance, is documented in `src/item_map.py`.

## Reference

Atari, M., Haidt, J., Graham, J., Koleva, S., Stevens, S. T., & Dehghani, M.
(2023). Morality beyond the WEIRD: How the nomological network of morality varies
across cultures. *Journal of Personality and Social Psychology, 125*(5),
1157-1188. https://doi.org/10.1037/pspp0000470
