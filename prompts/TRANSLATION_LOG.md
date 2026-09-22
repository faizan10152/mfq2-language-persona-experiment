# Translation log

Covers every Spanish string in the prompts that does **not** come from Atari et al.'s
official MFQ-2 translation. The instruction sentence, the 36 items and the 5 response
labels are official and were extracted verbatim by `src/parse_docx.py`; they are not
listed here and were not touched.

Everything below lives in `prompts/templates.json`.

**Status: VERIFIED (2026-09-22).** The Spanish was drafted by Claude Opus 5 (Claude
Code) on 2026-09-21/22. The student independently back-translated every string
ES -> EN with **DeepL** and recorded the output in the "DeepL back-translation"
column below. All four round-trips preserve the meaning of the English source; no
string was changed as a result. The student remains responsible for any uncorrected
error.

Caveat that no back-translation can settle: English does not mark the *usted* / *tu*
distinction, so a ES -> EN round-trip cannot confirm register. The formal register was
verified by inspection against the official Spanish instruction instead.

## Strings

| # | Purpose | English (source) | Spanish (used in the runs) | DeepL back-translation (ES -> EN) | Verdict |
|---|---|---|---|---|---|
| 1 | Persona sentence | You are a person from {country}. | Usted es una persona de {country}. | "You are from Mexico." | ✅ meaning preserved; DeepL drops the redundant "a person", which is kept in Spanish only to stay structurally parallel to string 2 |
| 2 | Baseline system message (no persona) | You are a person answering a survey. | Usted es una persona que responde a una encuesta. | "You are a person taking a survey." | ✅ meaning preserved |
| 3 | Scale header | Use the following scale: | Utilice la siguiente escala: | "Use the following scale:" | ✅ exact match |
| 4 | Format instruction | Answer every statement. Respond with ONLY a single JSON object mapping each statement number to an integer from 1 to 5, and no other text. Example format: {...} | Responda a todas las afirmaciones. Responda ÚNICAMENTE con un solo objeto JSON que asocie el número de cada afirmación con un número entero del 1 al 5, sin ningún otro texto. Formato de ejemplo: {...} | "Answer all the statements. Respond ONLY with a single JSON object that maps the number of each statement to an integer from 1 to 5, with no other text. Example format: {...}" | ✅ meaning preserved |

### Note on quote characters

DeepL rendered the JSON example in string 4 with typographic quotes
(`{"1": 3, '3': 1}`). That is DeepL's own output formatting, **not** what is in the
prompt: `prompts/templates.json`, `items_en.json` and `items_es.json` were scanned and
contain only straight ASCII quotes. This matters — a curly quote inside the example
JSON would invite the model to emit curly quotes back, which `json.loads` rejects, and
would have inflated the parse-failure rate in the Spanish cells specifically.

## Country names

English prompts use the English exonyms; Spanish prompts use the Spanish endonyms.

| Persona | English | Spanish |
|---|---|---|
| Argentina | Argentina | Argentina |
| Chile | Chile | Chile |
| Colombia | Colombia | Colombia |
| Mexico | Mexico | **México** |
| Peru | Peru | **Perú** |

Note that the human data file spells Colombia as `Columbia`; that is a data-file
artefact only and never appears in a prompt (see `src/item_map.py`).

## Resolved: register (decided 2026-09-22)

The official Spanish instruction and response labels address the respondent with the
**formal** *usted*. An earlier draft of the persona sentence used the informal *tú*
("Eres una persona de Perú"), mixing two registers inside one prompt. Register is not
cosmetic in Spanish — it encodes social distance and could plausibly shift responses
on the very foundations under study, Authority in particular.

**Decision: formal *usted* throughout**, so the persona sentence matches the register
of the official text. State this explicitly in the Method section.

## Resolved: baseline structure (decided 2026-09-22)

An earlier draft gave the persona cells a system message and the no-persona cells none
at all, so the baseline differed from the persona conditions structurally as well as in
content.

**Decision: all 12 cells carry a system message.** The baseline gets a contentless one
that is structurally parallel to the persona sentence — "You are a person answering a
survey." / "Usted es una persona que responde a una encuesta." — so the only thing
varying across persona conditions is the country cue itself, and any persona effect is
attributable to the country rather than to the presence of a system message.

## Resolved: persona wording vs Münker (decided 2026-09-22)

Münker (2025) describes his persona prompt but never prints it, and his code is only
available on request. The English persona sentence `You are a person from {country}.`
implements his description and is kept. Design-level comparability may be claimed;
string-level replication may not. Full analysis, including a divergence in MFQ-2
item 27, is in `prompts/MUNKER_COMPARABILITY.md`.
